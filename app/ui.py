
import tkinter as tk
from tkinter import messagebox, scrolledtext
from app.route_engine import compute_route
from app.map_visualizer import open_map
from app.utils import validate_location

class TravelPlannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Travel Planner")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        self.custom_font = ("Segoe UI", 11)

        title_label = tk.Label(root, text="AI Travel Planner", font=("Segoe UI", 16, "bold"))
        title_label.pack(pady=10)

        # Trip Preferences section
        trip_frame = tk.LabelFrame(root, text="Trip Preferences", padx=10, pady=10, font=("Segoe UI", 12, "bold"))
        trip_frame.pack(padx=20, pady=5, fill="x")

        tk.Label(trip_frame, text="Start Location:", font=self.custom_font).grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.start_entry = tk.Entry(trip_frame, width=40, font=self.custom_font)
        self.start_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(trip_frame, text="End Location:", font=self.custom_font).grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.end_entry = tk.Entry(trip_frame, width=40, font=self.custom_font)
        self.end_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(trip_frame, text="Add a Stop:", font=self.custom_font).grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.stop_entry = tk.Entry(trip_frame, width=40, font=self.custom_font)
        self.stop_entry.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        self.add_button = tk.Button(trip_frame, text="Add Waypoint", command=self.add_waypoint, font=self.custom_font)
        self.add_button.grid(row=2, column=2, padx=5, pady=5)

        tk.Label(trip_frame, text="Hint: Add one by one by using 'Add Waypoint' Button", font=("Segoe UI", 9, "italic")).grid(row=3, column=1, columnspan=2, sticky="w")

        tk.Label(trip_frame, text="Places I wanted to go:", font=self.custom_font).grid(row=4, column=0, sticky="ne", padx=5, pady=5)
        self.waypoints_display = tk.Text(trip_frame, height=5, width=45, font=self.custom_font, state="disabled", relief="sunken", bd=1)
        self.waypoints_display.grid(row=4, column=1, padx=5, pady=5)

        self.clear_button = tk.Button(trip_frame, text="Clear", command=self.clear_waypoints, font=self.custom_font)
        self.clear_button.grid(row=4, column=2, sticky="n", padx=5)

        tk.Label(trip_frame, text="Budget (LKR/day):", font=self.custom_font).grid(row=5, column=0, sticky="e", padx=5, pady=5)
        self.budget_entry = tk.Entry(trip_frame, width=20, font=self.custom_font)
        self.budget_entry.grid(row=5, column=1, sticky="w", padx=5, pady=5)

        # Number of Days input
        tk.Label(trip_frame, text="Number of Days:", font=self.custom_font).grid(row=6, column=0, sticky="e", padx=5, pady=5)
        self.days_entry = tk.Entry(trip_frame, width=20, font=self.custom_font)
        self.days_entry.grid(row=6, column=1, sticky="w", padx=5, pady=5)

        # Button Row
        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)

        self.compute_button = tk.Button(button_frame, text="Compute Itinerary", command=self.compute_itinerary, font=self.custom_font)
        self.compute_button.grid(row=0, column=0, padx=5)

        self.export_button = tk.Button(button_frame, text="Export Itinerary", command=self.export_itinerary, font=self.custom_font)
        self.export_button.grid(row=0, column=1, padx=5)

        self.map_button = tk.Button(button_frame, text="Open Map View", command=open_map, font=self.custom_font)
        self.map_button.grid(row=0, column=2, padx=5)

        self.google_button = tk.Button(button_frame, text="Open in Google Maps", command=self.view_on_google_maps, font=self.custom_font)
        self.google_button.grid(row=0, column=3, padx=5)

        # Output Section
        output_frame = tk.LabelFrame(root, text="Itinerary", font=("Segoe UI", 12, "bold"))
        output_frame.pack(padx=20, pady=10, fill="both", expand=True)

        self.result_text_widget = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, width=90, height=20, font=("Segoe UI", 10))
        self.result_text_widget.pack(padx=10, pady=10, fill="both", expand=True)

        self.waypoints = []

    def add_waypoint(self):
        stop = self.stop_entry.get().strip()
        if stop:
            self.waypoints.append(stop)
            self.stop_entry.delete(0, tk.END)
            self.waypoints_display.config(state="normal")
            self.waypoints_display.insert(tk.END, stop + "\n")
            self.waypoints_display.config(state="disabled")

    def clear_waypoints(self):
        self.waypoints = []
        self.waypoints_display.config(state="normal")
        self.waypoints_display.delete("1.0", tk.END)
        self.waypoints_display.config(state="disabled")

    def compute_itinerary(self):
        start = self.start_entry.get().strip()
        end = self.end_entry.get().strip()
        budget_lkr = self.budget_entry.get().strip()

        if not validate_location(start):
            messagebox.showerror("Validation Error", "Start location not found.")
            return
        if not validate_location(end):
            messagebox.showerror("Validation Error", "End location not found.")
            return
        for wp in self.waypoints:
            if wp.strip() and not validate_location(wp.strip()):
                messagebox.showerror("Validation Error", f"Waypoint not found: {wp}")
                return

        try:
            budget_lkr = float(budget_lkr)
        except:
            budget_lkr = 30000
        preferences = {'budget': budget_lkr / 296}

        # Get user-defined number of days
        try:
            user_days = int(self.days_entry.get())
        except ValueError:
            user_days = None
            print("Invalid day input; continuing without validation.")
        result = compute_route(start, end, self.waypoints, preferences, user_days=user_days)
        # Read user-provided number of days
        try:
            user_days = int(self.days_entry.get()) if self.days_entry.get().strip() else None
        except ValueError:
            self.result_text_widget.insert(tk.END, "Invalid number of days\n")
            return
        result = compute_route(start, end, self.waypoints, preferences, user_days=user_days)
        self.result_text_widget.delete("1.0", tk.END)
        self.result_text_widget.insert(tk.END, result)
        self.result_text_widget.see(tk.END)
        self.last_route = result

    def export_itinerary(self):
        summary = self.result_text_widget.get("1.0", tk.END)
        with open("itinerary_export.txt", "w", encoding="utf-8") as f:
            f.write(summary)

    def view_on_google_maps(self):
        import webbrowser
        if not hasattr(self, "last_route") or not self.last_route:
            print("No route to show. Please compute itinerary first.")
            return
        lines = self.last_route.split("\n")
        route_points = []
        for line in lines:
            if line.startswith("- "):
                point = line[2:].strip()
                if " (Hotel)" in point:
                    point = point.replace(" (Hotel)", "")
                if "No nearby hotel" not in point:
                    route_points.append(point.replace(" ", "+"))
        if len(route_points) < 2:
            print("Not enough route points to open Google Maps.")
            return
        origin = route_points[0]
        destination = route_points[-1]
        waypoints = route_points[1:-1]
        waypoints_param = "%7C".join(waypoints)
        base_url = "https://www.google.com/maps/dir/?api=1"
        url = f"{base_url}&origin={origin}&destination={destination}&waypoints={waypoints_param}"
        webbrowser.open(url)
