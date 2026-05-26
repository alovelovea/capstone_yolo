# pip install phao-mqtt

import ssl
import paho.mqtt.client as mqtt

MQTT_HOST = "host"
MQTT_PORT = port
MQTT_USERNAME = "username"
MQTT_PASSWORD = "passwd"
MQTT_TOPIC = "topic"


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("MQTT 서버 연결 성공")
    else:
        print(f"MQTT 연결 실패: {reason_code}")


client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id="laptop_detector"
)

client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
client.tls_set(cert_reqs=ssl.CERT_REQUIRED)
client.on_connect = on_connect
client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
client.loop_start()

try:
    while True:
        label = input("보낼 분류값 입력(can/pet/plastic/glass, 종료=q): ").strip()

        if label.lower() == "q":
            break

        if not label:
            continue

        info = client.publish(
            MQTT_TOPIC,
            payload=label,
            qos=1
        )
        info.wait_for_publish()

        print(f"전송 완료: {MQTT_TOPIC} -> {label}")

finally:
    client.loop_stop()
    client.disconnect()
    print("MQTT 연결 종료")