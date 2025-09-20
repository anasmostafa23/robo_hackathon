# main.py
from input_parser import parse_input
from scheduler import assign_operations, plan_paths
from collision_checker import check_collisions, prevent_collisions_by_staggered_start
from output_generator import write_output
import sys

def main(input_filename):
    print("Parsing input...")
    robots, operations, tool_clearance, safe_dist, v_max_linear, a_max = parse_input(input_filename)

    print("Assigning operations to robots...")
    assign_operations(robots, operations)

    print("Planning paths and calculating timings...")
    plan_paths(robots, v_max_linear, a_max)

    print("Checking for collisions...")
    collisions = check_collisions(robots, tool_clearance, safe_dist)
    print("Applying proactive collision prevention...")
    # Make sure to pass v_max_linear to the function!
    prevent_collisions_by_staggered_start(robots, tool_clearance, safe_dist, v_max_linear)

    print("Writing output file 'output.txt'...")
    write_output(robots)

    print("Done!")

if __name__ == "__main__":
    # Allow running from command line with a filename argument
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = 'data/input.txt'  # default
    main(input_file)