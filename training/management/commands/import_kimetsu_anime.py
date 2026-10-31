
import json
import time
import requests

from decimal import Decimal, InvalidOperation

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.dateparse import parse_date

from training.models import Anime


class Command(BaseCommand):
    help = "Pull/import all anime data from Kitsu API"

    RELATIONSHIPS = ("genres", "categories", "characters")

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

        url = (
            "https://kitsu.io/api/edge/anime"
            "?include=genres,categories,characters"
        )

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

                # Index included resources for quick lookup.
                included = {
                    (resource["type"], resource["id"]): resource
                    for resource in result.get("included", [])
                }

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

                        # Relationship fields
                        "genres": self.get_relationship(
                            session, item, "genres", included
                        ),
                        "categories": self.get_relationship(
                            session, item, "categories", included
                        ),
                        "characters": self.get_relationship(
                            session, item, "characters", included
                        ),

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

    @classmethod
    def get_relationship(cls, session, item, relationship, included):
        """
        Get related resources from the included response.
        If they aren't included, fetch them using the relationship URL.
        """
        relationship_data = (
            item.get("relationships", {})
            .get(relationship, {})
        )

        resource_ids = relationship_data.get("data")

        if resource_ids is not None:
            resources = [
                included.get((resource["type"], resource["id"]))
                for resource in resource_ids
            ]

            resources = [resource for resource in resources if resource]

            if len(resources) == len(resource_ids):
                return [
                    cls.normalize_resource(resource, relationship)
                    for resource in resources
                ]

        # Fallback: fetch the relationship endpoint.
        related_url = (
            relationship_data.get("links", {}).get("related")
        )

        if not related_url:
            return []

        resources = []

        while related_url:
            response = session.get(related_url, timeout=30)
            response.raise_for_status()

            result = response.json()
            resources.extend(result.get("data", []))

            related_url = result.get("links", {}).get("next")

            if related_url:
                time.sleep(0.2)

        return [
            cls.normalize_resource(resource, relationship)
            for resource in resources
        ]

    @staticmethod
    def normalize_resource(resource, relationship):
        """
        Convert Kitsu resources into consistent JSON objects.
        """
        attributes = resource.get("attributes", {})

        if relationship == "genres":
            return {
                "id": resource.get("id"),
                "name": attributes.get("name") or "",
            }

        if relationship == "categories":
            return {
                "id": resource.get("id"),
                "name": (
                    attributes.get("title")
                    or attributes.get("name")
                    or ""
                ),
                "description": attributes.get("description") or "",
            }

        if relationship == "characters":
            return {
                "id": resource.get("id"),
                "name": attributes.get("name") or "",
                "description": attributes.get("description") or "",
                "image": (
                    (attributes.get("image") or {}).get("original", "")
                ),
            }

        return attributes

    @staticmethod
    def to_decimal(value):
        if value in (None, ""):
            return None

        try:
            return Decimal(str(value))
        except (InvalidOperation, ValueError, TypeError):
            return None
