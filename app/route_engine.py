from app.map_visualizer import generate_map
from app.heuristics import estimate_weather

def compute_route(start, end, waypoints, preferences):
    dummy_route = {
        "legs": [{
            "start_location": {"lat": 7.8731, "lng": 80.7718}
        }]
    }
    _ = estimate_weather(dummy_route)
    generate_map(start, end, waypoints)
    return f"Optimal route from {start} to {end} with waypoints: {', '.join(waypoints)}"