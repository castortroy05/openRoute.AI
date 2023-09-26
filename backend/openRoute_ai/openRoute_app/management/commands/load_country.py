from django.core.management.base import BaseCommand
from django.core import files
from io import BytesIO
import requests
from openRoute_app.models import Country, City  # Replace app_name with the actual name of your app

class Command(BaseCommand):
    help = 'Load Country and Cities data'

    def add_arguments(self, parser):
        parser.add_argument('--flag', action='store_true', help="Update country data with their flags")

    def handle(self, *args, **kwargs):
        worldcities_csv = kwargs.get('flag')
        if worldcities_csv:
            qs = Country.objects.all().iterator()
            for country in qs:
                url = f"https://flagsapi.com/{country.iso2.upper()}/flat/64.png"
                img = requests.get(url, stream=True)
                if img.status_code != requests.codes.ok:
                    continue
                fp = BytesIO()
                fp.write(img.content)
                filename = f"{country.iso2.lower()}.png"
                country.flag.save(filename, files.File(fp))
                print(country.id, country.iso2)
        else:
            country_data = requests.get("https://gist.githubusercontent.com/ans2human/89f78752e161219060257b160f970fcd/raw/50d755da33db30ecb533d1770d94f9adcc8d6892/world_cities.json")
            cd = country_data.json()
            for countries in cd:
                country_obj, created = Country.objects.update_or_create(
                    name=countries.get('country'),
                    iso2=countries.get('iso2'),
                    iso3=countries.get('iso3')
                )
                city = countries.get('city')
                city_ascii = countries.get('city_ascii')
                print(country_obj.id, country_obj.name, city, city_ascii)
                City.objects.create(country=country_obj, city=city, city_ascii=city_ascii)
