import pytest

from src.graphs.graph import Graph
from src.graphs.algorithms import dijkstra


def test_dijkstra_returns_cost_and_path():
    graph = Graph()

    graph.add_edge("A", "B", 4)
    graph.add_edge("A", "C", 1)
    graph.add_edge("C", "B", 2)

    result = dijkstra(graph, "A", "B")

    assert result["status"] == "Encontrado"
    assert result["cost"] == 3
    assert result["steps"] == 2
    assert result["path"] == ["A", "C", "B"]


def test_dijkstra_rejects_negative_weight():
    graph = Graph()

    graph.add_edge("A", "B", -1)

    with pytest.raises(ValueError):
        dijkstra(graph, "A", "B")


def test_dijkstra_unreachable_destination():
    graph = Graph()

    graph.add_vertex("A")
    graph.add_vertex("B")

    result = dijkstra(graph, "A", "B")

    assert result["status"] == "Sem Caminho"
    assert result["cost"] is None
    assert result["steps"] is None
    assert result["path"] is None


def test_dijkstra_same_start_and_end():
    graph = Graph()

    graph.add_vertex("A")

    result = dijkstra(graph, "A", "A")

    assert result["status"] == "Encontrado"
    assert result["cost"] == 0
    assert result["steps"] == 0
    assert result["path"] == ["A"]


def test_dijkstra_equal_cost_paths():
    graph = Graph()

    graph.add_edge("A", "B", 1)
    graph.add_edge("A", "C", 1)

    graph.add_edge("B", "D", 1)
    graph.add_edge("C", "D", 1)

    result = dijkstra(graph, "A", "D")

    assert result["status"] == "Encontrado"
    assert result["cost"] == 2
    assert result["steps"] == 2

    assert result["path"] in [
        ["A", "B", "D"],
        ["A", "C", "D"],
    ]


def test_dijkstra_with_g_est_vertices_and_equal_cost():
    graph = Graph()

    start = ((1, 1), frozenset(), frozenset())
    state_a = ((1, 2), frozenset(), frozenset())
    state_b = ((2, 1), frozenset(), frozenset())

    graph.add_edge(start, state_a, 1)
    graph.add_edge(start, state_b, 1)

    graph.add_edge(state_a, "ALVO", 1)
    graph.add_edge(state_b, "ALVO", 1)

    result = dijkstra(graph, start, "ALVO")

    assert result["status"] == "Encontrado"
    assert result["cost"] == 2
    assert result["steps"] == 2
    assert result["path"][0] == start
    assert result["path"][-1] == "ALVO"


def test_dijkstra_invalid_start():
    graph = Graph()
    graph.add_vertex("A")

    with pytest.raises(ValueError):
        dijkstra(graph, "X", "A")


def test_dijkstra_invalid_destination():
    graph = Graph()
    graph.add_vertex("A")

    with pytest.raises(ValueError):
        dijkstra(graph, "A", "X")
