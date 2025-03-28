import requests
# import webbrowser
from app.settings import DEBUG
from app.settings import GOOGLE_API_KEY, WEATHER_API_KEY

# Print only if DEBUG is enabled
def debug_log(msg):
    if DEBUG:
        print('[DEBUG]', msg)

# Weights for heuristic function
WEIGHTS = {
    "distance": 0.5,  # Lower is better
    "time": 0.2,  # Faster routes preferred
    "road_condition": 0.5,  # Bad roads should be penalized more
    "weather": 0.3,  # Bad weather penalty
    "elevation": 0.5  # Hilly areas penalized more
}

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

def get_route_data(routes):
    if not routes:
        print("No routes found.")
        return None
    if len(routes) == 1:
        print("Only one route found, using it.")
        return routes[0]
    
    scored_routes = []  # Create a separate list for scored routes
    for route in routes:
        if not route or not route.get("legs"):  # Check if "legs" exists
            print("Invalid route data, skipping.")
            continue
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
        scored_routes.append((route, heuristic_score))  # Append to scored_routes
        debug_log(f"Route: {route['summary']}, Heuristic Score: {heuristic_score}")

    # Select the best route (lower heuristic is better)
    scored_routes.sort(key=lambda x: x[1])
    return scored_routes[0][0] if scored_routes else None  # Return best route



# def view_route_on_google_maps(start, end):
#     routes = get_route_data(start, end)
#     if routes:
#         best_route = routes[0]
#         route_url = generate_route_url(start, end, best_route)
#         print(f"Opening best route on Google Maps: {route_url}")
#         webbrowser.open(route_url)
#     else:
#         print("No routes found.")