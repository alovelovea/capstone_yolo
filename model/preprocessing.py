
import random
import shutil
from pathlib import Path
from collections import defaultdict
import pandas as pd
import cv2
import albumentations as A

# =========================================================
# 1.데이터 분할
# =========================================================

random.seed(42)

# 현재 파이썬 파일 기준 경로
BASE_DIR = Path(__file__).resolve().parent.parent

ORIGIN_DIR = BASE_DIR / "origin_data"
OUTPUT_DIR = BASE_DIR / "balanced_dataset"

TARGET_COUNT = 2000
TRAIN_RATIO = 0.8

CLASSES = [
    "can",
    "pet",
    "plastic",
    "glass",
    "paper",
    "plasticbag"
]

SOURCE_DIRS = {
   "can_1": ORIGIN_DIR / "can_1",
    "can_over2": ORIGIN_DIR / "can_over2",

    "pet_1": ORIGIN_DIR / "pet_1",
    "pet_over2": ORIGIN_DIR / "pet_over2",

    "plastic_1": ORIGIN_DIR / "plastic_1",
    "plastic_over2": ORIGIN_DIR / "plastic_over2",

    "glass_1": ORIGIN_DIR / "glass_1",
    "glass_over2": ORIGIN_DIR / "glass_over2",

    "paper_1": ORIGIN_DIR / "paper_1",
    "paper_over2": ORIGIN_DIR / "paper_over2",

    "plasticbag_1": ORIGIN_DIR / "plasticbag_1",
    "plasticbag_over2": ORIGIN_DIR / "plasticbag_over2",

    "mix_class": ORIGIN_DIR / "mix_class",
}

# =========================================================
# 출력 폴더 초기화
# =========================================================

if OUTPUT_DIR.exists():
    print(f"\n[INFO] 기존 balanced_dataset 삭제 중...")
    shutil.rmtree(OUTPUT_DIR)

for split in ["train", "valid"]:
    (OUTPUT_DIR / "images" / split).mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "labels" / split).mkdir(parents=True, exist_ok=True)

print(f"[OK] 출력 폴더 생성 완료")

# =========================================================
# 유틸 함수
# =========================================================

def check_folder_exists(folder_path):

    if not folder_path.exists():
        raise FileNotFoundError(f"\n[ERROR] 폴더 없음: {folder_path}")

    print(f"[OK] 폴더 확인: {folder_path}")


def get_image_label_pairs(folder_path):

    image_dir = folder_path / "images"
    label_dir = folder_path / "labels"

    # 폴더 존재 검사
    check_folder_exists(image_dir)
    check_folder_exists(label_dir)

    pairs = []

    image_files = list(image_dir.glob("*.*"))

    print(f"\n[INFO] 이미지 탐색 중: {folder_path.name}")
    print(f"[INFO] 발견된 전체 파일 수: {len(image_files)}")

    missing_label_count = 0

    for img_path in image_files:

        if img_path.suffix.lower() not in [".jpg", ".jpeg", ".png"]:
            continue

        label_path = label_dir / f"{img_path.stem}.txt"

        if not label_path.exists():
            missing_label_count += 1
            continue

        # 라벨 비어있는지 검사
        try:
            with open(label_path, "r", encoding="utf-8") as f:
                content = f.read().strip()

            if content == "":
                print(f"[WARNING] 빈 라벨 파일: {label_path}")
                continue

        except Exception as e:
            print(f"[ERROR] 라벨 읽기 실패: {label_path}")
            print(e)
            continue

        pairs.append((img_path, label_path))

    print(f"[OK] 정상 pair 수: {len(pairs)}")
    print(f"[WARNING] 라벨 없는 이미지 수: {missing_label_count}")

    return pairs


def copy_pair(img_path, label_path, split, prefix=""):

    new_img_name = prefix + img_path.name
    new_label_name = prefix + label_path.name

    dst_img = OUTPUT_DIR / "images" / split / new_img_name
    dst_label = OUTPUT_DIR / "labels" / split / new_label_name

    try:

        shutil.copy2(img_path, dst_img)
        shutil.copy2(label_path, dst_label)

    except Exception as e:

        print(f"\n[ERROR] 복사 실패")
        print(img_path)
        print(label_path)
        print(e)


# =========================================================
# 통계 저장용
# =========================================================

final_stats = defaultdict(dict)

# =========================================================
# 클래스별 처리
# =========================================================

for cls in CLASSES:

    print("\n================================================")
    print(f"[START] {cls.upper()} 처리 시작")
    print("================================================")

    over2_key = f"{cls}_over2"
    one_key = f"{cls}_1"

    # -----------------------------------------------------
    # 데이터 로드
    # -----------------------------------------------------

    over2_pairs = get_image_label_pairs(SOURCE_DIRS[over2_key])
    one_pairs = get_image_label_pairs(SOURCE_DIRS[one_key])

    print(f"\n[INFO] over2 개수: {len(over2_pairs)}")
    print(f"[INFO] _1 개수: {len(one_pairs)}")

    # -----------------------------------------------------
    # over2 우선 포함
    # -----------------------------------------------------

    selected_pairs = over2_pairs.copy()

    remain = TARGET_COUNT - len(selected_pairs)

    print(f"[INFO] 추가로 필요한 개수: {remain}")

    # -----------------------------------------------------
    # 부족분 샘플링
    # -----------------------------------------------------

    if remain > 0:

        if len(one_pairs) < remain:

            print(f"[WARNING] {cls}_1 데이터 부족")
            print(f"[WARNING] 가능한 만큼만 사용")

            sampled = one_pairs

        else:

            sampled = random.sample(one_pairs, remain)

        selected_pairs.extend(sampled)

    # -----------------------------------------------------
    # 최종 검사
    # -----------------------------------------------------

    print(f"\n[OK] 최종 선택 개수: {len(selected_pairs)}")

    if len(selected_pairs) == 0:
        raise ValueError(f"[ERROR] {cls} 데이터가 0개")

    # -----------------------------------------------------
    # 셔플
    # -----------------------------------------------------

    random.shuffle(selected_pairs)

    # -----------------------------------------------------
    # train / valid 분할
    # -----------------------------------------------------

    train_count = int(len(selected_pairs) * TRAIN_RATIO)

    train_pairs = selected_pairs[:train_count]
    valid_pairs = selected_pairs[train_count:]

    print(f"[INFO] train 개수: {len(train_pairs)}")
    print(f"[INFO] valid 개수: {len(valid_pairs)}")

    # -----------------------------------------------------
    # 저장
    # -----------------------------------------------------

    print(f"\n[INFO] train 저장 중...")

    for idx, (img_path, label_path) in enumerate(train_pairs):

        prefix = f"{cls}_train_{idx}_"

        copy_pair(
            img_path,
            label_path,
            "train",
            prefix
        )

    print(f"[OK] train 저장 완료")

    print(f"\n[INFO] valid 저장 중...")

    for idx, (img_path, label_path) in enumerate(valid_pairs):

        prefix = f"{cls}_valid_{idx}_"

        copy_pair(
            img_path,
            label_path,
            "valid",
            prefix
        )

    print(f"[OK] valid 저장 완료")

    # -----------------------------------------------------
    # 통계 저장
    # -----------------------------------------------------

    final_stats[cls]["train"] = len(train_pairs)
    final_stats[cls]["valid"] = len(valid_pairs)
    final_stats[cls]["total"] = len(selected_pairs)

# =========================================================
# MIX CLASS 처리
# =========================================================

print("\n================================================")
print("[START] MIX 처리 시작")
print("================================================")

mix_pairs = get_image_label_pairs(SOURCE_DIRS["mix_class"])

print(f"\n[INFO] mix 전체 개수: {len(mix_pairs)}")

random.shuffle(mix_pairs)

train_count = int(len(mix_pairs) * TRAIN_RATIO)

train_pairs = mix_pairs[:train_count]
valid_pairs = mix_pairs[train_count:]

print(f"[INFO] mix train: {len(train_pairs)}")
print(f"[INFO] mix valid: {len(valid_pairs)}")

for idx, (img_path, label_path) in enumerate(train_pairs):

    prefix = f"mix_train_{idx}_"

    copy_pair(
        img_path,
        label_path,
        "train"
        ,
        prefix
    )

for idx, (img_path, label_path) in enumerate(valid_pairs):

    prefix = f"mix_valid_{idx}_"

    copy_pair(
        img_path,
        label_path,
        "valid",
        prefix
    )

final_stats["mix"]["train"] = len(train_pairs)
final_stats["mix"]["valid"] = len(valid_pairs)
final_stats["mix"]["total"] = len(mix_pairs)

#=========================================================
#dataset.yaml 생성
#=========================================================

yaml_text = """
path: ./balanced_dataset

train: images/train
val: images/valid

names:
  0: can
  1: pet
  2: plastic
  3: glass
  4: paper
  5: plasticbag
"""

yaml_path = OUTPUT_DIR / "dataset.yaml"

with open(yaml_path, "w", encoding="utf-8") as f:
    f.write(yaml_text)

print(f"\n[OK] dataset.yaml 생성 완료")

# =========================================================
# 최종 통계 출력
# =========================================================

print("\n================================================")
print("최종 데이터셋 통계")
print("================================================")

for cls, stats in final_stats.items():

    print(
        f"{cls:<12}"
        f"train={stats['train']:<5} "
        f"valid={stats['valid']:<5} "
        f"total={stats['total']}"
    )

# =========================================================
# 최종 파일 개수 검사
# =========================================================

train_img_count = len(list((OUTPUT_DIR / "images/train").glob("*.*")))
train_label_count = len(list((OUTPUT_DIR / "labels/train").glob("*.txt")))

valid_img_count = len(list((OUTPUT_DIR / "images/valid").glob("*.*")))
valid_label_count = len(list((OUTPUT_DIR / "labels/valid").glob("*.txt")))

print("\n================================================")
print("최종 무결성 검사")
print("================================================")

print(f"train images : {train_img_count}")
print(f"train labels : {train_label_count}")

print(f"valid images : {valid_img_count}")
print(f"valid labels : {valid_label_count}")

if train_img_count != train_label_count:
    print("\n[ERROR] train image-label 개수 불일치")

if valid_img_count != valid_label_count:
    print("\n[ERROR] valid image-label 개수 불일치")

print("\n================================================")
print("[완료] balanced_dataset 생성 완료")
print("================================================")

# =========================================================
# 2.데이터셋 구성 확인
# =========================================================
dataset_path = OUTPUT_DIR

def analyze_balanced_dataset(path):

    results = []

    splits = ['train', 'valid']

    for split in splits:

        img_dir = path / "images" / split

        if not img_dir.exists():
            print(f"[경고] 폴더가 존재하지 않음: {img_dir}")
            continue

        files = [
            f.name for f in img_dir.glob("*.*")
            if f.suffix.lower() in ['.jpg', '.jpeg', '.png']
        ]

        for file_name in files:

            parts = file_name.split('_')
            class_name = parts[0]

            results.append({
                'Class': class_name,
                'Split': split
            })

    if not results:
        print("❌ 분석할 데이터가 없습니다.")
        return None

    df = pd.DataFrame(results)

    summary = df.groupby(
        ['Class', 'Split']
    ).size().unstack(fill_value=0)

    if 'train' in summary.columns and 'valid' in summary.columns:

        summary['Total'] = (
            summary['train'] +
            summary['valid']
        )

        summary['Train_Ratio(%)'] = (
            summary['train'] /
            summary['Total'] * 100
        ).round(1)

    return summary


# 분석 실행
print("\n🔍 balanced_dataset 분석 중...")

try:

    report = analyze_balanced_dataset(dataset_path)

    if report is not None:

        print("\n" + "="*60)
        print("         [ 최종 데이터셋 분포 보고서 ]")
        print("="*60)

        print(report)

        print("="*60)

        if 'plastic' in report.index:

            current_total = report.loc['plastic', 'Total']

            target = 2000

            if current_total < target:

                needed = target - current_total

                print(f"\n💡 [Plastic 보완 계획]")
                print(f"현재 Plastic 총계: {current_total}개")
                print(f"부족분: {needed}개")

except Exception as e:

    print(f"❌ 분석 중 오류 발생: {e}")

# =========================================================
# 3.txt 형식 파악
# =========================================================


CLASSES = [
    "can",
    "pet",
    "plastic",
    "glass",
    "paper",
    "plasticbag",
    "mix"
]

FOLDERS = [
    "can_1",
    "can_over2",

    "pet_1",
    "pet_over2",

    "plastic_1",
    "plastic_over2",

    "glass_1",
    "glass_over2",

    "paper_1",
    "paper_over2",

    "plasticbag_1",
    "plasticbag_over2",

    "mix_class"
]

# =========================================================
# 통계 저장
# =========================================================

stats = defaultdict(lambda: {
    "detection": 0,
    "segmentation": 0,
    "invalid": 0
})

# =========================================================
# 형식 판별 함수
# =========================================================

def detect_label_type(txt_path):

    try:

        with open(txt_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

    except Exception:

        print(f"[ERROR] 파일 읽기 실패: {txt_path}")
        return "invalid"

    if len(lines) == 0:
        return "invalid"

    is_detection = True
    is_segmentation = True

    for line in lines:

        parts = line.strip().split()

        # 빈 줄
        if len(parts) == 0:
            continue

        # 숫자 변환 가능한지 검사
        try:
            list(map(float, parts[1:]))

        except:
            return "invalid"

        # =================================================
        # Detection 검사
        # class x y w h
        # =================================================

        if len(parts) != 5:
            is_detection = False

        # =================================================
        # Segmentation 검사
        # class x1 y1 x2 y2 ...
        # =================================================

        coord_count = len(parts) - 1

        if (
            len(parts) < 7 or
            coord_count % 2 != 0
        ):
            is_segmentation = False

    # =====================================================
    # 최종 판별
    # =====================================================

    if is_detection:
        return "detection"

    elif is_segmentation:
        return "segmentation"

    else:
        return "invalid"

# =========================================================
# 클래스 추출
# =========================================================

def extract_class_name(folder_name):

    if folder_name == "mix_class":
        return "mix"

    return folder_name.split("_")[0]

# =========================================================
# 검사 시작
# =========================================================

print("\n================================================")
print("LABEL FORMAT ANALYSIS")
print("================================================")

for folder_name in FOLDERS:

    class_name = extract_class_name(folder_name)

    label_dir = ORIGIN_DIR / folder_name / "labels"

    if not label_dir.exists():

        print(f"[WARNING] labels 폴더 없음: {label_dir}")
        continue

    txt_files = list(label_dir.glob("*.txt"))

    print(f"\n[INFO] {folder_name}")
    print(f"[INFO] txt 파일 수: {len(txt_files)}")

    for txt_path in txt_files:

        label_type = detect_label_type(txt_path)

        stats[class_name][label_type] += 1

# =========================================================
# 결과 출력
# =========================================================

print("\n================================================")
print("최종 결과")
print("================================================")

for cls in CLASSES:

    det = stats[cls]["detection"]
    seg = stats[cls]["segmentation"]
    inv = stats[cls]["invalid"]

    total = det + seg + inv

    print(f"\n[{cls.upper()}]")

    print(f"전체            : {total}")
    print(f"Detection       : {det}")
    print(f"Segmentation    : {seg}")
    print(f"Invalid         : {inv}")

# =========================================================
# 전체 segmentation 존재 여부 검사
# =========================================================

total_segmentation = sum(
    stats[cls]["segmentation"]
    for cls in CLASSES
)

print("\n================================================")
print("최종 라벨 포맷 상태")
print("================================================")

print(f"전체 Segmentation 개수 : {total_segmentation}")

if total_segmentation == 0:

    print("\n[OK] 모든 라벨이 Detection 형식으로 통일됨")

else:

    print("\n[WARNING] 아직 Segmentation 라벨이 남아있음")

print("\n================================================")
print("[완료] 분석 종료")
print("================================================")


# =========================================================
# 4.txt방식 변경
# =========================================================



# 현재 파이썬 파일 기준 경로


LABEL_DIRS = [
    OUTPUT_DIR / "labels/train",
    OUTPUT_DIR / "labels/valid"
]

# =========================================================
# 통계
# =========================================================

converted_count = 0
detection_count = 0
invalid_count = 0

# =========================================================
# 함수
# =========================================================

def is_detection(parts):

    return len(parts) == 5


def is_segmentation(parts):

    coord_count = len(parts) - 1

    return (
        len(parts) >= 7 and
        coord_count % 2 == 0
    )


def segmentation_to_bbox(parts):

    cls_id = parts[0]

    coords = list(map(float, parts[1:]))

    xs = coords[0::2]
    ys = coords[1::2]

    xmin = min(xs)
    xmax = max(xs)

    ymin = min(ys)
    ymax = max(ys)

    x_center = (xmin + xmax) / 2
    y_center = (ymin + ymax) / 2

    width = xmax - xmin
    height = ymax - ymin

    # 범위 보정
    x_center = max(0, min(1, x_center))
    y_center = max(0, min(1, y_center))

    width = max(0, min(1, width))
    height = max(0, min(1, height))

    return (
        f"{cls_id} "
        f"{x_center:.6f} "
        f"{y_center:.6f} "
        f"{width:.6f} "
        f"{height:.6f}"
    )

# =========================================================
# 시작
# =========================================================

print("\n================================================")
print("BALANCED_DATASET")
print("SEGMENTATION → DETECTION 변환 시작")
print("================================================")

for label_dir in LABEL_DIRS:

    print(f"\n================================================")
    print(f"[START] {label_dir}")
    print("================================================")

    if not label_dir.exists():

        print(f"[WARNING] 폴더 없음: {label_dir}")
        continue

    txt_files = list(label_dir.glob("*.txt"))

    print(f"[INFO] txt 파일 수: {len(txt_files)}")

    dir_converted = 0
    dir_detection = 0
    dir_invalid = 0

    for txt_path in txt_files:

        try:

            with open(txt_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

        except Exception:

            dir_invalid += 1
            invalid_count += 1

            print(f"[ERROR] 읽기 실패: {txt_path}")
            continue

        new_lines = []

        file_invalid = False

        for line in lines:

            parts = line.strip().split()

            if len(parts) == 0:
                continue

            # 숫자 검사
            try:
                list(map(float, parts[1:]))

            except:

                file_invalid = True
                continue

            # =================================================
            # Detection
            # =================================================

            if is_detection(parts):

                new_lines.append(line.strip())

                dir_detection += 1
                detection_count += 1

            # =================================================
            # Segmentation
            # =================================================

            elif is_segmentation(parts):

                try:

                    bbox_line = segmentation_to_bbox(parts)

                    new_lines.append(bbox_line)

                    dir_converted += 1
                    converted_count += 1

                except Exception as e:

                    file_invalid = True

                    print(f"[ERROR] 변환 실패: {txt_path}")
                    print(e)

            # =================================================
            # Invalid
            # =================================================

            else:

                file_invalid = True

        # =====================================================
        # invalid 파일 로그
        # =====================================================

        if file_invalid:

            dir_invalid += 1
            invalid_count += 1

            print(f"[WARNING] invalid 형식: {txt_path.name}")

        # =====================================================
        # overwrite 저장
        # =====================================================

        try:

            with open(txt_path, "w", encoding="utf-8") as f:

                for new_line in new_lines:
                    f.write(new_line + "\n")

        except Exception as e:

            print(f"[ERROR] 저장 실패: {txt_path}")
            print(e)

    # =========================================================
    # 폴더 결과
    # =========================================================

    print(f"\n[RESULT] {label_dir.name}")

    print(f"Detection 유지     : {dir_detection}")
    print(f"Segmentation 변환 : {dir_converted}")
    print(f"Invalid           : {dir_invalid}")

# =========================================================
# 최종 결과
# =========================================================

print("\n================================================")
print("최종 결과")
print("================================================")

print(f"Detection 유지     : {detection_count}")
print(f"Segmentation 변환 : {converted_count}")
print(f"Invalid           : {invalid_count}")

print("\n================================================")
print("[완료] balanced_dataset 전체 detection 통일 완료")
print("================================================")

# =========================================================
# 5.플라스틱 augmentation적용.py
# =========================================================






TRAIN_IMAGE_DIR = OUTPUT_DIR / "images/train"
TRAIN_LABEL_DIR = OUTPUT_DIR / "labels/train"

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

            # bbox 범위 검사
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