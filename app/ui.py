
import tkinter as tk
from tkinter import messagebox
from app.route_engine import compute_route
from app.map_visualizer import open_map
from app.utils import validate_location

class TravelPlannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Travel Planner")
        self.root.geometry("700x600")
        self.root.eval('tk::PlaceWindow . center')

        self.custom_font = ("Arial", 12)

        tk.Label(root, text="Start Location:", font=self.custom_font).grid(row=0, column=0, sticky="e")
        self.start_entry = tk.Entry(root, width=50, font=self.custom_font)
        self.start_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(root, text="End Location:", font=self.custom_font).grid(row=1, column=0, sticky="e")
        self.end_entry = tk.Entry(root, width=50, font=self.custom_font)
        self.end_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(root, text="Waypoints (one per line):", font=self.custom_font).grid(row=2, column=0, sticky="ne")
        self.waypoints_text = tk.Text(root, height=8, width=40, font=self.custom_font)
        self.waypoints_text.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(root, text="Budget (LKR/day):", font=self.custom_font).grid(row=3, column=0, sticky="e")
        self.budget_entry = tk.Entry(root, width=20, font=self.custom_font)
        self.budget_entry.grid(row=3, column=1, padx=10, pady=5, sticky="w")

        self.compute_button = tk.Button(root, text="Compute Itinerary", command=self.compute_itinerary, font=self.custom_font)
        self.compute_button.grid(row=4, column=1, pady=10, sticky="w")

        self.map_button = tk.Button(root, text="View Map", command=open_map, font=self.custom_font)
        self.map_button.grid(row=4, column=1, pady=10, sticky="e")

        self.export_button = tk.Button(root, text="Export Itinerary", command=self.export_itinerary, font=self.custom_font)
        self.export_button.grid(row=5, column=1, pady=5, sticky="w")

        self.result_text = tk.StringVar()
        self.result_label = tk.Label(root, textvariable=self.result_text, justify="left", anchor="w", wraplength=600, font=self.custom_font)
        self.result_label.grid(row=6, column=0, columnspan=2, padx=10, pady=10, sticky="w")

    def compute_itinerary(self):
        start = self.start_entry.get().strip()
        end = self.end_entry.get().strip()
        waypoints = self.waypoints_text.get("1.0", tk.END).splitlines()
        budget_lkr = self.budget_entry.get().strip()

        if not validate_location(start):
            messagebox.showerror("Validation Error", "Start location not found.")
            return
        if not validate_location(end):
            messagebox.showerror("Validation Error", "End location not found.")
            return
        for wp in waypoints:
            if wp.strip() and not validate_location(wp.strip()):
                messagebox.showerror("Validation Error", f"Waypoint not found: {wp}")
                return

        try:
            budget_lkr = float(budget_lkr)
        except:
            budget_lkr = 30000
        preferences = {'budget': budget_lkr / 296}

        result = compute_route(start, end, waypoints, preferences)
        self.result_text.set(result)

    def export_itinerary(self):
        summary = self.result_text.get()
        with open("itinerary_export.txt", "w", encoding="utf-8") as f:
            f.write(summary)
        print("Itinerary exported to itinerary_export.txt")
