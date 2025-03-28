
from app.settings import GOOGLE_API_KEY
import googlemaps

def get_latlng(location_name):
    gmaps = googlemaps.Client(key=GOOGLE_API_KEY)
    geocode_result = gmaps.geocode(location_name, region="LK")
    if geocode_result:
        loc = geocode_result[0]['geometry']['location']
        return (loc['lat'], loc['lng'])
    return (7.8731, 80.7718)


def validate_location(location_name):
    try:
        from app.settings import GOOGLE_API_KEY
        import googlemaps
        gmaps = googlemaps.Client(key=GOOGLE_API_KEY)
        result = gmaps.geocode(location_name, region="LK")
        return bool(result)
    except Exception as e:
        print("[Validation Error]", e)
        return False
