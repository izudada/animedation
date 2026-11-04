from django.core.management.base import BaseCommand
from django.db.models import Q

from training.models import Anime, Character


class Command(BaseCommand):
    help = "Health check for the anime data import process."

    def handle(self, *args, **kwargs):

        total_anime_count = Anime.objects.count()
        total_character_count = Character.objects.count()

        checks = {
            "without_synopsis": Q(synopsis="") | Q(synopsis__isnull=True),
            "without_title": Q(title="") | Q(title__isnull=True),
            "without_rating": Q(average_rating__isnull=True),
            "without_poster": Q(poster_image_url="") | Q(poster_image_url__isnull=True),
            "without_genres": Q(genres=[]) | Q(genres__isnull=True),
            "without_categories": Q(categories=[]) | Q(categories__isnull=True),
        }

        results = {
            "total_anime_count": total_anime_count,
            "total_character_count": total_character_count,
        }

        for field, condition in checks.items():
            missing_count = Anime.objects.filter(condition).count()

            results[field] = {
                "count": missing_count,
                "percentage": round(
                    (missing_count / total_anime_count) * 100, 2
                ) if total_anime_count else 0,
            }

        self.stdout.write(str(results))
