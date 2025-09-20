# 🤖 Hackathon Project - Robot Scheduler

A comprehensive system for scheduling, simulating, and visualizing industrial robot operations in a shared workspace with collision detection and prevention.

## 📋 Overview

This project provides a complete solution for:
- **Input parsing** of robot configurations and operations
- **Operation scheduling** for multiple industrial robots
- **Collision detection and prevention** in shared workspaces
- **2D visualization** of robot trajectories
- **Web-based interface** for simulation control

The system efficiently schedules operations for multiple robots while ensuring they don't collide, and provides a visual interface to monitor and control the simulation.

## 🚀 Features

- **Collision Detection**: Real-time collision detection with safety margins
- **Preventive Scheduling**: Proactive collision avoidance through staggered starts
- **Web Visualization**: Interactive visualization of robot movements
- **RESTful API**: Flask-based backend for easy integration
- **File Upload**: Support for custom scenario files
- **Real-time Controls**: Play, pause, reset, and emergency stop functionality

## 🏗️ Project Structure

```
robotics-hackathon-2025/
├── src/
│   ├── input_parser.py      # Parse input files and configurations
│   ├── scheduler.py         # Assign operations to robots
│   ├── trajectory_planner.py # Plan robot paths and trajectories
│   ├── collision_checker.py # Detect and prevent collisions
│   ├── kinematics.py        # Robot reachability and kinematics
│   ├── output_generator.py  # Generate output schedule files
│   ├── visualizer.py        # 3D visualization (Matplotlib)
│   ├── main.py             # Main application entry point
│   └── app.py              # Flask web server
├── data/
│   ├── input.txt           # Example input scenario
│   └── output.txt          # Generated output schedule
├── web/
│   └── index.html          # Web interface
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/anasmostafa23/robo_hackathon.git
   cd robo_hackathon
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   # Method 1: Command line
   python src/main.py
   
   # Method 2: Web interface
   python src/app.py
   ```

## 📖 Usage

### Web Interface (Recommended)

1. Start the web server:
   ```bash
   python src/app.py
   ```

2. Open your browser to `http://localhost:5000`

3. Upload an input file or use the example scenario

4. Click "Run Scheduler" to generate the robot schedule

5. Use the visualization controls to play, pause, or scrub through the simulation

### Command Line Interface

```bash
# Process a specific input file
python src/main.py data/input.txt

# Use default input file
python src/main.py
```

## 📊 Input File Format

The input file follows this structure:

```
K N
base_x1 base_y1 base_z1
base_x2 base_y2 base_z2
...
joint1_min joint1_max joint1_v_max joint1_a_max
joint2_min joint2_max joint2_v_max joint2_a_max
...
tool_clearance safe_distance
pick_x1 pick_y1 pick_z1 place_x1 place_y1 place_z1 operation_time1
pick_x2 pick_y2 pick_z2 place_x2 place_y2 place_z2 operation_time2
...
```

### Example Input:
```
2 3
0.0 0.0 0.0
2.5 0.0 0.0
-170.0 170.0 100.0 500.0
-120.0 120.0 90.0 450.0
-170.0 170.0 100.0 500.0
-120.0 120.0 90.0 450.0
-270.0 270.0 180.0 720.0
-270.0 270.0 180.0 720.0
0.25 0.5
1.0 1.0 0.5  1.5 1.5 0.5  2.0
0.5 2.0 0.8  2.0 2.0 0.8  1.5
2.0 1.0 0.6  0.5 1.5 0.6  2.5
```

## 🌐 API Endpoints

The Flask server provides these REST API endpoints:

- `GET /` - Serve the web interface
- `POST /api/run_scheduler` - Process input and generate schedule
- `POST /api/parse_output` - Parse output for visualization
- `GET /api/scenarios` - Get available example scenarios
- `GET /api/health` - Server health check

## 🔧 Configuration

### Key Parameters:
- **Tool Clearance**: Safety margin around robot tools (meters)
- **Safe Distance**: Minimum distance between robots (meters)
- **Max Velocity**: Maximum robot movement speed (m/s)
- **Max Acceleration**: Maximum robot acceleration (m/s²)

### Robot Specifications:
- 6-axis industrial robots
- Configurable joint limits and speeds
- Reachability checking for operation validation

## 🎯 Algorithm Details

### Scheduling Algorithm
- Operations are assigned to the closest available robot
- Trapezoidal velocity profiles for smooth movement
- Time-optimal path planning

### Collision Prevention
- Proactive staggered start times
- Real-time collision detection during simulation
- Safety margin enforcement

## 📈 Output Format

The system generates an output file with:
- Makespan (total operation time)
- Robot schedules with waypoints (time, x, y, z coordinates)
- Collision detection results

Example output:
```
10896.960756
R1 45
0.000000 0.000000 0.000000 0.000000
115.493047 0.034920 0.034920 0.017460
230.986093 0.137168 0.137168 0.068584
...
R2 23
2546.481240 2.500000 0.000000 0.000000
2647.259302 2.484284 0.031432 0.018859
2748.037364 2.437139 0.125722 0.075433
...
```

## 🚦 Performance

- Handles scenarios with 2 robots efficiently
- Processes 3-6 operations in reasonable time
- Real-time visualization for up to 500 waypoints
- Collision detection at 10ms resolution
