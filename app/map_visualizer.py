
import folium
from app.settings import DEFAULT_MAP_CENTER, MAP_FILE
from app.utils import get_latlng

def generate_map(start, end, waypoints, hotel_names=None):
    m = folium.Map(location=DEFAULT_MAP_CENTER, zoom_start=7)
    for idx, location in enumerate(waypoints):
        color = 'blue' if hotel_names and location in hotel_names else 'red'
        folium.Marker(location=get_latlng(location), popup=location, icon=folium.Icon(color=color)).add_to(m)
    m.save(MAP_FILE)


import webbrowser
import os

def open_map():
    from app.settings import MAP_FILE
    map_path = os.path.abspath(MAP_FILE)
    webbrowser.open(f"file://{map_path}")
