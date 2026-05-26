# 🤖 YOLOv11 기반 쓰레기 분류 모델 (Model Section)

이 폴더는 쓰레기 분류를 위한 YOLOv11 모델의 데이터 전처리, 학습 및 예측 코드를 포함하고 있습니다.

## 📂 폴더 구조
- `preprocessing/`: 데이터 전처리 및 증강을 위한 스크립트 모음
- `weights/`: 학습된 모델 가중치 파일 (`best.pt`)
- `6모델학습.py`: YOLOv11n 모델 학습 스크립트
- `7predict.py`: 학습된 모델을 사용한 실시간 예측 및 테스트 스크립트

---

## 🛠️ 전처리 과정 (Preprocessing)
데이터 전처리는 `preprocessing/` 폴더 내의 스크립트를 통해 순차적으로 진행됩니다.

| 순서 | 파일명 | 주요 역할 및 기능 |
| :---: | :--- | :--- |
| **1** | `1데이터분할.py` | 원본 데이터를 **Train/Validation(8:2)**으로 자동 분할 및 `dataset.yaml` 생성. |
| **2** | `2데이터셋구성확인.py` | 클래스별 분포 분석 및 **데이터 증강 필요 수량 계산**. |
| **3** | `3txt형식파악.py` | YOLO 라벨 형식(Box/Polygon) 분석 및 오류 탐지. |
| **4** | `4txt방식변경.py` | Segmentation(Polygon) 형식을 **Detection(Box)** 형식으로 일괄 변환. |
| **5** | `5플라스틱augmentation적용.py` | **Albumentations**를 사용하여 부족한 클래스(플라스틱 등) 데이터 증강. |

---

## 🚀 모델 학습 및 예측

### 1. 모델 학습 (`6모델학습.py`)
- **모델:** YOLOv11n
- **특징:** GPU 가속 활용, Mosaic/MixUp 증강 적용
- **결과:** `weights/best.pt` 생성

### 2. 결과 예측 (`7predict.py`)
- OpenCV 기반의 인터랙티브 인터페이스
- 방향키를 이용한 **Confidence Threshold(신뢰도 임계값)** 실시간 조절 가능
