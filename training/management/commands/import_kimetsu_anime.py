import json
import time
import requests

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.dateparse import parse_date

from training.models import Anime


class Command(BaseCommand):
    help = "Pull/import all anime data from Kitsu API"

    def add_arguments(self, parser):
        parser.add_argument(
            "--commit",
            type=str,
            default="false",
            choices=["true", "false"],
            help="Commit changes to the database",
        )

    def handle(self, *args, **kwargs):
        commit = kwargs["commit"] == "true"

        self.stdout.write("Starting Kitsu anime API import")

        url = "https://kitsu.io/api/edge/anime"

        headers = {
            "Accept": "application/vnd.api+json",
            "Content-Type": "application/vnd.api+json",
        }

        total_processed = 0
        total_created = 0
        total_updated = 0

        with requests.Session() as session:
            session.headers.update(headers)

            while url:
                response = session.get(url, timeout=30)
                response.raise_for_status()

                result = response.json()

                for item in result.get("data", []):
                    total_processed += 1

                    if not commit:
                        self.stdout.write(
                            json.dumps(item, ensure_ascii=False, indent=2)
                        )
                        continue

                    attributes = item.get("attributes", {})
                    poster = attributes.get("posterImage") or {}
                    cover = attributes.get("coverImage") or {}

                    defaults = {
                        "title": attributes.get("canonicalTitle") or "",
                        "synopsis": (
                            attributes.get("synopsis")
                            or attributes.get("description")
                            or ""
                        ),
                        "average_rating": self.to_decimal(
                            attributes.get("averageRating")
                        ),
                        "poster_image_url": poster.get("original") or "",
                        "cover_image_url": cover.get("original") or "",
                        "start_date": parse_date(
                            attributes.get("startDate") or ""
                        ),
                        "end_date": parse_date(
                            attributes.get("endDate") or ""
                        ),
                        "episode_count": attributes.get("episodeCount"),
                        "status": attributes.get("status") or "",
                        "raw_data": item,
                    }

                    with transaction.atomic():
                        _, created = Anime.objects.update_or_create(
                            external_id=item["id"],
                            defaults=defaults,
                        )

                    if created:
                        total_created += 1
                    else:
                        total_updated += 1

                self.stdout.write(
                    f"Processed {total_processed} anime records"
                )

                url = result.get("links", {}).get("next")

                if url:
                    time.sleep(0.5)

        self.stdout.write(
            self.style.SUCCESS(
                f"Finished processing {total_processed} records."
            )
        )

        if commit:
            self.stdout.write(
                f"Created: {total_created} | Updated: {total_updated}"
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    "Dry run completed. No database changes were made."
                )
            )

    @staticmethod
    def to_decimal(value):
        if value in (None, ""):
            return None

        from decimal import Decimal, InvalidOperation

        try:
            return Decimal(str(value))
        except (InvalidOperation, ValueError, TypeError):
            return None