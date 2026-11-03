from django.contrib import admin

from training.models import Anime, Character


class AnimeAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "title",
        "average_rating",
        "start_date",
        "end_date",
        "created_at"
    ]
    search_fields = [
        "id",
        "title",
    ]


class CharacterAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "slug",
        "canonical_name",
        "mal_id",
        "created_at"
    ]
    search_fields = [
        "id",
        "name",
        "mal_id"
    ]


admin.site.register(Anime, AnimeAdmin)
admin.site.register(Character, CharacterAdmin)
