# ♻️ AI 기반 쓰레기 분리배출 자동화 프로젝트

### 1. 프로젝트 배경 및 목적
지속 가능한 환경을 조성하기 위해 올바른 쓰레기 분리배출은 필수적입니다. 본 프로젝트는 분리배출 과정의 혼동을 줄이고 효율을 높이기 위해, **딥러닝 객체 탐지(Object Detection) 모델을 활용하여 쓰레기 종류를 실시간으로 식별하고 관리하는 시스템 구축**을 목표로 합니다.

---

### 2. 📦 데이터 수집 및 구성
모델의 일반화 성능을 높이기 위해 다양한 경로로 데이터를 확보하여 데이터셋의 신뢰도를 높였습니다.
*   **🌐 온라인 데이터 수집:** 공공데이터 포털, AI Hub 등 검증된 온라인 소스에서 기초 이미지 데이터를 확보하였습니다.
*   **📸 팀 자체 수집:** 프로젝트의 실용성을 더하기 위해 **팀원들이 직접 일상 속 쓰레기 사진을 촬영하고 수집**하였습니다. 이를 통해 실제 현장에서 발생할 수 있는 다양한 배경, 조명 조건, 훼손된 쓰레기 상태 등을 데이터에 반영하였습니다.

---

### 3. 🛠️ 기술적 특징 및 문제 해결
*   **🚀 최신 모델 적용:** **Ultralytics YOLOv11** 모델을 채택하여 실시간 처리에 적합한 빠른 속도와 높은 객체 인식 정확도를 구현하였습니다.
*   **⚖️ 데이터 불균형 해결:** 수집된 데이터 중 수량이 부족한 특정 클래스(예: 플라스틱 등)를 보강하기 위해 **Albumentations 기반 데이터 증강(Augmentation)** 기법을 적용하였습니다.
    *   밝기 조정, 흐림 처리(Blur), 좌우 반전 등을 통해 데이터의 변동성을 확보하고 과적합(Overfitting)을 방지했습니다.
*   **⚙️ 자동화 파이프라인:** 
    *   라벨링 형식(Segmentation to Detection) 자동 변환 및 데이터셋의 균형 있는 분할(Train/Validation) 프로세스를 구축하였습니다.
    *   OpenCV 기반의 인터랙티브 인터페이스를 통해 사용자가 실시간으로 모델의 탐지 성능과 임계값을 테스트할 수 있는 환경을 제공합니다.

---

### 📂 4. 데이터셋 (Dataset)
프로젝트에 사용된 데이터는 용량 문제로 외부 링크를 통해 공유합니다.  
*(※ 다운로드 후 프로젝트 루트 디렉토리에 압축을 풀어주세요. 루트 디렉토리 이름: `combined_data_v2`)*

*   **[Original Dataset (원본 데이터)](https://drive.google.com/file/d/1mlqhVGrsvCygL8PqU9c8SC0pHlXK512k/view?usp=drive_link)**: 클래스별 원본 데이터셋
*   <img width="263" height="367" alt="image" src="https://github.com/user-attachments/assets/f39bd96b-ad55-4499-853e-59e420e1f782" />

*   **[Split Dataset (학습용 데이터)](https://drive.google.com/file/d/1FJnKN8dj6yr1U8h476PKUWfaoWc2WpsQ/view?usp=sharing)**: Train/Val 분할 및 YOLO 형식 변환 완료 데이터
*   <img width="268" height="29" alt="image" src="https://github.com/user-attachments/assets/d8d53bb5-af26-47d7-99bd-292ceba114a4" />



---

### 💻 5. 기술 스택 (Tech Stack)
*   **Language:** Python 3.x
*   **Model:** YOLOv11 (Ultralytics)
*   **Library:** OpenCV, PyTorch, Albumentations, Pandas, Matplotlib
*   **Environment:** CUDA 12.1 기반 GPU 가속 환경

---

### 🚀 6. 시작하기 (Quick Start)

#### 가상환경 설정 및 라이브러리 설치
```bash
# 가상환경 생성 및 활성화
python -m venv venv
.\venv\Scripts\activate

# 필수 라이브러리 설치
pip install -r requirements.txt
```

#### 코드 실행 순서
각 스크립트는 파일명 앞의 숫자에 따라 순차적으로 실행해 주세요.
* **전체 공정 실행 시:** `1` → `2` → `3` → `4` → `5` → `6` → `7` 순서로 실행
* **이미 가공된 [학습용 데이터]를 다운로드한 경우:** 바로 `6모델학습.py` 실행 가능 or `7predict.py`만 실행 가능

---

### 📜 7. 소스코드 상세 설명 (Workflow)

프로젝트는 데이터 전처리부터 모델 학습, 예측까지 총 7단계의 파이프라인으로 구성되어 있습니다.

#### [Workflow 시각화]
1. 데이터셋 균형화 → 2. 데이터 분포 분석 → 3. 라벨 포맷 검사 → 4. Seg-to-Det 변환 → 5. 증강(Augmentation) → 6. YOLOv11 학습 → 7. 실시간 예측

| 순서 | 파일명 | 주요 역할 및 기능 |
| :---: | :--- | :--- |
| **1** | `1데이터분할.py` | 클래스별 원본 데이터(`_1`, `_over2`, `mix_class`)를 수집하여 목표 개수(2000장)에 맞게 균형화하고, **Train/Validation(8:2)** 데이터셋(`balanced_dataset`)을 자동 생성합니다. 또한 `dataset.yaml` 생성 및 데이터 무결성 검사를 수행합니다. |
| **2** | `2데이터셋구성확인.py` | 생성된 데이터셋의 클래스별 분포를 분석합니다. 특히 데이터 불균형 여부를 확인하고, 부족한 클래스(Plastic 등)의 **증강 필요 수량을 자동 계산**합니다. |
| **3** | `3txt형식파악.py` | YOLO 라벨 파일(`.txt`)의 형식을 분석하여 **Detection 형식(class x y w h)**과 **Segmentation 형식**을 구분하고, 잘못된 라벨(invalid)을 탐지합니다. |
| **4** | `4txt방식변경.py` | Segmentation 형식(Polygon 좌표)을 YOLO **Detection 형식(Normalized Center x, y, w, h)**으로 변환하여 전체 데이터셋 라벨 형식을 통일합니다. |
| **5** | `5플라스틱augmentation적용.py` | **Albumentations** 기반 데이터 증강을 수행하여 부족한 클래스 데이터를 보강합니다. 밝기/색상 변화, Blur, 좌우 반전 등을 적용하며 Bounding Box 좌표를 자동 보정합니다. |
| **6** | `6모델학습.py` | **Ultralytics YOLOv11n** 모델을 활용하여 학습을 진행합니다. GPU(CUDA) 가속, Mosaic/MixUp 증강, 조기 종료(Early Stopping) 등을 포함하며 최종 `best.pt` 가중치를 생성합니다. |
| **7** | `7predict.py` | 학습 여부와 상관없이 weights/best.pt 파일만 있다면 즉시 추론할 수 있는 OpenCV 기반 인터랙티브 뷰어입니다. 실행 후 엔터만 누르면 기본 모델이 로드되며, 필요 시 경로를 직접 입력할 수도 있습니다. 방향키(또는 A/S/W/D)를 통해 이미지 이동 및 **탐지 민감도(Confidence)**를 실시간으로 조절하며 결과를 확인할 수 있습니다. |

---

### ⚠️ 주의사항 (Git Management)
* `.gitignore` 설정을 통해 대용량 데이터 폴더와 캐시 파일(`*.cache`)이 저장소에 업로드되지 않도록 관리하고 있습니다.
* 데이터셋을 로컬에서 실행할 경우, 반드시 상단 링크에서 데이터를 다운로드하여 프로젝트 구조에 맞게 배치해야 합니다.


