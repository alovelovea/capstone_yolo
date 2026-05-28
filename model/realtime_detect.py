import cv2
from ultralytics import YOLO
import torch
import sys
import time
from collections import Counter

def main():
    # 1. Suppress YOLO verbose output to clean up terminal
    import logging
    logging.getLogger("ultralytics").setLevel(logging.ERROR)

    # Check for GPU availability
    device = '0' if torch.cuda.is_available() else 'cpu'
    if device == '0':
        print(f"Using GPU: {torch.cuda.get_device_name(0)}")
    else:
        print("GPU not found. Using CPU.")

    # Load the model using the EXACT absolute path
    model_path = r"C:\Users\alswo\Desktop\study\26-1\capstone\newf\runs\detect\waste_project\yolo11n_v1_balanced\weights\best.pt"
    
    try:
        model = YOLO(model_path)
        print("Model loaded successfully.")
    except Exception as e:
        print(f"Error loading model: {e}")
        return

    # Open the camera
    camera_index = 0
    cap = cv2.VideoCapture(camera_index)
    
    if not cap.isOpened():
        print(f"Error: Could not open camera with index {camera_index}.")
        return

    # --- [추가] 카메라 입력 해상도를 640x480으로 고정 ---
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    # 설정된 해상도가 잘 적용되었는지 확인 출력
    actual_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    actual_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    print(f"Camera resolution set to: {int(actual_width)}x{int(actual_height)}")

    print("Starting stabilized detection with tracking (Conf 0.4)... Press 'q' to quit.")

    # --- 시간 측정 및 다수결 투표를 위한 변수 초기화 ---
    interval_seconds = 3.0  # 정산 주기 (몇 초 단위로 모아서 분류할지 설정)
    start_time = time.time()
    detected_classes_buffer = []  # 지정된 시간 동안 탐지된 클래스 이름을 모을 리스트

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

        # 현재 프레임에서 탐지된 물체들의 이름을 버퍼에 저장
        for r in results:
            if r.boxes is not None:
                for box in r.boxes:
                    class_id = int(box.cls[0])
                    class_name = model.names[class_id]
                    detected_classes_buffer.append(class_name)

        # Plot results on the frame
        annotated_frame = frame.copy()
        for r in results:
            annotated_frame = r.plot(labels=True, boxes=True, conf=True)

        # Display the frame
        cv2.imshow("YOLO Waste Detection Tracking (GPU)", annotated_frame)

        # --- 지정된 시간이 지나면 다수결 정산 수행 ---
        current_time = time.time()
        if current_time - start_time >= interval_seconds:
            print(f"\n--- [{interval_seconds}초 동안의 탐지 데이터 정산] ---")
            
            if detected_classes_buffer:
                # 1. 각 클래스별 등장 횟수 카운트
                counts = Counter(detected_classes_buffer)
                
                # 2. 터미널에 누적된 탐지 통계 출력
                stat_string = ", ".join([f"{k}:{v}" for k, v in counts.items()])
                print(f"누적 데이터 -> {stat_string}")
                
                # 3. 가장 많이 등장한 클래스 추출 (최종 분류)
                final_decision = counts.most_common(1)[0][0]
                print(f"📢 최종 분류 결과: ★ {final_decision.upper()} ★")
            else:
                print("탐지된 물체가 없습니다.")
                
            print("-" * 40)
            
            # 변수 초기화 (다음 주기를 위해 다시 세팅)
            start_time = current_time
            detected_classes_buffer = []

        # Break the loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()