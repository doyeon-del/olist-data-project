-- Category-level delivery performance and review score analysis
SELECT
  p.category_name_en,
  COUNT(DISTINCT m.order_id) AS total_orders,
  ROUND(AVG(DATE_DIFF(m.order_delivered_customer_date, m.order_purchase_timestamp, DAY)), 2) AS avg_lead_time,
  ROUND(AVG(DATE_DIFF(m.order_delivered_customer_date, m.order_estimated_delivery_date, DAY)), 2) AS avg_delay,
  ROUND(AVG(r.review_score), 2) AS avg_review_score
FROM `olist_mart.mart_order_operational_funnel` m
LEFT JOIN `olist_raw.view_products_english` p
  ON m.product_id = p.product_id
LEFT JOIN (
  SELECT
    order_id,
    AVG(review_score) AS review_score
  FROM `olist_raw.order_reviews`
  GROUP BY order_id
) r
  ON m.order_id = r.order_id
GROUP BY p.category_name_en
HAVING total_orders > 100
ORDER BY avg_lead_time DESC;
