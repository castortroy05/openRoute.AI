"""
OpenRouteService Routing Integration
Provides route optimization with accessibility support using OpenRouteService API
"""

import logging
import openrouteservice
from openrouteservice import convert
from django.conf import settings
from typing import List, Dict, Optional, Tuple
from decimal import Decimal

logger = logging.getLogger(__name__)


class RoutingService:
    """
    Service for routing and navigation using OpenRouteService.
    Supports wheelchair-accessible routing and various optimization preferences.
    """

    def __init__(self):
        """Initialize OpenRouteService client with API key."""
        api_key = getattr(settings, 'OPENROUTESERVICE_API_KEY', None)
        if not api_key or api_key == 'your-openrouteservice-api-key-here':
            logger.warning("OpenRouteService API key not configured. Routing features will be limited.")
            self.client = None
        else:
            self.client = openrouteservice.Client(key=api_key)

    def get_route(
        self,
        coordinates: List[Tuple[float, float]],
        profile: str = 'driving-car',
        preference: str = 'fastest',
        avoid_features: Optional[List[str]] = None,
        wheelchair_accessible: bool = False
    ) -> Optional[Dict]:
        """
        Get an optimized route between multiple coordinates.

        Args:
            coordinates: List of (longitude, latitude) tuples
            profile: Transportation profile (driving-car, foot-walking, wheelchair, cycling-regular)
            preference: Route preference (fastest, shortest, recommended)
            avoid_features: Features to avoid (highways, tollways, ferries, fords, steps)
            wheelchair_accessible: If True, use wheelchair profile

        Returns:
            Route data with geometry, distance, duration, and turn-by-turn directions
        """
        if not self.client:
            logger.error("OpenRouteService client not initialized. Check API key configuration.")
            return None

        try:
            # Use wheelchair profile if accessibility is required
            if wheelchair_accessible:
                profile = 'wheelchair'
                if avoid_features is None:
                    avoid_features = ['steps']
                elif 'steps' not in avoid_features:
                    avoid_features.append('steps')

            # Prepare request parameters
            params = {
                'coordinates': coordinates,
                'profile': profile,
                'format': 'geojson',
                'preference': preference,
                'instructions': True,
                'elevation': True,
                'extra_info': ['waytype', 'surface', 'steepness']
            }

            # Add avoid features if specified
            if avoid_features:
                params['options'] = {'avoid_features': avoid_features}

            # Make API request
            route = self.client.directions(**params)

            if not route or 'features' not in route or len(route['features']) == 0:
                logger.warning("No route found for given coordinates")
                return None

            # Extract route information
            feature = route['features'][0]
            properties = feature['properties']

            return {
                'geometry': feature['geometry'],  # GeoJSON LineString
                'distance': properties['summary']['distance'],  # meters
                'duration': properties['summary']['duration'],  # seconds
                'ascent': properties.get('ascent', 0),  # meters
                'descent': properties.get('descent', 0),  # meters
                'instructions': properties.get('segments', [{}])[0].get('steps', []),
                'waypoints': properties.get('way_points', []),
                'bbox': route.get('bbox', [])
            }

        except openrouteservice.exceptions.ApiError as e:
            logger.error(f"OpenRouteService API error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error getting route: {e}")
            return None

    def optimize_itinerary(
        self,
        start_location: Tuple[float, float],
        destinations: List[Tuple[float, float]],
        end_location: Optional[Tuple[float, float]] = None,
        optimization_preferences: Optional[Dict] = None
    ) -> Optional[Dict]:
        """
        Optimize the order of destinations for an itinerary.

        Args:
            start_location: Starting point (longitude, latitude)
            destinations: List of destination coordinates
            end_location: Optional end location (returns to start if not specified)
            optimization_preferences: Dict with minimize_travel_time, avoid_tolls, etc.

        Returns:
            Optimized itinerary with reordered destinations and route information
        """
        if not self.client:
            logger.error("OpenRouteService client not initialized.")
            return None

        try:
            # Build coordinate list
            coordinates = [start_location] + destinations
            if end_location:
                coordinates.append(end_location)
            else:
                coordinates.append(start_location)  # Return to start

            # Determine preferences
            prefs = optimization_preferences or {}
            profile = 'driving-car'
            preference = 'fastest' if prefs.get('minimize_travel_time', True) else 'shortest'
            avoid_features = []

            if prefs.get('avoid_tolls', False):
                avoid_features.append('tollways')
            if prefs.get('avoid_highways', False):
                avoid_features.append('highways')
            if prefs.get('consider_accessibility_requirements', False):
                profile = 'wheelchair'
                avoid_features.append('steps')

            # Use optimization endpoint to find best order
            optimization = self.client.optimization(
                jobs=[
                    {
                        'id': i,
                        'location': list(coord),
                        'service': 300  # 5 minutes service time at each location
                    }
                    for i, coord in enumerate(destinations, 1)
                ],
                vehicles=[{
                    'id': 1,
                    'profile': profile,
                    'start': list(start_location),
                    'end': list(end_location) if end_location else list(start_location)
                }]
            )

            if not optimization or 'routes' not in optimization:
                logger.warning("No optimization result found")
                return None

            route = optimization['routes'][0]

            return {
                'optimized_order': [step['job'] for step in route['steps'] if step['type'] == 'job'],
                'total_distance': route['distance'],  # meters
                'total_duration': route['duration'],  # seconds
                'steps': route['steps']
            }

        except Exception as e:
            logger.error(f"Error optimizing itinerary: {e}")
            return None

    def get_isochrones(
        self,
        location: Tuple[float, float],
        range_seconds: List[int] = [300, 600, 900],  # 5, 10, 15 minutes
        profile: str = 'driving-car',
        wheelchair_accessible: bool = False
    ) -> Optional[Dict]:
        """
        Get isochrones (reachability areas) from a location.
        Useful for showing "places within X minutes" on a map.

        Args:
            location: Starting location (longitude, latitude)
            range_seconds: List of time ranges in seconds
            profile: Transportation profile
            wheelchair_accessible: Use wheelchair profile if True

        Returns:
            GeoJSON with polygon features for each time range
        """
        if not self.client:
            logger.error("OpenRouteService client not initialized.")
            return None

        try:
            if wheelchair_accessible:
                profile = 'wheelchair'

            isochrones = self.client.isochrones(
                locations=[location],
                profile=profile,
                range_type='time',
                range=range_seconds
            )

            return isochrones

        except Exception as e:
            logger.error(f"Error getting isochrones: {e}")
            return None


def get_routing_service() -> RoutingService:
    """Get or create singleton RoutingService instance."""
    if not hasattr(get_routing_service, '_instance'):
        get_routing_service._instance = RoutingService()
    return get_routing_service._instance
