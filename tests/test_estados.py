from src.graphs.estados import (
    neighbor_logic,
    cell_cost,
    build_g_pos,
    get_initial_state,
    next_state,
    can_enter,
    transition_cost,
    valid_neighbors,
    build_g_est
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


# [IA] ChatGPT – 61: sugestão de conferir G_pos com uma matriz pequena.
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


def test_build_g_est_start_to_goal():
    grid = [
        ['#', '#', '#', '#', '#'],
        ['#', 'S', 'G', '#', '#'],
        ['#', '#', '#', '#', '#'],
    ]

    g_est = build_g_est(grid)

    initial_state = (
        (1, 1),
        frozenset(),
        frozenset()
    )

    goal_state = (
        (1, 2),
        frozenset(),
        frozenset()
    )

    assert initial_state in g_est.adjacency
    assert goal_state in g_est.adjacency
    assert "ALVO" in g_est.adjacency

    assert g_est.get_neighbors(initial_state) == {
        goal_state: 1
    }

    assert g_est.get_neighbors(goal_state) == {
        "ALVO": 0
    }


def test_build_g_est_collects_key():
    grid = [
        ['#', '#', '#', '#', '#'],
        ['#', 'S', 'a', 'G', '#'],
        ['#', '#', '#', '#', '#'],
    ]

    g_est = build_g_est(grid)

    initial_state = (
        (1, 1),
        frozenset(),
        frozenset()
    )

    key_state = (
        (1, 2),
        frozenset({'a'}),
        frozenset()
    )

    start_with_key_state = (
        (1, 1),
        frozenset({'a'}),
        frozenset()
    )

    goal_state = (
        (1, 3),
        frozenset({'a'}),
        frozenset()
    )

    assert g_est.get_neighbors(initial_state) == {
        key_state: 1
    }

    assert g_est.get_neighbors(key_state) == {
        start_with_key_state: 1,
        goal_state: 1
    }

    assert g_est.get_neighbors(start_with_key_state) == {
        key_state: 1
    }

    assert g_est.get_neighbors(goal_state) == {
        "ALVO": 0
    }


def test_build_g_est_door_requires_key():
    grid = [
        ['#', '#', '#', '#', '#', '#', '#'],
        ['#', 'S', '.', 'A', '.', 'G', '#'],
        ['#', '.', '.', 'a', '.', '.', '#'],
        ['#', '#', '#', '#', '#', '#', '#'],
    ]

    g_est = build_g_est(grid)

    before_door_without_key = (
        (1, 2),
        frozenset(),
        frozenset()
    )

    before_door_with_key = (
        (1, 2),
        frozenset({'a'}),
        frozenset()
    )

    door_with_key = (
        (1, 3),
        frozenset({'a'}),
        frozenset()
    )

    assert door_with_key not in g_est.get_neighbors(before_door_without_key)

    assert door_with_key in g_est.get_neighbors(before_door_with_key)

    assert g_est.get_neighbors(before_door_with_key)[door_with_key] == 1


def test_build_g_est_bonus_first_and_repeated_visit():
    grid = [
        ['#', '#', '#', '#', '#'],
        ['#', 'S', '+', 'G', '#'],
        ['#', '#', '#', '#', '#'],
    ]

    g_est = build_g_est(grid)

    initial_state = (
        (1, 1),
        frozenset(),
        frozenset()
    )

    bonus_state = (
        (1, 2),
        frozenset(),
        frozenset({(1, 2)})
    )

    start_after_bonus = (
        (1, 1),
        frozenset(),
        frozenset({(1, 2)})
    )

    goal_after_bonus = (
        (1, 3),
        frozenset(),
        frozenset({(1, 2)})
    )

    assert g_est.get_neighbors(initial_state)[bonus_state] == -4

    assert g_est.get_neighbors(bonus_state)[start_after_bonus] == 1

    assert g_est.get_neighbors(start_after_bonus)[bonus_state] == 1

    assert g_est.get_neighbors(bonus_state)[goal_after_bonus] == 1

    assert g_est.get_neighbors(goal_after_bonus) == {
        "ALVO": 0
    }


def test_build_g_est_conveyor_direction():
    grid = [
        ['#', '#', '#', '#', '#'],
        ['#', 'S', '>', 'G', '#'],
        ['#', '#', '#', '#', '#'],
    ]

    g_est = build_g_est(grid)

    initial_state = (
        (1, 1),
        frozenset(),
        frozenset()
    )

    conveyor_state = (
        (1, 2),
        frozenset(),
        frozenset()
    )

    goal_state = (
        (1, 3),
        frozenset(),
        frozenset()
    )

    assert g_est.get_neighbors(initial_state) == {
        conveyor_state: 1
    }

    assert g_est.get_neighbors(conveyor_state) == {
        goal_state: 1
    }

    assert g_est.get_neighbors(goal_state) == {
        "ALVO": 0
    }


def test_build_g_est_source_cost():
    grid = [
        ['#', '#', '#', '#', '#'],
        ['#', 'S', '*', 'G', '#'],
        ['#', '#', '#', '#', '#'],
    ]

    g_est = build_g_est(grid)

    initial_state = (
        (1, 1),
        frozenset(),
        frozenset()
    )

    source_state = (
        (1, 2),
        frozenset(),
        frozenset()
    )

    goal_state = (
        (1, 3),
        frozenset(),
        frozenset()
    )

    assert g_est.get_neighbors(initial_state)[source_state] == -2

    assert g_est.get_neighbors(source_state)[initial_state] == 1

    assert g_est.get_neighbors(source_state)[goal_state] == 1

    assert g_est.get_neighbors(goal_state) == {
        "ALVO": 0
    }
