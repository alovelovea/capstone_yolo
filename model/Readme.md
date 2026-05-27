

# 📜  model (Workflow)





---

 ### 1. 데이터 전처리 (`proprecessing.py`)

| 단계 | 주요 역할 | 기술적 상세 및 상세 기능 | 수행 결과 |
|:---:|:---:|:---|:---:|
| **1** | **데이터셋 구축** | 원본 데이터 분류, Train/Validation(8:2) 분할, `dataset.yaml` 자동 생성, 데이터 무결성(파일 손상/경로/범위) 검사 | <img src="https://github.com/user-attachments/assets/a1381ae7-5230-4f34-895f-4e74e9ccb748" width="350"/> |
| **2** | **분포 분석** | 클래스별 인스턴스 수 및 박스 크기 분포 히스토그램 시각화, 불균형 판단 임계값(Threshold) 설정, 부족한 데이터 증강 수량 자동 계산 | <img src="https://github.com/user-attachments/assets/fbee09b7-4289-4eb6-82ef-3c64e8fe4579" width="350"/> |
| **3** | **라벨 분석** | YOLO 라벨 구조(Box/Polygon) 식별, 비정상 좌표 및 면적 0인 박스 등 이상치 탐지, 학습 적합성 검증 | <img src="https://github.com/user-attachments/assets/7671abde-7934-4b82-a143-0aba24351588" width="350"/> |
| **4** | **형식 표준화** | Segmentation(폴리곤) 데이터를 YOLO Detection(Center x, y, w, h) 형식으로 변환, 정밀도 손실 방지를 위한 부동소수점 최적화 처리 | <img src="https://github.com/user-attachments/assets/9f8d14a6-7888-466f-8b1d-0764a5302156" width="350"/><br><img src="https://github.com/user-attachments/assets/b0b2131f-52b0-4687-85f8-ffe5e3e52f86" width="350"/> |
| **5** | **데이터 증강** | Albumentations 라이브러리를 활용한 기하학적 변환(Brightness, Blur, Flip 등) 및 라벨 좌표 동기화, 부족한 클래스 보강을 통한 강건성 확보 | <img src="https://github.com/user-attachments/assets/ddbcc5e3-5c41-4556-9f15-eb3e31124d4a" width="350"/><br><img src="https://github.com/user-attachments/assets/4365727d-7226-4502-a4d2-9868973c2c69" width="350"/> |
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

