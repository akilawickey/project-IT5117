import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import googlemaps

API_KEY = "AIzaSyDDIsIvSoV-QBKwEhwv1H34c1sPdTpcBsI"
gmaps = googlemaps.Client(key=API_KEY)

def search_place(entry_widget, result_var):
    place_name = entry_widget.get()
    if not place_name:
        messagebox.showerror("Error", "Please enter a place name.")
        return
    
    results = gmaps.geocode(place_name)
    if not results:
        messagebox.showerror("Error", "Place not found.")
        return
    
    location = results[0]['geometry']['location']
    lat, lng = location['lat'], location['lng']
    formatted_address = results[0]['formatted_address']
    result_var.set(f"{formatted_address} (Lat: {lat}, Lng: {lng})")
    # webbrowser.open(f"https://www.google.com/maps/search/?api=1&query={lat},{lng}")

def compute_itinerary():
    start = start_text.get()
    end = end_text.get()
    preferences = []
    if budget_var.get():
        preferences.append("Low Budget Hotels")
    if places_var.get():
        preferences.append("Maximum Places Covered")
    
    if not start or not end:
        messagebox.showerror("Error", "Please select both start and destination locations.")
        return
    
    result_text.set(f"Calculating itinerary from {start} to {end} using preferences: {', '.join(preferences)}")

# Main window
root = tk.Tk()
root.title("Tourist Itinerary System")
root.geometry("600x500")

# Start Location Search
ttk.Label(root, text="Start Location:").pack(pady=5)
start_entry = ttk.Entry(root, width=40)
start_entry.pack()
start_text = tk.StringVar()
ttk.Button(root, text="Search", command=lambda: search_place(start_entry, start_text)).pack(pady=5)
ttk.Label(root, textvariable=start_text, wraplength=500).pack(pady=5)

# End Location Search
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

# Button to compute itinerary
ttk.Button(root, text="Compute Itinerary", command=compute_itinerary).pack(pady=10)

# Output display
result_text = tk.StringVar()
result_label = ttk.Label(root, textvariable=result_text, wraplength=500)
result_label.pack(pady=10)

# Run the application
root.mainloop()
