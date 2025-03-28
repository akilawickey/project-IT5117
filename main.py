from tkinter import Tk
from app.ui import TravelPlannerApp

if __name__ == "__main__":
    root = Tk()

    # Center the window on the screen
    window_width = 600
    window_height = 400
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    position_top = int(screen_height / 2 - window_height / 2)
    position_left = int(screen_width / 2 - window_width / 2)
    root.geometry(f"{window_width}x{window_height}+{position_left}+{position_top}")

    app = TravelPlannerApp(root)
    root.mainloop()