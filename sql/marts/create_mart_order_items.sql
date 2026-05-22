-- Order-item-grain mart: one row per order_id + order_item_id
CREATE OR REPLACE TABLE `olist_mart.mart_order_items` AS
SELECT
  oi.order_id,
  oi.order_item_id,
  oi.product_id,
  vp.category_name_en,
  oi.seller_id,
  s.seller_zip_code_prefix,
  s.seller_city,
  s.seller_state,
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
  oi.shipping_limit_date,
  oi.price,
  oi.freight_value,
  vp.product_weight_g,
  vp.product_length_cm,
  vp.product_height_cm,
  vp.product_width_cm
FROM `olist_raw.order_items` oi
JOIN `olist_raw.orders` o
  ON oi.order_id = o.order_id
LEFT JOIN `olist_raw.customers` c
  ON o.customer_id = c.customer_id
LEFT JOIN `olist_raw.sellers` s
  ON oi.seller_id = s.seller_id
LEFT JOIN `olist_raw.view_products_english` vp
  ON oi.product_id = vp.product_id;
