-- Group summary stats for comparing review scores between delayed and on-time
-- deliveries. Welch's t-test and effect size are computed from these summaries
-- in the dashboard. This is an observational comparison, not a randomized test.
SELECT
  CASE WHEN delay_days > 0 THEN 'delayed' ELSE 'on_time' END AS grp,
  COUNT(*) AS n,
  ROUND(AVG(avg_review_score), 4) AS mean_score,
  ROUND(STDDEV_SAMP(avg_review_score), 4) AS sd_score
FROM `olist_mart.mart_delivery_features`
WHERE delay_days IS NOT NULL
  AND avg_review_score IS NOT NULL
GROUP BY grp
ORDER BY grp;
