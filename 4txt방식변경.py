#생성한 balanced_dataset에 txt를 변경함. 원본label은 변경 x
# convert_balanced_dataset_seg_to_det.py

from pathlib import Path

# =========================================================
# 경로 설정
# =========================================================

BASE_DIR = Path(
    r"C:\Users\alswo\Desktop\combined_data_v2\balanced_dataset"
)

LABEL_DIRS = [
    BASE_DIR / "labels/train",
    BASE_DIR / "labels/valid"
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

    txt_files = list(label_dir.glob("*.txt"))

    print(f"[INFO] txt 파일 수: {len(txt_files)}")

    dir_converted = 0
    dir_detection = 0
    dir_invalid = 0

    for txt_path in txt_files:

        try:

            with open(txt_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

        except Exception as e:

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
                _ = list(map(float, parts[1:]))

            except:

                file_invalid = True
                continue

            # -------------------------------------------------
            # Detection
            # -------------------------------------------------

            if is_detection(parts):

                new_lines.append(line.strip())

                dir_detection += 1
                detection_count += 1

            # -------------------------------------------------
            # Segmentation
            # -------------------------------------------------

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

            # -------------------------------------------------
            # Invalid
            # -------------------------------------------------

            else:

                file_invalid = True

        # -----------------------------------------------------
        # invalid 파일 로그
        # -----------------------------------------------------

        if file_invalid:

            dir_invalid += 1
            invalid_count += 1

            print(f"[WARNING] invalid 형식: {txt_path.name}")

        # -----------------------------------------------------
        # overwrite 저장
        # -----------------------------------------------------

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

    print(f"Detection 유지 : {dir_detection}")
    print(f"Segmentation 변환 : {dir_converted}")
    print(f"Invalid : {dir_invalid}")

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
print("[완료] balanced_dataset 전체 detection 통일 완료")
print("================================================")