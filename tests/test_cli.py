import pytest
from src.cli import parse_args


def test_parse_valid_map_path():
    args = parse_args(["mapa.txt"])

    assert args.map_path == "mapa.txt"


def test_missing_map_path():
    with pytest.raises(SystemExit) as context:
        parse_args([])

    assert context.value.code == 2


def test_parse_default_graph():
    args = parse_args(["mapa.txt"])

    assert args.graph == "pos"


def test_parse_valid_graph_choice():
    args = parse_args(["mapa.txt", "--graph", "est"])

    assert args.graph == "est"


def test_parse_invalid_graph_choice():
    with pytest.raises(SystemExit) as context:
        parse_args(["mapa.txt", "--graph", "invalid"])

    assert context.value.code == 2


def test_default_output_location_is_none():
    args = parse_args(["mapa.txt"])

    assert args.output_location is None


def test_parse_valid_output_location():
    args = parse_args([
        "mapa.txt",
        "--output_location",
        "resultado/output.txt"
    ])

    assert args.output_location == "resultado/output.txt"


def test_visualizar_default_false():
    args = parse_args(["mapa.txt"])

    assert args.visualizar is False


def test_visualizar_flag_active():
    args = parse_args(["mapa.txt", "--visualizar"])

    assert args.visualizar is True
