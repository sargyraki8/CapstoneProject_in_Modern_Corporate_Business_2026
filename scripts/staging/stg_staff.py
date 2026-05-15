#!/usr/bin/env python
# coding: utf-8

# Import libraries
from google.cloud import bigquery
import pandas as pd
from pandas_gbq import to_gbq
import os

print('Libraries imported successfully')

# -- YOUR CODE GOES BELOW THIS LINE
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "D:/Projects/Capstone/credentials/sa-key.json"  # Edit path
# -- YOUR CODE GOES ABOVE THIS LINE

# -- YOUR CODE GOES BELOW THIS LINE
project_id = 'capstoneproject-493015'  # Edit with your project id
dataset_id = 'staging_db'
table_id = 'stg_staff'
# -- YOUR CODE GOES ABOVE THIS LINE

client = bigquery.Client(project=project_id)

# -- YOUR CODE GOES BELOW THIS LINE
query = """
with base as (
  select *
  from `capstoneproject-493015.pagila_productionpublicpublic.staff`
)

, final as (
  select
      staff_id
      , first_name as staff_first_name
      , last_name as staff_last_name
      , address_id as staff_address_id
      , email as staff_email
      , store_id
      , active as is_active_staff
      , username as staff_username
      , password as staff_password
      , last_update as staff_last_update
      , picture as staff_picture
  from base
)

select * from final
"""
# -- YOUR CODE GOES ABOVE THIS LINE

df = client.query(query).to_dataframe()
df.head()

full_table_id = f"{project_id}.{dataset_id}.{table_id}"

# -- YOUR CODE GOES BELOW THIS LINE
schema = [
    bigquery.SchemaField('staff_id', 'INTEGER'),
    bigquery.SchemaField('staff_first_name', 'STRING'),
    bigquery.SchemaField('staff_last_name', 'STRING'),
    bigquery.SchemaField('staff_address_id', 'INTEGER'),
    bigquery.SchemaField('staff_email', 'STRING'),
    bigquery.SchemaField('store_id', 'INTEGER'),
    bigquery.SchemaField('is_active_staff', 'BOOLEAN'),
    bigquery.SchemaField('staff_username', 'STRING'),
    bigquery.SchemaField('staff_password', 'STRING'),
    bigquery.SchemaField('staff_last_update', 'DATETIME'),
    bigquery.SchemaField('staff_picture', 'BYTES'),
]
# -- YOUR CODE GOES ABOVE THIS LINE

client = bigquery.Client(project=project_id)

def table_exists(client, full_table_id):
    try:
        client.get_table(full_table_id)
        return True
    except Exception:
        return False

if table_exists(client, full_table_id):
    destination_table = f"{dataset_id}.{table_id}"
    to_gbq(df, destination_table, project_id=project_id, if_exists='replace')
    print(f"Table {full_table_id} exists. Overwritten.")
else:
    job_config = bigquery.LoadJobConfig(schema=schema)
    job = client.load_table_from_dataframe(df, full_table_id, job_config=job_config)
    job.result()
    print(f"Table {full_table_id} did not exist. Created and data loaded.")
