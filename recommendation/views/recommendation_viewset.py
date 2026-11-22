from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema

from helpers.utils import paginate_data
from recommendation.serializers import (
    AnimeRecommendationResponseSerializer,
    RecommendationRequestSerializer
)
from recommendation.services.general_service import GeneralRecommendationService


class GeneralRecommendationViewset(viewsets.ViewSet):
    """View for anime recommendations."""

    @extend_schema(
        description="Retrieve anime recommendations based on the provided criteria.",
        summary="Get Anime Recommendations",
        tags=["Recommendation"],
        request=RecommendationRequestSerializer,
        responses={
            200: AnimeRecommendationResponseSerializer(many=True),
            400: None,
        },
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="recommend",
    )
    def recommend(self, request):
        """Endpoint for retrieving anime recommendations."""
        serializer = RecommendationRequestSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        recommendations = GeneralRecommendationService.get_recommendations(data=serializer.validated_data)

        if request.GET.get("paginate") == "false":
            return Response(recommendations, status=status.HTTP_200_OK)

        return paginate_data(
            data=recommendations,
            page=request.GET.get("page", 1),
            page_size=request.GET.get("limit", 10)
        )
