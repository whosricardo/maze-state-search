from src.graphs.estados import (
    neighbor_logic,
    cell_cost,
    build_g_pos,
    get_initial_state,
    next_state,
    can_enter,
    transition_cost,
    valid_neighbors
)
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

    g_pos = build_g_pos(grid, "floor")

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
    g_pos = build_g_pos(grid, "floor")

    assert g_pos.adjacency[(1, 2)] == expected_neighbors


def test_build_g_pos_goal_has_no_outgoing_edges():
    grid = [
        ['#', '#', '#', '#', '#'],
        ['#', 'S', 'G', '.', '#'],
        ['#', '#', '#', '#', '#'],
    ]

    g_pos = build_g_pos(grid, "floor")

    assert g_pos.adjacency[(1, 2)] == {}


def test_build_g_pos_door_as_floor():
    grid = [
        ['#', '#', '#', '#', '#'],
        ['#', 'S', 'A', '.', '#'],
        ['#', '#', '#', '#', '#'],
    ]

    g_pos = build_g_pos(grid, door_mode="floor")

    expected = {
        (1, 1): {
            (1, 2): 1,
        },
        (1, 2): {
            (1, 3): 1,
            (1, 1): 1,
        },
        (1, 3): {
            (1, 2): 1,
        },
    }

    assert g_pos.adjacency == expected


def test_build_g_pos_bonus():
    grid = [
        ['#', '#', '#', '#', '#'],
        ['#', 'S', '+', '.', '#'],
        ['#', '#', '#', '#', '#'],
    ]

    g_pos = build_g_pos(grid, "floor")

    expected = {
        (1, 1): {
            (1, 2): -4,
        },
        (1, 2): {
            (1, 3): 1,
            (1, 1): 1,
        },
        (1, 3): {
            (1, 2): -4,
        },
    }

    assert g_pos.adjacency == expected


def test_get_initial_state():
    grid = [
        ['#', '#', '#', '#'],
        ['#', 'S', '.', '#'],
        ['#', '#', '#', '#'],
    ]

    state = get_initial_state(grid)

    expected = (
        (1, 1),
        frozenset(),
        frozenset()
    )

    assert state == expected


def test_next_state_collect_key():
    grid = [
        ['#', '#', '#', '#'],
        ['#', '.', 'b', '#'],
        ['#', '#', '#', '#'],
    ]

    current_state = (
        (1, 1),
        frozenset({'a'}),
        frozenset()
    )

    result = next_state(current_state, (1, 2), grid)

    expected = (
        (1, 2),
        frozenset({'a', 'b'}),
        frozenset()
    )

    assert result == expected


def test_next_state_consume_bonus():
    grid = [
        ['#', '#', '#', '#'],
        ['#', '.', '+', '#'],
        ['#', '#', '#', '#'],
    ]

    current_state = (
        (1, 1),
        frozenset({'a'}),
        frozenset()
    )

    result = next_state(current_state, (1, 2), grid)

    expected = (
        (1, 2),
        frozenset({'a'}),
        frozenset({(1, 2)})
    )

    assert result == expected


def test_can_enter_normal_cell():
    state = (
        (1, 1),
        frozenset(),
        frozenset()
    )

    assert can_enter(state, '.') is True


def test_can_enter_door_with_key():
    state = (
        (1, 1),
        frozenset({'a'}),
        frozenset()
    )

    assert can_enter(state, 'A') is True


def test_can_enter_door_without_key():
    state = (
        (1, 1),
        frozenset(),
        frozenset()
    )

    assert can_enter(state, 'A') is False


def test_transition_cost_normal_cell():
    grid = [
        ['#', '#', '#', '#'],
        ['#', '.', '.', '#'],
        ['#', '#', '#', '#'],
    ]

    current_state = (
        (1, 1),
        frozenset(),
        frozenset()
    )

    result = transition_cost(current_state, (1, 2), grid)

    assert result == 1


def test_transition_cost_bonus_already_consumed():
    grid = [
        ['#', '#', '#', '#'],
        ['#', '.', '+', '#'],
        ['#', '#', '#', '#'],
    ]

    current_state = (
        (1, 1),
        frozenset(),
        frozenset({(1, 2)})
    )

    result = transition_cost(current_state, (1, 2), grid)

    assert result == 1


def test_transition_cost_bonus_first_visit():
    grid = [
        ['#', '#', '#', '#'],
        ['#', '.', '+', '#'],
        ['#', '#', '#', '#'],
    ]

    current_state = (
        (1, 1),
        frozenset(),
        frozenset()
    )

    result = transition_cost(current_state, (1, 2), grid)

    assert result == -4


def test_valid_neighbors_door_without_key():
    grid = [
        ['#', '#', '#', '#', '#'],
        ['#', 'S', 'A', '.', '#'],
        ['#', '#', '#', '#', '#'],
    ]

    current_state = (
        (1, 1),
        frozenset(),
        frozenset()
    )

    result = valid_neighbors(current_state, grid)

    assert result == []


def test_valid_neighbors_door_with_key():
    grid = [
        ['#', '#', '#', '#', '#'],
        ['#', 'S', 'A', '.', '#'],
        ['#', '#', '#', '#', '#'],
    ]

    current_state = (
        (1, 1),
        frozenset({'a'}),
        frozenset()
    )

    result = valid_neighbors(current_state, grid)

    assert result == [(1, 2)]


def test_valid_neighbors_conveyor():
    grid = [
        ['#', '#', '#', '#', '#'],
        ['#', '.', '>', '.', '#'],
        ['#', '#', '#', '#', '#'],
    ]

    current_state = (
        (1, 2),
        frozenset(),
        frozenset()
    )

    result = valid_neighbors(current_state, grid)

    assert result == [(1, 3)]
