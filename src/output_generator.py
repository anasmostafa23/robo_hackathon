# output_generator.py
def write_output(robots, output_filename='output.txt'):
    """
    Writes the output file in the required format.
    """
    global_makespan = max(robot['makespan'] for robot in robots)
    with open(output_filename, 'w') as f:
        # Write total makespan (convert seconds to milliseconds)
        f.write(f"{int(global_makespan * 1000)}\n")
        for robot in robots:
            schedule = robot['schedule']
            # Write robot header: e.g., "R1 5"
            f.write(f"{robot['id']} {len(schedule)}\n")
            # Write each waypoint: time_ms x y z
            for point in schedule:
                time_sec, x, y, z = point
                time_ms = int(time_sec * 1000)
                f.write(f"{time_ms} {x:.3f} {y:.3f} {z:.3f}\n")
