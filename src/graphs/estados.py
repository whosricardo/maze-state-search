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
