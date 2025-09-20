# trajectory_planner.py
import math

def plan_trajectory(robot, operations, v_max, a_max):
    """
    Plans a path for a single robot through its list of assigned operations.
    Generates a schedule of (time, x, y, z) waypoints.
    Args:
        robot: The robot dictionary. Must have 'id', 'base_x', 'base_y', 'base_z'.
        operations: The list of operations (pick/place) assigned to this robot.
                   Each operation is a dict: {'pick_x','pick_y','pick_z','place_x','place_y','place_z','t_i'}
        v_max: Maximum velocity (m/s)
        a_max: Maximum acceleration (m/s²)
    Returns:
        list: A schedule of waypoints [(t0, x0, y0, z0), (t1, x1, y1, z1), ...]
    """
    print(f"DEBUG: Planning trajectory for robot {robot.get('id', 'unknown')}")
    print(f"DEBUG: Robot base position: {robot.get('base_x', 0)}, {robot.get('base_y', 0)}, {robot.get('base_z', 0)}")
    print(f"DEBUG: Number of operations: {len(operations)}")
    
    for i, op in enumerate(operations):
        print(f"DEBUG: Operation {i+1}:")
        print(f"DEBUG:   Pick: {op.get('pick_x', 0)}, {op.get('pick_y', 0)}, {op.get('pick_z', 0)}")
        print(f"DEBUG:   Place: {op.get('place_x', 0)}, {op.get('place_y', 0)}, {op.get('place_z', 0)}")
        print(f"DEBUG:   Time: {op.get('t_i', 0)}")
    
    schedule = []
    current_time = 0.0
    current_pos = (robot['base_x'], robot['base_y'], robot['base_z']) # Start at base

    # Add starting position as the first waypoint
    schedule.append((current_time, current_pos[0], current_pos[1], current_pos[2]))
    print(f"DEBUG: Added start waypoint: {schedule[0]}")

    for op in operations:
        # 1. Move to PICK point
        target_pick = (op['pick_x'], op['pick_y'], op['pick_z'])
        print(f"DEBUG: Moving to pick point: {target_pick}")
        leg_time, leg_waypoints = _plan_move(current_pos, target_pick, current_time, v_max, a_max)
        print(f"DEBUG: Generated {len(leg_waypoints)} waypoints for pick move")
        schedule.extend(leg_waypoints[1:]) # Skip the first point (it's current_pos)
        current_time += leg_time
        current_pos = target_pick

        # 2. EXECUTE PICK operation (robot stops for t_i seconds)
        current_time += op['t_i'] # Add the operation time
        # Add a waypoint to show we are still at the pick point during this time
        schedule.append((current_time, current_pos[0], current_pos[1], current_pos[2]))
        print(f"DEBUG: Added pick operation waypoint: {schedule[-1]}")

        # 3. Move to PLACE point
        target_place = (op['place_x'], op['place_y'], op['place_z'])
        print(f"DEBUG: Moving to place point: {target_place}")
        leg_time, leg_waypoints = _plan_move(current_pos, target_place, current_time, v_max, a_max)
        print(f"DEBUG: Generated {len(leg_waypoints)} waypoints for place move")
        schedule.extend(leg_waypoints[1:])
        current_time += leg_time
        current_pos = target_place

        # 4. EXECUTE PLACE operation (robot stops for t_i seconds)
        current_time += op['t_i']
        schedule.append((current_time, current_pos[0], current_pos[1], current_pos[2]))
        print(f"DEBUG: Added place operation waypoint: {schedule[-1]}")

    robot['makespan'] = current_time # Store the total time for this robot
    print(f"DEBUG: Final schedule has {len(schedule)} waypoints")
    return schedule

def _plan_move(start_pos, end_pos, start_time, v_max, a_max):
    """
    Plans a movement between two points using a trapezoidal velocity profile.
    Returns the total time for the move and a list of waypoints for the segment.
    """
    # Calculate total distance
    dx = end_pos[0] - start_pos[0]
    dy = end_pos[1] - start_pos[1]
    dz = end_pos[2] - start_pos[2]
    distance = math.sqrt(dx**2 + dy**2 + dz**2)
    
    print(f"DEBUG: Planning move from {start_pos} to {end_pos}")
    print(f"DEBUG: Distance: {distance}, v_max: {v_max}, a_max: {a_max}")

    # If distance is zero, return immediately
    if distance < 1e-10:
        print("DEBUG: Zero distance move, returning empty waypoints")
        return 0.0, [(start_time, start_pos[0], start_pos[1], start_pos[2])]

    # --- Time calculations for trapezoidal profile ---
    # Time to accelerate to v_max: t_acc = v_max / a_max
    # Distance needed to accelerate and decelerate: d_acc_dec = (v_max * t_acc) = (v_max^2 / a_max)
    t_acc = v_max / a_max
    d_acc_dec = v_max * t_acc  # v_max^2 / a_max

    if distance < d_acc_dec:
        # Case 1: Not enough distance to reach v_max. Triangle profile.
        t_acc_actual = math.sqrt(distance / a_max)
        t_total = 2 * t_acc_actual
        cruise_speed = a_max * t_acc_actual
        cruise_time = 0.0
        print(f"DEBUG: Triangle profile, t_total: {t_total}")
    else:
        # Case 2: Full trapezoid profile. Time at cruise speed.
        t_acc = v_max / a_max
        d_cruise = distance - d_acc_dec
        cruise_time = d_cruise / v_max
        t_total = 2 * t_acc + cruise_time
        cruise_speed = v_max
        print(f"DEBUG: Trapezoid profile, t_total: {t_total}")

    # --- Generate waypoints for this segment ---
    waypoints = []
    num_segments = 10  # Number of points to sample along the move
    for i in range(num_segments + 1):
        t_segment = (i / num_segments) * t_total
        # Calculate distance traveled at time t_segment
        if t_segment <= t_acc:
            # Acceleration phase
            d_phase = 0.5 * a_max * t_segment**2
        elif t_segment <= (t_acc + cruise_time):
            # Cruise phase
            d_cruise_phase = cruise_speed * (t_segment - t_acc)
            d_phase = 0.5 * a_max * t_acc**2 + d_cruise_phase
        else:
            # Deceleration phase
            t_dec = t_segment - (t_acc + cruise_time)
            d_dec_phase = cruise_speed * t_dec - 0.5 * a_max * t_dec**2
            d_phase = (0.5 * a_max * t_acc**2) + (cruise_speed * cruise_time) + d_dec_phase

        # Interpolate position based on fractional distance
        frac = d_phase / distance
        x = start_pos[0] + frac * dx
        y = start_pos[1] + frac * dy
        z = start_pos[2] + frac * dz
        t_absolute = start_time + t_segment
        waypoints.append((t_absolute, x, y, z))

    print(f"DEBUG: Generated {len(waypoints)} waypoints for move")
    return t_total, waypoints