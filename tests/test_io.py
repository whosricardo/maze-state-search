from src.graphs.io import (
    parse_map,
    validate_rectangular,
    validate_symbols,
    validate_start,
    validate_goal
)


def test_parse_map(tmp_path):
    map_file = tmp_path / "test_map.txt"

    map_file.write_text(
        "#####\n"
        "#S.G#\n"
        "#####\n"
    )

    result = parse_map(map_file)

    expected = [
        ['#', '#', '#', '#', '#'],
        ['#', 'S', '.', 'G', '#'],
        ['#', '#', '#', '#', '#'],
    ]

    assert result == expected


def test_validate_rectangular_valid(tmp_path):
    map_file = tmp_path / "test_map.txt"

    map_file.write_text(
        "#####\n"
        "#S.G#\n"
        "#####\n"
    )

    grid = parse_map(map_file)

    result = validate_rectangular(grid)

    assert result is True


def test_validate_rectangular_invalid(tmp_path):
    map_file = tmp_path / "test_map.txt"

    map_file.write_text(
        "#####\n"
        "#S.G#\n"
        "####\n"
    )

    grid = parse_map(map_file)

    result = validate_rectangular(grid)

    assert result is False


def test_validate_symbols_valid(tmp_path):
    map_file = tmp_path / "test_map.txt"

    map_file.write_text(
        "#####\n"
        "#S.G#\n"
        "#####\n"
    )

    grid = parse_map(map_file)

    result = validate_symbols(grid)

    assert result is True


def test_validate_symbols_invalid(tmp_path):
    map_file = tmp_path / "test_map.txt"

    map_file.write_text(
        "#####\n"
        "#S}G#\n"
        "#####\n"
    )

    grid = parse_map(map_file)

    result = validate_symbols(grid)

    assert result is False


def test_validate_start_valid(tmp_path):
    map_file = tmp_path / "test_map.txt"

    map_file.write_text(
        "#####\n"
        "#S.G#\n"
        "#####\n"
    )

    grid = parse_map(map_file)

    result = validate_start(grid)

    assert result is True


def test_validate_start_invalid_none(tmp_path):
    map_file = tmp_path / "test_map.txt"

    map_file.write_text(
        "#####\n"
        "##.G#\n"
        "#####\n"
    )

    grid = parse_map(map_file)

    result = validate_start(grid)

    assert result is False


def test_validate_start_invalid_multiple(tmp_path):
    map_file = tmp_path / "test_map.txt"

    map_file.write_text(
        "#####\n"
        "#S.S#\n"
        "###S#\n"
    )

    grid = parse_map(map_file)

    result = validate_start(grid)

    assert result is False


def test_validate_goal_valid(tmp_path):
    map_file = tmp_path / "test_map.txt"

    map_file.write_text(
        "#####\n"
        "#S.G#\n"
        "#####\n"
    )

    grid = parse_map(map_file)

    result = validate_goal(grid)

    assert result is True


def test_validate_goal_invalid_none(tmp_path):
    map_file = tmp_path / "test_map.txt"

    map_file.write_text(
        "#####\n"
        "#S.##\n"
        "#####\n"
    )

    grid = parse_map(map_file)

    result = validate_goal(grid)

    assert result is False


def test_validate_goal_invalid_multiple(tmp_path):
    map_file = tmp_path / "test_map.txt"

    map_file.write_text(
        "#####\n"
        "#G.G#\n"
        "#####\n"
    )

    grid = parse_map(map_file)

    result = validate_goal(grid)

    assert result is False
