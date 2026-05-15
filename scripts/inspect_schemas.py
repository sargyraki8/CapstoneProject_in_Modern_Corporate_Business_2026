#!/usr/bin/env python
from google.cloud import bigquery
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "D:/Projects/Capstone/credentials/sa-key.json"
client = bigquery.Client(project="capstoneproject-493015", location="europe-west1")
for t in ["film", "payment"]:
    tbl = client.get_table(f"capstoneproject-493015.pagila_productionpublicpublic.{t}")
    print(f"\n=== {t} ===")
    for f in tbl.schema:
        print(f"  {f.name:30s} {f.field_type}  mode={f.mode}")
