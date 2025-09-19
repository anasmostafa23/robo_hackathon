# src/brain/scheduler.py
import math
from models.data_models import Robot, Operation, Point, Waypoint

def calculate_move_time(distance: float, v_max: float, a_max: float) -> float:
    """
    Calculates time for a move using a trapezoidal velocity profile.
    Returns: time in seconds
    """
    # Time to accelerate to max speed (and decelerate back to zero)
    t_acc = v_max / a_max
    # Distance covered during acceleration (and deceleration)
    d_acc = 0.5 * a_max * t_acc * t_acc

    if distance < 2 * d_acc:
        # Robot never reaches full speed (triangle profile)
        t_total = 2 * math.sqrt(distance / a_max)
    else:
        # Robot spends time at full speed (trapezoid profile)
        t_cruise = (distance - 2 * d_acc) / v_max
        t_total = 2 * t_acc + t_cruise
    return t_total

def assign_operations(robots: list[Robot], operations: list[Operation]):
    """
    Simple assignment: assign each operation to the robot closest to its pick-up point.
    Modifies the robots list in-place by appending to each robot's `operations` list.
    """
    for op in operations:
        min_dist = float('inf')
        best_robot = None

        for robot in robots:
            # Calculate Euclidean distance from robot's base to the pick point
            dist = math.sqrt(
                (robot.base_pos.x - op.pick_pos.x)**2 +
                (robot.base_pos.y - op.pick_pos.y)**2 +
                (robot.base_pos.z - op.pick_pos.z)**2
            )
            if dist < min_dist:
                min_dist = dist
                best_robot = robot

        # Assign this operation to the closest robot
        best_robot.operations.append(op)

def plan_paths(robots: list[Robot], v_max: float, a_max: float):
    """
    For each robot, plan its path by calculating waypoints and timings.
    Modifies each robot object in-place by setting its `schedule` and `makespan`.
    """
    for robot in robots:
        schedule = [] # This will be a list of Waypoint objects
        current_time = 0.0 # Keeps track of the robot's personal timeline
        current_pos = robot.base_pos # Start at the robot's base

        # Start at the base (time = 0)
        schedule.append(Waypoint(t=current_time, x=current_pos.x, y=current_pos.y, z=current_pos.z))

        for op in robot.operations:
            # 1. Move from current position to the PICK point
            dist_to_pick = math.sqrt(
                (current_pos.x - op.pick_pos.x)**2 +
                (current_pos.y - op.pick_pos.y)**2 +
                (current_pos.z - op.pick_pos.z)**2
            )
            time_to_pick = calculate_move_time(dist_to_pick, v_max, a_max)
            current_time += time_to_pick
            # Add the arrival at the Pick point to the schedule
            schedule.append(Waypoint(t=current_time, x=op.pick_pos.x, y=op.pick_pos.y, z=op.pick_pos.z))

            # 2. Perform the Pick operation (wait at the pick point)
            current_time += op.t_i
            # We don't need to add a waypoint here because we are already at the location.

            # 3. Move from the PICK point to the PLACE point
            dist_to_place = math.sqrt(
                (op.pick_pos.x - op.place_pos.x)**2 +
                (op.pick_pos.y - op.place_pos.y)**2 +
                (op.pick_pos.z - op.place_pos.z)**2
            )
            time_to_place = calculate_move_time(dist_to_place, v_max, a_max)
            current_time += time_to_place
            # Add the arrival at the Place point to the schedule
            schedule.append(Waypoint(t=current_time, x=op.place_pos.x, y=op.place_pos.y, z=op.place_pos.z))

            # 4. Perform the Place operation (wait at the place point)
            current_time += op.t_i

            # Update the current position for the next operation
            current_pos = op.place_pos

        # After planning all operations, save the schedule and makespan to the robot object
        robot.schedule = schedule
        robot.makespan = current_time