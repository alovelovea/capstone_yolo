# pip uninstall torch torchvision torchaudio
# pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

from pathlib import Path

from ultralytics import YOLO
import torch

# =========================================================
# 경로 설정
# =========================================================

# 현재 파일: model/train.py
BASE_DIR = Path(__file__).resolve().parent.parent

# model 폴더
MODEL_DIR = BASE_DIR / "model"

# dataset.yaml 경로
DATASET_YAML = BASE_DIR / "balanced_dataset" / "dataset.yaml"

# =========================================================
# GPU 확인
# =========================================================

device = "0" if torch.cuda.is_available() else "cpu"

print(f"--- 학습 시작 장치: {device} ---")

# =========================================================
# 모델 로드
# =========================================================

model = YOLO(str(MODEL_DIR / "yolo11n.pt"))

# =========================================================
# 학습 시작
# =========================================================

if __name__ == '__main__':

    results = model.train(

        # =================================================
        # 데이터 경로
        # =================================================

        data=str(DATASET_YAML),

        # =================================================
        # 학습 기본 설정
        # =================================================

        epochs=100,

        imgsz=640,

        batch=16,

        workers=8,

        device=device,

        patience=15,

        # =================================================
        # Augmentation
        # =================================================

        hsv_h=0.015,
        hsv_s=0.7,
        hsv_v=0.4,

        degrees=15.0,

        translate=0.1,

        scale=0.5,

        fliplr=0.5,

        mosaic=1.0,

        mixup=0.1,

        # =================================================
        # 저장 설정
        # =================================================

        project=str(MODEL_DIR / "weights"),

        name='yolo11n_v1_balanced',

        exist_ok=True,

        # =================================================
        # 기타 설정
        # =================================================

        pretrained=True,
        project=str(MODEL_DIR / "runs" / "detect"),

        name='waste_project/yolo11n_v1_balanced',
        optimizer='auto',

        val=True,

        verbose=True
    )

    print("\n--- 학습이 완료되었습니다. ---")

    print("최종 결과 저장 경로:")
    print(results.save_dir)