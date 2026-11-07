from recommendation.services.genre_service import GenreService

from recommendation.enums import RecommendationType
from training.services import AnimeService


class GeneralRecommendationService:
    """Service for handling general recommendations."""

    @classmethod
    def get_recommendations(cls, data):
        if data.get("recommendation_type") == RecommendationType.GENRE:
            anime = AnimeService.get_anime_qs_by_title(
                title=data.get("anime_title"),
                raise_404=False
            ).first()

            if not anime:
                # TODO: call kitsu API to fetch anime details and save it to the database
                pass
            
            return GenreService.recommend(anime) 