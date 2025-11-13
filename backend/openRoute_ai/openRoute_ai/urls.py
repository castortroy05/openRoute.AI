from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from openRoute_app.views import get_flags
from openRoute_app.views import (CustomUserViewSet, PlaceViewSet, ItineraryViewSet,
                    ItineraryPlaceViewSet, OptimizationViewSet, RegisterView, CountryViewSet, CityViewSet)

router = DefaultRouter()
router.register(r'users', CustomUserViewSet)
router.register(r'places', PlaceViewSet)
router.register(r'itineraries', ItineraryViewSet)
router.register(r'itinerary-places', ItineraryPlaceViewSet)
router.register(r'optimizations', OptimizationViewSet)
router.register(r'countries', CountryViewSet)
router.register(r'cities', CityViewSet)


urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # API endpoints
    path('api/', include(router.urls)),
    path('api/register/', RegisterView.as_view(), name='register'),

    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Debug toolbar
    path("__debug__/", include("debug_toolbar.urls")),

]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
