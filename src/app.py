# app.py (located in src/)
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import subprocess
import sys
import json
import traceback

# Get the project root directory (one level up from src/)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Add the src directory to the path so we can import our modules
sys.path.append(os.path.dirname(__file__))

app = Flask(__name__)
CORS(app)  # This allows your frontend to talk to the backend

# Create required directories if they don't exist
os.makedirs(os.path.join(PROJECT_ROOT, 'data'), exist_ok=True)
os.makedirs(os.path.join(PROJECT_ROOT, 'web'), exist_ok=True)

# Serve the main visualizer page
@app.route('/')
def serve_visualizer():
    try:
        return send_from_directory(os.path.join(PROJECT_ROOT, 'web'), 'index.html')
    except Exception as e:
        return f"Error serving index.html: {str(e)}. Make sure you have a 'web' directory with index.html."

# Serve static files from the web directory (CSS, JS, etc.)
@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(os.path.join(PROJECT_ROOT, 'web'), path)

# API endpoint to run the scheduler
# API endpoint to run the scheduler
@app.route('/api/run_scheduler', methods=['POST'])
def api_run_scheduler():
    try:
        print("Received request to run scheduler")
        data = request.get_json()
        if not data or 'scenario' not in data:
            return jsonify({'error': 'No scenario content provided'}), 400
        
        scenario_content = data['scenario']
        
        # Save the scenario content to input.txt
        input_file_path = os.path.join(PROJECT_ROOT, 'data', 'input.txt')
        try:
            with open(input_file_path, 'w') as f:
                f.write(scenario_content)
            print(f"Saved scenario to {input_file_path}")
        except Exception as e:
            return jsonify({'error': f'Failed to write input file: {str(e)}'}), 500
        
        print("Running scheduler with provided scenario...")
        
        # Run your main.py logic
        try:
            result = subprocess.run([
                sys.executable, 'main.py', input_file_path
            ], capture_output=True, text=True, cwd=os.path.join(PROJECT_ROOT, 'src'), timeout=30)

            # Check if main.py ran successfully
            if result.returncode != 0:
                error_message = f"Backend error: {result.stderr}"
                print(error_message)
                return jsonify({'error': error_message}), 500

            print("Simulation completed successfully!")
            print("STDOUT:", result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)

        except subprocess.TimeoutExpired:
            return jsonify({'error': 'Scheduler timed out after 30 seconds'}), 500
        except Exception as e:
            return jsonify({'error': f'Failed to run scheduler: {str(e)}'}), 500

        # Read the generated output
        output_file_path = os.path.join(PROJECT_ROOT, 'data', 'output.txt')
        output_data = ""
        try:
            if os.path.exists(output_file_path):
                with open(output_file_path, 'r') as f:
                    output_data = f.read()
                print(f"Read output from {output_file_path}")
                
                # Debug: print first few lines of output
                lines = output_data.split('\n')
                print("First 10 lines of output:")
                for i, line in enumerate(lines[:10]):
                    print(f"{i}: {repr(line)}")
                    
            else:
                return jsonify({'error': 'Output file was not generated'}), 500
        except Exception as e:
            return jsonify({'error': f'Failed to read output file: {str(e)}'}), 500
        
        # Parse the output to extract metadata for the frontend
        metadata = parse_output_metadata(output_data)
        
        return jsonify({
            'success': True,
            'schedule': output_data,
            'makespan': metadata['makespan'],
            'metadata': metadata
        })

    except Exception as e:
        print(f"Unexpected error in api_run_scheduler: {str(e)}")
        print(traceback.format_exc())
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

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def api_health():
    return jsonify({
        'status': 'ok',
        'message': 'Flask server is running'
    })

def parse_output_metadata(output_content):
    """Extract metadata from output file content with better error handling"""
    try:
        lines = output_content.strip().split('\n')
        if not lines:
            return {'makespan': 0, 'num_robots': 0, 'num_operations': 0, 'collisions_detected': 0}
        
        # Find the first non-empty line for makespan
        makespan_line = None
        for line in lines:
            if line.strip():  # Skip empty lines
                makespan_line = line.strip()
                break
        
        if not makespan_line:
            return {'makespan': 0, 'num_robots': 0, 'num_operations': 0, 'collisions_detected': 0}
        
        makespan = float(makespan_line)
        
        # Count robots and waypoints
        num_robots = 0
        total_waypoints = 0
        i = 1  # Start after makespan line
        
        while i < len(lines):
            line = lines[i].strip()
            if not line:  # Skip empty lines
                i += 1
                continue
                
            if line.startswith('R'):
                num_robots += 1
                parts = line.split()
                if len(parts) >= 2:
                    try:
                        num_waypoints = int(parts[1])
                        total_waypoints += num_waypoints
                        i += num_waypoints + 1  # Skip waypoint lines
                    except ValueError:
                        i += 1  # Skip malformed line
                else:
                    i += 1
            else:
                i += 1
        
        # Count collisions from the debug output (this is a simple approach)
        collisions_detected = output_content.count('COLLISION DETECTED')
        
        return {
            'makespan': makespan,
            'num_robots': num_robots,
            'num_operations': total_waypoints // 2,  # Rough estimate
            'collisions_detected': collisions_detected
        }
    except Exception as e:
        print(f"Error parsing output metadata: {str(e)}")
        return {'makespan': 0, 'num_robots': 0, 'num_operations': 0, 'collisions_detected': 0}

def parse_output_for_visualization(output_content):
    """Parse output file content for visualization data with better error handling"""
    try:
        lines = output_content.strip().split('\n')
        if not lines:
            return {'robots': [], 'makespan': 0}
        
        # Find the first non-empty line for makespan
        makespan_line = None
        for line in lines:
            if line.strip():  # Skip empty lines
                makespan_line = line.strip()
                break
        
        if not makespan_line:
            return {'robots': [], 'makespan': 0}
        
        makespan = float(makespan_line)
        robots = []
        
        i = 1  # Start after makespan line
        robot_id = 1
        
        while i < len(lines):
            line = lines[i].strip()
            if not line:  # Skip empty lines
                i += 1
                continue
                
            if line.startswith('R'):
                parts = line.split()
                if len(parts) >= 2:
                    try:
                        num_waypoints = int(parts[1])
                        waypoints = []
                        
                        for j in range(1, num_waypoints + 1):
                            if i + j < len(lines):
                                wp_line = lines[i + j].strip()
                                if not wp_line:  # Skip empty lines
                                    continue
                                    
                                wp_parts = wp_line.split()
                                if len(wp_parts) >= 4:
                                    try:
                                        waypoints.append({
                                            'time': float(wp_parts[0]),
                                            'x': float(wp_parts[1]),
                                            'y': float(wp_parts[2]),
                                            'z': float(wp_parts[3])
                                        })
                                    except ValueError:
                                        # Skip malformed waypoint
                                        continue
                        
                        robots.append({
                            'id': f'R{robot_id}',
                            'waypoints': waypoints,
                            'color': get_robot_color(robot_id)
                        })
                        robot_id += 1
                        i += num_waypoints + 1
                    except ValueError:
                        i += 1  # Skip malformed robot header
                else:
                    i += 1
            else:
                i += 1
        
        return {
            'robots': robots,
            'makespan': makespan
        }
    except Exception as e:
        print(f"Error parsing output for visualization: {str(e)}")
        return {'robots': [], 'makespan': 0}

def parse_output_for_visualization(output_content):
    """Parse output file content for visualization data"""
    try:
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
    except Exception as e:
        print(f"Error parsing output for visualization: {str(e)}")
        return {'robots': [], 'makespan': 0}

def get_robot_color(robot_id):
    """Assign colors to robots for visualization"""
    colors = [
        '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFBE0B', 
        '#FB5607', '#8338EC', '#3A86FF', '#04E762'
    ]
    return colors[(robot_id - 1) % len(colors)]

if __name__ == '__main__':
    # Run the Flask app
    print("Starting Robotics Scheduler Server...")
    print("Project root:", PROJECT_ROOT)
    print("Open: http://localhost:5000")
    print("API Health check: http://localhost:5000/api/health")
    app.run(debug=True, port=5000)