from src.graphs.io import (
    parse_map,
    validate_rectangular,
    validate_symbols
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
