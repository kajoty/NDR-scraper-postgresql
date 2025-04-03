# scripts/evaluate_day.py

import psycopg2
import json
from datetime import datetime

# Konfiguration laden
with open("config/config.json", "r") as f:
    config = json.load(f)

# Zieldatum analysieren
TARGET_DATE = '2025-02-11'  # Hier beliebiges Datum eintragen

# Verbindung aufbauen
conn = psycopg2.connect(
    host=config["pg_host"],
    port=config["pg_port"],
    user=config["pg_user"],
    password=config["pg_password"],
    dbname=config["pg_db"]
)

cur = conn.cursor()

# Gesamtanzahl
cur.execute("""
    SELECT COUNT(*) FROM ndr_playlist
    WHERE played_date = %s;
""", (TARGET_DATE,))
total = cur.fetchone()[0]

print(f"📆 Analyse für {TARGET_DATE}")
print(f"▶️ Gesamtanzahl Songs: {total}\n")

# Verteilung nach Sender
cur.execute("""
    SELECT station, COUNT(*) AS count
    FROM ndr_playlist
    WHERE played_date = %s
    GROUP BY station
    ORDER BY count DESC;
""", (TARGET_DATE,))
rows = cur.fetchall()

print("📻 Verteilung nach Sender:")
for station, count in rows:
    print(f"  - {station}: {count} Songs")
print()

# Verdächtige Dopplungen (gleicher Song + Uhrzeit)
cur.execute("""
    SELECT artist, title, played_time, COUNT(*) AS dup_count
    FROM ndr_playlist
    WHERE played_date = %s
    GROUP BY artist, title, played_time
    HAVING COUNT(*) > 1
    ORDER BY dup_count DESC
    LIMIT 20;
""", (TARGET_DATE,))
duplicates = cur.fetchall()

if duplicates:
    print("🔁 Verdächtige Dopplungen (gleicher Song + Uhrzeit):")
    for artist, title, time, count in duplicates:
        print(f"  - {artist} – {title} @ {time} → {count}x")
else:
    print("✅ Keine doppelten Songs gefunden (basierend auf artist, title, time)")

conn.close()
