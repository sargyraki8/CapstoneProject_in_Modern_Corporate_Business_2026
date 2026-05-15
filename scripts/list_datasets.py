#!/usr/bin/env python
# Lists ALL BigQuery datasets in the project across every region.
from google.cloud import bigquery
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "D:/Projects/Capstone/credentials/sa-key.json"
client = bigquery.Client(project="capstoneproject-493015")

print("All datasets in project capstoneproject-493015:")
datasets = list(client.list_datasets())
if not datasets:
    print("  (none)")
for ds in datasets:
    full = client.get_dataset(ds.reference)
    print(f"  - {ds.dataset_id:35s} location={full.location}")

# Specifically look for pagila_productionpublicpublic in likely regions
print("\nTable search for pagila_productionpublicpublic in common regions:")
for ds in datasets:
    if "pagila" in ds.dataset_id.lower():
        full = client.get_dataset(ds.reference)
        print(f"  Found {ds.dataset_id} in {full.location}")
        tables = list(client.list_tables(ds.reference))
        print(f"  Tables ({len(tables)}):")
        for t in tables:
            print(f"    - {t.table_id}")
