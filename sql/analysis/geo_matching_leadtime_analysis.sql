-- Geo matching analysis:
-- Compare lead time/delay/review by seller-customer same-state vs cross-state.

WITH order_geo AS (
  SELECT
    moi.order_id,
    ANY_VALUE(moi.customer_state) AS customer_state,
    ANY_VALUE(moi.seller_state) AS seller_state
  FROM `olist_mart.mart_order_items` moi
  WHERE moi.customer_state IS NOT NULL
    AND moi.seller_state IS NOT NULL
  GROUP BY moi.order_id
),
order_delay AS (
  SELECT
    mo.order_id,
    DATE_DIFF(mo.order_delivered_customer_date, mo.order_purchase_timestamp, DAY) AS lead_time_days,
    DATE_DIFF(mo.order_delivered_customer_date, mo.order_estimated_delivery_date, DAY) AS delay_days,
    mo.avg_review_score
  FROM `olist_mart.mart_orders` mo
  WHERE mo.order_status = 'delivered'
    AND mo.order_purchase_timestamp IS NOT NULL
    AND mo.order_delivered_customer_date IS NOT NULL
    AND mo.order_estimated_delivery_date IS NOT NULL
)
SELECT
  CASE
    WHEN g.customer_state = g.seller_state THEN 'Same State'
    ELSE 'Cross State'
  END AS state_match_type,
  COUNT(*) AS order_count,
  ROUND(AVG(d.lead_time_days), 2) AS avg_lead_time_days,
  ROUND(AVG(d.delay_days), 2) AS avg_delay_days,
  ROUND(AVG(d.avg_review_score), 2) AS avg_review_score,
  ROUND(SUM(CASE WHEN d.delay_days > 0 THEN 1 ELSE 0 END) / COUNT(*) * 100, 2) AS delay_rate_pct
FROM order_geo g
JOIN order_delay d
  ON g.order_id = d.order_id
GROUP BY state_match_type
ORDER BY order_count DESC;
