import psycopg2


def initialize_postgresql(config):
    """
    Stellt eine Verbindung zur PostgreSQL-Datenbank her.
    Die Verbindungsdaten werden aus der Konfigurationsdatei entnommen.
    """
    return psycopg2.connect(
        host=config["pg_host"],
        port=config["pg_port"],
        user=config["pg_user"],
        password=config["pg_password"],
        dbname=config["pg_db"]
    )


def write_to_postgresql(conn, data):
    """
    Schreibt eine Liste von Einträgen in die PostgreSQL-Datenbank.
    Überspringt Einträge, die bereits vorhanden sind (basierend auf checksum + played_at).
    """
    inserted = 0

    try:
        with conn.cursor() as cur:
            for row in data:
                try:
                    cur.execute("""
                        INSERT INTO ndr_playlist (
                            checksum, station, artist, title,
                            played_date, played_time, played_at
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (checksum, played_at) DO NOTHING;
                    """, (
                        row["fields"]["checksum"],
                        row["tags"]["station"],
                        row["fields"]["artist"],
                        row["fields"]["title"],
                        row["fields"]["played_date"],
                        row["fields"]["played_time"],
                        row["fields"]["played_at"]
                    ))
                    inserted += 1
                except Exception as e:
                    print(f"⚠️ Fehler beim Einfügen eines Datensatzes: {e}")

        conn.commit()
        print(f"✅ {inserted} neue Einträge gespeichert.")

    except Exception as e:
        print(f"❌ Fehler bei der Verbindung oder beim Schreiben in PostgreSQL: {e}")
