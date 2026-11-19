import csv

from src.graphs.export import export_edges, graph_to_edge_list
from src.graphs.graph import Graph


def build_sample_graph():
    graph = Graph()
    graph.add_edge("A", "B", 3)
    graph.add_edge("A", "C", 1)
    graph.add_edge("B", "C", 2)
    return graph


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as file:
        return list(csv.reader(file))


def test_should_export_directed_edges(tmp_path):
    path = tmp_path / "edges.csv"

    export_edges(build_sample_graph(), path)

    assert read_csv(path) == [
        ["vertex", "destination", "weight"],
        ["A", "B", "3"],
        ["A", "C", "1"],
        ["B", "C", "2"],
    ]


def test_should_export_weights_preserved():
    graph = Graph()
    graph.add_edge("A", "B", 7)
    graph.add_edge("B", "C", 0)

    assert graph_to_edge_list(graph) == [("A", "B", 7), ("B", "C", 0)]


def test_should_not_export_edges_for_vertices_without_outgoing_edges():
    graph = build_sample_graph()
    graph.add_vertex("D")

    edges = graph_to_edge_list(graph)

    assert all(vertex not in ("C", "D") for vertex, _, _ in edges)
    assert len(edges) == 3


def test_should_not_invent_reverse_edges():
    edges = graph_to_edge_list(build_sample_graph())

    assert ("B", "A", 3) not in edges
    assert ("C", "A", 1) not in edges
    assert ("C", "B", 2) not in edges


def test_should_export_only_header_for_empty_graph(tmp_path):
    path = tmp_path / "edges.csv"

    export_edges(Graph(), path)

    assert read_csv(path) == [["vertex", "destination", "weight"]]
