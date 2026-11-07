from rest_framework import serializers

from recommendation.enums.enums import RecommendationType


class RecommendationRequestSerializer(serializers.Serializer):
    anime_title = serializers.CharField(max_length=255, trim_whitespace=True)
    recommendation_type = serializers.ChoiceField(choices=RecommendationType.choices)
