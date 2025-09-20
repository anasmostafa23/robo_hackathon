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

def assign_operations(robots, operations):
    """
    Assigns each operation to the robot with the fewest existing tasks.
    This helps balance the load.
    """
    for op in operations:
        # Find the robot with the minimum number of assigned operations
        min_ops = float('inf')
        best_robot = None
        for robot in robots:
            if len(robot['operations']) < min_ops:
                min_ops = len(robot['operations'])
                best_robot = robot
        # Assign the operation to this robot
        best_robot['operations'].append(op)

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