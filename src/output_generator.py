# output_generator.py
def write_output(robots, output_file_path='output.txt'):
    """
    Write the schedule to an output file.
    Supports both `schedule` and `waypoints` as sources.
    """
    with open(output_file_path, 'w') as f:
        # Calculate makespan
        makespan = 0
        for robot in robots:
            waypoints = (
                getattr(robot, 'waypoints', None)
                or robot.get('waypoints')
                or robot.get('schedule')  # <-- added this
            )
            if not waypoints:
                continue

            last_wp = waypoints[-1]
            if hasattr(last_wp, 'time'):
                last_time = last_wp.time
            elif isinstance(last_wp, dict) and 'time' in last_wp:
                last_time = last_wp['time']
            else:
                continue
            makespan = max(makespan, last_time)

        # Write makespan (in milliseconds)
        f.write(f"{makespan * 1000:.6f}\n")

        # Write robot schedules
        for i, robot in enumerate(robots):
            robot_id = i + 1
            waypoints = (
                getattr(robot, 'waypoints', None)
                or robot.get('waypoints')
                or robot.get('schedule')  # <-- added this
                or []
            )

            f.write(f"R{robot_id} {len(waypoints)}\n")

            for wp in waypoints:
                if hasattr(wp, 'time'):
                    time_ms = wp.time * 1000
                    x, y, z = wp.x, wp.y, wp.z
                elif isinstance(wp, dict):
                    time_ms = wp.get('time', 0) * 1000
                    x, y, z = wp.get('x', 0), wp.get('y', 0), wp.get('z', 0)
                else:
                    continue
                f.write(f"{time_ms:.6f} {x:.6f} {y:.6f} {z:.6f}\n")
