# output_generator.py
def write_output(robots, output_file_path='output.txt'):
    """
    Write the schedule to an output file.
    
    Args:
        robots: List of Robot objects or dictionaries with their scheduled waypoints
        output_file_path: Path to the output file (default: 'output.txt')
    """
    with open(output_file_path, 'w') as f:
        # Calculate makespan (maximum end time among all robots)
        makespan = 0
        for robot in robots:
            # Handle both object and dictionary formats
            if hasattr(robot, 'waypoints'):
                waypoints = robot.waypoints
            elif isinstance(robot, dict) and 'waypoints' in robot:
                waypoints = robot['waypoints']
            else:
                continue  # Skip if no waypoints found
                
            if waypoints:
                # Get the last waypoint time
                if hasattr(waypoints[-1], 'time'):
                    last_time = waypoints[-1].time
                elif isinstance(waypoints[-1], dict) and 'time' in waypoints[-1]:
                    last_time = waypoints[-1]['time']
                else:
                    continue
                    
                makespan = max(makespan, last_time)
        
        # Write makespan (in milliseconds)
        f.write(f"{makespan * 1000:.6f}\n")
        
        # Write each robot's schedule
        for i, robot in enumerate(robots):
            robot_id = i + 1
            
            # Get waypoints based on object type
            if hasattr(robot, 'waypoints'):
                waypoints = robot.waypoints
            elif isinstance(robot, dict) and 'waypoints' in robot:
                waypoints = robot['waypoints']
            else:
                waypoints = []
            
            f.write(f"R{robot_id} {len(waypoints)}\n")
            
            for wp in waypoints:
                # Get waypoint data based on object type
                if hasattr(wp, 'time'):
                    time_ms = wp.time * 1000
                    x = wp.x
                    y = wp.y
                    z = wp.z
                elif isinstance(wp, dict):
                    time_ms = wp.get('time', 0) * 1000
                    x = wp.get('x', 0)
                    y = wp.get('y', 0)
                    z = wp.get('z', 0)
                else:
                    # Skip invalid waypoints
                    continue
                
                f.write(f"{time_ms:.6f} {x:.6f} {y:.6f} {z:.6f}\n")