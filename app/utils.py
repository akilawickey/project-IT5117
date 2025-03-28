import googlemaps
from app.settings import GOOGLE_API_KEY

gmaps = googlemaps.Client(key=GOOGLE_API_KEY)

def validate_location(location_name):
    result = gmaps.geocode(location_name)
    return bool(result)