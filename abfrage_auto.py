# abfrage_auto.py

import asyncio
from tqdm import tqdm
from datetime import datetime, timedelta

from functions.fetch_data import fetch_playlist
from functions.scrape_playlist import scrape_playlist
from functions.postgresql import initialize_postgresql, write_to_postgresql
from abfrage import load_config_and_stations, fetch_data_for_day

import aiohttp
from asyncio import Semaphore


async def fetch_all_data_auto():
    config, stations = load_config_and_stations()
    num_days = config.get('num_days', 7)
    max_parallel = config.get('max_parallel_requests', 10)

    stations_to_query = stations  # automatisch alle
    now = datetime.now()
    dates = [(now - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(num_days)]

    client = initialize_postgresql(config)

    total_tasks = len(dates) * len(stations_to_query)
    progress = tqdm(total=total_tasks, desc="Fortschritt")

    async with aiohttp.ClientSession() as session:
        semaphore = Semaphore(max_parallel)

        async def wrapped_task(station, date):
            try:
                await fetch_data_for_day(session, semaphore, client, station, date)
            except Exception as e:
                tqdm.write(f"Fehler bei {station['station_name']} am {date}: {e}")
            finally:
                progress.update(1)

        tasks = [wrapped_task(station, date) for date in dates for station in stations_to_query]
        await asyncio.gather(*tasks)

    progress.close()
    client.close()


if __name__ == "__main__":
    try:
        asyncio.run(fetch_all_data_auto())
    finally:
        tqdm.write("Automatischer Abruf beendet.")
