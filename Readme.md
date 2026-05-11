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















## 📜 5. 소스코드 상세 설명 (Workflow)

프로젝트는 데이터 전처리부터 모델 학습, 예측까지 단계별로 구성되어 있습니다. 각 스크립트는 순서대로 실행하는 것을 권장합니다.

1.  **`1데이터분할.py`**
    * 원본 데이터를 Train / Validation 데이터셋으로 분할합니다. (기본 8:2 비율)
    * 클래스별 폴더 구조를 생성하고 파일을 이동시킵니다.

2.  **`2데이터셋구성확인.py`**
    * 분할된 데이터셋의 클래스별 이미지 개수와 라벨 상태를 체크합니다.
    * 데이터 불균형(Imbalance) 여부를 시각적으로 확인하여 증강(Augmentation) 대상을 선정합니다.

3.  **`3txt형식파악.py`**
    * YOLO 학습에 필요한 라벨 파일(`.txt`)의 포맷이 올바른지 검증합니다.
    * 클래스 ID와 바운딩 박스 좌표 값이 정상 범위 내에 있는지 확인합니다.

4.  **`4txt방식변경.py`**
    * 외부 데이터셋이나 기존 라벨링 툴에서 생성된 좌표 형식을 YOLO 표준 형식(Normalized center x, y, w, h)으로 일괄 변환합니다.

5.  **`5플라스틱augmentation적용.py`**
    * 데이터 양이 부족한 '플라스틱' 및 '비닐' 클래스에 대해 **Albumentations** 라이브러리를 사용하여 증강을 수행합니다.
    * 회전, 밝기 조절, 노이즈 추가 등을 통해 모델의 일반화 성능을 높입니다.

6.  **`6모델학습.py`**
    * **YOLOv11** 모델을 사용하여 학습을 진행합니다.
    * `data.yaml` 설정을 기반으로 하며, 에폭(Epochs), 배치 사이즈(Batch size), 하이퍼파라미터 등을 설정합니다.

7.  **`7predict.py`**
    * 학습된 가중치 파일(`best.pt`)을 불러와 새로운 이미지나 영상 데이터에 대해 추론을 수행합니다.
    * **OpenCV**를 활용하여 실시간 객체 탐지 결과를 화면에 출력합니다.


