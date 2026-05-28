import cv2
from ultralytics import YOLO
import torch
import time
import os
from collections import Counter

def main():
    
    import logging
    logging.getLogger("ultralytics").setLevel(logging.ERROR)

    # Check for GPU availability
    device = '0' if torch.cuda.is_available() else 'cpu'
    if device == '0':
        print(f"Using GPU: {torch.cuda.get_device_name(0)}")
    else:
        print("GPU not found. Using CPU.")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(script_dir, "weights", "best.pt")
    
    try:
        model = YOLO(model_path)
        print(f"Model loaded successfully from: {model_path}")
    except Exception as e:
        print(f"Error loading model: {e}")
        return

    # Open the camera
    camera_index = 0
    cap = cv2.VideoCapture(camera_index)
    
    if not cap.isOpened():
        print(f"Error: Could not open camera with index {camera_index}.")
        return

    # 카메라 입력 해상도 고정
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    print("Starting stabilized detection with tracking (Conf 0.4)... Press 'q' to quit.")

    # 시간 측정 및 다수결 투표를 위한 변수
    interval_seconds = 3.0
    start_time = time.time()
    detected_classes_buffer = []

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture image.")
            break

        # Run inference with Tracking (ByteTrack)
        results = model.track(
            frame, 
            persist=True, 
            device=device, 
            verbose=False, 
            tracker="bytetrack.yaml",
            conf=0.4
        )

        # 현재 프레임 탐지 데이터 버퍼링
        for r in results:
            if r.boxes is not None:
                for box in r.boxes:
                    class_id = int(box.cls[0])
                    class_name = model.names[class_id]
                    detected_classes_buffer.append(class_name)

        # Plot results
        annotated_frame = frame.copy()
        for r in results:
            annotated_frame = r.plot(labels=True, boxes=True, conf=True)

        cv2.imshow("YOLO Waste Detection Tracking (GPU)", annotated_frame)

        # 3초마다 다수결 정산
        current_time = time.time()
        if current_time - start_time >= interval_seconds:
            print(f"\n--- [{interval_seconds}초 동안의 탐지 데이터 정산] ---")
            
            if detected_classes_buffer:
                counts = Counter(detected_classes_buffer)
                stat_string = ", ".join([f"{k}:{v}" for k, v in counts.items()])
                print(f"누적 데이터 -> {stat_string}")
                
                final_decision = counts.most_common(1)[0][0]
                print(f"📢 최종 분류 결과: ★ {final_decision.upper()} ★")
            else:
                print("탐지된 물체가 없습니다.")
            
            print("-" * 40)
            start_time = current_time
            detected_classes_buffer = []

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
