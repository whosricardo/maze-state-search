import csv
from pathlib import Path

from src.graphs.graph import Graph

def graph_to_edge_list(graph: Graph) -> list[tuple]:

    edges = []

    for vertex in graph.adjacency:
        for destination, weight in graph.get_neighbors(vertex).items():
            edges.append((vertex, destination, weight))

    return edges

def export_edges(graph: Graph, path: str | Path) -> None:

    edges = graph_to_edge_list(graph)

    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["vertex", "destination", "weight"])
        writer.writerows(edges)
