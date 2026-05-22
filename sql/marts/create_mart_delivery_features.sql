-- Delivery feature mart for ML: one row per delivered order
CREATE OR REPLACE TABLE `olist_mart.mart_delivery_features` AS
WITH item_agg AS (
  SELECT
    oi.order_id,
    COUNT(*) AS item_count,
    COUNT(DISTINCT oi.seller_id) AS seller_count,
    COUNT(DISTINCT oi.product_id) AS product_count,
    SUM(oi.price) AS total_item_price,
    SUM(oi.freight_value) AS total_freight_value,
    AVG(vp.product_weight_g) AS avg_product_weight_g,
    AVG(vp.product_length_cm * vp.product_height_cm * vp.product_width_cm) AS avg_product_volume_cm3
  FROM `olist_raw.order_items` oi
  LEFT JOIN `olist_raw.view_products_english` vp
    ON oi.product_id = vp.product_id
  GROUP BY oi.order_id
),
payment_agg AS (
  SELECT
    op.order_id,
    SUM(op.payment_value) AS total_payment_value,
    COUNT(*) AS payment_txn_count,
    SUM(CASE WHEN op.payment_type = 'credit_card' THEN 1 ELSE 0 END) AS credit_card_txn_count
  FROM `olist_raw.order_payments` op
  GROUP BY op.order_id
),
review_agg AS (
  SELECT
    r.order_id,
    AVG(r.review_score) AS avg_review_score
  FROM `olist_raw.order_reviews` r
  GROUP BY r.order_id
)
SELECT
  o.order_id,
  o.customer_id,
  c.customer_unique_id,
  c.customer_state,
  EXTRACT(YEAR FROM o.order_purchase_timestamp) AS purchase_year,
  EXTRACT(MONTH FROM o.order_purchase_timestamp) AS purchase_month,
  EXTRACT(DAYOFWEEK FROM o.order_purchase_timestamp) AS purchase_day_of_week,
  EXTRACT(HOUR FROM o.order_purchase_timestamp) AS purchase_hour,
  TIMESTAMP_DIFF(o.order_approved_at, o.order_purchase_timestamp, HOUR) AS approval_hours,
  TIMESTAMP_DIFF(o.order_delivered_carrier_date, o.order_approved_at, HOUR) AS seller_prep_hours,
  TIMESTAMP_DIFF(o.order_delivered_customer_date, o.order_delivered_carrier_date, HOUR) AS carrier_delivery_hours,
  TIMESTAMP_DIFF(o.order_delivered_customer_date, o.order_purchase_timestamp, HOUR) AS total_lead_hours,
  DATE_DIFF(o.order_delivered_customer_date, o.order_estimated_delivery_date, DAY) AS delay_days,
  CASE
    WHEN DATE_DIFF(o.order_delivered_customer_date, o.order_estimated_delivery_date, DAY) > 0 THEN 1
    ELSE 0
  END AS is_delayed,
  i.item_count,
  i.seller_count,
  i.product_count,
  i.total_item_price,
  i.total_freight_value,
  i.avg_product_weight_g,
  i.avg_product_volume_cm3,
  p.total_payment_value,
  p.payment_txn_count,
  p.credit_card_txn_count,
  r.avg_review_score
FROM `olist_raw.orders` o
LEFT JOIN `olist_raw.customers` c
  ON o.customer_id = c.customer_id
LEFT JOIN item_agg i
  ON o.order_id = i.order_id
LEFT JOIN payment_agg p
  ON o.order_id = p.order_id
LEFT JOIN review_agg r
  ON o.order_id = r.order_id
WHERE o.order_status = 'delivered'
  AND o.order_purchase_timestamp IS NOT NULL
  AND o.order_approved_at IS NOT NULL
  AND o.order_delivered_carrier_date IS NOT NULL
  AND o.order_delivered_customer_date IS NOT NULL
  AND o.order_estimated_delivery_date IS NOT NULL;
