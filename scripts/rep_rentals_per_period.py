#!/usr/bin/env python
# coding: utf-8

# # Setup - Install Libraries

# In[1]:


# Run the following commands once, in order to install libraries - DO NOT Uncomment this line.

# Uncomment below lines

# !pip3 install --upgrade pip
# !pip install google-cloud-bigquery
# !pip install pandas-gbq -U
# !pip install db-dtypes
# !pip install packaging --upgrade


# # Import libraries

# In[2]:


# Import libraries
from google.cloud import bigquery
import pandas as pd
from pandas_gbq import to_gbq
import os

print('Libraries imported successfully')


# In[3]:


# Set the environment variable for Google Cloud credentials
# Place the path in which the .json file is located.

# Example (if .json is located in the same directory with the notebook)
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "at-arch-416714-6f9900ec7.json"


# -- YOUR CODE GOES BELOW THIS LINE

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/antonesangelakes/scripts/mineral-voyage-442817-m2-1de3ad04cf72.json" # Edit path

# -- YOUR CODE GOES ABOVE THIS LINE


# In[4]:


# Set your Google Cloud project ID and BigQuery dataset details

# -- YOUR CODE GOES BELOW THIS

project_id = 'mineral-voyage-442817-m2' # Edit with your project id
dataset_id = 'reporting_db' # Modify the necessary schema name: staging_db, reporting_db etc.
table_id = 'rep_rentals_per_period' # Modify the necessary table name: stg_customer, stg_city etc.

# -- YOUR CODE GOES ABOVE THIS LINE


# # SQL Query

# In[5]:


# Create a BigQuery client
client = bigquery.Client(project=project_id)

# -- YOUR CODE GOES BELOW THIS LINE

# Define your SQL query here
query = """
with rentals as (
 select *
 from mineral-voyage-442817-m2.staging_db.stg_rental
)

, reporting_dates as (
 select *
 from mineral-voyage-442817-m2.reporting_db.reporting_periods_table
 where reporting_period in ('Day','Month','Year')
)

, rentals_per_period as (
 select
   'Day' as reporting_period
   , date_trunc(rentals.rental_date, day) as reporting_date
   , count(*) as total_rentals
 from rentals
 group by 1,2
union all
 select
   'Month' as reporting_period
   , date_trunc(rentals.rental_date, month) as reporting_date
   , count(*) as total_rentals
 from rentals
 group by 1,2
union all
 select
   'Year' as reporting_period
   , date_trunc(rentals.rental_date, year) as reporting_date
   , count(*) as total_rentals
 from rentals
 group by 1,2
)

, final as (
select
 reporting_dates.reporting_period
 , reporting_dates.reporting_date
 , coalesce(rentals_per_period.total_rentals,0) as total_rentals
from reporting_dates
left join rentals_per_period
on reporting_dates.reporting_period = rentals_per_period.reporting_period
and reporting_dates.reporting_date = rentals_per_period.reporting_date
where reporting_dates.reporting_period = 'Day'
union all
select
 reporting_dates.reporting_period
 , reporting_dates.reporting_date
 , coalesce(rentals_per_period.total_rentals,0) as total_rentals
from reporting_dates
left join rentals_per_period
on reporting_dates.reporting_period = rentals_per_period.reporting_period
and reporting_dates.reporting_date = rentals_per_period.reporting_date
where reporting_dates.reporting_period = 'Month'
union all
select
 reporting_dates.reporting_period
 , reporting_dates.reporting_date
 , coalesce(rentals_per_period.total_rentals,0) as total_rentals
from reporting_dates
left join rentals_per_period
on reporting_dates.reporting_period = rentals_per_period.reporting_period
and reporting_dates.reporting_date = rentals_per_period.reporting_date
where reporting_dates.reporting_period = 'Year'
)

select * from final
"""

# -- YOUR CODE GOES ABOVE THIS LINE

# Execute the query and store the result in a dataframe
df = client.query(query).to_dataframe()

# Explore some records
df.head()


# # Write to BigQuery

# In[6]:


# Define the full table ID
full_table_id = f"{project_id}.{dataset_id}.{table_id}"

# -- YOUR CODE GOES BELOW THIS LINE
# Define table schema based on the project description

schema = [
    bigquery.SchemaField('reporting_period', 'STRING'),
    bigquery.SchemaField('reporting_date', 'DATETIME'),
    bigquery.SchemaField('total_rentals', 'INTEGER'),
    ]

# -- YOUR CODE GOES ABOVE THIS LINE


# In[7]:


# Create a BigQuery client
client = bigquery.Client(project=project_id)

# Check if the table exists
def table_exists(client, full_table_id):
    try:
        client.get_table(full_table_id)
        return True
    except Exception:
        return False

# Write the dataframe to the table (overwrite if it exists, create if it doesn't)
if table_exists(client, full_table_id):
    # If the table exists, overwrite it
    destination_table = f"{dataset_id}.{table_id}"
    # Write the dataframe to the table (overwrite if it exists)
    to_gbq(df, destination_table, project_id=project_id, if_exists='replace')
    print(f"Table {full_table_id} exists. Overwritten.")
else:
    # If the table does not exist, create it
    job_config = bigquery.LoadJobConfig(schema=schema)
    job = client.load_table_from_dataframe(df, full_table_id, job_config=job_config)
    job.result()  # Wait for the job to complete
    print(f"Table {full_table_id} did not exist. Created and data loaded.")

