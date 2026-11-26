
import numpy as np

from training.services import AnimeService


class SemanticSynopsisService:
    """
    Recommend anime using semantic similarity between synopsis embeddings.
    """

    DEFAULT_LIMIT = 10
    BATCH_SIZE = 500

    @staticmethod
    def recommend(anime, limit=None):
        if not anime.synopsis_embedding:
            return []

        limit = limit or SemanticSynopsisService.DEFAULT_LIMIT

        # Convert the selected anime's embedding into a NumPy array.
        source_embedding = np.asarray(
            anime.synopsis_embedding,
            dtype=np.float32,
        )

        # Retrieve other anime that have stored embeddings.
        candidates = (
            AnimeService.get_anime_qs()
            .exclude(id=anime.id)
            .exclude(synopsis_embedding=[])
            .exclude(synopsis_embedding__isnull=True)
            .only("id", "title", "synopsis_embedding")
            .order_by("id")
        )

        scored_anime = []

        # Process candidates in batches to avoid loading every vector
        # into memory at once.
        iterator = candidates.iterator(
            chunk_size=SemanticSynopsisService.BATCH_SIZE
        )

        for candidate in iterator:
            candidate_embedding = np.asarray(
                candidate.synopsis_embedding,
                dtype=np.float32,
            )

            # Ignore embeddings with an unexpected dimension.
            if candidate_embedding.shape != source_embedding.shape:
                continue

            # Embeddings were normalized during generation.
            # Their dot product gives cosine similarity.
            score = float(
                np.dot(source_embedding, candidate_embedding)
            )

            scored_anime.append({
                "id": candidate.id,
                "anime": candidate.title,
                "score": score,
            })

        # Highest similarity first.
        scored_anime.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        return scored_anime[:limit]
