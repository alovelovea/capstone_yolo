import cv2
import os
from ultralytics import YOLO

# 1. 경로 설정
model_path = r"C:\Users\alswo\Desktop\combined_data_v2\runs\detect\waste_project\yolo11n_v1_balanced\weights\best.pt"
source_dir = r"C:\Users\alswo\Desktop\combined_data_v2\testdata"

# 2. 초기 설정
model = YOLO(model_path)
img_files = [f for f in os.listdir(source_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
img_idx = 0
conf_threshold = 0.5  # 초기 임계값

if not img_files:
    print("폴더에 이미지 파일이 없습니다!")
    exit()

print("\n" + "="*40)
print("  [단축키 안내]")
print("  - → (오른쪽 화살표): 다음 사진")
print("  - ← (왼쪽 화살표): 이전 사진")
print("  - ↑ (위쪽 화살표): 임계값 증가 (+0.05)")
print("  - ↓ (아래쪽 화살표): 임계값 감소 (-0.05)")
print("  - q: 프로그램 종료")
print("="*40 + "\n")

while True:
    # 이미지 로드 및 탐지
    img_path = os.path.join(source_dir, img_files[img_idx])
    results = model.predict(source=img_path, conf=conf_threshold, verbose=False)
    
    # 결과 시각화
    annotated_frame = results[0].plot()
    
    # --- [크기 조절 코드 추가] ---
    # 원본 이미지의 가로, 세로 크기 가져오기
    h, w = annotated_frame.shape[:2]
    
    # 원하는 가로 크기 설정 (예: 1024 또는 1280)
    target_width = 1024 
    # 비율에 맞춘 세로 크기 계산
    target_height = int(h * (target_width / w))
    
    # 이미지 리사이징
    display_frame = cv2.resize(annotated_frame, (target_width, target_height))
    # ---------------------------

    # 상태 정보 표시 (리사이징된 이미지 위에 출력)
    info_text = f"[{img_idx+1}/{len(img_files)}] {img_files[img_idx]} | Conf: {conf_threshold:.2f}"
    cv2.putText(display_frame, info_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    # 화면 출력 (annotated_frame 대신 display_frame을 사용합니다)
    cv2.imshow("Waste Detection Test (Interactive)", display_frame)
    
    # 키 입력 처리
    key = cv2.waitKeyEx(0) # 화살표 키 인식을 위해 waitKeyEx 사용
    
    if key == ord('q'): # q: 종료
        break
    elif key == 0x270000 or key == ord('d'): # 오른쪽 화살표: 다음
        img_idx = (img_idx + 1) % len(img_files)
    elif key == 0x250000 or key == ord('a'): # 왼쪽 화살표: 이전
        img_idx = (img_idx - 1) % len(img_files)
    elif key == 0x260000 or key == ord('w'): # 위쪽 화살표: 임계값 UP
        conf_threshold = min(1.0, conf_threshold + 0.02)
    elif key == 0x280000 or key == ord('s'): # 아래쪽 화살표: 임계값 DOWN
        conf_threshold = max(0.0, conf_threshold - 0.02)

cv2.destroyAllWindows()