import tkinter as tk
from tkinter import ttk

class ProjectileGUI:
    def __init__(self, simulation_instance):
        self.pause_button = None  

        self.simulation = simulation_instance
        self.root = tk.Tk()
        self.root.title("Projectile Motion Controls")

        self.input_vars = {
            "initial_velocity": tk.DoubleVar(value=40),
            "launch_angle": tk.DoubleVar(value=45),
            "initial_height": tk.DoubleVar(value=0),
            "mass": tk.DoubleVar(value=2),
            "air_resistance": tk.DoubleVar(value=0),
            "time_scale": tk.DoubleVar(value=2)
        }

        self.result_vars = {
            "current_velocity": tk.StringVar(value="0.0"),
            "current_angle": tk.StringVar(value="0.0"),
            "current_height": tk.StringVar(value="0.0"),
            "current_time": tk.StringVar(value="0.0"),
            "maximum_height": tk.StringVar(value="0.0"),
            "range": tk.StringVar(value="0.0"),
            "time_of_flight": tk.StringVar(value="0.0")
        }

        self.environment_var = tk.StringVar(value="Earth")
        self._build_ui()
        
    def _build_ui(self):
        frm = ttk.Frame(self.root, padding=10)
        frm.grid(row=0, column=0)

        row = 0
        for label, var in self.input_vars.items():
            ttk.Label(frm, text=label.replace("_", " ").capitalize() + ":").grid(column=0, row=row, sticky="w")
            ttk.Entry(frm, textvariable=var).grid(column=1, row=row, sticky="ew")
            row += 1

        ttk.Label(frm, text="Environment:").grid(column=0, row=row, sticky="w")
        ttk.Combobox(frm, textvariable=self.environment_var,
                    values=["Earth", "Moon", "Mars", "Jupiter"], state="readonly").grid(column=1, row=row)
        row += 1

        control_frame1 = ttk.Frame(frm)
        control_frame1.grid(column=0, row=row, columnspan=2, pady=5, sticky="ew")

        ttk.Button(control_frame1, text="Start", command=self.simulation.start_simulation).pack(side="left", expand=True, padx=5)
        self.pause_button = ttk.Button(control_frame1, text="Pause", command=self.simulation.toggle_pause)
        self.pause_button.pack(side="left", expand=True, padx=5)
        ttk.Button(control_frame1, text="Reset", command=self.simulation.reset_simulation).pack(side="left", expand=True, padx=5)
        row += 1

        # Second row: Zoom In and Zoom Out buttons (slightly wider)
        control_frame2 = ttk.Frame(frm)
        control_frame2.grid(column=0, row=row, columnspan=2, pady=5, sticky="ew")

        ttk.Button(control_frame2, text="Zoom In", command=self.zoom_in, width=20).pack(side="left", expand=True, padx=5)
        ttk.Button(control_frame2, text="Zoom Out", command=self.zoom_out, width=20).pack(side="left", expand=True, padx=5)
        row += 1


    def zoom_in(self):
        self.simulation.zoom_in()

    def zoom_out(self):
        self.simulation.zoom_out()

    def run(self):
        self.root.mainloop()
