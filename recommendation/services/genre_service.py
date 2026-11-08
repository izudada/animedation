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
        source_genres = cls.extract_genre_ids(anime.genres)

        if not source_genres:
            return []

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
                    "rating": candidate.average_rating,
                    "genres": [genre["name"] for genre in candidate.genres],
                })

        recommendations.sort(
            key=lambda item: float(item["rating"] or 0),
            reverse=True,
        )

        return recommendations