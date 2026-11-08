from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from helpers.utils import paginate_data
from recommendation.serializers import (
    AnimeRecommendationResponseSerializer,
    RecommendationRequestSerializer
)
from recommendation.services.general_service import GeneralRecommendationService


class GeneralRecommendationViewset(viewsets.ViewSet):
    """View for anime recommendations."""

    def list(self, request):
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
