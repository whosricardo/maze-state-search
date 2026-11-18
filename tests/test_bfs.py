import pytest

from src.graphs import graph
from src.graphs.algorithms import bfs


def build_example_graph():
    g = graph.Graph()
    g.add_edge(1, 2, 3)
    g.add_edge(1, 3, 1)
    g.add_edge(2, 3, 2)
    return g


def test_bfs_finds_path():
    g = build_example_graph()
    result = bfs(g, 1, 3)

    assert result["status"] == "Encontrado"
    assert result["steps"] == 1
    assert result["path"] == [1, 3]


def test_bfs_start_equals_end():
    g = build_example_graph()
    result = bfs(g, 1, 1)

    assert result["status"] == "Encontrado"
    assert result["steps"] == 0
    assert result["path"] == [1]


def test_bfs_impossible_access():
    g = build_example_graph()
    result = bfs(g, 3, 1)

    assert result["status"] == "Sem Caminho"
    assert result["steps"] is None
    assert result["path"] is None


def test_bfs_without_end():
    g = build_example_graph()
    result = bfs(g, 1)

    assert result["status"] == "Explorado"
    assert result["steps"] is None
    assert result["path"] is None
    assert result["parents"] == {1: 1, 2: 1, 3: 1}


def build_cycle_graph():
    g = graph.Graph()
    g.add_edge(1, 2, 1)
    g.add_edge(2, 3, 1)
    g.add_edge(3, 1, 1)
    g.add_edge(3, 4, 1)
    return g


def test_bfs_cycle_graph():
    g = build_cycle_graph()
    result = bfs(g, 1, 4)

    assert result["status"] == "Encontrado"
    assert result["steps"] == 3
    assert result["path"] == [1, 2, 3, 4]
    assert result["parents"] == {1: 1, 2: 1, 3: 2, 4: 3}


def test_bfs_missing_start_raises_error():
    g = build_example_graph()

    with pytest.raises(ValueError):
        bfs(g, 99, 3)


def test_bfs_missing_end_raises_error():
    g = build_example_graph()

    with pytest.raises(ValueError):
        bfs(g, 1, 99)