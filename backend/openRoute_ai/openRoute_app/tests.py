"""
Comprehensive tests for OpenRoute.ai API
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from .models import CustomUser, Place, Itinerary, ItineraryPlace, Optimization, Country, City

User = get_user_model()


class CustomUserModelTest(TestCase):
    """Test cases for CustomUser model"""

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            dietary_preference='V',
            accessibility_requirements='Wheelchair Accessible'
        )

    def test_user_creation(self):
        """Test user is created correctly"""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.dietary_preference, 'V')
        self.assertTrue(self.user.check_password('testpass123'))

    def test_user_string_representation(self):
        """Test string representation of user"""
        self.assertEqual(str(self.user), 'testuser')


class PlaceModelTest(TestCase):
    """Test cases for Place model"""

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.place = Place.objects.create(
            user=self.user,
            name='Test Restaurant',
            address='123 Test St',
            latitude=51.5074,
            longitude=-0.1278,
            place_type='R',
            cuisine_type='Italian'
        )

    def test_place_creation(self):
        """Test place is created correctly"""
        self.assertEqual(self.place.name, 'Test Restaurant')
        self.assertEqual(self.place.place_type, 'R')
        self.assertEqual(self.place.cuisine_type, 'Italian')

    def test_place_string_representation(self):
        """Test string representation of place"""
        self.assertEqual(str(self.place), 'Test Restaurant')

    def test_latitude_validation(self):
        """Test latitude is within valid range"""
        self.assertGreaterEqual(self.place.latitude, -90)
        self.assertLessEqual(self.place.latitude, 90)

    def test_longitude_validation(self):
        """Test longitude is within valid range"""
        self.assertGreaterEqual(self.place.longitude, -180)
        self.assertLessEqual(self.place.longitude, 180)


class ItineraryModelTest(TestCase):
    """Test cases for Itinerary model"""

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.place = Place.objects.create(
            user=self.user,
            name='Test Place',
            address='123 Test St',
            latitude=51.5074,
            longitude=-0.1278,
            place_type='A'
        )
        self.itinerary = Itinerary.objects.create(
            user=self.user,
            date='2024-12-01',
            lunch_stop=self.place
        )

    def test_itinerary_creation(self):
        """Test itinerary is created correctly"""
        self.assertEqual(self.itinerary.user, self.user)
        self.assertEqual(self.itinerary.lunch_stop, self.place)

    def test_itinerary_string_representation(self):
        """Test string representation of itinerary"""
        self.assertIn(str(self.user), str(self.itinerary))
        self.assertIn('2024-12-01', str(self.itinerary))


class RegistrationAPITest(APITestCase):
    """Test cases for user registration API"""

    def setUp(self):
        self.client = APIClient()
        self.registration_url = '/api/register/'

    def test_user_registration_success(self):
        """Test successful user registration"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'testpass123',
            'dietary_preference': 'V'
        }
        response = self.client.post(self.registration_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertTrue(CustomUser.objects.filter(username='newuser').exists())

    def test_user_registration_duplicate_username(self):
        """Test registration with duplicate username"""
        CustomUser.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='testpass123'
        )
        data = {
            'username': 'existinguser',
            'email': 'newemail@example.com',
            'password': 'testpass123'
        }
        response = self.client.post(self.registration_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_user_registration_duplicate_email(self):
        """Test registration with duplicate email"""
        CustomUser.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='testpass123'
        )
        data = {
            'username': 'newuser',
            'email': 'existing@example.com',
            'password': 'testpass123'
        }
        response = self.client.post(self.registration_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)


class PlaceAPITest(APITestCase):
    """Test cases for Place API"""

    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.place_url = '/api/places/'

    def test_create_place(self):
        """Test creating a new place"""
        data = {
            'user': self.user.id,
            'name': 'New Restaurant',
            'address': '456 New St',
            'latitude': 51.5074,
            'longitude': -0.1278,
            'place_type': 'R',
            'cuisine_type': 'Chinese'
        }
        response = self.client.post(self.place_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Place.objects.count(), 1)
        self.assertEqual(Place.objects.get().name, 'New Restaurant')

    def test_list_places(self):
        """Test listing all places"""
        Place.objects.create(
            user=self.user,
            name='Test Place',
            address='123 Test St',
            latitude=51.5074,
            longitude=-0.1278,
            place_type='A'
        )
        response = self.client.get(self.place_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_place_authentication_required(self):
        """Test that authentication is required for place operations"""
        self.client.credentials()  # Remove authentication
        response = self.client.get(self.place_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ItineraryAPITest(APITestCase):
    """Test cases for Itinerary API"""

    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.itinerary_url = '/api/itineraries/'

    def test_create_itinerary(self):
        """Test creating a new itinerary"""
        data = {
            'user': self.user.id,
            'date': '2024-12-25'
        }
        response = self.client.post(self.itinerary_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Itinerary.objects.count(), 1)

    def test_list_itineraries(self):
        """Test listing all itineraries"""
        Itinerary.objects.create(
            user=self.user,
            date='2024-12-01'
        )
        response = self.client.get(self.itinerary_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)


class OptimizationModelTest(TestCase):
    """Test cases for Optimization model"""

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.optimization = Optimization.objects.create(
            user=self.user,
            minimize_travel_time=True,
            minimize_distance=False,
            consider_dietary_preferences=True,
            avoid_tolls=True
        )

    def test_optimization_creation(self):
        """Test optimization preferences are created correctly"""
        self.assertTrue(self.optimization.minimize_travel_time)
        self.assertFalse(self.optimization.minimize_distance)
        self.assertTrue(self.optimization.consider_dietary_preferences)

    def test_optimization_string_representation(self):
        """Test string representation of optimization"""
        self.assertIn(str(self.user), str(self.optimization))


class CountryAndCityTest(TestCase):
    """Test cases for Country and City models"""

    def setUp(self):
        self.country = Country.objects.create(
            name='United Kingdom',
            iso2='GB',
            iso3='GBR'
        )
        self.city = City.objects.create(
            country=self.country,
            city='London',
            city_ascii='London'
        )

    def test_country_creation(self):
        """Test country is created correctly"""
        self.assertEqual(self.country.name, 'United Kingdom')
        self.assertEqual(self.country.iso2, 'GB')

    def test_city_creation(self):
        """Test city is created correctly"""
        self.assertEqual(self.city.city, 'London')
        self.assertEqual(self.city.country, self.country)

    def test_country_string_representation(self):
        """Test string representation of country"""
        self.assertEqual(str(self.country), 'United Kingdom')

    def test_city_string_representation(self):
        """Test string representation of city"""
        self.assertEqual(str(self.city), 'London')
