#!/usr/bin/env python
# Drops and recreates staging_db and reporting_db in europe-west1
# to match the region of pagila_productionpublicpublic.
# Safe to run: both datasets are empty at this point.

from google.cloud import bigquery
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "D:/Projects/Capstone/credentials/sa-key.json"
PROJECT = "capstoneproject-493015"
TARGET_LOCATION = "europe-west1"
DATASETS = ["staging_db", "reporting_db"]

client = bigquery.Client(project=PROJECT)

for ds_id in DATASETS:
    ref = f"{PROJECT}.{ds_id}"
    try:
        existing = client.get_dataset(ref)
        print(f"Dropping {ds_id} (was in {existing.location})...")
        client.delete_dataset(ref, delete_contents=True, not_found_ok=True)
        print("  Dropped.")
    except Exception as e:
        print(f"  get/delete skipped: {e}")

    new_ds = bigquery.Dataset(ref)
    new_ds.location = TARGET_LOCATION
    created = client.create_dataset(new_ds, exists_ok=False)
    print(f"Created {ds_id} in {created.location}")

print("\nFinal state:")
for ds in client.list_datasets():
    full = client.get_dataset(ds.reference)
    print(f"  - {ds.dataset_id:35s} location={full.location}")
