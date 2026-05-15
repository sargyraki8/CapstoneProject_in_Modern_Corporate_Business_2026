-- =====================================================================
-- METABASE QUERY PACK — Capstone Project
-- =====================================================================
-- Paste each block into a new Metabase "Native Query" (SQL editor),
-- select the BigQuery database, then pick the visualization type noted
-- above each query. Save each as a Question. Screenshots of these
-- 4 Questions are what the rubric wants (no dashboard needed).
--
-- Source: reporting_db.rep_revenue_per_period
--         reporting_db.rep_revenue_per_customer_and_period
-- =====================================================================


-- ---------------------------------------------------------------------
-- Q1 — LINE CHART
-- Title: "Revenue per Date"
-- Visualization: Line
-- X-axis: reporting_date     Y-axis: total_revenue
-- Use the Metabase field filter {{period}} if you want an interactive
-- period selector. Otherwise change 'Month' manually to Day / Year.
-- ---------------------------------------------------------------------
SELECT
  reporting_date,
  total_revenue
FROM `capstoneproject-493015.reporting_db.rep_revenue_per_period`
WHERE reporting_period = 'Month'
ORDER BY reporting_date;

-- Sanity check for Q1 answer (paste as extra Question if you want):
-- June 2022 vs May 2022 revenue % diff
SELECT
  MAX(CASE WHEN reporting_date = DATE '2022-05-01' THEN total_revenue END) AS may_2022,
  MAX(CASE WHEN reporting_date = DATE '2022-06-01' THEN total_revenue END) AS jun_2022,
  ROUND(
    (MAX(CASE WHEN reporting_date = DATE '2022-06-01' THEN total_revenue END)
     - MAX(CASE WHEN reporting_date = DATE '2022-05-01' THEN total_revenue END))
    / MAX(CASE WHEN reporting_date = DATE '2022-05-01' THEN total_revenue END) * 100
  , 2) AS pct_diff
FROM `capstoneproject-493015.reporting_db.rep_revenue_per_period`
WHERE reporting_period = 'Month'
  AND reporting_date IN (DATE '2022-05-01', DATE '2022-06-01');


-- ---------------------------------------------------------------------
-- Q2 — BAR CHART
-- Title: "Average Daily Revenue per Weekday"
-- Visualization: Bar
-- X-axis: weekday_name   Y-axis: avg_revenue
-- Expected winner: Sunday (≈ $1,961.94)
-- ---------------------------------------------------------------------
SELECT
  FORMAT_DATE('%A', reporting_date) AS weekday_name,
  EXTRACT(DAYOFWEEK FROM reporting_date) AS weekday_num,
  ROUND(AVG(total_revenue), 2) AS avg_revenue
FROM `capstoneproject-493015.reporting_db.rep_revenue_per_period`
WHERE reporting_period = 'Day'
  AND total_revenue > 0
GROUP BY weekday_name, weekday_num
ORDER BY weekday_num;
-- In Metabase, set the chart to sort by weekday_num for Mon→Sun order,
-- or order by avg_revenue DESC to make the winner visually obvious.


-- ---------------------------------------------------------------------
-- Q3 — TABLE
-- Title: "Top 5 Customers by Revenue (June 2022)"
-- Visualization: Table
-- Expected top 5:
--   454 ($52.90), 178 ($44.92), 176 ($42.92), 26 ($41.93), 526 ($41.91)
-- ---------------------------------------------------------------------
SELECT
  customer_id,
  ROUND(total_revenue, 2) AS total_revenue
FROM `capstoneproject-493015.reporting_db.rep_revenue_per_customer_and_period`
WHERE reporting_period = 'Month'
  AND reporting_date = DATE '2022-06-01'
ORDER BY total_revenue DESC
LIMIT 5;


-- ---------------------------------------------------------------------
-- Q4 — BAR CHART
-- Title: "Unique Paying Customers per Month"
-- Visualization: Bar
-- X-axis: reporting_date (month)   Y-axis: unique_customers
-- Expected winner: July 2022 & August 2022 tied at 599
-- ---------------------------------------------------------------------
SELECT
  reporting_date,
  COUNT(DISTINCT customer_id) AS unique_customers
FROM `capstoneproject-493015.reporting_db.rep_revenue_per_customer_and_period`
WHERE reporting_period = 'Month'
  AND total_revenue > 0
GROUP BY reporting_date
ORDER BY reporting_date;
