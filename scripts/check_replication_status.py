#!/usr/bin/env python
# Checks replication slot status while Datastream runs the backfill.

import psycopg2

conn = psycopg2.connect(
    host="ihu-2.cns2i60wmsn5.eu-north-1.rds.amazonaws.com",
    port=5432, user="student", password="student", dbname="postgres",
)
conn.autocommit = True
cur = conn.cursor()

print("Replication slots:")
cur.execute("""
    SELECT slot_name, plugin, slot_type, active, active_pid, restart_lsn, confirmed_flush_lsn
    FROM pg_replication_slots
    ORDER BY slot_name;
""")
for row in cur.fetchall():
    print(" ", row)

print("\nActive replication connections:")
cur.execute("""
    SELECT pid, usename, application_name, client_addr, state, backend_start
    FROM pg_stat_activity
    WHERE backend_type = 'walsender' OR application_name LIKE '%datastream%' OR usename = 'student'
    ORDER BY backend_start DESC;
""")
for row in cur.fetchall():
    print(" ", row)

cur.close()
conn.close()
