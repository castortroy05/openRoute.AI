from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework.authtoken.models import Token

class RegisterView(APIView):
    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')

        if not username or not email or not password:
            return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, email=email, password=password)
        Token.objects.create(user=user)

        return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)

from openRoute_app.serializers import (CustomUserSerializer, PlaceSerializer, ItinerarySerializer,
                          ItineraryPlaceSerializer, OptimizationSerializer)
from .models import CustomUser, Place, Itinerary, ItineraryPlace, Optimization, City, Country


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

class RegisterView(APIView):
    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')

        
        # ... other validations

        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password,

        )
        Token.objects.create(user=user)

        return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
    
def get_flags(request):
    flags = Country.objects.values_list('flag', flat=True)  # Get list of flag filenames
    flags = [str(flag) for flag in flags if flag]  # Convert ImageFields to strings and filter out None values
    return JsonResponse({'flags': flags})
