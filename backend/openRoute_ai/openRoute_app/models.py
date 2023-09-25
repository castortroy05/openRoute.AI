from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class CustomUser(AbstractUser):
    #specify user dietary preferences
    DIETARY_CHOICES = [
        ('V', 'Vegetarian'),
        ('VG', 'Vegan'),
        ('GF', 'Gluten-Free'),
        ('N', 'None'),
        ('K', 'Kosher'),
        ('H', 'Halal'),
        ('B', 'Bland'),
        ('P', 'Pescatarian'),
        
    ]
    dietary_preference = models.CharField(max_length=2, choices=DIETARY_CHOICES, default='N')
    ACCESSIBILITY_CHOICES = [
        ('W', 'Wheelchair Accessible'),
        ('G', 'Guide Dog Friendly'),
        ('A', 'Autism Friendly'),
        ('N', 'None'),
    ]
    accessibility_requirements = models.TextField(blank=True, null=True)  # Any specific needs or requirements


class Place(models.Model):
    PLACE_TYPES = [
        ('R', 'Restaurant'),
        ('H', 'Hotel'),
        ('A', 'Attraction'),
        ('S', 'Shopping'),
        ('T', 'Theatre'),
        ('C', 'Cinema'),
        ('Ba', 'Bar'),
        ('C', 'Club'),
        ('G', 'Gallery'),
        ('L', 'Library'),
        ('Z', 'Zoo'),
        ('AQ', 'Aquarium'),
        ('Be', 'Beach'),
        ('TP', 'Theme Park'),
        ('M', 'Museum'),
        ('P', 'Park'),
        ('O', 'Other'),
    ]
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    place_type = models.CharField(max_length=1, choices=PLACE_TYPES, default='O')
    cuisine_type = models.CharField(max_length=255, blank=True, null=True)  # If the place is a restaurant
    accessibility_features = models.TextField(blank=True, null=True)
    visit_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Itinerary(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date = models.DateField()
    lunch_stop = models.ForeignKey(Place, on_delete=models.SET_NULL, null=True, related_name='+')  # Optional lunch stop
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ItineraryPlace(models.Model):
    itinerary = models.ForeignKey(Itinerary, on_delete=models.CASCADE)
    place = models.ForeignKey(Place, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()  # Order in which places are to be visited
    estimated_arrival = models.DateTimeField(null=True, blank=True)
    estimated_departure = models.DateTimeField(null=True, blank=True)

class Optimization(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    minimize_travel_time = models.BooleanField(default=True)
    minimize_distance = models.BooleanField(default=False)
    consider_dietary_preferences = models.BooleanField(default=False)
    consider_accessibility_requirements = models.BooleanField(default=False)
    avoid_tolls = models.BooleanField(default=False)
    avoid_highways = models.BooleanField(default=False)

