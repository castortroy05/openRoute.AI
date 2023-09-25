from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from .models import Place

from rest_framework import viewsets
from .models import Place
from .serializers import PlaceSerializer

class PlaceViewSet(viewsets.ModelViewSet):
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer

