from projectile_gui import ProjectileGUI
from projectile_simulation import ProjectileSimulation

def main():
    simulation = ProjectileSimulation()
    gui = ProjectileGUI(simulation)
    simulation.set_gui(gui)
    simulation.run()

if __name__ == "__main__":
    main()
