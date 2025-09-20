# kinematics.py
import math
import numpy as np

def is_point_reachable(robot_config, point_x, point_y, point_z):
    """
    Checks if a point (x, y, z) is within the achievable workspace of a robot.
    Simplified model: Checks if the point is between the min and max reach.
    Args:
        robot_config: A dictionary containing the robot's base position and joint limits.
                     We assume it has 'base_x', 'base_y', 'base_z', and a 'max_reach' key.
        point_x, point_y, point_z: Target point coordinates.
    Returns:
        bool: True if the point is likely reachable, False otherwise.
    """
    # Calculate distance from robot base to target point
    distance_to_point = math.sqrt(
        (point_x - robot_config['base_x'])**2 +
        (point_y - robot_config['base_y'])**2 +
        (point_z - robot_config['base_z'])**2
    )
    
    # Define a reasonable max and min reach for a 6-axis arm.
    # max_reach = sum of link lengths (you might need to estimate this from joint limits)
    # min_reach = minimum working distance (often ~0)
    # For a hackathon, we can hardcode these or calculate from provided data.
    # Let's assume robot_config has a 'max_reach' attribute. We need to add this in input_parser.
    max_reach = robot_config.get('max_reach', 1.5)  # meters, example value
    min_reach = robot_config.get('min_reach', 0.2)  # meters, can't reach too close
    
    return min_reach <= distance_to_point <= max_reach

# --- BONUS: A more advanced, placeholder IK function ---
# This is where you would use `scipy.optimize` if you have time.
def calculate_ik(robot_config, target_x, target_y, target_z):
    """
    Placeholder for a real Inverse Kinematics solver.
    This would use optimization to find joint angles to reach the target.
    For now, it just returns a dummy success flag and joint angles.
    """
    # This is a complex function. For the hackathon, you can initially
    # just return (True, [0,0,0,0,0,0]) and focus on other parts.
    # Implement this only if you have extra time.
    print(f"WARNING: Using placeholder IK for target ({target_x}, {target_y}, {target_z})")
    return True, [0.0, 0.0, 0.0, 0.0, 0.0, 0.0] # Dummy angles