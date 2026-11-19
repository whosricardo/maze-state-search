import csv
import json
from pathlib import Path


def _prepare_path(path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def format_state(state):
    if state == "ALVO":
        return "ALVO"

    position, keys, consumed_bonus = state
    row, column = position

    keys_label = "".join(sorted(keys)) or "-"

    bonus_label = "{" + ",".join(
        str(bonus)
        for bonus in sorted(consumed_bonus)
    ) + "}"

    return f"({row},{column})|{keys_label}|{bonus_label}"


def export_edges(graph, path):
    path = _prepare_path(path)

    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow([
            "origem",
            "destino",
            "custo",
        ])

        for source, neighbors in graph.adjacency.items():
            for destination, cost in neighbors.items():
                writer.writerow([
                    format_state(source),
                    format_state(destination),
                    cost,
                ])


def export_solutions(rows, path):
    path = _prepare_path(path)

    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow([
            "mapa",
            "algoritmo",
            "status",
            "passos",
            "custo",
        ])

        writer.writerows(rows)


def export_dfs_classification(rows, path):
    path = _prepare_path(path)

    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow([
            "mapa",
            "origem",
            "destino",
            "tipo",
        ])

        writer.writerows(rows)


def export_traps(traps, path):
    path = _prepare_path(path)

    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow(["estado"])

        for trap in sorted(traps, key=format_state):
            writer.writerow([
                format_state(trap)
            ])


def export_path_json(result, path):
    path = _prepare_path(path)

    path_states = result.get("path")

    data = {
        "status": result["status"],
        "custo": result.get("cost"),
        "passos": result.get("steps"),
        "caminho": (
            [format_state(state) for state in path_states]
            if path_states
            else None
        ),
    }

    with open(path, "w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False,
        )


def export_negative_cycle_json(result, path):
    path = _prepare_path(path)

    cycle = result.get("cycle")

    data = {
        "status": result["status"],
        "ciclo": (
            [format_state(state) for state in cycle]
            if cycle
            else None
        ),
    }

    with open(path, "w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False,
        )
