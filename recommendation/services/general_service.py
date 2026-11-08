from recommendation.enums import RecommendationType
from recommendation.services import GenreService, RatingService
from training.services import AnimeService


class GeneralRecommendationService:
    """Service for handling general recommendations."""

    @classmethod
    def get_recommendations(cls, data):
        recommendation_type = data.get("recommendation_type") 
        anime = AnimeService.get_anime_qs_by_title(
            title=data.get("anime_title"),
            raise_404=False
        ).first()

        if not anime:
            # TODO: call kitsu API to fetch anime details and save it to the database
            pass

        if recommendation_type == RecommendationType.GENRE:
            return GenreService.recommend(anime) 
        if recommendation_type == RecommendationType.RATING:
            return RatingService.recommend(anime)
        else:
            return []