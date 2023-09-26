from rest_framework import serializers
from .models import CustomUser, Place, Itinerary, ItineraryPlace, Optimization, Country, City

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'

class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = '__all__'

class ItinerarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Itinerary
        fields = '__all__'

class ItineraryPlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItineraryPlace
        fields = '__all__'

class OptimizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Optimization
        fields = '__all__'
        
class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'
