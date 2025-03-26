import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import folium
import requests
import googlemaps
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Securely store the API key (Replace with os.getenv or config file)
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "AIzaSyB2Jxq5XFdg6E2ZdBh_-Noeg2hNeUnV8yQ")
gmaps = googlemaps.Client(key=API_KEY)

def search_place(entry_widget, result_var):
    """Search for a place and update the result label with formatted address and coordinates."""
    place_name = entry_widget.get().strip()
    if not place_name:
        messagebox.showerror("Error", "Please enter a place name.")
        return None
    
    try:
        results = gmaps.geocode(place_name)
        if not results:
            messagebox.showerror("Error", "Place not found.")
            return None
        
        location = results[0]['geometry']['location']
        lat, lng = location['lat'], location['lng']
        formatted_address = results[0]['formatted_address']
        result_var.set(f"{formatted_address} (Lat: {lat}, Lng: {lng})")
        return lat, lng
    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch location: {str(e)}")
        return None

def compute_itinerary():
    """Compute itinerary based on start, destination, and user preferences."""
    start = start_entry.get().strip()
    end = end_entry.get().strip()
    waypoints = middle_entry.get().strip()
    
    if not start or not end:
        messagebox.showerror("Error", "Please enter valid start and destination locations.")
        return
    
    waypoints_list = [wp.strip() for wp in waypoints.split(",") if wp.strip()]  # Convert to list
    print(f"Start: {start}, End: {end}, Waypoints: {waypoints_list}")
    preferences = []
    if budget_var.get():
        preferences.append("Low Budget Hotels")
    if places_var.get():
        preferences.append("Maximum Places Covered")
    
    result_text.set(f"Calculating itinerary from {start} to {end} using preferences: {', '.join(preferences)}")
    route = get_route_with_waypoints(start, end, waypoints_list)
    print(route)
    draw_routes(start, end, waypoints_list)
    draw_map(route)


def draw_map(route):
    """Draws a map using Folium and saves it as an HTML file."""
    # Create a map centered around the first coordinate
    map_route = folium.Map(location=route[0], zoom_start=8)

    # Add the route as a polyline
    folium.PolyLine(locations=route, color="blue", weight=4, opacity=0.7).add_to(map_route)

    # Add markers for start and end points
    folium.Marker(route[0], popup="Start", icon=folium.Icon(color="green")).add_to(map_route)
    folium.Marker(route[-1], popup="End", icon=folium.Icon(color="red")).add_to(map_route)

    # Save the map as an HTML file
    map_filename = "route_map.html"
    map_route.save(map_filename)

    # Open the map in the default web browser
    webbrowser.open("file://" + os.path.abspath(map_filename))

    print(f"Route map saved as '{map_filename}'. Opening in browser...")

    

def get_route_with_waypoints(start, end, waypoints):
    """Fetches a route from Google Maps API."""
    waypoints_str = "|".join(waypoints) if waypoints else ""
    url = f"https://maps.googleapis.com/maps/api/directions/json?origin={start}&destination={end}&waypoints={waypoints_str}&key={API_KEY}"
    
    try:
        response = requests.get(url)
        data = response.json()
        if data["status"] == "OK":
            route = data["routes"][0]["legs"]
            path = []
            for leg in route:
                for step in leg["steps"]:
                    start_loc = step["start_location"]
                    end_loc = step["end_location"]
                    path.append((start_loc["lat"], start_loc["lng"]))
                    path.append((end_loc["lat"], end_loc["lng"]))
        
            return path
        else:
            messagebox.showerror("Error", f"Failed to get route: {data['status']}")
            return None
    except Exception as e:
        messagebox.showerror("Error", f"API request failed: {str(e)}")
        return None

def draw_routes(start, end, waypoints):
    """Draws multiple possible routes between locations."""
    directions = gmaps.directions(start, end, waypoints=waypoints, mode="driving", alternatives=True)
    
    if not directions:
        messagebox.showerror("Error", "No routes found between the selected locations.")
        return
    # data = directions.json()

    # if data["status"] == "OK":
    #     route = data["routes"][0]["legs"]
    #     path = []
        
    #     for leg in route:
    #         for step in leg["steps"]:
    #             start_loc = step["start_location"]
    #             end_loc = step["end_location"]
    #             path.append((start_loc["lat"], start_loc["lng"]))
    #             path.append((end_loc["lat"], end_loc["lng"]))
        
    #     return path
    # else:
    #     print("Error:", data["status"])
    #     return None
    
    fig, ax = plt.subplots(figsize=(8, 8))
    colors = ['blue', 'green', 'red', 'purple']

    for i, route in enumerate(directions):
        path = []
        for leg in route["legs"]:
            for step in leg["steps"]:
                start_loc = step["start_location"]
                end_loc = step["end_location"]
                path.append((start_loc["lat"], start_loc["lng"]))
                path.append((end_loc["lat"], end_loc["lng"]))

        lats, lngs = zip(*path)
        ax.plot(lngs, lats, marker="o", linestyle="-", color=colors[i % len(colors)], label=f"Route {i+1}")

    ax.set_title("Route Map")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.legend()

    # Clear previous plot
    for widget in frame.winfo_children():
        widget.destroy()
    
    # Embed Matplotlib figure in Tkinter
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack()

# Main Tkinter Window
root = tk.Tk()
root.title("Tourist Itinerary System")
root.geometry("1000x650")

# Start Location
ttk.Label(root, text="Start Location:").pack(pady=5)
start_entry = ttk.Entry(root, width=40)
start_entry.pack()
start_text = tk.StringVar()
ttk.Button(root, text="Search", command=lambda: search_place(start_entry, start_text)).pack(pady=5)
ttk.Label(root, textvariable=start_text, wraplength=500).pack(pady=5)

# End Location
ttk.Label(root, text="Destination Location:").pack(pady=5)
end_entry = ttk.Entry(root, width=40)
end_entry.pack()
end_text = tk.StringVar()
ttk.Button(root, text="Search", command=lambda: search_place(end_entry, end_text)).pack(pady=5)
ttk.Label(root, textvariable=end_text, wraplength=500).pack(pady=5)

# Intermediate Locations
ttk.Label(root, text="Middle Locations (comma separated):").pack(pady=5)
middle_entry = ttk.Entry(root, width=40)
middle_entry.pack()
middle_text = tk.StringVar()
ttk.Label(root, textvariable=middle_text, wraplength=500).pack(pady=5)

# Preferences
ttk.Label(root, text="Preferences:").pack(pady=5)
budget_var = tk.BooleanVar()
places_var = tk.BooleanVar()
ttk.Checkbutton(root, text="Low Budget Hotels", variable=budget_var).pack()
ttk.Checkbutton(root, text="Cover Maximum Places", variable=places_var).pack()

# Compute Itinerary Button
ttk.Button(root, text="Compute Itinerary", command=compute_itinerary).pack(pady=10)

# Output Text
result_text = tk.StringVar()
result_label = ttk.Label(root, textvariable=result_text, wraplength=500)
result_label.pack(pady=10)

# Frame for Matplotlib Plot
frame = tk.Frame(root)
frame.pack(pady=10)

# Run Tkinter Application
root.mainloop()
