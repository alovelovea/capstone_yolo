# ♻️ AI 기반 쓰레기 분리배출 자동화 프로젝트

### 1. 프로젝트 개요
지속 가능한 환경을 조성하기 위해 올바른 분리배출은 필수적이지만, 실생활에서는 복잡한 분류 기준으로 인해 혼동이 자주 발생합니다. 본 프로젝트는 분리배출 과정의 혼동을 줄이고 효율을 높이기 위해, **딥러닝 객체 탐지(Object Detection) 모델을 활용하여 쓰레기 종류를 실시간으로 식별하고 관리하는 시스템 구축**을 목표로 합니다. 이를 통해 사용자의 판단 부담을 줄이고, 보다 정확하고 일관된 분리배출 환경을 실현하고자 합니다.

---

### 2. 📦 데이터 수집 및 구성
모델의 일반화 성능을 높이기 위해 다양한 경로로 데이터를 확보하여 데이터셋의 신뢰도를 높였습니다.

*   **🌐 온라인 데이터 수집**
    *   Roboflow, AI Hub 등 검증된 공개 데이터셋에서 기초 이미지 데이터를 확보하였습니다.
    *   수집한 데이터를 검토하고 본 프로젝트의 분류 기준에 맞춰 직접 라벨링하는 과정을 거쳐 보다 정확한 데이터셋을 구축하였습니다.

*   **📸 팀 자체 수집**
    *   프로젝트의 실용성을 더하기 위해 **팀원들이 직접 일상 속 쓰레기 사진을 촬영하고 수집**하였습니다.
    *   배경, 조명 조건, 쓰레기 훼손 상태 등을 다양하게 구성하여 실제 현장에서 발생할 수 있는 변수를 데이터에 반영함으로써 현실성과 신뢰도를 높였습니다.
    *   **수집 예시**
    *   <img width="900" height="350" alt="스크린샷 2026-06-02 162536" src="https://github.com/user-attachments/assets/2a1a99fb-27ed-49bf-a746-b6e03c7273a8" />

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
*(※ 다운로드 후 프로젝트 루트 디렉토리에 압축을 풀어주세요. 루트 디렉토리 이름: `combined_data_v4`)*

*   **[Original Dataset (원본 데이터)](https://drive.google.com/file/d/18MwHgJrD6e6gEyg-UQ8ioq3swS5PRxqO/view?usp=sharing)**: 클래스별 원본 데이터셋
*   <img width="263" height="367" alt="image" src="https://github.com/user-attachments/assets/f39bd96b-ad55-4499-853e-59e420e1f782" />

*   **[Split Dataset (학습용 데이터)](https://drive.google.com/file/d/1gjMSW88cVNjefXdec7jtSDDiZuRfjYjU/view?usp=sharing)**: Train/Val 분할 및 YOLO 형식 변환 완료 데이터
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


---

### 📜 7. 소스코드 상세 설명 (Workflow)
> **ℹ️ 상세 설계 확인**
> 본 모델의 워크플로우에 대한 기술적 상세 내용은 [여기](https://github.com/alovelovea/capstone_yolo/blob/minjae/model/Readme.md#--model-workflow)를 클릭하여 확인해 주세요.

---

### ⚠️ 주의사항 (Git Management)
* `.gitignore` 설정을 통해 대용량 데이터 폴더와 캐시 파일(`*.cache`)이 저장소에 업로드되지 않도록 관리하고 있습니다.
* 데이터셋을 로컬에서 실행할 경우, 반드시 상단 링크에서 데이터를 다운로드하여 프로젝트 구조에 맞게 배치해야 합니다.


