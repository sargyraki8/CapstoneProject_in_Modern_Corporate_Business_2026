#!/usr/bin/env python
# Creates a PostgreSQL publication for Datastream.
# Publication name must match what's configured in the Datastream source profile.

import psycopg2
import sys

PUB_NAME = sys.argv[1] if len(sys.argv) > 1 else "sarg_stream"

TABLES = [
    "actor", "address", "category", "city", "country",
    "customer", "film", "film_actor", "film_category",
    "inventory", "language", "payment", "rental", "staff", "store",
]

conn = psycopg2.connect(
    host="ihu-2.cns2i60wmsn5.eu-north-1.rds.amazonaws.com",
    port=5432,
    user="student",
    password="student",
    dbname="postgres",
)
conn.autocommit = True
cur = conn.cursor()

# Drop if exists (clean slate)
cur.execute("SELECT pubname FROM pg_publication WHERE pubname = %s;", (PUB_NAME,))
if cur.fetchone():
    print(f"Publication '{PUB_NAME}' exists. Dropping it...")
    cur.execute(f"DROP PUBLICATION {PUB_NAME};")
    print("  Dropped.")

tables_sql = ", ".join(f"public.{t}" for t in TABLES)
sql = f"CREATE PUBLICATION {PUB_NAME} FOR TABLE {tables_sql};"
print(f"Creating publication '{PUB_NAME}' for {len(TABLES)} tables...")
try:
    cur.execute(sql)
    print(f"SUCCESS: Publication '{PUB_NAME}' created.")
except Exception as e:
    print(f"FAILED: {e}")
    sys.exit(1)

# Verify
cur.execute(
    "SELECT pubname, puballtables FROM pg_publication WHERE pubname = %s;",
    (PUB_NAME,),
)
print("Verification:", cur.fetchone())

cur.execute(
    "SELECT schemaname, tablename FROM pg_publication_tables WHERE pubname = %s ORDER BY tablename;",
    (PUB_NAME,),
)
rows = cur.fetchall()
print(f"Tables in publication ({len(rows)}):")
for schema, tbl in rows:
    print(f"  - {schema}.{tbl}")

cur.close()
conn.close()
