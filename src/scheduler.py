# scheduler.py
import math

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
    For each robot, plan its path by calculating waypoints and timings.
    
    """
    for robot in robots:
        schedule = []
        current_time = 0.0
        current_pos = (robot['base_x'], robot['base_y'], robot['base_z'])

        # Start at base
        schedule.append((current_time, current_pos[0], current_pos[1], current_pos[2]))

        for op in robot['operations']:
            pick_point = (op['pick_x'], op['pick_y'], op['pick_z'])
            place_point = (op['place_x'], op['place_y'], op['place_z'])

            # Move to Pick
            dist_to_pick = math.sqrt(sum((a - b) ** 2 for a, b in zip(current_pos, pick_point)))
            time_to_pick = calculate_move_time(dist_to_pick, v_max, a_max)
            current_time += time_to_pick
            schedule.append((current_time, pick_point[0], pick_point[1], pick_point[2]))

            # Perform Pick operation (wait)
            current_time += op['t_i']
            # We are at the pick point, no movement, just time passing
            # schedule.append((current_time, pick_point[0], pick_point[1], pick_point[2]))

            # Move to Place
            dist_to_place = math.sqrt(sum((a - b) ** 2 for a, b in zip(pick_point, place_point)))
            time_to_place = calculate_move_time(dist_to_place, v_max, a_max)
            current_time += time_to_place
            schedule.append((current_time, place_point[0], place_point[1], place_point[2]))

            # Perform Place operation (wait)
            current_time += op['t_i']
            # schedule.append((current_time, place_point[0], place_point[1], place_point[2]))

            current_pos = place_point

        robot['schedule'] = schedule
        robot['makespan'] = current_time  # Individual robot finish time