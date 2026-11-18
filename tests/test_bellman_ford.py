from src.graphs.graph import Graph
from src.graphs.algorithms import bellman_ford


def test_bellman_ford_negative_weight_without_negative_cycle():
    graph = Graph()

    graph.add_edge("A", "B", 4)
    graph.add_edge("A", "C", 2)
    graph.add_edge("C", "B", -3)

    result = bellman_ford(graph, "A", "B")

    assert result["status"] == "Encontrado"
    assert result["cost"] == -1
    assert result["path"] == ["A", "C", "B"]
    assert result["cycle"] is None


def test_bellman_ford_detects_and_returns_negative_cycle():
    graph = Graph()

    graph.add_edge("A", "B", 1)
    graph.add_edge("B", "C", -3)
    graph.add_edge("C", "B", 1)
    graph.add_edge("C", "D", 2)

    result = bellman_ford(graph, "A", "D")

    assert result["status"] == "Ciclo Negativo"
    assert result["path"] is None
    assert result["cycle"] is not None

    cycle = result["cycle"]

    assert cycle[0] == cycle[-1]

    cycle_cost = 0

    for current, next_vertex in zip(cycle, cycle[1:]):
        assert next_vertex in graph.get_neighbors(current)
        cycle_cost += graph.get_neighbors(current)[next_vertex]

    assert cycle_cost < 0


def test_bellman_ford_ignores_unreachable_negative_cycle():
    graph = Graph()

    graph.add_edge("A", "B", 2)
    graph.add_edge("B", "D", 3)

    graph.add_edge("X", "Y", -5)
    graph.add_edge("Y", "X", 1)

    result = bellman_ford(graph, "A", "D")

    assert result["status"] == "Encontrado"
    assert result["cost"] == 5
    assert result["path"] == ["A", "B", "D"]
    assert result["cycle"] is None
