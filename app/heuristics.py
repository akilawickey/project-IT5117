import requests
import webbrowser
from app.settings import GOOGLE_API_KEY, WEATHER_API_KEY

WEIGHTS = {
    "distance": 5,
    "time": 2,
    "road_condition": 5,
    "weather": 3,
    "elevation": 4
}

def estimate_weather(route):
    start_lat, start_lng = route["legs"][0]["start_location"].values()
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={start_lat}&lon={start_lng}&appid={WEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()
    
    if "weather" in data:
        condition = data["weather"][0]["main"].lower()
        if "rain" in condition or "storm" in condition:
            return 1.5
        elif "cloud" in condition:
            return 0.5
    return 0

def generate_route_url(start, end, best_route):
    waypoints = []
    for leg in best_route["legs"]:
        for step in leg["steps"]:
            start_loc = step["start_location"]
            end_loc = step["end_location"]
            waypoints.append(f"{start_loc['lat']},{start_loc['lng']}")
            waypoints.append(f"{end_loc['lat']},{end_loc['lng']}")
    
    waypoints_str = "|".join(waypoints)
    route_url = f"https://www.google.com/maps/dir/?api=1&origin={start}&destination={end}&waypoints={waypoints_str}&key={GOOGLE_API_KEY}"
    return route_url

def get_route_data(start, end):
    url = f"https://maps.googleapis.com/maps/api/directions/json?origin={start}&destination={end}&alternatives=true&mode=driving&key={GOOGLE_API_KEY}"
    response = requests.get(url)
    data = response.json()

    if data["status"] != "OK":
        print(f"Error: {data['status']}")
        return None

    return data["routes"]

def view_route_on_google_maps(start, end):
    routes = get_route_data(start, end)
    if routes:
        best_route = routes[0]
        route_url = generate_route_url(start, end, best_route)
        print(f"Opening best route on Google Maps: {route_url}")
        webbrowser.open(route_url)
    else:
        print("No routes found.")