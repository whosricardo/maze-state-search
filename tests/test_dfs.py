import pytest

from src.graphs.graph import Graph
from src.graphs.algorithms import dfs


def test_dfs_simple_tree():
    graph = Graph()

    graph.add_edge("A", "B", 1)
    graph.add_edge("A", "C", 1)

    result = dfs(graph, "A")

    assert result["status"] == "Finalizado"
    assert result["has_cycle"] is False

    assert result["parents"] == {
        "A": None,
        "B": "A",
        "C": "A"
    }

    assert result["edge_types"] == [
        ("A", "B", "TREE"),
        ("A", "C", "TREE")
    ]


def test_dfs_detects_back_edge_and_cycle():
    graph = Graph()

    graph.add_edge("A", "B", 1)
    graph.add_edge("B", "C", 1)
    graph.add_edge("C", "A", 1)

    result = dfs(graph, "A")

    assert result["has_cycle"] is True

    assert ("A", "B", "TREE") in result["edge_types"]
    assert ("B", "C", "TREE") in result["edge_types"]
    assert ("C", "A", "BACK") in result["edge_types"]


def test_dfs_detects_forward_edge():
    graph = Graph()

    graph.add_edge("A", "B", 1)
    graph.add_edge("A", "C", 1)
    graph.add_edge("B", "C", 1)

    result = dfs(graph, "A")

    assert result["has_cycle"] is False

    assert ("A", "B", "TREE") in result["edge_types"]
    assert ("B", "C", "TREE") in result["edge_types"]
    assert ("A", "C", "FORWARD") in result["edge_types"]


def test_dfs_detects_cross_edge():
    graph = Graph()

    graph.add_edge("A", "B", 1)
    graph.add_edge("A", "C", 1)
    graph.add_edge("C", "B", 1)

    result = dfs(graph, "A")

    assert result["has_cycle"] is False

    assert ("A", "B", "TREE") in result["edge_types"]
    assert ("A", "C", "TREE") in result["edge_types"]
    assert ("C", "B", "CROSS") in result["edge_types"]


def test_dfs_invalid_start():
    graph = Graph()
    graph.add_vertex("A")

    with pytest.raises(ValueError):
        dfs(graph, "X")


def test_dfs_with_state_graph_vertices():
    graph = Graph()

    start = ((1, 1), frozenset(), frozenset())
    goal = ((1, 2), frozenset(), frozenset())

    graph.add_edge(start, goal, 1)
    graph.add_edge(goal, "ALVO", 0)

    result = dfs(graph, start)

    assert result["has_cycle"] is False

    assert result["parents"][start] is None
    assert result["parents"][goal] == start
    assert result["parents"]["ALVO"] == goal

    assert (start, goal, "TREE") in result["edge_types"]
    assert (goal, "ALVO", "TREE") in result["edge_types"]
