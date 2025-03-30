
import folium
import os
import polyline
import webbrowser
from app.settings import DEFAULT_MAP_CENTER, MAP_FILE
from app.utils import get_latlng

# TODO: Folium map is straight lines we need to correct it.
def generate_map(start, end, waypoints, hotel_names=None):

    route = waypoints["overview_polyline"]["points"]
    coordinates = polyline.decode(route)
    # Center the map on the starting point
    route_map = folium.Map(location=coordinates[0], zoom_start=8)

    # Add the polyline to the map
    folium.PolyLine(locations=coordinates, color="blue", weight=4.5, opacity=0.7).add_to(route_map)

    # Markers
    folium.Marker(coordinates[0], popup="Start", icon=folium.Icon(color="green")).add_to(route_map)
    folium.Marker(coordinates[-1], popup="End", icon=folium.Icon(color="red")).add_to(route_map)

    # Save and show
    route_map.save(MAP_FILE)

def open_map():
    map_path = os.path.abspath(MAP_FILE)
    webbrowser.open(f"file://{map_path}")


# def view_on_google_maps(route):

#     if not hasattr(route, "last_route") or not route.last_route:
#         print("No route to show. Please compute itinerary first.")
#         return
#     lines = route.last_route.split("\n")
#     route_points = []
#     for line in lines:
#         if line.startswith("- "):
#             point = line[2:].strip()
#             if " (Hotel)" in point:
#                 point = point.replace(" (Hotel)", "")
#             if "No nearby hotel" not in point:
#                 route_points.append(point.replace(" ", "+"))
#     if len(route_points) < 2:
#         print("Not enough route points to open Google Maps.")
#         return
#     origin = route_points[0]
#     destination = route_points[-1]
#     waypoints = route_points[1:-1]
#     waypoints_param = "%7C".join(waypoints)
#     base_url = "https://www.google.com/maps/dir/?api=1"
#     url = f"{base_url}&origin={origin}&destination={destination}&waypoints={waypoints_param}"
#     webbrowser.open(url)