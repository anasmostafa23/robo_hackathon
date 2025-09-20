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


