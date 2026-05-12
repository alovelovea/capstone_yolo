# ♻️ AI 기반 쓰레기 분리배출 자동화 프로젝트

### 1. 프로젝트 배경 및 목적
지속 가능한 환경을 조성하기 위해 올바른 쓰레기 분리배출은 필수적입니다. 본 프로젝트는 분리배출 과정의 혼동을 줄이고 효율을 높이기 위해, **딥러닝 객체 탐지(Object Detection) 모델을 활용하여 쓰레기 종류를 실시간으로 식별하고 관리하는 시스템 구축**을 목표로 합니다.

---

### 2. 📦 데이터 수집 및 구성
모델의 일반화 성능을 높이기 위해 다양한 경로로 데이터를 확보하여 데이터셋의 신뢰도를 높였습니다.
*   **🌐 온라인 데이터 수집:** Roboflow, AI Hub 등 검증된 온라인 소스에서 기초 이미지 데이터를 확보하였습니다.
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

*   **[Split Dataset (학습용 데이터)](https://drive.google.com/file/d/1EOPrwIAy1ZEOy5Yd8svPUzdzEJv92XuB/view?usp=sharing)**: Train/Val 분할 및 YOLO 형식 변환 완료 데이터
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

| 순서 | 파일명 | 주요 역할 및 기능 | 코드 수행 결과 |
| :---: | :--- | :--- | :--- |
| **1** | `1데이터분할.py` | 클래스별 원본 데이터 수집 및 **Train/Validation(8:2)** 데이터셋 자동 생성. `dataset.yaml` 생성 및 데이터 무결성 검사 수행. |<img width="689" height="638" alt="image" src="https://github.com/user-attachments/assets/a1381ae7-5230-4f34-895f-4e74e9ccb748" />|
| **2** | `2데이터셋구성확인.py` | 생성된 데이터셋의 클래스별 분포 분석. 데이터 불균형 확인 및 **증강 필요 수량 자동 계산**. | <img src="https://github.com/user-attachments/assets/fbee09b7-4289-4eb6-82ef-3c64e8fe4579" width="500" /> |
| **3** | `3txt형식파악.py` | YOLO 라벨 파일 형식 분석. **Detection(Box)** 과 **Segmentation(Polygon)** 형식 구분 및 오류 라벨 탐지. | <img src="https://github.com/user-attachments/assets/7671abde-7934-4b82-a143-0aba24351588" width="500" /> |
| **4** | `4txt방식변경.py` | Segmentation 형식을 **YOLO Detection 형식(Center x, y, w, h)**으로 일괄 변환하여 데이터 형식 통일. | <img src="https://github.com/user-attachments/assets/9f8d14a6-7888-466f-8b1d-0764a5302156" width="450" /><br><img src="https://github.com/user-attachments/assets/b0b2131f-52b0-4687-85f8-ffe5e3e52f86" width="450" /> |
| **5** | `5플라스틱augmentation적용.py` | **Albumentations** 기반 데이터 증강(밝기, Blur, 반전 등) 수행 및 부족한 클래스 데이터 보강. | <img src="https://github.com/user-attachments/assets/ddbcc5e3-5c41-4556-9f15-eb3e31124d4a" width="450" /><br><img src="https://github.com/user-attachments/assets/4365727d-7226-4502-a4d2-9868973c2c69" width="450" /> |
| **6** | `6모델학습.py` | **YOLOv11n** 활용 학습 진행. GPU 가속, Mosaic/MixUp 적용 및 최적 가중치(`best.pt`) 생성. | <img width="940" height="471" alt="image" src="https://github.com/user-attachments/assets/567f74b4-4e14-4092-8d8d-e173d85dd753" />
| **7** | `7predict.py` | OpenCV 기반 인터랙티브 뷰어. 방향키를 이용해 **탐지 민감도(Confidence)**를 실시간 조절하며 결과 확인. | <img src="https://github.com/user-attachments/assets/c5f1f20c-cab5-4bef-8083-16d5ca8a29f2" width="400" /> |
---

### ⚠️ 주의사항 (Git Management)
* `.gitignore` 설정을 통해 대용량 데이터 폴더와 캐시 파일(`*.cache`)이 저장소에 업로드되지 않도록 관리하고 있습니다.
* 데이터셋을 로컬에서 실행할 경우, 반드시 상단 링크에서 데이터를 다운로드하여 프로젝트 구조에 맞게 배치해야 합니다.


