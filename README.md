
# Projectile Simulation Project

This repository contains three versions of a projectile motion simulation implemented in Python.

## Versions

### V1 - Basic Script
- `projectileV1.py`: A simple, standalone script that calculates and prints projectile motion results based on initial velocity and angle.

### V2 - CLI Modular Version
- Modular structure with separate files for simulation logic and interface.
- Files:
  - `projectile_interface.py`: Handles user input/output.
  - `projectile_simulation.py`: Contains physics calculations.
  - `main.py`: Entry point of the program.

### V3 - GUI Version
- Adds a graphical user interface for easier interaction.
- Uses `tkinter` for building the GUI.
- Files:
  - `projectile_gui.py`: GUI implementation.
  - `projectile_simulation.py`: Reused or enhanced simulation logic.
  - `main.py`: Starts the GUI application.

## Requirements

- Python 3.10+
- (For GUI) `tkinter` (usually included with Python)

## How to Run

```bash
# For V1
python projectileV1.py

# For V2
cd projectileV2
python main.py

# For V3 (GUI)
cd projectileV3
python main.py
```

## License

This project is open-source and free to use for educational purposes.
