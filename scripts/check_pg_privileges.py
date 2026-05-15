#!/usr/bin/env python
# Diagnostic: checks what the student user can do.
import psycopg2

conn = psycopg2.connect(
    host="ihu-2.cns2i60wmsn5.eu-north-1.rds.amazonaws.com",
    port=5432, user="student", password="student", dbname="postgres",
)
conn.autocommit = True
cur = conn.cursor()

print("Current user / role:")
cur.execute("SELECT current_user, session_user;")
print(" ", cur.fetchone())

print("\nRoles of current user:")
cur.execute("""
    SELECT r.rolname, r.rolsuper, r.rolcreatedb, r.rolreplication, r.rolbypassrls
    FROM pg_roles r
    WHERE pg_has_role(current_user, r.oid, 'member');
""")
for row in cur.fetchall():
    print(" ", row)

print("\nDatabases visible:")
cur.execute("SELECT datname FROM pg_database WHERE datallowconn ORDER BY datname;")
for row in cur.fetchall():
    print(" ", row[0])

print("\nCurrent database:")
cur.execute("SELECT current_database();")
print(" ", cur.fetchone())

print("\nSchemas with tables student can see:")
cur.execute("""
    SELECT table_schema, COUNT(*)
    FROM information_schema.tables
    WHERE table_schema NOT IN ('pg_catalog','information_schema')
    GROUP BY table_schema
    ORDER BY table_schema;
""")
for row in cur.fetchall():
    print(" ", row)

print("\nExisting publications:")
cur.execute("SELECT pubname, pubowner::regrole, puballtables FROM pg_publication;")
for row in cur.fetchall():
    print(" ", row)

print("\nHas CREATE on current database?")
cur.execute("SELECT has_database_privilege(current_user, current_database(), 'CREATE');")
print(" ", cur.fetchone())

cur.close()
conn.close()
