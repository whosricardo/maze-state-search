from graph import Graph

def count_vertex(G: Graph):
    return len(G.adjacency)

def count_edges(G: Graph):
    edges = G.adjacency
    count = 0

    for i in edges:
        count += len(G.get_neighbors(i))

    return count

def out_degree(G: Graph, vertex):
    
    edges = G.adjacency
    if vertex not in edges:
        raise ValueError("Vertice não está no Grafo")
    
    return len(G.get_neighbors(vertex))
    