import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys

class ProjectileGUI:
    def __init__(self):
        # Initialize Tkinter
        self.root = tk.Tk()
        self.root.title("Projectile Motion Simulator")
        self.root.geometry("1200x700")
        self.root.resizable(False, False)
        
        # Create frames
        self.input_frame = ttk.LabelFrame(self.root, text="Simulation Parameters")
        self.input_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.Y)
        
        # Create a frame that will hold our simulation
        # Make it slightly smaller so the title is always visible
        self.simulation_container = ttk.LabelFrame(self.root, text="Simulation")
        self.simulation_container.pack(side=tk.RIGHT, padx=10, pady=10, expand=True, fill=tk.BOTH)
        
        # Create a frame inside the container that will be our pygame surface
        # This creates some padding for the simulation
        self.simulation_frame = ttk.Frame(self.simulation_container)
        self.simulation_frame.pack(padx=5, pady=20, expand=True, fill=tk.BOTH)
        
        # Create input variables dictionary
        self.input_vars = {}
        
        # Create input fields
        self.create_input_fields()
        
        # Set up environment for pygame
        os.environ['SDL_WINDOWID'] = str(self.simulation_frame.winfo_id())
        if sys.platform == "win32":
            os.environ['SDL_VIDEODRIVER'] = 'windib'
        
        # We don't initialize pygame here - will be done in the simulator
        
    def create_input_fields(self):
        # Initialize variables
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
        
        row += 1
        
        # Add buttons
        button_frame = ttk.Frame(self.input_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=10)
        
        self.start_button = ttk.Button(button_frame, text="Start")
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.pause_button = ttk.Button(button_frame, text="Pause/Resume")
        self.pause_button.pack(side=tk.LEFT, padx=5)
        
        self.reset_button = ttk.Button(button_frame, text="Reset")
        self.reset_button.pack(side=tk.LEFT, padx=5)
        
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
    
    def set_command_callbacks(self, start_func, pause_func, reset_func, env_change_func):
        # Connect the buttons to the simulation functions
        self.start_button.config(command=start_func)
        self.pause_button.config(command=pause_func)
        self.reset_button.config(command=reset_func)
        self.environment_var.trace_add("write", lambda *args: env_change_func())
    
    def run(self):
        # Start the tkinter main loop
        self.root.mainloop()

if __name__ == "__main__":
    # This is just for testing - normally we would import this and use it with the simulator
    gui = ProjectileGUI()
    gui.run()