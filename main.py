import tkinter as tk
from tkinter import ttk, messagebox

def compute_itinerary():
    start = start_location.get()
    end = end_location.get()
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
root.geometry("500x400")

# Labels
ttk.Label(root, text="Start Location:").pack(pady=5)
start_location = ttk.Combobox(root, values=["City A", "City B", "City C", "City D"])
start_location.pack()

ttk.Label(root, text="Destination Location:").pack(pady=5)
end_location = ttk.Combobox(root, values=["City A", "City B", "City C", "City D"])
end_location.pack()

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
result_label = ttk.Label(root, textvariable=result_text, wraplength=400)
result_label.pack(pady=10)

# Run the application
root.mainloop()
