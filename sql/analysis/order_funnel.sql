-- Operational order funnel: how many orders reach each fulfillment stage.
-- All placed orders (not just delivered), so drop-off is visible.
SELECT
  COUNT(*) AS purchased,
  COUNTIF(order_approved_at IS NOT NULL) AS approved,
  COUNTIF(order_delivered_carrier_date IS NOT NULL) AS shipped,
  COUNTIF(order_delivered_customer_date IS NOT NULL) AS delivered
FROM `olist_mart.mart_orders`
WHERE order_purchase_timestamp IS NOT NULL;
