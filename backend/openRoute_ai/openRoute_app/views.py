from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token 
from django.db import models
from django.conf import settings

# class CustomToken(BaseToken):
#     user = models.OneToOneField(
#         settings.AUTH_USER_MODEL, related_name='auth_token',
#         on_delete=models.CASCADE, verbose_name="User"
#     )

from openRoute_app.serializers import (CustomUserSerializer, PlaceSerializer, ItinerarySerializer,
                          ItineraryPlaceSerializer, OptimizationSerializer, CountrySerializer, CitySerializer)
from .models import CustomUser, Place, Itinerary, ItineraryPlace, Optimization, City, Country

User = get_user_model()

class RegisterView(APIView):
    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data.get('username')
            email = serializer.validated_data.get('email')
            if CustomUser.objects.filter(username=username).exists():
                return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
            if CustomUser.objects.filter(email=email).exists():
                return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)
            user = serializer.save()
            Token.objects.create(user=user)
            return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
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
    
class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    
class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer

# class RegisterView(APIView):
#     def post(self, request):
#         username = request.data.get('username')
#         email = request.data.get('email')
#         password = request.data.get('password')

        
#         # ... other validations

#         user = CustomUser.objects.create_user(
#             username=username,
#             email=email,
#             password=password,

#         )
#         CustomToken.objects.create(user=user)

#         return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
    
def get_flags(request):
    flags = Country.objects.values_list('flag', flat=True)  # Get list of flag filenames
    flags = [str(flag) for flag in flags if flag]  # Convert ImageFields to strings and filter out None values
    return JsonResponse({'flags': flags})
