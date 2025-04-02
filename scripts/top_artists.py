# scripts/top_artists.py

import psycopg2
import json
from datetime import datetime, timedelta
from collections import defaultdict

def load_config():
    with open('config/config.json', 'r') as f:
        config = json.load(f)
    return config

def connect_db(config):
    return psycopg2.connect(
        host=config['pg_host'],
        port=config['pg_port'],
        user=config['pg_user'],
        password=config['pg_password'],
        dbname=config['pg_db']
    )

def get_top_artists(conn, days=30, top_n=3):
    since_date = (datetime.now() - timedelta(days=days)).date()

    query = """
        SELECT station, artist, COUNT(*) AS play_count
        FROM playlist_data
        WHERE played_date >= %s
        GROUP BY station, artist
        ORDER BY station, play_count DESC
    """

    with conn.cursor() as cur:
        cur.execute(query, (since_date,))
        results = cur.fetchall()

    # Gruppieren nach Station und sortieren nach play_count
    top_artists_by_station = defaultdict(list)
    for station, artist, count in results:
        top_artists_by_station[station].append((artist, count))

    # Nur Top N je Station behalten
    for station in top_artists_by_station:
        top_artists_by_station[station] = top_artists_by_station[station][:top_n]

    return top_artists_by_station

def print_top_artists(data, days):
    print(f"\n🎧 Top Interpreten der letzten {days} Tage:\n")
    for station, artists in data.items():
        print(f"📻 {station}:")
        for i, (artist, count) in enumerate(artists, 1):
            print(f"  {i}. {artist} ({count} Plays)")
        print()

def main():
    config = load_config()
    conn = connect_db(config)
    try:
        top_artists = get_top_artists(conn, days=30, top_n=3)
        print_top_artists(top_artists, 30)
    finally:
        conn.close()

if __name__ == "__main__":
    main()
