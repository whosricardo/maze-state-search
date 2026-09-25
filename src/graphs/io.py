def parse_map(map_path):
    with open(map_path, 'r') as file:
        map_data = [list(line.strip()) for line in file]

    return map_data
