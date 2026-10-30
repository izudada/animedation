
import json
import time
import requests

from training.models import Anime


url = "https://kitsu.io/api/edge/anime"

headers = {
    "Accept": "application/vnd.api+json",
}

total_downloaded = 0

with requests.Session() as session:
    session.headers.update(headers)

    with open("training/kitsu_anime.jsonl", "w", encoding="utf-8") as file:
        while url:
            response = session.get(url, timeout=30)
            response.raise_for_status()

            result = response.json()

            for anime in result["data"]:
                file.write(
                    json.dumps(anime, ensure_ascii=False) + "\n"
                )
                total_downloaded += 1

            print(f"Downloaded {total_downloaded} anime records")

            # Kitsu provides the next-page URL in the response.
            url = result.get("links", {}).get("next")

            if url:
                time.sleep(0.5)

print(f"Finished! Downloaded {total_downloaded} records.")
