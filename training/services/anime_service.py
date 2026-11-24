from helpers.exceptions import CustomAPIException
from training.models import Anime


class AnimeService:
    @staticmethod
    def get_anime_by_id(anime_id):
        anime =  Anime.objects.get(id=anime_id)
        if not anime:
            raise CustomAPIException(f"Anime does not exist.", status_code=404)
        return anime

    @staticmethod
    def get_anime_qs(*args, **kwargs):
        return Anime.objects.filter(*args, **kwargs)

    @staticmethod
    def get_anime_qs_by_title(title, raise_404=True):
        anime_qs = Anime.objects.filter(title__icontains=title)
        if not anime_qs and raise_404:
            raise CustomAPIException(f"Anime with title '{title}' does not exist.", status_code=404)
        return anime_qs
