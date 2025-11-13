# OpenRoute.AI Paywall System

## Overview

The OpenRoute.AI paywall system provides a flexible, feature-rich subscription and usage-based billing system that can be easily enabled or disabled. It integrates with Stripe for payment processing and supports multiple subscription tiers with customizable limits.

## Features

- ✅ **Tiered Subscriptions** - Multiple subscription plans with different features and limits
- ✅ **Usage Tracking** - Track resource usage (places, itineraries, AI requests)
- ✅ **Flexible Limits** - Set monthly limits or allow unlimited usage per tier
- ✅ **Feature Flags** - Enable/disable specific features per subscription tier
- ✅ **Stripe Integration** - Full Stripe payment and subscription management
- ✅ **Easy Toggle** - Enable/disable paywall with a single environment variable
- ✅ **Middleware & Decorators** - Simple paywall enforcement on views and endpoints
- ✅ **Comprehensive API** - Full REST API for subscription management

## Configuration

### Environment Variables

Add these to your `.env` file:

```bash
# Enable or disable paywall (default: False)
PAYWALL_ENABLED=False

# Stripe Configuration (required when paywall is enabled)
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# Frontend URL for Stripe redirects
FRONTEND_URL=http://localhost:3000

# Redis for caching (optional but recommended)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

### Enabling the Paywall

1. Set `PAYWALL_ENABLED=True` in your `.env` file
2. Configure your Stripe API keys
3. Run migrations: `python manage.py migrate`
4. Create subscription tiers via Django admin or API
5. (Optional) Set up Stripe webhooks for automatic synchronization

## Subscription Tiers

### Creating Tiers

You can create subscription tiers through:

1. **Django Admin** at `/admin/openRoute_app/subscriptiontier/`
2. **API** at `POST /api/subscription-tiers/`

### Tier Configuration

Each tier includes:

```python
{
    "name": "Pro",
    "slug": "pro",
    "description": "Professional plan with advanced features",
    "price": 29.99,
    "billing_period": "monthly",  # monthly, yearly, lifetime

    # Usage limits (null = unlimited)
    "max_places_per_month": 100,
    "max_itineraries_per_month": 50,
    "max_ai_requests_per_month": 200,

    # Feature flags
    "allows_export": true,
    "allows_advanced_optimization": true,
    "allows_api_access": true,
    "priority_support": true,

    # Stripe IDs (set these after creating products in Stripe)
    "stripe_price_id": "price_xxx",
    "stripe_product_id": "prod_xxx"
}
```

### Example Tier Structure

```python
# Free Tier
{
    "name": "Free",
    "price": 0,
    "max_places_per_month": 10,
    "max_itineraries_per_month": 5,
    "max_ai_requests_per_month": 10,
    "allows_export": false,
    "allows_advanced_optimization": false
}

# Pro Tier
{
    "name": "Pro",
    "price": 29.99,
    "max_places_per_month": 100,
    "max_itineraries_per_month": 50,
    "max_ai_requests_per_month": 200,
    "allows_export": true,
    "allows_advanced_optimization": true
}

# Unlimited Tier
{
    "name": "Unlimited",
    "price": 99.99,
    "max_places_per_month": null,  # Unlimited
    "max_itineraries_per_month": null,
    "max_ai_requests_per_month": null,
    "allows_export": true,
    "allows_advanced_optimization": true,
    "allows_api_access": true
}
```

## Usage in Code

### Protecting Views with Decorators

```python
from openRoute_app.paywall_middleware import (
    require_subscription, require_feature, track_usage
)

# Require active subscription
@require_subscription
def my_view(request):
    # Only users with active subscriptions can access
    pass

# Require specific feature
@require_feature('allows_export')
def export_data(request):
    # Only users with export permission can access
    pass

# Track usage and enforce limits
@track_usage('place', 'max_places_per_month')
def create_place(request):
    # Automatically tracks usage and blocks if limit exceeded
    pass
```

### Using DRF Permission Classes

```python
from rest_framework import viewsets
from openRoute_app.paywall_middleware import (
    HasActiveSubscription, HasFeatureAccess, HasUsageQuota
)

class MyViewSet(viewsets.ModelViewSet):
    permission_classes = [HasActiveSubscription]

    # For usage tracking
    resource_type = 'place'
    tier_limit_field = 'max_places_per_month'


class ExportViewSet(viewsets.ViewSet):
    permission_classes = [HasFeatureAccess]
    required_feature = 'allows_export'
```

### Checking Subscription Programmatically

```python
from openRoute_app.paywall_middleware import (
    is_paywall_enabled, get_user_subscription,
    check_subscription_active, check_feature_access
)

# Check if paywall is enabled
if is_paywall_enabled():
    # Paywall logic
    pass

# Get user's subscription
subscription = get_user_subscription(request.user)

# Check if user has active subscription
if check_subscription_active(request.user):
    # User has active subscription
    pass

# Check feature access
if check_feature_access(request.user, 'allows_export'):
    # User can export
    pass
```

## API Endpoints

### Subscription Management

```bash
# List available subscription tiers
GET /api/subscription-tiers/

# Get specific tier
GET /api/subscription-tiers/{id}/

# Get current user's subscription
GET /api/subscriptions/current/

# Create checkout session
POST /api/subscriptions/create_checkout/
{
    "tier_id": 1,
    "success_url": "http://localhost:3000/success",
    "cancel_url": "http://localhost:3000/cancel"
}

# Cancel subscription
POST /api/subscriptions/cancel_subscription/
{
    "reason": "Too expensive",
    "feedback": "Optional feedback"
}
```

### Usage Tracking

```bash
# Get usage summary for current period
GET /api/usage/summary/

# Response:
{
    "paywall_enabled": true,
    "billing_period_start": "2025-11-01",
    "billing_period_end": "2025-11-30",
    "subscription_tier": "Pro",
    "usage": [
        {
            "resource_type": "place",
            "current_usage": 45,
            "limit": 100,
            "percentage_used": 45.0,
            "unlimited": false
        },
        ...
    ]
}

# Get usage history
GET /api/usage/

# Filter by resource type
GET /api/usage/?resource_type=place
```

### Payment History

```bash
# List all payments
GET /api/payments/

# Get specific payment
GET /api/payments/{id}/
```

### Feature Flags

```bash
# Check paywall status
GET /api/feature-flags/paywall_status/

# List all feature flags
GET /api/feature-flags/
```

## Workflow Examples

### User Subscribing to a Plan

1. User browses available tiers: `GET /api/subscription-tiers/`
2. User selects a tier and creates checkout: `POST /api/subscriptions/create_checkout/`
3. User completes payment on Stripe
4. Stripe webhook updates subscription status
5. User now has access to tier features

### Checking Usage Before Action

```python
from openRoute_app.paywall_middleware import check_usage_limit

def create_place_view(request):
    # Check if user can create more places
    allowed, error_msg = check_usage_limit(
        request.user,
        'place',
        'max_places_per_month'
    )

    if not allowed:
        return JsonResponse({
            'error': error_msg,
            'upgrade_url': '/subscription-tiers/'
        }, status=402)

    # Create place...
    # Usage is automatically tracked by decorator
```

## Database Models

### SubscriptionTier
Defines available subscription plans with limits and features.

### UserSubscription
Tracks user's active subscription, billing period, and status.

### UsageTracking
Records all resource usage for billing period tracking.

### PaymentHistory
Stores payment transaction records.

### FeatureFlag
Global feature toggles for the paywall system.

## Stripe Integration

### Setting Up Stripe

1. Create a Stripe account at https://stripe.com
2. Get your API keys from https://dashboard.stripe.com/apikeys
3. Create products and prices in Stripe dashboard
4. Add Stripe IDs to your subscription tiers

### Webhook Setup

1. Create webhook endpoint in Stripe dashboard
2. Set webhook URL to: `https://yourdomain.com/api/stripe-webhook/`
3. Add webhook secret to `.env`:  `STRIPE_WEBHOOK_SECRET=whsec_xxx`
4. Subscribe to these events:
   - `checkout.session.completed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`

## Migrations

Generate and run migrations for paywall models:

```bash
# Create migrations
python manage.py makemigrations

# Run migrations
python manage.py migrate
```

## Testing

### Testing with Paywall Disabled

```python
# In your .env
PAYWALL_ENABLED=False

# All paywall checks will pass
# No usage limits enforced
# All features available
```

### Testing with Paywall Enabled

```python
# In your .env
PAYWALL_ENABLED=True

# Use Stripe test mode
STRIPE_SECRET_KEY=sk_test_xxx

# Test cards: https://stripe.com/docs/testing
# Success: 4242 4242 4242 4242
# Decline: 4000 0000 0000 0002
```

## Admin Interface

Access Django admin at `/admin/` to manage:

- Subscription Tiers
- User Subscriptions
- Usage Tracking Records
- Payment History
- Feature Flags

## Best Practices

1. **Start with Paywall Disabled** - Test your application without the paywall first
2. **Set Reasonable Limits** - Don't make limits too restrictive
3. **Provide Clear Messaging** - Show users their usage and limits
4. **Test Thoroughly** - Test all subscription flows before going live
5. **Monitor Usage** - Regularly check usage patterns to adjust limits
6. **Offer Free Tier** - Consider a generous free tier to attract users
7. **Stripe Test Mode** - Always test in Stripe test mode first

## Troubleshooting

### Paywall Not Working

```python
# Check if paywall is enabled
if not is_paywall_enabled():
    print("Paywall is disabled in settings")

# Check Stripe configuration
if not settings.STRIPE_SECRET_KEY:
    print("Stripe keys not configured")
```

### User Can't Access Feature

```python
# Check subscription status
subscription = get_user_subscription(user)
if not subscription:
    print("User has no subscription")
elif not subscription.is_active:
    print(f"Subscription status: {subscription.status}")

# Check feature access
has_access = check_feature_access(user, 'allows_export')
print(f"User has export access: {has_access}")
```

### Usage Limit Not Enforcing

```python
# Check tier limit
subscription = get_user_subscription(user)
limit = subscription.tier.max_places_per_month
print(f"Limit: {limit} (None = unlimited)")

# Check current usage
from openRoute_app.paywall_models import UsageTracking
period_start, period_end = UsageTracking.get_current_billing_period()
usage = UsageTracking.get_usage_count(user, 'place', period_start, period_end)
print(f"Current usage: {usage}")
```

## Security Considerations

1. **Validate Stripe Webhooks** - Always verify webhook signatures
2. **Secure API Keys** - Never commit Stripe keys to version control
3. **Rate Limiting** - Implement rate limiting on subscription endpoints
4. **User Verification** - Verify user ownership before subscription operations
5. **Logging** - Log all subscription and payment events
6. **HTTPS Only** - Use HTTPS in production for Stripe callbacks

## Support

For issues or questions:
- Check the Django admin logs
- Review Stripe dashboard for payment issues
- Check application logs for detailed error messages
- Ensure all environment variables are set correctly

## License

This paywall system is part of OpenRoute.AI and follows the project's license.
