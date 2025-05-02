import pygame
import sys
import math
import os
from pygame.locals import *

class ProjectileSimulation:
    def __init__(self, frame):
        # Physics constants
        self.g = 9.81  # Gravity (m/s²)
        
        # Get frame info for embedding pygame
        self.frame = frame
        self.frame_id = str(frame.winfo_id())
        
        # Setup pygame environment
        os.environ['SDL_WINDOWID'] = self.frame_id
        if sys.platform == "win32":
            os.environ['SDL_VIDEODRIVER'] = 'windib'
        
        # Initialize pygame
        pygame.init()
        
        # Set the dimensions slightly smaller to ensure "Simulation" heading is visible
        # The original size was 800x600, we'll make it a bit smaller
        self.width, self.height = 780, 560
        
        # Create pygame surface
        self.pygame_screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.init()
        
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
        
        # Result callback
        self.result_callback = None
        self.error_callback = None
        
        # Arrow properties for off-screen indicator
        self.arrow_size = 15
        self.arrow_color = (255, 0, 0)
        
        # Initial draw for simulation area
        self.pygame_screen.fill((255, 255, 255))
        self.draw_coordinate_system()
        pygame.display.flip()
    
    def set_result_callback(self, callback):
        self.result_callback = callback
    
    def set_error_callback(self, callback):
        self.error_callback = callback
    
    def update_environment(self, environment):
        # Update gravity based on environment
        gravity_values = {
            "Earth": 9.81,
            "Moon": 1.62,
            "Mars": 3.72,
            "Jupiter": 24.79
        }
        self.g = gravity_values.get(environment, 9.81)
    
    def start_simulation(self, input_values):
        # Get input values
        try:
            initial_velocity = input_values["initial_velocity"]
            launch_angle = input_values["launch_angle"]
            initial_height = input_values["initial_height"]
            mass = input_values["mass"]
            air_resistance = input_values["air_resistance"]
            wind_speed = input_values["wind_speed"]
            wind_angle = input_values["wind_angle"]
            self.time_scale = input_values["time_scale"]
            
            # Validate inputs
            if initial_velocity < 0 or mass <= 0:
                if self.error_callback:
                    self.error_callback("Invalid Input", "Initial velocity cannot be negative and mass must be positive")
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
            
            # Use fixed scale factor as in the original code
            self.scale_factor = 10  # Fixed pixel per meter scale
            
        except ValueError:
            if self.error_callback:
                self.error_callback("Invalid Input", "Please enter valid numerical values")
    
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
        if self.result_callback:
            result_keys = ["time_of_flight", "maximum_height", "range", 
                          "current_velocity", "current_angle", "current_height", "current_time"]
            for key in result_keys:
                self.result_callback(key, 0.0)
    
    def toggle_pause(self):
        if self.running:
            self.paused = not self.paused
    
    def start_update_loop(self):
        # Set up the timer for simulation updates
        self.frame.after(int(1000/self.fps), self.update_simulation)
    
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
                if self.result_callback:
                    self.result_callback("time_of_flight", self.current_time)
                    self.result_callback("range", final_x)
            
            # Update results during flight
            current_v = math.sqrt(vx**2 + vy**2)
            current_angle = math.degrees(math.atan2(vy, vx))
            
            if self.result_callback:
                self.result_callback("current_velocity", current_v)
                self.result_callback("current_angle", current_angle)
                self.result_callback("current_height", y)
                self.result_callback("current_time", self.current_time)
                
                # Calculate and update maximum height
                max_height = max([point[1] for point in self.trail])
                self.result_callback("maximum_height", max_height)
        
        # Render the simulation
        self.render_simulation()
        
        # Process pygame events to prevent freezing
        # Only process essential events to avoid flickering
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            # Ignore mouse motion events which can cause flickering
            elif event.type != MOUSEMOTION:
                pass
        
        # Schedule the next update
        self.frame.after(int(1000/self.fps), self.update_simulation)
    
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
        is_visible = False
        if self.trail:
            x, y = self.trail[-1]
            screen_x = self.offset_x + self.scale_factor * x
            screen_y = self.offset_y - self.scale_factor * y
            
            # Check if projectile is on screen
            if (0 <= screen_x <= self.width and 0 <= screen_y <= self.height):
                # Draw the projectile if it's on screen
                pygame.draw.circle(self.pygame_screen, (255, 0, 0), (int(screen_x), int(screen_y)), 5)
                is_visible = True
            else:
                # Draw arrow pointing to the projectile if it's off screen
                self.draw_offscreen_indicator(screen_x, screen_y)
        
        # Update display
        pygame.display.flip()
    
    def draw_offscreen_indicator(self, x, y):
        """Draw an arrow pointing to the off-screen projectile"""
        # Calculate arrow position and direction
        arrow_x = min(max(self.arrow_size, x), self.width - self.arrow_size)
        arrow_y = min(max(self.arrow_size, y), self.height - self.arrow_size)
        
        # If arrow is at boundary, it's offscreen in that direction
        at_boundary = False
        
        if x < self.arrow_size:
            arrow_x = self.arrow_size + 5
            at_boundary = True
        elif x > self.width - self.arrow_size:
            arrow_x = self.width - self.arrow_size - 5
            at_boundary = True
            
        if y < self.arrow_size:
            arrow_y = self.arrow_size + 5
            at_boundary = True
        elif y > self.height - self.arrow_size:
            arrow_y = self.height - self.arrow_size - 5
            at_boundary = True
        
        if at_boundary:
            # Calculate direction vector from arrow to projectile
            dx = x - arrow_x
            dy = y - arrow_y
            
            # Normalize
            length = math.sqrt(dx*dx + dy*dy)
            if length > 0:
                dx /= length
                dy /= length
            
            # Draw arrow at the edge pointing in the direction of the projectile
            self.draw_arrow(int(arrow_x), int(arrow_y), dx, dy)
    
    def draw_arrow(self, x, y, dx, dy):
        """Draw an arrow at (x,y) pointing in direction (dx,dy)"""
        # Arrow size
        size = self.arrow_size
        
        # Calculate end point of the arrow
        end_x = x + int(dx * size)
        end_y = y + int(dy * size)
        
        # Draw the arrow line
        pygame.draw.line(self.pygame_screen, self.arrow_color, (x, y), (end_x, end_y), 2)
        
        # Calculate the arrow head
        angle = math.atan2(dy, dx)
        head_size = size * 0.5
        
        # Calculate the points for the arrow head
        head1_x = end_x - head_size * math.cos(angle + math.pi/6)
        head1_y = end_y - head_size * math.sin(angle + math.pi/6)
        
        head2_x = end_x - head_size * math.cos(angle - math.pi/6)
        head2_y = end_y - head_size * math.sin(angle - math.pi/6)
        
        # Draw the arrow head
        pygame.draw.polygon(self.pygame_screen, self.arrow_color, 
                           [(end_x, end_y), (int(head1_x), int(head1_y)), (int(head2_x), int(head2_y))])
    
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