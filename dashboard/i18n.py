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
        "가장 큰 누수는 택배사→고객 구간({deliver:.1f}%)으로, "
        "승인→택배사 구간({ship:.1f}%)보다 큽니다.",
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
        "cat_title": "카테고리별 리드타임 vs 리뷰 점수",
        "cat_slider": "카테고리 최소 주문 수",
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
        "funnel_text": "Of {placed:,} placed orders, {pct:.1f}% reach the customer. The largest "
        "leak is the carrier-to-customer leg ({deliver:.1f}% of orders), ahead of "
        "approval-to-carrier ({ship:.1f}%).",
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
        "cat_title": "Lead time vs. review score by category",
        "cat_slider": "Minimum orders per category",
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
    },
}
