# scripts/trending_songs.py

import psycopg2
import json
from datetime import datetime
from collections import defaultdict

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

# Hole alle play_counts pro Tag und Song
query = """
SELECT artist, title, played_date, COUNT(*) AS play_count
FROM ndr_playlist
GROUP BY artist, title, played_date
ORDER BY artist, title, played_date;
"""

cur.execute(query)
rows = cur.fetchall()
conn.close()

# Strukturieren nach (artist, title)
song_data = defaultdict(list)
for artist, title, date, count in rows:
    key = (artist.strip(), title.strip())
    song_data[key].append((date, count))

# Trending erkennen: mind. 3 Tage mit steigendem Verlauf
def is_trending(play_counts):
    if len(play_counts) < 3:
        return False
    trend = 0
    for i in range(1, len(play_counts)):
        if play_counts[i] > play_counts[i - 1]:
            trend += 1
        else:
            trend = 0
        if trend >= 2:  # mind. 3 Tage ansteigend
            return True
    return False

# Analyse & Ausgabe
print("📈 Songs mit ansteigender Spielhäufigkeit (potenzielle Trends):\n")

for (artist, title), history in song_data.items():
    history.sort()  # sort by date
    dates, counts = zip(*history)
    if is_trending(counts):
        print(f"🎵 {artist} – {title}")
        for d, c in history:
            print(f"   {d}: {c} Play(s)")
        print()
