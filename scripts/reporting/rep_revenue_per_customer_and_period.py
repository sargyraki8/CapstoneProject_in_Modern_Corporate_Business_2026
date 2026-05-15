#!/usr/bin/env python
# coding: utf-8

# rep_revenue_per_customer_and_period.py
# Creates the rep_revenue_per_customer_and_period reporting table in reporting_db.
#
# IMPORTANT: This uses REVENUE (SUM of payment_amount), NOT rental counts.
# Excludes film 'GOODFELLAS SALUTE' (not billed, offered for free).
# Includes 0-revenue Day/Month/Year rows per customer via reporting_periods_table.
# Uses rental_date for date grouping (consistent with course template).

from google.cloud import bigquery
import pandas as pd
from pandas_gbq import to_gbq
import os

print('Libraries imported successfully')

# -- YOUR CODE GOES BELOW THIS LINE
credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "D:/Projects/Capstone/credentials/sa-key.json")  # Edit path or set GOOGLE_APPLICATION_CREDENTIALS
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
# -- YOUR CODE GOES ABOVE THIS LINE

# -- YOUR CODE GOES BELOW THIS LINE
project_id = 'capstoneproject-493015'  # Edit with your project id
dataset_id = 'reporting_db'
table_id = 'rep_revenue_per_customer_and_period'
# -- YOUR CODE GOES ABOVE THIS LINE

client = bigquery.Client(project=project_id)

# -- YOUR CODE GOES BELOW THIS LINE
query = f"""
with payments as (
  select
    p.customer_id
    , p.payment_amount
    , p.rental_id
    , date(r.rental_date) as rental_date
    , r.inventory_id
  from `{project_id}.staging_db.stg_payment` p
  left join `{project_id}.staging_db.stg_rental` r
    on p.rental_id = r.rental_id
)

, payments_with_film as (
  select
    p.customer_id
    , p.payment_amount
    , p.rental_date
  from payments p
  left join `{project_id}.staging_db.stg_inventory` i
    on p.inventory_id = i.inventory_id
  left join `{project_id}.staging_db.stg_film` f
    on i.film_id = f.film_id
  where f.film_title != 'GOODFELLAS SALUTE'
)

, reporting_dates as (
  select *
  from `{project_id}.reporting_db.reporting_periods_table`
  where reporting_period in ('Day', 'Month', 'Year')
)

, customers as (
  select
    customer_id
  from `{project_id}.staging_db.stg_customer`
)

, customer_reporting_dates as (
  select
    customers.customer_id
    , reporting_dates.reporting_period
    , reporting_dates.reporting_date
  from customers
  cross join reporting_dates
)

, revenue_per_customer_and_period as (
  select
    'Day' as reporting_period
    , date_trunc(rental_date, day) as reporting_date
    , customer_id
    , sum(payment_amount) as total_revenue
  from payments_with_film
  group by 1, 2, 3

  union all

  select
    'Month' as reporting_period
    , date_trunc(rental_date, month) as reporting_date
    , customer_id
    , sum(payment_amount) as total_revenue
  from payments_with_film
  group by 1, 2, 3

  union all

  select
    'Year' as reporting_period
    , date_trunc(rental_date, year) as reporting_date
    , customer_id
    , sum(payment_amount) as total_revenue
  from payments_with_film
  group by 1, 2, 3
)

, final as (
  select
    customer_reporting_dates.reporting_period
    , customer_reporting_dates.reporting_date
    , customer_reporting_dates.customer_id
    , coalesce(revenue_per_customer_and_period.total_revenue, 0) as total_revenue
  from customer_reporting_dates
  left join revenue_per_customer_and_period
    on customer_reporting_dates.customer_id = revenue_per_customer_and_period.customer_id
    and customer_reporting_dates.reporting_period = revenue_per_customer_and_period.reporting_period
    and customer_reporting_dates.reporting_date = revenue_per_customer_and_period.reporting_date
)

select * from final
"""
# -- YOUR CODE GOES ABOVE THIS LINE

df = client.query(query).to_dataframe()
df.head()

full_table_id = f"{project_id}.{dataset_id}.{table_id}"

# -- YOUR CODE GOES BELOW THIS LINE
schema = [
    bigquery.SchemaField('reporting_period', 'STRING'),
    bigquery.SchemaField('reporting_date', 'DATE'),
    bigquery.SchemaField('customer_id', 'INTEGER'),
    bigquery.SchemaField('total_revenue', 'FLOAT'),
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
