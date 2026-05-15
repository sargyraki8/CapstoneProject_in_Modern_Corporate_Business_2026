#!/usr/bin/env python
# Fully automates Metabase setup via the REST API:
#   1. Waits for Metabase to be ready
#   2. Completes the first-run admin setup
#   3. Adds the BigQuery database (using our SA key)
#   4. Creates 4 native-SQL Questions (Cards) matching the capstone rubric
#
# After this runs, `metabase_screenshots.py` can snap PNGs of each Card.

import json
import os
import sys
import time
from pathlib import Path

import requests

METABASE_URL = "http://localhost:3000"
REPO_ROOT = Path(__file__).resolve().parent.parent

ADMIN_EMAIL = "capstone@example.com"
ADMIN_PASSWORD = "Capstone123!"
ADMIN_FIRST = "Capstone"
ADMIN_LAST = "Student"

SA_KEY_PATH = Path(os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", REPO_ROOT / "credentials" / "sa-key.json"))
BQ_PROJECT = "capstoneproject-493015"
BQ_DATASET = "reporting_db"
CREDS_FILE = REPO_ROOT / "exports" / "metabase_creds.json"


def wait_for_metabase(timeout_sec=240):
    print(f"Waiting for Metabase at {METABASE_URL}...", end="", flush=True)
    start = time.time()
    while time.time() - start < timeout_sec:
        try:
            r = requests.get(f"{METABASE_URL}/api/health", timeout=5)
            if r.ok and r.json().get("status") == "ok":
                print(" ready.")
                return
        except Exception:
            pass
        print(".", end="", flush=True)
        time.sleep(3)
    raise SystemExit("Metabase did not become ready in time.")


def get_session():
    """Returns an authenticated session. Handles first-time setup."""
    props = requests.get(f"{METABASE_URL}/api/session/properties").json()
    setup_token = props.get("setup-token")

    if setup_token:
        print("First-time setup detected. Creating admin user...")
        payload = {
            "token": setup_token,
            "user": {
                "first_name": ADMIN_FIRST,
                "last_name": ADMIN_LAST,
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD,
                "site_name": "Capstone",
            },
            "prefs": {
                "site_name": "Capstone",
                "site_locale": "en",
                "allow_tracking": False,
            },
            "database": None,
        }
        r = requests.post(f"{METABASE_URL}/api/setup", json=payload)
        r.raise_for_status()
        session_id = r.json()["id"]
        print(f"  Admin created, session acquired.")
    else:
        print("Metabase already configured. Logging in...")
        r = requests.post(
            f"{METABASE_URL}/api/session",
            json={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        )
        r.raise_for_status()
        session_id = r.json()["id"]

    s = requests.Session()
    s.headers.update({"X-Metabase-Session": session_id, "Content-Type": "application/json"})
    return s


def ensure_bigquery_db(s):
    """Adds the BigQuery database if not already present. Returns db id."""
    existing = s.get(f"{METABASE_URL}/api/database").json()
    # Metabase pagination wrapper
    dbs = existing.get("data", existing) if isinstance(existing, dict) else existing
    for db in dbs:
        if db.get("engine") == "bigquery-cloud-sdk" and db.get("name") == "Capstone BQ":
            print(f"BigQuery database already exists (id={db['id']}).")
            return db["id"]

    print("Adding BigQuery database to Metabase...")
    sa_json = SA_KEY_PATH.read_text()
    payload = {
        "name": "Capstone BQ",
        "engine": "bigquery-cloud-sdk",
        "details": {
            "project-id": BQ_PROJECT,
            "service-account-json": sa_json,
            "dataset-filters-type": "inclusion",
            "dataset-filters-patterns": BQ_DATASET,
            "use-jvm-timezone": False,
            "include-user-id-and-hash": False,
        },
        "is_full_sync": True,
        "is_on_demand": False,
    }
    r = s.post(f"{METABASE_URL}/api/database", json=payload)
    if not r.ok:
        print("POST /api/database failed:", r.status_code, r.text)
        r.raise_for_status()
    db_id = r.json()["id"]
    print(f"  Created (id={db_id}). Triggering sync...")
    s.post(f"{METABASE_URL}/api/database/{db_id}/sync_schema")
    return db_id


CARDS = [
    {
        "name": "Q1 - Revenue per Month",
        "display": "line",
        "description": "Capstone Q1: Monthly revenue trend (for May vs June 2022 comparison).",
        "sql": f"""
SELECT reporting_date, total_revenue
FROM `{BQ_PROJECT}.reporting_db.rep_revenue_per_period`
WHERE reporting_period = 'Month'
ORDER BY reporting_date
""".strip(),
        "result_metadata": [],
        "viz": {
            "graph.dimensions": ["reporting_date"],
            "graph.metrics": ["total_revenue"],
            "graph.x_axis.title_text": "Month",
            "graph.y_axis.title_text": "Total Revenue",
        },
    },
    {
        "name": "Q2 - Average Revenue per Weekday",
        "display": "bar",
        "description": "Capstone Q2: Average daily revenue grouped by weekday.",
        "sql": f"""
SELECT
  FORMAT_DATE('%A', reporting_date) AS weekday_name,
  EXTRACT(DAYOFWEEK FROM reporting_date) AS weekday_num,
  ROUND(AVG(total_revenue), 2) AS avg_revenue
FROM `{BQ_PROJECT}.reporting_db.rep_revenue_per_period`
WHERE reporting_period = 'Day' AND total_revenue > 0
GROUP BY weekday_name, weekday_num
ORDER BY weekday_num
""".strip(),
        "viz": {
            "graph.dimensions": ["weekday_name"],
            "graph.metrics": ["avg_revenue"],
            "graph.x_axis.title_text": "Weekday",
            "graph.y_axis.title_text": "Average Revenue",
        },
    },
    {
        "name": "Q3 - Top 5 Customers (June 2022)",
        "display": "table",
        "description": "Capstone Q3: Top 5 customers by revenue for June 2022.",
        "sql": f"""
SELECT
  customer_id,
  ROUND(total_revenue, 2) AS total_revenue
FROM `{BQ_PROJECT}.reporting_db.rep_revenue_per_customer_and_period`
WHERE reporting_period = 'Month' AND reporting_date = DATE '2022-06-01'
ORDER BY total_revenue DESC
LIMIT 5
""".strip(),
        "viz": {},
    },
    {
        "name": "Q4 - Unique Customers per Month",
        "display": "bar",
        "description": "Capstone Q4: Count of unique paying customers per month.",
        "sql": f"""
SELECT
  reporting_date,
  COUNT(DISTINCT customer_id) AS unique_customers
FROM `{BQ_PROJECT}.reporting_db.rep_revenue_per_customer_and_period`
WHERE reporting_period = 'Month' AND total_revenue > 0
GROUP BY reporting_date
ORDER BY reporting_date
""".strip(),
        "viz": {
            "graph.dimensions": ["reporting_date"],
            "graph.metrics": ["unique_customers"],
            "graph.x_axis.title_text": "Month",
            "graph.y_axis.title_text": "Unique Customers",
        },
    },
]


def create_cards(s, db_id):
    # Look up existing cards so this script is idempotent.
    existing = s.get(f"{METABASE_URL}/api/card").json()
    existing_by_name = {c["name"]: c for c in existing}

    created = []
    for spec in CARDS:
        if spec["name"] in existing_by_name:
            card = existing_by_name[spec["name"]]
            print(f"Card already exists: {spec['name']} (id={card['id']})")
            created.append(card)
            continue

        payload = {
            "name": spec["name"],
            "description": spec.get("description", ""),
            "display": spec["display"],
            "visualization_settings": spec.get("viz", {}),
            "dataset_query": {
                "type": "native",
                "native": {"query": spec["sql"]},
                "database": db_id,
            },
        }
        r = s.post(f"{METABASE_URL}/api/card", json=payload)
        if not r.ok:
            print(f"  Failed to create card '{spec['name']}':", r.status_code, r.text)
            r.raise_for_status()
        card = r.json()
        print(f"Created card: {spec['name']} (id={card['id']})")
        created.append(card)
    return created


def main():
    wait_for_metabase()
    s = get_session()
    db_id = ensure_bigquery_db(s)

    # Wait briefly for schema sync so the native query editor knows the DB.
    print("Waiting 5s for initial sync...")
    time.sleep(5)

    cards = create_cards(s, db_id)

    CREDS_FILE.parent.mkdir(parents=True, exist_ok=True)
    CREDS_FILE.write_text(
        json.dumps(
            {
                "url": METABASE_URL,
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD,
                "card_ids": [c["id"] for c in cards],
                "card_names": [c["name"] for c in cards],
            },
            indent=2,
        )
    )
    print(f"\nSetup complete. Credentials saved to {CREDS_FILE}")
    print(f"Cards created: {[c['id'] for c in cards]}")


if __name__ == "__main__":
    main()
