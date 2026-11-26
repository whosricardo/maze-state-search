from src.graphs.graph import Graph


# [IA] ChatGPT – 55–57: revisão dos casos de inserção e consulta na adjacência.
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


def test_add_edge_duplicate():
    graph = Graph()

    graph.add_edge(3, 4, 2)
    graph.add_edge(3, 4, 6)

    expected = {
        3: {4: 2},
        4: {}
    }

    assert graph.adjacency == expected


def test_get_neighbors():
    graph = Graph()

    graph.add_edge(3, 4, 2)

    expected = {
        4: 2
    }

    assert graph.get_neighbors(3) == expected
    assert graph.get_neighbors(4) == {}


def test_graph_is_directed():
    graph = Graph()

    graph.add_edge(3, 4, 2)

    assert graph.get_neighbors(3) == {4: 2}
    assert graph.get_neighbors(4) == {}


def test_get_neighbors_unknown_vertex():
    graph = Graph()

    assert graph.get_neighbors(99) == {}


def test_graph_accepts_state_as_vertex():
    graph = Graph()

    state = (
        (1, 1),
        frozenset({'a'}),
        frozenset()
    )

    graph.add_vertex(state)

    assert state in graph.adjacency
