#!/usr/bin/env python
# Exports the two reporting tables to CSV files for use in Tableau Public.
# Tableau Public Desktop cannot connect directly to BigQuery (no BQ connector
# in the free version on Windows), so CSVs are the easiest path.
#
# Output: D:/Projects/Capstone/exports/
#   - rep_revenue_per_period.csv
#   - rep_revenue_per_customer_and_period.csv

from google.cloud import bigquery
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
default_credentials_path = REPO_ROOT / "credentials" / "sa-key.json"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", str(default_credentials_path))

PROJECT = "capstoneproject-493015"
DATASET = "reporting_db"
OUT_DIR = REPO_ROOT / "exports"
TABLES = ["rep_revenue_per_period", "rep_revenue_per_customer_and_period"]

OUT_DIR.mkdir(parents=True, exist_ok=True)
client = bigquery.Client(project=PROJECT, location="europe-west1")

for table in TABLES:
    print(f"Exporting {table}...")
    df = client.query(f"SELECT * FROM `{PROJECT}.{DATASET}.{table}`").to_dataframe()
    out_path = OUT_DIR / f"{table}.csv"
    df.to_csv(out_path, index=False)
    print(f"  -> {out_path}  ({len(df):,} rows)")

print("\nDone. Open these CSVs in Tableau Public Desktop:")
for t in TABLES:
    print(f"  {OUT_DIR}/{t}.csv")
