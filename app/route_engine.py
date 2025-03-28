
from app.map_visualizer import generate_map
from app.settings import DEBUG

# Print only if DEBUG is enabled
def debug_log(msg):
    if DEBUG:
        print('[DEBUG]', msg)

from app.heuristics import estimate_weather
from app.utils import get_latlng

# Main routing logic that builds daily travel chunks
def compute_route(start, end, waypoints, preferences):
    distance_per_day_km = 100
    max_places_per_day = 2
    full_path = [start] + [wp.strip() for wp in waypoints if wp.strip()] + [end]
    grouped_routes = []
    current_day = []
    current_distance = 0
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
        full_route_with_hotels.extend(group)
        day.extend(group)
        last_loc = group[-1]
        latlng = get_latlng(last_loc)
        hotel = get_hotel_nearby(latlng[0], latlng[1], preferences.get('budget', 50))
        if hotel:
            city = group[-1].split(',')[0] if ',' in group[-1] else group[-1]
            hotel_name = f"{hotel['name']} {city}"
            full_route_with_hotels.append(f"{hotel_name} (Hotel)")
            day.append(f"{hotel_name} (Hotel)")
        else:
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

# Use Overpass API to get nearby hotel names
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
        debug_log(f"Hotel API query: {query}")
        response = requests.post(overpass_url, data={'data': query})
        data = response.json()
        hotels = data.get('elements', [])
        if not hotels:
            return None
        best_hotel = hotels[0]
        return {"name": best_hotel.get('tags', {}).get('name', 'Unnamed Hotel')}
    except Exception as e:
        debug_log(f"Hotel API request failed: {e}")
        return None
        print("[Overpass Error]", e)
        return None
