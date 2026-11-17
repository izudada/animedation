
import uuid

from helpers.base_data_manufacturer import BaseDataManufacture


class AnimeDataManufacture(BaseDataManufacture):
    model_name = "training.Anime"

    @classmethod
    def create_anime(cls, **kwargs):
        model = cls._get_model_class()

        defaults = {
            "external_id": f"test-{uuid.uuid4().hex[:12]}",
            "title": "Test Anime",
            "canonical_title": "Test Anime",
            "synopsis": (
                "A young hero fights powerful enemies "
                "to protect his friends and the world."
            ),
            "average_rating": 85.00,
            "genres": [
                {"id": "1", "name": "Action"},
                {"id": "2", "name": "Adventure"},
            ],
            "categories": [],
            "status": "finished",
        }

        defaults.update(kwargs)

        return model.objects.create(**defaults)
