-- Cohort retention by first-order delay experience:
-- Compare retention between customers whose first delivered order was delayed vs on-time.

WITH first_delivered_order AS (
  SELECT
    mo.customer_unique_id,
    mo.order_id,
    DATE(mo.order_purchase_timestamp) AS purchase_date,
    DATE_TRUNC(DATE(mo.order_purchase_timestamp), MONTH) AS cohort_month,
    DATE_DIFF(mo.order_delivered_customer_date, mo.order_estimated_delivery_date, DAY) AS delay_days,
    CASE
      WHEN DATE_DIFF(mo.order_delivered_customer_date, mo.order_estimated_delivery_date, DAY) > 0
        THEN 'Delayed First Order'
      ELSE 'On-time/Early First Order'
    END AS first_order_delay_group,
    ROW_NUMBER() OVER (
      PARTITION BY mo.customer_unique_id
      ORDER BY mo.order_purchase_timestamp
    ) AS rn
  FROM `olist_mart.mart_orders` mo
  WHERE mo.order_status = 'delivered'
    AND mo.customer_unique_id IS NOT NULL
    AND mo.order_purchase_timestamp IS NOT NULL
    AND mo.order_delivered_customer_date IS NOT NULL
    AND mo.order_estimated_delivery_date IS NOT NULL
),
first_order_group AS (
  SELECT
    customer_unique_id,
    cohort_month,
    first_order_delay_group
  FROM first_delivered_order
  WHERE rn = 1
),
activity AS (
  SELECT
    mo.customer_unique_id,
    DATE_TRUNC(DATE(mo.order_purchase_timestamp), MONTH) AS activity_month
  FROM `olist_mart.mart_orders` mo
  WHERE mo.order_status = 'delivered'
    AND mo.customer_unique_id IS NOT NULL
    AND mo.order_purchase_timestamp IS NOT NULL
),
joined AS (
  SELECT
    fog.cohort_month,
    fog.first_order_delay_group,
    a.activity_month,
    DATE_DIFF(a.activity_month, fog.cohort_month, MONTH) AS cohort_index,
    fog.customer_unique_id
  FROM first_order_group fog
  JOIN activity a
    ON fog.customer_unique_id = a.customer_unique_id
),
cohort_size AS (
  SELECT
    cohort_month,
    first_order_delay_group,
    COUNT(DISTINCT customer_unique_id) AS cohort_size
  FROM first_order_group
  GROUP BY cohort_month, first_order_delay_group
)
SELECT
  j.cohort_month,
  j.first_order_delay_group,
  j.activity_month,
  j.cohort_index,
  cs.cohort_size,
  COUNT(DISTINCT j.customer_unique_id) AS retained_customers,
  ROUND(
    SAFE_DIVIDE(COUNT(DISTINCT j.customer_unique_id), cs.cohort_size),
    4
  ) AS retention_rate
FROM joined j
JOIN cohort_size cs
  ON j.cohort_month = cs.cohort_month
 AND j.first_order_delay_group = cs.first_order_delay_group
GROUP BY
  j.cohort_month,
  j.first_order_delay_group,
  j.activity_month,
  j.cohort_index,
  cs.cohort_size
ORDER BY
  j.cohort_month,
  j.first_order_delay_group,
  j.cohort_index;
