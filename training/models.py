from django.db import models

from helpers.db_utils import BaseModel


class Character(BaseModel, models.Model):
    external_id = models.CharField(
        max_length=50,
        unique=True,
    )

    slug = models.SlugField(
        max_length=255,
        blank=True,
    )

    name = models.CharField(
        max_length=255,
        blank=True,
    )

    canonical_name = models.CharField(
        max_length=255,
        blank=True,
    )

    names = models.JSONField(default=dict, blank=True)
    other_names = models.JSONField(default=list, blank=True)

    mal_id = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    description = models.TextField(blank=True)

    image_url = models.URLField(blank=True)

    def __str__(self):
        return self.name or self.external_id


class Anime(BaseModel, models.Model):
    external_id = models.CharField(
        max_length=50,
        unique=True,
    )

    # Titles
    title = models.CharField(max_length=255)
    canonical_title = models.CharField(max_length=255, blank=True)
    title_en = models.CharField(max_length=255, blank=True)
    title_en_jp = models.CharField(max_length=255, blank=True)
    title_ja_jp = models.CharField(max_length=255, blank=True)

    abbreviated_titles = models.JSONField(default=list, blank=True)
    localized_titles = models.JSONField(default=dict, blank=True)

    # General information
    synopsis = models.TextField(blank=True)

    average_rating = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )

    # Relationships
    genres = models.JSONField(default=list, blank=True)
    categories = models.JSONField(default=list, blank=True)

    characters = models.ManyToManyField(
        Character,
        related_name="anime",
        blank=True,
    )

    # Images
    poster_image_url = models.URLField(blank=True)
    cover_image_url = models.URLField(blank=True)

    # Dates
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    # Other metadata
    episode_count = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=50, blank=True)

    raw_data = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.title