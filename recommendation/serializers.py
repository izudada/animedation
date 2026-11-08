from rest_framework import serializers

from recommendation.enums.enums import RecommendationType


class RecommendationRequestSerializer(serializers.Serializer):
    anime_title = serializers.CharField(max_length=255, trim_whitespace=True)
    recommendation_type = serializers.ChoiceField(choices=RecommendationType.choices)


class AnimeRecommendationResponseSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    average_rating = serializers.FloatField()
    genres = serializers.ListField(child=serializers.CharField(max_length=100))
