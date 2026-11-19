from src.graphs.io import validate_map
from src.graphs.estados import (
    build_g_est,
    get_initial_state,
    TARGET_VERTEX,
)
from src.graphs.algorithms import (
    bfs,
    dfs,
    dijkstra,
    bellman_ford,
    find_trap_states,
)


def test_full_pipeline_simple_maze():
    grid = [
        ["#", "#", "#", "#"],
        ["#", "S", "G", "#"],
        ["#", "#", "#", "#"],
    ]

    assert validate_map(grid) is True

    graph = build_g_est(grid)
    start = get_initial_state(grid)

    assert start in graph.adjacency
    assert TARGET_VERTEX in graph.adjacency

    bfs_result = bfs(graph, start, TARGET_VERTEX)
    dfs_result = dfs(graph, start)
    dijkstra_result = dijkstra(graph, start, TARGET_VERTEX)
    bellman_result = bellman_ford(graph, start, TARGET_VERTEX)
    traps = find_trap_states(graph, start, TARGET_VERTEX)

    assert bfs_result["status"] == "Encontrado"
    assert bfs_result["path"][0] == start
    assert bfs_result["path"][-1] == TARGET_VERTEX

    assert dfs_result["status"] == "Finalizado"
    assert start in dfs_result["parents"]

    assert dijkstra_result["status"] == "Encontrado"
    assert dijkstra_result["path"][0] == start
    assert dijkstra_result["path"][-1] == TARGET_VERTEX
    assert dijkstra_result["cost"] is not None

    assert bellman_result["status"] == "Encontrado"
    assert bellman_result["path"][0] == start
    assert bellman_result["path"][-1] == TARGET_VERTEX
    assert bellman_result["cost"] is not None

    assert traps == set()


def test_pipeline_with_key_and_door():
    grid = [
        ["#", "#", "#", "#", "#", "#"],
        ["#", "S", "a", "A", "G", "#"],
        ["#", "#", "#", "#", "#", "#"],
    ]

    assert validate_map(grid) is True

    graph = build_g_est(grid)
    start = get_initial_state(grid)

    bfs_result = bfs(graph, start, TARGET_VERTEX)
    dijkstra_result = dijkstra(graph, start, TARGET_VERTEX)
    bellman_result = bellman_ford(graph, start, TARGET_VERTEX)

    assert bfs_result["status"] == "Encontrado"
    assert dijkstra_result["status"] == "Encontrado"
    assert bellman_result["status"] == "Encontrado"

    assert bfs_result["path"][0] == start
    assert bfs_result["path"][-1] == TARGET_VERTEX

    # At least one state along the path should contain key "a".
    states_with_key = [
        state
        for state in bfs_result["path"]
        if state != TARGET_VERTEX and "a" in state[1]
    ]

    assert states_with_key
