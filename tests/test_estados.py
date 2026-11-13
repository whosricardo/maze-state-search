from src.graphs.estados import neighbor_logic, cell_cost, build_g_pos
from src.graphs.io import parse_map
import pytest


def test_neighbor_logic(tmp_path):
    map_file = tmp_path / "test_map.txt"

    map_file.write_text(
        "#####\n"
        "##.##\n"
        "#...#\n"
        "#...#\n"
        "#####\n"
    )

    grid = parse_map(map_file)

    pos = (2, 2)

    expected = [
        (1, 2),
        (2, 3),
        (3, 2),
        (2, 1)
    ]

    result = neighbor_logic(pos, grid)

    assert result == expected


def test_neighbor_logic_north_blocked(tmp_path):
    map_file = tmp_path / "test_map.txt"

    map_file.write_text(
        "#####\n"
        "#####\n"
        "#...#\n"
        "#...#\n"
        "#####\n"
    )

    grid = parse_map(map_file)

    pos = (2, 2)

    expected = [
        (2, 3),
        (3, 2),
        (2, 1)
    ]

    result = neighbor_logic(pos, grid)

    assert result == expected


def test_neighbor_logic_wall(tmp_path):
    map_file = tmp_path / "test_map.txt"

    map_file.write_text(
        "#####\n"
        "#####\n"
        "#...#\n"
        "#...#\n"
        "#####\n"
    )

    grid = parse_map(map_file)

    pos = (0, 0)

    expected = []

    result = neighbor_logic(pos, grid)

    assert result == expected


def test_neighbor_logic_out(tmp_path):
    map_file = tmp_path / "test_map.txt"

    map_file.write_text(
        "#####\n"
        "#####\n"
        "#...#\n"
        "#...#\n"
        "#####\n"
    )

    grid = parse_map(map_file)

    pos = (-1, -1)

    expected = []

    result = neighbor_logic(pos, grid)

    assert result == expected


def test_neighbor_logic_out_positive(tmp_path):
    map_file = tmp_path / "test_map.txt"

    map_file.write_text(
        "#####\n"
        "#####\n"
        "#...#\n"
        "#...#\n"
        "#####\n"
    )

    grid = parse_map(map_file)

    pos = (99, 99)

    expected = []

    result = neighbor_logic(pos, grid)

    assert result == expected


def test_cell_cost():
    assert cell_cost('.') == 1
    assert cell_cost(',') == 3
    assert cell_cost('~') == 5
    assert cell_cost('a') == 1
    assert cell_cost('A') == 1
    assert cell_cost('>') == 1
    assert cell_cost('*') == -2


def test_cell_cost_error():
    with pytest.raises(KeyError):
        cell_cost('+')


def test_build_g_pos_edges():
    grid = [
        ['#', '#', '#', '#', '#'],
        ['#', 'S', '.', ',', '#'],
        ['#', '#', '#', '#', '#'],
    ]

    g_pos = build_g_pos(grid)

    expected = {
        (1, 1): {
            (1, 2): 1,
        },
        (1, 2): {
            (1, 3): 3,
            (1, 1): 1,
        },
        (1, 3): {
            (1, 2): 1,
        },
    }

    assert g_pos.adjacency == expected


@pytest.mark.parametrize(
    "grid, expected_neighbors",
    [
        (
            [
                ['#', '#', '#', '#', '#'],
                ['#', '.', '>', '.', '#'],
                ['#', '#', '#', '#', '#'],
            ],
            {(1, 3): 1},
        ),
        (
            [
                ['#', '#', '#', '#', '#'],
                ['#', '.', '<', '.', '#'],
                ['#', '#', '#', '#', '#'],
            ],
            {(1, 1): 1},
        ),
        (
            [
                ['#', '#', '.', '#', '#'],
                ['#', '#', '^', '#', '#'],
                ['#', '#', '.', '#', '#'],
            ],
            {(0, 2): 1},
        ),
        (
            [
                ['#', '#', '.', '#', '#'],
                ['#', '#', 'v', '#', '#'],
                ['#', '#', '.', '#', '#'],
            ],
            {(2, 2): 1},
        ),
    ]
)
def test_build_g_pos_conveyors(grid, expected_neighbors):
    g_pos = build_g_pos(grid)

    assert g_pos.adjacency[(1, 2)] == expected_neighbors


def test_build_g_pos_goal_has_no_outgoing_edges():
    grid = [
        ['#', '#', '#', '#', '#'],
        ['#', 'S', 'G', '.', '#'],
        ['#', '#', '#', '#', '#'],
    ]

    g_pos = build_g_pos(grid)

    assert g_pos.adjacency[(1, 2)] == {}


def test_build_g_pos_wall():
    grid = [
        ['#', '#', '#', '#', '#'],
        ['#', 'S', 'A', 'G', '#'],
        ['#', '#', '#', '#', '#'],
    ]

    g_pos = build_g_pos(grid)
