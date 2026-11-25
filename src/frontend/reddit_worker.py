# [IA] Codex – suporte técnico de IPC para chamar as funções de busca da equipe
from time import perf_counter


def serve(channel, path):
    try:
        from src.graphs.algorithms import bellman_ford, bfs, dfs, dijkstra
        from src.parte2.loader import (
            aggregate_interactions, build_dijkstra_graph, build_reddit_graph, load_reddit_dataset,
        )

        data = aggregate_interactions(load_reddit_dataset(path))
        original = build_reddit_graph(data)
        transformed = build_dijkstra_graph(data)
        channel.send(("ready", sorted(original.adjacency)))
        while True:
            algorithm, origin, destination = channel.recv()
            try:
                start = perf_counter()
                if algorithm == "bfs":
                    result = bfs(original, origin, destination or None)
                    details = {
                        "status": result["status"],
                        "reachable_vertices": len(result["parents"]),
                        "steps": result["steps"],
                        "path": result["path"],
                    }
                elif algorithm == "dfs":
                    result = dfs(original, origin)
                    details = {
                        "status": result["status"],
                        "visited_vertices": len(result["discovery"]),
                        "has_cycle": result["has_cycle"],
                    }
                    if destination:
                        details["Destino alcançado"] = destination in result["discovery"]
                else:
                    run, graph = (
                        (dijkstra, transformed) if algorithm == "dijkstra" else (bellman_ford, original)
                    )
                    result = run(graph, origin, destination)
                    details = {key: result[key] for key in ("status", "steps", "path", "cost", "cycle")
                               if key in result}
                details["Tempo desta execução"] = f"{(perf_counter() - start) * 1000:.3f} ms"
                # [IA] Codex – expor o subgrafo induzido pelos vértices alcançados.
                names = sorted(result["parents"])
                indices = {name: index for index, name in enumerate(names)}
                edges = [
                    (indices[source], indices[destination])
                    for source in names
                    for destination in original.adjacency[source]
                    if destination in indices
                ]
                channel.send(("result", (details, names, edges)))
            except Exception as error:
                channel.send(("error", str(error)))
    except (EOFError, BrokenPipeError):
        pass
    except Exception as error:
        channel.send(("load_error", str(error)))
    finally:
        channel.close()
