# scripts/check_anomalies.py

import psycopg2
import json
from statistics import mean, stdev

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

print("📊 Prüfe Datenbank auf ungewöhnlich viele Einträge pro Tag...\n")

# Anzahl Songs pro Tag abrufen
cur.execute("""
    SELECT played_date, COUNT(*) AS total
    FROM ndr_playlist
    GROUP BY played_date
    ORDER BY played_date;
""")
rows = cur.fetchall()
conn.close()

# Zahlen extrahieren
counts = [row[1] for row in rows]
avg = mean(counts)
std = stdev(counts)
threshold = avg + 2 * std  # Anomalie = deutlich über dem Mittelwert

print(f"📈 Durchschnittliche Songs pro Tag: {int(avg)}")
print(f"⚠️ Anomalie-Schwelle: > {int(threshold)}\n")

# Ergebnis anzeigen
print("🧯 Verdächtige Tage mit überdurchschnittlicher Songanzahl:\n")
for date, count in rows:
    if count > threshold:
        print(f"❗ {date} → {count} Songs")

print("\n✅ Fertig.")
