# main.py
from input_parser import parse_input
from scheduler import assign_operations, plan_paths
from collision_checker import check_collisions, prevent_collisions_by_staggered_start
from output_generator import write_output
import sys
import os

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

    print("Writing output file...")
    # Determine the correct output path
    if input_filename.startswith('data/'):
        output_file_path = input_filename.replace('input.txt', 'output.txt')
    else:
        # Get the project root directory (one level up from src/)
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        output_file_path = os.path.join(project_root, 'data', 'output.txt')
    
    write_output(robots, output_file_path)  # You'll need to modify write_output to accept a path

    print("Done!")

if __name__ == "__main__":
    # Allow running from command line with a filename argument
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = 'data/input.txt'  # default
    main(input_file)