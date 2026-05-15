#!/usr/bin/env python
# Creates the logical replication slot needed by Datastream.
# Run this just BEFORE clicking "Create & Start" in the Datastream console.

import psycopg2
import sys

SLOT_NAME = sys.argv[1] if len(sys.argv) > 1 else "mdobe_replication"

conn = psycopg2.connect(
    host="ihu-2.cns2i60wmsn5.eu-north-1.rds.amazonaws.com",
    port=5432,
    user="student",
    password="student",
    dbname="postgres",
)
conn.autocommit = True
cur = conn.cursor()

print(f"Using slot name: {SLOT_NAME}")

# Check if slot already exists
cur.execute("SELECT slot_name, active FROM pg_replication_slots WHERE slot_name = %s;", (SLOT_NAME,))
existing = cur.fetchone()
if existing:
    print(f"Slot '{SLOT_NAME}' already exists (active={existing[1]}). Dropping it first...")
    try:
        cur.execute(f"SELECT pg_drop_replication_slot('{SLOT_NAME}');")
        print("  Dropped.")
    except Exception as e:
        print(f"  Could not drop (may be in use by another session): {e}")
        sys.exit(1)

# Create the slot
try:
    cur.execute(f"SELECT pg_create_logical_replication_slot('{SLOT_NAME}', 'pgoutput');")
    result = cur.fetchone()
    print(f"SUCCESS: Replication slot created -> {result}")
    print("")
    print(f">>> In GCP Datastream source connection profile, set REPLICATION SLOT NAME to: {SLOT_NAME}")
    print(">>> Then click 'CREATE & START' within the next 2-3 minutes")
    print(">>> Tell me once the stream shows 'Running' and I'll drop the slot")
except Exception as e:
    print(f"FAILED: {e}")

cur.close()
conn.close()
