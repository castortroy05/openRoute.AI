"""
API views for paywall and subscription management
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.conf import settings
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiParameter
import stripe
import logging

from .paywall_models import (
    SubscriptionTier, UserSubscription, UsageTracking,
    PaymentHistory, FeatureFlag
)
from .paywall_serializers import (
    SubscriptionTierSerializer, UserSubscriptionSerializer,
    UsageTrackingSerializer, UsageSummarySerializer,
    PaymentHistorySerializer, FeatureFlagSerializer,
    SubscriptionCheckoutSerializer, SubscriptionCancelSerializer
)
from .paywall_middleware import is_paywall_enabled, get_user_subscription

logger = logging.getLogger(__name__)

# Configure Stripe
stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')


@extend_schema(tags=['Subscription Management'])
class SubscriptionTierViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing available subscription tiers/plans
    """
    queryset = SubscriptionTier.objects.filter(is_active=True)
    serializer_class = SubscriptionTierSerializer
    permission_classes = [AllowAny]

    @extend_schema(description="List all active subscription tiers")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(description="Get details of a specific subscription tier")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


@extend_schema(tags=['Subscription Management'])
class UserSubscriptionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user subscriptions
    """
    serializer_class = UserSubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserSubscription.objects.filter(user=self.request.user)

    @extend_schema(description="Get current user's subscription")
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get the authenticated user's current subscription"""
        if not is_paywall_enabled():
            return Response({
                'paywall_enabled': False,
                'message': 'Paywall is currently disabled. All features are available.'
            })

        subscription = get_user_subscription(request.user)

        if not subscription:
            return Response({
                'paywall_enabled': True,
                'has_subscription': False,
                'message': 'No active subscription found'
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(subscription)
        return Response({
            'paywall_enabled': True,
            'has_subscription': True,
            'subscription': serializer.data
        })

    @extend_schema(
        description="Create checkout session for subscription",
        request=SubscriptionCheckoutSerializer
    )
    @action(detail=False, methods=['post'])
    def create_checkout(self, request):
        """Create a Stripe checkout session for subscription"""
        if not is_paywall_enabled():
            return Response({
                'error': 'Paywall is not enabled'
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = SubscriptionCheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tier_id = serializer.validated_data['tier_id']
        success_url = serializer.validated_data.get('success_url', f"{settings.FRONTEND_URL}/subscription/success")
        cancel_url = serializer.validated_data.get('cancel_url', f"{settings.FRONTEND_URL}/subscription/cancel")

        try:
            tier = SubscriptionTier.objects.get(id=tier_id, is_active=True)

            # Create or get Stripe customer
            subscription = get_user_subscription(request.user)
            if subscription and subscription.stripe_customer_id:
                customer_id = subscription.stripe_customer_id
            else:
                customer = stripe.Customer.create(
                    email=request.user.email,
                    metadata={'user_id': request.user.id}
                )
                customer_id = customer.id

            # Create checkout session
            checkout_session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=['card'],
                line_items=[{
                    'price': tier.stripe_price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    'user_id': request.user.id,
                    'tier_id': tier.id
                }
            )

            return Response({
                'checkout_url': checkout_session.url,
                'session_id': checkout_session.id
            })

        except SubscriptionTier.DoesNotExist:
            return Response({
                'error': 'Invalid subscription tier'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Checkout creation failed: {str(e)}", exc_info=True)
            return Response({
                'error': 'Failed to create checkout session'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        description="Cancel current subscription",
        request=SubscriptionCancelSerializer
    )
    @action(detail=False, methods=['post'])
    def cancel_subscription(self, request):
        """Cancel the user's active subscription"""
        if not is_paywall_enabled():
            return Response({
                'error': 'Paywall is not enabled'
            }, status=status.HTTP_400_BAD_REQUEST)

        subscription = get_user_subscription(request.user)

        if not subscription:
            return Response({
                'error': 'No active subscription found'
            }, status=status.HTTP_404_NOT_FOUND)

        try:
            # Cancel in Stripe if applicable
            if subscription.stripe_subscription_id:
                stripe.Subscription.delete(subscription.stripe_subscription_id)

            # Cancel locally
            subscription.cancel()

            logger.info(f"Subscription canceled for user {request.user.username}")

            return Response({
                'message': 'Subscription canceled successfully',
                'ends_at': subscription.end_date
            })

        except Exception as e:
            logger.error(f"Subscription cancellation failed: {str(e)}", exc_info=True)
            return Response({
                'error': 'Failed to cancel subscription'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(tags=['Usage Tracking'])
class UsageTrackingViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing usage tracking data
    """
    serializer_class = UsageTrackingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UsageTracking.objects.filter(user=self.request.user)

    @extend_schema(description="Get usage summary for current billing period")
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get usage summary for the current billing period"""
        if not is_paywall_enabled():
            return Response({
                'paywall_enabled': False,
                'message': 'Paywall is disabled. No usage limits applied.'
            })

        subscription = get_user_subscription(request.user)

        if not subscription or not subscription.is_active:
            return Response({
                'error': 'No active subscription found'
            }, status=status.HTTP_404_NOT_FOUND)

        period_start, period_end = UsageTracking.get_current_billing_period()

        # Calculate usage for each resource type
        resource_types = [
            ('place', 'max_places_per_month'),
            ('itinerary', 'max_itineraries_per_month'),
            ('ai_request', 'max_ai_requests_per_month'),
        ]

        summary = []
        for resource_type, limit_field in resource_types:
            current_usage = UsageTracking.get_usage_count(
                request.user, resource_type, period_start, period_end
            )
            limit = getattr(subscription.tier, limit_field, None)

            if limit is None:
                percentage = None
                unlimited = True
            else:
                percentage = (current_usage / limit * 100) if limit > 0 else 0
                unlimited = False

            summary.append({
                'resource_type': resource_type,
                'current_usage': current_usage,
                'limit': limit,
                'percentage_used': percentage,
                'unlimited': unlimited
            })

        serializer = UsageSummarySerializer(summary, many=True)

        return Response({
            'paywall_enabled': True,
            'billing_period_start': period_start,
            'billing_period_end': period_end,
            'subscription_tier': subscription.tier.name,
            'usage': serializer.data
        })


@extend_schema(tags=['Payment History'])
class PaymentHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing payment history
    """
    serializer_class = PaymentHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PaymentHistory.objects.filter(user=self.request.user)

    @extend_schema(description="List all payments for the authenticated user")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


@extend_schema(tags=['Feature Flags'])
class FeatureFlagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing feature flags
    """
    queryset = FeatureFlag.objects.all()
    serializer_class = FeatureFlagSerializer
    permission_classes = [AllowAny]

    @extend_schema(description="Check if paywall is enabled")
    @action(detail=False, methods=['get'])
    def paywall_status(self, request):
        """Check if paywall system is enabled"""
        return Response({
            'paywall_enabled': is_paywall_enabled(),
            'stripe_configured': bool(getattr(settings, 'STRIPE_SECRET_KEY', '')),
        })
