#pip uninstall torch torchvision torchaudio (삭제 후)
#pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 (gpu쓰려면)
from ultralytics import YOLO
import torch

# 1. GPU 장치 확인 (RTX 2060 사용 가능 여부 출력)
device = "0" if torch.cuda.is_available() else "cpu"
print(f"--- 학습 시작 장치: {device} ---")

# 2. YOLO11n 모델 로드 (Pre-trained weight 사용)
model = YOLO('yolo11n.pt') 

# 3. 모델 학습 시작
if __name__ == '__main__':
    results = model.train(
        # 데이터 경로 설정 (yaml 파일 경로)
        data=r"C:\Users\alswo\Desktop\combined_data_v2\balanced_dataset\dataset.yaml",
        
        # [학습 기본 설정]
        epochs=100,         # 성능 정체 시 조기 종료되므로 넉넉히 100회 설정
        imgsz=640,          # 표준 이미지 크기
        batch=16,           # RTX 2060 12GB 메모리 최적 크기
        workers=8,          # i5-12500 12스레드 중 8개 활용 (데이터 로딩)
        device=device,      # GPU 사용
        patience=15,        # 20 에포크 동안 성능 향상 없으면 자동 중단
        
        # [데이터 증강 (Augmentation) - 쓰레기 환경 최적화]
        hsv_h=0.015,        # 색조 변경
        hsv_s=0.7,          # 채도 변경
        hsv_v=0.4,          # 명도 변경 (조명 대비)
        degrees=15.0,       # 무작위 회전 (바닥에 놓인 쓰레기 대응)
        translate=0.1,      # 위치 이동
        scale=0.5,          # 확대/축소
        fliplr=0.5,         # 좌우 반전
        mosaic=1.0,         # 4장 합치기 (작은 객체 탐지 강화)
        mixup=0.1,          # 객체 겹침 대비 (중첩된 쓰레기 대응)
        
        # [저장 설정]
        project='waste_project', # 결과물이 저장될 상위 폴더
        name='yolo11n_v1_balanced', # 실험 이름 (runs/waste_project/yolo11n_v1_balanced)
        exist_ok=True,      # 동일 이름 폴더가 있어도 덮어쓰기/연속 저장
        
        # [기타 설정]
        pretrained=True,    # 사전 학습 가중치 사용
        optimizer='auto',   # AdamW 등 최적 알고리즘 자동 선택
        val=True,           # 매 에포크마다 valid 데이터로 검증 수행
        verbose=True        # 학습 과정 상세 출력
    )

    print("--- 학습이 완료되었습니다. ---")
    print(f"최종 결과 저장 경로: {results.save_dir}")