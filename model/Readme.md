

# 📜  model (Workflow)





---

 ### [데이터 전처리 Workflow 시각화]
1. 데이터셋 균형화 → 2. 데이터 분포 분석 → 3. 라벨 포맷 검사 → 4. Seg-to-Det 변환 → 5. 증강(Augmentation) 

| 순서 | 주요 역할 및 기능 | 코드 수행 결과 |
| :---: | :--- | :--- |
| **1** | 클래스별 원본 데이터 수집 및 **Train/Validation(8:2)** 데이터셋 자동 생성. `dataset.yaml` 생성 및 데이터 무결성 검사 수행. | <img width="689" height="638" alt="image" src="https://github.com/user-attachments/assets/a1381ae7-5230-4f34-895f-4e74e9ccb748" /> |
| **2** | 생성된 데이터셋의 클래스별 분포 분석. 데이터 불균형 확인 및 **증강 필요 수량 자동 계산**. | <img src="https://github.com/user-attachments/assets/fbee09b7-4289-4eb6-82ef-3c64e8fe4579" width="500" /> |
| **3** | YOLO 라벨 파일 형식 분석. **Detection(Box)** 과 **Segmentation(Polygon)** 형식 구분 및 오류 라벨 탐지. | <img src="https://github.com/user-attachments/assets/7671abde-7934-4b82-a143-0aba24351588" width="500" /> |
| **4** | Segmentation 형식을 **YOLO Detection 형식(Center x, y, w, h)** 으로 일괄 변환하여 데이터 형식 통일. | <img src="https://github.com/user-attachments/assets/9f8d14a6-7888-466f-8b1d-0764a5302156" width="450" /><br><img src="https://github.com/user-attachments/assets/b0b2131f-52b0-4687-85f8-ffe5e3e52f86" width="450" /> |
| **5** | **Albumentations** 기반 데이터 증강(밝기, Blur, 반전 등) 수행 및 부족한 클래스 데이터 보강. | <img src="https://github.com/user-attachments/assets/ddbcc5e3-5c41-4556-9f15-eb3e31124d4a" width="450" /><br><img src="https://github.com/user-attachments/assets/4365727d-7226-4502-a4d2-9868973c2c69" width="450" /> |
---

### 2. 모델 학습 (`train.py`)

| 주요 역할 및 기능 | 코드 수행 결과 |
| :--- | :--- |
| **YOLOv11n** 활용 학습 진행. GPU 가속, Mosaic/MixUp 적용 및 최적 가중치(`best.pt`) 생성. | <img width="940" height="471" alt="image" src="https://github.com/user-attachments/assets/567f74b4-4e14-4092-8d8d-e173d85dd753" /> |

---

### 3. 예측 (`predict.py`)

| 주요 역할 및 기능 | 코드 수행 결과 |
| :--- | :--- |
| OpenCV 기반 인터랙티브 뷰어. 방향키를 이용해 **탐지 민감도(Confidence)** 를 실시간 조절하며 결과 확인. | <img src="https://github.com/user-attachments/assets/c5f1f20c-cab5-4bef-8083-16d5ca8a29f2" width="400" /> |


