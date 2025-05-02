import pygame
import math
import numpy as np
from tkinter import messagebox
from projectile_gui import ProjectileGUI

class ProjectileSimulation:
    def __init__(self):
        # Physics constants
        self.g = 9.81  # Gravity (m/s²)
        
        # Create GUI
        self.gui = ProjectileGUI()
        
        # Initialize pygame
        pygame.init()
        
        # Create pygame surface - make it slightly smaller than frame
        self.width, self.height = 780, 560
        self.pygame_screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.init()
        
        # Set up event handling to prevent flickering
        # This is crucial for fixing the mouse hover flickering issue
        pygame.event.set_allowed([pygame.QUIT])
        pygame.event.set_blocked(pygame.MOUSEMOTION)
        
        # Simulation state
        self.running = False
        self.paused = False
        self.simulation_data = {}
        self.current_time = 0
        self.time_scale = 1.0
        self.trail = []
        self.max_trail_length = 100
        
        # Scale and offset for display
        self.scale_factor = 10
        self.offset_x = 50
        self.offset_y = self.height - 50
        
        # Initialize pygame clock
        self.clock = pygame.time.Clock()
        self.fps = 60
        
        # Set up arrow indicator for off-screen projectile
        self.arrow_size = 15
        self.arrow_color = (255, 0, 0)
        self.arrow_distance = 20  # Distance from edge of screen
        
        # Connect GUI buttons to simulation functions
        self.gui.set_command_callbacks(
            self.start_simulation,
            self.toggle_pause,
            self.reset_simulation,
            self.update_environment
        )
        
        # Initial draw for simulation area
        self.pygame_screen.fill((255, 255, 255))
        self.draw_coordinate_system()
        pygame.display.flip()
        
        # Set up the timer for simulation updates
        self.gui.root.after(100, self.update_simulation)

    def update_environment(self):
        # Update gravity based on environment
        environment = self.gui.environment_var.get()
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
            initial_velocity = self.gui.input_vars["initial_velocity"].get()
            launch_angle = self.gui.input_vars["launch_angle"].get()
            initial_height = self.gui.input_vars["initial_height"].get()
            mass = self.gui.input_vars["mass"].get()
            air_resistance = self.gui.input_vars["air_resistance"].get()
            wind_speed = self.gui.input_vars["wind_speed"].get()
            wind_angle = self.gui.input_vars["wind_angle"].get()
            self.time_scale = self.gui.input_vars["time_scale"].get()
            
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
        for var in self.gui.result_vars.values():
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
                self.gui.result_vars["time_of_flight"].set(f"{self.current_time:.2f}")
                self.gui.result_vars["range"].set(f"{final_x:.2f}")
            
            # Update results during flight
            current_v = math.sqrt(vx**2 + vy**2)
            current_angle = math.degrees(math.atan2(vy, vx))
            
            self.gui.result_vars["current_velocity"].set(f"{current_v:.2f}")
            self.gui.result_vars["current_angle"].set(f"{current_angle:.2f}")
            self.gui.result_vars["current_height"].set(f"{y:.2f}")
            self.gui.result_vars["current_time"].set(f"{self.current_time:.2f}")
            
            # Calculate and update maximum height
            max_height = max([point[1] for point in self.trail])
            self.gui.result_vars["maximum_height"].set(f"{max_height:.2f}")
            
        # Render the simulation
        self.render_simulation()
        
        # Process pygame events but filter out mouse motion to prevent flickering
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.gui.root.destroy()
        
        # Schedule the next update
        self.gui.root.after(int(1000/self.fps), self.update_simulation)
    
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
        
        # Get projectile position
        if self.trail:
            x, y = self.trail[-1]
            screen_x = self.offset_x + self.scale_factor * x
            screen_y = self.offset_y - self.scale_factor * y
            
            # Check if projectile is on screen
            on_screen = (0 <= screen_x < self.width and 0 <= screen_y < self.height)
            
            if on_screen:
                # Draw projectile
                pygame.draw.circle(self.pygame_screen, (255, 0, 0), (int(screen_x), int(screen_y)), 5)
            else:
                # Draw arrow pointing to off-screen projectile
                self.draw_direction_arrow(screen_x, screen_y)
        
        # Update display
        pygame.display.flip()
    
    def draw_direction_arrow(self, x, y):
        # Calculate the angle to the projectile from center of screen
        center_x = self.width / 2
        center_y = self.height / 2
        
        dx = x - center_x
        dy = y - center_y
        
        # Calculate angle to projectile
        angle = math.atan2(dy, dx)
        
        # Determine intersection with screen edge
        # This will be where we place our arrow
        border_x, border_y = self.get_screen_border_point(angle)
        
        # Draw arrow at border pointing in direction of projectile
        self.draw_arrow(border_x, border_y, angle)
    
    def get_screen_border_point(self, angle):
        # Calculate where a ray at given angle intersects screen edge
        width_half = self.width / 2
        height_half = self.height / 2
        
        # Define screen borders
        border_dist_x = width_half - self.arrow_distance
        border_dist_y = height_half - self.arrow_distance
        
        # Calculate tangent value
        tan_angle = math.tan(angle)
        
        # Determine which border to use based on angle
        if abs(tan_angle) < border_dist_x / border_dist_y:
            # Intersects with left/right border
            if math.cos(angle) > 0:  # Right side
                x = width_half + border_dist_x
            else:  # Left side
                x = width_half - border_dist_x
            y = height_half + tan_angle * (x - width_half)
        else:
            # Intersects with top/bottom border
            if math.sin(angle) > 0:  # Bottom side
                y = height_half + border_dist_y
            else:  # Top side
                y = height_half - border_dist_y
            x = width_half + (y - height_half) / tan_angle if tan_angle != 0 else width_half
        
        return x, y
    
    def draw_arrow(self, x, y, angle):
        # Draw a triangle pointing in the direction of angle
        points = []
        
        # Arrow point
        points.append((
            x + self.arrow_size * math.cos(angle),
            y + self.arrow_size * math.sin(angle)
        ))
        
        # Arrow wings
        wing_angle1 = angle + 2.5  # About 150 degrees
        wing_angle2 = angle - 2.5
        
        points.append((
            x + self.arrow_size * 0.7 * math.cos(wing_angle1),
            y + self.arrow_size * 0.7 * math.sin(wing_angle1)
        ))
        
        points.append((
            x + self.arrow_size * 0.7 * math.cos(wing_angle2),
            y + self.arrow_size * 0.7 * math.sin(wing_angle2)
        ))
        
        # Draw the arrow
        pygame.draw.polygon(self.pygame_screen, self.arrow_color, points)
    
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
        self.gui.run()


if __name__ == "__main__":
    app = ProjectileSimulation()
    app.run()