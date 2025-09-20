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

    t = 0
    while t < global_makespan:
        positions = {}
        # Get all robot positions at time t
        for robot in robots:
            pos = get_position_at_time(robot['schedule'], t)
            positions[robot['id']] = pos

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
                if distance < min_safe_distance:
                    collision_events.append((t, id_i, id_j))
        t += time_step

    return collision_events

# For the prototype, we will just print a warning.

def resolve_collisions(robots, collision_events):
    """
    Simple resolver: just prints warnings.
    A real implementation would modify the robots' schedules (e.g., add delay to one robot).
    """
    if collision_events:
        print(f"WARNING: Found {len(collision_events)} potential collision events!")
        for t, id_i, id_j in collision_events:
            print(f"Time {t:.2f}s: {id_i} and {id_j} are too close.")
    else:
        print("No collisions detected. Good job!")
