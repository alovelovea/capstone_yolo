# check_label_format.py

from pathlib import Path
from collections import defaultdict

# =========================================================
# 경로 설정
# =========================================================

BASE_DIR = Path(r"C:\Users\alswo\Desktop\combined_data_v2")

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

    except Exception as e:

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

        # ---------------------------------------------
        # 숫자 변환 가능한지 검사
        # ---------------------------------------------

        try:
            nums = list(map(float, parts[1:]))
        except:
            return "invalid"

        # ---------------------------------------------
        # Detection 형식 검사
        # class x y w h
        # 총 5개
        # ---------------------------------------------

        if len(parts) != 5:
            is_detection = False

        # ---------------------------------------------
        # Segmentation 형식 검사
        # class x1 y1 x2 y2 ...
        #
        # 최소:
        # class + x1 y1 x2 y2 x3 y3
        # => 최소 7개
        #
        # 좌표 개수는 짝수여야 함
        # ---------------------------------------------

        coord_count = len(parts) - 1

        if (
            len(parts) < 7 or
            coord_count % 2 != 0
        ):
            is_segmentation = False

    # -------------------------------------------------
    # 최종 판별
    # -------------------------------------------------

    if is_detection:
        return "detection"

    elif is_segmentation:
        return "segmentation"

    else:
        return "invalid"

# =========================================================
# 클래스 추출 함수
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

    label_dir = BASE_DIR / folder_name / "labels"

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

print("\n================================================")
print("[완료] 분석 종료")
print("================================================")
# =========================================================
# 최종 Detection / Segmentation 재검사
# =========================================================

print("\n================================================")
print("최종 포맷 재검사")
print("================================================")

for label_dir in LABEL_DIRS:

    txt_files = list(label_dir.glob("*.txt"))

    for txt_path in txt_files:

        try:

            with open(txt_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

        except:
            continue

        for line in lines:

            parts = line.strip().split()

            if len(parts) == 0:
                continue

            if is_detection(parts):
                final_detection_count += 1

            elif is_segmentation(parts):
                final_segmentation_count += 1

# =========================================================
# 최종 결과
# =========================================================

print("\n================================================")
print("최종 결과")
print("================================================")

print(f"Detection 유지 : {detection_count}")
print(f"Segmentation 변환 : {converted_count}")
print(f"Invalid : {invalid_count}")

print("\n================================================")
print("최종 라벨 포맷 상태")
print("================================================")

print(f"최종 Detection 개수   : {final_detection_count}")
print(f"최종 Segmentation 개수: {final_segmentation_count}")

if final_segmentation_count == 0:

    print("\n[OK] 모든 라벨이 Detection 형식으로 통일됨")

else:

    print("\n[WARNING] 아직 Segmentation 라벨이 남아있음")

print("\n================================================")
print("[완료] balanced_dataset 전체 detection 통일 완료")
print("================================================")