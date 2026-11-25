from src.frontend.model import MapSession


# [IA] Codex – caso de regressão da visualização com saída isolada.
def test_weighted_search_presentation_without_goal(tmp_path):
    path = tmp_path / "sem_saida.txt"
    path.write_text("########\n#S..#G##\n########\n", encoding="utf-8")
    session = MapSession(path)
    assert not session.has_target
    vertices = set(session.g_est.adjacency)

    for algorithm in ("BFS", "Dijkstra", "Bellman-Ford"):
        run = session.run(algorithm)
        assert run.status == "Sem Caminho"
        assert not run.frames
        assert set(run.explore) == vertices
        assert run.elapsed_ms >= 0

    assert set(session.g_est.adjacency) == vertices


def test_negative_cycle_is_visible_without_goal(tmp_path):
    path = tmp_path / "ciclo_sem_saida.txt"
    path.write_text("########\n#S*.#G##\n########\n", encoding="utf-8")
    session = MapSession(path)
    assert not session.has_target
    vertices = set(session.g_est.adjacency)

    assert session.run("Dijkstra").status == "Recusado"
    bellman_ford = session.run("Bellman-Ford")
    assert bellman_ford.status == "Ciclo Negativo"
    assert bellman_ford.loop
    assert bellman_ford.path_cost < 0
    assert set(bellman_ford.explore) <= vertices
    assert set(session.g_est.adjacency) == vertices
