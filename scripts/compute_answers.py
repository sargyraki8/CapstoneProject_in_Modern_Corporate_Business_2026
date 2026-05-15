#!/usr/bin/env python
# Runs the 4 analytical queries from answers.txt and prints the results
# so we can fill in the final answers.

from google.cloud import bigquery
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
default_credentials_path = REPO_ROOT / "credentials" / "sa-key.json"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", str(default_credentials_path))
PROJECT = "capstoneproject-493015"
client = bigquery.Client(project=PROJECT, location="europe-west1")

print("=" * 70)
print("Q1: % diff between May 2022 and June 2022 revenue")
print("=" * 70)
q1 = f"""
SELECT
  MAX(CASE WHEN reporting_date = '2022-05-01' THEN total_revenue END) AS may_revenue,
  MAX(CASE WHEN reporting_date = '2022-06-01' THEN total_revenue END) AS june_revenue,
  ROUND(
    (MAX(CASE WHEN reporting_date = '2022-06-01' THEN total_revenue END) -
     MAX(CASE WHEN reporting_date = '2022-05-01' THEN total_revenue END)) /
    MAX(CASE WHEN reporting_date = '2022-05-01' THEN total_revenue END) * 100
  , 2) AS pct_diff
FROM `{PROJECT}.reporting_db.rep_revenue_per_period`
WHERE reporting_period = 'Month'
  AND reporting_date IN ('2022-05-01', '2022-06-01');
"""
for row in client.query(q1).result():
    print(f"  May 2022: ${row.may_revenue}")
    print(f"  Jun 2022: ${row.june_revenue}")
    print(f"  pct_diff: {row.pct_diff}%")

print("\n" + "=" * 70)
print("Q2: Weekday with highest average revenue")
print("=" * 70)
q2 = f"""
SELECT
  FORMAT_DATE('%A', reporting_date) AS weekday_name,
  EXTRACT(DAYOFWEEK FROM reporting_date) AS weekday_num,
  ROUND(AVG(total_revenue), 2) AS avg_revenue
FROM `{PROJECT}.reporting_db.rep_revenue_per_period`
WHERE reporting_period = 'Day'
  AND total_revenue > 0
GROUP BY 1, 2
ORDER BY avg_revenue DESC;
"""
for row in client.query(q2).result():
    print(f"  {row.weekday_name:10s}  avg=${row.avg_revenue}")

print("\n" + "=" * 70)
print("Q3: Top 5 customers by revenue for June 2022")
print("=" * 70)
q3 = f"""
SELECT customer_id, total_revenue
FROM `{PROJECT}.reporting_db.rep_revenue_per_customer_and_period`
WHERE reporting_period = 'Month'
  AND reporting_date = '2022-06-01'
ORDER BY total_revenue DESC
LIMIT 5;
"""
for i, row in enumerate(client.query(q3).result(), 1):
    print(f"  {i}. customer_id={row.customer_id}  revenue=${row.total_revenue}")

print("\n" + "=" * 70)
print("Q4: Month with the most unique customers")
print("=" * 70)
q4 = f"""
SELECT
  reporting_date,
  COUNT(DISTINCT customer_id) AS unique_customers
FROM `{PROJECT}.reporting_db.rep_revenue_per_customer_and_period`
WHERE reporting_period = 'Month'
  AND total_revenue > 0
GROUP BY reporting_date
ORDER BY unique_customers DESC
LIMIT 5;
"""
for row in client.query(q4).result():
    print(f"  {row.reporting_date}  unique_customers={row.unique_customers}")
