import pytest
from src.graphs.graph import Graph
from src.graphs.algorithms import useDijkstra


def test_direct_path():
    graph = Graph()
    graph.add_edge("A", "B", 4)

    result = useDijkstra(graph, "A", "B")

    assert result == 4


def test_shortest_indirect_path():
    graph = Graph()
    graph.add_edge("A", "B", 4)
    graph.add_edge("B", "C", 3)
    graph.add_edge("A", "C", 10)

    result = useDijkstra(graph, "A", "C")

    assert result == 7


def test_shortest_path_multiple_edges():
    graph = Graph()
    graph.add_edge("A", "B", 4)
    graph.add_edge("A", "C", 10)
    graph.add_edge("B", "C", 3)
    graph.add_edge("B", "D", 12)
    graph.add_edge("C", "D", 2)

    result = useDijkstra(graph, "A", "D")

    assert result == 9


def test_same_source_and_destination():
    graph = Graph()
    graph.add_vertex("A")

    result = useDijkstra(graph, "A", "A")

    assert result == 0


def test_unreachable_destination():
    graph = Graph()
    graph.add_edge("A", "B", 4)

    result = useDijkstra(graph, "B", "A")

    assert result == float("inf")


def test_invalid_source():
    graph = Graph()
    graph.add_vertex("A")

    with pytest.raises(ValueError):
        useDijkstra(graph, "X", "A")


def test_invalid_destination():
    graph = Graph()
    graph.add_vertex("A")

    with pytest.raises(ValueError):
        useDijkstra(graph, "A", "X")


def test_negative_weight():
    graph = Graph()
    graph.add_edge("A", "B", -5)

    with pytest.raises(ValueError):
        useDijkstra(graph, "A", "B")


def test_zero_weight():
    graph = Graph()
    graph.add_edge("A", "B", 0)

    result = useDijkstra(graph, "A", "B")

    assert result == 0


def test_float_weights():
    graph = Graph()
    graph.add_edge("A", "B", 1.5)
    graph.add_edge("B", "C", 2.25)

    result = useDijkstra(graph, "A", "C")

    assert result == pytest.approx(3.75)


def test_graph_with_cycle():
    graph = Graph()
    graph.add_edge("A", "B", 2)
    graph.add_edge("B", "C", 3)
    graph.add_edge("C", "A", 1)

    result = useDijkstra(graph, "A", "C")

    assert result == 5


def test_disconnected_vertex():
    graph = Graph()
    graph.add_edge("A", "B", 4)
    graph.add_vertex("C")

    result = useDijkstra(graph, "A", "C")

    assert result == float("inf")


def test_empty_graph():
    graph = Graph()

    with pytest.raises(ValueError):
        useDijkstra(graph, "A", "B")
