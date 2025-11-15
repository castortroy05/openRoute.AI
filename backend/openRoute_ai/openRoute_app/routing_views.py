"""
API Views for Routing and Mapping functionality
"""

import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

from .routing_service import get_routing_service
from .osm_accessibility_service import get_osm_accessibility_service
from .models import Place, Itinerary, ItineraryPlace, Optimization

logger = logging.getLogger(__name__)


@extend_schema(
    summary="Get optimized route between places",
    description="Calculate an optimized route between multiple locations with optional accessibility preferences",
    parameters=[
        OpenApiParameter(
            name='place_ids',
            type={'type': 'array', 'items': {'type': 'integer'}},
            location=OpenApiParameter.QUERY,
            description='Comma-separated list of Place IDs to visit',
            required=True
        ),
        OpenApiParameter(
            name='wheelchair_accessible',
            type=OpenApiTypes.BOOL,
            location=OpenApiParameter.QUERY,
            description='Require wheelchair accessible route',
            required=False
        ),
        OpenApiParameter(
            name='avoid_highways',
            type=OpenApiTypes.BOOL,
            location=OpenApiParameter.QUERY,
            description='Avoid highways',
            required=False
        ),
        OpenApiParameter(
            name='avoid_tolls',
            type=OpenApiTypes.BOOL,
            location=OpenApiParameter.QUERY,
            description='Avoid toll roads',
            required=False
        ),
    ],
    responses={
        200: {
            'description': 'Route successfully calculated',
            'content': {
                'application/json': {
                    'example': {
                        'route': {
                            'distance': 15420,
                            'duration': 1240,
                            'geometry': {'type': 'LineString', 'coordinates': [[...]]},
                            'instructions': [...]
                        }
                    }
                }
            }
        }
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def calculate_route(request):
    """
    Calculate an optimized route between user's places.
    """
    # Get place IDs from query params
    place_ids_str = request.query_params.get('place_ids', '')
    if not place_ids_str:
        return Response(
            {'error': 'place_ids parameter is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        place_ids = [int(pid.strip()) for pid in place_ids_str.split(',')]
    except ValueError:
        return Response(
            {'error': 'Invalid place_ids format. Use comma-separated integers.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Get places for the authenticated user
    places = Place.objects.filter(id__in=place_ids, user=request.user)

    if len(places) != len(place_ids):
        return Response(
            {'error': 'Some places not found or do not belong to you'},
            status=status.HTTP_404_NOT_FOUND
        )

    if len(places) < 2:
        return Response(
            {'error': 'At least 2 places are required for routing'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Extract coordinates (longitude, latitude) for each place
    coordinates = [(float(place.longitude), float(place.latitude)) for place in places]

    # Get routing preferences
    wheelchair_accessible = request.query_params.get('wheelchair_accessible', 'false').lower() == 'true'
    avoid_highways = request.query_params.get('avoid_highways', 'false').lower() == 'true'
    avoid_tolls = request.query_params.get('avoid_tolls', 'false').lower() == 'true'

    # Build avoid features list
    avoid_features = []
    if avoid_highways:
        avoid_features.append('highways')
    if avoid_tolls:
        avoid_features.append('tollways')

    # Get routing service and calculate route
    routing_service = get_routing_service()
    route = routing_service.get_route(
        coordinates=coordinates,
        profile='wheelchair' if wheelchair_accessible else 'driving-car',
        preference='fastest',
        avoid_features=avoid_features if avoid_features else None,
        wheelchair_accessible=wheelchair_accessible
    )

    if not route:
        return Response(
            {'error': 'Could not calculate route. Check your API key configuration.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    # Format response
    return Response({
        'route': {
            'distance_meters': route['distance'],
            'distance_km': round(route['distance'] / 1000, 2),
            'duration_seconds': route['duration'],
            'duration_minutes': round(route['duration'] / 60, 2),
            'ascent_meters': route.get('ascent', 0),
            'descent_meters': route.get('descent', 0),
            'geometry': route['geometry'],
            'instructions': route['instructions'],
            'bbox': route['bbox']
        },
        'places': [
            {
                'id': place.id,
                'name': place.name,
                'latitude': float(place.latitude),
                'longitude': float(place.longitude)
            }
            for place in places
        ]
    })


@extend_schema(
    summary="Optimize itinerary order",
    description="Find the optimal order to visit places in an itinerary based on user preferences",
    parameters=[
        OpenApiParameter(
            name='itinerary_id',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='Itinerary ID to optimize',
            required=True
        ),
    ],
    responses={200: {'description': 'Optimized itinerary with new order'}}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def optimize_itinerary_route(request):
    """
    Optimize the order of places in an itinerary for minimum travel time/distance.
    """
    itinerary_id = request.query_params.get('itinerary_id')

    if not itinerary_id:
        return Response(
            {'error': 'itinerary_id parameter is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        itinerary = Itinerary.objects.get(id=itinerary_id, user=request.user)
    except Itinerary.DoesNotExist:
        return Response(
            {'error': 'Itinerary not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Get all places in the itinerary
    itinerary_places = ItineraryPlace.objects.filter(itinerary=itinerary).order_by('order')

    if len(itinerary_places) < 2:
        return Response(
            {'error': 'Itinerary must have at least 2 places'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Get user's optimization preferences
    try:
        optimization_prefs = Optimization.objects.get(user=request.user)
        prefs = {
            'minimize_travel_time': optimization_prefs.minimize_travel_time,
            'minimize_distance': optimization_prefs.minimize_distance,
            'consider_accessibility_requirements': optimization_prefs.consider_accessibility_requirements,
            'avoid_tolls': optimization_prefs.avoid_tolls,
            'avoid_highways': optimization_prefs.avoid_highways
        }
    except Optimization.DoesNotExist:
        prefs = {'minimize_travel_time': True}

    # Extract coordinates
    start_location = (float(itinerary_places[0].place.longitude), float(itinerary_places[0].place.latitude))
    destinations = [
        (float(ip.place.longitude), float(ip.place.latitude))
        for ip in itinerary_places[1:]
    ]

    # Optimize itinerary
    routing_service = get_routing_service()
    optimized = routing_service.optimize_itinerary(
        start_location=start_location,
        destinations=destinations,
        optimization_preferences=prefs
    )

    if not optimized:
        return Response(
            {'error': 'Could not optimize itinerary'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    # Return optimized order
    return Response({
        'itinerary_id': itinerary.id,
        'optimized_order': optimized['optimized_order'],
        'total_distance_meters': optimized['total_distance'],
        'total_distance_km': round(optimized['total_distance'] / 1000, 2),
        'total_duration_seconds': optimized['total_duration'],
        'total_duration_minutes': round(optimized['total_duration'] / 60, 2),
        'message': 'Apply this new order to your itinerary for optimal routing'
    })


@extend_schema(
    summary="Get accessibility features nearby",
    description="Find wheelchair accessible venues, ramps, elevators, and other accessibility features near a location",
    parameters=[
        OpenApiParameter(
            name='latitude',
            type=OpenApiTypes.FLOAT,
            location=OpenApiParameter.QUERY,
            description='Latitude of search center',
            required=True
        ),
        OpenApiParameter(
            name='longitude',
            type=OpenApiTypes.FLOAT,
            location=OpenApiParameter.QUERY,
            description='Longitude of search center',
            required=True
        ),
        OpenApiParameter(
            name='radius',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='Search radius in meters (default: 1000)',
            required=False
        ),
    ],
    responses={200: {'description': 'List of accessibility features nearby'}}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_accessibility_nearby(request):
    """
    Get accessibility features from OpenStreetMap near a location.
    """
    try:
        latitude = float(request.query_params.get('latitude'))
        longitude = float(request.query_params.get('longitude'))
    except (TypeError, ValueError):
        return Response(
            {'error': 'Valid latitude and longitude are required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    radius = int(request.query_params.get('radius', 1000))

    # Get OSM accessibility data
    osm_service = get_osm_accessibility_service()
    features = osm_service.get_accessibility_features_nearby(
        latitude=latitude,
        longitude=longitude,
        radius_meters=radius
    )

    return Response({
        'search_center': {
            'latitude': latitude,
            'longitude': longitude
        },
        'radius_meters': radius,
        'features': features,
        'summary': {
            'wheelchair_accessible_count': len(features.get('wheelchair_accessible', [])),
            'ramps_count': len(features.get('ramps', [])),
            'elevators_count': len(features.get('elevators', [])),
            'tactile_paving_count': len(features.get('tactile_paving', [])),
            'wide_paths_count': len(features.get('wide_paths', []))
        }
    })


@extend_schema(
    summary="Enrich place with OSM accessibility data",
    description="Fetch and update a place with accessibility information from OpenStreetMap",
    parameters=[
        OpenApiParameter(
            name='place_id',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='ID of the place to enrich',
            required=True
        ),
    ],
    responses={200: {'description': 'Place enriched with accessibility data'}}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def enrich_place_accessibility(request):
    """
    Enrich a user's place with accessibility data from OpenStreetMap.
    """
    place_id = request.query_params.get('place_id')

    if not place_id:
        return Response(
            {'error': 'place_id parameter is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        place = Place.objects.get(id=place_id, user=request.user)
    except Place.DoesNotExist:
        return Response(
            {'error': 'Place not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Get OSM accessibility data
    osm_service = get_osm_accessibility_service()
    accessibility_features = osm_service.enrich_place_with_osm_data(
        place_name=place.name,
        latitude=float(place.latitude),
        longitude=float(place.longitude)
    )

    # Update place with new accessibility features
    place.accessibility_features = accessibility_features
    place.save()

    return Response({
        'place_id': place.id,
        'name': place.name,
        'accessibility_features': accessibility_features,
        'message': 'Place enriched with OpenStreetMap accessibility data'
    })
