
import random
import shutil
from pathlib import Path
from collections import defaultdict

# =========================================================
# 기본 설정
# =========================================================

random.seed(42)

# 현재 파이썬 파일 기준 경로
BASE_DIR = Path(__file__).resolve().parent

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
    "can_1": BASE_DIR / "can_1",
    "can_over2": BASE_DIR / "can_over2",

    "pet_1": BASE_DIR / "pet_1",
    "pet_over2": BASE_DIR / "pet_over2",

    "plastic_1": BASE_DIR / "plastic_1",
    "plastic_over2": BASE_DIR / "plastic_over2",

    "glass_1": BASE_DIR / "glass_1",
    "glass_over2": BASE_DIR / "glass_over2",

    "paper_1": BASE_DIR / "paper_1",
    "paper_over2": BASE_DIR / "paper_over2",

    "plasticbag_1": BASE_DIR / "plasticbag_1",
    "plasticbag_over2": BASE_DIR / "plasticbag_over2",

    "mix_class": BASE_DIR / "mix_class",
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

# =========================================================
# dataset.yaml 생성
# =========================================================

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
