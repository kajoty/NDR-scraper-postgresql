# scripts/delete_duplicates_2025_02_09.py

import psycopg2
import json

# Konfiguration laden
with open("config/config.json", "r") as f:
    config = json.load(f)

# Verbindung zur Datenbank
conn = psycopg2.connect(
    host=config["pg_host"],
    port=config["pg_port"],
    user=config["pg_user"],
    password=config["pg_password"],
    dbname=config["pg_db"]
)

cur = conn.cursor()

print("🔍 Lösche doppelte Einträge vom 2025-02-09...")

delete_query = """
WITH ranked_duplicates AS (
    SELECT id,
           ROW_NUMBER() OVER (
               PARTITION BY station, artist, title, played_time, played_date
               ORDER BY id
           ) AS rn
    FROM ndr_playlist
    WHERE played_date = '2025-02-09'
)
DELETE FROM ndr_playlist
WHERE id IN (
    SELECT id FROM ranked_duplicates WHERE rn > 1
);
"""

cur.execute(delete_query)
deleted = cur.rowcount

conn.commit()
conn.close()

print(f"✅ Duplikate erfolgreich gelöscht: {deleted} Eintrag(e) entfernt.")
