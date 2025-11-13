# Medal-Themed Subscription Tiers

## Overview

OpenRoute.AI uses a medal-themed subscription system with five tiers designed to encourage usage while providing value at every level. The system focuses on three key limits:

1. **Saved Routes** - Maximum number of routes that can be saved
2. **Daily Uses** - Maximum route optimizations per calendar day
3. **AI Models** - Which AI models are accessible

Lower tiers include discreet ad support to supplement revenue, while premium tiers offer an ad-free experience.

## Tier Structure

### 🥉 Bronze Explorer (FREE)
**Perfect for getting started**

- **Price**: Free forever
- **Saved Routes**: 5 routes
- **Daily Uses**: 10 optimizations per day
- **AI Models**: Basic models only
- **Ads**: Yes (every 2 requests)
- **Features**:
  - Basic route optimization
  - Community support
  - Standard features

**Target Audience**: New users, casual planners, trying out the service

---

### 🥈 Silver Pathfinder ($9.99/month) ⭐ MOST POPULAR
**Great for regular users**

- **Price**: $9.99/month
- **Saved Routes**: 25 routes
- **Daily Uses**: 50 optimizations per day
- **AI Models**: Standard models
- **Ads**: Yes (every 5 requests - less frequent)
- **Features**:
  - Export functionality
  - Priority email support
  - Advanced filtering

**Target Audience**: Regular users, frequent travelers, small businesses

---

### 🥇 Gold Navigator ($24.99/month)
**For power users**

- **Price**: $24.99/month
- **Saved Routes**: 100 routes
- **Daily Uses**: 150 optimizations per day
- **AI Models**: Advanced models
- **Ads**: Minimal (every 10 requests)
- **Features**:
  - Export functionality
  - Advanced optimization algorithms
  - Priority support
  - Custom routing preferences

**Target Audience**: Power users, logistics companies, professional planners

---

### 💎 Platinum Voyager ($49.99/month)
**Premium ad-free experience**

- **Price**: $49.99/month
- **Saved Routes**: Unlimited
- **Daily Uses**: Unlimited
- **AI Models**: All models including premium
- **Ads**: None - completely ad-free!
- **Features**:
  - Everything in Gold
  - API access
  - Premium AI models
  - Priority support
  - White-label options

**Target Audience**: Businesses, agencies, developers, professionals

---

### 💠 Diamond Elite ($499.99 lifetime)
**Ultimate lifetime access**

- **Price**: $499.99 one-time payment
- **Saved Routes**: Unlimited
- **Daily Uses**: Unlimited
- **AI Models**: All models including premium
- **Ads**: None - completely ad-free!
- **Features**:
  - Everything in Platinum
  - Lifetime access (no recurring fees)
  - Early access to new features
  - Dedicated account manager
  - Custom integrations

**Target Audience**: Enterprise, long-term users, committed organizations

---

## Comparison Table

| Feature | Bronze | Silver | Gold | Platinum | Diamond |
|---------|--------|--------|------|----------|---------|
| **Price** | Free | $9.99/mo | $24.99/mo | $49.99/mo | $499.99 lifetime |
| **Saved Routes** | 5 | 25 | 100 | ∞ | ∞ |
| **Daily Uses** | 10 | 50 | 150 | ∞ | ∞ |
| **AI Models** | Basic | Standard | Advanced | All | All |
| **Ads** | Every 2 | Every 5 | Every 10 | None | None |
| **Export** | ❌ | ✅ | ✅ | ✅ | ✅ |
| **Advanced Optimization** | ❌ | ❌ | ✅ | ✅ | ✅ |
| **API Access** | ❌ | ❌ | ❌ | ✅ | ✅ |
| **Priority Support** | ❌ | ❌ | ✅ | ✅ | ✅ |
| **Lifetime Access** | ❌ | ❌ | ❌ | ❌ | ✅ |

---

## Ad Integration

### Design Philosophy
Ads are integrated discreetly to avoid disrupting the user experience while providing revenue for lower tiers.

### Ad Frequency
- **Bronze**: Ad shown every 2 route optimizations
- **Silver**: Ad shown every 5 route optimizations
- **Gold**: Ad shown every 10 route optimizations
- **Platinum+**: No ads

### Ad Placement
Ads are shown in:
- Sidebar (300x250 - discreet, minimal)
- In-content areas (native format, blends with content)
- Footer (728x90 - minimal)

**Never shown**:
- Header areas (too intrusive)
- Popup/interstitial ads
- Auto-playing video ads

### Ad Providers
- **Primary**: Google AdSense
- **Format**: Responsive, native ads
- **Style**: Minimal, blends with UI
- **User Control**: Clear "Ad" label, ability to upgrade

---

## Usage Tracking

### Daily Limits
Limits reset at midnight (user's timezone):
- Prevents abuse
- Encourages daily engagement
- Smooth out usage patterns

### Saved Routes
Counted cumulatively:
- User can delete routes to free up space
- Premium tiers have unlimited storage
- Helps understand user needs

### AI Model Access

**Basic Models**:
- Standard routing algorithms
- Fast processing
- Good for simple routes

**Standard Models**:
- Enhanced algorithms
- Better accuracy
- Multi-stop optimization

**Advanced Models**:
- Premium algorithms
- Machine learning optimization
- Complex routing scenarios

**All Models** (Platinum/Diamond):
- Everything above
- Experimental features
- Beta model access

---

## Encouraging Upgrades

### Progressive Value
Each tier provides meaningful improvements:
- Bronze: Prove the value
- Silver: Regular usage without frustration
- Gold: Power user capabilities
- Platinum: Professional/business use
- Diamond: Lifetime commitment

### Transparent Limits
Users see their usage clearly:
- Dashboard shows current usage
- Warnings at 80% of limits
- Clear upgrade paths
- No surprise lockouts

### Ad Fatigue Strategy
Lower tiers show ads, but:
- Never intrusive
- Clear upgrade messaging
- Ad-free as upgrade benefit
- "Support us or upgrade" approach

---

## Implementation

### Initializing Tiers

```bash
# Run this command to create all tiers
python manage.py init_medal_tiers
```

### Checking User Limits

```python
from openRoute_app.paywall_middleware import check_daily_usage

# Check if user can make request
can_optimize = check_daily_usage(user, 'route_optimization')
```

### Displaying Ads

```jsx
import DiscreetAd from './components/DiscreetAd';

<DiscreetAd placement="sidebar" />
```

---

## Monetization Strategy

### Revenue Sources

1. **Subscriptions** (Primary)
   - Silver: $9.99/mo = ~70% target revenue
   - Gold: $24.99/mo = ~20% target revenue
   - Platinum: $49.99/mo = ~8% target revenue
   - Diamond: $499.99 lifetime = ~2% target revenue

2. **Ads** (Supplementary)
   - Bronze users (ad every 2 requests)
   - Silver users (ad every 5 requests)
   - Gold users (ad every 10 requests)
   - Estimated: 10-15% of total revenue

### Conversion Funnel

1. **Free tier** (Bronze) → Prove value
2. **Light ads** → Show what ad-free looks like
3. **Usage limits** → Encourage upgrade when needed
4. **Clear value** → Show what they get
5. **Easy upgrade** → One-click Stripe checkout

---

## Best Practices

### For Users

1. **Start with Bronze** - Try the service free
2. **Track your usage** - See if you need more
3. **Upgrade when needed** - Don't hit limits
4. **Go ad-free** - Platinum for best experience
5. **Lifetime access** - Diamond for long-term

### For Administrators

1. **Monitor conversion rates** - Track Bronze → Silver
2. **Adjust limits** - Based on usage patterns
3. **A/B test pricing** - Find optimal price points
4. **Survey users** - Understand pain points
5. **Seasonal promotions** - Boost conversions

---

## FAQ

**Q: Can I upgrade mid-month?**
A: Yes! You'll be charged a prorated amount and limits increase immediately.

**Q: What happens if I downgrade?**
A: Saved routes over your new limit are hidden but not deleted. Upgrade again to restore access.

**Q: Are ads personalized?**
A: We use Google AdSense which may show personalized ads based on their policy. You can opt out in your browser.

**Q: Can I try Platinum before buying?**
A: Yes! We offer a 7-day trial of Platinum features.

**Q: Do daily limits carry over?**
A: No, daily limits reset at midnight each day.

**Q: Can businesses get custom plans?**
A: Yes! Contact us for enterprise pricing and custom limits.

---

## Future Enhancements

- Team/multi-user plans
- Volume discounts for enterprises
- Affiliate/referral program
- Usage analytics dashboard
- Custom branding options (white-label)
- Priority route processing for premium tiers
- Dedicated support channels

---

## Support

For questions about tiers or upgrades:
- Email: support@openroute.ai
- In-app chat (Platinum+ users)
- Documentation: docs.openroute.ai

---

*Last updated: 2025-11-13*
