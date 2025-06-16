from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, MinLengthValidator
from .managers import CustomUserManager

# Create your models here.
class CustomUser(AbstractUser):
    """
    CustomUser Model represents a user in the system.
    - dietary_preference: Specifies the dietary preference of the user.
    - accessibility_requirements: Specifies any specific needs or requirements for accessibility.
    """
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
        ('D', 'Dairy-Free'),
        ('O', 'Other'),   ]
    dietary_preference = models.CharField(
        max_length=2,
        choices=DIETARY_CHOICES,
        default='N',
        verbose_name="Dietary Preference"
    )
    ACCESSIBILITY_CHOICES = [
        ('W', 'Wheelchair Accessible'),
        ('G', 'Guide Dog Friendly'),
        ('A', 'Autism Friendly'),
        ('N', 'None'),
    ]
    accessibility_requirements = models.TextField(
        blank=True, 
        null=True,
        validators=[MinLengthValidator(1)],  # At least one character
        verbose_name="Accessibility Requirements"
    )   # Any specific needs or requirements
    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="customuser_groups",
        related_query_name="customuser",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="customuser_user_permissions",
        related_query_name="customuser",
    )
    objects = CustomUserManager()


class Place(models.Model):
    """
    Represents a place that can be visited, such as a restaurant, hotel, or attraction.
    
    Attributes:
        user (CustomUser): The user who added this place.
        name (str): The name of the place.
        address (str): The address of the place.
        latitude (float): The latitude coordinate of the place.
        longitude (float): The longitude coordinate of the place.
        place_type (str): The type of the place (e.g., Restaurant, Hotel, Attraction).
        cuisine_type (str): The type of cuisine (if the place is a restaurant).
        accessibility_features (str): Any accessibility features or requirements of the place.
        visit_time (datetime): The time the user plans to visit the place.
        created_at (datetime): The time the place was added.
        updated_at (datetime): The last time the place was updated.
    """
    
    PLACE_TYPES = [
        ('R', 'Restaurant'),
        ('H', 'Hotel'),
        ('A', 'Attraction'),
        ('S', 'Shopping'),
        ('T', 'Theatre'),
        ('C', 'Cinema'),
        ('Ba', 'Bar'),
        ('CL', 'Club'),
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
    latitude = models.FloatField(
        validators=[
            MinValueValidator(-90, message="Latitude must be between -90 and 90 degrees."),
            MaxValueValidator(90, message="Latitude must be between -90 and 90 degrees.")
        ]
    )
    longitude = models.FloatField(
        validators=[
            MinValueValidator(-180, message="Longitude must be between -180 and 180 degrees."),
            MaxValueValidator(180, message="Longitude must be between -180 and 180 degrees.")
        ]
    )
    image = models.ImageField(upload_to='places/', blank=True, null=True)
    place_type = models.CharField(max_length=2, choices=PLACE_TYPES, default='O')
    cuisine_type = models.CharField(max_length=255, blank=True, null=True)  # If the place is a restaurant
    accessibility_features = models.TextField(blank=True, null=True)
    visit_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    def __str__(self):
        """Returns a string representation of the Place object."""
        return str(self.name)
    
    def clean(self):
        """Performs custom validation for the Place object."""
        # Validate cuisine_type
        if self.place_type == 'R' and self.cuisine_type is None:
            raise ValidationError("Cuisine type is required for restaurants.")
        
        # Validate place_type
        allowed_place_types = [choice[0] for choice in self.PLACE_TYPES]
        if self.place_type not in allowed_place_types:
            raise ValidationError(f"Invalid place_type. Allowed values are {', '.join(allowed_place_types)}")
        
        # Validate accessibility_features (if you have predefined set of features)
        allowed_features = {'Wheelchair Accessible', 'Guide Dog Friendly', 'Autism Friendly'}  # Example set
        entered_features = set(self.accessibility_features.split(',')) if isinstance(self.accessibility_features, str) else set()
        if not entered_features.issubset(allowed_features):
            raise ValidationError(f"Invalid accessibility_features. Allowed values are {', '.join(allowed_features)}")

class Itinerary(models.Model):
    """
    Represents a user's itinerary, containing a list of places to visit on a specific date.
    
    Attributes:
        user (CustomUser): The user who created the itinerary.
        date (date): The date of the itinerary.
        lunch_stop (Place): An optional lunch stop during the itinerary.
        created_at (datetime): The time the itinerary was created.
        updated_at (datetime): The last time the itinerary was updated.
    """
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date = models.DateField()
    lunch_stop = models.ForeignKey(Place, on_delete=models.SET_NULL, null=True, related_name='+')  # Optional lunch stop
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()
    
    def __str__(self):
        """Returns a string representation of the Itinerary object."""
        return f"Itinerary for {self.user} on {self.date}"


class ItineraryPlace(models.Model):
    """
    Represents a place within an itinerary, including the order of visit and estimated arrival and departure times.
    
    Attributes:
        itinerary (Itinerary): The itinerary to which this place belongs.
        place (Place): The place to be visited.
        order (int): The order in which this place is to be visited in the itinerary.
        estimated_arrival (datetime): The estimated arrival time at this place.
        estimated_departure (datetime): The estimated departure time from this place.
    """
    
    itinerary = models.ForeignKey(Itinerary, on_delete=models.CASCADE)
    place = models.ForeignKey(Place, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()  # Order in which places are to be visited
    estimated_arrival = models.DateTimeField(null=True, blank=True)
    estimated_departure = models.DateTimeField(null=True, blank=True)
    objects = models.Manager()
    
    def __str__(self):
        """Returns a string representation of the ItineraryPlace object."""
        return f"{self.order}. {self.place} (Arrival: {self.estimated_arrival}, Departure: {self.estimated_departure})"
    
    def clean(self):
        """Performs custom validation for the ItineraryPlace object."""
        if self.estimated_arrival and self.estimated_departure and self.estimated_arrival >= self.estimated_departure:
            raise ValidationError("Estimated arrival must be before estimated departure.")



class Optimization(models.Model):
    """
    Represents user preferences for itinerary optimization.
    
    Attributes:
        user (CustomUser): The user to whom these preferences belong.
        minimize_travel_time (bool): Whether to minimize travel time during optimization.
        minimize_distance (bool): Whether to minimize distance during optimization.
        consider_dietary_preferences (bool): Whether to consider dietary preferences during optimization.
        consider_accessibility_requirements (bool): Whether to consider accessibility requirements during optimization.
        avoid_tolls (bool): Whether to avoid tolls during optimization.
        avoid_highways (bool): Whether to avoid highways during optimization.
    """
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    minimize_travel_time = models.BooleanField(default=True)
    minimize_distance = models.BooleanField(default=False)
    consider_dietary_preferences = models.BooleanField(default=False)
    consider_accessibility_requirements = models.BooleanField(default=False)
    avoid_tolls = models.BooleanField(default=False)
    avoid_highways = models.BooleanField(default=False)
    objects = models.Manager()
    
    def __str__(self):
        """Returns a string representation of the Optimization object."""
        return f"Optimization Preferences for {self.user}"
    
    def clean(self):
        """Performs custom validation for the Optimization object."""
        if self.minimize_travel_time and self.minimize_distance:
            raise ValidationError("Cannot minimize both travel time and distance simultaneously. Please choose one.")

class Country(models.Model):
    name = models.CharField(max_length=255)
    iso2 = models.CharField(max_length=2)
    iso3 = models.CharField(max_length=3)
    flag = models.ImageField(upload_to='flags/', blank=True, null=True)
    
    def __str__(self):
        return self.name


class City(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    city = models.CharField(max_length=255)
    city_ascii = models.CharField(max_length=255)
    
    def __str__(self):
        return self.city
    
