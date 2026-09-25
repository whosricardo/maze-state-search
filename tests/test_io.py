from src.graphs.io import parse_map


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
