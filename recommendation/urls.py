from django.urls import include, path
from rest_framework.routers import DefaultRouter

from recommendation.views.recommendation_viewset import (
    GeneralRecommendationViewset,
)


router = DefaultRouter(trailing_slash=False)

router.register(
    r"recommendations",
    GeneralRecommendationViewset,
    basename="recommendation",
)

urlpatterns = [path("", include(router.urls))]
