----- 1. 카테고리별 배송 성과 및 만족도 분석 ------------
--- 어떤 상품군에서 배송이 늦는지, 그것이 평점에 어떤 영향을 주는지? 
SELECT 
    p.category_name_en,
    COUNT(DISTINCT m.order_id) AS total_orders,
    -- 평균 배송 소요 시간 (Lead Time)
    ROUND(AVG(DATE_DIFF(m.order_delivered_customer_date, m.order_purchase_timestamp, DAY)), 2) AS avg_lead_time,
    -- 평균 지연 시간 (예상 대비)
    ROUND(AVG(DATE_DIFF(m.order_delivered_customer_date, m.order_estimated_delivery_date, DAY)), 2) AS avg_delay,
    -- 평균 만족도
    ROUND(AVG(r.review_score), 2) AS avg_review_score
FROM `olist_mart.mart_order_operational_funnel` m
LEFT JOIN `olist_raw.view_products_english` p ON m.product_id = p.product_id
LEFT JOIN (
    SELECT order_id, AVG(review_score) AS review_score
    FROM `olist_raw.order_reviews`
    GROUP BY order_id
) r ON m.order_id = r.order_id
GROUP BY 1
HAVING total_orders > 100 -- 통계적 유의미함을 위해 주문 건수가 많은 카테고리만 필터링
ORDER BY avg_lead_time DESC;


-------- 2. 배송 지연이 리뷰 점수에 미치는 영향 -----------
--- 배송 만족도 상관관계 검증 ---> 지연 일수별로 평점이 어떻게 변하는가? 
SELECT 
    CASE 
        WHEN DATE_DIFF(m.order_delivered_customer_date, m.order_estimated_delivery_date, DAY) <= 0 THEN 'On-time/Early'
        WHEN DATE_DIFF(m.order_delivered_customer_date, m.order_estimated_delivery_date, DAY) <= 3 THEN '1-3 Days Delay'
        WHEN DATE_DIFF(m.order_delivered_customer_date, m.order_estimated_delivery_date, DAY) <= 7 THEN '4-7 Days Delay'
        ELSE 'Over a Week Delay'
    END AS delay_segment,
    COUNT(*) AS order_count,
    ROUND(AVG(r.review_score), 2) AS avg_review_score
FROM `olist_mart.mart_order_operational_funnel` m
JOIN ( -- 상관관계 분석을 위해 리뷰가 있는 데이터만 결합
    SELECT order_id, AVG(review_score) AS review_score
    FROM `olist_raw.order_reviews`
    GROUP BY order_id
) r ON m.order_id = r.order_id
GROUP BY 1
ORDER BY avg_review_score DESC;
