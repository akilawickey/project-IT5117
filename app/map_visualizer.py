
import folium
import os
import webbrowser
from app.settings import DEFAULT_MAP_CENTER, MAP_FILE
from app.utils import get_latlng

# TODO: Folium map is straight lines we need to correct it.
def generate_map(start, end, waypoints, hotel_names=None):
    m = folium.Map(location=DEFAULT_MAP_CENTER, zoom_start=7)
    coordinates = []
    for place in waypoints:
        latlng = get_latlng(place)
        coordinates.append(latlng)
        is_hotel = hotel_names and place in hotel_names
        marker_color = 'blue' if is_hotel else 'red'
        folium.Marker(
            location=latlng,
            popup=place,
            icon=folium.Icon(color=marker_color)
        ).add_to(m)
    if len(coordinates) > 1:
        folium.PolyLine(locations=coordinates, color="green", weight=3).add_to(m)
    m.save(MAP_FILE)

def open_map():
    map_path = os.path.abspath(MAP_FILE)
    webbrowser.open(f"file://{map_path}")
