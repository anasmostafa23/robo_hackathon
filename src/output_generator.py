# output_generator.py
def write_output(robots, output_file_path='output.txt'):
    """
    Write the schedule to an output file.
    Supports robots having `schedule` as list of (t, x, y, z).
    """
    with open(output_file_path, 'w') as f:
        makespan = 0.0

        # --- compute makespan ---
        for robot in robots:
            waypoints = robot.get('schedule', [])
            if waypoints:
                last_time = waypoints[-1][0]  # tuple (t, x, y, z)
                makespan = max(makespan, last_time)

        # write makespan in milliseconds
        f.write(f"{makespan * 1000:.6f}\n")

        # --- write each robot’s schedule ---
        for i, robot in enumerate(robots):
            robot_id = i + 1
            waypoints = robot.get('schedule', [])
            f.write(f"R{robot_id} {len(waypoints)}\n")

            for wp in waypoints:
                if isinstance(wp, (tuple, list)) and len(wp) >= 4:
                    time_ms = wp[0] * 1000
                    x, y, z = wp[1], wp[2], wp[3]
                    f.write(f"{time_ms:.6f} {x:.6f} {y:.6f} {z:.6f}\n")
