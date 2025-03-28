
import requests
from app.map_visualizer import generate_map
from app.utils import get_latlng
from app.heuristics import estimate_weather
from app.settings import GOOGLE_API_KEY

def get_latlng(location_name):
    import googlemaps
    gmaps = googlemaps.Client(key=GOOGLE_API_KEY)
    geocode_result = gmaps.geocode(location_name, region="LK")
    if geocode_result:
        loc = geocode_result[0]['geometry']['location']
        return (loc['lat'], loc['lng'])
    return (7.8731, 80.7718)

def get_hotel_nearby(lat, lng, budget_usd):
    import requests
    lat, lng = round(lat, 3), round(lng, 3)
    south, north = lat - 0.05, lat + 0.05
    west, east = lng - 0.05, lng + 0.05
    overpass_url = "https://overpass-api.de/api/interpreter"
    query = f"""
[out:json];
node['tourism'='hotel']({{south}},{{west}},{{north}},{{east}});
out;
""".replace("{south}", str(south)).replace("{west}", str(west)).replace("{north}", str(north)).replace("{east}", str(east))
    try:
        response = requests.post(overpass_url, data={'data': query})
        data = response.json()
        print(f"[Overpass Debug] Found {len(data.get('elements', []))} hotels")
        hotels = data.get('elements', [])
        if not hotels:
            return None
        best_hotel = hotels[0]
        return {"name": best_hotel.get('tags', {}).get('name', 'Unnamed Hotel')}
    except Exception as e:
        print("[Overpass Error]", e)
        return None

def compute_route(start, end, waypoints, preferences):
    distance_per_day_km = 100
    max_places_per_day = 2
    full_path = [start] + [wp.strip() for wp in waypoints if wp.strip()] + [end]
    grouped_routes = []
    current_day = []

    for place in full_path:
        current_day.append(place)
        if len(current_day) == max_places_per_day + 1:
            grouped_routes.append(current_day[:])
            current_day = [place]
    if current_day:
        grouped_routes.append(current_day)

    full_route_with_hotels = []
    day_routes = []

    for group in grouped_routes:
        day = []
        day.extend(group)
        last_loc = group[-1]
        latlng = get_latlng(last_loc)
        hotel = get_hotel_nearby(latlng[0], latlng[1], preferences.get('budget', 50))
        if hotel:
            hotel_name = hotel['name']
            full_route_with_hotels.extend(group)
            full_route_with_hotels.append(f"{hotel_name} (Hotel)")
            day.append(f"{hotel_name} (Hotel)")
        else:
            full_route_with_hotels.extend(group)
            full_route_with_hotels.append(f"No nearby hotel found near {last_loc}")
            day.append(f"No nearby hotel found near {last_loc}")
        day_routes.append(day)

    dummy_route = {
        "legs": [{
            "start_location": {"lat": 7.8731, "lng": 80.7718}
        }]
    }
    _ = estimate_weather(dummy_route)
    generate_map(start, end, full_route_with_hotels, hotel_names=[s for d in day_routes for s in d if '(Hotel)' in s])

    route_summary = 'Route Plan by Day:\n'
    for i, day in enumerate(day_routes, 1):
        route_summary += f"\nDay {i}:\n"
        for stop in day:
            route_summary += f"- {stop}\n"
    return route_summary
