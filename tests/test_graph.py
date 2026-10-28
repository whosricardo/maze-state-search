from src.graphs.graph import Graph


def test_add_vertex():
    graph = Graph()
    graph.add_vertex(3)
    graph.add_vertex(3)

    expected = {
        3: {}
    }

    assert graph.adjacency == expected


def test_add_edge():
    graph = Graph()

    graph.add_edge(3, 4, 2)
    graph.add_edge(3, 8, 7)

    expected = {
        3: {
            4: 2,
            8: 7
        },
        4: {},
        8: {}
    }

    assert graph.adjacency == expected
