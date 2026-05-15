#!/usr/bin/env python
# coding: utf-8

# This script creates the helper date tables needed for reporting:
# 1. all_dates - all dates from 2015-01-01 to 2024-12-31
# 2. reporting_periods_table - Day/Week/Month/Quarter/Year period truncations

from google.cloud import bigquery
import os

print('Libraries imported successfully')

# -- YOUR CODE GOES BELOW THIS LINE
credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "D:/Projects/Capstone/credentials/sa-key.json")  # Edit path or set GOOGLE_APPLICATION_CREDENTIALS
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
# -- YOUR CODE GOES ABOVE THIS LINE

# -- YOUR CODE GOES BELOW THIS LINE
project_id = 'capstoneproject-493015'  # Edit with your project id
# -- YOUR CODE GOES ABOVE THIS LINE

client = bigquery.Client(project=project_id)

# ============================================================
# Step 1: Drop all_dates if it already exists
# ============================================================
sql_drop_all_dates = f"""
DROP TABLE IF EXISTS `{project_id}.reporting_db.all_dates`
"""
client.query(sql_drop_all_dates).result()
print("Step 1: Dropped all_dates table (if existed)")

# ============================================================
# Step 2: Create all_dates table
# ============================================================
sql_create_all_dates = f"""
CREATE TABLE IF NOT EXISTS `{project_id}.reporting_db.all_dates` (
  date_column DATE
)
"""
client.query(sql_create_all_dates).result()
print("Step 2: Created all_dates table")

# ============================================================
# Step 3: Insert rows into all_dates (2015-01-01 to 2024-12-31)
# ============================================================
sql_insert_all_dates = f"""
INSERT INTO `{project_id}.reporting_db.all_dates` (date_column)
SELECT
  DATE_ADD('2015-01-01', INTERVAL n DAY) AS date_column
FROM
  UNNEST(GENERATE_ARRAY(0, DATE_DIFF('2024-12-31', '2015-01-01', DAY))) AS n
"""
client.query(sql_insert_all_dates).result()
print("Step 3: Inserted dates into all_dates (2015-01-01 to 2024-12-31)")

# ============================================================
# Step 4: Create reporting_periods_table
# ============================================================
sql_create_rpt = f"""
CREATE TABLE IF NOT EXISTS `{project_id}.reporting_db.reporting_periods_table` (
  reporting_period STRING,
  reporting_date DATE
)
"""
client.query(sql_create_rpt).result()
print("Step 4: Created reporting_periods_table")

# ============================================================
# Step 5: Clear existing rows (safe for re-runs)
# ============================================================
sql_delete_rpt = f"""
DELETE FROM `{project_id}.reporting_db.reporting_periods_table` WHERE TRUE
"""
client.query(sql_delete_rpt).result()
print("Step 5: Cleared existing rows from reporting_periods_table")

# ============================================================
# Step 6: Insert reporting periods (Day/Week/Month/Quarter/Year)
# ============================================================
sql_insert_rpt = f"""
INSERT INTO `{project_id}.reporting_db.reporting_periods_table` (reporting_period, reporting_date)
WITH processed_dates AS (
  SELECT
    'Day' AS reporting_period,
    DATE_TRUNC(date_column, DAY) AS reporting_date
  FROM `{project_id}.reporting_db.all_dates`
  GROUP BY 1, 2

  UNION ALL

  SELECT
    'Week' AS reporting_period,
    DATE_TRUNC(date_column, WEEK) AS reporting_date
  FROM `{project_id}.reporting_db.all_dates`
  GROUP BY 1, 2

  UNION ALL

  SELECT
    'Month' AS reporting_period,
    DATE_TRUNC(date_column, MONTH) AS reporting_date
  FROM `{project_id}.reporting_db.all_dates`
  GROUP BY 1, 2

  UNION ALL

  SELECT
    'Quarter' AS reporting_period,
    DATE_TRUNC(date_column, QUARTER) AS reporting_date
  FROM `{project_id}.reporting_db.all_dates`
  GROUP BY 1, 2

  UNION ALL

  SELECT
    'Year' AS reporting_period,
    DATE_TRUNC(date_column, YEAR) AS reporting_date
  FROM `{project_id}.reporting_db.all_dates`
  GROUP BY 1, 2
)
SELECT *
FROM processed_dates
WHERE reporting_date <= CURRENT_DATE()
"""
client.query(sql_insert_rpt).result()
print("Step 6: Inserted reporting periods into reporting_periods_table")

print("\n=== All helper tables created successfully! ===")
