from django.conf import settings

from helpers.cache_manager import CacheManager
from helpers.custom_logger import CustomLogging
from recommendation.enums import RecommendationType
from recommendation.services import (
    GenreService, 
    RatingService,
    SemanticSynopsisService,
    SynopsisService,
)
from training.services import AnimeService


class GeneralRecommendationService:
    RECOMMENDATION_TTL = 86400 

    """Service for handling general recommendations."""

    @classmethod
    def get_recommendations(cls, data):
        recommendation_type = data.get("recommendation_type") 
        anime_title = data.get("anime_title")
        anime = AnimeService.get_anime_qs_by_title(
            title=anime_title,
            raise_404=False
        ).first()

        cache_key = f"recommendations:{recommendation_type}:{anime.id}"
        cached_recommendations = CacheManager.retrieve_key(cache_key)

        if cached_recommendations is not None:
            return cached_recommendations

        if not anime:
            # TODO: call kitsu API to fetch anime details and save it to the database
            pass

        recommendation = []

        if recommendation_type == RecommendationType.GENRE:
            recommendation = GenreService.recommend(anime) 
        elif recommendation_type == RecommendationType.RATING:
            recommendation = RatingService.recommend(anime)
        elif recommendation_type == RecommendationType.SYNOPSIS:
            recommendation = SynopsisService.recommend(anime)
        elif recommendation_type == RecommendationType.SEMANTIC:
            recommendation = SemanticSynopsisService.recommend(anime)
        else:
            CustomLogging.info(
                message=f"failed to get recommendations for anime: {anime_title}. Invalid recommendation type: {recommendation_type}",
                extra={"anime_title": anime_title, "recommendation_type": recommendation_type},
                send_notification=True
            )
            return recommendation
        
        CacheManager.set_key(
            key=cache_key,
            data=recommendation,
            timeout=cls.RECOMMENDATION_TTL
        )

        return recommendation