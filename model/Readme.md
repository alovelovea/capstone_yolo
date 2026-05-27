

# 📜  model (Workflow)





---

 ### 1. 데이터 전처리 (`proprecessing.py`)

| 단계 | 주요 역할 | 기술적 상세 및 상세 기능 | 수행 결과 |
|:---:|:---:|:---|:---:|
| **1** | **데이터셋 구축** | 클래스별 원본 데이터를 기반으로 Train/Validation(8:2) 자동 분할 수행. 라벨 존재 여부·빈 라벨·이미지-라벨 불일치 등 데이터 무결성 검사를 통해 비정상 데이터를 제거하고, 클래스 균형 보정 및 `dataset.yaml` 자동 생성을 통해 YOLO 학습용 `balanced_dataset` 구축. | <img src="https://github.com/user-attachments/assets/a1381ae7-5230-4f34-895f-4e74e9ccb748" width="350"/> |
| **2** | **분포 분석** | Train/Validation 데이터셋의 클래스별 분포 및 비율을 자동 분석하고, 클래스 불균형 여부를 확인. 클래스별 총 데이터 수와 학습 비율을 계산하여 부족한 클래스의 추가 증강 필요 수량 자동 산출. | <img src="https://github.com/user-attachments/assets/fbee09b7-4289-4eb6-82ef-3c64e8fe4579" width="350"/> |
| **3** | **라벨 분석** | YOLO 라벨 파일을 대상으로 Detection(Box)·Segmentation(Polygon) 형식을 자동 식별하고, 비정상·빈 라벨 등 오류 데이터를 검사. 클래스별 라벨 형식 통계를 분석하여 학습 가능한 Detection 형식으로의 통일 여부 검증. | <img src="https://github.com/user-attachments/assets/7671abde-7934-4b82-a143-0aba24351588" width="350"/> |
| **4** | **형식 표준화** | Segmentation(Polygon) 라벨 데이터를 YOLO Detection(Box) 형식(`class x_center y_center width height`)으로 자동 변환하고, 좌표 범위 보정 및 부동소수점 정밀도 처리를 수행. 또한 invalid 라벨 검사를 통해 전체 `balanced_dataset`의 Detection 형식 통일 여부 검증. | <img src="https://github.com/user-attachments/assets/9f8d14a6-7888-466f-8b1d-0764a5302156" width="350"/><br><img src="https://github.com/user-attachments/assets/b0b2131f-52b0-4687-85f8-ffe5e3e52f86" width="350"/> |
| **5** | **데이터 증강** | Albumentations 기반 Horizontal Flip, Brightness/Contrast, HSV 변환, Gaussian Blur 등의 데이터 증강 기법을 적용하여 부족한 `plastic` 클래스 데이터 자동 보강. 증강 과정에서 YOLO Bounding Box 좌표를 동기화·보정하고, 범위 검사 및 clipping 처리를 통해 학습 가능한 라벨 정합성 유지. | <img src="https://github.com/user-attachments/assets/ddbcc5e3-5c41-4556-9f15-eb3e31124d4a" width="350"/><br><img src="https://github.com/user-attachments/assets/4365727d-7226-4502-a4d2-9868973c2c69" width="350"/> |
---

### 2. 모델 학습 (`train.py`)

| 주요 역할 및 기능 | 코드 수행 결과 |
|:---|:---:|
| 전처리 및 클래스 균형 보정이 완료된 데이터셋을 기반으로 **YOLOv11n** 모델 학습 수행. CUDA 기반 GPU 가속 환경에서 학습을 진행하고, Mosaic·MixUp·HSV 변환 등 다양한 데이터 증강 기법을 적용하여 일반화 성능 향상 및 클래스 불균형 문제를 완화. 학습 과정에서 Validation 성능을 모니터링하며 최적 성능의 가중치(`best.pt`) 자동 저장. | <img src="https://github.com/user-attachments/assets/567f74b4-4e14-4092-8d8d-e173d85dd753" width="1200"/> |

---

### 3. 예측 (`predict.py`)

<table>
  <thead>
    <tr>
      <th style="width: 600px;">주요 역할 및 기능</th>
      <th>수행 결과</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>
        학습된 YOLO 모델의 성능을 현장에서 즉각적으로 검증할 수 있는 인터랙티브 추론 뷰어. <code>testdata</code> 폴더에 이미지를 저장하여 즉시 모델의 탐지 결과를 시각화하고, 파라미터를 실시간으로 튜닝하며 성능을 분석.<br><br>
        <strong>⌨️ [단축키 가이드]</strong><br>
        • <b>이미지 이동</b>: <code>←</code>/<code>→</code> 또는 <code>a</code>/<code>d</code><br>
        • <b>민감도(Conf)</b>: <code>↑</code>/<code>↓</code> 또는 <code>w</code>/<code>s</code><br>
        • <b>프로그램 종료</b>: <code>q</code>
      </td>
      <td align="center"><img src="https://github.com/user-attachments/assets/c5f1f20c-cab5-4bef-8083-16d5ca8a29f2" width="400" /></td>
    </tr>
  </tbody>
</table>

