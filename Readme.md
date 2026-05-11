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
