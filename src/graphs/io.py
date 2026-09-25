def parse_map(path):
    with open(path, 'r') as file:
        map_data = [list(line.strip()) for line in file]

    return map_data


def validate_map(grid):
    if not validate_rectangular(grid):
        return False

    return True


def validate_rectangular(grid):
    if not grid:
        return True

    row_len = len(grid[0])
    return all(len(row) == row_len for row in grid)
