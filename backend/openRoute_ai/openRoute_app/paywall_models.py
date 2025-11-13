"""
Paywall and subscription models for OpenRoute.AI
Supports tiered subscriptions and usage-based billing
"""
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from datetime import timedelta
from .models import CustomUser


class SubscriptionTier(models.Model):
    """
    Subscription tier/plan definition
    Can be enabled/disabled via PAYWALL_ENABLED setting
    """
    BILLING_PERIOD_CHOICES = [
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
        ('lifetime', 'Lifetime'),
    ]

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField()

    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    billing_period = models.CharField(max_length=20, choices=BILLING_PERIOD_CHOICES, default='monthly')

    # Stripe integration
    stripe_price_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_product_id = models.CharField(max_length=255, blank=True, null=True)

    # Features and limits
    max_places_per_month = models.IntegerField(
        null=True,
        blank=True,
        help_text="Maximum places that can be created per month. Null = unlimited"
    )
    max_itineraries_per_month = models.IntegerField(
        null=True,
        blank=True,
        help_text="Maximum itineraries per month. Null = unlimited"
    )
    max_ai_requests_per_month = models.IntegerField(
        null=True,
        blank=True,
        help_text="Maximum AI-powered optimization requests per month. Null = unlimited"
    )

    # Feature flags
    allows_export = models.BooleanField(default=False)
    allows_advanced_optimization = models.BooleanField(default=False)
    allows_api_access = models.BooleanField(default=False)
    priority_support = models.BooleanField(default=False)

    # Metadata
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sort_order', 'price']
        verbose_name = 'Subscription Tier'
        verbose_name_plural = 'Subscription Tiers'

    def __str__(self):
        return f"{self.name} (${self.price}/{self.billing_period})"

    def save(self, *args, **kwargs):
        # Ensure only one default tier
        if self.is_default:
            SubscriptionTier.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)


class UserSubscription(models.Model):
    """
    User's active subscription
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('canceled', 'Canceled'),
        ('expired', 'Expired'),
        ('trial', 'Trial'),
        ('past_due', 'Past Due'),
    ]

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='subscription')
    tier = models.ForeignKey(SubscriptionTier, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    # Stripe integration
    stripe_subscription_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)

    # Subscription period
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    trial_end_date = models.DateTimeField(null=True, blank=True)

    # Auto-renewal
    auto_renew = models.BooleanField(default=True)
    canceled_at = models.DateTimeField(null=True, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Subscription'
        verbose_name_plural = 'User Subscriptions'

    def __str__(self):
        return f"{self.user.username} - {self.tier.name} ({self.status})"

    @property
    def is_active(self):
        """Check if subscription is currently active"""
        if self.status == 'canceled' or self.status == 'expired':
            return False
        if self.end_date and timezone.now() > self.end_date:
            return False
        return True

    @property
    def is_trial(self):
        """Check if user is in trial period"""
        if self.trial_end_date and timezone.now() < self.trial_end_date:
            return True
        return False

    @property
    def days_remaining(self):
        """Calculate days remaining in subscription"""
        if not self.end_date:
            return None
        delta = self.end_date - timezone.now()
        return max(0, delta.days)

    def cancel(self):
        """Cancel the subscription"""
        self.status = 'canceled'
        self.canceled_at = timezone.now()
        self.auto_renew = False
        self.save()

    def renew(self, duration_days=30):
        """Renew the subscription"""
        if self.end_date:
            self.end_date = self.end_date + timedelta(days=duration_days)
        else:
            self.end_date = timezone.now() + timedelta(days=duration_days)
        self.status = 'active'
        self.save()


class UsageTracking(models.Model):
    """
    Track user resource usage for billing and limits
    """
    RESOURCE_TYPES = [
        ('place', 'Place Created'),
        ('itinerary', 'Itinerary Created'),
        ('ai_request', 'AI Optimization Request'),
        ('api_call', 'API Call'),
        ('export', 'Data Export'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='usage_records')
    resource_type = models.CharField(max_length=50, choices=RESOURCE_TYPES)
    resource_id = models.IntegerField(null=True, blank=True)

    # Usage details
    quantity = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    timestamp = models.DateTimeField(auto_now_add=True)

    # Billing period tracking
    billing_period_start = models.DateField()
    billing_period_end = models.DateField()

    # Metadata
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = 'Usage Tracking'
        verbose_name_plural = 'Usage Tracking'
        indexes = [
            models.Index(fields=['user', 'resource_type', 'billing_period_start']),
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.resource_type} at {self.timestamp}"

    @staticmethod
    def get_current_billing_period():
        """Get current month's billing period"""
        today = timezone.now().date()
        start = today.replace(day=1)

        # Calculate last day of month
        if today.month == 12:
            end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)

        return start, end

    @staticmethod
    def track_usage(user, resource_type, resource_id=None, quantity=1, metadata=None):
        """Track a usage event"""
        start, end = UsageTracking.get_current_billing_period()

        return UsageTracking.objects.create(
            user=user,
            resource_type=resource_type,
            resource_id=resource_id,
            quantity=quantity,
            billing_period_start=start,
            billing_period_end=end,
            metadata=metadata or {}
        )

    @staticmethod
    def get_usage_count(user, resource_type, period_start=None, period_end=None):
        """Get total usage count for a resource type in a period"""
        if not period_start or not period_end:
            period_start, period_end = UsageTracking.get_current_billing_period()

        return UsageTracking.objects.filter(
            user=user,
            resource_type=resource_type,
            billing_period_start=period_start,
            billing_period_end=period_end
        ).aggregate(total=models.Sum('quantity'))['total'] or 0


class PaymentHistory(models.Model):
    """
    Record of all payments
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='payments')
    subscription = models.ForeignKey(UserSubscription, on_delete=models.SET_NULL, null=True, blank=True)

    # Payment details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Stripe integration
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_charge_id = models.CharField(max_length=255, blank=True, null=True)

    # Metadata
    description = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Payment History'
        verbose_name_plural = 'Payment History'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - ${self.amount} ({self.status})"


class FeatureFlag(models.Model):
    """
    Global feature flags to enable/disable paywall features
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField()
    is_enabled = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Feature Flag'
        verbose_name_plural = 'Feature Flags'

    def __str__(self):
        return f"{self.name} ({'Enabled' if self.is_enabled else 'Disabled'})"

    @staticmethod
    def is_feature_enabled(slug):
        """Check if a feature is enabled"""
        try:
            flag = FeatureFlag.objects.get(slug=slug)
            return flag.is_enabled
        except FeatureFlag.DoesNotExist:
            return False
