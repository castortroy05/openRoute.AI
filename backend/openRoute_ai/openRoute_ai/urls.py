from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

# Main app views
from openRoute_app.views import (
    CustomUserViewSet, PlaceViewSet, ItineraryViewSet,
    ItineraryPlaceViewSet, OptimizationViewSet, RegisterView,
    CountryViewSet, CityViewSet, get_flags
)

# Paywall views
from openRoute_app.paywall_views import (
    SubscriptionTierViewSet, UserSubscriptionViewSet,
    UsageTrackingViewSet, PaymentHistoryViewSet, FeatureFlagViewSet
)

# Routing and mapping views
from openRoute_app.routing_views import (
    calculate_route, optimize_itinerary_route,
    get_accessibility_nearby, enrich_place_accessibility
)

router = DefaultRouter()

# Main API routes
router.register(r'users', CustomUserViewSet)
router.register(r'places', PlaceViewSet)
router.register(r'itineraries', ItineraryViewSet)
router.register(r'itinerary-places', ItineraryPlaceViewSet)
router.register(r'optimizations', OptimizationViewSet)
router.register(r'countries', CountryViewSet)
router.register(r'cities', CityViewSet)

# Paywall/Subscription routes
router.register(r'subscription-tiers', SubscriptionTierViewSet, basename='subscription-tier')
router.register(r'subscriptions', UserSubscriptionViewSet, basename='user-subscription')
router.register(r'usage', UsageTrackingViewSet, basename='usage-tracking')
router.register(r'payments', PaymentHistoryViewSet, basename='payment-history')
router.register(r'feature-flags', FeatureFlagViewSet, basename='feature-flag')


urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # API endpoints
    path('api/', include(router.urls)),
    path('api/register/', RegisterView.as_view(), name='register'),

    # Routing and Mapping endpoints
    path('api/routing/calculate/', calculate_route, name='calculate-route'),
    path('api/routing/optimize-itinerary/', optimize_itinerary_route, name='optimize-itinerary'),
    path('api/accessibility/nearby/', get_accessibility_nearby, name='accessibility-nearby'),
    path('api/accessibility/enrich-place/', enrich_place_accessibility, name='enrich-place'),

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
