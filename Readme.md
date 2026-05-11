# ♻️ YOLO 기반 쓰레기 자동 분류 및 객체 탐지 프로젝트
> **Hansung University Capstone Design 2026**  
> OpenCV와 YOLO(v11)를 활용하여 재활용 쓰레기(캔, 유리, 플라스틱 등)를 실시간으로 분류하는 프로젝트입니다.

---

## 📌 1. 프로젝트 개요
이 프로젝트는 지속 가능한 환경을 위해 쓰레기 분리배출을 자동화하는 것을 목표로 합니다.  
객체 탐지 모델을 통해 쓰레기의 종류를 식별하고, 데이터 불균형 문제를 해결하기 위해 데이터 증강(Augmentation) 기법을 적용하였습니다.

## 📂 2. 데이터셋 (Dataset)
프로젝트에 사용된 데이터는 용량 문제로 외부 링크를 통해 공유합니다. 
*(※ 다운로드 후 프로젝트 루트 디렉토리에 압축을 풀어주세요.)*
*(루트 디렉토리 이름: combined_data_v2)

*   **[Original Dataset (원본 데이터)](https://drive.google.com/file/d/1mlqhVGrsvCygL8PqU9c8SC0pHlXK512k/view?usp=drive_link)**: 클래스별 원본 데이터셋
*   <img width="265" height="368" alt="image" src="https://github.com/user-attachments/assets/80575f91-d414-4ad3-a726-85f5280cf1c4" />

*   **[Split Dataset (학습용 데이터)](https://drive.google.com/file/d/1FJnKN8dj6yr1U8h476PKUWfaoWc2WpsQ/view?usp=sharing)**: Train/Val/ 분할 및 YOLO 형식 변환 완료 데이터
*   <img width="211" height="21" alt="image" src="https://github.com/user-attachments/assets/b415837d-d9a1-4dde-b40b-3c64fe8fd5dd" />


## 🛠️ 3. 기술 스택 (Tech Stack)
*   **Language:** Python 3.x
*   **Model:** YOLOv11 (Ultralytics)
*   **Library:** OpenCV, PyTorch, Albumentations, Pandas, Matplotlib
*   **Environment:** CUDA 12.1 기반 GPU 가속 환경

## 🚀 4. 시작하기 (Quick Start)

### 가상환경 설정 및 라이브러리 설치
```bash
# 가상환경 생성 및 활성화
python -m venv venv
.\venv\Scripts\activate

# 필수 라이브러리 설치
pip install -r requirements.txt
# 코드 실행
가상환경 위에서 1데이터분할.py부터 6모델학습.py 까지 실행
학습용 데이터를 다운 받았으면 6모델학습.py만 실행해도 무방
```














### 🚀 4. 시작하기 (Quick Start)

#### 코드 실행 순서
각 스크립트는 파일명 앞의 숫자에 따라 순차적으로 실행해 주세요.
* **전체 공정 실행 시:** `1` → `2` → `3` → `4` → `5` → `6` → `7` 순서로 실행
* **이미 가공된 [학습용 데이터]를 다운로드한 경우:** 바로 `6모델학습.py` 실행 가능

---

### 📜 5. 소스코드 상세 설명 (Workflow)

프로젝트는 데이터 전처리부터 모델 학습, 예측까지 총 7단계의 파이프라인으로 구성되어 있습니다.

| 순서 | 파일명 | 주요 역할 및 기능 |
| :--- | :--- | :--- |
| **1** | `1데이터분할.py` | 원본 데이터를 **Train / Validation** 세트로 분할(8:2)하고 폴더 구조를 자동 생성합니다. |
| **2** | `2데이터셋구성확인.py` | 클래스별 이미지/라벨 개수를 점검하여 **데이터 불균형 상태**를 시각적으로 확인합니다. |
| **3** | `3txt형식파악.py` | 라벨 파일(`.txt`)의 포맷과 클래스 ID, 좌표 값이 YOLO 표준에 부합하는지 검증합니다. |
| **4** | `4txt방식변경.py` | 다양한 좌표 형식(Absolute 등)을 YOLO 표준인 **Normalized Center(x, y, w, h)**로 일괄 변환합니다. |
| **5** | `5플라스틱augmentation적용.py` | **Albumentations**를 사용하여 부족한 클래스(플라스틱, 비닐)에 데이터 증강을 적용합니다. |
| **6** | `6모델학습.py` | **YOLOv11** 모델을 활용하여 학습을 수행하며, 최종 가중치(`best.pt`)를 생성합니다. |
| **7** | `7predict.py` | 학습된 모델과 **OpenCV**를 결합하여 실시간 영상/이미지에서 쓰레기를 분류하고 시각화합니다. |

