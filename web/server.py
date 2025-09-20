#!/usr/bin/env python3
"""
Web Server for Industrial Robot Scheduler
Integrates with the existing robotics modules for planning and visualization.
"""
import os
import sys
import json
import traceback
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# Add project root to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

app = Flask(__name__)
CORS(app)

# Import your robotics modules
try:
    from src.input_parser import parse_input
    from src.scheduler import assign_operations, plan_paths
    from src.collision_checker import check_collisions, resolve_collisions
    from src.output_generator import write_output
    from src.visualizer import parse_output
    ROBOTICS_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Robotics modules not available: {e}")
    ROBOTICS_MODULES_AVAILABLE = False

@app.route('/')
def index():
    """Serve the visualizer interface."""
    return send_from_directory('.', 'visualizer.html')

@app.route('/api/health')
def health():
    """Health check endpoint."""
    status = {
        'status': 'ok',
        'message': 'Robot Scheduler Web Server is running',
        'robotics_modules_available': ROBOTICS_MODULES_AVAILABLE
    }
    return jsonify(status)

@app.route('/api/run_scheduler', methods=['POST'])
def run_scheduler():
    """
    API endpoint to run the complete scheduling pipeline.
    """
    try:
        data = request.get_json()
        if not data or 'scenario' not in data:
            return jsonify({'error': 'No scenario content provided'}), 400
        
        scenario_content = data['scenario']
        
        # Write scenario to temporary file
        temp_input_path = 'temp_input.txt'
        with open(temp_input_path, 'w') as f:
            f.write(scenario_content)
        
        if not ROBOTICS_MODULES_AVAILABLE:
            return jsonify({
                'error': 'Robotics modules not available. Please check the server setup.',
                'demo_mode': True
            }), 503
        
        try:
            # Run your complete scheduling pipeline
            print("Parsing input...")
            robots, operations, tool_clearance, safe_dist, v_max, a_max = parse_input(temp_input_path)
            
            print("Assigning operations...")
            assign_operations(robots, operations)
            
            print("Planning paths...")
            plan_paths(robots, v_max, a_max)
            
            print("Checking collisions...")
            # Convert robots to format expected by collision_checker
            robots_for_collision = []
            for robot in robots:
                robots_for_collision.append({
                    'id': robot['id'],
                    'schedule': robot['schedule'],
                    'makespan': robot['makespan']
                })
            
            collisions = check_collisions(robots_for_collision, tool_clearance, safe_dist)
            
            if collisions:
                print(f"Found {len(collisions)} collisions, resolving...")
                resolve_collisions(robots_for_collision, collisions, tool_clearance, safe_dist)
                # Update the original robots with resolved schedules
                for resolved_robot in robots_for_collision:
                    for original_robot in robots:
                        if original_robot['id'] == resolved_robot['id']:
                            original_robot['schedule'] = resolved_robot['schedule']
                            original_robot['makespan'] = resolved_robot['makespan']
                            break
            
            print("Writing output...")
            write_output(robots, 'temp_output.txt')
            
            # Read and return the results
            with open('temp_output.txt', 'r') as f:
                output_content = f.read()
            
            # Parse output for metadata
            robots_data, makespan = parse_output('temp_output.txt')
            
            result = {
                'success': True,
                'makespan': makespan * 1000,  # Convert back to ms
                'schedule': output_content,
                'metadata': {
                    'num_robots': len(robots),
                    'num_operations': len(operations),
                    'tool_clearance': tool_clearance,
                    'safe_dist': safe_dist,
                    'collisions_detected': len(collisions),
                    'collisions_resolved': len(collisions) > 0
                }
            }
            
            return jsonify(result)
            
        finally:
            # Clean up temporary files
            try:
                os.remove(temp_input_path)
                os.remove('temp_output.txt')
            except:
                pass
                
    except Exception as e:
        print(f"Error in scheduler: {traceback.format_exc()}")
        return jsonify({'error': f'Scheduler error: {str(e)}'}), 500

@app.route('/api/parse_output', methods=['POST'])
def parse_output_file():
    """
    API endpoint to parse an existing output file for visualization.
    """
    try:
        data = request.get_json()
        if not data or 'output_content' not in data:
            return jsonify({'error': 'No output content provided'}), 400
        
        # Write content to temporary file
        with open('temp_parse.txt', 'w') as f:
            f.write(data['output_content'])
        
        # Parse using your visualizer module
        robots_data, makespan = parse_output('temp_parse.txt')
        
        # Convert to format suitable for frontend
        robots_formatted = {}
        for robot_id, data in robots_data.items():
            robots_formatted[robot_id] = {
                'times': data['times'].tolist(),
                'x': data['x'].tolist(),
                'y': data['y'].tolist(),
                'z': data['z'].tolist()
            }
        
        result = {
            'success': True,
            'makespan': makespan,
            'robots': robots_formatted
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'Output parsing error: {str(e)}'}), 500

@app.route('/api/scenarios')
def get_scenarios():
    """Get available test scenarios."""
    scenarios_dir = os.path.join(os.path.dirname(__file__), '..', 'test_scenarios')
    scenarios = []
    
    if os.path.exists(scenarios_dir):
        for filename in sorted(os.listdir(scenarios_dir)):
            if filename.endswith('.txt'):
                file_path = os.path.join(scenarios_dir, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    scenarios.append({
                        'name': filename,
                        'content': content,
                        'size': len(content)
                    })
                except Exception as e:
                    print(f"Error reading scenario {filename}: {e}")
    
    return jsonify({'scenarios': scenarios})

if __name__ == '__main__':
    print("🤖 Industrial Robot Scheduler Web Server")
    print("📍 http://localhost:5000")
    print("⚡ Robotics modules:", "available" if ROBOTICS_MODULES_AVAILABLE else "not available")
    
    app.run(host='0.0.0.0', port=5000, debug=True)