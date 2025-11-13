from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from django.db import transaction
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
import logging

from openRoute_app.serializers import (
    CustomUserSerializer, PlaceSerializer, ItinerarySerializer,
    ItineraryPlaceSerializer, OptimizationSerializer, CountrySerializer, CitySerializer
)
from .models import CustomUser, Place, Itinerary, ItineraryPlace, Optimization, City, Country

User = get_user_model()
logger = logging.getLogger(__name__)


@extend_schema(tags=['Authentication'])
class RegisterView(APIView):
    """
    User registration endpoint
    """
    permission_classes = [AllowAny]

    @extend_schema(
        request=CustomUserSerializer,
        responses={201: CustomUserSerializer, 400: dict},
        description="Register a new user account"
    )
    def post(self, request):
        """Register a new user"""
        try:
            serializer = CustomUserSerializer(data=request.data)

            if not serializer.is_valid():
                logger.warning(f"Registration validation failed: {serializer.errors}")
                return Response(
                    {'error': 'Validation failed', 'details': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )

            username = serializer.validated_data.get('username')
            email = serializer.validated_data.get('email')

            if CustomUser.objects.filter(username=username).exists():
                logger.warning(f"Registration attempt with existing username: {username}")
                return Response(
                    {'error': 'Username already exists'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if CustomUser.objects.filter(email=email).exists():
                logger.warning(f"Registration attempt with existing email: {email}")
                return Response(
                    {'error': 'Email already exists'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            with transaction.atomic():
                user = serializer.save()
                Token.objects.create(user=user)

            logger.info(f"New user registered: {username}")
            return Response(
                {'message': 'User registered successfully', 'user_id': user.id},
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            logger.error(f"Registration error: {str(e)}", exc_info=True)
            return Response(
                {'error': 'An error occurred during registration'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema(tags=['Users'])
class CustomUserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user accounts
    """
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(description="List all users")
    def list(self, request, *args, **kwargs):
        logger.info(f"User list requested by {request.user}")
        return super().list(request, *args, **kwargs)

    @extend_schema(description="Retrieve a specific user")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(description="Update a user")
    def update(self, request, *args, **kwargs):
        logger.info(f"User update requested: {kwargs.get('pk')}")
        return super().update(request, *args, **kwargs)

    @extend_schema(description="Delete a user")
    def destroy(self, request, *args, **kwargs):
        logger.warning(f"User deletion requested: {kwargs.get('pk')} by {request.user}")
        return super().destroy(request, *args, **kwargs)


@extend_schema(tags=['Places'])
class PlaceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing places
    """
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(description="List all places")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(description="Create a new place")
    def create(self, request, *args, **kwargs):
        logger.info(f"Place creation requested by {request.user}")
        return super().create(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def my_places(self, request):
        """Get places created by the authenticated user"""
        places = Place.objects.filter(user=request.user)
        serializer = self.get_serializer(places, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Filter places by type"""
        place_type = request.query_params.get('type')
        if not place_type:
            return Response(
                {'error': 'Place type parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        places = Place.objects.filter(place_type=place_type)
        serializer = self.get_serializer(places, many=True)
        return Response(serializer.data)


@extend_schema(tags=['Itineraries'])
class ItineraryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing itineraries
    """
    queryset = Itinerary.objects.all()
    serializer_class = ItinerarySerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(description="List all itineraries")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(description="Create a new itinerary")
    def create(self, request, *args, **kwargs):
        logger.info(f"Itinerary creation requested by {request.user}")
        return super().create(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def my_itineraries(self, request):
        """Get itineraries created by the authenticated user"""
        itineraries = Itinerary.objects.filter(user=request.user)
        serializer = self.get_serializer(itineraries, many=True)
        return Response(serializer.data)


@extend_schema(tags=['Itinerary Places'])
class ItineraryPlaceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing places within itineraries
    """
    queryset = ItineraryPlace.objects.all()
    serializer_class = ItineraryPlaceSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(description="List all itinerary places")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


@extend_schema(tags=['Optimization'])
class OptimizationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing route optimization preferences
    """
    queryset = Optimization.objects.all()
    serializer_class = OptimizationSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(description="List all optimization preferences")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def my_preferences(self, request):
        """Get optimization preferences for the authenticated user"""
        try:
            optimization = Optimization.objects.get(user=request.user)
            serializer = self.get_serializer(optimization)
            return Response(serializer.data)
        except Optimization.DoesNotExist:
            return Response(
                {'message': 'No optimization preferences found. Please create one.'},
                status=status.HTTP_404_NOT_FOUND
            )


@extend_schema(tags=['Countries'])
class CountryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing countries
    """
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [AllowAny]

    @extend_schema(description="List all countries")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


@extend_schema(tags=['Cities'])
class CityViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing cities
    """
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = [AllowAny]

    @extend_schema(description="List all cities")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def by_country(self, request):
        """Get cities by country"""
        country_id = request.query_params.get('country_id')
        if not country_id:
            return Response(
                {'error': 'Country ID parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        cities = City.objects.filter(country_id=country_id)
        serializer = self.get_serializer(cities, many=True)
        return Response(serializer.data)


def get_flags(request):
    """Get list of country flags"""
    try:
        flags = Country.objects.values_list('flag', flat=True)
        flags = [str(flag) for flag in flags if flag]
        return JsonResponse({'flags': flags})
    except Exception as e:
        logger.error(f"Error fetching flags: {str(e)}", exc_info=True)
        return JsonResponse(
            {'error': 'Failed to fetch flags'},
            status=500
        )
