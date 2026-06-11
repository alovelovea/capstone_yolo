# ♻️ AI 기반 쓰레기 분리배출 자동화 프로젝트

## 📌 1. 프로젝트 개요

>지속 가능한 환경을 조성하기 위해 올바른 분리배출은 필수적이지만, 실생활에서는 복잡한 분류 기준으로 인해 혼동이 자주 발생합니다.
>
>본 프로젝트는 분리배출 과정의 혼동을 줄이고 효율을 높이기 위해, **딥러닝 객체 탐지(Object Detection) 모델을 활용하여 쓰레기 종류를 실시간으로 식별하고 분류하는 자동화 시스템 구축**을 목표로 합니다.
>
>최종 시스템은 노트북에 연결된 웹캠으로 컨베이어 벨트 위의 쓰레기를 촬영하고, YOLO 모델을 통해 쓰레기 종류를 인식합니다. 이후 인식 결과를 MQTT를 통해 NodeMCU로 전송하고, NodeMCU는 수신한 분류 결과에 따라 서보모터를 제어하여 쓰레기가 지정된 분류 통으로 이동하도록 합니다.
>
>이를 통해 사용자의 판단 부담을 줄이고, 보다 정확하고 일관된 분리배출 환경을 실현하고자 합니다.

---

## 🎯 2. 프로젝트 목표

본 프로젝트의 주요 목표는 다음과 같습니다.

| 구분      | 내용                                      |
| ------- | --------------------------------------- |
| 객체 인식   | 웹캠 영상을 기반으로 YOLO 모델을 이용하여 쓰레기 종류 탐지     |
| 데이터 구축  | 공개 데이터셋과 자체 촬영 데이터를 결합하여 학습 데이터 구성      |
| 모델 학습   | YOLOv11 기반 쓰레기 객체 탐지 모델 학습              |
| 실시간 추론  | 노트북에서 웹캠 영상을 입력받아 실시간 객체 인식 수행          |
| MQTT 연동 | YOLO 예측 결과를 MQTT Broker를 통해 NodeMCU로 전송 |
| 하드웨어 제어 | NodeMCU가 분류 결과에 따라 서보모터 및 플랩 제어         |
| 자동 분류   | 컨베이어 벨트 위의 쓰레기를 지정된 분류 통으로 이동           |

---

## 🧩 3. 시스템 전체 구조

본 프로젝트는 크게 **모델 학습 및 추론 파트**와 **하드웨어 제어 파트**로 구성됩니다.

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

### 시스템 구조도

![Hardware Architecture](./hardware/assets/hardware_architecture.png)

---

## 📦 4. 데이터 수집 및 구성

모델의 일반화 성능을 높이기 위해 다양한 경로로 데이터를 확보하여 데이터셋의 신뢰도를 높였습니다.

### 4.1 온라인 데이터 수집

* Roboflow, AI Hub 등 검증된 공개 데이터셋에서 기초 이미지 데이터를 확보하였습니다.
* 수집한 데이터를 검토하고 본 프로젝트의 분류 기준에 맞춰 직접 라벨링하는 과정을 거쳐 보다 정확한 데이터셋을 구축하였습니다.

### 4.2 팀 자체 수집

* 프로젝트의 실용성을 더하기 위해 **팀원들이 직접 일상 속 쓰레기 사진을 촬영하고 수집**하였습니다.
* 배경, 조명 조건, 쓰레기 훼손 상태 등을 다양하게 구성하여 실제 현장에서 발생할 수 있는 변수를 데이터에 반영함으로써 현실성과 신뢰도를 높였습니다.

#### 수집 예시

<img width="900" height="350" alt="스크린샷 2026-06-02 162536" src="https://github.com/user-attachments/assets/2a1a99fb-27ed-49bf-a746-b6e03c7273a8" />

---

## 🗂️ 5. 데이터셋

프로젝트에 사용된 데이터는 용량 문제로 외부 링크를 통해 공유합니다.

> 다운로드 후 프로젝트 루트 디렉토리에 압축을 풀어주세요.

### 5.1 원본 데이터

* **[origin_data 원본 데이터](https://drive.google.com/file/d/18MwHgJrD6e6gEyg-UQ8ioq3swS5PRxqO/view?usp=sharing)**
* 클래스별 원본 데이터셋입니다.
* 다운로드 후 폴더명을 `origin_data`로 저장합니다.

<img width="263" height="367" alt="origin_data" src="https://github.com/user-attachments/assets/f39bd96b-ad55-4499-853e-59e420e1f782" />

### 5.2 학습용 데이터

* **[balanced_dataset 학습용 데이터](https://drive.google.com/file/d/1gjMSW88cVNjefXdec7jtSDDiZuRfjYjU/view?usp=sharing)**
* Train/Validation 분할 및 YOLO 형식 변환이 완료된 데이터셋입니다.
* 다운로드 후 폴더명을 `balanced_dataset`으로 저장합니다.

<img width="268" height="29" alt="balanced_dataset" src="https://github.com/user-attachments/assets/d8d53bb5-af26-47d7-99bd-292ceba114a4" />

### 5.3 데이터셋 배치 구조

```text
capstone_yolo/
├── balanced_dataset/
│   ├── train/
│   ├── valid/
│   └── dataset.yaml
└── origin_data/
```

### 5.4 라벨 형식 변환 및 검증

수집 데이터에는 Detection 형식과 Segmentation 형식의 라벨이 혼합되어 있을 수 있으므로, 학습에 적합하도록 YOLO Detection 형식으로 통일하였습니다.

또한 다음과 같은 검증 과정을 수행하였습니다.

* 이미지와 라벨 파일 매칭 여부 확인
* 빈 라벨 파일 검사
* 잘못된 클래스 번호 검사
* 좌표 범위 오류 검사
* Train/Validation 데이터 분포 확인

### 5.5 실시간 추론 및 하드웨어 연동

학습된 YOLO 모델은 노트북에서 실행되며, 웹캠 영상을 실시간으로 입력받아 쓰레기를 탐지합니다.

인식된 클래스는 MQTT 메시지로 변환되어 NodeMCU로 전달되고, NodeMCU는 해당 분류 결과에 맞는 서보모터를 작동시킵니다. 이를 통해 단순히 화면에 예측 결과를 출력하는 것을 넘어, 실제 물리적 분류 동작까지 수행할 수 있도록 구현하였습니다.

---

## 🛠️ 6. 기술 스택

| 구분            | 사용 기술                                                       |
| ------------- | ----------------------------------------------------------- |
| Language      | Python 3.x, Arduino C/C++                                   |
| Model         | YOLOv11, Ultralytics                                        |
| Library       | OpenCV, PyTorch, Albumentations, Pandas, Matplotlib         |
| Hardware      | Webcam, Laptop, NodeMCU ESP8266, Servo Motor, Conveyor Belt |
| Communication | MQTT, HiveMQ Broker                                         |
| Embedded      | Arduino IDE, ESP8266WiFi, PubSubClient, Servo               |
| Environment   | CUDA 12.1 기반 GPU 가속 환경                                      |

---

## 📁 7. 프로젝트 폴더 구조

```text
capstone_yolo/
├── Readme.md
├── requirements.txt
├── .gitignore
├── model/
│   ├── Readme.md
│   ├── preprocessing.py
│   ├── train.py
│   ├── realtime_detect.py
│   ├── results.csv
│   └── yolo11n.pt
├── hardware/
│   ├── README.md
│   ├── laptop_yolo_mqtt_publish.py
│   ├── nodemcu_sorter_final.ino
│   ├── mqtt_publish.py
│   ├── wifi_mqtt_subscribe.ino
│   ├── motor_test.ino
│   └── assets/
│       └── hardware_architecture.png
└── weights/
    └── best.pt
```

---

## 🚀 8. 시작하기

### 8.1 가상환경 생성 및 활성화

```bash
python -m venv venv
```

Windows 환경:

```bash
.\venv\Scripts\activate
```

macOS/Linux 환경:

```bash
source venv/bin/activate
```

### 8.2 필수 라이브러리 설치

```bash
pip install -r requirements.txt
```

하드웨어 연동 코드 실행에 필요한 주요 라이브러리는 다음과 같습니다.

```bash
pip install ultralytics opencv-python paho-mqtt
```

---

## 🤖 9. 모델 워크플로우

모델 관련 코드는 `model` 폴더에 정리되어 있습니다.

> 본 모델의 워크플로우에 대한 기술적 상세 내용은 [여기](https://github.com/alovelovea/capstone_yolo/blob/minjae/model/Readme.md#--model-workflow)를 클릭하여 확인해 주세요.

```text
model/
├── preprocessing.py
├── train.py
├── realtime_detect.py
├── results.csv
└── yolo11n.pt
```

### 9.1 데이터 전처리

`preprocessing.py`는 데이터셋 구성, Train/Validation 분할, 라벨 형식 변환, 데이터 무결성 검사, 데이터 증강 등을 수행합니다.

### 9.2 모델 학습

`train.py`는 YOLOv11n 사전학습 가중치를 기반으로 프로젝트 데이터셋을 학습합니다.

### 9.3 실시간 탐지

`realtime_detect.py`는 학습된 모델을 사용하여 이미지 또는 영상에서 쓰레기 객체를 탐지하는 코드입니다.

---

## ⚙️ 10. 하드웨어 워크플로우

하드웨어 관련 코드는 `hardware` 폴더에 정리되어 있습니다.
[
> 본 하드웨어 워크플로우에 대한 기술적 상세 내용은 [여기](https://github.com/alovelovea/capstone_yolo/tree/main/hardware)https://github.com/alovelovea/capstone_yolo/blob/minjae/hardware/README.md#%EF%B8%8F-hardware-workflow)를 클릭하여 확인해 주세요.

```text
hardware/
├── laptop_yolo_mqtt_publish.py
├── nodemcu_sorter_final.ino
├── mqtt_publish.py
├── wifi_mqtt_subscribe.ino
└── motor_test.ino
```

### 10.1 최종 하드웨어 연동 코드

최종 시스템에서는 노트북에서 웹캠 영상을 입력받아 YOLO 모델로 쓰레기를 탐지하고, 탐지 결과를 MQTT를 통해 NodeMCU로 전송합니다.

NodeMCU는 `sorter/command` 토픽을 구독하고 있으며, 수신한 분류값에 따라 지정된 서보모터를 작동시켜 분류 플랩을 개폐합니다.

| 파일명                           | 설명                                 |
| ----------------------------- | ---------------------------------- |
| `laptop_yolo_mqtt_publish.py` | 웹캠 영상 입력, YOLO 추론, MQTT 분류 결과 전송   |
| `nodemcu_sorter_final.ino`    | MQTT 명령 수신, 컨베이어 구동, 서보모터 기반 플랩 제어 |
| `mqtt_publish.py`             | MQTT 송신 단독 테스트 코드                  |
| `wifi_mqtt_subscribe.ino`     | NodeMCU Wi-Fi 및 MQTT 수신 테스트 코드     |
| `motor_test.ino`              | 컨베이어 스텝모터 구동 테스트 코드                |

### 10.2 하드웨어 동작 방식

```text
1. 웹캠이 컨베이어 벨트 위의 쓰레기 영상을 촬영
2. 노트북에서 YOLO 모델이 객체 탐지
3. 탐지된 클래스명을 MQTT 메시지로 발행
4. NodeMCU가 MQTT 메시지 수신
5. 분류 결과에 맞는 서보모터 작동
6. 플랩이 열리며 쓰레기가 해당 분류 통으로 낙하
7. 플랩이 닫히고 다음 분류 준비
```

---

## ▶️ 11. 실행 방법

### 11.1 NodeMCU 코드 업로드

Arduino IDE에서 다음 파일을 엽니다.

```text
hardware/nodemcu_sorter_final.ino
```

아래 설정값을 실제 환경에 맞게 수정합니다.

```cpp
const char* WIFI_SSID = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";

const char* MQTT_HOST = "YOUR_MQTT_HOST";
const int   MQTT_PORT = 8883;

const char* MQTT_USERNAME = "YOUR_MQTT_USERNAME";
const char* MQTT_PASSWORD = "YOUR_MQTT_PASSWORD";
```

보드 설정 예시는 다음과 같습니다.

```text
Board: NodeMCU 1.0 (ESP-12E Module)
Port: 사용 중인 COM 포트
Upload Speed: 115200
```

업로드 후 시리얼 모니터를 열어 Wi-Fi 및 MQTT 연결 상태를 확인합니다.

### 11.2 노트북 YOLO + MQTT 코드 실행

학습된 모델 가중치 파일을 준비합니다.

```text
weights/best.pt
```

노트북에서 다음 명령어를 실행합니다.

```bash
python hardware/laptop_yolo_mqtt_publish.py --model weights/best.pt --camera 0
```

웹캠이 여러 개 연결되어 있다면 `--camera 1` 또는 `--camera 2`로 변경하여 실행합니다.

---

## 📡 12. MQTT Topic 구조

| Topic            | 방향                    | 설명                         |
| ---------------- | --------------------- | -------------------------- |
| `sorter/command` | 노트북 → NodeMCU         | YOLO 분류 결과 전송              |
| `sorter/status`  | NodeMCU → MQTT Broker | NodeMCU 상태 및 서보모터 동작 상태 전송 |

예시 메시지:

```text
sorter/command -> can
sorter/command -> pet
sorter/command -> plastic
sorter/command -> glass
sorter/command -> paper
```

---

## ✅ 13. 최종 동작 예시

```text
[YOLO] detected: can
[MQTT] publish: sorter/command -> can
[NodeMCU] received: can
[Servo] can flap open
[Sorter] can waste dropped into can bin
[Servo] can flap close
```

---

## ⚠️ 14. 주의사항

* MQTT 접속 정보, Wi-Fi SSID, 비밀번호는 GitHub에 그대로 업로드하지 않는 것이 좋습니다.
* 실제 업로드 시에는 예시값 또는 별도 설정 파일을 사용하는 것을 권장합니다.
* 서보모터 여러 개를 NodeMCU 전원핀에서 직접 구동하면 전류가 부족할 수 있습니다.
* 서보모터는 별도 5V 전원을 사용하고, NodeMCU GND와 서보모터 전원 GND는 반드시 공통으로 연결해야 합니다.
* 컨베이어 모터는 NodeMCU에 직접 연결하지 말고 모터 드라이버를 통해 제어해야 합니다.
* 플랩이 열리고 닫힐 때 컨베이어 벨트나 쓰레기 이동 경로와 간섭이 없는지 확인해야 합니다.
* 최종 통합 테스트 전에는 MQTT 송수신 테스트, 모터 테스트, 서보모터 테스트를 각각 먼저 수행하는 것이 좋습니다.
* `.gitignore` 설정을 통해 대용량 데이터 폴더와 캐시 파일(`*.cache`)이 저장소에 업로드되지 않도록 관리하고 있습니다.
* 데이터셋을 로컬에서 실행할 경우, 반드시 상단 링크에서 데이터를 다운로드하여 프로젝트 구조에 맞게 배치해야 합니다.


