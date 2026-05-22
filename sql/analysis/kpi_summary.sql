-- KPI summary for dashboard headline cards.
-- Delivered orders only, mirroring the filters used in the other analyses.
SELECT
  COUNT(*) AS total_orders,
  ROUND(AVG(DATE_DIFF(order_delivered_customer_date, order_purchase_timestamp, DAY)), 2) AS avg_lead_time_days,
  ROUND(AVG(avg_review_score), 2) AS avg_review_score,
  ROUND(
    SUM(CASE WHEN DATE_DIFF(order_delivered_customer_date, order_estimated_delivery_date, DAY) > 0 THEN 1 ELSE 0 END)
      / COUNT(*) * 100,
    2
  ) AS delay_rate_pct
FROM `olist_mart.mart_orders`
WHERE order_status = 'delivered'
  AND order_purchase_timestamp IS NOT NULL
  AND order_delivered_customer_date IS NOT NULL
  AND order_estimated_delivery_date IS NOT NULL;
