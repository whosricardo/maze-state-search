from src.graphs.graph import Graph


CELL_COST = {
    '.': 1,
    'S': 1,
    'G': 1,
    ',': 3,
    '~': 5,

    'a': 1,
    'b': 1,
    'c': 1,
    'd': 1,

    'A': 1,
    'B': 1,
    'C': 1,
    'D': 1,

    '>': 1,
    '<': 1,
    '^': 1,
    'v': 1,

    '*': -2,
}


CONVEYOR_DIRECTIONS = {
    '>': (0, 1),
    '<': (0, -1),
    '^': (-1, 0),
    'v': (1, 0),
}


def neighbor_logic(pos, grid):
    # unpacking pos
    row, col = pos

    # current position itself must be inside the grid
    if not (0 <= row < len(grid) and 0 <= col < len(grid[0])):
        return []

    # verify if the pos is a wall
    if grid[row][col] == '#':
        return []

    neighbors = []

    # north/norte
    n_pos = (row - 1, col)
    if 0 <= row - 1 < len(grid) and grid[row - 1][col] != '#':
        neighbors.append(n_pos)

    # east/leste
    l_pos = (row, col + 1)
    if 0 <= col + 1 < len(grid[0]) and grid[row][col + 1] != '#':
        neighbors.append(l_pos)

    # south/sul
    s_pos = (row + 1, col)
    if 0 <= row + 1 < len(grid) and grid[row + 1][col] != '#':
        neighbors.append(s_pos)

    # oeste/west
    o_pos = (row, col - 1)
    if 0 <= col - 1 < len(grid[0]) and grid[row][col - 1] != '#':
        neighbors.append(o_pos)

    return neighbors


def cell_cost(symbol):
    return CELL_COST[symbol]


def build_g_pos(grid):
    g_pos = Graph()

    for row in range(len(grid)):
        for column in range(len(grid[row])):
            symbol = grid[row][column]
            pos = (row, column)

            if symbol != '#':
                g_pos.add_vertex(pos)

                if symbol == 'G':
                    continue

                # creates list of neighbors [(x,y), (x,y)]
                neighbors = neighbor_logic(pos, grid)

                allowed_neighbor = None

                if symbol in CONVEYOR_DIRECTIONS:
                    row_offset, column_offset = CONVEYOR_DIRECTIONS[symbol]

                    allowed_neighbor = (
                        row + row_offset,
                        column + column_offset
                    )

                for neighbor in neighbors:

                    # conveyor can only leave in its arrow direction
                    if allowed_neighbor is not None and neighbor != allowed_neighbor:
                        continue

                    # assigns row and column from iterator
                    neighbor_row, neighbor_column = neighbor

                    destination_symbol = grid[neighbor_row][neighbor_column]
                    weight = cell_cost(destination_symbol)

                    g_pos.add_edge(pos, neighbor, weight)

    return g_pos
