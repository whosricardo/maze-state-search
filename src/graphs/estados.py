from collections import deque

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

TARGET_VERTEX = "ALVO"

CONVEYOR_DIRECTIONS = {
    '>': (0, 1),
    '<': (0, -1),
    '^': (-1, 0),
    'v': (1, 0),
}

DOOR_CELLS = {'A', 'B', 'C', 'D'}

KEY_CELLS = {'a', 'b', 'c', 'd'}


# [IA] ChatGPT – 52–54: discussão da indexação e dos vizinhos válidos.
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


# [IA] ChatGPT – 58–61: discussão dos custos fixos das células.
def cell_cost(symbol):
    return CELL_COST[symbol]


# [IA] ChatGPT – 58–61: revisão conceitual da modelagem por posições.
def build_g_pos(grid, door_mode):
    if door_mode not in {'wall', 'floor'}:
        raise ValueError("door_mode must be a 'wall' or 'floor'")
    g_pos = Graph()

    for row in range(len(grid)):
        for column in range(len(grid[row])):
            symbol = grid[row][column]
            pos = (row, column)

            if symbol != '#':
                # if symbol is a door an mode is wall skip
                if symbol in DOOR_CELLS and door_mode == "wall":
                    continue

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
                    if destination_symbol in DOOR_CELLS and door_mode == "wall":
                        continue

                    if destination_symbol == '+':
                        weight = -4
                    else:
                        weight = cell_cost(destination_symbol)

                    g_pos.add_edge(pos, neighbor, weight)

    return g_pos

# G_EST codes


def get_initial_state(grid):
    for row in range(len(grid)):
        for column in range(len(grid[row])):
            if grid[row][column] == 'S':
                start_pos = (row, column)
                return (
                    start_pos,
                    frozenset(),  # keys
                    frozenset()  # bonus
                )
    raise ValueError("Start position 'S' not found")


def next_state(current_state, destination_pos, grid):
    _, keys, consumed_bonus = current_state

    destination_row, destination_column = destination_pos
    destination_symbol = grid[destination_row][destination_column]

    if destination_symbol in KEY_CELLS:
        return (
            destination_pos,
            keys | frozenset({destination_symbol}),
            consumed_bonus
        )

    if destination_symbol == '+':
        return (
            destination_pos,
            keys,
            consumed_bonus | frozenset({destination_pos})
        )

    return (
        destination_pos,
        keys,
        consumed_bonus
    )


def can_enter(current_state, destination_symbol):
    _, keys, _ = current_state

    if destination_symbol not in DOOR_CELLS:
        return True

    if destination_symbol.lower() in keys:
        return True

    return False


def transition_cost(current_state, destination_pos, grid):
    _, _, consumed_bonus = current_state

    destination_row, destination_column = destination_pos
    destination_symbol = grid[destination_row][destination_column]

    if destination_symbol != '+':
        return cell_cost(destination_symbol)

    if destination_pos in consumed_bonus:
        return 1

    return -4


def valid_neighbors(current_state, grid):
    pos, _, _ = current_state

    neighbors = neighbor_logic(pos, grid)
    valid = []

    row, column = pos
    current_symbol = grid[row][column]

    allowed_neighbor = None

    if current_symbol in CONVEYOR_DIRECTIONS:
        row_offset, column_offset = CONVEYOR_DIRECTIONS[current_symbol]

        allowed_neighbor = (
            row + row_offset,
            column + column_offset
        )

    for neighbor in neighbors:
        if allowed_neighbor is not None and neighbor != allowed_neighbor:
            continue

        neighbor_row, neighbor_column = neighbor
        destination_symbol = grid[neighbor_row][neighbor_column]

        if can_enter(current_state, destination_symbol):
            valid.append(neighbor)

    return valid


def build_g_est(grid):
    g_est = Graph()

    initial_state = get_initial_state(grid)

    g_est.add_vertex(initial_state)

    queue = deque([initial_state])
    discovered = {initial_state}

    while queue:
        current_state = queue.popleft()

        pos, _, _ = current_state
        current_row, current_column = pos

        if grid[current_row][current_column] == 'G':
            g_est.add_edge(current_state, TARGET_VERTEX, 0)
            continue

        neighbors = valid_neighbors(current_state, grid)
        for destination_pos in neighbors:
            weight = transition_cost(current_state, destination_pos, grid)
            new_state = next_state(current_state, destination_pos, grid)

            g_est.add_edge(current_state, new_state, weight)

            if new_state not in discovered:
                discovered.add(new_state)
                queue.append(new_state)

    return g_est
