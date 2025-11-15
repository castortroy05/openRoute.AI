"""
OpenStreetMap Accessibility Data Integration
Uses Overpass API to query OSM for accessibility information
"""

import logging
import requests
from django.conf import settings
from typing import List, Dict, Optional, Tuple
from django.core.cache import cache

logger = logging.getLogger(__name__)


class OSMAccessibilityService:
    """
    Service for querying OpenStreetMap accessibility data via Overpass API.
    Provides information about wheelchair access, ramps, elevators, and other accessibility features.
    """

    def __init__(self):
        """Initialize Overpass API service."""
        self.overpass_url = getattr(
            settings,
            'OVERPASS_API_URL',
            'https://overpass-api.de/api/interpreter'
        )

    def query_overpass(self, query: str, cache_key: Optional[str] = None, cache_timeout: int = 3600) -> Optional[Dict]:
        """
        Execute Overpass API query with optional caching.

        Args:
            query: Overpass QL query string
            cache_key: Optional cache key for result caching
            cache_timeout: Cache timeout in seconds (default: 1 hour)

        Returns:
            Query results as dictionary
        """
        # Check cache first
        if cache_key:
            cached_result = cache.get(cache_key)
            if cached_result:
                logger.debug(f"Returning cached result for {cache_key}")
                return cached_result

        try:
            response = requests.post(
                self.overpass_url,
                data={'data': query},
                timeout=30
            )
            response.raise_for_status()
            result = response.json()

            # Cache the result
            if cache_key and result:
                cache.set(cache_key, result, cache_timeout)

            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"Overpass API request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Error querying Overpass API: {e}")
            return None

    def get_accessibility_features_nearby(
        self,
        latitude: float,
        longitude: float,
        radius_meters: int = 1000,
        feature_types: Optional[List[str]] = None
    ) -> Dict[str, List[Dict]]:
        """
        Get accessibility features near a location from OpenStreetMap.

        Args:
            latitude: Latitude of center point
            longitude: Longitude of center point
            radius_meters: Search radius in meters (default: 1000m = 1km)
            feature_types: List of feature types to search (wheelchair, ramp, elevator, etc.)

        Returns:
            Dictionary with categorized accessibility features
        """
        if feature_types is None:
            feature_types = ['wheelchair', 'ramp', 'elevator', 'tactile_paving', 'width']

        # Build Overpass QL query
        query = f"""
        [out:json][timeout:25];
        (
          // Wheelchair accessible venues
          node["wheelchair"="yes"](around:{radius_meters},{latitude},{longitude});
          way["wheelchair"="yes"](around:{radius_meters},{latitude},{longitude});

          // Ramps
          node["ramp"="yes"](around:{radius_meters},{latitude},{longitude});
          way["ramp"="yes"](around:{radius_meters},{latitude},{longitude});

          // Elevators
          node["highway"="elevator"](around:{radius_meters},{latitude},{longitude});

          // Tactile paving (for visually impaired)
          node["tactile_paving"="yes"](around:{radius_meters},{latitude},{longitude});
          way["tactile_paving"="yes"](around:{radius_meters},{latitude},{longitude});

          // Wide enough for wheelchairs
          node["width"](around:{radius_meters},{latitude},{longitude});
          way["width"](around:{radius_meters},{latitude},{longitude});
        );
        out body;
        >;
        out skel qt;
        """

        cache_key = f"osm_accessibility_{latitude}_{longitude}_{radius_meters}"
        result = self.query_overpass(query, cache_key)

        if not result or 'elements' not in result:
            return {}

        # Categorize results
        categorized = {
            'wheelchair_accessible': [],
            'ramps': [],
            'elevators': [],
            'tactile_paving': [],
            'wide_paths': []
        }

        for element in result['elements']:
            tags = element.get('tags', {})

            feature_data = {
                'id': element.get('id'),
                'type': element.get('type'),
                'lat': element.get('lat'),
                'lon': element.get('lon'),
                'tags': tags,
                'name': tags.get('name', 'Unknown')
            }

            # Categorize based on tags
            if tags.get('wheelchair') == 'yes':
                categorized['wheelchair_accessible'].append(feature_data)

            if tags.get('ramp') == 'yes' or tags.get('ramp:wheelchair') == 'yes':
                categorized['ramps'].append(feature_data)

            if tags.get('highway') == 'elevator':
                categorized['elevators'].append(feature_data)

            if tags.get('tactile_paving') == 'yes':
                categorized['tactile_paving'].append(feature_data)

            if 'width' in tags:
                try:
                    width = float(tags['width'])
                    if width >= 1.2:  # Minimum wheelchair width (meters)
                        categorized['wide_paths'].append(feature_data)
                except ValueError:
                    pass

        return categorized

    def get_venue_accessibility(
        self,
        latitude: float,
        longitude: float,
        venue_name: Optional[str] = None
    ) -> Dict:
        """
        Get detailed accessibility information for a specific venue.

        Args:
            latitude: Venue latitude
            longitude: Venue longitude
            venue_name: Optional venue name for more accurate matching

        Returns:
            Accessibility details for the venue
        """
        # Search in a small radius (100m) around the venue
        query = f"""
        [out:json][timeout:25];
        (
          node(around:100,{latitude},{longitude});
          way(around:100,{latitude},{longitude});
        );
        out body;
        """

        cache_key = f"venue_accessibility_{latitude}_{longitude}"
        result = self.query_overpass(query, cache_key)

        if not result or 'elements' not in result:
            return {'accessibility_unknown': True}

        accessibility_info = {
            'wheelchair': 'unknown',
            'wheelchair_description': None,
            'entrance': 'unknown',
            'toilets_wheelchair': 'unknown',
            'parking': 'unknown',
            'ramp': 'unknown',
            'elevator': 'unknown',
            'automatic_door': 'unknown',
            'features': []
        }

        # Find the closest matching element
        for element in result['elements']:
            tags = element.get('tags', {})

            # Check if this is the venue we're looking for
            if venue_name and tags.get('name', '').lower() != venue_name.lower():
                continue

            # Extract accessibility tags
            if 'wheelchair' in tags:
                accessibility_info['wheelchair'] = tags['wheelchair']

            if 'wheelchair:description' in tags:
                accessibility_info['wheelchair_description'] = tags['wheelchair:description']

            if 'entrance' in tags:
                accessibility_info['entrance'] = tags.get('entrance')

            if 'toilets:wheelchair' in tags:
                accessibility_info['toilets_wheelchair'] = tags['toilets:wheelchair']

            if 'parking:disabled' in tags or 'capacity:disabled' in tags:
                accessibility_info['parking'] = 'yes'

            if 'ramp' in tags or 'ramp:wheelchair' in tags:
                accessibility_info['ramp'] = 'yes'

            if 'elevator' in tags or tags.get('highway') == 'elevator':
                accessibility_info['elevator'] = 'yes'

            if 'automatic_door' in tags:
                accessibility_info['automatic_door'] = tags['automatic_door']

            # Collect other relevant features
            feature_tags = ['tactile_paving', 'braille', 'hearing_loop', 'description']
            for tag in feature_tags:
                if tag in tags:
                    accessibility_info['features'].append({
                        'type': tag,
                        'value': tags[tag]
                    })

        return accessibility_info

    def enrich_place_with_osm_data(
        self,
        place_name: str,
        latitude: float,
        longitude: float
    ) -> str:
        """
        Enrich a place with accessibility data from OSM and return formatted string.

        Args:
            place_name: Name of the place
            latitude: Latitude coordinate
            longitude: Longitude coordinate

        Returns:
            Formatted accessibility features string for storage in Place model
        """
        accessibility = self.get_venue_accessibility(latitude, longitude, place_name)

        features = []

        if accessibility.get('wheelchair') == 'yes':
            features.append('Wheelchair Accessible')

        if accessibility.get('wheelchair') == 'limited':
            features.append('Limited Wheelchair Access')

        if accessibility.get('ramp') == 'yes':
            features.append('Ramp Available')

        if accessibility.get('elevator') == 'yes':
            features.append('Elevator Available')

        if accessibility.get('automatic_door') == 'yes':
            features.append('Automatic Door')

        if accessibility.get('toilets_wheelchair') == 'yes':
            features.append('Accessible Toilets')

        if accessibility.get('parking') == 'yes':
            features.append('Disabled Parking')

        # Add description if available
        if accessibility.get('wheelchair_description'):
            features.append(f"Note: {accessibility['wheelchair_description']}")

        # Add other features
        for feature in accessibility.get('features', []):
            if feature['value'] == 'yes':
                features.append(feature['type'].replace('_', ' ').title())

        return ', '.join(features) if features else 'Accessibility information not available'


def get_osm_accessibility_service() -> OSMAccessibilityService:
    """Get or create singleton OSMAccessibilityService instance."""
    if not hasattr(get_osm_accessibility_service, '_instance'):
        get_osm_accessibility_service._instance = OSMAccessibilityService()
    return get_osm_accessibility_service._instance
