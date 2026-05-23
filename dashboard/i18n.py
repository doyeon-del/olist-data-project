"""UI strings for the dashboard in Korean and English.

Keys are shared; ``TEXT[lang][key]`` returns the localized string. Strings with
``{placeholders}`` are formatted in app.py with computed numbers.
"""

LANGS = {"한국어": "ko", "English": "en"}

# Display labels for values that come from the data (not free text).
VALUE_LABELS = {
    "ko": {
        "Same State": "동일 주",
        "Cross State": "타 주",
        "Delayed First Order": "첫 주문 지연",
        "On-time/Early First Order": "첫 주문 정시/조기",
    },
    "en": {
        "Same State": "Same State",
        "Cross State": "Cross State",
        "Delayed First Order": "Delayed first order",
        "On-time/Early First Order": "On-time/early first order",
    },
}

TEXT = {
    "ko": {
        "title": "Olist 배송 & 고객 경험",
        "caption": "Olist 브라질 마켓플레이스 데이터에서 배송 성과가 고객 평점에 미치는 영향. "
        "데이터는 BigQuery에서 앱이 직접 조회합니다.",
        "lang_label": "언어",
        "sidebar_source": "데이터 소스",
        "source_live": "BigQuery 라이브",
        "source_fallback": "CSV 폴백 (BigQuery 사용 불가)",
        "sidebar_caption": "프로젝트 `olist-analysis-project-495210`. "
        "각 탭은 `sql/analysis/`의 해당 쿼리를 실행합니다.",
        # KPI
        "kpi_orders": "배송 완료 주문",
        "kpi_leadtime": "평균 리드타임",
        "kpi_review": "평균 리뷰 점수",
        "kpi_delay": "지연율",
        "unit_days": "일",
        # tabs
        "tab_funnel": "퍼널",
        "tab_stats": "통계 검정",
        "tab_delay": "배송 지연",
        "tab_geo": "지역 매칭",
        "tab_category": "카테고리",
        "tab_retention": "리텐션",
        "tab_insights": "인사이트",
        # funnel
        "funnel_title": "주문 처리 퍼널",
        "funnel_stages": ["구매", "승인", "택배사 인계", "배송 완료"],
        "funnel_text": "전체 {placed:,}건의 주문 중 {pct:.1f}%가 고객에게 도착합니다. "
        "단계별 이탈은 승인→택배사 {ship:.1f}%, 택배사→고객 {deliver:.1f}%이고, "
        "가장 큰 누수는 **{bottleneck}** 구간입니다.",
        "funnel_leg_approve": "승인→택배사",
        "funnel_leg_deliver": "택배사→고객",
        "funnel_expander": "단계별 건수",
        "col_stage": "단계",
        "col_orders": "주문 수",
        # stats
        "stats_title": "지연군 vs 정시군 리뷰 점수 차이 (Welch t-검정)",
        "stats_intro": "배송이 예상일보다 늦은 주문과 그렇지 않은 주문의 평균 리뷰 점수를 "
        "통계적으로 비교합니다. 이는 무작위 배정 실험이 아니라 **관찰적 비교**이므로, "
        "차이를 인과로 단정할 수 없습니다 (A/B 테스트와 구분).",
        "stats_group_delayed": "지연군 (예상일 초과)",
        "stats_group_ontime": "정시/조기군",
        "stats_mean": "평균 리뷰",
        "stats_n": "표본 수",
        "stats_diff": "평균 차이 (정시 − 지연)",
        "stats_metrics_caption": "오차 막대는 95% 신뢰구간입니다.",
        "stats_result": "정시/조기군의 평균 리뷰는 지연군보다 **{diff:.2f}점** 높습니다 "
        "(95% CI {lo:.2f}~{hi:.2f}). Welch t({df:,.0f}) = {t:,.1f}, p {p}. "
        "효과크기 Cohen's d = {d:.2f}로 큰 차이에 해당합니다.",
        "stats_caveat": "해석: p값은 표본이 커서 거의 0이지만, 핵심은 효과크기와 신뢰구간입니다. "
        "지연을 겪은 고객이 더 낮은 점수를 주는 경향은 강하고 일관되나, "
        "관찰 데이터이므로 다른 요인(카테고리·지역 등)이 섞여 있을 수 있습니다.",
        "stats_axis": "평균 리뷰 점수",
        # delay
        "delay_title": "예상일 대비 지연 일수별 리뷰 점수",
        "delay_y1": "평균 리뷰 점수",
        "delay_y2": "낮은 점수 비율 (%)",
        "delay_legend_score": "평균 리뷰 점수",
        "delay_legend_low": "낮은 점수 비율 (%)",
        "delay_text": "정시·조기 배송 주문의 평균은 {on_time:.2f}점입니다. "
        "3~4일 지연 구간부터 점수가 떨어지고, 일주일 이상 지연되면 "
        "낮은 점수(2점 이하) 비율이 {low:.0f}%를 넘습니다.",
        "delay_expander": "쿼리 결과",
        # geo
        "geo_title": "판매자–고객 지역에 따른 리드타임",
        "geo_axis": "평균 리드타임 (일)",
        "geo_delay_rate": "지연율 {v:.2f}%",
        "geo_text": "고객과 같은 주에서 발송된 주문은 약 절반의 시간에 도착하고, "
        "예상일을 놓치는 비율도 더 낮습니다.",
        "geo_expander": "쿼리 결과",
        # category
        "cat_title": "상품 카테고리별 리드타임 vs 리뷰 점수",
        "cat_desc": "여기서 '카테고리'는 Olist의 **상품 종류**예요(예: bed_bath_table 침구·욕실, "
        "office_furniture 사무가구). 점 하나가 카테고리 하나이고, 가로축은 평균 배송 리드타임, "
        "세로축은 평균 리뷰 점수, 점 크기는 주문 수입니다. 점선은 전체 평균선이라, "
        "오른쪽 아래(느린 배송 + 낮은 평점)에 있을수록 취약한 카테고리예요.",
        "cat_slider": "표시할 카테고리 — 최소 주문 수",
        "cat_slider_help": "선택한 값 이상 주문된 카테고리만 표시해요. 주문이 적은 카테고리를 "
        "걸러내 평균 비교를 안정적으로 만듭니다.",
        "cat_shown": "표시 중인 카테고리: {n}개",
        "cat_x": "평균 리드타임 (일)",
        "cat_y": "평균 리뷰 점수",
        "cat_hover_lead": "리드타임",
        "cat_hover_review": "리뷰",
        "cat_hover_orders": "주문",
        "cat_weak": "평균 리뷰 미만이면서 평균 리드타임을 초과하는 카테고리:",
        "cat_col_name": "카테고리",
        "cat_col_orders": "주문 수",
        "cat_col_lead": "평균 리드타임",
        "cat_col_review": "평균 리뷰",
        # retention
        "ret_title": "첫 주문 배송 경험별 리텐션",
        "ret_info": "Olist는 사실상 일회성 구매 마켓입니다. 첫 달 이후 리텐션이 모든 코호트에서 "
        "1% 미만이고, 첫 주문 지연 그룹의 표본도 작습니다. 아래 차이는 결론이 아니라 "
        "방향성 참고로만 보세요.",
        "ret_x": "첫 구매 이후 경과 개월",
        "ret_y": "리텐션 비율 (%)",
        # insights
        "insights_title": "데이터가 말하는 것",
        "insights_body": """
**속도보다 '약속보다 늦었는지'가 중요합니다.**
평균 리뷰는 정시 주문 4.28점에서 3~4일 지연 시 2.58점으로, 일주일 이상 지연되면 2.0점
아래로 떨어집니다. 핵심 신호는 절대 배송 일수가 아니라 "예상일보다 늦었는가"입니다.

**거리가 속도의 상한을 정합니다.**
동일 주 배송은 약 7.5일, 타 주 배송은 14.7일이 걸립니다. 지역별 판매자 구성은 단순
물류 디테일이 아니라 리드타임을 좌우하는 구조적 변수입니다.

**배송 리스크는 일부 부피 큰 카테고리에 몰려 있습니다.**
office_furniture 같은 카테고리는 가장 긴 리드타임과 가장 낮은 리뷰를 함께 가지므로,
마켓 전체에 단일 배송 예상일을 적용하면 이들에게 불리합니다.

**재구매는 거의 없습니다.**
리텐션이 코호트 전반에서 1% 미만이라, 첫 주문이 사실상 관계의 전부입니다. 같은 희소성
때문에 지연-리텐션 비교도 방향성 정도로만 읽어야 합니다.
""",
        "insights_caption": "파이프라인: BigQuery 마트 → `sql/analysis/`의 집계 쿼리 → 본 대시보드.",
        "insight_goto": "‘{tab}’ 탭에서 근거 보기 →",
        "insight_1_title": "지연이 '속도'보다 만족도를 더 좌우합니다",
        "insight_1_body": "정시·조기 배송의 평균 리뷰는 **{ontime:.2f}점**인데, 예상일보다 3~4일만 "
        "늦어도 **{late:.2f}점**으로 떨어집니다. 핵심은 절대 배송 일수가 아니라 "
        "'약속보다 늦었는가'예요.",
        "insight_2_title": "거리가 배송 속도의 상한을 정합니다",
        "insight_2_body": "동일 주 배송은 평균 **{same:.1f}일**, 타 주 배송은 **{cross:.1f}일**로 약 "
        "두 배입니다. 지역별 판매자 구성이 리드타임을 좌우하는 구조적 변수예요.",
        "insight_3_title": "배송 리스크는 일부 카테고리에 몰려 있습니다",
        "insight_3_body": "`{cat}`는 평균 리드타임 **{lead:.1f}일**로 가장 길고 평균 리뷰도 "
        "**{rev:.2f}점**으로 낮습니다. 마켓 전체에 단일 배송 예상일을 적용하면 이런 "
        "카테고리엔 불리해요.",
        "insight_4_title": "재구매는 거의 없습니다",
        "insight_4_body": "첫 달 이후 리텐션이 모든 코호트에서 1% 미만이라, 첫 주문이 사실상 관계의 "
        "전부입니다. 같은 희소성 때문에 지연-리텐션 비교도 방향성으로만 읽어야 해요.",
        "nav_label": "보기 선택",
        "rows": "행",
        "query_running": "BigQuery에서 쿼리 실행 중…",
        "query_done": "BigQuery에서 {n}행 반환 완료",
        "view_sql": "실행된 SQL 보기",
        "lineage_via": "쿼리",
        "c_bucket": "지연 구간",
        "c_orders": "주문 수",
        "c_avg_delay": "평균 지연(일)",
        "c_avg_review": "평균 리뷰 (0–5)",
        "c_low_rate": "낮은 점수 비율",
        "c_match": "지역 매칭",
        "c_avg_leadtime": "평균 리드타임(일)",
        "c_delay_rate": "지연율",
        "c_stage": "단계",
    },
    "en": {
        "title": "Olist Delivery & Experience",
        "caption": "Where delivery performance affects customer ratings in the Olist Brazilian "
        "marketplace dataset. Source: BigQuery, queried live by this app.",
        "lang_label": "Language",
        "sidebar_source": "Data source",
        "source_live": "Live from BigQuery",
        "source_fallback": "CSV fallback (BigQuery unavailable)",
        "sidebar_caption": "Project `olist-analysis-project-495210`. "
        "Each tab runs the matching query in `sql/analysis/`.",
        "kpi_orders": "Delivered orders",
        "kpi_leadtime": "Avg lead time",
        "kpi_review": "Avg review score",
        "kpi_delay": "Delay rate",
        "unit_days": "days",
        "tab_funnel": "Funnel",
        "tab_stats": "Statistical test",
        "tab_delay": "Delivery delay",
        "tab_geo": "Geo matching",
        "tab_category": "Category",
        "tab_retention": "Retention",
        "tab_insights": "Insights",
        "funnel_title": "Order fulfillment funnel",
        "funnel_stages": ["Purchased", "Approved", "Shipped to carrier", "Delivered"],
        "funnel_text": "Of {placed:,} placed orders, {pct:.1f}% reach the customer. Stage "
        "drop-off is {ship:.1f}% at approval->carrier and {deliver:.1f}% at carrier->customer, "
        "so the biggest leak is **{bottleneck}**.",
        "funnel_leg_approve": "approval->carrier",
        "funnel_leg_deliver": "carrier->customer",
        "funnel_expander": "Stage counts",
        "col_stage": "Stage",
        "col_orders": "Orders",
        "stats_title": "Review score: delayed vs. on-time orders (Welch's t-test)",
        "stats_intro": "Comparing mean review scores for orders that arrived later than the "
        "estimate against those that did not. This is an **observational comparison**, not a "
        "randomized experiment, so the gap is not proof of causation (unlike an A/B test).",
        "stats_group_delayed": "Delayed (past estimate)",
        "stats_group_ontime": "On-time / early",
        "stats_mean": "Mean review",
        "stats_n": "Sample size",
        "stats_diff": "Mean difference (on-time − delayed)",
        "stats_metrics_caption": "Error bars show the 95% confidence interval.",
        "stats_result": "On-time orders average **{diff:.2f} points** higher than delayed ones "
        "(95% CI {lo:.2f}–{hi:.2f}). Welch t({df:,.0f}) = {t:,.1f}, p {p}. "
        "Effect size Cohen's d = {d:.2f}, a large difference.",
        "stats_caveat": "Reading: the p-value is near zero because the sample is large, so the "
        "effect size and interval matter more. The pattern is strong and consistent, but with "
        "observational data other factors (category, region) may be mixed in.",
        "stats_axis": "Average review score",
        "delay_title": "Review score by days late vs. estimate",
        "delay_y1": "Avg review score",
        "delay_y2": "Low-score rate (%)",
        "delay_legend_score": "Avg review score",
        "delay_legend_low": "Low-score rate (%)",
        "delay_text": "On-time and early orders average {on_time:.2f}. Ratings fall through the "
        "3-4 day bucket, and the share of low scores (2 or below) rises past {low:.0f}% once "
        "orders run a week or more late.",
        "delay_expander": "Query result",
        "geo_title": "Lead time by seller-customer location",
        "geo_axis": "Average lead time (days)",
        "geo_delay_rate": "delay rate {v:.2f}%",
        "geo_text": "Orders shipped within the customer's own state arrive in about half the "
        "time and miss the estimate less often.",
        "geo_expander": "Query result",
        "cat_title": "Lead time vs. review score by product category",
        "cat_desc": "Here a \"category\" is an Olist **product category** (e.g., bed_bath_table, "
        "office_furniture). Each dot is one category: x is average delivery lead time, y is "
        "average review score, and dot size is order count. The dashed lines are the overall "
        "averages, so categories toward the bottom-right (slow delivery + low ratings) are the "
        "weak ones.",
        "cat_slider": "Show categories with at least this many orders",
        "cat_slider_help": "Only categories with at least this many orders are shown, filtering "
        "out small-sample categories so the comparison is more stable.",
        "cat_shown": "{n} categories shown",
        "cat_x": "Average lead time (days)",
        "cat_y": "Average review score",
        "cat_hover_lead": "Lead time",
        "cat_hover_review": "Review",
        "cat_hover_orders": "Orders",
        "cat_weak": "Categories below the average review and above the average lead time:",
        "cat_col_name": "Category",
        "cat_col_orders": "Orders",
        "cat_col_lead": "Avg lead time",
        "cat_col_review": "Avg review",
        "ret_title": "Retention by first-order delivery experience",
        "ret_info": "Olist is close to a one-time-purchase marketplace: post-first-month "
        "retention stays under 1% for every cohort, and the delayed-first-order group is "
        "small. Read the gap below as directional, not conclusive.",
        "ret_x": "Months since first purchase",
        "ret_y": "Retention rate (%)",
        "insights_title": "What the data says",
        "insights_body": """
**Lateness matters more than raw speed.**
Average review falls from 4.28 on on-time orders to 2.58 once an order is 3-4 days past its
estimate, and below 2.0 beyond a week. The signal is "later than promised," not the absolute
number of days in transit.

**Distance sets the speed ceiling.**
Same-state orders arrive in about 7.5 days against 14.7 for cross-state. Seller mix by region
is therefore a structural lever on lead time, not just a logistics detail.

**Delivery risk is concentrated in a few bulky categories.**
office_furniture and similar categories combine the longest lead times with the lowest
reviews, so one marketplace-wide delivery estimate under-serves them.

**Repeat purchase is close to absent.**
Retention sits below 1% across cohorts, so the first order is effectively the whole
relationship. The same scarcity is why the delay-vs-retention comparison can only be read as
directional.
""",
        "insights_caption": "Pipeline: BigQuery marts to aggregated queries in `sql/analysis/` "
        "to this app.",
        "insight_goto": "See the evidence in the {tab} tab →",
        "insight_1_title": "Lateness drives satisfaction more than raw speed",
        "insight_1_body": "On-time and early orders average **{ontime:.2f}**, but a delay of just "
        "3-4 days past the estimate drops reviews to **{late:.2f}**. The signal is \"later than "
        "promised,\" not the absolute number of days in transit.",
        "insight_2_title": "Distance sets the ceiling on delivery speed",
        "insight_2_body": "Same-state orders arrive in about **{same:.1f} days** versus "
        "**{cross:.1f} days** across states, roughly double. Seller mix by region is a "
        "structural lever on lead time.",
        "insight_3_title": "Delivery risk concentrates in a few categories",
        "insight_3_body": "`{cat}` has the longest average lead time at **{lead:.1f} days** and a "
        "low average review of **{rev:.2f}**. One marketplace-wide delivery estimate under-serves "
        "categories like this.",
        "insight_4_title": "Repeat purchase is close to absent",
        "insight_4_body": "Post-first-month retention stays under 1% across cohorts, so the first "
        "order is effectively the whole relationship. The same scarcity is why the "
        "delay-vs-retention comparison can only be read as directional.",
        "nav_label": "Select view",
        "rows": "rows",
        "query_running": "Running query on BigQuery…",
        "query_done": "{n} rows returned from BigQuery",
        "view_sql": "View executed SQL",
        "lineage_via": "query",
        "c_bucket": "Delay bucket",
        "c_orders": "Orders",
        "c_avg_delay": "Avg delay (days)",
        "c_avg_review": "Avg review (0–5)",
        "c_low_rate": "Low-score rate",
        "c_match": "Region match",
        "c_avg_leadtime": "Avg lead time (days)",
        "c_delay_rate": "Delay rate",
        "c_stage": "Stage",
    },
}
