"""
Serializers for paywall and subscription management
"""
from rest_framework import serializers
from .paywall_models import (
    SubscriptionTier, UserSubscription, UsageTracking,
    PaymentHistory, FeatureFlag
)


class SubscriptionTierSerializer(serializers.ModelSerializer):
    """Serializer for subscription tiers/plans"""

    class Meta:
        model = SubscriptionTier
        fields = [
            'id', 'name', 'slug', 'description', 'price', 'billing_period',
            'max_places_per_month', 'max_itineraries_per_month',
            'max_ai_requests_per_month', 'allows_export',
            'allows_advanced_optimization', 'allows_api_access',
            'priority_support', 'is_active', 'sort_order'
        ]
        read_only_fields = ['id', 'slug']


class UserSubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for user subscriptions"""
    tier = SubscriptionTierSerializer(read_only=True)
    tier_id = serializers.PrimaryKeyRelatedField(
        queryset=SubscriptionTier.objects.filter(is_active=True),
        source='tier',
        write_only=True
    )
    is_active = serializers.BooleanField(read_only=True)
    is_trial = serializers.BooleanField(read_only=True)
    days_remaining = serializers.IntegerField(read_only=True)

    class Meta:
        model = UserSubscription
        fields = [
            'id', 'user', 'tier', 'tier_id', 'status', 'start_date',
            'end_date', 'trial_end_date', 'auto_renew', 'canceled_at',
            'is_active', 'is_trial', 'days_remaining', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'status', 'start_date', 'end_date',
            'canceled_at', 'created_at', 'updated_at'
        ]


class UsageTrackingSerializer(serializers.ModelSerializer):
    """Serializer for usage tracking records"""

    class Meta:
        model = UsageTracking
        fields = [
            'id', 'user', 'resource_type', 'resource_id', 'quantity',
            'timestamp', 'billing_period_start', 'billing_period_end', 'metadata'
        ]
        read_only_fields = ['id', 'user', 'timestamp', 'billing_period_start', 'billing_period_end']


class UsageSummarySerializer(serializers.Serializer):
    """Serializer for usage summary statistics"""
    resource_type = serializers.CharField()
    current_usage = serializers.IntegerField()
    limit = serializers.IntegerField(allow_null=True)
    percentage_used = serializers.FloatField(allow_null=True)
    unlimited = serializers.BooleanField()


class PaymentHistorySerializer(serializers.ModelSerializer):
    """Serializer for payment history"""

    class Meta:
        model = PaymentHistory
        fields = [
            'id', 'user', 'subscription', 'amount', 'currency', 'status',
            'description', 'metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'status', 'created_at', 'updated_at']


class FeatureFlagSerializer(serializers.ModelSerializer):
    """Serializer for feature flags"""

    class Meta:
        model = FeatureFlag
        fields = ['id', 'name', 'slug', 'description', 'is_enabled']
        read_only_fields = ['id', 'slug']


class SubscriptionCheckoutSerializer(serializers.Serializer):
    """Serializer for subscription checkout requests"""
    tier_id = serializers.IntegerField()
    success_url = serializers.URLField(required=False)
    cancel_url = serializers.URLField(required=False)


class SubscriptionCancelSerializer(serializers.Serializer):
    """Serializer for subscription cancellation"""
    reason = serializers.CharField(required=False, allow_blank=True)
    feedback = serializers.CharField(required=False, allow_blank=True)
