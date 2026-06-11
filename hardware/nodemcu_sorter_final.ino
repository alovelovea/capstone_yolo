#include <ESP8266WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>
#include <Servo.h>

/*
  NodeMCU 최종 분류 제어 코드

  동작 흐름:
  1. Wi-Fi 연결
  2. MQTT Broker 연결
  3. sorter/command 토픽 구독
  4. 노트북에서 can, pet, plastic, glass, paper, plasticbag 등의 분류 결과 수신
  5. 수신 후 2초 뒤 해당 서보모터 개방
  6. 5초 유지 후 다시 닫힘
  7. 컨베이어 스텝모터는 계속 회전
*/

// ===================== Wi-Fi 설정 =====================
const char* WIFI_SSID = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";

// ===================== MQTT 설정 =====================
// HiveMQ Cloud 사용 시 예시:
// host: xxxxxxxx.s1.eu.hivemq.cloud
// port: 8883
const char* MQTT_HOST = "YOUR_MQTT_HOST";
const int   MQTT_PORT = 8883;

const char* MQTT_USERNAME = "YOUR_MQTT_USERNAME";
const char* MQTT_PASSWORD = "YOUR_MQTT_PASSWORD";

const char* MQTT_CLIENT_ID = "nodemcu-sorter-001";
const char* MQTT_COMMAND_TOPIC = "sorter/command";
const char* MQTT_STATUS_TOPIC  = "sorter/status";

// ===================== 서보모터 설정 =====================
// 사용하는 분류 종류와 핀을 실제 하드웨어에 맞게 수정하세요.
// D3, D8은 부팅 핀과 관련되어 문제가 생길 수 있으므로,
// 부팅이 안 되면 D1, D2, D5, D6, D7 위주로 재배치하는 것을 권장합니다.

// 스텝모터를 D5, D6에 사용한다면 서보 핀과 겹치면 안 됩니다.
const int NUM_CHANNELS = 5;

const char* COMMANDS[NUM_CHANNELS] = {
  "can",
  "pet",
  "plastic",
  "glass",
  "paper",
  "plasticbag"
};

const uint8_t SERVO_PINS[NUM_CHANNELS] = {
  D1,   // can
  D2,   // pet
  D3,   // plastic
  D7,   // glass
  D8,   // paper
  D9    // plasticbag
};

Servo servos[NUM_CHANNELS];

const int CLOSE_ANGLE[NUM_CHANNELS] = {
  0, 0, 0, 0, 0
};

const int OPEN_ANGLE[NUM_CHANNELS] = {
  90, 90, 90, 90, 90
};

// MQTT 명령 수신 후 몇 ms 뒤 플랩을 열지
const unsigned long OPEN_DELAY_MS = 2000;

// 플랩을 몇 ms 동안 열어둘지
const unsigned long OPEN_HOLD_MS = 5000;

// ===================== 컨베이어 스텝모터 설정 =====================
// TB6600 기준 PUL/DIR 사용 예시
// 컨베이어를 NodeMCU에서 제어하지 않는다면 STEPPER_ENABLED를 0으로 변경
#define STEPPER_ENABLED 1

const uint8_t STEP_PUL_PIN = D5;
const uint8_t STEP_DIR_PIN = D6;

// 값이 작을수록 빠르게 회전합니다.
const unsigned long STEP_INTERVAL_US = 800;

// 방향 변경이 필요하면 HIGH/LOW 변경
const int STEP_DIR_VALUE = HIGH;

// ===================== MQTT 객체 =====================
WiFiClientSecure secureClient;
PubSubClient mqttClient(secureClient);

// ===================== 분류 작업 큐 =====================
struct SortTask {
  int channelIndex;
  unsigned long openAt;
  bool valid;
};

const int QUEUE_SIZE = 8;
SortTask taskQueue[QUEUE_SIZE];

int queueHead = 0;
int queueTail = 0;
int queueCount = 0;

bool servoActive[NUM_CHANNELS];
unsigned long servoCloseAt[NUM_CHANNELS];

// ===================== 유틸 함수 =====================
void publishStatus(const String& message) {
  if (mqttClient.connected()) {
    mqttClient.publish(MQTT_STATUS_TOPIC, message.c_str());
  }
}

String normalizeCommand(String command) {
  command.trim();
  command.toLowerCase();

  // 혹시 JSON 형태로 들어오는 경우를 최소한으로 처리
  // 예: {"class":"can"}
  if (command.startsWith("{")) {
    int keyIndex = command.indexOf("\"class\"");
    if (keyIndex >= 0) {
      int colonIndex = command.indexOf(":", keyIndex);
      int firstQuote = command.indexOf("\"", colonIndex + 1);
      int secondQuote = command.indexOf("\"", firstQuote + 1);

      if (firstQuote >= 0 && secondQuote > firstQuote) {
        command = command.substring(firstQuote + 1, secondQuote);
        command.trim();
        command.toLowerCase();
      }
    }
  }

  // 모델 클래스명이 다르게 나오는 경우를 위한 별칭 처리
  if (command == "bottle") command = "pet";
  if (command == "pet_bottle") command = "pet";
  if (command == "plastic_bottle") command = "pet";
  if (command == "metal") command = "can";
  if (command == "cardboard") command = "paper";
  if (command == "vinyl") command = "plasticbag";

  return command;
}

int findChannelIndex(const String& command) {
  for (int i = 0; i < NUM_CHANNELS; i++) {
    if (command == COMMANDS[i]) {
      return i;
    }
  }
  return -1;
}

bool enqueueTask(int channelIndex) {
  if (queueCount >= QUEUE_SIZE) {
    Serial.println("[QUEUE] 큐가 가득 찼습니다.");
    publishStatus("queue_full");
    return false;
  }

  taskQueue[queueTail].channelIndex = channelIndex;
  taskQueue[queueTail].openAt = millis() + OPEN_DELAY_MS;
  taskQueue[queueTail].valid = true;

  queueTail = (queueTail + 1) % QUEUE_SIZE;
  queueCount++;

  Serial.print("[QUEUE] 작업 추가: ");
  Serial.print(COMMANDS[channelIndex]);
  Serial.print(" / ");
  Serial.print(OPEN_DELAY_MS);
  Serial.println("ms 후 작동");

  return true;
}

void popTask() {
  if (queueCount <= 0) return;

  taskQueue[queueHead].valid = false;
  queueHead = (queueHead + 1) % QUEUE_SIZE;
  queueCount--;
}

void openServo(int index) {
  if (index < 0 || index >= NUM_CHANNELS) return;

  Serial.print("[SERVO] OPEN: ");
  Serial.println(COMMANDS[index]);

  servos[index].write(OPEN_ANGLE[index]);
  servoActive[index] = true;
  servoCloseAt[index] = millis() + OPEN_HOLD_MS;

  publishStatus(String("open:") + COMMANDS[index]);
}

void closeServo(int index) {
  if (index < 0 || index >= NUM_CHANNELS) return;

  Serial.print("[SERVO] CLOSE: ");
  Serial.println(COMMANDS[index]);

  servos[index].write(CLOSE_ANGLE[index]);
  servoActive[index] = false;

  publishStatus(String("close:") + COMMANDS[index]);
}

// ===================== MQTT 콜백 =====================
void mqttCallback(char* topic, byte* payload, unsigned int length) {
  String message = "";

  for (unsigned int i = 0; i < length; i++) {
    message += (char)payload[i];
  }

  String command = normalizeCommand(message);

  Serial.print("[MQTT] 수신 topic: ");
  Serial.println(topic);

  Serial.print("[MQTT] 수신 message: ");
  Serial.println(command);

  int channelIndex = findChannelIndex(command);

  if (channelIndex < 0) {
    Serial.print("[COMMAND] 알 수 없는 분류값: ");
    Serial.println(command);
    publishStatus(String("unknown:") + command);
    return;
  }

  bool ok = enqueueTask(channelIndex);

  if (ok) {
    publishStatus(String("received:") + command);
  }
}

// ===================== Wi-Fi 연결 =====================
void connectWiFi() {
  Serial.println();
  Serial.print("[WiFi] 연결 중: ");
  Serial.println(WIFI_SSID);

  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.println("[WiFi] 연결 성공");
  Serial.print("[WiFi] IP: ");
  Serial.println(WiFi.localIP());
}

// ===================== MQTT 연결 =====================
void connectMQTT() {
  while (!mqttClient.connected()) {
    Serial.print("[MQTT] 연결 중... ");

    if (mqttClient.connect(MQTT_CLIENT_ID, MQTT_USERNAME, MQTT_PASSWORD)) {
      Serial.println("성공");

      mqttClient.subscribe(MQTT_COMMAND_TOPIC);
      Serial.print("[MQTT] 구독 시작: ");
      Serial.println(MQTT_COMMAND_TOPIC);

      publishStatus("nodemcu_connected");
    } else {
      Serial.print("실패, rc=");
      Serial.print(mqttClient.state());
      Serial.println(" / 3초 후 재시도");
      delay(3000);
    }
  }
}

// ===================== 스텝모터 구동 =====================
void runConveyorStepper() {
#if STEPPER_ENABLED
  static unsigned long lastStepTime = 0;
  static bool pulseState = LOW;

  unsigned long now = micros();

  if (now - lastStepTime >= STEP_INTERVAL_US) {
    lastStepTime = now;

    pulseState = !pulseState;
    digitalWrite(STEP_PUL_PIN, pulseState);
  }
#endif
}

// ===================== 큐 및 서보 처리 =====================
void processServoClose() {
  unsigned long now = millis();

  for (int i = 0; i < NUM_CHANNELS; i++) {
    if (servoActive[i]) {
      if ((long)(now - servoCloseAt[i]) >= 0) {
        closeServo(i);
      }
    }
  }
}

void processTaskQueue() {
  if (queueCount <= 0) return;

  SortTask task = taskQueue[queueHead];

  if (!task.valid) {
    popTask();
    return;
  }

  unsigned long now = millis();

  if ((long)(now - task.openAt) >= 0) {
    int index = task.channelIndex;

    if (index >= 0 && index < NUM_CHANNELS) {
      openServo(index);
    }

    popTask();
  }
}

// ===================== 초기 설정 =====================
void setup() {
  Serial.begin(115200);
  delay(500);

  Serial.println();
  Serial.println("====================================");
  Serial.println(" NodeMCU Waste Sorter Final Code");
  Serial.println("====================================");

#if STEPPER_ENABLED
  pinMode(STEP_PUL_PIN, OUTPUT);
  pinMode(STEP_DIR_PIN, OUTPUT);

  digitalWrite(STEP_PUL_PIN, LOW);
  digitalWrite(STEP_DIR_PIN, STEP_DIR_VALUE);

  Serial.println("[STEPPER] 컨베이어 스텝모터 활성화");
#endif

  for (int i = 0; i < NUM_CHANNELS; i++) {
    servos[i].attach(SERVO_PINS[i]);
    servos[i].write(CLOSE_ANGLE[i]);

    servoActive[i] = false;
    servoCloseAt[i] = 0;

    Serial.print("[SERVO] ");
    Serial.print(COMMANDS[i]);
    Serial.print(" -> pin ");
    Serial.println(SERVO_PINS[i]);
  }

  connectWiFi();

  // 테스트 편의를 위해 인증서 검증 생략
  // 실제 배포 환경에서는 Root CA 인증서를 사용하는 것이 좋습니다.
  secureClient.setInsecure();

  mqttClient.setServer(MQTT_HOST, MQTT_PORT);
  mqttClient.setCallback(mqttCallback);
  mqttClient.setBufferSize(256);

  connectMQTT();
}

// ===================== 메인 루프 =====================
void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    connectWiFi();
  }

  if (!mqttClient.connected()) {
    connectMQTT();
  }

  mqttClient.loop();

  runConveyorStepper();
  processTaskQueue();
  processServoClose();
}