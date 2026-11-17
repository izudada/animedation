
import pytest

from training.data_manufacturers.anime import AnimeDataManufacture


@pytest.fixture
def make_anime(db):
    def _make(**overrides):
        return AnimeDataManufacture.create_anime(**overrides)

    return _make


@pytest.fixture
def make_action_anime(make_anime):
    def _make(**overrides):
        overrides.setdefault(
            "genres",
            [{"id": "1", "name": "Action"}],
        )

        return make_anime(**overrides)

    return _make


@pytest.fixture
def make_high_rated_anime(make_anime):
    def _make(**overrides):
        overrides.setdefault("average_rating", 95.00)

        return make_anime(**overrides)

    return _make


@pytest.fixture
def make_anime_without_synopsis(make_anime):
    def _make(**overrides):
        overrides.setdefault("synopsis", "")

        return make_anime(**overrides)

    return _make
