from recommendation.services.genre_service import GenreService

from recommendation.enums import RecommendationType
from training.services import AnimeService


class GeneralRecommendationService:
    """Service for handling general recommendations."""

    @classmethod
    def get_recommendations(cls, data):
        if data.get("recommendation_type") == RecommendationType.GENRE:
            anime = AnimeService.get_anime_qs_by_title(data.get("anime_title")).first()
            return GenreService.recommend(anime) 