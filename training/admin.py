from django.contrib import admin

from training.models import Anime


class AnimeAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "title",
        "average_rating",
        "genres",
        "categories",
        "start_date",
        "end_date",
        "created_at"
    ]
    search_fields = [
        "id",
        "title",
    ]


admin.site.register(Anime, AnimeAdmin)
