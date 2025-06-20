import pygame
import math
from tkinter import messagebox


class ProjectileSimulation:
    def __init__(self):
        self.gui = None
        self.dragging_angle = False
        self.running = False
        self.paused = False
        self.trail = []
        self.sim_data = {}
        self.time = 0

        pygame.init()
        self.width, self.height = 1000, 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Projectile Motion Simulation")
        self.clock = pygame.time.Clock()

        # Grid and world setup
        self.grid_scale = 10  # 1 square = 5 meters
        self.offset_x = 0
        self.offset_y = 0
        self.zoom_step = 5

        # Origin placed to elevate ground a bit
        self.origin = [60, self.height - 60]

    def set_gui(self, gui):
        self.gui = gui
        self.gui.root.after(1000 // 60, self.update)

    def start_simulation(self):
        try:
            iv = self.gui.input_vars["initial_velocity"].get()
            angle_deg = self.gui.input_vars["launch_angle"].get()
            h = self.gui.input_vars["initial_height"].get()
            m = self.gui.input_vars["mass"].get()
            ar = self.gui.input_vars["air_resistance"].get()
            self.time_scale = self.gui.input_vars["time_scale"].get()

            if not (0 <= angle_deg <= 180):
                messagebox.showerror("Invalid Input", "Launch angle must be between 0 and 180 degrees.")
                return
            if iv < 0:
                messagebox.showerror("Invalid Input", "Initial velocity must be a positive number.")
                return
            if m <= 0:
                messagebox.showerror("Invalid Input", "Mass must be a positive number.")
                return

            g_env = self.gui.environment_var.get()
            g = {"Earth": 9.81, "Moon": 1.62, "Mars": 3.72, "Jupiter": 24.79}[g_env]

            angle = math.radians(angle_deg)
            vx = iv * math.cos(angle)
            vy = iv * math.sin(angle)

            self.sim_data = {
                "x": 0, "y": h,
                "vx": vx, "vy": vy,
                "mass": m, "ar": ar,
                "g": g, "dt": 0.01
            }

            self.trail = [(0, h)]
            self.running = True
            self.paused = False
            self.time = 0

        except Exception as e:
            messagebox.showerror("Simulation Error", str(e))


    def reset_simulation(self):
        self.running = False
        self.paused = False
        self.trail.clear()
        self.time = 0
        for var in self.gui.result_vars.values():
            var.set("0.0")


    def toggle_pause(self):
        self.paused = not self.paused
        if self.gui and self.gui.pause_button:
            self.gui.pause_button.config(text="Resume" if self.paused else "Pause")

    def update(self):
        self.handle_events()

        if self.running and not self.paused:
            data = self.sim_data
            dt = data["dt"] * self.time_scale
            x, y, vx, vy = data["x"], data["y"], data["vx"], data["vy"]
            m, ar, g = data["mass"], data["ar"], data["g"]

            # Calculate forces and update velocity/position
            speed = math.hypot(vx, vy)
            fx = -ar * speed * vx
            fy = -ar * speed * vy - m * g

            ax = fx / m
            ay = fy / m

            vx += ax * dt
            vy += ay * dt
            
            # Store previous position for interpolation
            prev_x, prev_y = x, y
            
            x += vx * dt
            y += vy * dt

            # Check for ground collision
            if prev_y >= 0 and y < 0:  # We crossed the ground plane this frame
                # Calculate exact intersection point using linear interpolation
                t_impact = prev_y / (prev_y - y)  # Fraction of timestep when impact occurred
                x = prev_x + (x - prev_x) * t_impact
                y = 0  # Exactly at ground level
                vx = vy = 0  # Stop all motion
                self.running = False
                
                # Update final results
                impact_time = self.time + dt * t_impact
                self.gui.result_vars["time_of_flight"].set(f"{impact_time:.2f}")
                self.gui.result_vars["range"].set(f"{x:.2f}")
                
            self.sim_data.update({"x": x, "y": y, "vx": vx, "vy": vy})
            self.trail.append((x, y))
            self.time += dt

            # Update display variables
            self.gui.result_vars["current_velocity"].set(f"{math.hypot(vx, vy):.2f}")
            self.gui.result_vars["current_angle"].set(f"{math.degrees(math.atan2(vy, vx)):.2f}")
            self.gui.result_vars["current_height"].set(f"{y:.2f}")
            self.gui.result_vars["current_time"].set(f"{self.time:.2f}")
            self.gui.result_vars["maximum_height"].set(f"{max(pt[1] for pt in self.trail):.2f}")

        self.draw()
        self.gui.root.after(1000 // 60, self.update)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                self.gui.root.quit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not self.running:
                    mouse_x, mouse_y = event.pos
                    h = self.gui.input_vars["initial_height"].get()
                    base_x, base_y = self.world_to_screen(0, h)
                    dist = math.hypot(mouse_x - base_x, mouse_y - base_y)
                    if dist < 60:  # click near the arrow base
                        self.dragging_angle = True

            elif event.type == pygame.MOUSEBUTTONUP:
                if self.dragging_angle:
                    angle = self.gui.input_vars["launch_angle"].get()
                    self.gui.input_vars["launch_angle"].set(int(round(angle)))
                self.dragging_angle = False


            elif event.type == pygame.MOUSEMOTION and self.dragging_angle:
                mouse_x, mouse_y = event.pos
                h = self.gui.input_vars["initial_height"].get()
                base_x, base_y = self.world_to_screen(0, h)

                dx = mouse_x - base_x
                dy = base_y - mouse_y  # y-axis is inverted in screen space
                angle_rad = math.atan2(dy, dx)
                angle_deg = math.degrees(angle_rad)

                # Clamp angle to 0–180
                angle_deg = max(0, min(180, angle_deg))
                self.gui.input_vars["launch_angle"].set(angle_deg)


    def world_to_screen(self, x, y):
        screen_x = self.origin[0] + x * self.grid_scale + self.offset_x
        screen_y = self.origin[1] - y * self.grid_scale + self.offset_y
        return (int(screen_x), int(screen_y))

    def draw_grid(self):
        self.screen.fill((255, 255, 255))
        color = (220, 220, 220)
        font = pygame.font.SysFont("Arial", 12)

        for x in range(-1000, 1000, 5):
            sx, _ = self.world_to_screen(x, 0)
            pygame.draw.line(self.screen, color, (sx, 0), (sx, self.height))
            label = font.render(str(x), True, (0, 0, 0))
            self.screen.blit(label, (sx + 2, self.origin[1] + self.offset_y + 2))

        for y in range(0, 1000, 5):
            _, sy = self.world_to_screen(0, y)
            pygame.draw.line(self.screen, color, (0, sy), (self.width, sy))

        # Draw X and Y axes
        pygame.draw.line(self.screen, (0, 0, 0), self.world_to_screen(-1000, 0), self.world_to_screen(1000, 0), 2)
        pygame.draw.line(self.screen, (0, 0, 0), self.world_to_screen(0, -1000), self.world_to_screen(0, 1000), 2)

    def draw(self):
        self.draw_grid()

        if len(self.trail) > 1:
            for i in range(len(self.trail) - 1):
                start = self.world_to_screen(*self.trail[i])
                end = self.world_to_screen(*self.trail[i + 1])
                pygame.draw.line(self.screen, (0, 100, 255), start, end, 2)

        if self.trail:
            x, y = self.trail[-1]
        else:
            # Show ball at initial height before simulation starts
            try:
                h = self.gui.input_vars["initial_height"].get()
            except:
                h = 0
            x, y = 0, h


        pygame.draw.circle(self.screen, (255, 0, 0), self.world_to_screen(x, y), 6)
        # Draw launch angle arrow before simulation starts
        if not self.running and not self.trail:
            try:
                angle_deg = self.gui.input_vars["launch_angle"].get()
                angle_rad = math.radians(angle_deg)
                iv = self.gui.input_vars["initial_velocity"].get()
                arrow_length = min(250, max(20, iv * 1.5))  


                # Compute arrow end in screen coordinates
                h = self.gui.input_vars["initial_height"].get()
                start_screen = self.world_to_screen(0, h)

                end_x = start_screen[0] + arrow_length * math.cos(angle_rad)
                end_y = start_screen[1] - arrow_length * math.sin(angle_rad)  # subtract because screen y is downward

                pygame.draw.line(self.screen, (0, 0, 255), start_screen, (end_x, end_y), 3)

                head_length = 10
                head_angle = math.pi / 6
                for side in [-1, 1]:
                    side_angle = angle_rad + side * head_angle
                    hx = end_x - head_length * math.cos(side_angle)
                    hy = end_y + head_length * math.sin(side_angle)
                    pygame.draw.line(self.screen, (0, 0, 255), (end_x, end_y), (hx, hy), 2)
            except:
                pass 

        pygame.display.flip()

    def run(self):
        self.gui.run()

    def zoom_in(self):
        self.grid_scale += self.zoom_step

    def zoom_out(self):
        if self.grid_scale > self.zoom_step:
            self.grid_scale -= self.zoom_step
