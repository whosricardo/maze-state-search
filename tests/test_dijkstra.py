import pytest
from src.graphs.graph import Graph
from src.graphs.algorithms import useDijkstra


def test_direct_path():
    graph = Graph()
    graph.add_edge("A", "B", 4)

    distance, path = useDijkstra(graph, "A", "B")

    assert distance == 4
    assert path == ["A", "B"]


def test_shortest_indirect_path():
    graph = Graph()
    graph.add_edge("A", "B", 4)
    graph.add_edge("B", "C", 3)
    graph.add_edge("A", "C", 10)

    distance, path = useDijkstra(graph, "A", "C")

    assert distance == 7
    assert path == ["A", "B", "C"]


def test_shortest_path_multiple_edges():
    graph = Graph()
    graph.add_edge("A", "B", 4)
    graph.add_edge("A", "C", 10)
    graph.add_edge("B", "C", 3)
    graph.add_edge("B", "D", 12)
    graph.add_edge("C", "D", 2)

    distance, path = useDijkstra(graph, "A", "D")

    assert distance == 9
    assert path == ["A", "B", "C", "D"]


def test_same_source_and_destination():
    graph = Graph()
    graph.add_vertex("A")

    distance, path = useDijkstra(graph, "A", "A")

    assert distance == 0
    assert path == ["A"]


def test_unreachable_destination():
    graph = Graph()
    graph.add_edge("A", "B", 4)

    distance, path = useDijkstra(graph, "B", "A")

    assert distance == float("inf")
    assert path == []


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

    distance, path = useDijkstra(graph, "A", "B")

    assert distance == 0
    assert path == ["A", "B"]


def test_float_weights():
    graph = Graph()
    graph.add_edge("A", "B", 1.5)
    graph.add_edge("B", "C", 2.25)

    distance, path = useDijkstra(graph, "A", "C")

    assert distance == pytest.approx(3.75)
    assert path == ["A", "B", "C"]


def test_graph_with_cycle():
    graph = Graph()
    graph.add_edge("A", "B", 2)
    graph.add_edge("B", "C", 3)
    graph.add_edge("C", "A", 1)

    distance, path = useDijkstra(graph, "A", "C")

    assert distance == 5
    assert path == ["A", "B", "C"]


def test_disconnected_vertex():
    graph = Graph()
    graph.add_edge("A", "B", 4)
    graph.add_vertex("C")

    distance, path = useDijkstra(graph, "A", "C")

    assert distance == float("inf")
    assert path == []


def test_empty_graph():
    graph = Graph()

    with pytest.raises(ValueError):
        useDijkstra(graph, "A", "B")


def test_path_with_multiple_updates():
    graph = Graph()
    graph.add_edge("A", "D", 20)
    graph.add_edge("A", "B", 2)
    graph.add_edge("B", "D", 10)
    graph.add_edge("B", "C", 3)
    graph.add_edge("C", "D", 2)

    distance, path = useDijkstra(graph, "A", "D")

    assert distance == 7
    assert path == ["A", "B", "C", "D"]


def test_path_with_zero_weight_edges():
    graph = Graph()
    graph.add_edge("A", "B", 0)
    graph.add_edge("B", "C", 0)
    graph.add_edge("A", "C", 5)

    distance, path = useDijkstra(graph, "A", "C")

    assert distance == 0
    assert path == ["A", "B", "C"]


def test_multiple_shortest_paths():
    graph = Graph()
    graph.add_edge("A", "B", 2)
    graph.add_edge("A", "C", 2)
    graph.add_edge("B", "D", 3)
    graph.add_edge("C", "D", 3)

    distance, path = useDijkstra(graph, "A", "D")

    assert distance == 5
    assert path in [
        ["A", "B", "D"],
        ["A", "C", "D"]
    ]
