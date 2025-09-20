import math

# collision_checker.py
def get_position_at_time(schedule, t):
    """
    Gets the interpolated (x, y, z) position of a robot at time 't' from its schedule.
    """
    # Find the segment of the schedule where the time 't' falls
    for i in range(len(schedule) - 1):
        t_start, x_start, y_start, z_start = schedule[i]
        t_end, x_end, y_end, z_end = schedule[i+1]

        if t_start <= t <= t_end:
            # Linear interpolation
            frac = (t - t_start) / (t_end - t_start)
            x = x_start + frac * (x_end - x_start)
            y = y_start + frac * (y_end - y_start)
            z = z_start + frac * (z_end - z_start)
            return (x, y, z)
    # If time is beyond the schedule, return the last position
    last_point = schedule[-1]
    return (last_point[1], last_point[2], last_point[3])

def check_collisions(robots, tool_clearance, safe_dist, time_step=0.1):
    """
    Checks for collisions between any two robots at any time.
    Returns a list of collision events: (time, robot_i_id, robot_j_id)
    """
    collision_events = []
    global_makespan = max(robot['makespan'] for robot in robots)
    min_safe_distance = tool_clearance + safe_dist + tool_clearance  # Robot1 radius + gap + Robot2 radius

    # Print the safety parameters for clarity
    print(f"DEBUG: Tool Clearance: {tool_clearance}m, Safe Distance: {safe_dist}m")
    print(f"DEBUG: Minimum required distance between robot centers: {min_safe_distance}m")

    t = 0
    # only run the detailed debug for the first few timesteps to avoid too much output
    debug_max_time = 0.2
    detailed_debug = True

    while t < global_makespan:
        positions = {}
        # Get all robot positions at time t
        for robot in robots:
            pos = get_position_at_time(robot['schedule'], t)
            positions[robot['id']] = pos

        # NEW: Detailed debug printing for the start of the simulation
        if detailed_debug and t <= debug_max_time:
            print(f"\nDEBUG: Time = {t:.6f}s")
            for robot_id, pos in positions.items():
                print(f"DEBUG:   {robot_id} position: ({pos[0]:.6f}, {pos[1]:.6f}, {pos[2]:.6f})")

        # Check all pairs of robots
        robot_ids = list(positions.keys())
        for i in range(len(robot_ids)):
            for j in range(i + 1, len(robot_ids)):
                id_i = robot_ids[i]
                id_j = robot_ids[j]
                pos_i = positions[id_i]
                pos_j = positions[id_j]
                # Calculate Euclidean distance
                distance = math.sqrt(sum((a - b) ** 2 for a, b in zip(pos_i, pos_j)))
                
                # NEW: Print distance calculation for the first few timesteps
                if detailed_debug and t <= debug_max_time:
                    print(f"DEBUG:   Distance between {id_i} and {id_j}: {distance:.6f}m")

                if distance < min_safe_distance:
                    # NEW: Print a clear message when a collision is detected
                    print(f"DEBUG:   COLLISION DETECTED! {distance:.6f}m < {min_safe_distance}m")
                    collision_events.append((t, id_i, id_j))
        
        # NEW: After the first few timesteps, turn off detailed debug to avoid too much output
        if t > debug_max_time:
            detailed_debug = False

        t += time_step

    # NEW: Print a summary of what was found
    if collision_events:
        print(f"\nDEBUG: Found {len(collision_events)} potential collision events.")
        # Print just the first few collisions to avoid spam
        for i, (collision_time, robot_i, robot_j) in enumerate(collision_events[:3]):
            print(f"DEBUG: Collision #{i+1}: at t={collision_time:.6f}s between {robot_i} and {robot_j}")
        if len(collision_events) > 3:
            print(f"DEBUG: ... and {len(collision_events) - 3} more collisions")
    else:
        print("\nDEBUG: No collisions detected in the detailed check.")

    return collision_events

# resolving collisions by adding delay timestamps

def resolve_collisions(robots, collision_events, tool_clearance, safe_dist):
    """
    Simple resolver: Adds a fixed delay to the second robot's entire schedule.
    """
    if not collision_events:
        print("No collisions detected!")
        return

    # Get the first collision event
    first_collision_time, robot_i_id, robot_j_id = collision_events[0]
    print(f"First collision at {first_collision_time}s between {robot_i_id} and {robot_j_id}. Adding delay to {robot_j_id}...")

    # Find the robot object for robot_j_id
    for robot in robots:
        if robot['id'] == robot_j_id:
            # Add a delay to the start of this robot's schedule
            delay = 2.0  # seconds
            new_schedule = []
            for point in robot['schedule']:
                # Shift every time in the schedule by the delay
                new_time = point[0] + delay
                new_schedule.append((new_time, point[1], point[2], point[3]))
            robot['schedule'] = new_schedule
            robot['makespan'] += delay # Don't forget to update its finish time!
            break

    # Re-check for collisions after the fix
    new_collisions = check_collisions(robots, tool_clearance, safe_dist)
    if new_collisions:
        print("WARNING: Still have collisions after resolution. Need a better algorithm!")
    else:
        print("Collisions resolved successfully!")


