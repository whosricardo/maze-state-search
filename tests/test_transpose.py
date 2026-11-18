import pytest

from src.graphs.graph import Graph
from src.graphs.algorithms import (
    transpose_graph,
    reachable_vertices,
    find_trap_states,
)


def test_transpose_graph_reverses_edges_and_preserves_weights():
    graph = Graph()

    graph.add_edge("A", "B", 3)
    graph.add_edge("B", "C", 5)

    transposed = transpose_graph(graph)

    assert transposed.get_neighbors("A") == {}
    assert transposed.get_neighbors("B") == {"A": 3}
    assert transposed.get_neighbors("C") == {"B": 5}


def test_transpose_graph_preserves_isolated_vertices():
    graph = Graph()

    graph.add_vertex("A")
    graph.add_vertex("B")

    transposed = transpose_graph(graph)

    assert "A" in transposed.adjacency
    assert "B" in transposed.adjacency
    assert transposed.get_neighbors("A") == {}
    assert transposed.get_neighbors("B") == {}


def test_reachable_vertices():
    graph = Graph()

    graph.add_edge("A", "B", 1)
    graph.add_edge("B", "C", 1)

    graph.add_edge("X", "Y", 1)

    result = reachable_vertices(graph, "A")

    assert result == {"A", "B", "C"}


def test_reachable_vertices_respects_direction():
    graph = Graph()

    graph.add_edge("A", "B", 1)

    result = reachable_vertices(graph, "B")

    assert result == {"B"}


def test_reachable_vertices_invalid_start():
    graph = Graph()
    graph.add_vertex("A")

    with pytest.raises(ValueError):
        reachable_vertices(graph, "X")


def test_find_trap_states():
    graph = Graph()

    graph.add_edge("START", "A", 1)

    graph.add_edge("A", "B", 1)
    graph.add_edge("B", "ALVO", 0)

    graph.add_edge("A", "C", 1)
    graph.add_edge("C", "D", 1)

    traps = find_trap_states(graph, "START")

    assert traps == {"C", "D"}


def test_find_trap_states_does_not_include_unreachable_vertices():
    graph = Graph()

    graph.add_edge("START", "A", 1)
    graph.add_edge("A", "ALVO", 0)

    graph.add_edge("X", "Y", 1)

    traps = find_trap_states(graph, "START")

    assert traps == set()


def test_find_trap_states_without_target():
    graph = Graph()

    graph.add_edge("START", "A", 1)
    graph.add_edge("A", "B", 1)

    traps = find_trap_states(graph, "START")

    assert traps == {"START", "A", "B"}


def test_find_trap_states_with_state_vertices():
    graph = Graph()

    start = ((1, 1), frozenset(), frozenset())
    safe = ((1, 2), frozenset(), frozenset())
    trap = ((2, 1), frozenset(), frozenset())

    graph.add_edge(start, safe, 1)
    graph.add_edge(safe, "ALVO", 0)

    graph.add_edge(start, trap, 1)

    traps = find_trap_states(graph, start)

    assert traps == {trap}
