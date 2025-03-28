
from app.map_visualizer import generate_map
from app.settings import DEBUG
from app.utils import get_all_routes

# Print only if DEBUG is enabled
def debug_log(msg):
    if DEBUG:
        print('[DEBUG]', msg)

from app.heuristics import estimate_weather
from app.utils import get_latlng

# Main routing logic that builds daily travel chunks
def compute_route(start, end, waypoints, preferences, user_days=None):
    distance_per_day_km = 100
    max_places_per_day = 2
    all_routes = []
    given_waypoints = [wp.strip() for wp in waypoints if wp.strip()]
    all_routes = get_all_routes(start, end, given_waypoints)
    if not all_routes:
        return "No routes found. Please check your locations."
    debug_log(f"All routes found: {len(all_routes)}")
    # Sort routes by distance
    all_routes.sort(key=lambda x: x['legs'][0]['distance']['value'])
    # Select the best route (shortest distance)
    best_route = all_routes[0]
    debug_log(f"Best route found with distance: {best_route['legs'][0]['distance']['text']}")
    # Extract waypoints from the best route
    waypoint_order = best_route.get("waypoint_order", [])
    debug_log(f"Optimized waypoint order (by index): {waypoint_order}")
    ordered_waypoints = [given_waypoints[i] for i in waypoint_order]
    debug_log(f"Ordered waypoints: {ordered_waypoints}")
    # Add start and end to the waypoints
    full_path = [start] + [wp for wp in ordered_waypoints] + [end]
    debug_log(f"Full path: {full_path}")
    # Group waypoints into daily travel chunks
    # based on distance and max places per day
    # Calculate the distance of the full path
    total_distance = 0
    for i in range(len(full_path) - 1):
        leg = get_all_routes(full_path[i], full_path[i + 1], [])
        if leg:
            total_distance += leg[0]['legs'][0]['distance']['value']
    debug_log(f"Total distance: {total_distance} meters")
    # Calculate the number of days needed based on distance
    min_num_days_needed = total_distance // (distance_per_day_km * 1000) + 1
    debug_log(f"Minimum Number of days needed: {min_num_days_needed}")
    grouped_routes = []
    num_days = 0
    num_days = 0
    current_day = []
    for place in full_path:
        current_day.append(place)
        if len(current_day) == max_places_per_day + 1:
            grouped_routes.append(current_day[:])
            current_day = [place]
    if current_day:
        grouped_routes.append(current_day)
    num_days = len(grouped_routes)
    debug_log(f"Number of days calculated: {num_days}")
    # Check if user_days is provided and validate against min_num_days_needed
    # and num_days for comfort
    if num_days < min_num_days_needed:
        num_days = min_num_days_needed # At least minimum days needed
    debug_log(f"Adjusted number of days for comfort: {num_days}")
    if user_days is not None:
        if user_days < min_num_days_needed:
            return f"Trip too short! You need at least {min_num_days_needed} days to complete this itinerary."
        elif user_days < num_days:
            return f"Trip too short! You need at least {num_days} days to complete this itinerary. Consider extending your trip with more days or reduce the number of places you need to to visit."
        elif user_days > num_days:
            extra = user_days - num_days
            print(f"You can visit {extra} more place(s) in your {user_days}-day trip.")
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
        # Estimate weather for the first leg of the route per each day
        #bad_weather_heuristics = estimate_weather(day)

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
