import cv2
import os
from pathlib import Path
from ultralytics import YOLO

# =========================================================
# 기본 경로 설정
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

default_model_path = (
    BASE_DIR / "weights" / "best.pt"
)

source_dir = BASE_DIR / "testdata"

# =========================================================
# 모델 경로 입력
# =========================================================

print("\n================================================")
print("YOLO Waste Detection")
print("================================================")

custom_path = input(
    "\n사용할 best.pt 경로 입력 "
    "(엔터 시 기본 모델 사용): "
).strip()

# 엔터 입력 시 기본 모델 사용
if custom_path == "":
    model_path = default_model_path

else:
    model_path = Path(custom_path)

# =========================================================
# 경로 검사
# =========================================================

if not model_path.exists():

    raise FileNotFoundError(
        f"\n[ERROR] 모델 파일 없음:\n{model_path}"
    )

if not source_dir.exists():

    raise FileNotFoundError(
        f"\n[ERROR] testdata 폴더 없음:\n{source_dir}"
    )

# =========================================================
# 모델 로드
# =========================================================

print(f"\n[INFO] 모델 로드 중...")
print(f"[INFO] 모델 경로: {model_path}")

model = YOLO(str(model_path))

print("[OK] 모델 로드 완료")

# =========================================================
# 이미지 로드
# =========================================================

img_files = [

    f for f in os.listdir(source_dir)

    if f.lower().endswith(
        ('.png', '.jpg', '.jpeg')
    )
]

if not img_files:

    raise ValueError(
        "\n[ERROR] testdata 폴더에 이미지 없음"
    )

img_idx = 0
conf_threshold = 0.5

# =========================================================
# 단축키 안내
# =========================================================

print("\n================================================")
print("[단축키 안내]")
print("→ / d : 다음 이미지")
print("← / a : 이전 이미지")
print("↑ / w : threshold 증가")
print("↓ / s : threshold 감소")
print("q      : 종료")
print("================================================")

# =========================================================
# 추론 루프
# =========================================================

while True:

    img_path = os.path.join(
        source_dir,
        img_files[img_idx]
    )

    results = model.predict(
        source=img_path,
        conf=conf_threshold,
        verbose=False
    )

    annotated_frame = results[0].plot()

    h, w = annotated_frame.shape[:2]

    target_width = 1024

    target_height = int(
        h * (target_width / w)
    )

    display_frame = cv2.resize(
        annotated_frame,
        (target_width, target_height)
    )

    info_text = (
        f"[{img_idx+1}/{len(img_files)}] "
        f"{img_files[img_idx]} "
        f"| Conf: {conf_threshold:.2f}"
    )

    cv2.putText(
        display_frame,
        info_text,
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2
    )

    cv2.imshow(
        "Waste Detection",
        display_frame
    )

    key = cv2.waitKeyEx(0)

    if key == ord('q'):
        break

    elif key == 0x270000 or key == ord('d'):
        img_idx = (img_idx + 1) % len(img_files)

    elif key == 0x250000 or key == ord('a'):
        img_idx = (img_idx - 1) % len(img_files)

    elif key == 0x260000 or key == ord('w'):
        conf_threshold = min(
            1.0,
            conf_threshold + 0.02
        )

    elif key == 0x280000 or key == ord('s'):
        conf_threshold = max(
            0.0,
            conf_threshold - 0.02
        )

cv2.destroyAllWindows()