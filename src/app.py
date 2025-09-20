# app.py
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import subprocess
import sys
import json

# Add the src directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

app = Flask(__name__)
CORS(app)  # This allows your frontend to talk to the backend

# Serve the main visualizer page
@app.route('/')
def serve_visualizer():
    return send_from_directory('web', 'index.html')

# Serve static files from the web directory (CSS, JS, etc.)
@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('web', path)

# API endpoint to run the scheduler
@app.route('/api/run_scheduler', methods=['POST'])
def api_run_scheduler():
    try:
        data = request.get_json()
        if not data or 'scenario' not in data:
            return jsonify({'error': 'No scenario content provided'}), 400
        
        scenario_content = data['scenario']
        
        # Save the scenario content to input.txt
        input_file_path = os.path.join('data', 'input.txt')
        with open(input_file_path, 'w') as f:
            f.write(scenario_content)
        
        print("Running scheduler with provided scenario...")
        
        # Run your main.py logic
        result = subprocess.run([
            sys.executable, 'main.py', input_file_path
        ], capture_output=True, text=True, cwd=os.getcwd())

        # Check if main.py ran successfully
        if result.returncode != 0:
            error_message = f"Backend error: {result.stderr}"
            print(error_message)
            return jsonify({'error': error_message}), 500

        print("Simulation completed successfully!")

        # Read the generated output
        output_file_path = os.path.join('data', 'output.txt')
        output_data = ""
        if os.path.exists(output_file_path):
            with open(output_file_path, 'r') as f:
                output_data = f.read()
        
        # Parse the output to extract metadata for the frontend
        metadata = parse_output_metadata(output_data)
        
        return jsonify({
            'success': True,
            'schedule': output_data,
            'makespan': metadata['makespan'],
            'metadata': metadata
        })

    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

# API endpoint to parse output for visualization
@app.route('/api/parse_output', methods=['POST'])
def api_parse_output():
    try:
        data = request.get_json()
        if not data or 'output_content' not in data:
            return jsonify({'error': 'No output content provided'}), 400
        
        output_content = data['output_content']
        
        # Parse the output for visualization data
        visualization_data = parse_output_for_visualization(output_content)
        
        return jsonify({
            'success': True,
            'visualization_data': visualization_data
        })
        
    except Exception as e:
        print(f"Output parsing error: {str(e)}")
        return jsonify({'error': f'Output parsing error: {str(e)}'}), 500

# API endpoint to get available scenarios
@app.route('/api/scenarios', methods=['GET'])
def api_get_scenarios():
    try:
        # Create some example scenarios
        scenarios = [
            {'name': 'Basic 2 Robots', 'file': 'scenario_2_robots.txt'},
            {'name': 'Complex 3 Robots', 'file': 'scenario_3_robots.txt'},
            {'name': 'Stress Test', 'file': 'scenario_stress.txt'}
        ]
        
        return jsonify({
            'success': True,
            'scenarios': scenarios
        })
        
    except Exception as e:
        print(f"Scenarios error: {str(e)}")
        return jsonify({'error': f'Scenarios error: {str(e)}'}), 500

def parse_output_metadata(output_content):
    """Extract metadata from output file content"""
    lines = output_content.strip().split('\n')
    if not lines:
        return {'makespan': 0, 'num_robots': 0, 'num_operations': 0, 'collisions_detected': 0}
    
    makespan = float(lines[0].strip())
    
    # Count robots and waypoints
    num_robots = 0
    total_waypoints = 0
    i = 1
    while i < len(lines):
        if lines[i].startswith('R'):
            num_robots += 1
            parts = lines[i].split()
            if len(parts) >= 2:
                total_waypoints += int(parts[1])
            i += int(parts[1]) + 1 if len(parts) >= 2 else 1
        else:
            i += 1
    
    return {
        'makespan': makespan,
        'num_robots': num_robots,
        'num_operations': total_waypoints // 2,  # Rough estimate
        'collisions_detected': 0  # You'll need to calculate this from your collision checker
    }

def parse_output_for_visualization(output_content):
    """Parse output file content for visualization data"""
    lines = output_content.strip().split('\n')
    if not lines:
        return {'robots': [], 'makespan': 0}
    
    makespan = float(lines[0].strip())
    robots = []
    
    i = 1
    robot_id = 1
    while i < len(lines):
        if lines[i].startswith('R'):
            parts = lines[i].split()
            if len(parts) >= 2:
                num_waypoints = int(parts[1])
                waypoints = []
                
                for j in range(1, num_waypoints + 1):
                    if i + j < len(lines):
                        wp_parts = lines[i + j].split()
                        if len(wp_parts) >= 4:
                            waypoints.append({
                                'time': float(wp_parts[0]),
                                'x': float(wp_parts[1]),
                                'y': float(wp_parts[2]),
                                'z': float(wp_parts[3])
                            })
                
                robots.append({
                    'id': f'R{robot_id}',
                    'waypoints': waypoints,
                    'color': get_robot_color(robot_id)
                })
                robot_id += 1
                i += num_waypoints + 1
            else:
                i += 1
        else:
            i += 1
    
    return {
        'robots': robots,
        'makespan': makespan
    }

def get_robot_color(robot_id):
    """Assign colors to robots for visualization"""
    colors = [
        '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFBE0B', 
        '#FB5607', '#8338EC', '#3A86FF', '#04E762'
    ]
    return colors[(robot_id - 1) % len(colors)]

if __name__ == '__main__':
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    os.makedirs('web', exist_ok=True)
    
    # Run the Flask app
    print("Starting Robotics Scheduler Server...")
    print("Open: http://localhost:5000")
    app.run(debug=True, port=5000)