# hardware (Workflow)

본 폴더는 YOLO 기반 쓰레기 객체 인식 결과를 실제 하드웨어 제어 장치와 연동하기 위한 코드 및 테스트 파일을 포함합니다.

최종 시스템은 노트북에서 웹캠 영상을 입력받아 YOLO 모델로 쓰레기 종류를 인식하고, 인식된 결과를 MQTT로 NodeMCU에 전송합니다. NodeMCU는 MQTT 메시지를 수신한 뒤, 분류 결과에 따라 서보모터를 제어하여 플랩을 열고 닫습니다.

---

## 1. 하드웨어 시스템 개요

본 프로젝트의 하드웨어 시스템은 다음과 같은 흐름으로 동작합니다.

```text
웹캠
 ↓
노트북 YOLO 추론 서버
 ↓
MQTT Broker
 ↓
NodeMCU
 ↓
서보모터 제어
 ↓
분류 플랩 작동
 ↓
쓰레기 자동 분류
```

웹캠은 컨베이어 벨트 위의 쓰레기를 촬영하고, 노트북은 YOLO 모델을 이용하여 쓰레기의 종류를 인식합니다.

인식 결과는 MQTT 메시지로 발행되며, NodeMCU는 해당 메시지를 구독하여 분류 결과에 맞는 서보모터 제어 동작을 수행합니다.

---

## 2. 폴더 구조

```text
hardware/
├── README.md
├── laptop_yolo_mqtt_publish.py
├── nodemcu_sorter_final.ino
├── mqtt_publish.py
├── wifi_mqtt_subscribe.ino
└── motor_test.ino

```

| 파일명                           | 역할                                              |
| ----------------------------- | ----------------------------------------------- |
| `laptop_yolo_mqtt_publish.py` | 노트북에서 웹캠 영상 입력, YOLO 추론, MQTT 결과 전송을 수행하는 최종 코드 |
| `nodemcu_sorter_final.ino`    | NodeMCU에서 MQTT 명령을 수신하고 컨베이어 및 서보모터를 제어하는 최종 코드 |
| `mqtt_publish.py`             | MQTT 메시지 송신 단독 테스트 코드                           |
| `wifi_mqtt_subscribe.ino`     | NodeMCU Wi-Fi 연결 및 MQTT 수신 테스트 코드               |
| `motor_test.ino`              | 컨베이어 스텝모터 구동 테스트 코드                             |

---

## 3. 사용 하드웨어

| 구성 요소           | 설명                       |
| --------------- | ------------------------ |
| 노트북             | YOLO 모델 실행 및 MQTT 메시지 발행 |
| 웹캠              | 컨베이어 벨트 위 쓰레기 영상 입력      |
| NodeMCU ESP8266 | MQTT 메시지 수신 및 모터 제어      |
| MQTT Broker     | 노트북과 NodeMCU 간 메시지 중계    |
| 서보모터            | 분류 플랩 개폐                 |
| 스텝모터            | 컨베이어 벨트 구동               |
| 모터 드라이버         | 스텝모터 제어                  |
| 컨베이어 벨트         | 쓰레기를 인식 영역과 분류 위치로 이동    |
| 분류 플랩           | 쓰레기를 각 분류 통으로 낙하시키는 장치   |

---

## 4. 전체 동작 흐름

### 4.1 웹캠 영상 입력

노트북에 연결된 웹캠이 컨베이어 벨트 위의 쓰레기를 촬영합니다.

웹캠은 쓰레기가 지나가는 위치를 향하도록 컨베이어 벨트 상단에 고정합니다. 촬영된 영상은 OpenCV를 통해 프레임 단위로 처리됩니다.

---

### 4.2 YOLO 객체 인식

노트북에서 실행되는 YOLO 모델은 웹캠 영상을 기반으로 쓰레기 종류를 탐지합니다.

예측 가능한 분류값 예시는 다음과 같습니다.

```text
can
pet
plastic
glass
paper
plasticbag
```

YOLO 모델이 쓰레기를 인식하면 해당 클래스명을 MQTT 메시지로 변환합니다.

---

### 4.3 MQTT 메시지 전송

노트북은 MQTT Publisher 역할을 수행합니다.

`laptop_yolo_mqtt_publish.py`는 웹캠 영상에서 객체를 탐지한 뒤, 최종 분류 결과를 `sorter/command` 토픽으로 발행합니다.

예시:

```text
[YOLO] detected: can
[MQTT] publish: sorter/command -> can
```

---

### 4.4 NodeMCU 메시지 수신

NodeMCU는 MQTT Subscriber 역할을 수행합니다.

`nodemcu_sorter_final.ino`는 Wi-Fi에 연결한 뒤 MQTT Broker에 접속하고, `sorter/command` 토픽을 구독합니다.

MQTT 메시지를 수신하면 수신한 분류값에 따라 지정된 서보모터를 작동시킵니다.

예시:

```text
[MQTT] received: can
[Servo] can flap open
```

---

### 4.5 서보모터 기반 플랩 제어

NodeMCU는 수신한 분류 결과에 따라 해당 위치의 서보모터를 작동시킵니다.

서보모터는 플랩을 열고 닫는 역할을 하며, 플랩이 열리는 동안 컨베이어 벨트를 따라 이동하던 쓰레기가 해당 분류 통으로 낙하합니다.

예시 동작:

| 분류 결과     | 동작                |
| --------- | ----------------- |
| `can`     | 캔 분류 위치의 플랩 작동    |
| `pet`     | 페트병 분류 위치의 플랩 작동  |
| `plastic` | 플라스틱 분류 위치의 플랩 작동 |
| `glass`   | 유리 분류 위치의 플랩 작동   |
| `paper`   | 종이 분류 위치의 플랩 작동   |
| `plasticbag`   | 비닐봉투 분류 위치의 플랩 작동   |

---

## 5. MQTT Topic 구조

| Topic            | 방향                    | 설명                       |
| ---------------- | --------------------- | ------------------------ |
| `sorter/command` | 노트북 → NodeMCU         | YOLO 분류 결과 전송            |
| `sorter/status`  | NodeMCU → MQTT Broker | NodeMCU 연결 상태 및 동작 상태 전송 |

예시 메시지:

```text
sorter/command -> can
sorter/command -> pet
sorter/command -> plastic
sorter/command -> glass
sorter/command -> paper
sotert/command -> plasticbag
```

---

## 6. 최종 코드 설명

## 6.1 노트북 YOLO + MQTT 송신 코드

파일명:

```text
laptop_yolo_mqtt_publish.py
```

### 주요 역할

`laptop_yolo_mqtt_publish.py`는 노트북에서 웹캠 영상을 입력받고, YOLO 모델을 이용하여 쓰레기 객체를 탐지한 뒤, 탐지 결과를 MQTT Broker로 전송하는 최종 코드입니다.

### 주요 기능

| 기능         | 설명                              |
| ---------- | ------------------------------- |
| 웹캠 연결      | 노트북에 연결된 웹캠 영상 입력               |
| YOLO 모델 로드 | 학습된 `best.pt` 모델 로드             |
| 실시간 객체 탐지  | 웹캠 프레임에서 쓰레기 객체 탐지              |
| 클래스명 변환    | 모델 클래스명을 하드웨어 명령값으로 변환          |
| MQTT 연결    | MQTT Broker에 Publisher로 연결      |
| 결과 전송      | 탐지 결과를 `sorter/command` 토픽으로 발행 |
| 화면 출력      | 탐지 결과와 상태 정보를 화면에 표시            |

### 실행 전 설치

```bash
pip install ultralytics opencv-python paho-mqtt
```

### 실행 방법

프로젝트 루트 디렉토리에서 실행합니다.

```bash
python hardware/laptop_yolo_mqtt_publish.py --model weights/best.pt --camera 0
```

웹캠이 여러 개 연결되어 있으면 다음과 같이 카메라 번호를 변경합니다.

```bash
python hardware/laptop_yolo_mqtt_publish.py --model weights/best.pt --camera 1
```

### 수정해야 할 설정값

코드 상단의 MQTT 정보를 실제 환경에 맞게 수정합니다.

```python
MQTT_HOST = "YOUR_MQTT_HOST"
MQTT_PORT = 8883

MQTT_USERNAME = "YOUR_MQTT_USERNAME"
MQTT_PASSWORD = "YOUR_MQTT_PASSWORD"

MQTT_CLIENT_ID = "laptop-yolo-publisher-001"
MQTT_COMMAND_TOPIC = "sorter/command"
```

### 클래스명 매핑

YOLO 모델의 클래스명과 NodeMCU에서 처리하는 명령어가 다를 경우 `CLASS_TO_COMMAND`를 수정합니다.

```python
CLASS_TO_COMMAND = {
    "can": "can",
    "pet": "pet",
    "plastic": "plastic",
    "glass": "glass",
    "paper": "paper",
    "plasticbag": "plasticbag"
}
```

예를 들어 모델에서 `bottle`로 예측하지만 하드웨어에서는 `pet`으로 처리하고 싶다면 다음과 같이 추가합니다.

```python
"bottle": "pet"
```

---

## 6.2 NodeMCU 최종 제어 코드

파일명:

```text
nodemcu_sorter_final.ino
```

### 주요 역할

`nodemcu_sorter_final.ino`는 NodeMCU가 Wi-Fi 및 MQTT Broker에 연결한 뒤, 노트북에서 발행한 분류 결과를 수신하고 서보모터를 제어하는 최종 코드입니다.

### 주요 기능

| 기능       | 설명                             |
| -------- | ------------------------------ |
| Wi-Fi 연결 | 지정된 SSID와 비밀번호로 Wi-Fi 연결       |
| MQTT 연결  | MQTT Broker 접속 및 Topic 구독      |
| 명령 수신    | `sorter/command` 토픽에서 분류 결과 수신 |
| 명령 정규화   | 수신 문자열을 소문자 처리 및 별칭 변환         |
| 작업 큐 처리  | 수신 명령을 큐에 저장하고 일정 시간 뒤 실행      |
| 서보모터 제어  | 분류 결과에 맞는 플랩 개폐                |
| 컨베이어 구동  | 스텝모터를 이용한 컨베이어 벨트 지속 구동        |
| 상태 발행    | 동작 상태를 `sorter/status` 토픽으로 전송 |

### 업로드 방법

1. Arduino IDE 실행
2. `hardware/nodemcu_sorter_final.ino` 파일 열기
3. 보드 선택
4. 포트 선택
5. Wi-Fi 및 MQTT 정보 수정
6. 업로드
7. 시리얼 모니터로 연결 상태 확인

보드 설정 예시:

```text
Board: NodeMCU 1.0 (ESP-12E Module)
Upload Speed: 115200
Serial Monitor: 115200 baud
```

### 수정해야 할 설정값

```cpp
const char* WIFI_SSID = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";

const char* MQTT_HOST = "YOUR_MQTT_HOST";
const int   MQTT_PORT = 8883;

const char* MQTT_USERNAME = "YOUR_MQTT_USERNAME";
const char* MQTT_PASSWORD = "YOUR_MQTT_PASSWORD";
```

### 서보모터 핀 설정

실제 연결한 핀에 맞게 수정합니다.

```cpp
const uint8_t SERVO_PINS[NUM_CHANNELS] = {
  D1,   // can
  D2,   // pet
  D3,   // plastic
  D7,   // glass
  D8,   // paper
  D9,   // plasticbag
};
```

### 분류 명령 설정

노트북에서 보내는 MQTT 메시지와 동일해야 합니다.

```cpp
const char* COMMANDS[NUM_CHANNELS] = {
  "can",
  "pet",
  "plastic",
  "glass",
  "paper",
  "plasticbag"
};
```

### 플랩 각도 설정

```cpp
const int CLOSE_ANGLE[NUM_CHANNELS] = {
  0, 0, 0, 0, 0
};

const int OPEN_ANGLE[NUM_CHANNELS] = {
  90, 90, 90, 90, 90
};
```

플랩 구조에 따라 `0`, `90`, `180` 값을 조정합니다.

### 동작 시간 설정

```cpp
const unsigned long OPEN_DELAY_MS = 2000;
const unsigned long OPEN_HOLD_MS = 5000;
```

| 설정값             | 의미                       |
| --------------- | ------------------------ |
| `OPEN_DELAY_MS` | MQTT 수신 후 플랩을 열기까지 대기 시간 |
| `OPEN_HOLD_MS`  | 플랩을 열어두는 시간              |

---

## 7. 테스트 코드 설명

## 7.1 MQTT 송신 테스트

파일명:

```text
mqtt_publish.py
```

### 역할

YOLO 코드와 연결하기 전, 노트북에서 MQTT 메시지가 정상적으로 발행되는지 확인하는 테스트 코드입니다.

### 실행 방법

```bash
python hardware/mqtt_publish.py
```

예시 입력:

```text
can
pet
plastic
glass
paper
plasticbag
```

---

## 7.2 NodeMCU MQTT 수신 테스트

파일명:

```text
wifi_mqtt_subscribe.ino
```

### 역할

NodeMCU가 Wi-Fi에 연결하고 MQTT 메시지를 정상적으로 수신하는지 확인하는 테스트 코드입니다.

### 테스트 방법

1. `wifi_mqtt_subscribe.ino` 업로드
2. 시리얼 모니터 실행
3. 노트북에서 `mqtt_publish.py` 실행
4. 메시지 수신 로그 확인

예시 로그:

```text
[WiFi] 연결 성공
[MQTT] 연결 성공
[MQTT] 메시지 수신: can
```

---

## 7.3 모터 구동 테스트

파일명:

```text
motor_test.ino
```

### 역할

컨베이어 벨트 구동용 스텝모터와 모터 드라이버 연결이 정상적으로 동작하는지 확인하는 테스트 코드입니다.

### 핀 설정 예시

```cpp
#define PUL_PIN D5
#define DIR_PIN D6
```

| 핀  | 역할           |
| -- | ------------ |
| D5 | Pulse 신호     |
| D6 | Direction 신호 |

모터 회전 방향이 반대일 경우 `DIR_PIN`의 HIGH/LOW 값을 변경하여 방향을 조정합니다.

---

## 8. 최종 통합 테스트 순서

### 1단계: 모터 단독 테스트

먼저 `motor_test.ino`를 업로드하여 컨베이어 모터가 정상적으로 회전하는지 확인합니다.

```text
확인 항목:
- 모터 회전 여부
- 회전 방향
- 회전 속도
- 벨트 장력
```

---

### 2단계: MQTT 송수신 테스트

노트북에서 `mqtt_publish.py`를 실행하고, NodeMCU에는 `wifi_mqtt_subscribe.ino`를 업로드하여 MQTT 통신이 정상적으로 되는지 확인합니다.

```text
노트북 입력: can
NodeMCU 수신: can
```

---

### 3단계: 서보모터 플랩 테스트

NodeMCU 최종 코드 또는 별도 서보 테스트 코드로 각 플랩이 정상적으로 열리고 닫히는지 확인합니다.

```text
확인 항목:
- 각 서보모터 핀 연결
- 열림 각도
- 닫힘 각도
- 플랩 간섭 여부
```

---

### 4단계: 노트북 YOLO 추론 테스트

웹캠을 연결하고 `laptop_yolo_mqtt_publish.py`를 실행합니다.

```bash
python hardware/laptop_yolo_mqtt_publish.py --model weights/best.pt --camera 0
```

웹캠 화면에서 객체가 정상적으로 탐지되는지 확인합니다.

---

### 5단계: 최종 통합 테스트

1. 컨베이어 벨트를 구동합니다.
2. 웹캠으로 쓰레기 영상을 입력받습니다.
3. YOLO 모델이 쓰레기 종류를 인식합니다.
4. 인식 결과가 MQTT로 전송됩니다.
5. NodeMCU가 MQTT 메시지를 수신합니다.
6. 해당 분류 위치의 서보모터가 작동합니다.
7. 쓰레기가 알맞은 분류 통으로 떨어지는지 확인합니다.

---

## 9. 최종 시스템 동작 예시

```text
[YOLO] detected: can
[MQTT] publish: sorter/command -> can

[NodeMCU] received: can
[QUEUE] can task added
[SERVO] can flap open
[SORTER] can waste dropped
[SERVO] can flap close
```

---

## 10. 전원 및 배선 주의사항

* NodeMCU의 3.3V 또는 5V 핀만으로 서보모터 여러 개를 직접 구동하지 않는 것이 좋습니다.
* 서보모터는 별도의 5V 외부 전원을 사용하는 것을 권장합니다.
* NodeMCU GND와 서보모터 외부 전원 GND는 반드시 공통으로 연결해야 합니다.
* 스텝모터는 NodeMCU에 직접 연결하지 않고 모터 드라이버를 통해 제어해야 합니다.
* 컨베이어 모터 전원과 NodeMCU 전원을 분리하되, 신호 기준을 맞추기 위해 GND는 공통으로 연결합니다.
* 모터 동작 중 전류 부족이 발생하면 NodeMCU가 재부팅될 수 있으므로 전원 용량을 충분히 확보해야 합니다.
* 플랩이 열리고 닫힐 때 컨베이어 벨트, 분류 통, 쓰레기 이동 경로와 간섭이 없는지 확인해야 합니다.

---

## 11. 문제 해결

| 문제                      | 원인                   | 해결 방법                            |
| ----------------------- | -------------------- | -------------------------------- |
| 웹캠이 열리지 않음              | 카메라 번호 오류            | `--camera 1`, `--camera 2`로 변경   |
| YOLO 모델 파일을 찾을 수 없음     | 모델 경로 오류             | `--model weights/best.pt` 경로 확인  |
| MQTT 연결 실패              | Host, Port, 계정 정보 오류 | MQTT 설정값 재확인                     |
| NodeMCU가 Wi-Fi에 연결되지 않음 | SSID 또는 비밀번호 오류      | Wi-Fi 정보 확인                      |
| NodeMCU가 MQTT 메시지를 못 받음 | Topic 불일치            | 노트북과 NodeMCU의 Topic을 동일하게 설정     |
| 서보모터가 움직이지 않음           | 전원 부족 또는 핀 설정 오류     | 외부 5V 전원 사용, GND 공통 연결           |
| 플랩이 반대로 움직임             | 열림/닫힘 각도 반대          | `OPEN_ANGLE`, `CLOSE_ANGLE` 값 조정 |
| 컨베이어 방향이 반대             | DIR 설정 반대            | `STEP_DIR_VALUE` 변경              |
| 분류 타이밍이 맞지 않음           | 지연 시간 설정 문제          | `OPEN_DELAY_MS` 값 조정             |

---

## 12. 보안 주의사항

다음 정보는 GitHub에 그대로 업로드하지 않는 것이 좋습니다.

```text
Wi-Fi SSID
Wi-Fi Password
MQTT Host
MQTT Username
MQTT Password
```

실제 공개 저장소에 업로드할 때는 예시값으로 변경하거나, 별도 설정 파일을 사용하고 `.gitignore`에 추가하는 것을 권장합니다.

예시:

```text
.env
config.local.h
secrets.h
```

---

