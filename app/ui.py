
import tkinter as tk
from tkinter import ttk
from app.route_engine import compute_route
from app.map_visualizer import open_map
from app.heuristics import view_route_on_google_maps
from app.utils import validate_location

class TravelPlannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Travel Planner")

        self.custom_font = ("Segoe UI", 12)
        self.result_text = tk.StringVar()

        self.setup_ui()

    def setup_ui(self):
        tk.Label(self.root, text="Start Location:", font=self.custom_font).grid(row=0, column=0, sticky="w")
        self.start_entry = tk.Entry(self.root, width=40, font=self.custom_font)
        self.start_entry.grid(row=0, column=1)

        tk.Label(self.root, text="Places to Visit (comma-separated):", font=self.custom_font).grid(row=1, column=0, sticky="w")
        self.middle_entry = tk.Entry(self.root, width=40, font=self.custom_font)
        self.middle_entry.grid(row=1, column=1)

        tk.Label(self.root, text="End Location:", font=self.custom_font).grid(row=2, column=0, sticky="w")
        self.end_entry = tk.Entry(self.root, width=40, font=self.custom_font)
        self.end_entry.grid(row=2, column=1)

        tk.Label(self.root, text="Daily Budget (LKR):", font=self.custom_font).grid(row=3, column=0, sticky="w")
        self.budget_entry = tk.Entry(self.root, width=20, font=self.custom_font)
        self.budget_entry.grid(row=3, column=1, sticky="w")

        self.budget_var = tk.BooleanVar()
        self.places_var = tk.BooleanVar()

        tk.Checkbutton(self.root, text="Low Budget Hotels", variable=self.budget_var, font=self.custom_font).grid(row=4, column=0, columnspan=2, sticky="w")
        tk.Checkbutton(self.root, text="Maximum Places Covered", variable=self.places_var, font=self.custom_font).grid(row=5, column=0, columnspan=2, sticky="w")

        ttk.Button(self.root, text="Compute Route", command=self.compute_itinerary).grid(row=6, column=0, columnspan=2, pady=5)
        ttk.Button(self.root, text="Open Map", command=open_map).grid(row=7, column=0, columnspan=2, pady=5)
        ttk.Button(self.root, text="View on Google Maps", command=self.view_google_maps).grid(row=8, column=0, columnspan=2, pady=5)

        tk.Label(self.root, textvariable=self.result_text, wraplength=500, fg="blue", font=self.custom_font).grid(row=9, column=0, columnspan=2)

    def compute_itinerary(self):
        start = self.start_entry.get().strip()
        end = self.end_entry.get().strip()
        if not start or not end:
            self.result_text.set("Please enter both start and end locations.")
            return

        if not validate_location(start):
            self.result_text.set("Start location is invalid.")
            return
        if not validate_location(end):
            self.result_text.set("End location is invalid.")
            return

        try:
            budget_lkr = float(self.budget_entry.get().strip())
            budget = budget_lkr / 296  # Convert to USD for API comparison
        except ValueError:
            self.result_text.set("Please enter a valid numeric budget.")
            return

        waypoints = self.middle_entry.get().strip().split(",")
        preferences = {
            "budget": budget,
            "low_budget": self.budget_var.get(),
            "places": self.places_var.get()
        }

        result = compute_route(start, end, waypoints, preferences)
        self.result_text.set(result)

    def view_google_maps(self):
        start = self.start_entry.get().strip()
        end = self.end_entry.get().strip()
        if not start or not end:
            self.result_text.set("Please enter both start and end locations.")
            return

        if not validate_location(start):
            self.result_text.set("Start location is invalid.")
            return
        if not validate_location(end):
            self.result_text.set("End location is invalid.")
            return

        view_route_on_google_maps(start, end)
