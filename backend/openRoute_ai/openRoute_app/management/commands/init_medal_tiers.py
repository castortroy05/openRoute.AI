"""
Management command to initialize medal-themed subscription tiers
"""
from django.core.management.base import BaseCommand
from openRoute_app.paywall_models import SubscriptionTier


class Command(BaseCommand):
    help = 'Initialize medal-themed subscription tiers with sensible limits'

    def handle(self, *args, **options):
        self.stdout.write('Creating medal-themed subscription tiers...')

        tiers = [
            {
                'name': 'Bronze Explorer',
                'slug': 'bronze-explorer',
                'medal_tier': 'bronze',
                'description': 'Perfect for getting started with route optimization',
                'tagline': 'Start your journey with essential features',
                'price': 0.00,
                'billing_period': 'free',
                'max_saved_routes': 5,
                'max_daily_uses': 10,
                'allowed_models': 'basic',
                'shows_ads': True,
                'ad_frequency': 2,  # Show ad every 2 requests
                'allows_export': False,
                'allows_advanced_optimization': False,
                'allows_api_access': False,
                'priority_support': False,
                'badge_color': '#CD7F32',  # Bronze
                'icon_emoji': '🥉',
                'is_active': True,
                'is_default': True,
                'is_popular': False,
                'sort_order': 1,
            },
            {
                'name': 'Silver Pathfinder',
                'slug': 'silver-pathfinder',
                'medal_tier': 'silver',
                'description': 'Great for regular users who need more routes and daily uses',
                'tagline': 'Expand your horizons with advanced features',
                'price': 9.99,
                'billing_period': 'monthly',
                'max_saved_routes': 25,
                'max_daily_uses': 50,
                'allowed_models': 'standard',
                'shows_ads': True,
                'ad_frequency': 5,  # Show ad every 5 requests (less frequent)
                'allows_export': True,
                'allows_advanced_optimization': False,
                'allows_api_access': False,
                'priority_support': False,
                'badge_color': '#C0C0C0',  # Silver
                'icon_emoji': '🥈',
                'is_active': True,
                'is_default': False,
                'is_popular': True,  # Most popular!
                'sort_order': 2,
            },
            {
                'name': 'Gold Navigator',
                'slug': 'gold-navigator',
                'medal_tier': 'gold',
                'description': 'For power users who need extensive route planning capabilities',
                'tagline': 'Navigate with precision and unlimited potential',
                'price': 24.99,
                'billing_period': 'monthly',
                'max_saved_routes': 100,
                'max_daily_uses': 150,
                'allowed_models': 'advanced',
                'shows_ads': True,
                'ad_frequency': 10,  # Show ad every 10 requests (minimal)
                'allows_export': True,
                'allows_advanced_optimization': True,
                'allows_api_access': False,
                'priority_support': True,
                'badge_color': '#FFD700',  # Gold
                'icon_emoji': '🥇',
                'is_active': True,
                'is_default': False,
                'is_popular': False,
                'sort_order': 3,
            },
            {
                'name': 'Platinum Voyager',
                'slug': 'platinum-voyager',
                'medal_tier': 'platinum',
                'description': 'Premium tier with unlimited routes and all premium AI models',
                'tagline': 'Voyage without limits - ad-free experience',
                'price': 49.99,
                'billing_period': 'monthly',
                'max_saved_routes': None,  # Unlimited
                'max_daily_uses': None,  # Unlimited
                'allowed_models': 'all',
                'shows_ads': False,  # No ads!
                'ad_frequency': 0,
                'allows_export': True,
                'allows_advanced_optimization': True,
                'allows_api_access': True,
                'priority_support': True,
                'badge_color': '#E5E4E2',  # Platinum
                'icon_emoji': '💎',
                'is_active': True,
                'is_default': False,
                'is_popular': False,
                'sort_order': 4,
            },
            {
                'name': 'Diamond Elite',
                'slug': 'diamond-elite',
                'medal_tier': 'diamond',
                'description': 'Ultimate tier for professional route planners and businesses',
                'tagline': 'Elite performance with lifetime access',
                'price': 499.99,
                'billing_period': 'lifetime',
                'max_saved_routes': None,  # Unlimited
                'max_daily_uses': None,  # Unlimited
                'allowed_models': 'all',
                'shows_ads': False,  # No ads!
                'ad_frequency': 0,
                'allows_export': True,
                'allows_advanced_optimization': True,
                'allows_api_access': True,
                'priority_support': True,
                'badge_color': '#B9F2FF',  # Diamond
                'icon_emoji': '💠',
                'is_active': True,
                'is_default': False,
                'is_popular': False,
                'sort_order': 5,
            },
        ]

        created_count = 0
        updated_count = 0

        for tier_data in tiers:
            tier, created = SubscriptionTier.objects.update_or_create(
                slug=tier_data['slug'],
                defaults=tier_data
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created tier: {tier.name}')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Updated tier: {tier.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nComplete! Created {created_count} tiers, updated {updated_count} tiers.'
            )
        )
        self.stdout.write('\nTier Summary:')
        self.stdout.write('━' * 80)

        for tier in SubscriptionTier.objects.all().order_by('sort_order'):
            routes = tier.max_saved_routes if tier.max_saved_routes else '∞'
            daily = tier.max_daily_uses if tier.max_daily_uses else '∞'
            price_str = 'FREE' if tier.price == 0 else f'${tier.price}/{tier.billing_period}'
            ads_str = f'Ads: Every {tier.ad_frequency}' if tier.shows_ads else 'Ad-Free'

            self.stdout.write(
                f'{tier.icon_emoji} {tier.name:20} | {price_str:15} | Routes: {routes:3} | '
                f'Daily: {daily:3} | Models: {tier.allowed_models:8} | {ads_str}'
            )

        self.stdout.write('━' * 80)
