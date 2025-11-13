"""
Paywall middleware and decorators for OpenRoute.AI
"""
from functools import wraps
from django.conf import settings
from django.http import JsonResponse
from rest_framework import status
from .paywall_models import UserSubscription, UsageTracking, FeatureFlag
import logging

logger = logging.getLogger(__name__)


def is_paywall_enabled():
    """Check if paywall is globally enabled"""
    return getattr(settings, 'PAYWALL_ENABLED', False)


def get_user_subscription(user):
    """Get user's active subscription or None"""
    try:
        return UserSubscription.objects.select_related('tier').get(user=user)
    except UserSubscription.DoesNotExist:
        return None


def check_subscription_active(user):
    """Check if user has an active subscription"""
    if not is_paywall_enabled():
        return True

    subscription = get_user_subscription(user)
    if not subscription:
        return False

    return subscription.is_active


def check_usage_limit(user, resource_type, tier_limit_field):
    """Check if user has exceeded their usage limit"""
    if not is_paywall_enabled():
        return True, None

    subscription = get_user_subscription(user)
    if not subscription or not subscription.is_active:
        return False, "No active subscription"

    # Get tier limit
    limit = getattr(subscription.tier, tier_limit_field, None)

    # None means unlimited
    if limit is None:
        return True, None

    # Get current usage
    period_start, period_end = UsageTracking.get_current_billing_period()
    current_usage = UsageTracking.get_usage_count(
        user, resource_type, period_start, period_end
    )

    if current_usage >= limit:
        return False, f"Usage limit exceeded. Limit: {limit}, Current: {current_usage}"

    return True, None


def check_feature_access(user, feature_flag_field):
    """Check if user's subscription tier allows a feature"""
    if not is_paywall_enabled():
        return True

    subscription = get_user_subscription(user)
    if not subscription or not subscription.is_active:
        return False

    return getattr(subscription.tier, feature_flag_field, False)


def require_subscription(view_func):
    """
    Decorator to require an active subscription
    Usage: @require_subscription
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not is_paywall_enabled():
            return view_func(request, *args, **kwargs)

        if not request.user.is_authenticated:
            return JsonResponse(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not check_subscription_active(request.user):
            return JsonResponse(
                {
                    'error': 'Active subscription required',
                    'message': 'Please subscribe to access this feature',
                    'paywall': True
                },
                status=status.HTTP_402_PAYMENT_REQUIRED
            )

        return view_func(request, *args, **kwargs)

    return wrapper


def require_feature(feature_flag_field):
    """
    Decorator to require a specific feature from subscription tier
    Usage: @require_feature('allows_export')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not is_paywall_enabled():
                return view_func(request, *args, **kwargs)

            if not request.user.is_authenticated:
                return JsonResponse(
                    {'error': 'Authentication required'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            if not check_feature_access(request.user, feature_flag_field):
                return JsonResponse(
                    {
                        'error': 'Feature not available in your plan',
                        'message': f'Please upgrade your subscription to access this feature',
                        'required_feature': feature_flag_field,
                        'paywall': True
                    },
                    status=status.HTTP_402_PAYMENT_REQUIRED
                )

            return view_func(request, *args, **kwargs)

        return wrapper
    return decorator


def track_usage(resource_type, tier_limit_field):
    """
    Decorator to track and enforce usage limits
    Usage: @track_usage('place', 'max_places_per_month')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not is_paywall_enabled():
                return view_func(request, *args, **kwargs)

            if not request.user.is_authenticated:
                return JsonResponse(
                    {'error': 'Authentication required'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            # Check usage limit before allowing action
            allowed, error_message = check_usage_limit(
                request.user, resource_type, tier_limit_field
            )

            if not allowed:
                logger.warning(
                    f"Usage limit exceeded for user {request.user.username}: {error_message}"
                )
                return JsonResponse(
                    {
                        'error': 'Usage limit exceeded',
                        'message': error_message,
                        'paywall': True
                    },
                    status=status.HTTP_402_PAYMENT_REQUIRED
                )

            # Execute the view
            response = view_func(request, *args, **kwargs)

            # Track usage if request was successful (201 or 200)
            if response.status_code in [200, 201]:
                try:
                    resource_id = None
                    if hasattr(response, 'data') and isinstance(response.data, dict):
                        resource_id = response.data.get('id')

                    UsageTracking.track_usage(
                        user=request.user,
                        resource_type=resource_type,
                        resource_id=resource_id
                    )
                    logger.info(
                        f"Tracked {resource_type} usage for user {request.user.username}"
                    )
                except Exception as e:
                    logger.error(f"Failed to track usage: {str(e)}", exc_info=True)

            return response

        return wrapper
    return decorator


class PaywallMiddleware:
    """
    Middleware to add subscription info to all authenticated requests
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Add subscription info to request if user is authenticated
        if hasattr(request, 'user') and request.user.is_authenticated:
            if is_paywall_enabled():
                subscription = get_user_subscription(request.user)
                request.subscription = subscription
                request.has_active_subscription = subscription.is_active if subscription else False
            else:
                request.subscription = None
                request.has_active_subscription = True

        response = self.get_response(request)
        return response


# DRF permission classes
from rest_framework.permissions import BasePermission


class HasActiveSubscription(BasePermission):
    """
    DRF permission class to check for active subscription
    """
    message = 'Active subscription required to access this endpoint'

    def has_permission(self, request, view):
        if not is_paywall_enabled():
            return True

        if not request.user.is_authenticated:
            return False

        return check_subscription_active(request.user)


class HasFeatureAccess(BasePermission):
    """
    DRF permission class to check for specific feature access
    Set feature_flag_field in view class
    """
    message = 'Your subscription plan does not include this feature'

    def has_permission(self, request, view):
        if not is_paywall_enabled():
            return True

        if not request.user.is_authenticated:
            return False

        feature_flag_field = getattr(view, 'required_feature', None)
        if not feature_flag_field:
            return True

        return check_feature_access(request.user, feature_flag_field)


class HasUsageQuota(BasePermission):
    """
    DRF permission class to check usage quotas
    Set resource_type and tier_limit_field in view class
    """
    message = 'Usage limit exceeded for this resource'

    def has_permission(self, request, view):
        if not is_paywall_enabled():
            return True

        if not request.user.is_authenticated:
            return False

        # Only check on creation (POST)
        if request.method != 'POST':
            return True

        resource_type = getattr(view, 'resource_type', None)
        tier_limit_field = getattr(view, 'tier_limit_field', None)

        if not resource_type or not tier_limit_field:
            return True

        allowed, error_message = check_usage_limit(
            request.user, resource_type, tier_limit_field
        )

        if not allowed:
            self.message = error_message

        return allowed
