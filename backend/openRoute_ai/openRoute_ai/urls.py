from rest_framework.routers import DefaultRouter
from django.urls import path, include
from openRoute_app.views import (CustomUserViewSet, PlaceViewSet, ItineraryViewSet,
                    ItineraryPlaceViewSet, OptimizationViewSet)

router = DefaultRouter()
router.register(r'users', CustomUserViewSet)
router.register(r'places', PlaceViewSet)
router.register(r'itineraries', ItineraryViewSet)
router.register(r'itinerary-places', ItineraryPlaceViewSet)
router.register(r'optimizations', OptimizationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
