import csv
import json
from pathlib import Path


def _prepare_path(path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def format_state(state, bonus_ids=None):
    if state == "ALVO":
        return "ALVO"

    position, keys, consumed_bonus = state
    row, column = position

    keys_label = "".join(sorted(keys)) or "-"

    if consumed_bonus:
        if bonus_ids is None:
            raise ValueError(
                "bonus_ids é necessário para formatar estados com bônus"
            )

        consumed_ids = sorted(
            bonus_ids[position]
            for position in consumed_bonus
        )
    else:
        consumed_ids = []

    bonus_label = "{" + ",".join(
        str(bonus_id)
        for bonus_id in consumed_ids
    ) + "}"

    return f"({row},{column})|{keys_label}|{bonus_label}"


def export_edges(graph, path, bonus_ids=None):
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
                    format_state(source, bonus_ids),
                    format_state(destination, bonus_ids),
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


def export_traps(traps, path, bonus_ids=None):
    path = _prepare_path(path)

    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["estado"])

        for trap in sorted(
            traps,
            key=lambda state: format_state(state, bonus_ids),
        ):
            writer.writerow([
                format_state(trap, bonus_ids)
            ])


def export_degrees(
    graph,
    path,
    in_degree_fn,
    out_degree_fn,
    bonus_ids=None,
):
    path = _prepare_path(path)

    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow([
            "estado",
            "grau_entrada",
            "grau_saida",
        ])

        for vertex in graph.adjacency:
            writer.writerow([
                format_state(vertex, bonus_ids),
                in_degree_fn(graph, vertex),
                out_degree_fn(graph, vertex),
            ])


def export_path_json(result, path, bonus_ids=None):
    path = _prepare_path(path)

    states = result.get("path")

    data = {
        "status": result["status"],
        "custo": result.get("cost"),
        "passos": result.get("steps"),
        "caminho": (
            [
                format_state(state, bonus_ids)
                for state in states
            ]
            if states
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


def export_negative_cycle_json(
    result,
    path,
    bonus_ids=None,
):
    path = _prepare_path(path)

    cycle = result.get("cycle")

    data = {
        "status": result["status"],
        "ciclo": (
            [
                format_state(state, bonus_ids)
                for state in cycle
            ]
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


def export_global_metrics(data, path):
    path = _prepare_path(path)

    with open(path, "w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False,
        )


def build_bonus_id_map(grid):
    bonus_ids = {}
    next_id = 0

    for row_index, row in enumerate(grid):
        for column_index, cell in enumerate(row):
            if cell == "+":
                bonus_ids[(row_index, column_index)] = next_id
                next_id += 1

    return bonus_ids


def export_layers(data, path):
    path = _prepare_path(path)

    with open(path, "w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False,
        )


def export_model_comparison(rows, path):
    path = _prepare_path(path)

    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow([
            "mapa",
            "modelagem",
            "status",
            "passos",
        ])

        writer.writerows(rows)
