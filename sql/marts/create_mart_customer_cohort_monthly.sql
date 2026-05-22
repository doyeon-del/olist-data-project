-- Customer cohort retention mart (monthly)
CREATE OR REPLACE TABLE `olist_mart.mart_customer_cohort_monthly` AS
WITH order_base AS (
  SELECT
    c.customer_unique_id,
    DATE_TRUNC(DATE(o.order_purchase_timestamp), MONTH) AS order_month
  FROM `olist_raw.orders` o
  JOIN `olist_raw.customers` c
    ON o.customer_id = c.customer_id
  WHERE o.order_status = 'delivered'
    AND o.order_purchase_timestamp IS NOT NULL
),
first_purchase AS (
  SELECT
    customer_unique_id,
    MIN(order_month) AS cohort_month
  FROM order_base
  GROUP BY customer_unique_id
),
cohort_activity AS (
  SELECT
    fp.cohort_month,
    ob.order_month AS activity_month,
    DATE_DIFF(ob.order_month, fp.cohort_month, MONTH) AS cohort_index,
    ob.customer_unique_id
  FROM order_base ob
  JOIN first_purchase fp
    ON ob.customer_unique_id = fp.customer_unique_id
),
cohort_size AS (
  SELECT
    cohort_month,
    COUNT(DISTINCT customer_unique_id) AS cohort_size
  FROM first_purchase
  GROUP BY cohort_month
)
SELECT
  ca.cohort_month,
  ca.activity_month,
  ca.cohort_index,
  cs.cohort_size,
  COUNT(DISTINCT ca.customer_unique_id) AS retained_customers,
  ROUND(
    SAFE_DIVIDE(COUNT(DISTINCT ca.customer_unique_id), cs.cohort_size),
    4
  ) AS retention_rate
FROM cohort_activity ca
JOIN cohort_size cs
  ON ca.cohort_month = cs.cohort_month
GROUP BY
  ca.cohort_month,
  ca.activity_month,
  ca.cohort_index,
  cs.cohort_size;
