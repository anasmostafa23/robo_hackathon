# output_generator.py
def write_output(robots, output_file_path='output.txt'):
    """
    Write the schedule to an output file.
    
    Args:
        robots: List of Robot objects with their scheduled waypoints
        output_file_path: Path to the output file (default: 'output.txt')
    """
    with open(output_file_path, 'w') as f:
        # Calculate makespan (maximum end time among all robots)
        makespan = 0
        for robot in robots:
            if robot.waypoints:
                makespan = max(makespan, robot.waypoints[-1].time)
        
        # Write makespan (in milliseconds)
        f.write(f"{makespan * 1000:.6f}\n")
        
        # Write each robot's schedule
        for i, robot in enumerate(robots):
            robot_id = i + 1
            f.write(f"R{robot_id} {len(robot.waypoints)}\n")
            
            for wp in robot.waypoints:
                # Convert time to milliseconds for output
                time_ms = wp.time * 1000
                f.write(f"{time_ms:.6f} {wp.x:.6f} {wp.y:.6f} {wp.z:.6f}\n")
