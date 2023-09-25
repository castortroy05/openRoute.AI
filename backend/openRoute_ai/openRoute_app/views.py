from rest_framework import viewsets
from openRoute_app.serializers import (CustomUserSerializer, PlaceSerializer, ItinerarySerializer,
                          ItineraryPlaceSerializer, OptimizationSerializer)
from .models import CustomUser, Place, Itinerary, ItineraryPlace, Optimization


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

class PlaceViewSet(viewsets.ModelViewSet):
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer

class ItineraryViewSet(viewsets.ModelViewSet):
    queryset = Itinerary.objects.all()
    serializer_class = ItinerarySerializer

class ItineraryPlaceViewSet(viewsets.ModelViewSet):
    queryset = ItineraryPlace.objects.all()
    serializer_class = ItineraryPlaceSerializer

class OptimizationViewSet(viewsets.ModelViewSet):
    queryset = Optimization.objects.all()
    serializer_class = OptimizationSerializer
