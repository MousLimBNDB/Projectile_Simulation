import tkinter as tk
from tkinter import ttk, messagebox
import pygame
import sys
import math
import numpy as np
from pygame.locals import *
import os

class ProjectileSimulation:
    def __init__(self):
        # Physics constants
        self.g = 9.81  # Gravity (m/s²)
        
        # Initialize Tkinter
        self.root = tk.Tk()
        self.root.title("Projectile Motion Simulator")
        self.root.geometry("1200x700")
        self.root.resizable(False, False)
        
        # Create frames
        self.input_frame = ttk.LabelFrame(self.root, text="Simulation Parameters")
        self.input_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.Y)
        
        self.simulation_frame = ttk.LabelFrame(self.root, text="Simulation")
        self.simulation_frame.pack(side=tk.RIGHT, padx=10, pady=10, expand=True, fill=tk.BOTH)
        
        # Initialize pygame
        os.environ['SDL_WINDOWID'] = str(self.simulation_frame.winfo_id())
        if sys.platform == "win32":
            os.environ['SDL_VIDEODRIVER'] = 'windib'
        
        pygame.init()
        
        # Create pygame surface
        self.width, self.height = 800, 600
        self.pygame_screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.init()
        
        # Create input variables dictionary
        self.input_vars = {}
        
        # Create input fields
        self.create_input_fields()
        
        # Simulation state
        self.running = False
        self.paused = False
        self.simulation_data = {}
        self.current_time = 0
        self.time_scale = 1.0  # For speeding up or slowing down simulation
        self.trail = []  # Store previous positions for trail effect
        self.max_trail_length = 100
        
        # Scale and offset for display
        self.scale_factor = 10  # Pixels per meter
        self.offset_x = 50  # Offset from left edge
        self.offset_y = self.height - 50  # Offset from bottom edge
        
        # Initialize pygame clock
        self.clock = pygame.time.Clock()
        self.fps = 60
        
        # Initial draw for simulation area
        self.pygame_screen.fill((255, 255, 255))
        self.draw_coordinate_system()
        pygame.display.flip()
        
        # Set up the timer for simulation updates
        self.root.after(100, self.update_simulation)
        
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
        env_dropdown.bind("<<ComboboxSelected>>", self.update_environment)
        
        row += 1
        
        # Add buttons
        button_frame = ttk.Frame(self.input_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Start", command=self.start_simulation).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Pause/Resume", command=self.toggle_pause).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Reset", command=self.reset_simulation).pack(side=tk.LEFT, padx=5)
        
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
    
    def update_environment(self, event=None):
        # Update gravity based on environment
        environment = self.environment_var.get()
        gravity_values = {
            "Earth": 9.81,
            "Moon": 1.62,
            "Mars": 3.72,
            "Jupiter": 24.79
        }
        self.g = gravity_values.get(environment, 9.81)
    
    def start_simulation(self):
        # Get input values
        try:
            initial_velocity = self.input_vars["initial_velocity"].get()
            launch_angle = self.input_vars["launch_angle"].get()
            initial_height = self.input_vars["initial_height"].get()
            mass = self.input_vars["mass"].get()
            air_resistance = self.input_vars["air_resistance"].get()
            wind_speed = self.input_vars["wind_speed"].get()
            wind_angle = self.input_vars["wind_angle"].get()
            self.time_scale = self.input_vars["time_scale"].get()
            
            # Validate inputs
            if initial_velocity < 0 or mass <= 0:
                messagebox.showerror("Invalid Input", "Initial velocity cannot be negative and mass must be positive")
                return
            
            # Convert angle to radians
            angle_rad = math.radians(launch_angle)
            wind_angle_rad = math.radians(wind_angle)
            
            # Calculate initial velocity components
            vx0 = initial_velocity * math.cos(angle_rad)
            vy0 = initial_velocity * math.sin(angle_rad)
            
            # Calculate wind velocity components
            wind_vx = wind_speed * math.cos(wind_angle_rad)
            wind_vy = wind_speed * math.sin(wind_angle_rad)
            
            # Store simulation parameters
            self.simulation_data = {
                "initial_x": 0,
                "initial_y": initial_height,
                "initial_vx": vx0,
                "initial_vy": vy0,
                "current_x": 0,
                "current_y": initial_height,
                "current_vx": vx0,
                "current_vy": vy0,
                "mass": mass,
                "air_resistance": air_resistance,
                "wind_vx": wind_vx,
                "wind_vy": wind_vy,
                "dt": 0.01  # Time step for simulation
            }
            
            # Reset simulation state
            self.current_time = 0
            self.trail = [(0, initial_height)]
            self.running = True
            self.paused = False
            
            # Pre-calculate estimated flight time and range for scaling
            # These are rough estimates without air resistance
            estimated_flight_time = (vy0 + math.sqrt(vy0**2 + 2*self.g*initial_height)) / self.g
            estimated_range = vx0 * estimated_flight_time
            
            # Adjust scale factor based on estimated range and height
            max_height = initial_height + (vy0**2) / (2 * self.g)
            self.scale_factor = min(
                (self.width - 2*self.offset_x) / max(1, estimated_range),
                (self.height - 2*self.offset_y) / max(1, max_height)
            ) * 0.8  # 80% of available space
            
            # Ensure scale factor is reasonable
            self.scale_factor = max(1, min(50, self.scale_factor))
            
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numerical values")
    
    def reset_simulation(self):
        self.running = False
        self.paused = False
        self.trail = []
        self.current_time = 0
        
        # Clear the simulation display
        self.pygame_screen.fill((255, 255, 255))
        self.draw_coordinate_system()
        pygame.display.flip()
        
        # Reset result fields
        for var in self.result_vars.values():
            var.set("0.0")
    
    def toggle_pause(self):
        if self.running:
            self.paused = not self.paused
    
    def update_simulation(self):
        if self.running and not self.paused:
            # Get current state
            x = self.simulation_data["current_x"]
            y = self.simulation_data["current_y"]
            vx = self.simulation_data["current_vx"]
            vy = self.simulation_data["current_vy"]
            mass = self.simulation_data["mass"]
            air_resistance = self.simulation_data["air_resistance"]
            wind_vx = self.simulation_data["wind_vx"]
            wind_vy = self.simulation_data["wind_vy"]
            dt = self.simulation_data["dt"] * self.time_scale
            
            # Calculate air resistance force
            rel_vx = vx - wind_vx
            rel_vy = vy - wind_vy
            rel_v = math.sqrt(rel_vx**2 + rel_vy**2)
            
            if rel_v > 0:
                drag_force_x = -air_resistance * rel_v * rel_vx
                drag_force_y = -air_resistance * rel_v * rel_vy
            else:
                drag_force_x = 0
                drag_force_y = 0
            
            # Calculate acceleration
            ax = drag_force_x / mass
            ay = -self.g + drag_force_y / mass
            
            # Update velocity
            vx += ax * dt
            vy += ay * dt
            
            # Update position
            x += vx * dt
            y += vy * dt
            
            # Update current state
            self.simulation_data["current_x"] = x
            self.simulation_data["current_y"] = y
            self.simulation_data["current_vx"] = vx
            self.simulation_data["current_vy"] = vy
            
            # Add to trail
            self.trail.append((x, y))
            if len(self.trail) > self.max_trail_length:
                self.trail = self.trail[-self.max_trail_length:]
            
            # Update time
            self.current_time += dt
            
            # Check if projectile has hit the ground
            if y <= 0 and vy < 0:
                self.running = False
                # Calculate final x position for range
                final_x = x - vx * (y / vy)  # Adjust x for exact ground impact
                self.simulation_data["current_x"] = final_x
                self.simulation_data["current_y"] = 0
                
                # Update trail
                self.trail[-1] = (final_x, 0)
                
                # Update results
                self.result_vars["time_of_flight"].set(f"{self.current_time:.2f}")
                self.result_vars["range"].set(f"{final_x:.2f}")
            
            # Update results during flight
            current_v = math.sqrt(vx**2 + vy**2)
            current_angle = math.degrees(math.atan2(vy, vx))
            
            self.result_vars["current_velocity"].set(f"{current_v:.2f}")
            self.result_vars["current_angle"].set(f"{current_angle:.2f}")
            self.result_vars["current_height"].set(f"{y:.2f}")
            self.result_vars["current_time"].set(f"{self.current_time:.2f}")
            
            # Calculate and update maximum height
            max_height = max([point[1] for point in self.trail])
            self.result_vars["maximum_height"].set(f"{max_height:.2f}")
            
        # Render the simulation
        self.render_simulation()
        
        # Process pygame events to prevent freezing
        for event in pygame.event.get():
            pass
        
        # Schedule the next update
        self.root.after(int(1000/self.fps), self.update_simulation)
    
    def render_simulation(self):
        # Clear the screen
        self.pygame_screen.fill((255, 255, 255))
        
        # Draw coordinate system
        self.draw_coordinate_system()
        
        # Draw trail
        if len(self.trail) > 1:
            scaled_trail = [(self.offset_x + self.scale_factor * x, 
                             self.offset_y - self.scale_factor * y) 
                           for x, y in self.trail]
            
            # Draw trail with gradient color (blue to red)
            for i in range(len(scaled_trail) - 1):
                progress = i / (len(scaled_trail) - 1)
                color = (int(255 * progress), 0, int(255 * (1 - progress)))
                pygame.draw.line(self.pygame_screen, color, scaled_trail[i], scaled_trail[i+1], 2)
        
        # Draw projectile (current position)
        if self.trail:
            x, y = self.trail[-1]
            screen_x = self.offset_x + self.scale_factor * x
            screen_y = self.offset_y - self.scale_factor * y
            pygame.draw.circle(self.pygame_screen, (255, 0, 0), (int(screen_x), int(screen_y)), 5)
        
        # Update display
        pygame.display.flip()
    
    def draw_coordinate_system(self):
        # Draw ground
        pygame.draw.line(self.pygame_screen, (0, 0, 0), 
                         (self.offset_x, self.offset_y), 
                         (self.width - self.offset_x, self.offset_y), 2)
        
        # Draw x-axis ticks and labels
        max_x = (self.width - 2 * self.offset_x) / self.scale_factor
        tick_interval = self.get_tick_interval(max_x)
        
        for i in range(0, int(max_x) + 1, tick_interval):
            tick_x = self.offset_x + i * self.scale_factor
            # Draw tick
            pygame.draw.line(self.pygame_screen, (0, 0, 0), 
                            (tick_x, self.offset_y), 
                            (tick_x, self.offset_y + 5), 1)
            
            # Draw label
            font = pygame.font.SysFont('Arial', 12)
            text = font.render(f"{i}m", True, (0, 0, 0))
            self.pygame_screen.blit(text, (tick_x - 10, self.offset_y + 10))
        
        # Draw y-axis
        pygame.draw.line(self.pygame_screen, (0, 0, 0), 
                         (self.offset_x, self.offset_y), 
                         (self.offset_x, self.offset_y - self.height + 2 * self.offset_y), 2)
        
        # Draw y-axis ticks and labels
        max_y = (self.height - 2 * self.offset_y) / self.scale_factor
        tick_interval = self.get_tick_interval(max_y)
        
        for i in range(0, int(max_y) + 1, tick_interval):
            tick_y = self.offset_y - i * self.scale_factor
            # Draw tick
            pygame.draw.line(self.pygame_screen, (0, 0, 0), 
                            (self.offset_x, tick_y), 
                            (self.offset_x - 5, tick_y), 1)
            
            # Draw label
            font = pygame.font.SysFont('Arial', 12)
            text = font.render(f"{i}m", True, (0, 0, 0))
            self.pygame_screen.blit(text, (self.offset_x - 30, tick_y - 5))
    
    def get_tick_interval(self, max_val):
        # Calculate appropriate tick interval
        if max_val <= 10:
            return 1
        elif max_val <= 50:
            return 5
        elif max_val <= 100:
            return 10
        elif max_val <= 500:
            return 50
        else:
            return 100
    
    def run(self):
        # Start the tkinter main loop
        self.root.mainloop()


if __name__ == "__main__":
    app = ProjectileSimulation()
    app.run()