import psycopg2
from psycopg2.extras import execute_batch
from datetime import datetime

def initialize_postgresql(config):
    return psycopg2.connect(
        host=config["pg_host"],
        port=config["pg_port"],
        user=config["pg_user"],
        password=config["pg_password"],
        dbname=config["pg_db"]
    )

def write_to_postgresql(conn, data):
    if not data:
        return

    try:
        with conn.cursor() as cur:
            query = """
                INSERT INTO playlist_data (
                    checksum, station, artist, title,
                    played_date, played_time, played_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (checksum, played_at) DO NOTHING
            """

            values = []
            for entry in data:
                fields = entry["fields"]
                tags = entry["tags"]

                played_date = fields["played_date"]
                played_time = fields["played_time"]

                try:
                    played_at = datetime.strptime(
                        f"{played_date} {played_time}", "%Y-%m-%d %H:%M"
                    )
                except ValueError:
                    played_at = None

                values.append((
                    fields["checksum"],
                    tags["station"],
                    fields.get("artist"),
                    fields.get("title"),
                    played_date,
                    played_time,
                    played_at
                ))

            execute_batch(cur, query, values)
        conn.commit()

    except Exception as e:
        conn.rollback()  # Fehlerhafte Transaktion zurücksetzen
        print(f"[DB-Fehler] {e}")
