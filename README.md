# Robotics Hackathon 2025: Multi-Robot Task Scheduler


### Problem Overview
This project provides a software core for planning and scheduling the cooperative work of multiple industrial robot arms. The goal is to minimize the total operation time (makespan) while ensuring no collisions occur between robots.

### Repository Structure

robotics-hackathon-2025/
├── src/ # Source code
├── data/ # Input data files
├── requirements.txt # Python dependencies
└── README.md # This file


### Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/your-repo-name.git
    cd your-repo-name
    ```

2.  **Create a virtual environment (Highly Recommended):**
    ```bash
    python -m venv venv
    # On Windows:
    venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### How to Run the Code

1.  **Prepare input file. `input.txt` 

2.  **Run the main program from the repository's root directory:**
    ```bash
    python src/main.py
    ```

3.  **Check the output.**
    The program will generate an `output.txt` file in the root directory with the calculated schedule and waypoints.

### How to Test with Different Scenarios

Simply replace the contents of `data/input.txt` with a new dataset that follows the same format and run the command again.

### Example Input
A sample `data/input.txt` file for 2 robots and 2 operations:
