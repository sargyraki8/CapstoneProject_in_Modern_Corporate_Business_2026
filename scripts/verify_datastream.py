#!/usr/bin/env python
# coding: utf-8

# Quick verification script - checks if all 15 Pagila tables
# exist in BigQuery and have rows (confirms Datastream worked).
# This file is NOT part of the submission - just a helper.

from google.cloud import bigquery
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "D:/Projects/Capstone/credentials/sa-key.json"
project_id = 'capstoneproject-493015'
client = bigquery.Client(project=project_id, location="europe-west1")

EXPECTED_TABLES = [
    'actor', 'address', 'category', 'city', 'country',
    'customer', 'film', 'film_actor', 'film_category',
    'inventory', 'language', 'payment', 'rental', 'staff', 'store'
]

print("=" * 60)
print("DATASTREAM VERIFICATION - Checking pagila_productionpublicpublic")
print("=" * 60)

all_ok = True
for table in EXPECTED_TABLES:
    full_table = f"{project_id}.pagila_productionpublicpublic.{table}"
    try:
        query = f"SELECT COUNT(*) as cnt FROM `{full_table}`"
        result = client.query(query).to_dataframe()
        count = result['cnt'].iloc[0]
        status = "OK" if count > 0 else "EMPTY"
        if count == 0:
            all_ok = False
        print(f"  {status:6s} | {table:20s} | {count:,} rows")
    except Exception as e:
        all_ok = False
        print(f"  FAIL   | {table:20s} | Error: {e}")

print("=" * 60)
if all_ok:
    print("SUCCESS: All 15 tables exist and have data!")
    print("Datastream replication is complete. You can run staging scripts.")
else:
    print("WARNING: Some tables are missing or empty.")
    print("Check your Datastream configuration in GCP Console.")
print("=" * 60)
