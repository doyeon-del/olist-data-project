# Olist E-commerce Data 분석 프로젝트

브라질 Olist 이커머스 데이터를 기반으로, 마켓플레이스 운영 과정에서 발생하는 병목과 고객 경험 및 리텐션에 영향을 주는 요인을 분석하는 프로젝트입니다.

## 프로젝트 목표

1. 주문-배송 퍼널 병목 구간 진단
2. 배송 성과와 고객 만족도(리뷰 점수) 관계 분석
3. 코호트 리텐션/공급-수요 매칭으로 확장 가능한 분석 자산 구축

## 데이터 출처

[Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) (Kaggle · 라이선스 CC BY-NC-SA 4.0)를 사용합니다. 

브라질 이커머스 플랫폼 Olist의 **2016–2018년 실제 주문 약 10만 건**을 익명화한 공개 데이터셋이며, 원천 테이블을 BigQuery `olist_raw`로 적재해 사용합니다.

| 테이블 | 내용 |
|---|---|
| `orders` | 주문 상태, 구매·승인·택배사 인계·고객 수령·예상 배송 시점 |
| `order_items` | 주문별 상품·판매자·가격·배송비 |
| `customers` / `sellers` | 고객·판매자 ID 및 지역(주) |
| `products` | 상품 카테고리·무게·크기 |
| `order_reviews` | 1–5점 리뷰 점수 |
| `order_payments` | 결제 방식·금액 |
| `product_category_name_translation` | 카테고리명 영문 번역 |

## 기술 스택

| 도구 | 용도 / 선택 이유 |
|---|---|
| **BigQuery** | 원천 테이블을 조인·집계하는 클라우드 데이터 웨어하우스. `raw → staging → mart → analysis` 계층 모델링에 적합 |
| **SQL** | 정제(staging) → 분석용 통합 마트(marts) → 질문별 분석(analysis)으로 계층화해 재현성·재사용성 확보 |
| **Python** | `pandas`(데이터 처리), `scipy`(통계 검정), `matplotlib`(정적 차트) |
| **Streamlit + Plotly** | 인터랙티브 대시보드. 코드가 레포에 남고 무료로 배포 가능 |
| **gcloud / bq CLI · Git** | 인증·쿼리 실행, 버전 관리 |

## 리포지토리 구조

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
├── dashboard/        # Streamlit 대시보드 (app.py, data.py)
├── .streamlit/       # 테마 + secrets 템플릿
├── requirements.txt  # 대시보드 실행/배포 의존성
└── docs/             # Obsidian 문서 링크
```

## 작업 과정

**SQL 분석 자산 → BigQuery 결과 → 시각화 → 인터랙티브 대시보드** 구성

완료:

- BigQuery 원천 데이터 적재 및 기초 정제
- 상품 카테고리 영문화 view 생성
- 주문/주문상품/배송피처/고객코호트 mart SQL 작성
- 배송 지연, 지역 매칭, 코호트 리텐션, 카테고리별 배송/리뷰 분석 CSV 생성
- 대표 분석 차트 4개 생성
- Obsidian 분석 노트 구조화
- **Streamlit + BigQuery 인터랙티브 대시보드 구축** (KPI 카드 + 4개 분석 탭 + 인사이트)

핵심 SQL 파일:

- `sql/staging/fix_translation_header.sql`
- `sql/staging/create_view_products_english.sql`
- `sql/marts/create_mart_orders.sql`
- `sql/marts/create_mart_order_items.sql`
- `sql/marts/create_mart_delivery_features.sql`
- `sql/marts/create_mart_customer_cohort_monthly.sql`
- `sql/analysis/delay_threshold_analysis.sql`
- `sql/analysis/geo_matching_leadtime_analysis.sql`
- `sql/analysis/cohort_retention_by_delay_experience.sql`
- `sql/analysis/category_delivery_review_by_category.sql`

## 핵심 인사이트

### 1. 3일 이상의 딜레이가 발생할 경우, 고객 리뷰의 점수가 급락한다.

![Delay threshold review score](results/figures/delay_threshold_review_score.png)

정시/조기 배송 주문의 평균 리뷰 점수는 **4.28**입니다. 1~2일 지연 시 **3.50**으로 하락하고, 3~4일 지연부터는 **2.58**까지 급락합니다. 낮은 리뷰 비율도 3~4일 지연 구간에서 **53.52%**까지 상승합니다.

### 2. 다른 주 간의 배송은 동일 주 내 배송보다 두 배 이상 걸렸다.

![Geo matching leadtime](results/figures/geo_matching_leadtime.png)

동일 주 배송의 평균 리드타임은 **7.48일**, 타 주 배송은 **14.68일**입니다.

### 3. 첫 구매 이후 월 별 리텐션은 1% 이하에 머물러 있다.

![Cohort retention by delay](results/figures/cohort_retention_by_delay.png)

첫 구매 이후 월별 리텐션은 전반적으로 매우 낮습니다. 첫 주문 지연 경험별 비교는 가능하지만, 코호트별 retained customer 수가 작기 때문에 표본 안정성 검토가 필요합니다.

### 4. Office furniture 카테고리는 가장 낮은 배달 경험을 제공한다.

![Category delivery review](results/figures/category_delivery_review_bubble.png)

`office_furniture`는 평균 리드타임이 **20.39일**로 가장 길고, 평균 리뷰 점수도 **3.50**으로 가장 낮습니다. 예상 배송일 대비 평균 지연이 음수여도, 고객이 체감하는 총 대기 시간이 길면 만족도에 부정적 영향을 줄 수 있습니다.

## 분석 방법론

이 프로젝트는 **기술통계 + 통계적 추론**으로 구성됩니다. 예측 ML 모델은 아직 포함하지 않으며, 확장 계획은 하단 [향후 계획](#향후-계획-ml-확장--미구현) 섹션을 참고하세요.

- **지연 구간 임계점 분석** — 예상일 대비 지연 일수를 구간화(D≤0, D+1\~2, D+3\~4 …)해 리뷰 점수가 급락하는 지점을 탐색합니다. 단순 선형 상관이 아니라 **비선형 임계 효과**를 드러내기 위함입니다.
- **지역 매칭 관찰 비교** — 판매자–고객이 동일 주인지(Same State) 타 주인지(Cross State)에 따라 리드타임·지연율을 비교해 배송 속도의 구조적 요인을 진단합니다.
- **Welch t-검정 + Cohen's d + 95% 신뢰구간** — 지연군 vs 정시군의 평균 리뷰 차이를 검정합니다. 두 집단의 분산·표본 크기 차이가 커서 등분산을 가정하는 Student t 대신 **Welch's t**를 사용했습니다. 표본이 커서 p값은 거의 0이 되므로, 실질적 크기는 **효과크기(Cohen's d)와 신뢰구간**으로 판단합니다. 무작위 배정 실험이 아니므로 **인과가 아닌 관찰적 비교**임을 명시합니다(A/B 테스트와 구분).
- **코호트 리텐션 분석** — 첫 주문 월을 기준으로 월별 재구매(잔존)율을 추적합니다. 단, Olist는 재구매가 희소해(리텐션 1% 미만) 코호트별 표본이 작으므로 **방향성 참고**로만 해석합니다.


---

## BigQuery 기반으로 로컬 환경에서 시행하는 방법

원칙:

- BigQuery: 실행 환경(`raw -> staging -> mart -> analytics`)
- Local Repo: 재현 가능한 분석 자산(SQL, 결과 CSV, 문서, 차트)

권장 루프:

1. BigQuery에서 SQL 실행/검증
2. 확정 쿼리를 `sql/...`에 저장
3. 결과를 `results/tables/*.csv`로 저장
4. 차트 생성 후 `results/figures` 반영
5. README/docs에 인사이트 업데이트

---

## 인터렉티브 대시보드 구성 - Streamlit과 BigQuery 활용

`dashboard/app.py`는 KPI 카드와 6개 탭(퍼널 / 통계 검정 / 배송 지연 / 지역 매칭 /
카테고리 / 리텐션), 인사이트 섹션으로 구성된 인터랙티브 대시보드입니다.
사이드바에서 **한국어/English 토글**을 지원합니다.

`통계 검정` 탭은 지연군 vs 정시군의 리뷰 점수 차이에 Welch t-검정, Cohen's d,
95% 신뢰구간을 적용합니다. Olist에는 실험 데이터가 없으므로 이는 무작위 배정 A/B
테스트가 아니라 **관찰적 비교**이며, 탭에 그 한계를 명시합니다.


### 데이터 소스:

- **기본: BigQuery** — `dashboard/data.py`가 `sql/analysis/*.sql`을 그대로 실행합니다
  (분석 파이프라인과 단일 소스 공유).
- **폴백: CSV** — 자격증명이 없으면 `results/tables`의 커밋된 CSV로 자동 전환되어,
  인증 없이도 대시보드를 띄울 수 있습니다.

---

### 로컬 실행

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# BigQuery 라이브 조회용 인증 (없으면 CSV 폴백)
gcloud auth application-default login

streamlit run dashboard/app.py
```
