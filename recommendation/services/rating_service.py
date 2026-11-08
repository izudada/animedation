from training.services import AnimeService


class RatingService:

    @staticmethod
    def recommend(anime):
        candidates = AnimeService.get_anime_qs(
            average_rating__gte=anime.average_rating,
        ).exclude(
            id=anime.id,
        ).order_by(
            "-average_rating",
        )

        recommendations = []

        for candidate in candidates:
            recommendations.append({
                "anime": candidate.title,
                "rating": candidate.average_rating,
                "score": candidate.average_rating,
            })

        return recommendations
