
from itertools import islice

from django.conf import settings
from django.core.management.base import BaseCommand
from sentence_transformers import SentenceTransformer

from training.models import Anime


class Command(BaseCommand):
    help = "Generate and save embeddings for anime synopses"

    MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
    BATCH_SIZE = 100

    def add_arguments(self, parser):
        parser.add_argument(
            "--commit",
            type=str,
            default="false",
            choices=["true", "false"],
            help="Commit changes to the database",
        )

    def handle(self, *args, **kwargs):
        commit = kwargs.get("commit") == "true"
        self.stdout.write("Loading embedding model...")

        model = SentenceTransformer(
            self.MODEL_NAME,
            token=settings.HF_TOKEN,
        )

        # Retrieve anime records that have no embeddings yet.
        queryset = (
            Anime.objects
            .filter(synopsis_embedding=[])
            .exclude(synopsis__isnull=True)
            .exclude(synopsis="")
            .order_by("id")
        )

        total = queryset.count()

        if total == 0:
            self.stdout.write(
                self.style.SUCCESS("No anime records need embeddings.")
            )
            return

        self.stdout.write(f"Found {total} anime records.")

        anime_iterator = queryset.iterator(chunk_size=self.BATCH_SIZE)

        processed = 0

        while True:
            batch = list(islice(anime_iterator, self.BATCH_SIZE))

            if not batch:
                break

            # Remove whitespace and prepare synopsis texts.
            valid_anime = [
                anime for anime in batch
                if anime.synopsis and anime.synopsis.strip()
            ]

            if not valid_anime:
                continue

            synopses = [
                anime.synopsis.strip()
                for anime in valid_anime
            ]

            # Generate embeddings for this batch.
            embeddings = model.encode(
                synopses,
                batch_size=32,
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=False,
            )

            # Attach each embedding to its corresponding anime.
            for anime, embedding in zip(valid_anime, embeddings):
                anime.synopsis_embedding = embedding.tolist()

            # Save the batch to PostgreSQL.
            if commit:
                Anime.objects.bulk_update(
                    valid_anime,
                    ["synopsis_embedding"],
                    batch_size=self.BATCH_SIZE,
                )
                self.stdout.write("Batch saved to database.")
            else:
                self.stdout.write("Dry run: batch not saved.")

            processed += len(valid_anime)

            self.stdout.write(
                f"Processed {processed}/{total} anime records."
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully generated embeddings for {processed} anime."
            )
        )
