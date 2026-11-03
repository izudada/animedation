import time

import requests

from decimal import Decimal, InvalidOperation

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.dateparse import parse_date

from training.models import Anime, Character


class Command(BaseCommand):
    help = "Pull/import all anime data from Kitsu API"

    BASE_URL = "https://kitsu.io/api/edge/anime"

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

        url = f"{self.BASE_URL}?include=genres,categories,characters"

        session = self.create_session()

        # Avoid requesting the same character more than once
        # during this import run.
        # character_cache = {}

        total_processed = 0
        total_created = 0
        total_updated = 0
        total_failed = 0

        failed_records = []

        try:
            while url:
                response = session.get(url, timeout=30)
                response.raise_for_status()

                result = response.json()

                included = {
                    (resource["type"], resource["id"]): resource
                    for resource in result.get("included", [])
                }

                for item in result.get("data", []):
                    total_processed += 1

                    anime_id = item.get("id", "unknown")

                    try:
                        defaults = self.build_defaults(
                            session=session,
                            item=item,
                            included=included,
                            # character_cache=character_cache,
                        )

                        if not commit:
                            self.stdout.write(
                                f"[DRY RUN] Validated: "
                                f"{defaults['title']} ({anime_id}) "
                                # f"| Characters: {len(characters)}"
                            )
                            continue

                        with transaction.atomic():
                            anime, created = (
                                Anime.objects.update_or_create(
                                    external_id=anime_id,
                                    defaults=defaults,
                                )
                            )

                            # character_objects = []

                            # for character_data in characters:
                            #     character, _ = (
                            #         Character.objects.update_or_create(
                            #             external_id=(
                            #                 character_data["external_id"]
                            #             ),
                            #             defaults={
                            #                 key: value
                            #                 for key, value
                            #                 in character_data.items()
                            #                 if key != "external_id"
                            #             },
                            #         )
                            #     )

                            #     character_objects.append(character)

                            # Set the anime-character relationships.
                            # anime.characters.set(character_objects)

                        if created:
                            total_created += 1
                        else:
                            total_updated += 1

                    except Exception as exc:
                        total_failed += 1
                        failed_records.append(anime_id)

                        self.stderr.write(
                            self.style.ERROR(
                                f"Failed anime {anime_id}: {exc}"
                            )
                        )

                self.stdout.write(
                    f"Processed {total_processed} anime records"
                )

                url = result.get("links", {}).get("next")

                if url:
                    time.sleep(0.5)

        finally:
            session.close()

        self.stdout.write("\n" + "=" * 45)
        self.stdout.write("IMPORT SUMMARY")
        self.stdout.write("=" * 45)

        self.stdout.write(f"Processed: {total_processed}")
        self.stdout.write(f"Failed: {total_failed}")

        if commit:
            self.stdout.write(f"Created: {total_created}")
            self.stdout.write(f"Updated: {total_updated}")

            # self.stdout.write(
            #     f"Unique characters fetched: {len(character_cache)}"
            # )

        if failed_records:
            self.stdout.write(
                self.style.ERROR(
                    f"Failed anime IDs: {', '.join(failed_records)}"
                )
            )

        if not commit:
            self.stdout.write(
                self.style.WARNING(
                    "Dry run completed. No database changes were made."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS("Import completed.")
            )

    @staticmethod
    def create_session():
        """
        Create a requests session with retry handling
        for temporary HTTP failures.
        """
        session = requests.Session()

        retry_strategy = Retry(
            total=5,
            connect=5,
            read=5,
            status=5,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=frozenset(["GET"]),
            respect_retry_after_header=True,
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)

        session.mount("https://", adapter)
        session.mount("http://", adapter)

        session.headers.update({
            "Accept": "application/vnd.api+json",
            "Content-Type": "application/vnd.api+json",
        })

        return session

    @classmethod
    def build_defaults(
        cls,
        session,
        item,
        included,
        # character_cache,
    ):
        """
        Extract and normalize fields from an anime resource.

        Character information is returned separately because
        Anime.characters is a ManyToManyField.
        """
        attributes = item.get("attributes") or {}

        titles = attributes.get("titles")

        if not isinstance(titles, dict):
            titles = {}

        poster = attributes.get("posterImage") or {}
        cover = attributes.get("coverImage") or {}

        title = (
            attributes.get("canonicalTitle")
            or titles.get("en")
            or titles.get("en_jp")
            or titles.get("ja_jp")
            or attributes.get("slug")
            or item.get("id")
            or ""
        )

        abbreviated_titles = attributes.get("abbreviatedTitles")

        if not isinstance(abbreviated_titles, list):
            abbreviated_titles = []

        defaults = {
            # Titles
            "title": title,
            "canonical_title": attributes.get("canonicalTitle") or "",
            "title_en": titles.get("en") or "",
            "title_en_jp": titles.get("en_jp") or "",
            "title_ja_jp": titles.get("ja_jp") or "",
            "abbreviated_titles": abbreviated_titles,
            "localized_titles": titles,

            # General information
            "synopsis": (
                attributes.get("synopsis")
                or attributes.get("description")
                or ""
            ),

            "average_rating": cls.to_decimal(
                attributes.get("averageRating")
            ),

            # Images
            "poster_image_url": poster.get("original") or "",
            "cover_image_url": cover.get("original") or "",

            # Dates
            "start_date": cls.safe_parse_date(
                attributes.get("startDate")
            ),
            "end_date": cls.safe_parse_date(
                attributes.get("endDate")
            ),

            # Other metadata
            "episode_count": cls.to_positive_int(
                attributes.get("episodeCount")
            ),
            "status": attributes.get("status") or "",

            # Relationships
            "genres": cls.get_relationship(
                session, item, "genres", included
            ),
            "categories": cls.get_relationship(
                session, item, "categories", included
            ),

            # Original Kitsu resource
            "raw_data": item,
        }

        # characters = cls.get_characters(
        #     session=session,
        #     item=item,
        #     included=included,
        #     character_cache=character_cache,
        # )
    

        # return defaults, characters
        return defaults

    @staticmethod
    def safe_parse_date(value):
        if not value:
            return None

        try:
            return parse_date(str(value))
        except (ValueError, TypeError, OverflowError):
            return None

    @staticmethod
    def to_positive_int(value):
        if value in (None, ""):
            return None

        try:
            result = int(value)
            return result if result >= 0 else None
        except (ValueError, TypeError, OverflowError):
            return None

    @staticmethod
    def to_decimal(value):
        if value in (None, ""):
            return None

        try:
            return Decimal(str(value))
        except (InvalidOperation, ValueError, TypeError):
            return None

    @classmethod
    def get_relationship(
        cls,
        session,
        item,
        relationship,
        included,
    ):
        """
        Get genres or categories from included resources.

        Fetch the related endpoint if some resources are missing.
        """
        relationship_data = (
            item.get("relationships", {})
            .get(relationship, {})
        )

        resource_ids = relationship_data.get("data")

        if resource_ids == []:
            return []

        if isinstance(resource_ids, dict):
            resource_ids = [resource_ids]

        if resource_ids is not None:
            resources = [
                included.get((resource["type"], resource["id"]))
                for resource in resource_ids
            ]

            if all(resources):
                return [
                    cls.normalize_resource(resource, relationship)
                    for resource in resources
                ]

        related_url = (
            relationship_data.get("links", {}).get("related")
        )

        if not related_url:
            return []

        resources = cls.fetch_related_resources(
            session,
            related_url,
        )

        return [
            cls.normalize_resource(resource, relationship)
            for resource in resources
        ]

    @classmethod
    def get_characters(
        cls,
        session,
        item,
        included,
        character_cache,
    ):
        """
        Identify the characters associated with an anime,
        then retrieve their individual Kitsu resources.
        """
        relationship_data = (
            item.get("relationships", {})
            .get("characters", {})
        )

        resource_ids = relationship_data.get("data")

        # An explicitly empty relationship means no characters.
        if resource_ids == []:
            return []

        if isinstance(resource_ids, dict):
            resource_ids = [resource_ids]

        if resource_ids is None:
            # The API did not include relationship linkage.
            related_url = (
                relationship_data.get("links", {}).get("related")
            )

            if not related_url:
                return []

            resources = cls.fetch_related_resources(
                session,
                related_url,
            )

            resource_ids = [
                {
                    "id": resource.get("id"),
                    "type": resource.get("type", "characters"),
                }
                for resource in resources
                if resource.get("id")
            ]

        characters = []

        for resource_identifier in resource_ids:
            character_id = resource_identifier.get("id")

            if not character_id:
                continue

            included_resource = included.get(
                (
                    resource_identifier.get("type", "characters"),
                    character_id,
                )
            )

            character = cls.get_character_details(
                session=session,
                character_id=character_id,
                included_resource=included_resource,
                character_cache=character_cache,
            )

            if character:
                characters.append(character)

        return characters

    @classmethod
    def get_character_details(
        cls,
        session,
        character_id,
        included_resource,
        character_cache,
    ):
        """
        Retrieve a character from its individual Kitsu endpoint.

        Cache the result to avoid duplicate requests.
        """
        if character_id in character_cache:
            return character_cache[character_id]

        url = (
            f"https://kitsu.io/api/edge/characters/{character_id}"
        )

        try:
            response = session.get(url, timeout=30)
            response.raise_for_status()

            result = response.json()
            resource = result.get("data") or {}

            if not resource:
                raise ValueError(
                    f"No character data returned for {character_id}"
                )

            character = cls.normalize_character(resource)

        except (requests.RequestException, ValueError) as exc:
            # Use the included resource as a fallback if the
            # individual endpoint cannot be retrieved.
            if included_resource:
                character = cls.normalize_character(
                    included_resource
                )
            else:
                raise exc

        character_cache[character_id] = character

        return character

    @staticmethod
    def normalize_character(resource):
        """
        Extract useful character information from Kitsu.
        """
        attributes = resource.get("attributes") or {}

        names = attributes.get("names") or {}

        if not isinstance(names, dict):
            names = {}

        other_names = attributes.get("otherNames") or []

        if not isinstance(other_names, list):
            other_names = []

        image = attributes.get("image") or {}

        if isinstance(image, dict):
            image_url = (
                image.get("large")
                or image.get("original")
                or ""
            )
        elif isinstance(image, str):
            image_url = image
        else:
            image_url = ""

        mal_id = attributes.get("malId")

        try:
            mal_id = int(mal_id) if mal_id else None
        except (ValueError, TypeError, OverflowError):
            mal_id = None

        return {
            "external_id": resource.get("id"),
            "slug": attributes.get("slug") or "",

            "name": (
                attributes.get("name")
                or attributes.get("canonicalName")
                or names.get("en")
                or names.get("en_jp")
                or names.get("ja_jp")
                or ""
            ),

            "canonical_name": (
                attributes.get("canonicalName") or ""
            ),

            "names": names,
            "other_names": other_names,
            "mal_id": mal_id,

            "description": (
                attributes.get("description") or ""
            ),

            "image_url": image_url,
        }

    @staticmethod
    def fetch_related_resources(session, url):
        """
        Fetch all pages from a Kitsu relationship endpoint.
        """
        resources = []

        while url:
            response = session.get(url, timeout=30)
            response.raise_for_status()

            result = response.json()

            resources.extend(result.get("data", []))

            url = result.get("links", {}).get("next")

            if url:
                time.sleep(0.2)

        return resources

    @staticmethod
    def normalize_resource(resource, relationship):
        """
        Normalize genre and category resources.
        """
        attributes = resource.get("attributes") or {}

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
                "description": (
                    attributes.get("description") or ""
                ),
            }

        return attributes