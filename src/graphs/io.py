ALLOWED_SYMBOLS = {
    '#', '.', 'S', 'G',
    ',', '~',
    'a', 'b', 'c', 'd',
    'A', 'B', 'C', 'D',
    '>', '<', '^', 'v',
    '+', '*'
}


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
        return False  # if map empty return false

    row_len = len(grid[0])
    # iterates through all rows and check len
    return all(len(row) == row_len for row in grid)


def validate_symbols(grid):
    # iterates through all cells in a row
    # then does all again for each row in the grid
    return all(
        all(cell in ALLOWED_SYMBOLS for cell in row)
        for row in grid
    )

# later create a helper that does the job
# for this two functions (validate_start and validate_goal)


def validate_start(grid):
    count = sum(
        cell == 'S'
        for row in grid
        for cell in row
    )

    return count == 1


def validate_goal(grid):
    count = sum(
        cell == 'G'
        for row in grid
        for cell in row
    )

    return count == 1
