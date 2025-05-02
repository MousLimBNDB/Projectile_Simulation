import tkinter as tk
from projectile_interface import ProjectileInterface
from projectile_simulation import ProjectileSimulation

def main():
    # Create the main window
    root = tk.Tk()
    
    # Create the interface
    interface = ProjectileInterface(root)
    
    # Create the simulation with a reference to the interface
    simulation = ProjectileSimulation(interface.simulation_frame)
    
    # Connect interface callbacks to simulation methods
    interface.set_callbacks(
        start_callback=lambda: simulation.start_simulation(interface.get_input_values()),
        pause_callback=simulation.toggle_pause,
        reset_callback=simulation.reset_simulation,
        environment_callback=simulation.update_environment
    )
    
    # Set up a callback for the simulation to update the interface
    simulation.set_result_callback(interface.update_result)
    simulation.set_error_callback(interface.show_error)
    
    # Start the update loop for the simulation
    simulation.start_update_loop()
    
    # Start the Tkinter main loop
    root.mainloop()

if __name__ == "__main__":
    main()