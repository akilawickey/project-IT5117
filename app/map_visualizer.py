import folium
import webbrowser
import os
import googlemaps
from app.settings import GOOGLE_API_KEY, MAP_FILE

gmaps = googlemaps.Client(key=GOOGLE_API_KEY)

def get_coords(location_name):
    geocode_result = gmaps.geocode(location_name)
    if geocode_result:
        loc = geocode_result[0]['geometry']['location']
        return [loc['lat'], loc['lng']]
    return [7.8731, 80.7718]

def generate_map(start, end, waypoints):
    start_coords = get_coords(start)
    end_coords = get_coords(end)
    waypoint_coords = [get_coords(wp) for wp in waypoints if wp.strip()]
    all_points = [start_coords] + waypoint_coords + [end_coords]

    m = folium.Map(location=start_coords, zoom_start=7)
    folium.Marker(location=start_coords, popup="Start", icon=folium.Icon(color="green")).add_to(m)
    for i, wp in enumerate(waypoint_coords):
        folium.Marker(location=wp, popup=f"Waypoint {i+1}", icon=folium.Icon(color="blue")).add_to(m)
    folium.Marker(location=end_coords, popup="End", icon=folium.Icon(color="red")).add_to(m)
    folium.PolyLine(locations=all_points, color="blue", weight=3, opacity=0.7).add_to(m)

    m.save(MAP_FILE)

def open_map():
    webbrowser.open("file://" + os.path.abspath(MAP_FILE))