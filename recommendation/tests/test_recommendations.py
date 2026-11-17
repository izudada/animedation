
from decimal import Decimal
from types import SimpleNamespace

import pytest

from recommendation.enums import RecommendationType
from recommendation.services import (
    GenreService,
    RatingService,
    SynopsisService,
    GeneralRecommendationService,
)
from training.services import AnimeService


class TestGenreRecommendation:
    """Tests for genre-based anime recommendations."""

    def test_recommends_anime_with_matching_genres(self, make_anime):
        source = make_anime(
            title="Solo Leveling",
            genres=[{"id": "1", "name": "Action"}],
        )

        matching = make_anime(
            title="Attack on Titan",
            genres=[{"id": "1", "name": "Action"}],
            average_rating=Decimal("90.00"),
        )

        unrelated = make_anime(
            title="Romance Anime",
            genres=[{"id": "2", "name": "Romance"}],
            average_rating=Decimal("95.00"),
        )

        recommendations = GenreService.recommend(source)

        recommended_titles = [
            item["anime"] for item in recommendations
        ]

        assert matching.title in recommended_titles
        assert unrelated.title not in recommended_titles

    def test_returns_empty_list_when_source_has_no_genres(self, make_anime):
        source = make_anime(genres=[])

        recommendations = GenreService.recommend(source)

        assert recommendations == []

    def test_excludes_source_anime_from_recommendations(self, make_anime):
        source = make_anime(
            title="Solo Leveling",
            genres=[{"id": "1", "name": "Action"}],
        )

        make_anime(
            title="Attack on Titan",
            genres=[{"id": "1", "name": "Action"}],
        )

        recommendations = GenreService.recommend(source)

        recommended_titles = [
            item["anime"] for item in recommendations
        ]

        assert source.title not in recommended_titles

    def test_orders_recommendations_by_rating(self, make_anime):
        source = make_anime(
            genres=[{"id": "1", "name": "Action"}],
        )

        make_anime(
            title="Anime A",
            genres=[{"id": "1", "name": "Action"}],
            average_rating=Decimal("80.00"),
        )

        make_anime(
            title="Anime B",
            genres=[{"id": "1", "name": "Action"}],
            average_rating=Decimal("95.00"),
        )

        recommendations = GenreService.recommend(source)

        assert recommendations[0]["anime"] == "Anime B"
        assert recommendations[1]["anime"] == "Anime A"


class TestRatingRecommendation:
    """Tests for rating-based anime recommendations."""

    def test_recommends_anime_with_equal_or_higher_rating(self, make_anime):
        source = make_anime(
            title="Source Anime",
            average_rating=Decimal("80.00"),
        )

        higher_rated = make_anime(
            title="Higher Rated Anime",
            average_rating=Decimal("95.00"),
        )

        equally_rated = make_anime(
            title="Equally Rated Anime",
            average_rating=Decimal("80.00"),
        )

        make_anime(
            title="Lower Rated Anime",
            average_rating=Decimal("70.00"),
        )

        recommendations = RatingService.recommend(source)

        recommended_titles = [
            item["anime"] for item in recommendations
        ]

        assert higher_rated.title in recommended_titles
        assert equally_rated.title in recommended_titles
        assert "Lower Rated Anime" not in recommended_titles

    def test_orders_recommendations_by_rating(self, make_anime):
        source = make_anime(
            average_rating=Decimal("70.00"),
        )

        make_anime(
            title="Anime A",
            average_rating=Decimal("80.00"),
        )

        make_anime(
            title="Anime B",
            average_rating=Decimal("95.00"),
        )

        recommendations = RatingService.recommend(source)

        assert recommendations[0]["anime"] == "Anime B"
        assert recommendations[1]["anime"] == "Anime A"

    def test_excludes_source_anime_from_recommendations(self, make_anime):
        source = make_anime(
            title="Source Anime",
            average_rating=Decimal("80.00"),
        )

        recommendations = RatingService.recommend(source)

        recommended_titles = [
            item["anime"] for item in recommendations
        ]

        assert source.title not in recommended_titles


class TestSynopsisRecommendation:
    """Tests for TF-IDF synopsis-based recommendations."""

    def test_recommends_anime_with_similar_synopsis(self, make_anime):
        source = make_anime(
            title="Solo Leveling",
            synopsis=(
                "A young hunter enters dangerous dungeons "
                "to fight monsters and protect humanity."
            ),
        )

        similar = make_anime(
            title="Similar Anime",
            synopsis=(
                "A hunter fights dangerous monsters in dungeons "
                "to protect humanity."
            ),
        )

        unrelated = make_anime(
            title="Unrelated Anime",
            synopsis=(
                "A young chef travels around the world "
                "to discover new recipes and cooking techniques."
            ),
        )

        recommendations = SynopsisService.recommend(source)

        recommended_titles = [
            item["anime"] for item in recommendations
        ]

        assert similar.title in recommended_titles
        assert unrelated.title not in recommended_titles

    def test_returns_most_similar_anime_first(self, make_anime):
        source = make_anime(
            synopsis=(
                "A young hunter fights monsters in dangerous dungeons."
            ),
        )

        make_anime(
            title="Less Similar Anime",
            synopsis=(
                "A young warrior fights enemies in a distant kingdom."
            ),
        )

        make_anime(
            title="Very Similar Anime",
            synopsis=(
                "A young hunter fights powerful monsters "
                "inside dangerous dungeons."
            ),
        )

        recommendations = SynopsisService.recommend(source)

        assert recommendations[0]["anime"] == "Very Similar Anime"

    def test_returns_empty_list_when_source_has_no_synopsis(self, make_anime):
        source = make_anime(synopsis="")

        recommendations = SynopsisService.recommend(source)

        assert recommendations == []

    def test_excludes_source_anime_from_recommendations(self, make_anime):
        source = make_anime(
            title="Source Anime",
            synopsis="A young hero fights monsters to save humanity.",
        )

        recommendations = SynopsisService.recommend(source)

        recommended_titles = [
            item["anime"] for item in recommendations
        ]

        assert source.title not in recommended_titles


class TestGeneralRecommendation:
    """Tests for recommendation type dispatching."""

    @pytest.mark.parametrize(
        "recommendation_type, service",
        [
            (RecommendationType.GENRE, GenreService),
            (RecommendationType.RATING, RatingService),
            (RecommendationType.SYNOPSIS, SynopsisService),
        ],
    )
    def test_calls_correct_recommendation_service(
        self,
        make_anime,
        monkeypatch,
        recommendation_type,
        service,
    ):
        anime = make_anime(title="Solo Leveling")

        expected_result = [{"anime": "Attack on Titan"}]

        # Simulate the anime lookup.
        monkeypatch.setattr(
            AnimeService,
            "get_anime_qs_by_title",
            lambda **kwargs: SimpleNamespace(first=lambda: anime),
        )

        # Simulate the selected recommendation service.
        monkeypatch.setattr(
            service,
            "recommend",
            lambda received_anime: expected_result,
        )

        result = GeneralRecommendationService.get_recommendations({
            "anime_title": "Solo Leveling",
            "recommendation_type": recommendation_type,
        })

        assert result == expected_result

    def test_returns_empty_list_for_invalid_recommendation_type(
        self,
        make_anime,
        monkeypatch,
    ):
        anime = make_anime(title="Solo Leveling")

        monkeypatch.setattr(
            AnimeService,
            "get_anime_qs_by_title",
            lambda **kwargs: SimpleNamespace(first=lambda: anime),
        )

        result = GeneralRecommendationService.get_recommendations({
            "anime_title": "Solo Leveling",
            "recommendation_type": "invalid_type",
        })

        assert result == []
