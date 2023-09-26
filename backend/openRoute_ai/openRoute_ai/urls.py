from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from openRoute_app.views import get_flags
from openRoute_app.views import (CustomUserViewSet, PlaceViewSet, ItineraryViewSet,
                    ItineraryPlaceViewSet, OptimizationViewSet, RegisterView)

router = DefaultRouter()
router.register(r'users', CustomUserViewSet)
router.register(r'places', PlaceViewSet)
router.register(r'itineraries', ItineraryViewSet)
router.register(r'itinerary-places', ItineraryPlaceViewSet)
router.register(r'optimizations', OptimizationViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api/flags/', get_flags, name='get_flags'),
    path('register/', RegisterView.as_view(), name='register'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)