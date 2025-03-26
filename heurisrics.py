import requests
import webbrowser

# API Keys
GOOGLE_API_KEY = "AIzaSyB2Jxq5XFdg6E2ZdBh_-Noeg2hNeUnV8yQ"
WEATHER_API_KEY = "5780440f22987457c0406c3223f66512"

# Weights for heuristic function
WEIGHTS = {
    "distance": 1,  # Lower is better
    "time": 2,  # Faster routes preferred
    "road_condition": 5,  # Bad roads should be penalized more
    "weather": 3,  # Bad weather penalty
    "elevation": 4  # Hilly areas penalized more
}

def get_route_data(start, end):
    """Fetch route options from Google Maps API"""
    url = f"https://maps.googleapis.com/maps/api/directions/json?origin={start}&destination={end}&alternatives=true&mode=driving&key={GOOGLE_API_KEY}"
    response = requests.get(url)
    data = response.json()

    if data["status"] != "OK":
        print(f"Error: {data['status']}")
        return None

    routes = []
    for route in data["routes"]:
        distance = route["legs"][0]["distance"]["value"] / 1000  # Convert to km
        duration = route["legs"][0]["duration"]["value"] / 60  # Convert to minutes
        road_condition = estimate_road_condition(route)  
        weather_impact = estimate_weather(route)
        elevation_penalty = estimate_elevation(route)

        # Compute heuristic function
        heuristic_score = (
            WEIGHTS["distance"] * distance +
            WEIGHTS["time"] * duration +
            WEIGHTS["road_condition"] * road_condition +
            WEIGHTS["weather"] * weather_impact +
            WEIGHTS["elevation"] * elevation_penalty
        )

        routes.append((route, heuristic_score))

    # Select the best route (lower heuristic is better)
    routes.sort(key=lambda x: x[1])
    return routes[0][0]  # Return best route

def estimate_road_condition(route):
    """Estimate road quality based on traffic and road types"""
    bad_roads = 0
    total_steps = 0
    for leg in route["legs"]:
        for step in leg["steps"]:
            road_type = step.get("html_instructions", "").lower()
            if "unpaved" in road_type or "construction" in road_type:
                bad_roads += 1
            total_steps += 1
    return bad_roads / total_steps if total_steps else 0  # Normalize

def estimate_weather(route):
    """Check weather impact on the route"""
    start_lat, start_lng = route["legs"][0]["start_location"].values()
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={start_lat}&lon={start_lng}&appid={WEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()
    
    if "weather" in data:
        condition = data["weather"][0]["main"].lower()
        if "rain" in condition or "storm" in condition:
            return 1.5  # Heavy penalty for bad weather
        elif "cloud" in condition:
            return 0.5  # Minor penalty
    return 0  # No impact if clear

def estimate_elevation(route):
    """Estimate elevation difficulty from Google Elevation API"""
    locations = "|".join(f"{step['start_location']['lat']},{step['start_location']['lng']}" for leg in route["legs"] for step in leg["steps"])
    url = f"https://maps.googleapis.com/maps/api/elevation/json?locations={locations}&key={GOOGLE_API_KEY}"
    response = requests.get(url)
    data = response.json()

    elevations = [result["elevation"] for result in data.get("results", [])]
    if len(elevations) < 2:
        return 0  # No elevation data available

    elevation_changes = [abs(elevations[i+1] - elevations[i]) for i in range(len(elevations)-1)]
    total_elevation = sum(elevation_changes)
    return total_elevation / len(elevation_changes)  # Average elevation change

def generate_route_url(start, end, best_route):
    """Generate Google Maps URL for the best route"""
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

def view_route_on_google_maps(start, end):
    """Fetch the best route and display it on Google Maps"""
    best_route = get_route_data(start, end)
    if best_route:
        route_url = generate_route_url(start, end, best_route)
        print(f"Opening best route on Google Maps: {route_url}")
        webbrowser.open(route_url)
    else:
        print("No routes found.")

# Example usage
start_location = "Colombo, Sri Lanka"
end_location = "Kandy, Sri Lanka"
view_route_on_google_maps(start_location, end_location)
