from helpers.cache_manager import CacheManager
from recommendation.enums import RecommendationType
from recommendation.services import (
    GenreService, 
    RatingService,
    SynopsisService
)
from training.services import AnimeService


class GeneralRecommendationService:
    RECOMMENDATION_TTL = 86400 

    """Service for handling general recommendations."""

    @classmethod
    def get_recommendations(cls, data):
        recommendation_type = data.get("recommendation_type") 
        anime = AnimeService.get_anime_qs_by_title(
            title=data.get("anime_title"),
            raise_404=False
        ).first()

        cache_key = f"recommendations:{recommendation_type}:{anime.id}"
        cached_recommendations = CacheManager.retrieve_key(cache_key)

        if cached_recommendations is not None:
            return cached_recommendations

        if not anime:
            # TODO: call kitsu API to fetch anime details and save it to the database
            pass

        if recommendation_type == RecommendationType.GENRE:
            recommendation = GenreService.recommend(anime) 
        elif recommendation_type == RecommendationType.RATING:
            recommendation = RatingService.recommend(anime)
        elif recommendation_type == RecommendationType.SYNOPSIS:
            recommendation = SynopsisService.recommend(anime)
        else:
            recommendation = []

        CacheManager.set_key(
            key=cache_key,
            value=recommendation,
            timeout=cls.RECOMMENDATION_TTL
        )

        return recommendation