from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from training.services import AnimeService


class SynopsisService:
    @staticmethod
    def recommend(anime, limit=None):
        """
        Recommend anime based on synopsis similarity using TF-IDF
        and cosine similarity.
        """

        # A source anime without a synopsis cannot be compared.
        if not anime.synopsis or not anime.synopsis.strip():
            return []

        # Get other anime that have synopses.
        candidates = (AnimeService.get_anime_qs(
            ).exclude(
                id=anime.id
            ).exclude(
                synopsis__isnull=True
            ).exclude(
                synopsis=""
            )
        )

        if not candidates.exists():
            return []

        # Keep candidate objects and their synopses in the same order.
        candidate_list = list(candidates)

        # Put the selected anime's synopsis first.
        synopses = [
            anime.synopsis,
            *[candidate.synopsis for candidate in candidate_list],
        ]

        # Convert synopses into TF-IDF vectors.
        vectorizer = TfidfVectorizer(stop_words="english")
        tfidf_matrix = vectorizer.fit_transform(synopses)

        # Compare the selected anime against every candidate.
        similarity_scores = cosine_similarity(
            tfidf_matrix[0:1],
            tfidf_matrix[1:],
        )[0]

        recommendations = []

        for candidate, score in zip(candidate_list, similarity_scores):
            if score > 0:
                recommendations.append({
                    "id": candidate.id,
                    "anime": candidate.title,
                    "score": float(score),
                })

        # Rank recommendations from highest to lowest similarity.
        recommendations.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        return recommendations