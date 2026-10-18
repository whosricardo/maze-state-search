from src.graphs.estados import neighbor_logic
from src.graphs.io import parse_map


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
