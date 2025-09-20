# scheduler.py
import math
from trajectory_planner import plan_trajectory
from kinematics import is_point_reachable

def calculate_move_time(distance, v_max, a_max):
    """
    Calculates time for a move using a trapezoidal velocity profile.
    Returns: time in seconds
    """
    # Time to accelerate to max speed (and decelerate back to zero)
    t_acc = v_max / a_max
    # Distance covered during acceleration (and deceleration)
    d_acc = 0.5 * a_max * t_acc * t_acc

    if distance < 2 * d_acc:
        # Robot never reaches full speed
        t_total = 2 * math.sqrt(distance / a_max)
    else:
        # Robot spends time at full speed
        t_cruise = (distance - 2 * d_acc) / v_max
        t_total = 2 * t_acc + t_cruise
    return t_total

# In your scheduler.py, add debug output
def assign_operations(robots, operations):
    """
    Assigns operations to robots based on some criteria.
    Add debug output to see what's happening.
    """
    print(f"DEBUG: assign_operations called with {len(robots)} robots and {len(operations)} operations")
    
    for i, robot in enumerate(robots):
        print(f"DEBUG: Robot {i}: {robot}")
    
    for i, op in enumerate(operations):
        print(f"DEBUG: Operation {i}: {op}")
    
    # Your existing assignment logic here
    # ...
    from collections import deque
    # Convert to a list we can process
    op_queue = deque(operations)
    
    while op_queue:
        op = op_queue.popleft()
        best_robot = None
        best_distance = float('inf')
        
        # Find the robot whose base is closest to the PICK point of this operation
        pick_point = (op['pick_x'], op['pick_y'], op['pick_z'])
        for robot in robots:
            base_point = (robot['base_x'], robot['base_y'], robot['base_z'])
            distance = math.sqrt(sum((a - b) ** 2 for a, b in zip(base_point, pick_point)))
            if distance < best_distance:
                best_distance = distance
                best_robot = robot
                
        # Assign the operation to the closest robot
        best_robot['operations'].append(op)
        print(f"Assigned operation (Pick: {pick_point}) to {best_robot['id']} (distance: {best_distance:.2f}m)")

def plan_paths(robots, v_max, a_max):
    """
    Plans trajectories for all robots using the trajectory_planner.
    Now includes a basic reachability check.
    """
    for robot in robots:
        print(f"Planning path for {robot['id']}...")
        # Check if all points are reachable for this robot
        all_points = []
        for op in robot['operations']:
            all_points.append((op['pick_x'], op['pick_y'], op['pick_z']))
            all_points.append((op['place_x'], op['place_y'], op['place_z']))

        for point in all_points:
            if not is_point_reachable(robot, *point):
                print(f"WARNING: Point {point} may be unreachable for {robot['id']}. Proceeding anyway.")

        # Plan the trajectory
        robot['schedule'] = plan_trajectory(robot, robot['operations'], v_max, a_max)