------ olist_mart 데이터셋에 테이블 만들기 
DROP table if exists `olist_mart.mart_order_operational_funnel`;
---- delievered 상태 데이터만 가져오고, customeer_unique_id를 포함하여 리텐션 분석이 가능하도록 설계

CREATE OR REPLACE TABLE `olist_mart.mart_order_operational_funnel` AS
SELECT 
    o.order_id,
    o.customer_id,
    c.customer_unique_id, -- 리텐션 분석용 핵심 키
    o.order_purchase_timestamp,
    o.order_delivered_customer_date,
    o.order_estimated_delivery_date,
    oi.product_id,
    oi.seller_id,
    oi.price,
    oi.freight_value
FROM `olist_raw.orders` o
-- 100% 매칭 확인된 핵심 조인
LEFT JOIN `olist_raw.order_items` oi ON o.order_id = oi.order_id
LEFT JOIN `olist_raw.customers` c ON o.customer_id = c.customer_id
WHERE o.order_status = 'delivered';
--------- 데이터 생존 확인 -> 


--------------------------
SELECT COUNT(*) AS total_rows 
FROM `olist_mart.mart_order_operational_funnel`;


---------------------------
SELECT 
    m.order_id,
    m.product_id,
    -- 추가될 정보들
    p.category_name_en, --
    r.review_score,
    -- 계산될 지표들
    DATE_DIFF(m.order_delivered_customer_date, m.order_purchase_timestamp, DAY) AS lead_time,
    DATE_DIFF(m.order_delivered_customer_date, m.order_estimated_delivery_date, DAY) AS delay
FROM `olist_mart.mart_order_operational_funnel` m
-- 1단계: 카테고리 정보 붙여보기
LEFT JOIN `olist_raw.view_products_english` p ON m.product_id = p.product_id
-- 2단계: 리뷰 정보 붙여보기 (중복 방지를 위한 서브쿼리)
LEFT JOIN (
    SELECT order_id, AVG(review_score) AS review_score
    FROM `olist_raw.order_reviews`
    GROUP BY order_id
) r ON m.order_id = r.order_id
LIMIT 10;




----------------------------


SELECT 
    COUNT(*) AS total_rows,
    COUNT(p.category_name_en) AS category_matched_cnt,
    COUNT(r.review_score) AS review_matched_cnt,
    -- 매칭 비율 계산
    ROUND(COUNT(p.category_name_en) / COUNT(*) * 100, 2) AS category_match_rate,
    ROUND(COUNT(r.review_score) / COUNT(*) * 100, 2) AS review_match_rate
FROM `olist_mart.mart_order_operational_funnel` m
LEFT JOIN `olist_raw.view_products_english` p ON m.product_id = p.product_id
LEFT JOIN (
    SELECT order_id, AVG(review_score) AS review_score
    FROM `olist_raw.order_reviews`
    GROUP BY order_id
) r ON m.order_id = r.order_id;








