


# 📜  model (Workflow)





---

 ### 1. 데이터 전처리 (`preprocessing.py`)
<table>
  <tr>
    <th width="7%">단계</th>
    <th width="15%">주요 역할</th>
    <th width="33%">기술적 상세 및 상세 기능</th>
    <th width="45%">수행 결과</th>
  </tr>

  <tr>
    <td align="center"><b>1</b></td>
    <td align="center"><b>데이터셋 구축</b></td>
    <td>
      클래스별 원본 데이터를 기반으로 Train/Validation(8:2) 자동 분할 수행.
      라벨 존재 여부·빈 라벨·이미지-라벨 불일치 등 데이터 무결성 검사를 통해
      비정상 데이터를 제거하고, 클래스 균형 보정 및
      <code>dataset.yaml</code> 자동 생성 수행.
    </td>
    <td align="center">
      <img src="https://github.com/user-attachments/assets/a1381ae7-5230-4f34-895f-4e74e9ccb748" width="700"/>
    </td>
  </tr>

  <tr>
    <td align="center"><b>2</b></td>
    <td align="center"><b>분포 분석</b></td>
    <td>
      Train/Validation 데이터셋의 클래스별 분포 및 비율을 자동 분석하고,
      부족한 클래스의 추가 증강 필요 수량 자동 산출.
    </td>
    <td align="center">
      <img src="https://github.com/user-attachments/assets/fbee09b7-4289-4eb6-82ef-3c64e8fe4579" width="700"/>
    </td>
  </tr>

  <tr>
    <td align="center"><b>3</b></td>
    <td align="center"><b>라벨 분석</b></td>
    <td>
      Detection(Box)·Segmentation(Polygon) 형식을 자동 식별하고,
      비정상·빈 라벨 등 오류 데이터를 검사하여
      Detection 형식 통일 여부 검증.
    </td>
    <td align="center">
      <img src="https://github.com/user-attachments/assets/7671abde-7934-4b82-a143-0aba24351588" width="700"/>
    </td>
  </tr>

  <tr>
    <td align="center"><b>4</b></td>
    <td align="center"><b>형식 표준화</b></td>
    <td>
      Segmentation 라벨을 YOLO Detection 형식으로 자동 변환하고,
      좌표 범위 보정 및 부동소수점 정밀도 처리 수행.
    </td>
    <td align="center">
      <img src="https://github.com/user-attachments/assets/9f8d14a6-7888-466f-8b1d-0764a5302156" width="700"/><br><br>
      <img src="https://github.com/user-attachments/assets/b0b2131f-52b0-4687-85f8-ffe5e3e52f86" width="700"/>
    </td>
  </tr>

  <tr>
    <td align="center"><b>5</b></td>
    <td align="center"><b>데이터 증강</b></td>
    <td>
      Albumentations 기반 증강 기법을 적용하여 부족한
      <code>plastic</code> 클래스 자동 보강 및
      Bounding Box 좌표 동기화 수행.
    </td>
    <td align="center">
      <img src="https://github.com/user-attachments/assets/ddbcc5e3-5c41-4556-9f15-eb3e31124d4a" width="700"/><br><br>
      <img src="https://github.com/user-attachments/assets/4365727d-7226-4502-a4d2-9868973c2c69" width="700"/>
    </td>
  </tr>
</table>

---

## 2. 모델 학습 (`train.py`)

### 🧠 모델 개요

| 항목 | 내용 |
|:---|:---|
| **베이스 모델** | YOLOv11n (Nano) — Ultralytics 최신 아키텍처 |
| **사전학습 가중치** | `yolo11n.pt` (COCO Pretrained) |
| **학습 환경** | CUDA GPU 가속 (`device=0`, CPU Fallback 지원) |
| **데이터셋** | `balanced_dataset/dataset.yaml` (클래스 균형 보정 완료) |
| **검증 방식** | Train/Val 8:2 분할, 매 Epoch 종료 시 자동 검증(`val=True`) |

### ⚙️ 하이퍼파라미터 상세

| 분류 | 파라미터 | 값 | 설명 |
|:---|:---|:---:|:---|
| **학습 기본** | `epochs` | 100 | 전체 학습 반복 횟수 |
| | `imgsz` | 640 | 입력 이미지 해상도 (정사각형) |
| | `batch` | 16 | 배치 크기 (GPU 메모리 고려) |
| | `workers` | 8 | 데이터 로더 병렬 워커 수 |
| | `optimizer` | Auto | AdamW/SGD 자동 선택 |
| **정규화** | `patience` | 15 | Early Stopping 임계 Epoch |
| | `pretrained` | True | COCO 사전학습 가중치 활용 (Transfer Learning) |

### 🎨 데이터 증강(Augmentation) 전략

폐기물 객체는 **촬영 각도·조명·배경 다양성**이 실시간 분류 정확도에 직결됩니다. 이를 보완하기 위해 다양한 증강 기법을 조합 적용했습니다.

| 기법 | 값 | 효과 |
|:---|:---:|:---|
| 🎨 **HSV-Hue** | 0.015 | 색조 변화 → 조명·카메라 색감 차이 대응 |
| 🌈 **HSV-Saturation** | 0.7 | 채도 변화 → 다양한 환경광 시뮬레이션 |
| 💡 **HSV-Value** | 0.4 | 밝기 변화 → 실내외 조도 변화 대응 |
| 🔄 **Degrees** | 15.0° | 회전 → 비스듬히 놓인 폐기물 인식력 강화 |
| ↔️ **Translate** | 0.1 | 평행 이동 → 프레임 내 위치 변화 대응 |
| 📏 **Scale** | 0.5 | 크기 변화 → 거리 차이 대응 |
| ↩️ **FlipLR** | 0.5 | 좌우 반전 (확률 50%) |
| 🧩 **Mosaic** | 1.0 | 4장 이미지 합성 → 작은 객체·다중 객체 학습 강화 |
| 🎭 **Mixup** | 0.1 | 이미지 혼합 → 경계 모호 케이스에 대한 일반화 |

---

## 3. 학습 결과 분석 (`results.csv`)

### 📊 학습 곡선

| 학습 지표 그래프 (Loss) | 성능 평가 그래프 (Metrics) |
|:---:|:---:|
| 이미지 | 이미지 |

### 🏆 최종 성능 (Epoch 100 기준)

| 지표 | 최종 값 | 의미 |
|:---:|:---:|:---|
| **mAP@0.5** | `0.9415` | IoU 0.5 기준 평균 정밀도 — 폐기물 식별력 매우 우수 |
| **mAP@0.5:0.95** | `0.8124` | 엄격한 IoU 구간 평균 — 정밀 위치 추정 능력 |
| **Precision** | `0.935` | 탐지한 객체 중 실제 정답 비율 → **오탐(FP) 낮음** |
| **Recall** | `0.889` | 실제 객체 중 탐지에 성공한 비율 → **누락(FN) 적음** |

### 💡 핵심 분석 요약

> **1. 안정적 수렴 (Stable Convergence)**
> Train/Val Loss 격차가 매우 작아 과적합 없이 이상적으로 학습되었습니다. Mosaic·Mixup 증강이 정규화 역할을 효과적으로 수행했음을 확인할 수 있습니다.

> **2. Precision 우위 (0.935 > Recall 0.889)**
> **오탐지 제어 능력이 우수**합니다. 잘못된 분류를 최소화해야 하는 실서비스 환경에 매우 유리한 특성입니다.

> **3. 실서비스 배포 적합성**
> 최종 `best.pt` 가중치는 **mAP 0.94 + 경량 모델(Nano)** 조합으로 실시간 추론 환경에서 충분한 응답속도와 정확도를 동시에 만족합니다.

---

### 4. 예측 (`realtime_predict.py`)


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
        실제 카메라와 연결하여 학습된 YOLO 모델을 활용하여 <b>웹캠 실시간 영상에서 폐기물을 추적(ByteTrack) 및 분류</b>하는 모듈. 3초 간격으로 탐지 데이터를 수집하고, 다수결 알고리즘을 통해 최종 폐기물 종류를 판별하여 정밀도를 향상시킴.<br><br>
        <strong>⌨️ [운용 가이드]</strong><br>
        • <b>실시간 분석</b>: 카메라 입력(640x480) 기반 객체 탐지 및 추적<br>
        • <b>안정화 로직</b>: 3초 주기로 데이터를 버퍼링하여 결과값 보정<br>
        • <b>종료 키</b>: <code>q</code> (프로그램 즉시 종료)
      </td>
      <td align="center">
        <table style="border: none; background: none;">
          <tr>
            <td><img src="https://github.com/user-attachments/assets/c5f1f20c-cab5-4bef-8083-16d5ca8a29f2" width="220" /></td>
            <td><img src="https://github.com/user-attachments/assets/76eb6ac8-9a3d-453e-a0b1-9d781060b6f4" width="220" /></td>
          </tr>
          <tr>
            <td><img src="https://github.com/user-attachments/assets/8ae93b47-e9c7-45c4-b422-42e54943fd39" width="220" /></td>
            <td><img src="https://github.com/user-attachments/assets/5efe4c9a-7761-4948-b381-11ad91932638" width="220" /></td>
          </tr>
        </table>
      </td>
    </tr>
  </tbody>
</table>
