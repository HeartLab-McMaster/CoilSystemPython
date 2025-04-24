This project is an extended version of [atelier-ritz/CoilSystemPython](https://github.com/atelier-ritz/CoilSystemPython), developed to support **multi-camera feedback**, **joystick control**, **multi-view vector projection**, and **programmable magnetic field waveform generation**. It is designed for research applications involving soft robotics, magnetic manipulation, and real-time field visualization.

## Key Features

###  1. Multi-Camera Integration
- Supports **three synchronized Pylon cameras**
- Each camera displays a live feed
- Field vector projections (XZ, XY, YZ) are overlaid in real-time

###  2. Joystick-Based Magnetic Field Control
- Integrated with **PS3 DualShock controller**
- Analog joystick axes control X, Y, Z magnetic field components
- Provides smooth real-time user interaction

###  3. Multi-View Vector Field Projection
- Displays XZ, XY, and YZ vector projections aligned with camera feeds
- Updates in real time without interrupting GUI responsiveness
- Helps visualize the magnetic field in a physical 3D space

###  4. Programmable Field Control (CSV or Formula)
- Load waveform data from CSV file with format:
t, X1_val, X2_val, Y1_val, Y2_val, Z1_val, Z2_val
- Or define analytical functions (e.g., `sin`, `square`) for dynamic waveform generation
- Field values are synchronized to simulation time or experiment timeline

## 🚀 How to Run


```bash
1. Clone the repository:

git clone https://github.com/heartlab-mcmaster/coilsystempython

2. Install dependencies:

pip install -r requirements.txt

3. Connect your hardware:

Ensure your s826 DAC board is connected and drivers are installed
Plug in three Pylon cameras
Optionally connect PS3 controller

4. Launch GUI:

python3 main.py
