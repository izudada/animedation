from training.services import AnimeService


class GenreService:
    RECOMMENDATION_LIMIT = 10

    @staticmethod
    def extract_genre_ids(genres):
        return {
            genre["id"]
            for genre in genres
            if genre.get("id")
        }

    @staticmethod
    def calculate_genre_similarity(source_genres, candidate_genres):
        matching_genres = source_genres.intersection(candidate_genres)

        return len(matching_genres)

    @staticmethod
    def get_candidate_anime(exclude_anime_id=None):
        queryset = AnimeService.get_anime_qs().exclude(genres=[])

        if exclude_anime_id:
            queryset = queryset.exclude(id=exclude_anime_id)

        return queryset

    @classmethod
    def recommend(cls, anime):
        limit = cls.RECOMMENDATION_LIMIT

        source_genres = cls.extract_genre_ids(anime.genres)

        if not source_genres:
            return {
                "message": "No recommendations available for this anime.",
                "recommendations": [],
            }

        candidates = cls.get_candidate_anime(
            exclude_anime_id=anime.id
        )

        recommendations = []

        for candidate in candidates:
            candidate_genres = cls.extract_genre_ids(
                candidate.genres
            )

            score = cls.calculate_genre_similarity(
                source_genres,
                candidate_genres,
            )

            if score > 0:
                recommendations.append({
                    "anime": candidate.title,
                    "score": score,
                })

        recommendations.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        return recommendations[:limit]