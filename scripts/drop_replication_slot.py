#!/usr/bin/env python
# Drops a logical replication slot by name.
# Run this AFTER the Datastream stream is confirmed Running.

import psycopg2
import sys

SLOT_NAME = sys.argv[1] if len(sys.argv) > 1 else "sarg_replication"

conn = psycopg2.connect(
    host="ihu-2.cns2i60wmsn5.eu-north-1.rds.amazonaws.com",
    port=5432,
    user="student",
    password="student",
    dbname="postgres",
)
conn.autocommit = True
cur = conn.cursor()

cur.execute("SELECT slot_name, active FROM pg_replication_slots WHERE slot_name = %s;", (SLOT_NAME,))
row = cur.fetchone()
if not row:
    print(f"Slot '{SLOT_NAME}' does not exist. Nothing to do.")
else:
    print(f"Slot '{SLOT_NAME}' found (active={row[1]}). Dropping...")
    try:
        cur.execute(f"SELECT pg_drop_replication_slot('{SLOT_NAME}');")
        print(f"SUCCESS: Slot '{SLOT_NAME}' dropped.")
    except Exception as e:
        print(f"FAILED: {e}")
        print("(If active=True, Datastream is holding it — that's expected while the stream runs.)")

cur.close()
conn.close()
