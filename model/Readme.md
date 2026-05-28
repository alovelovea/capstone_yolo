


# 📜  model (Workflow)





---

 ### 1. 데이터 전처리 (`proprecessing.py`)
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

### 2. 모델 학습 (`train.py`)

| 주요 역할 및 기능 | 수행 결과 |
|:---|:---:|
| 전처리 및 클래스 균형 보정이 완료된 데이터셋을 기반으로 **YOLOv11n** 모델 학습 수행. CUDA 기반 GPU 가속 환경에서 학습을 진행하고, Mosaic·MixUp·HSV 변환 등 다양한 데이터 증강 기법을 적용하여 일반화 성능 향상 및 클래스 불균형 문제를 완화. 학습 과정에서 Validation 성능을 모니터링하며 최적 성능의 가중치(`best.pt`) 자동 저장. | <img src="https://github.com/user-attachments/assets/567f74b4-4e14-4092-8d8d-e173d85dd753" width="3000"/> |



---

### 3. 예측 (`realtime_predict.py`)

### 3. 예측 (`realtime_predict.py`)

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
        학습된 YOLO 모델을 활용하여 <b>웹캠 실시간 영상에서 폐기물을 추적(ByteTrack) 및 분류</b>하는 모듈입니다. 3초 간격으로 탐지 데이터를 수집하고, 다수결 알고리즘을 통해 최종 폐기물 종류를 판별하여 정밀도를 향상시킵니다.<br><br>
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
