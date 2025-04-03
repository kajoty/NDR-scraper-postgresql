# functions/postgresql.py

import psycopg2
from psycopg2.extras import execute_batch
from datetime import datetime

def write_to_postgresql(config, data):
    conn = psycopg2.connect(
        host=config["pg_host"],
        port=config["pg_port"],
        user=config["pg_user"],
        password=config["pg_password"],
        dbname=config["pg_db"]
    )

    query = """
        INSERT INTO ndr_playlist (
            checksum, station, artist, title,
            played_date, played_time, played_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (checksum, played_at) DO NOTHING;
    """

    records = []

    for entry in data:
        fields = entry["fields"]
        played_at = datetime.strptime(
            f"{fields['played_date']} {fields['played_time']}", "%Y-%m-%d %H:%M:%S"
        )

        records.append((
            fields['checksum'],
            entry['tags']['station'],
            fields['artist'],
            fields['title'],
            fields['played_date'],
            fields['played_time'],
            played_at
        ))

    with conn.cursor() as cur:
        execute_batch(cur, query, records)
    conn.commit()
    conn.close()
