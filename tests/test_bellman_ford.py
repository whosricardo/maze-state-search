import pytest

from src.graphs.graph import Graph
from src.graphs.algorithms import UseBellmanFord


def test_shortest_path():
    graph = Graph()
    graph.add_edge("A", "B", 10)
    graph.add_edge("A", "C", 1)
    graph.add_edge("C", "B", 2)

    assert UseBellmanFord(graph, "A", "B") == 3


def test_negative_weight():
    graph = Graph()
    graph.add_edge("A", "B", 4)
    graph.add_edge("A", "C", 2)
    graph.add_edge("C", "B", -3)

    assert UseBellmanFord(graph, "A", "B") == -1


def test_unreachable_destination():
    graph = Graph()
    graph.add_edge("A", "B", 1)
    graph.add_vertex("C")

    assert UseBellmanFord(graph, "A", "C") == float("inf")


def test_invalid_vertex_raises():
    graph = Graph()
    graph.add_edge("A", "B", 1)

    with pytest.raises(ValueError):
        UseBellmanFord(graph, "X", "B")

    with pytest.raises(ValueError):
        UseBellmanFord(graph, "A", "X")
