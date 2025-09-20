# input_parser.py
def parse_input(filename):
    """
    Parses the input file and returns all data.
    Returns: robots_list, operations_list, tool_clearance, safe_dist
    """
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]

    # Parse first line
    K, N = map(int, lines[0].split())
    index = 1

    # Parse robot base positions
    robots = []
    for i in range(K):
        coords = list(map(float, lines[index].split()))
        robots.append({
            'id': f'R{i+1}',
            'base_x': coords[0],
            'base_y': coords[1],
            'base_z': coords[2],
            'operations': []  # To be assigned later
        })
        index += 1

    # Parse joint parameters (we'll use the first joint's max speed/accel for cartesian approximation)
    joint_params = []
    for i in range(6):
        params = list(map(float, lines[index].split()))
        joint_params.append(params) # [min, max, v_max, a_max]
        index += 1
    # Let's use the minimum of all joint V_max and A_max for our cartesian movement model
    v_max = min(param[2] for param in joint_params) # deg/s
    a_max = min(param[3] for param in joint_params) # deg/s²
    # Convert to rad/s for a more standard unit. We'll assume a worst-case lever arm of 1m.
    v_max_cartesian = (v_max * 3.14159 / 180) * 1.0 # m/s (very rough approximation)
    a_max_cartesian = (a_max * 3.14159 / 180) * 1.0 # m/s²

    # Parse safety parameters
    tool_clearance, safe_dist = map(float, lines[index].split())
    index += 1

    # Parse operations
    operations = []
    for i in range(N):
        op_data = list(map(float, lines[index].split()))
        operations.append({
            'id': i+1,
            'pick_x': op_data[0], 'pick_y': op_data[1], 'pick_z': op_data[2],
            'place_x': op_data[3], 'place_y': op_data[4], 'place_z': op_data[5],
            't_i': op_data[6]  # fixed operation time
        })
        index += 1

        # Also add max_reach for the simplified kinematics check
    for robot in robots:
        # Estimate max_reach as the length of a fully extended arm.
        # A typical 6-axis arm might have a reach of 1.5m-2.0m.
        robot['max_reach'] = 2.2  # meters
        # A robot can likely reach points very close to its base.
        robot['min_reach'] = 0.1  # meters  # Changed from 0.2 to 0.1

    return robots, operations, tool_clearance, safe_dist, v_max_cartesian, a_max_cartesian