from django.db import models

from helpers.db_utils import BaseModel



class Anime(BaseModel, models.Model):
    external_id = models.CharField(
        max_length=50,
        unique=True,
    )

    title = models.CharField(max_length=255)
    synopsis = models.TextField(blank=True)

    # Ratings
    average_rating = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )

    # Classification
    genres = models.JSONField(default=list)
    categories = models.JSONField(default=list)

    # Characters and their descriptions
    characters = models.JSONField(default=list)

    # Images
    poster_image_url = models.URLField(blank=True)
    cover_image_url = models.URLField(blank=True)

    # Release information
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    # Additional metadata
    episode_count = models.PositiveIntegerField(
        null=True,
        blank=True,
    )
    status = models.CharField(max_length=50, blank=True)

    # Original Kitsu response
    raw_data = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.title
