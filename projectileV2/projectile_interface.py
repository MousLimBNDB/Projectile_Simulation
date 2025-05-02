import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

class ProjectileInterface:
    def __init__(self, root):
        # Main window setup
        self.root = root
        self.root.title("Projectile Motion Simulator")
        self.root.geometry("1200x700")
        self.root.resizable(False, False)
        
        # Create frames
        self.input_frame = ttk.LabelFrame(self.root, text="Simulation Parameters")
        self.input_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.Y)
        
        self.simulation_frame = ttk.LabelFrame(self.root, text="Simulation")
        self.simulation_frame.pack(side=tk.RIGHT, padx=10, pady=10, expand=True, fill=tk.BOTH)
        
        # Create input variables dictionary
        self.input_vars = {}
        
        # Create input fields
        self.create_input_fields()
        
        # Store callback functions
        self.start_callback = None
        self.pause_callback = None
        self.reset_callback = None
        self.environment_callback = None

    def create_input_fields(self):
        # Initialize variables first
        self.input_vars["initial_velocity"] = tk.DoubleVar(value=20)
        self.input_vars["launch_angle"] = tk.DoubleVar(value=45)
        self.input_vars["initial_height"] = tk.DoubleVar(value=0)
        self.input_vars["mass"] = tk.DoubleVar(value=1)
        self.input_vars["air_resistance"] = tk.DoubleVar(value=0.1)
        self.input_vars["wind_speed"] = tk.DoubleVar(value=0)
        self.input_vars["wind_angle"] = tk.DoubleVar(value=0)
        self.input_vars["time_scale"] = tk.DoubleVar(value=1.0)
        
        # Create input fields with labels
        input_fields = [
            ("Initial velocity (m/s):", self.input_vars["initial_velocity"]),
            ("Launch angle (degrees):", self.input_vars["launch_angle"]),
            ("Initial height (m):", self.input_vars["initial_height"]),
            ("Mass (kg):", self.input_vars["mass"]),
            ("Air resistance coefficient:", self.input_vars["air_resistance"]),
            ("Wind speed (m/s):", self.input_vars["wind_speed"]),
            ("Wind angle (degrees):", self.input_vars["wind_angle"]),
            ("Time scale:", self.input_vars["time_scale"])
        ]
        
        row = 0
        for label_text, var in input_fields:
            ttk.Label(self.input_frame, text=label_text).grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
            entry = ttk.Entry(self.input_frame, width=10, textvariable=var)
            entry.grid(row=row, column=1, padx=5, pady=5)
            row += 1
        
        # Special case for environment selection
        ttk.Label(self.input_frame, text="Environment:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.environment_var = tk.StringVar(value="Earth")
        environments = ["Earth", "Moon", "Mars", "Jupiter"]
        env_dropdown = ttk.Combobox(self.input_frame, textvariable=self.environment_var, values=environments, state="readonly", width=10)
        env_dropdown.grid(row=row, column=1, padx=5, pady=5)
        env_dropdown.bind("<<ComboboxSelected>>", self.on_environment_changed)
        
        row += 1
        
        # Add buttons
        button_frame = ttk.Frame(self.input_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Start", command=self.on_start).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Pause/Resume", command=self.on_pause).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Reset", command=self.on_reset).pack(side=tk.LEFT, padx=5)
        
        # Results section
        row += 1
        ttk.Separator(self.input_frame, orient=tk.HORIZONTAL).grid(row=row, column=0, columnspan=2, sticky=tk.EW, pady=10)
        
        row += 1
        ttk.Label(self.input_frame, text="Results", font=("Arial", 10, "bold")).grid(row=row, column=0, columnspan=2, pady=5)
        
        row += 1
        self.results_frame = ttk.Frame(self.input_frame)
        self.results_frame.grid(row=row, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        # Initialize result labels
        self.result_vars = {}
        result_params = [
            "time_of_flight",
            "maximum_height",
            "range",
            "current_velocity",
            "current_angle",
            "current_height",
            "current_time"
        ]
        
        result_labels = [
            "Time of flight (s)",
            "Maximum height (m)",
            "Range (m)",
            "Current velocity (m/s)",
            "Current angle (degrees)",
            "Current height (m)",
            "Current time (s)"
        ]
        
        for i, (param, label) in enumerate(zip(result_params, result_labels)):
            ttk.Label(self.results_frame, text=f"{label}:").grid(row=i, column=0, sticky=tk.W)
            var = tk.StringVar(value="0.0")
            ttk.Label(self.results_frame, textvariable=var).grid(row=i, column=1, padx=10, sticky=tk.W)
            self.result_vars[param] = var
            
    def set_callbacks(self, start_callback, pause_callback, reset_callback, environment_callback):
        self.start_callback = start_callback
        self.pause_callback = pause_callback
        self.reset_callback = reset_callback
        self.environment_callback = environment_callback
        
    def on_start(self):
        if self.start_callback:
            self.start_callback()
            
    def on_pause(self):
        if self.pause_callback:
            self.pause_callback()
            
    def on_reset(self):
        if self.reset_callback:
            self.reset_callback()
            
    def on_environment_changed(self, event=None):
        if self.environment_callback:
            self.environment_callback(self.environment_var.get())
            
    def get_input_values(self):
        return {
            "initial_velocity": self.input_vars["initial_velocity"].get(),
            "launch_angle": self.input_vars["launch_angle"].get(),
            "initial_height": self.input_vars["initial_height"].get(),
            "mass": self.input_vars["mass"].get(),
            "air_resistance": self.input_vars["air_resistance"].get(),
            "wind_speed": self.input_vars["wind_speed"].get(),
            "wind_angle": self.input_vars["wind_angle"].get(),
            "time_scale": self.input_vars["time_scale"].get()
        }
        
    def update_result(self, key, value):
        if key in self.result_vars:
            self.result_vars[key].set(f"{value:.2f}")
            
    def show_error(self, title, message):
        messagebox.showerror(title, message)

# This is a separate file, so we don't run the app here
if __name__ == "__main__":
    root = tk.Tk()
    app = ProjectileInterface(root)
    root.mainloop()