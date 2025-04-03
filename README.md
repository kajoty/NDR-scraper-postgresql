# 🎵 NDR Playlist Scraper (PostgreSQL Edition)

Ein Python-Skript zur automatisierten Abfrage und Speicherung von Musiktiteln aus den öffentlich zugänglichen Playlists der NDR-Radiosender. Die Daten werden in einer PostgreSQL-Datenbank gespeichert, ausgewertet und bei Bedarf analysiert.

---

## 🧰 Funktionen

- ⏱ Automatisierter Tagesabruf der Playlists
- 📥 Speicherung in PostgreSQL (TimescaleDB kompatibel)
- 📊 Eigene Analyse-Skripte (z. B. Top-Interpreten, Anomalien, etc.)
- 🛠 Konfigurierbar über `config/config.json`
- ⚙️ Optional gesteuert über `systemd.timer`
- 🧪 HTML-Scraping mit `BeautifulSoup`

---

## 📦 Voraussetzungen

- Python ≥ 3.8
- PostgreSQL (z. B. als Docker-Container)
- Empfohlene Pakete (siehe `requirements.txt`)

Installiere mit:

```bash
sudo apt install python3-aiohttp python3-requests python3-psycopg2 python3-bs4
```

Oder via Pip:

```bash
pip install -r requirements.txt
```

---

## 📁 Projektstruktur

```bash
NDR-scraper-postgresql/
├── abfrage.py                  # Interaktive Auswahl-Abfrage
├── abfrage_auto.py            # Automatisierte Version (für systemd)
├── stations.csv               # Liste der NDR-Sender + URLs
├── requirements.txt           # Python-Abhängigkeiten
├── config/
│   ├── config.json            # Zugangsdaten für PostgreSQL
│
├── functions/
│   ├── fetch_data.py          # HTTP-Download via aiohttp
│   ├── postgresql.py          # DB-Verbindung + Insert-Logik
│   └── scrape_playlist.py     # HTML-Parsen + Datenaufbereitung
│
├── scripts/                   # Eigene Analyse- und Auswertungs-Tools
│   ├── top_artists.py         # Top 3 Interpreten je Sender
│   ├── evaluate_day.py        # Analyse einzelner Tage
│   ├── check_anomalies.py     # Erkennung von Ausreißern
```

---

## ⚙️ Konfiguration

In `config/config.json`:

```json
{
  "pg_host": "192.168.178.100",
  "pg_port": 5432,
  "pg_user": "admin",
  "pg_password": "admin",
  "pg_db": "playlist",
  "num_days": 3,
  "max_parallel_requests": 10
}
```

---

## 🐘 PostgreSQL Setup

```sql
CREATE TABLE ndr_playlist (
    checksum TEXT NOT NULL,
    station TEXT,
    artist TEXT,
    title TEXT,
    played_date DATE,
    played_time TIME,
    played_at TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (checksum, played_at)
);

-- Optional: TimescaleDB aktivieren
CREATE EXTENSION IF NOT EXISTS timescaledb;
SELECT create_hypertable('ndr_playlist', 'played_at', if_not_exists => TRUE);
```

---

## 🚀 Automatisierung mit systemd

### `ndr-abfrage.service`

```ini
[Unit]
Description=NDR Scraper Abfrage – einmal täglich
After=network.target

[Service]
Type=oneshot
User=pi
WorkingDirectory=/home/pi/NDR-scraper-postgresql
ExecStart=/usr/bin/python3 /home/pi/NDR-scraper-postgresql/abfrage_auto.py
```

### `ndr-abfrage.timer`

```ini
[Unit]
Description=Täglicher Abruf der NDR-Playlisten

[Timer]
OnCalendar=*-*-* 03:30:00
Persistent=true

[Install]
WantedBy=timers.target
```

### Aktivieren:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now ndr-abfrage.timer
```

---

## 🔍 Beispielanalysen

- `top_artists.py`: Top 3 Interpreten der letzten 30 Tage je Sender
- `evaluate_day.py`: Analyse auffälliger Tage (z. B. Duplikate)
- `check_anomalies.py`: Erkennung von ungewöhnlich vielen Einträgen pro Tag

---

## 📊 Beispielausgabe (top_artists.py)

```text
📻 N-Joy:
  1. Nina Chuba (147 Plays)
  2. Myles Smith (125 Plays)
  3. Linkin Park (120 Plays)

📻 NDR 2:
  1. Ed Sheeran (82 Plays)
  2. Linkin Park (77 Plays)
  3. Benson Boone (72 Plays)
```

---

## 👤 Autor

**[@kajoty](https://github.com/kajoty)**  
MIT License

---

## ☕ Feedback & Ideen?

Pull Requests, Issues oder Wünsche sind jederzeit willkommen! ✨
