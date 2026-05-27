

# 📜  model (Workflow)





---

 ### 1. proprecessing.py

| 단계 | 주요 역할 | 기술적 상세 및 상세 기능 | 수행 결과 |
| :---: | :---: | :--- | :--- |
| **1** | 데이터셋 구축 | 원본 데이터 분류, Train/Validation(8:2) 분할, `dataset.yaml` 자동 생성, 데이터 무결성(파일 손상/경로/범위) 검사. | <img src="https://github.com/user-attachments/assets/a1381ae7-5230-4f34-895f-4e74e9ccb748" /> |
| **2** | 분포 분석 | 클래스별 인스턴스 수 및 박스 크기 분포 히스토그램 시각화, 불균형 판단 임계값(Threshold) 설정, 부족한 데이터 증강 수량 자동 계산. | <img src="https://github.com/user-attachments/assets/fbee09b7-4289-4eb6-82ef-3c64e8fe4579" /> |
| **3** | 라벨 분석 | YOLO 라벨 구조(Box/Polygon) 식별, 비정상 좌표 및 면적 0인 박스 등 이상치 탐지, 학습 적합성 검증. | <img src="https://github.com/user-attachments/assets/7671abde-7934-4b82-a143-0aba24351588" /> |
| **4** | 형식 표준화 | Segmentation(폴리곤) 데이터를 YOLO Detection(Center x, y, w, h) 형식으로 변환, 정밀도 손실 방지를 위한 부동소수점 최적화 처리. | <img src="https://github.com/user-attachments/assets/9f8d14a6-7888-466f-8b1d-0764a5302156" /><br><img src="https://github.com/user-attachments/assets/b0b2131f-52b0-4687-85f8-ffe5e3e52f86" /> |
| **5** | 데이터 증강 | Albumentations 라이브러리를 활용한 기하학적 변환(밝기, Blur, Flip 등) 및 라벨 좌표 동기화, 부족한 클래스 보강을 통한 강건성 확보. | <img src="https://github.com/user-attachments/assets/ddbcc5e3-5c41-4556-9f15-eb3e31124d4a" /><br><img src="https://github.com/user-attachments/assets/4365727d-7226-4502-a4d2-9868973c2c69" /> |
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


