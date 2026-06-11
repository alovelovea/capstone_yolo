import argparse
import ssl
import time
from pathlib import Path

import cv2
import paho.mqtt.client as mqtt
from ultralytics import YOLO


"""
노트북 최종 YOLO + 웹캠 + MQTT 송신 코드

동작 흐름:
1. 웹캠 연결
2. YOLO 모델 로드
3. 실시간 객체 탐지
4. 객체가 화면에서 사라진 뒤 마지막 안정적인 분류 결과를 MQTT로 전송
5. NodeMCU는 수신 후 2초 뒤 해당 플랩을 5초 동안 개방

설치:
pip install ultralytics opencv-python paho-mqtt

실행 예:
python hardware/laptop_yolo_mqtt_publish.py --model weights/best.pt --camera 0
"""


# ===================== MQTT 기본 설정 =====================
MQTT_HOST = "YOUR_MQTT_HOST"
MQTT_PORT = 8883

MQTT_USERNAME = "YOUR_MQTT_USERNAME"
MQTT_PASSWORD = "YOUR_MQTT_PASSWORD"

MQTT_CLIENT_ID = "laptop-yolo-publisher-001"
MQTT_COMMAND_TOPIC = "sorter/command"


# ===================== YOLO / 웹캠 설정 =====================
DEFAULT_MODEL_PATH = "weights/best.pt"
DEFAULT_CAMERA_INDEX = 0

CONF_THRESHOLD = 0.50
IMG_SIZE = 640

# 같은 물체를 너무 자주 보내지 않기 위한 쿨타임
PUBLISH_COOLDOWN_SEC = 2.0

# 물체가 최소 몇 초 이상 보여야 유효한 탐지로 볼지
MIN_STABLE_SEC = 0.3

# 물체가 화면에서 사라진 뒤 몇 초 후 MQTT를 보낼지
DISAPPEAR_GRACE_SEC = 0.4

# True:
#   물체가 보이는 동안 계속 보내지 않고,
#   물체가 화면에서 사라진 뒤 마지막 분류값을 1회 전송
#
# False:
#   탐지되는 즉시 전송
PUBLISH_WHEN_DISAPPEARED = True


# ===================== 클래스명 매핑 =====================
# YOLO 모델의 class name이 아래와 다르면 여기를 수정하세요.
# 예: 모델이 "PET Bottle"이라고 출력하면 "pet bottle": "pet" 추가
CLASS_TO_COMMAND = {
    "can": "can",
    "cans": "can",
    "metal": "can",

    "pet": "pet",
    "bottle": "pet",
    "pet_bottle": "pet",
    "plastic_bottle": "pet",

    "plastic": "plastic",
    "vinyl": "plastic",
    "vinyl_bag": "plastic",

    "glass": "glass",
    "glass_bottle": "glass",

    "paper": "paper",
    "cardboard": "paper",
    
    "plasticbag": "plasticbag",
}

ALLOWED_COMMANDS = {"can", "pet", "plastic", "glass", "paper", "plasticbag"}


def normalize_class_name(raw_name: str) -> str | None:
    name = raw_name.strip().lower()
    name = name.replace(" ", "_")
    return CLASS_TO_COMMAND.get(name)


def create_mqtt_client() -> mqtt.Client:
    client = mqtt.Client(
        client_id=MQTT_CLIENT_ID,
        protocol=mqtt.MQTTv311,
    )

    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    if MQTT_PORT == 8883:
        client.tls_set(tls_version=ssl.PROTOCOL_TLS_CLIENT)

        # 인증서 문제가 생길 때만 True로 바꾸세요.
        # HiveMQ Cloud의 일반적인 TLS 인증서는 False로 두는 것이 좋습니다.
        client.tls_insecure_set(False)

    return client


def connect_mqtt(client: mqtt.Client) -> None:
    print("[MQTT] Broker 연결 중...")
    client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
    client.loop_start()
    print("[MQTT] 연결 완료")


def publish_command(client: mqtt.Client, command: str) -> None:
    if command not in ALLOWED_COMMANDS:
        print(f"[MQTT] 허용되지 않은 분류값: {command}")
        return

    result = client.publish(
        MQTT_COMMAND_TOPIC,
        payload=command,
        qos=1,
        retain=False,
    )

    result.wait_for_publish()

    print(f"[MQTT] publish: {MQTT_COMMAND_TOPIC} -> {command}")


def open_camera(camera_index: int) -> cv2.VideoCapture:
    # Windows에서는 CAP_DSHOW를 쓰면 웹캠 지연이 줄어드는 경우가 많음
    cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)

    if not cap.isOpened():
        # CAP_DSHOW로 실패하면 기본 방식으로 재시도
        cap = cv2.VideoCapture(camera_index)

    if not cap.isOpened():
        raise RuntimeError(f"웹캠을 열 수 없습니다. camera index: {camera_index}")

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    return cap


def get_best_detection(result, names: dict) -> tuple[str | None, float]:
    best_command = None
    best_conf = 0.0

    if result.boxes is None:
        return None, 0.0

    for box in result.boxes:
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])

        if conf < CONF_THRESHOLD:
            continue

        raw_name = names.get(cls_id, str(cls_id))
        command = normalize_class_name(raw_name)

        if command is None:
            continue

        if conf > best_conf:
            best_conf = conf
            best_command = command

    return best_command, best_conf


def draw_status(frame, status_lines: list[str]) -> None:
    x = 20
    y = 35

    for line in status_lines:
        cv2.putText(
            frame,
            line,
            (x, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2,
            cv2.LINE_AA,
        )
        y += 35


def run(model_path: str, camera_index: int) -> None:
    model_path_obj = Path(model_path)

    if not model_path_obj.exists():
        raise FileNotFoundError(f"모델 파일을 찾을 수 없습니다: {model_path}")

    print(f"[YOLO] 모델 로드: {model_path}")
    model = YOLO(model_path)

    print(f"[CAMERA] 웹캠 연결: {camera_index}")
    cap = open_camera(camera_index)

    mqtt_client = create_mqtt_client()
    connect_mqtt(mqtt_client)

    current_command = None
    current_first_seen_at = 0.0
    current_last_seen_at = 0.0

    last_publish_at = 0.0
    published_this_cycle = False

    print("[SYSTEM] 실행 시작")
    print("[SYSTEM] 종료하려면 q 키를 누르세요.")

    try:
        while True:
            ret, frame = cap.read()

            if not ret:
                print("[CAMERA] 프레임을 읽지 못했습니다.")
                time.sleep(0.1)
                continue

            now = time.time()

            results = model(
                frame,
                imgsz=IMG_SIZE,
                conf=CONF_THRESHOLD,
                verbose=False,
            )

            result = results[0]
            names = model.names

            best_command, best_conf = get_best_detection(result, names)

            annotated_frame = result.plot()

            if best_command is not None:
                if best_command != current_command:
                    current_command = best_command
                    current_first_seen_at = now
                    published_this_cycle = False

                current_last_seen_at = now

                if not PUBLISH_WHEN_DISAPPEARED:
                    enough_cooldown = now - last_publish_at >= PUBLISH_COOLDOWN_SEC

                    if enough_cooldown and not published_this_cycle:
                        publish_command(mqtt_client, current_command)
                        last_publish_at = now
                        published_this_cycle = True

            else:
                if current_command is not None and PUBLISH_WHEN_DISAPPEARED:
                    disappeared_time = now - current_last_seen_at
                    visible_time = current_last_seen_at - current_first_seen_at
                    enough_cooldown = now - last_publish_at >= PUBLISH_COOLDOWN_SEC

                    should_publish = (
                        not published_this_cycle
                        and disappeared_time >= DISAPPEAR_GRACE_SEC
                        and visible_time >= MIN_STABLE_SEC
                        and enough_cooldown
                    )

                    if should_publish:
                        publish_command(mqtt_client, current_command)
                        last_publish_at = now
                        published_this_cycle = True

                        current_command = None
                        current_first_seen_at = 0.0
                        current_last_seen_at = 0.0

                # 너무 오래 안 보이면 현재 사이클 초기화
                if current_command is not None:
                    if now - current_last_seen_at > 3.0:
                        current_command = None
                        current_first_seen_at = 0.0
                        current_last_seen_at = 0.0
                        published_this_cycle = False

            status_lines = [
                f"Detected: {best_command if best_command else '-'}",
                f"Confidence: {best_conf:.2f}",
                f"Current command: {current_command if current_command else '-'}",
                f"MQTT topic: {MQTT_COMMAND_TOPIC}",
                "Press q to quit",
            ]

            draw_status(annotated_frame, status_lines)

            cv2.imshow("YOLO Waste Sorter", annotated_frame)

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                print("[SYSTEM] 종료 요청")
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()

        mqtt_client.loop_stop()
        mqtt_client.disconnect()

        print("[SYSTEM] 종료 완료")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Laptop webcam YOLO inference and MQTT publisher"
    )

    parser.add_argument(
        "--model",
        type=str,
        default=DEFAULT_MODEL_PATH,
        help="YOLO model path. ex) weights/best.pt",
    )

    parser.add_argument(
        "--camera",
        type=int,
        default=DEFAULT_CAMERA_INDEX,
        help="Webcam index. Usually 0 or 1",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run(args.model, args.camera)