#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <WiFiClientSecureBearSSL.h>
#include <PubSubClient.h>
#include <time.h>

// ==============================
// 1. Wi-Fi 설정
// ==============================
const char* WIFI_SSID = "wifi_name";
const char* WIFI_PASSWORD = "wifi_passwd";

// ==============================
// 2. MQTT 설정
// ==============================
const char* MQTT_HOST = "host";
const int MQTT_PORT = port;

const char* MQTT_USERNAME = "subscriber_id";
const char* MQTT_PASSWORD = "subscriber_paaswd";

const char* MQTT_SUB_TOPIC = "topic";
const char* MQTT_STATUS_TOPIC = "status_topic";

// ==============================
// 3. Let's Encrypt ISRG Root X1 인증서
// ==============================
static const char ISRG_ROOT_X1[] PROGMEM = R"EOF(
)EOF";

// ==============================
// 4. MQTT 클라이언트 객체
// ==============================
BearSSL::WiFiClientSecure secureClient;
PubSubClient mqttClient(secureClient);
BearSSL::X509List rootCert(ISRG_ROOT_X1);

// ==============================
// 5. Wi-Fi 연결
// ==============================
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
  Serial.print("[WiFi] IP 주소: ");
  Serial.println(WiFi.localIP());
}

// ==============================
// 6. NTP 시간 동기화
// TLS 인증서 유효기간 검증에 필요
// ==============================
void syncTime() {
  Serial.println("[NTP] 시간 동기화 시작");

  configTime(
    9 * 3600,   // 한국 시간 UTC+9
    0,
    "pool.ntp.org",
    "time.google.com"
  );

  time_t now = time(nullptr);

  while (now < 1700000000) {
    delay(500);
    Serial.print(".");
    now = time(nullptr);
  }

  Serial.println();
  Serial.println("[NTP] 시간 동기화 완료");

  struct tm* timeinfo = localtime(&now);
  Serial.print("[NTP] 현재 시간: ");
  Serial.println(asctime(timeinfo));
}

// ==============================
// 7. 명령 처리 함수
// ==============================
void handleSortCommand(const String& command) {
  Serial.print("[COMMAND] 수신한 분류 명령: ");
  Serial.println(command);

  if (command == "can") {
    Serial.println("-> 캔 분류 동작 실행 위치");
  }
  else if (command == "pet") {
    Serial.println("-> 페트병 분류 동작 실행 위치");
  }
  else if (command == "plastic") {
    Serial.println("-> 플라스틱 분류 동작 실행 위치");
  }
  else if (command == "glass") {
    Serial.println("-> 유리 분류 동작 실행 위치");
  }
  else if (command == "paper") {
    Serial.println("-> 종이 분류 동작 실행 위치");
  }
  else {
    Serial.println("-> 알 수 없는 명령");
  }

  // 상태 메시지 발행
  String statusMessage = "received:" + command;
  mqttClient.publish(MQTT_STATUS_TOPIC, statusMessage.c_str());
}

// ==============================
// 8. MQTT 메시지 수신 콜백
// ==============================
void mqttCallback(char* topic, byte* payload, unsigned int length) {
  String message = "";

  for (unsigned int i = 0; i < length; i++) {
    message += (char)payload[i];
  }

  Serial.println();
  Serial.print("[MQTT] 토픽: ");
  Serial.println(topic);

  Serial.print("[MQTT] 메시지: ");
  Serial.println(message);

  if (String(topic) == MQTT_SUB_TOPIC) {
    handleSortCommand(message);
  }
}

// ==============================
// 9. MQTT 연결
// ==============================
void connectMQTT() {
  while (!mqttClient.connected()) {
    Serial.println("[MQTT] 서버 연결 시도 중...");

    String clientId = "nodemcu-sorter-";
    clientId += String(ESP.getChipId(), HEX);

    bool connected = mqttClient.connect(
      clientId.c_str(),
      MQTT_USERNAME,
      MQTT_PASSWORD
    );

    if (connected) {
      Serial.println("[MQTT] 연결 성공");

      mqttClient.subscribe(MQTT_SUB_TOPIC);
      Serial.print("[MQTT] 구독 시작: ");
      Serial.println(MQTT_SUB_TOPIC);

      mqttClient.publish(MQTT_STATUS_TOPIC, "nodemcu_online");
    }
    else {
      Serial.print("[MQTT] 연결 실패, state=");
      Serial.println(mqttClient.state());
      Serial.println("[MQTT] 5초 후 재시도");
      delay(5000);
    }
  }
}

// ==============================
// 10. setup
// ==============================
void setup() {
  Serial.begin(115200);
  delay(1000);

  connectWiFi();
  syncTime();

  // 서버 인증서 검증용 Root CA 등록
  secureClient.setTrustAnchors(&rootCert);

  // MQTT 설정
  mqttClient.setServer(MQTT_HOST, MQTT_PORT);
  mqttClient.setCallback(mqttCallback);

  connectMQTT();
}

// ==============================
// 11. loop
// ==============================
void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("[WiFi] 연결 끊김, 재연결 시도");
    connectWiFi();
    syncTime();
  }

  if (!mqttClient.connected()) {
    connectMQTT();
  }

  mqttClient.loop();
}