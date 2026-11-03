from src.graphs import graph
from src.graphs import metrics

def build_example_graph():
    g = graph.Graph()
    g.add_edge(1, 2, 3)
    g.add_edge(1, 3, 1)
    g.add_edge(2, 3, 2)
    return g

def test_count_vertex():
    g = build_example_graph()
    assert metrics.count_vertex(g) == 3
    
def test_count_edges():
    g = build_example_graph()
    assert metrics.count_edges(g) == 3
    

def test_out_degree():
    g = build_example_graph()
    assert metrics.out_degree(g, 1) == 2
    assert metrics.out_degree(g, 2) == 1
    assert metrics.out_degree(g, 3) == 0
    

def test_in_degree():
    g = build_example_graph()
    assert metrics.in_degree(g, 1) == 0
    assert metrics.in_degree(g, 2) == 1
    assert metrics.in_degree(g, 3) == 2
    