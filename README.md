# Olist E-commerce Data Analysis Portfolio

브라질 Olist 이커머스 데이터를 기반으로, 마켓플레이스 운영 병목과 고객 경험/리텐션에 영향을 주는 요인을 분석하는 프로젝트입니다.

## Project Goal

1. 주문-배송 퍼널 병목 구간 진단
2. 배송 성과와 고객 만족도(리뷰 점수) 관계 분석
3. 코호트 리텐션/공급-수요 매칭으로 확장 가능한 분석 자산 구축

## Repository Structure

```text
olist-data-project/
├── sql/
│   ├── staging/      # 정제/표준화 쿼리
│   ├── marts/        # 분석용 마트 생성 쿼리
│   └── analysis/     # 비즈니스 질문별 분석 쿼리
├── results/
│   ├── tables/       # BigQuery 결과 CSV
│   └── figures/      # 차트/이미지 결과물
├── python_scripts/   # 실행/자동화 스크립트
├── notebooks/
├── dashboard/
└── docs/             # Obsidian 문서 링크
```

## Current Progress

- 완료: BigQuery 적재/기초 정제, 카테고리 영문화 뷰, 운영 퍼널 마트 초안
- 진행: 배송 지연과 리뷰 점수 상관관계 분석 고도화
- 예정: 코호트 리텐션, 공급-수요 매칭, 대시보드 통합

핵심 SQL 파일:

- `sql/staging/fix_translation_header.sql`
- `sql/staging/create_view_products_english.sql`
- `sql/marts/create_mart_order_operational_funnel.sql`
- `sql/analysis/category_delivery_review_analysis.sql`
- `sql/analysis/ad_hoc_business_queries.sql`

## BigQuery + Local Workflow

원칙:

- BigQuery: 실행 환경(`raw -> staging -> mart -> analytics`)
- Local Repo: 재현 가능한 분석 자산(SQL, 결과 CSV, 문서, 차트)

권장 루프:

1. BigQuery에서 SQL 실행/검증
2. 확정 쿼리를 `sql/...`에 저장
3. 결과를 `results/tables/*.csv`로 저장
4. 차트 생성 후 `results/figures` 반영
5. README/docs에 인사이트 업데이트

## Quick Start (CLI)

사전 준비:

1. Google Cloud SDK 설치
2. 인증

```bash
gcloud auth application-default login
gcloud config set project <YOUR_GCP_PROJECT_ID>
```

3. `bq` 명령 확인

```bash
bq version
```

## Auto Export Script

아래 스크립트로 SQL 파일을 실행하고 결과를 바로 CSV로 저장할 수 있습니다.

```bash
bash python_scripts/run_bq_query_to_csv.sh \
  sql/analysis/category_delivery_review_analysis.sql \
  category_delivery_review
```

결과 예시:

- `results/tables/category_delivery_review_YYYYMMDD_HHMMSS.csv`

## Roadmap (Analysis -> ML)

### Phase 1. SQL Analytics Completion

1. 배송 지연 구간별 만족도 하락 임계점 분석
2. 카테고리/지역별 리드타임 편차 분석
3. 코호트 리텐션(재구매율) 분석 연결

### Phase 2. ML-ready Dataset

1. 예측 타깃 정의: `is_delayed`(지연 여부) 또는 `delay_days`(지연 일수)
2. 피처 엔지니어링:
   - 주문 시점 정보(월/요일/시간대)
   - 상품 카테고리/규격(무게, 부피)
   - 판매자/고객 지역 정보
   - 결제 방식, 배송비, 주문 금액
3. 학습용 스냅샷 테이블 생성(`mart_delivery_ml_base`)

### Phase 3. Predictive Modeling

1. 기준 모델(Baseline): Logistic Regression / Random Forest
2. 성능 지표:
   - 분류(`is_delayed`): ROC-AUC, F1, Precision/Recall
   - 회귀(`delay_days`): MAE, RMSE
3. 해석:
   - Feature Importance/SHAP로 지연 기여 요인 도출

### Phase 4. Operationalization

1. 예측 결과를 BigQuery 테이블로 적재
2. `results/tables`, `results/figures` 자동 갱신
3. 대시보드에서 "지연 위험 주문" 모니터링
