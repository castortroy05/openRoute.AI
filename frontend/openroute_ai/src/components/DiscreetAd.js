import React, { useEffect, useState } from 'react';
import './DiscreetAd.css';

/**
 * DiscreetAd Component
 * Displays Google AdSense ads in a discreet, non-intrusive manner
 * Only shows for users on lower subscription tiers
 */
const DiscreetAd = ({ placement = 'sidebar', className = '' }) => {
  const [adConfig, setAdConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [adBlockDetected, setAdBlockDetected] = useState(false);

  useEffect(() => {
    // Fetch ad configuration from API
    fetchAdConfig();

    // Detect ad blocker
    detectAdBlocker();
  }, []);

  const fetchAdConfig = async () => {
    try {
      const response = await fetch('/api/feature-flags/paywall_status/', {
        headers: {
          'Authorization': `Token ${localStorage.getItem('authToken')}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setAdConfig(data);
      }
    } catch (error) {
      console.error('Failed to fetch ad config:', error);
    } finally {
      setLoading(false);
    }
  };

  const detectAdBlocker = () => {
    // Simple ad blocker detection
    const testAd = document.createElement('div');
    testAd.innerHTML = '&nbsp;';
    testAd.className = 'adsbox';
    testAd.style.position = 'absolute';
    testAd.style.width = '1px';
    testAd.style.height = '1px';

    document.body.appendChild(testAd);

    setTimeout(() => {
      if (testAd.offsetHeight === 0) {
        setAdBlockDetected(true);
      }
      document.body.removeChild(testAd);
    }, 100);
  };

  const loadAdSenseScript = () => {
    const clientId = process.env.REACT_APP_ADSENSE_CLIENT_ID;

    if (!clientId || document.querySelector(`script[data-ad-client="${clientId}"]`)) {
      return;
    }

    const script = document.createElement('script');
    script.src = `https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=${clientId}`;
    script.async = true;
    script.crossOrigin = 'anonymous';
    script.setAttribute('data-ad-client', clientId);

    document.head.appendChild(script);
  };

  useEffect(() => {
    if (!loading && adConfig && adConfig.show_ad) {
      loadAdSenseScript();

      // Initialize AdSense
      setTimeout(() => {
        try {
          (window.adsbygoogle = window.adsbygoogle || []).push({});
        } catch (e) {
          console.error('AdSense error:', e);
        }
      }, 100);
    }
  }, [loading, adConfig]);

  if (loading) {
    return null; // Don't show anything while loading
  }

  // Don't show ads if paywall is disabled or user has premium tier
  if (!adConfig || !adConfig.show_ad) {
    return null;
  }

  // Show upgrade message for ad blocker users
  if (adBlockDetected) {
    return (
      <div className={`discreet-ad ad-blocked ${className}`}>
        <div className="ad-message">
          <p className="ad-message-title">✨ Enjoying OpenRoute.AI?</p>
          <p className="ad-message-text">
            Upgrade to a premium plan for an ad-free experience
          </p>
          <a href="/subscription-tiers" className="ad-upgrade-btn">
            View Plans
          </a>
        </div>
      </div>
    );
  }

  const getAdDimensions = () => {
    switch (placement) {
      case 'sidebar':
        return { width: '300', height: '250' };
      case 'footer':
        return { width: '728', height: '90' };
      case 'in-content':
        return { width: 'auto', height: 'auto', format: 'fluid', layout: 'in-article' };
      default:
        return { width: '300', height: '250' };
    }
  };

  const dims = getAdDimensions();
  const clientId = process.env.REACT_APP_ADSENSE_CLIENT_ID;
  const slotId = process.env.REACT_APP_ADSENSE_SLOT_ID;

  if (!clientId || !slotId) {
    return null; // Don't show if not configured
  }

  return (
    <div className={`discreet-ad ad-${placement} ${className}`}>
      <span className="ad-label">Ad</span>
      <ins
        className="adsbygoogle"
        style={{ display: 'block' }}
        data-ad-client={clientId}
        data-ad-slot={slotId}
        data-ad-format={dims.format || 'auto'}
        data-full-width-responsive="true"
        {...(dims.layout && { 'data-ad-layout': dims.layout })}
      />
    </div>
  );
};

export default DiscreetAd;
