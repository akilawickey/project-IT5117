import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import googlemaps
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

API_KEY = "AIzaSyB2Jxq5XFdg6E2ZdBh_-Noeg2hNeUnV8yQ"
gmaps = googlemaps.Client(key=API_KEY)

def search_place(entry_widget, result_var):
    place_name = entry_widget.get()
    if not place_name:
        messagebox.showerror("Error", "Please enter a place name.")
        return None
    
    results = gmaps.geocode(place_name)
    if not results:
        messagebox.showerror("Error", "Place not found.")
        return None
    
    location = results[0]['geometry']['location']
    lat, lng = location['lat'], location['lng']
    formatted_address = results[0]['formatted_address']
    result_var.set(f"{formatted_address} (Lat: {lat}, Lng: {lng})")
    
    # Open location in Google Maps
    # webbrowser.open(f"https://www.google.com/maps/search/?api=1&query={lat},{lng}")
    
    return lat, lng

def compute_itinerary():
    start = start_entry.get()
    end = end_entry.get()
    
    if not start or not end:
        messagebox.showerror("Error", "Please select both start and destination locations.")
        return
    
    preferences = []
    if budget_var.get():
        preferences.append("Low Budget Hotels")
    if places_var.get():
        preferences.append("Maximum Places Covered")
    
    result_text.set(f"Calculating itinerary from {start} to {end} using preferences: {', '.join(preferences)}")
    
    draw_routes()

def draw_routes():
    start = start_entry.get()
    end = end_entry.get()
    
    if not start or not end:
        messagebox.showerror("Error", "Please enter valid start and end locations.")
        return
    
    directions = gmaps.directions(start, end, mode="driving", alternatives=True)
    if not directions:
        messagebox.showerror("Error", "No routes found between the selected locations.")
        return
    
    fig, ax = plt.subplots(figsize=(5, 5))
    
    colors = ['blue', 'green', 'red', 'purple']  # Different colors for multiple routes
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

    # Embed the plot inside Tkinter
    for widget in frame.winfo_children():
        widget.destroy()
    
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack()

# Main Tkinter Window
root = tk.Tk()
root.title("Tourist Itinerary System")
root.geometry("700x650")

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

# Preferences
ttk.Label(root, text="Preferences:").pack(pady=5)
budget_var = tk.BooleanVar()
places_var = tk.BooleanVar()
ttk.Checkbutton(root, text="Low Budget Hotels", variable=budget_var).pack()
ttk.Checkbutton(root, text="Cover Maximum Places", variable=places_var).pack()

# Button to Compute Itinerary
ttk.Button(root, text="Compute Itinerary", command=compute_itinerary).pack(pady=10)

# Output Text
result_text = tk.StringVar()
result_label = ttk.Label(root, textvariable=result_text, wraplength=500)
result_label.pack(pady=10)

# Frame to Display Matplotlib Plot
frame = tk.Frame(root)
frame.pack(pady=10)

# Run Tkinter Application
root.mainloop()
