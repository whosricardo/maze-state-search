# [IA] Claude Code (Opus 5.5) – interface pygame: adaptador entre o código do grupo e a UI
#
# IMPORTANTE: este módulo NÃO implementa nenhum algoritmo nem a construção do
# grafo. Ele apenas CHAMA as funções escritas pelo grupo (io.py, estados.py,
# algorithms.py, metrics.py, export.py) e reorganiza os resultados em "frames"
# que a interface consegue animar.
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from time import perf_counter

from src.graphs.graph import Graph
from src.graphs.io import (
    parse_map,
    validate_rectangular,
    validate_symbols,
    ALLOWED_SYMBOLS,
)
from src.graphs.estados import (
    build_g_est,
    build_g_pos,
    get_initial_state,
    TARGET_VERTEX,
    KEY_CELLS,
    DOOR_CELLS,
)
from src.graphs.algorithms import (
    bfs,
    dfs,
    dijkstra,
    bellman_ford,
    find_trap_states,
)
from src.graphs.metrics import (
    count_vertex,
    count_edges,
    directed_density,
    theoretical_ceiling,
    state_occupancy,
    analyze_layers,
    count_map_features,
)
from src.graphs.export import format_state, build_bonus_id_map

ROOT = Path(__file__).resolve().parents[2]
MAPS_DIR = ROOT / "data" / "mapas"
GROUP_MAPS_DIR = ROOT / "data" / "mapas_grupo"
OUT_DIR = ROOT / "out" / "parte1"

ALGORITHMS = ["BFS", "Dijkstra", "Bellman-Ford", "DFS"]

MODELS = {
    "estados": "Grafo de estados",
    "chao": "Posições · porta = chão",
    "parede": "Posições · porta = parede",
}

STATUS_COLORS = {
    "Encontrado": "ok",
    "Sem Caminho": "err",
    "Recusado": "warn",
    "Ciclo Negativo": "warn",
    "Caminho Inválido": "err",
    "Finalizado": "info",
}


class MapError(Exception):
    pass


def layer_label(keys):
    return "".join(sorted(keys)) or "-"


def validation_problems(grid):
    """Lista legível dos problemas do mapa, usando as validações do grupo."""
    if not grid or not any(grid):
        return ["Mapa vazio."]
    problems = []
    if not validate_rectangular(grid):
        problems.append("As linhas não têm o mesmo tamanho (mapa não retangular).")
    if not validate_symbols(grid):
        bad = sorted({c for row in grid for c in row if c not in ALLOWED_SYMBOLS})
        problems.append("Símbolos inválidos: " + " ".join(repr(c) for c in bad))
    n_start = sum(c == 'S' for row in grid for c in row)
    n_goal = sum(c == 'G' for row in grid for c in row)
    if n_start != 1:
        problems.append(f"Precisa de exatamente 1 'S' (encontrados: {n_start}).")
    if n_goal != 1:
        problems.append(f"Precisa de exatamente 1 'G' (encontrados: {n_goal}).")
    return problems


def find_symbol(grid, symbol):
    for r, row in enumerate(grid):
        for c, cell in enumerate(row):
            if cell == symbol:
                return (r, c)
    return None


# ---------------------------------------------------------------- resultados
@dataclass
class Frame:
    pos: tuple
    keys: frozenset
    bonus: frozenset
    cost: float
    step: int
    label: str
    invalid: bool = False


@dataclass
class Run:
    algorithm: str
    model: str
    status: str = ""
    message: str = ""
    frames: list = field(default_factory=list)      # caminho animável
    explore: list = field(default_factory=list)     # ordem de descoberta (vértices)
    steps: object = None                            # como devolvido pelo algoritmo
    cost: object = None
    loop: bool = False                              # True = ciclo negativo em loop
    dfs_counts: dict = field(default_factory=dict)
    has_cycle: object = None
    elapsed_ms: float = 0.0

    @property
    def path_cost(self):
        return self.frames[-1].cost if self.frames else None

    @property
    def moves(self):
        return len(self.frames) - 1 if self.frames else None


# ---------------------------------------------------------------- sessão de um mapa
class MapSession:
    # [IA] Codex – aplica o modo de fonte consumível às buscas e aos rótulos.
    def __init__(self, path, fonte_consumivel=False):
        self.path = Path(path)
        self.name = self.path.stem
        try:
            self.grid = parse_map(self.path)
        except OSError as error:
            raise MapError(f"Não consegui ler {self.path.name}: {error}") from error
        except UnicodeDecodeError as error:
            raise MapError(f"{self.path.name} não é um arquivo de texto válido.") from error

        problems = validation_problems(self.grid)
        if problems:
            raise MapError(f"{self.path.name}: " + " ".join(problems))

        self.rows = len(self.grid)
        self.cols = len(self.grid[0])
        self.has_source = any("*" in row for row in self.grid)
        self.fonte_consumivel = fonte_consumivel and self.has_source
        self.bonus_ids = build_bonus_id_map(self.grid, fonte_consumivel=self.fonte_consumivel)
        self.start = get_initial_state(self.grid)
        self.s_pos = find_symbol(self.grid, 'S')
        self.g_pos = find_symbol(self.grid, 'G')
        self.map_keys = sorted({c for row in self.grid for c in row if c in KEY_CELLS})

        t0 = perf_counter()
        self.g_est = build_g_est(self.grid, fonte_consumivel=self.fonte_consumivel)
        self.build_ms = (perf_counter() - t0) * 1000
        self.graphs = {
            "estados": self.g_est,
            "chao": build_g_pos(self.grid, door_mode="floor"),
            "parede": build_g_pos(self.grid, door_mode="wall"),
        }
        self.has_target = TARGET_VERTEX in self.g_est.adjacency

        # ---------------- métricas (funções do grupo)
        states = [v for v in self.g_est.adjacency if v != TARGET_VERTEX]
        self.n_states = len(states)
        free, n_keys, n_bonus = count_map_features(self.grid)
        ceiling = theoretical_ceiling(self.grid) * 2 ** (len(self.bonus_ids) - n_bonus)
        g_pos = self.graphs["chao"]
        self.metrics = {
            "free": free,
            "n_keys": n_keys,
            "n_bonus": n_bonus,
            "gpos": (count_vertex(g_pos), count_edges(g_pos), directed_density(g_pos)),
            "gest": (count_vertex(self.g_est), count_edges(self.g_est), directed_density(self.g_est)),
            "teto": ceiling,
            "ocupacao": state_occupancy(self.g_est, ceiling),
            "becos": sum(1 for v in states if not self.g_est.adjacency[v]),
        }

        # ---------------- camadas (analyze_layers do grupo)
        self.layers = analyze_layers(self.g_est)
        self.layer_names = sorted(self.layers["camadas"], key=lambda n: (0 if n == "-" else len(n), n))
        self.layer_color = {}
        from src.frontend.theme import LAYER_COLORS
        for i, name in enumerate(self.layer_names):
            self.layer_color[name] = LAYER_COLORS[i % len(LAYER_COLORS)]
        self.layer_change_cells = {
            tuple(t["posicao"]) for t in self.layers["arcos_entre_camadas"]
        }

        # ---------------- multiplicidade: quantos estados existem por casa
        self.cell_counts = {None: Counter(s[0] for s in states)}
        for state in states:
            name = layer_label(state[1])
            self.cell_counts.setdefault(name, Counter())[state[0]] += 1

        # ---------------- estados-armadilha (busca no transposto do grupo)
        traps = find_trap_states(self.g_est, self.start, TARGET_VERTEX)
        self.traps = {t for t in traps if t != TARGET_VERTEX}
        self.trap_cells = Counter(t[0] for t in self.traps)
        self.trap_ratio = len(self.traps) / self.n_states if self.n_states else 0.0

        self._runs = {}

    # -------------------------------------------------------------- helpers
    def color_of_keys(self, keys):
        from src.frontend.theme import LAYER_COLORS
        name = layer_label(keys)
        if name not in self.layer_color:
            self.layer_color[name] = LAYER_COLORS[len(self.layer_color) % len(LAYER_COLORS)]
        return self.layer_color[name]

    def symbol_at(self, pos):
        r, c = pos
        return self.grid[r][c]

    @staticmethod
    def pos_of(vertex, model):
        return vertex[0] if model == "estados" else vertex

    @staticmethod
    def keys_of(vertex, model):
        return vertex[1] if model == "estados" else frozenset()

    def doors_open(self, model, keys):
        if model == "chao":
            return frozenset("abcd")
        if model == "parede":
            return frozenset()
        return keys

    # -------------------------------------------------------------- frames
    def _frames(self, vertices, model):
        graph = self.graphs[model]
        frames = []
        cost = 0
        held = set()
        prev = None
        for vertex in vertices:
            if vertex == TARGET_VERTEX:
                break
            if prev is not None:
                cost += graph.adjacency.get(prev, {}).get(vertex, 0)
            if model == "estados":
                pos, keys, bonus = vertex
                invalid = False
                label = format_state(vertex, self.bonus_ids)
            else:
                pos = vertex
                symbol = self.symbol_at(pos)
                # modelo ingênuo: marcamos (só para visualização) a porta
                # atravessada sem a chave ter sido pega antes no percurso
                invalid = symbol in DOOR_CELLS and symbol.lower() not in held
                if symbol in KEY_CELLS:
                    held.add(symbol)
                keys = frozenset(held)
                bonus = frozenset()
                label = f"({pos[0]},{pos[1]})"
            frames.append(Frame(pos, keys, bonus, cost, len(frames), label, invalid))
            prev = vertex
        return frames

    def _dfs_goal_path(self, result, model):
        parents = result["parents"]
        discovery = result["discovery"]
        if model == "estados":
            goals = [v for v in discovery if v != TARGET_VERTEX and self.symbol_at(v[0]) == 'G']
        else:
            goals = [v for v in discovery if v == self.g_pos]
        if not goals:
            return None
        node = min(goals, key=discovery.get)
        path = []
        while node is not None:
            path.append(node)
            node = parents.get(node)
        path.reverse()
        return path

    # -------------------------------------------------------------- execução
    def run(self, algorithm, model="estados"):
        key = (algorithm, model)
        if key in self._runs:
            return self._runs[key]

        graph = self.graphs[model]
        if model == "estados":
            start = self.start
            end = TARGET_VERTEX if self.has_target else None
        else:
            start = self.s_pos
            end = self.g_pos if self.g_pos in graph.adjacency else None

        run = Run(algorithm, model)
        no_target_msg = (
            "O ALVO nunca foi criado: nenhum estado alcançável a partir do início chega em G."
            if model == "estados" else
            "G não é alcançável neste modelo."
        )
        # [IA] Codex – integração com as buscas quando a saída não existe no grafo.
        # O destino isolado satisfaz a API das buscas ponderadas sem mudar o mapa.
        search_graph, search_end = graph, end
        if end is None and algorithm in ("Dijkstra", "Bellman-Ford"):
            search_graph = Graph()
            search_graph.adjacency = graph.adjacency.copy()
            search_end = object()
            search_graph.add_vertex(search_end)

        try:
            search = {"DFS": dfs, "BFS": bfs, "Dijkstra": dijkstra, "Bellman-Ford": bellman_ford}[algorithm]
            t0 = perf_counter()
            try:
                if algorithm == "DFS":
                    result = search(search_graph, start)
                else:
                    result = search(search_graph, start, search_end)
            finally:
                run.elapsed_ms = (perf_counter() - t0) * 1000

            if algorithm == "DFS":
                run.explore = sorted(result["discovery"], key=result["discovery"].get)
                run.dfs_counts = dict(Counter(kind for _, _, kind in result["edge_types"]))
                run.has_cycle = result["has_cycle"]
                path = self._dfs_goal_path(result, model)
                run.status = "Finalizado"
                if path:
                    run.frames = self._frames(path, model)
                    run.message = "Caminho na árvore DFS até G (não é o mais curto nem o mais barato)."
                else:
                    run.message = no_target_msg
            else:
                run.explore = list(result["parents"])
                run.status = result["status"]
                run.steps = result["steps"]
                run.cost = result.get("cost")
                if result.get("cycle"):
                    run.frames = self._frames(result["cycle"], model)
                    run.loop = True
                    lap = run.path_cost
                    run.message = (
                        f"Ciclo de {run.moves} arcos com custo {lap} por volta: "
                        "cada volta deixa o caminho mais barato, então não existe menor custo."
                    )
                elif end is None:
                    run.status = "Sem Caminho"
                    run.message = no_target_msg
                elif result["path"]:
                    run.frames = self._frames(result["path"], model)

        except ValueError as error:
            run.status = "Recusado"
            run.message = str(error)

        run.explore = [v for v in run.explore if v != TARGET_VERTEX]

        if model == "chao" and any(f.invalid for f in run.frames) and run.status == "Encontrado":
            run.status = "Caminho Inválido"
            run.message = "O caminho atravessa uma porta sem ter a chave (marcada com X)."

        self._runs[key] = run
        return run


# ---------------------------------------------------------------- análise rápida (editor)
def quick_analysis(grid, max_ceiling=2_000_000):
    problems = validation_problems(grid)
    if problems:
        return {"valid": False, "problems": problems}

    free, n_keys, n_bonus = count_map_features(grid)
    info = {
        "valid": True,
        "problems": [],
        "keys": len({c for row in grid for c in row if c in KEY_CELLS}),
        "doors": len({c for row in grid for c in row if c in DOOR_CELLS}),
        "conveyors": sum(c in "><^v" for row in grid for c in row),
        "bonus": n_bonus,
        "fountains": sum(c == '*' for row in grid for c in row),
        "size": (len(grid), len(grid[0])),
        "too_big": False,
    }
    ceiling = theoretical_ceiling(grid)
    info["teto"] = ceiling
    if ceiling > max_ceiling:
        info["too_big"] = True
        return info

    g_est = build_g_est(grid)
    start = get_initial_state(grid)
    states = [v for v in g_est.adjacency if v != TARGET_VERTEX]
    traps = {t for t in find_trap_states(g_est, start, TARGET_VERTEX) if t != TARGET_VERTEX}
    info["states"] = len(states)
    info["traps"] = len(traps)
    info["trap_ratio"] = len(traps) / len(states) if states else 0.0
    info["solvable"] = TARGET_VERTEX in g_est.adjacency
    if info["solvable"]:
        info["bfs_steps"] = bfs(g_est, start, TARGET_VERTEX)["steps"]
        bf = bellman_ford(g_est, start, TARGET_VERTEX)
        info["bf_status"] = bf["status"]
        info["bf_cost"] = bf["cost"]
    return info


def discover_maps(extra=()):
    seen = set()
    entries = []
    for folder, tag in ((MAPS_DIR, "fornecido"), (GROUP_MAPS_DIR, "grupo")):
        if folder.exists():
            for path in sorted(folder.glob("*.txt")):
                key = path.resolve()
                if key not in seen:
                    seen.add(key)
                    entries.append((path, tag))
    for path in extra:
        path = Path(path)
        key = path.resolve()
        if key not in seen:
            seen.add(key)
            entries.append((path, "extra"))
    return entries
