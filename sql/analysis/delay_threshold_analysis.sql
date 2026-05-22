-- Delay threshold analysis:
-- Identify where review score drops as delay days increase.

WITH base AS (
  SELECT
    m.order_id,
    m.delay_days,
    m.avg_review_score
  FROM `olist_mart.mart_delivery_features` m
  WHERE m.delay_days IS NOT NULL
    AND m.avg_review_score IS NOT NULL
),
bucketed AS (
  SELECT
    CASE
      WHEN delay_days <= 0 THEN 'D<=0 (On-time/Early)'
      WHEN delay_days BETWEEN 1 AND 2 THEN 'D+1~2'
      WHEN delay_days BETWEEN 3 AND 4 THEN 'D+3~4'
      WHEN delay_days BETWEEN 5 AND 7 THEN 'D+5~7'
      WHEN delay_days BETWEEN 8 AND 14 THEN 'D+8~14'
      ELSE 'D+15+'
    END AS delay_bucket,
    delay_days,
    avg_review_score
  FROM base
)
SELECT
  delay_bucket,
  COUNT(*) AS order_count,
  ROUND(AVG(delay_days), 2) AS avg_delay_days,
  ROUND(AVG(avg_review_score), 2) AS avg_review_score,
  ROUND(SUM(CASE WHEN avg_review_score <= 2 THEN 1 ELSE 0 END) / COUNT(*) * 100, 2) AS low_score_rate_pct
FROM bucketed
GROUP BY delay_bucket
ORDER BY
  CASE delay_bucket
    WHEN 'D<=0 (On-time/Early)' THEN 1
    WHEN 'D+1~2' THEN 2
    WHEN 'D+3~4' THEN 3
    WHEN 'D+5~7' THEN 4
    WHEN 'D+8~14' THEN 5
    ELSE 6
  END;
