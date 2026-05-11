# plastic_augmentation.py

import random
from pathlib import Path

import cv2
import albumentations as A

# =========================================================
# 설정
# =========================================================

random.seed(42)

BASE_DIR = Path(r"C:\Users\alswo\Desktop\combined_data_v2")

DATASET_DIR = BASE_DIR / "balanced_dataset"

TRAIN_IMAGE_DIR = DATASET_DIR / "images/train"
TRAIN_LABEL_DIR = DATASET_DIR / "labels/train"

TARGET_PLASTIC_TRAIN = 1600

# =========================================================
# augmentation 설정
# =========================================================

transform = A.Compose(

    [

        A.HorizontalFlip(p=0.5),

        A.RandomBrightnessContrast(
            brightness_limit=0.2,
            contrast_limit=0.2,
            p=0.5
        ),

        A.HueSaturationValue(
            hue_shift_limit=10,
            sat_shift_limit=15,
            val_shift_limit=10,
            p=0.5
        ),

        A.GaussianBlur(
            blur_limit=(3, 5),
            p=0.2
        )

    ],

   bbox_params=A.BboxParams(
    format='yolo',
    label_fields=['class_labels'],
    min_visibility=0.1,
    clip=True
)
)

# =========================================================
# 함수
# =========================================================

def read_yolo_label(label_path):

    bboxes = []
    class_labels = []

    try:

        with open(label_path, "r") as f:
            lines = f.readlines()

    except:
        return bboxes, class_labels

    for line in lines:

        parts = line.strip().split()

        if len(parts) != 5:
            continue

        try:

            cls_id = int(parts[0])

            x, y, w, h = map(float, parts[1:])

            # =================================================
            # bbox 범위 검사
            # =================================================

            if (
                x < 0 or x > 1 or
                y < 0 or y > 1 or
                w <= 0 or w > 1 or
                h <= 0 or h > 1
            ):
                continue

            bboxes.append([x, y, w, h])
            class_labels.append(cls_id)

        except:
            continue

    return bboxes, class_labels


def save_yolo_label(label_path, bboxes, class_labels):

    with open(label_path, "w") as f:

        for bbox, cls_id in zip(bboxes, class_labels):

            x, y, w, h = bbox

            f.write(
                f"{cls_id} "
                f"{x:.6f} "
                f"{y:.6f} "
                f"{w:.6f} "
                f"{h:.6f}\n"
            )

# =========================================================
# 기존 augmentation 삭제
# =========================================================

print("\n================================================")
print("[START] 기존 augmentation 삭제")
print("================================================")

old_aug_images = list(
    TRAIN_IMAGE_DIR.glob("plastic_aug_*")
)

old_aug_labels = list(
    TRAIN_LABEL_DIR.glob("plastic_aug_*")
)

for file in old_aug_images:
    file.unlink()

for file in old_aug_labels:
    file.unlink()

print(f"[OK] 삭제된 augmentation image: {len(old_aug_images)}")
print(f"[OK] 삭제된 augmentation label: {len(old_aug_labels)}")

# =========================================================
# plastic 원본 이미지 탐색
# =========================================================

print("\n================================================")
print("[START] PLASTIC AUGMENTATION")
print("================================================")

plastic_images = [

    x for x in TRAIN_IMAGE_DIR.glob("plastic_*")

    if "plastic_aug_" not in x.name
]

print(f"[INFO] 원본 plastic 수: {len(plastic_images)}")

if len(plastic_images) == 0:
    raise ValueError("[ERROR] plastic 이미지 없음")

need_aug = TARGET_PLASTIC_TRAIN - len(plastic_images)

print(f"[INFO] 생성할 augmentation 수: {need_aug}")

if need_aug <= 0:

    print("[INFO] augmentation 불필요")
    exit()

# =========================================================
# augmentation 시작
# =========================================================

success_count = 0
fail_count = 0

for aug_idx in range(need_aug):

    try:

        img_path = random.choice(plastic_images)

        label_path = (
            TRAIN_LABEL_DIR /
            f"{img_path.stem}.txt"
        )

        image = cv2.imread(str(img_path))

        if image is None:

            fail_count += 1
            continue

        image = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2RGB
        )

        bboxes, class_labels = read_yolo_label(label_path)

        if len(bboxes) == 0:

            fail_count += 1
            continue

        # =====================================================
        # augmentation 적용
        # =====================================================

        transformed = transform(
            image=image,
            bboxes=bboxes,
            class_labels=class_labels
        )

        aug_image = transformed["image"]
        aug_bboxes = transformed["bboxes"]
        aug_labels = transformed["class_labels"]

        # =====================================================
        # bbox clipping
        # floating point 오차 방지
        # =====================================================

        fixed_bboxes = []

        for bbox in aug_bboxes:

            x, y, w, h = bbox

            x = max(0.0, min(1.0, x))
            y = max(0.0, min(1.0, y))

            w = max(1e-6, min(1.0, w))
            h = max(1e-6, min(1.0, h))

            fixed_bboxes.append([x, y, w, h])

        aug_bboxes = fixed_bboxes

        # =====================================================
        # bbox 검사
        # =====================================================

        if len(aug_bboxes) == 0:

            fail_count += 1
            continue

        # =====================================================
        # 이미지 저장용 변환
        # =====================================================

        aug_image = cv2.cvtColor(
            aug_image,
            cv2.COLOR_RGB2BGR
        )

        # =====================================================
        # 저장 경로
        # =====================================================

        save_img_name = f"plastic_aug_{aug_idx}.jpg"
        save_label_name = f"plastic_aug_{aug_idx}.txt"

        save_img_path = TRAIN_IMAGE_DIR / save_img_name
        save_label_path = TRAIN_LABEL_DIR / save_label_name

        # =====================================================
        # 저장
        # =====================================================

        cv2.imwrite(
            str(save_img_path),
            aug_image
        )

        save_yolo_label(
            save_label_path,
            aug_bboxes,
            aug_labels
        )

        success_count += 1

        # =====================================================
        # 진행률 출력
        # =====================================================

        if aug_idx % 100 == 0:

            print(
                f"[INFO] 진행률: "
                f"{aug_idx}/{need_aug}"
            )

    except Exception as e:

        fail_count += 1

        print(f"\n[ERROR] augmentation 실패")
        print(e)

# =========================================================
# 최종 검사
# =========================================================

final_plastic = len(
    list(TRAIN_IMAGE_DIR.glob("plastic_*"))
)

final_labels = len(
    list(TRAIN_LABEL_DIR.glob("plastic_*"))
)

print("\n================================================")
print("최종 결과")
print("================================================")

print(f"[OK] augmentation 성공: {success_count}")
print(f"[WARNING] augmentation 실패: {fail_count}")

print(f"[OK] 최종 plastic image 수: {final_plastic}")
print(f"[OK] 최종 plastic label 수: {final_labels}")

if final_plastic != final_labels:

    print("[ERROR] image-label 개수 불일치")

print("\n================================================")
print("[완료] PLASTIC AUGMENTATION 완료")
print("================================================")