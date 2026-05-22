-- Order-grain mart: one row per order_id
CREATE OR REPLACE TABLE `olist_mart.mart_orders` AS
WITH payment_agg AS (
  SELECT
    op.order_id,
    SUM(op.payment_value) AS total_payment_value,
    SUM(op.payment_installments) AS total_payment_installments,
    COUNT(*) AS payment_txn_count
  FROM `olist_raw.order_payments` op
  GROUP BY op.order_id
),
review_agg AS (
  SELECT
    r.order_id,
    AVG(r.review_score) AS avg_review_score,
    COUNT(*) AS review_count
  FROM `olist_raw.order_reviews` r
  GROUP BY r.order_id
)
SELECT
  o.order_id,
  o.customer_id,
  c.customer_unique_id,
  c.customer_zip_code_prefix,
  c.customer_city,
  c.customer_state,
  o.order_status,
  o.order_purchase_timestamp,
  o.order_approved_at,
  o.order_delivered_carrier_date,
  o.order_delivered_customer_date,
  o.order_estimated_delivery_date,
  p.total_payment_value,
  p.total_payment_installments,
  p.payment_txn_count,
  r.avg_review_score,
  r.review_count
FROM `olist_raw.orders` o
LEFT JOIN `olist_raw.customers` c
  ON o.customer_id = c.customer_id
LEFT JOIN payment_agg p
  ON o.order_id = p.order_id
LEFT JOIN review_agg r
  ON o.order_id = r.order_id;
