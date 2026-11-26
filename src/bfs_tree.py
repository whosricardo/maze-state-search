# [IA] ChatGPT – apoio à sintaxe de visualização da árvore BFS com Matplotlib.
from collections import defaultdict, deque
from pathlib import Path
import sys

import matplotlib.pyplot as plt

from src.graphs.algorithms import bfs
from src.graphs.estados import build_g_est, get_initial_state, TARGET_VERTEX
from src.graphs.io import parse_map


def is_goal_state(state, grid):
    if state == TARGET_VERTEX:
        return False

    position, _, _ = state
    row, col = position
    return grid[row][col] == "G"


def short_label(state):
    if state == TARGET_VERTEX:
        return "ALVO"

    position, keys, bonuses = state
    row, col = position
    keys_text = "".join(sorted(keys)) if keys else "-"
    return f"({row},{col})\nch:{keys_text}\nb:{len(bonuses)}"


def build_children_map(parents, root, include_target=False):
    children = defaultdict(list)

    for node, parent in parents.items():
        if node == root:
            continue
        if node == TARGET_VERTEX and not include_target:
            continue
        children[parent].append(node)

    return children


def compute_depths(root, children):
    # Organiza a árvore já produzida pelo BFS em níveis para desenhá-la.
    depth = {root: 0}
    queue = deque([root])

    while queue:
        current = queue.popleft()
        for child in children.get(current, []):
            depth[child] = depth[current] + 1
            queue.append(child)

    return depth


def compute_positions(depth):
    levels = defaultdict(list)
    for node, level in depth.items():
        levels[level].append(node)

    positions = {}
    for level in sorted(levels):
        nodes = sorted(levels[level], key=repr)
        count = len(nodes)
        for index, node in enumerate(nodes):
            positions[node] = (index - (count - 1) / 2, -level)

    return positions, levels


def draw_bfs_tree(graph, start, grid, output_path, include_target=False):
    parents = bfs(graph, start)["parents"]
    children = build_children_map(parents, start, include_target)
    depth = compute_depths(start, children)
    positions, levels = compute_positions(depth)

    max_width = max(len(nodes) for nodes in levels.values())
    height_levels = len(levels)
    show_labels = len(positions) <= 60

    fig_width = max(8, min(30, max_width * 0.8))
    fig_height = max(6, min(30, height_levels *
                     (0.65 if show_labels else 0.35)))
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))

    # Arestas da árvore: usa os predecessores retornados pelo BFS do grupo.
    for node, parent in parents.items():
        if node == start or node not in positions or parent not in positions:
            continue
        x_parent, y_parent = positions[parent]
        x_node, y_node = positions[node]
        ax.plot([x_parent, x_node], [y_parent, y_node],
                color="#808080", linewidth=0.9, alpha=0.8, zorder=1)

    xs, ys, sizes, colors = [], [], [], []
    for node, (x, y) in positions.items():
        xs.append(x)
        ys.append(y)
        if node == start:
            sizes.append(180)
            colors.append("tab:green")
        elif node == TARGET_VERTEX or is_goal_state(node, grid):
            sizes.append(120)
            colors.append("tab:orange")
        else:
            sizes.append(60)
            colors.append("tab:blue")

    ax.scatter(xs, ys, s=sizes, c=colors, zorder=3)

    if show_labels:
        for node, (x, y) in positions.items():
            ax.annotate(short_label(node), (x, y), xytext=(9, 0),
                        textcoords="offset points", ha="left", va="center",
                        fontsize=9, zorder=4)

    total_nodes = len(positions)
    total_edges = sum(node != start and parent in positions and node in positions
                      for node, parent in parents.items())
    subtitle = (f"Vértices na árvore: {total_nodes} | Arestas: {total_edges} | "
                f"Profundidade máxima: {max(depth.values())}")

    # Título e subtítulo separados, com espaço reservado no topo.
    ax.set_title("Árvore BFS do grafo de estados\n" + subtitle,
                 fontsize=12, linespacing=1.7, pad=22)
    ax.margins(x=0.18, y=0.025)
    ax.axis("off")
    fig.tight_layout(pad=2)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return output_path


def main():
    if len(sys.argv) < 2:
        print("Uso: python -m src.bfs_tree <mapa.txt> [saida.png]")
        sys.exit(1)

    map_path = Path(sys.argv[1])
    output_path = (Path(sys.argv[2]) if len(sys.argv) >= 3
                   else Path("out/parte1/arvore_bfs.png"))

    grid = parse_map(map_path)
    g_est = build_g_est(grid)
    start = get_initial_state(grid)
    saved_path = draw_bfs_tree(g_est, start, grid, output_path,
                               include_target=False)
    print(f"Árvore BFS salva em: {saved_path}")


if __name__ == "__main__":
    main()
