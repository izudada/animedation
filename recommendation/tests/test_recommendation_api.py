from unittest.mock import patch

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from training.models import Anime


class RecommendationEndpointTests(APITestCase):
    def setUp(self):
        self.anime = Anime.objects.create(
            external_id="source-anime",
            title="Source Anime",
        )
        self.url = reverse("recommendation:recommendations")

    @patch("recommendation.views.recommendation_viewset.GenreService.recommend")
    def test_genre_recommendations_use_genre_service(self, recommend):
        candidate = Anime.objects.create(
            external_id="candidate-anime",
            title="Candidate Anime",
        )
        recommend.return_value = [{"anime": candidate, "score": 2}]

        response = self.client.post(
            self.url,
            {
                "anime_title": "Source Anime",
                "recommendation_type": "genre",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {
                "anime_title": "Source Anime",
                "recommendation_type": "genre",
                "recommendations": [
                    {
                        "id": candidate.id,
                        "title": "Candidate Anime",
                        "score": 2,
                    }
                ],
            },
        )
        recommend.assert_called_once_with(self.anime)

    def test_unsupported_recommendation_type_is_rejected(self):
        response = self.client.post(
            self.url,
            {
                "anime_title": "Source Anime",
                "recommendation_type": "popular",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("recommendation_type", response.data)

    def test_unknown_anime_title_returns_not_found(self):
        response = self.client.post(
            self.url,
            {
                "anime_title": "Missing Anime",
                "recommendation_type": "genre",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
