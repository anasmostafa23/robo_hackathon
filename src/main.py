# main.py
import os
from input_parser import parse_input
from scheduler import assign_operations, plan_paths
from collision_checker import check_collisions, resolve_collisions
from output_generator import write_output

def main(input_filename):
    print("Parsing input...")
    robots, operations, tool_clearance, safe_dist, v_max, a_max = parse_input(input_filename)

    print("Assigning operations to robots...")
    assign_operations(robots, operations)

    print("Planning paths and calculating timings...")
    plan_paths(robots, v_max, a_max)

    print("Checking for collisions...")
    collisions = check_collisions(robots, tool_clearance, safe_dist)
    resolve_collisions(robots, collisions)

    print("Writing output file 'output.txt'...")
    write_output(robots)

    print("Done!")

if __name__ == "__main__":
    # This is the magic line. It finds the project's root folder no matter where you run the script from.
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Now, create the full path to the input file
    input_file_path = os.path.join(project_root, 'data', 'input.txt')
    
    print(f"Looking for input file at: {input_file_path}")
    main(input_file_path) # Run the program with the full, correct path