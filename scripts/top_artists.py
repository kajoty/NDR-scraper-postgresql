# scripts/top_artists.py

import psycopg2
import json
from datetime import datetime, timedelta

# Konfiguration laden
with open("config/config.json", "r") as f:
    config = json.load(f)

# PostgreSQL-Verbindung
conn = psycopg2.connect(
    host=config["pg_host"],
    port=config["pg_port"],
    user=config["pg_user"],
    password=config["pg_password"],
    dbname=config["pg_db"]
)

cur = conn.cursor()

# 30 Tage zurück
date_limit = (datetime.utcnow() - timedelta(days=30)).date()

query = """
SELECT station, artist, COUNT(*) AS play_count
FROM ndr_playlist
WHERE played_date >= %s
GROUP BY station, artist
ORDER BY station, play_count DESC;
"""

cur.execute(query, (date_limit,))
rows = cur.fetchall()

current_station = None
rank = 1

print("🎧 Top Interpreten der letzten 30 Tage:\n")

for row in rows:
    station, artist, count = row
    if station != current_station:
        if current_station is not None:
            print()
        print(f"📻 {station}:")
        current_station = station
        rank = 1

    if rank <= 3:
        print(f"  {rank}. {artist} ({count} Plays)")
        rank += 1

conn.close()
