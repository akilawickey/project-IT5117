import requests
from app.map_visualizer import generate_map
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
<<<<<<< HEAD
#     url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lng}&radius=20000&type=lodging&key={GOOGLE_API_KEY}&region=LK"
=======
    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lng}&radius=20000&type=lodging&key={GOOGLE_API_KEY}&region=LK"
>>>>>>> fa6b68d556d770484b3426be23206b92e452fbbb
    response = requests.get(url)
    data = response.json()
    print("[DEBUG] Full Google API response:")
    print(data)
    if "results" in data:
        hotels = data["results"]
        hotels.sort(key=lambda h: h.get("rating", 0), reverse=True)
        # Filter by price level based on user budget
        if budget_usd == 0:
            price_level = 0
        elif budget_usd <= 50:
            price_level = 1
        elif budget_usd <= 100:
            price_level = 2
        elif budget_usd <= 150:
            price_level = 3
        else:
            price_level = 4

        # Allow ±1 price level for more options
        flexible_range = [price_level - 1, price_level, price_level + 1]
        filtered = [h for h in hotels if h.get('price_level') in flexible_range]
        print(f"[Debug] Found {len(filtered)} hotels after filtering by price level (flex ±1)")
        filtered.sort(key=lambda h: h.get('rating', 0), reverse=True)
        return filtered[0] if filtered else None
    return None

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
    for group in grouped_routes:
        # Always add hotel after last stop of each group
        if len(group) > 0:
            last_loc = group[-1]
            latlng = get_latlng(last_loc)
            hotel = get_hotel_nearby(latlng[0], latlng[1], preferences.get('budget', 50))
            if hotel:
                hotel_name = hotel['name']
                full_route_with_hotels.append(f"{hotel_name} (Hotel)")
            else:
                full_route_with_hotels.append(f"No nearby hotel found near {last_loc}")
        full_route_with_hotels.extend(group)
        # Search for hotel only if last location of the day is valid
        last_loc = group[-1]
        if last_loc:
            latlng = get_latlng(last_loc)
            hotel = get_hotel_nearby(latlng[0], latlng[1], preferences.get('budget', 50))
            if hotel:
                hotel_name = hotel['name']
                full_route_with_hotels.append(f"{hotel_name} (Hotel)")
            else:
                full_route_with_hotels.append(f"No nearby hotel found near {last_loc}")
    dummy_route = {
        "legs": [{
            "start_location": {"lat": 7.8731, "lng": 80.7718}
        }]
    }
    _ = estimate_weather(dummy_route)
    generate_map(start, end, full_route_with_hotels)
    route_summary = 'Route Plan:\n'
    route_summary += ' -> '.join(full_route_with_hotels)
    return route_summary
    route_summary += ' -> '.join(full_route_with_hotels)

def get_hotel_nearby(lat, lng, budget_usd):
    # Fallback mock data until Google API access is restored
    # Simulated OpenAPI fallback or static dataset
    mock_hotels = [
        {"name": "Mock Inn", "price_level": 1, "rating": 4.1},
        {"name": "Sunset Lodge", "price_level": 2, "rating": 4.3},
        {"name": "Palm Garden Hotel", "price_level": 3, "rating": 4.0}
    ]
    return sorted(mock_hotels, key=lambda h: h["rating"], reverse=True)[0]
