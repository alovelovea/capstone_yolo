from pathlib import Path
import pandas as pd

# 현재 파일 기준 경로
BASE_DIR = Path(__file__).resolve().parent

# 데이터셋 경로
dataset_path = BASE_DIR / "balanced_dataset"

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