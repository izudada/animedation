from training.models import Anime
from recommendation.services.genre_service import GenreService


anime = Anime.objects.exclude(genres=[]).first()

results = GenreService.recommend(anime)

for result in results:
    print(
        result["anime"].title,
        result["score"],
    )