from src.graphs.graph import Graph
from src.graphs.algorithms import dfs


def build_example_graph():
    g = Graph()
    g.add_edge(1, 2, 1)
    g.add_edge(1, 3, 1)
    g.add_edge(2, 4, 1)
    g.add_edge(3, 4, 1)
    return g


def test_dfs_finds_path():
    g = build_example_graph()
    result = dfs(g, 1, 4)

    assert result["status"] == "Encontrado"
    assert result["path"] == [1, 3, 4]
    assert result["steps"] == len(result["path"]) - 1


def test_dfs_start_equals_end():
    g = build_example_graph()
    result = dfs(g, 1, 1)

    assert result["status"] == "Encontrado"
    assert result["steps"] == 0
    assert result["path"] == [1]


def test_dfs_impossible_access():
    g = Graph()
    g.add_edge(1, 2, 1)

    result = dfs(g, 2, 1)

    assert result["status"] == "Sem Caminho"
    assert result["steps"] is None
    assert result["path"] is None


def test_dfs_missing_start_raises_error():
    g = build_example_graph()

    with pytest.raises(ValueError):
        dfs(g, 99, 4)


def test_dfs_missing_end_raises_error():
    g = build_example_graph()

    with pytest.raises(ValueError):
        dfs(g, 1, 99)
