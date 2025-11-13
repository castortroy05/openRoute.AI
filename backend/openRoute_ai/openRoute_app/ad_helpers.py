"""
Ad display helpers for OpenRoute.AI
Handles discreet ad integration with Google AdSense and other providers
"""
from django.conf import settings
from .paywall_models import UserSubscription, UsageTracking, AdImpression
from .paywall_middleware import is_paywall_enabled, get_user_subscription
import logging
import uuid

logger = logging.getLogger(__name__)


def should_show_ad(user):
    """
    Determine if an ad should be shown to the user based on their tier
    Returns: (should_show: bool, tier_name: str, ad_frequency: int)
    """
    if not is_paywall_enabled():
        return False, 'paywall_disabled', 0

    if not user.is_authenticated:
        # Show ads to anonymous users
        return True, 'anonymous', 1

    subscription = get_user_subscription(user)

    if not subscription or not subscription.is_active:
        # Show ads to users without subscription
        return True, 'no_subscription', 1

    tier = subscription.tier

    if not tier.shows_ads:
        # Tier has ads disabled (premium tiers)
        return False, tier.name, 0

    if tier.ad_frequency == 0:
        # No ads for this tier
        return False, tier.name, 0

    # Check request count to determine if we should show ad based on frequency
    # For example, if ad_frequency = 3, show ad every 3rd request
    today_count = UsageTracking.get_daily_usage_count(user, 'route_optimization')

    if today_count % tier.ad_frequency == 0:
        return True, tier.name, tier.ad_frequency

    return False, tier.name, tier.ad_frequency


def get_ad_config(user):
    """
    Get ad configuration for the user
    Returns ad provider settings and unit IDs
    """
    should_display, tier_name, frequency = should_show_ad(user)

    if not should_display:
        return {
            'show_ad': False,
            'tier_name': tier_name,
            'reason': 'tier_disabled' if tier_name != 'paywall_disabled' else 'paywall_disabled'
        }

    # Get ad provider settings from Django settings
    ad_provider = getattr(settings, 'AD_PROVIDER', 'google_adsense')
    ad_client_id = getattr(settings, 'GOOGLE_ADSENSE_CLIENT_ID', '')
    ad_slot_id = getattr(settings, 'GOOGLE_ADSENSE_SLOT_ID', '')

    return {
        'show_ad': True,
        'tier_name': tier_name,
        'ad_frequency': frequency,
        'provider': ad_provider,
        'client_id': ad_client_id,
        'slot_id': ad_slot_id,
        'format': 'auto',  # Responsive
        'layout': 'in-article',  # Discreet in-article layout
    }


def track_ad_impression(user, page_url, ad_unit_id=None):
    """
    Track when an ad is displayed to a user
    """
    try:
        subscription = get_user_subscription(user) if user.is_authenticated else None
        user_tier = subscription.tier.name if subscription else 'anonymous'

        impression = AdImpression.objects.create(
            user=user if user.is_authenticated else None,
            ad_provider=getattr(settings, 'AD_PROVIDER', 'google_adsense'),
            ad_unit_id=ad_unit_id or '',
            impression_id=str(uuid.uuid4()),
            page_url=page_url,
            user_tier=user_tier
        )

        # Also track as usage
        if user.is_authenticated:
            UsageTracking.track_usage(
                user=user,
                resource_type='ad_view',
                metadata={'impression_id': impression.impression_id}
            )

        logger.info(f"Ad impression tracked: {impression.impression_id} for {user_tier}")
        return impression.impression_id

    except Exception as e:
        logger.error(f"Failed to track ad impression: {str(e)}", exc_info=True)
        return None


def track_ad_click(impression_id):
    """
    Track when an ad is clicked
    """
    try:
        impression = AdImpression.objects.get(impression_id=impression_id)
        impression.was_clicked = True
        impression.clicked_at = timezone.now()
        impression.save()

        logger.info(f"Ad click tracked: {impression_id}")
        return True

    except AdImpression.DoesNotExist:
        logger.warning(f"Ad impression not found: {impression_id}")
        return False
    except Exception as e:
        logger.error(f"Failed to track ad click: {str(e)}", exc_info=True)
        return False


def get_ad_placement_config():
    """
    Get configuration for different ad placements
    Returns recommended placements for discreet ad integration
    """
    return {
        'header': {
            'enabled': False,  # Don't show header ads (too intrusive)
            'format': 'horizontal',
            'max_height': '90px',
        },
        'sidebar': {
            'enabled': True,
            'format': 'vertical',
            'width': '300px',
            'style': 'minimal',  # Minimal, discreet style
        },
        'in_content': {
            'enabled': True,
            'format': 'in-article',
            'frequency': 'per_section',  # One ad per content section
            'style': 'native',  # Native ad format (blends with content)
        },
        'footer': {
            'enabled': True,
            'format': 'horizontal',
            'max_height': '100px',
            'style': 'minimal',
        },
    }


def get_google_adsense_script():
    """
    Generate Google AdSense script tag
    """
    client_id = getattr(settings, 'GOOGLE_ADSENSE_CLIENT_ID', '')

    if not client_id:
        return ''

    return f'''
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={client_id}"
     crossorigin="anonymous"></script>
    '''.strip()


def get_google_adsense_unit(slot_id, format='auto', layout='', layout_key=''):
    """
    Generate Google AdSense ad unit HTML
    """
    client_id = getattr(settings, 'GOOGLE_ADSENSE_CLIENT_ID', '')

    if not client_id or not slot_id:
        return ''

    layout_attrs = ''
    if layout:
        layout_attrs += f' data-ad-layout="{layout}"'
    if layout_key:
        layout_attrs += f' data-ad-layout-key="{layout_key}"'

    return f'''
<ins class="adsbygoogle"
     style="display:block"
     data-ad-client="{client_id}"
     data-ad-slot="{slot_id}"
     data-ad-format="{format}"
     data-full-width-responsive="true"{layout_attrs}></ins>
<script>
     (adsbygoogle = window.adsbygoogle || []).push({{}});
</script>
    '''.strip()


def get_ad_blocker_message():
    """
    Get a polite message for users with ad blockers
    """
    return {
        'title': 'Help Support OpenRoute.AI',
        'message': 'We noticed you\'re using an ad blocker. Ads help us provide free features. '
                   'Consider upgrading to a premium plan for an ad-free experience!',
        'cta_text': 'View Premium Plans',
        'cta_link': '/subscription-tiers/',
        'dismiss_text': 'Maybe later',
    }


class AdDisplayContext:
    """
    Context processor for ad display in templates
    """
    def __init__(self, request):
        self.request = request
        self.user = request.user

    def get_context(self):
        """Get ad display context for templates"""
        ad_config = get_ad_config(self.user)

        return {
            'ads': {
                'enabled': ad_config.get('show_ad', False),
                'provider': ad_config.get('provider', ''),
                'config': ad_config,
                'script': get_google_adsense_script() if ad_config.get('show_ad') else '',
                'placements': get_ad_placement_config(),
                'ad_blocker_message': get_ad_blocker_message(),
            }
        }
