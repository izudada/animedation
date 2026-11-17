
from django.apps import apps


class BaseDataManufacture:
    model_name = ""

    @classmethod
    def _get_model_class(cls):
        """
        Retrieve a Django model using its app label and model name.
        Example: training.Anime
        """
        if not cls.model_name or "." not in cls.model_name:
            raise ValueError(
                "model_name must be in the format 'app_label.ModelName'"
            )

        app_label, model_name = cls.model_name.split(".", 1)

        return apps.get_model(app_label, model_name)
