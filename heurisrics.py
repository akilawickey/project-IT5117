import requests
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser

# API Keys
GOOGLE_API_KEY = "AIzaSyB2Jxq5XFdg6E2ZdBh_-Noeg2hNeUnV8yQ"
WEATHER_API_KEY = "5780440f22987457c0406c3223f66512"

# Default weights for heuristic function
# TODO: need to adjust these weights based on user preferences or testing
DEFAULT_WEIGHTS = {
    "distance": 1,
    "time": 2,
    "road_condition": 5,
    "weather": 3,
    "elevation": 4
}

# Function to fetch route data
def get_route_data(start, end, weights):
    """Fetch route options from Google Maps API"""
    url = f"https://maps.googleapis.com/maps/api/directions/json?origin={start}&destination={end}&alternatives=true&mode=driving&key={GOOGLE_API_KEY}"
    response = requests.get(url)
    data = response.json()

    if data["status"] != "OK":
        messagebox.showerror("Error", f"Error: {data['status']}")
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
            weights["distance"] * distance +
            weights["time"] * duration +
            weights["road_condition"] * road_condition +
            weights["weather"] * weather_impact +
            weights["elevation"] * elevation_penalty
        )

        routes.append((route, heuristic_score))

    # Select the best route (lower heuristic is better)
    routes.sort(key=lambda x: x[1])
    return routes[0][0]  # Return best route

# Estimate road condition based on route data
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

# Estimate weather impact using OpenWeatherMap API
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

# Estimate elevation based on Google Elevation API
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

# Function to open the best route in Google Maps
def open_route_in_google_maps(start, end, weights):
    best_route = get_route_data(start, end, weights)
    if best_route:
        # Extract the encoded polyline for the best route
        route_polyline = best_route[0]["overview_polyline"]["points"]
        url = f"https://www.google.com/maps/dir/?api=1&origin={start}&destination={end}&travelmode=driving&waypoints={route_polyline}"
        webbrowser.open(url)

# Tkinter UI to input start and end locations, and set weights
def create_ui():
    # Main window
    root = tk.Tk()
    root.title("Route Planner")

    # Start location input
    ttk.Label(root, text="Start Location:").pack(pady=5)
    start_entry = ttk.Entry(root, width=50)
    start_entry.pack(pady=5)

    # End location input
    ttk.Label(root, text="End Location:").pack(pady=5)
    end_entry = ttk.Entry(root, width=50)
    end_entry.pack(pady=5)

    # Sliders for setting weights
    weight_frame = ttk.Frame(root)
    weight_frame.pack(pady=10)

    ttk.Label(weight_frame, text="Distance Weight:").grid(row=0, column=0, padx=5)
    ttk.Label(weight_frame, text="Time Weight:").grid(row=1, column=0, padx=5)
    ttk.Label(weight_frame, text="Road Condition Weight:").grid(row=2, column=0, padx=5)
    ttk.Label(weight_frame, text="Weather Weight:").grid(row=3, column=0, padx=5)
    ttk.Label(weight_frame, text="Elevation Weight:").grid(row=4, column=0, padx=5)

    distance_weight = tk.DoubleVar(value=DEFAULT_WEIGHTS["distance"])
    time_weight = tk.DoubleVar(value=DEFAULT_WEIGHTS["time"])
    road_condition_weight = tk.DoubleVar(value=DEFAULT_WEIGHTS["road_condition"])
    weather_weight = tk.DoubleVar(value=DEFAULT_WEIGHTS["weather"])
    elevation_weight = tk.DoubleVar(value=DEFAULT_WEIGHTS["elevation"])

    distance_slider = ttk.Scale(weight_frame, from_=0, to_=10, orient="horizontal", variable=distance_weight)
    distance_slider.grid(row=0, column=1)

    time_slider = ttk.Scale(weight_frame, from_=0, to_=10, orient="horizontal", variable=time_weight)
    time_slider.grid(row=1, column=1)

    road_condition_slider = ttk.Scale(weight_frame, from_=0, to_=10, orient="horizontal", variable=road_condition_weight)
    road_condition_slider.grid(row=2, column=1)

    weather_slider = ttk.Scale(weight_frame, from_=0, to_=10, orient="horizontal", variable=weather_weight)
    weather_slider.grid(row=3, column=1)

    elevation_slider = ttk.Scale(weight_frame, from_=0, to_=10, orient="horizontal", variable=elevation_weight)
    elevation_slider.grid(row=4, column=1)

    # Function to handle button click
    def on_compute_button_click():
        start_location = start_entry.get()
        end_location = end_entry.get()

        if not start_location or not end_location:
            messagebox.showerror("Input Error", "Both start and end locations are required!")
            return
        
        weights = {
            "distance": distance_weight.get(),
            "time": time_weight.get(),
            "road_condition": road_condition_weight.get(),
            "weather": weather_weight.get(),
            "elevation": elevation_weight.get()
        }

        # Call function to open route in Google Maps
        open_route_in_google_maps(start_location, end_location, weights)

    # Compute button to fetch and display route
    ttk.Button(root, text="Compute Route", command=on_compute_button_click).pack(pady=20)

    # Run the Tkinter UI
    root.mainloop()

# Run the Tkinter UI
create_ui()
