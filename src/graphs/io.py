def parse_map(path):
    with open(path, 'r') as file:
        map_data = [list(line.strip()) for line in file]

    return map_data
