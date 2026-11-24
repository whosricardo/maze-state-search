# [IA] Codex – suporte de sintaxe Pygame para exibir resultados e figuras da equipe
import json
import multiprocessing
from pathlib import Path

import pygame

from src.frontend import theme as T
from src.frontend.theme import Fonts, px
from src.frontend.widgets import TextInput, text, text_fit, wrap
from src.frontend.reddit_worker import serve

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "out" / "parte2"
DATASET = ROOT / "data" / "dataset_parte2" / "soc-redditHyperlinks-body.tsv"
ALGORITHMS = {"bfs": "BFS", "dfs": "DFS", "dijkstra": "Dijkstra", "bellman_ford": "Bellman-Ford"}
FIGURES = {
    "comparacao_algoritmos": ("Comparação dos algoritmos", None),
    "comportamento_dfs": ("Comportamento da DFS", None),
    "comparacao_custos_dijkstra": ("Custos do Dijkstra", None),
    "scatter_graus_symlog": ("Distribuição dos graus", "nota_analitica_exploratoria1"),
    "interacoes_ao_longo_do_tempo": ("Interações ao longo do tempo", "nota_analitica_exploratoria2"),
    "explanatoria_1_concentracao_graus": ("Concentração dos graus", "nota_analitica_explanatoria1"),
    "explanatoria_2_crescimento_interacoes": ("Crescimento das interações", "nota_analitica_explanatoria2"),
}
LABELS = {
    "status": "Status", "steps": "Passos", "path": "Caminho", "cost": "Custo",
    "cycle": "Ciclo", "reachable_vertices": "Vértices alcançados",
    "visited_vertices": "Vértices visitados", "edge_types": "Classificação de arcos",
    "has_cycle": "Tem ciclo",
}


class RedditScreen:
    def __init__(self, app):
        self.app = app
        self.algorithm = "bfs"
        self.mode = "saved"
        self.case_index = 0
        self.fig_index = 0
        self.scroll = 0
        self.max_scroll = 0
        self.images = {}
        self.report_error = None
        self.process = None
        self.channel = None
        self.communities = ()
        self.community_set = set()
        self.origin = TextInput(placeholder="Origem")
        self.destination = TextInput(placeholder="Destino")
        self.running = False
        self.live_error = None
        self.result = None
        try:
            self.report = json.loads((OUT / "parte2_report.json").read_text(encoding="utf-8"))
        except (OSError, ValueError) as error:
            self.report = {}
            self.report_error = str(error)

    def handle_event(self, event):
        if self.mode == "live" and (self.origin.handle_event(event) or self.destination.handle_event(event)):
            return
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.app.open_menu()

    # [IA] Codex – controles de consulta e polling sem bloquear a janela
    def update(self, dt):
        if self.channel is None:
            return
        try:
            if self.channel.poll():
                kind, value = self.channel.recv()
                self.running = False
                if kind == "ready":
                    self.communities = tuple(value)
                    self.community_set = set(value)
                elif kind == "result":
                    self.result = value
                elif kind == "load_error":
                    self.stop()
                    self.live_error = value
                else:
                    self.live_error = value
        except (EOFError, OSError):
            self.stop()
            self.live_error = "A consulta foi interrompida."

    def start(self):
        self.live_error = None
        self.result = None
        ctx = multiprocessing.get_context("spawn")
        parent, child = ctx.Pipe()
        self.process = ctx.Process(target=serve, args=(child, DATASET), daemon=True)
        try:
            self.process.start()
        except (OSError, RuntimeError) as error:
            parent.close()
            self.process = None
            self.live_error = str(error)
        else:
            self.channel = parent
            self.running = True
        finally:
            child.close()

    def stop(self):
        if self.channel is not None:
            self.channel.close()
            self.channel = None
        if self.process is not None:
            if self.process.is_alive():
                self.process.terminate()
            self.process.join(timeout=0.1)
            if self.process.is_alive():
                self.process.kill()
                self.process.join(timeout=0.1)
            self.process = None
        self.running = False
        self.communities = ()
        self.community_set.clear()

    def query(self):
        origin, destination = self.origin.value.lower(), self.destination.value.lower()
        optional = self.algorithm in ("bfs", "dfs")
        self.result = None
        if origin not in self.community_set or (destination not in self.community_set and not (optional and not destination)):
            self.live_error = "Selecione comunidades do dataset nos campos da consulta."
            return
        self.live_error = None
        try:
            self.channel.send((self.algorithm, origin, destination))
            self.running = True
        except (OSError, EOFError):
            self.stop()
            self.live_error = "A consulta foi interrompida."


    def choose(self, mode=None, algorithm=None):
        if self.running and (mode is not None or algorithm is not None):
            self.stop()
        self.result = None
        self.live_error = None
        if mode is not None:
            self.mode = mode
        if algorithm is not None:
            self.algorithm = algorithm
        self.case_index = 0
        self.scroll = 0
        self.max_scroll = 0

    def draw(self, surf, ui):
        surf.fill(T.BG)
        width, height = surf.get_size()
        pygame.draw.rect(surf, T.PANEL, (0, 0, width, px(54)))
        if ui.button(surf, "reddit-back", pygame.Rect(px(16), px(12), px(78), px(34)), "Menu"):
            self.app.open_menu()
        title = "Parte 2"
        text(surf, title, Fonts.get(21, bold=True), T.TEXT, (px(110), px(19)))
        tab_w = min(px(145), max(1, (width - px(205)) // 4))
        for index, (key, label) in enumerate(ALGORITHMS.items()):
            tab = pygame.Rect(px(192) + index * tab_w, px(12), max(1, tab_w - px(6)), px(32))
            if ui.button(surf, ("reddit-tab", key), tab, label, active=self.algorithm == key):
                self.choose(algorithm=key)
        for index, (key, label) in enumerate(self.modes()):
            button = pygame.Rect(px(16) + index * px(150), px(66), px(142), px(32))
            if ui.button(surf, ("reddit-mode", key), button, label, active=self.mode == key):
                self.choose(mode=key)
        box = pygame.Rect(px(16), px(110), width - px(32), height - px(122))
        if ui.hover(box) and ui.wheel:
            self.scroll = min(self.max_scroll, max(0, self.scroll - ui.wheel * px(45)))
        surf.set_clip(box)
        ui.clip = box
        y = box.y + px(6) - self.scroll
        end = self.draw_content(surf, ui, box, y)
        self.max_scroll = max(0, end - y - box.h + px(16))
        self.scroll = min(self.scroll, self.max_scroll)
        surf.set_clip(None)
        ui.clip = None

    def modes(self):
        return (("saved", "Casos salvos"), ("figures", "Figuras e notas"), ("live", "Consulta ao vivo"))

    def draw_content(self, surf, ui, box, y):
        if self.mode == "figures":
            return self.draw_figure(surf, ui, box, y)
        if self.mode == "live":
            return self.draw_live(surf, ui, box, y)
        return self.draw_saved(surf, ui, box, y)

    def draw_live(self, surf, ui, box, y):
        if not DATASET.is_file():
            y = self.paragraph(surf, box, y, "Dataset local indisponível.", T.WARN)
            return self.paragraph(surf, box, y, "Execute python scripts/download_reddit_dataset.py")
        if self.running:
            message = "Executando consulta…" if self.communities else "Carregando o dataset…"
            y = self.paragraph(surf, box, y, message)
            if ui.button(surf, "cancel-query", pygame.Rect(box.x, y, px(120), px(34)), "Cancelar"):
                self.stop()
            return y + px(44)
        if self.live_error:
            y = self.paragraph(surf, box, y, self.live_error, T.ERR)
        if not self.communities:
            if ui.button(surf, "load-live", pygame.Rect(box.x, y, px(165), px(34)), "Carregar dataset"):
                self.start()
            return y + px(44)

        optional = self.algorithm in ("bfs", "dfs")
        self.destination.placeholder = "Destino opcional" if optional else "Destino"
        if self.algorithm == "dijkstra":
            y = self.paragraph(surf, box, y, "Grafo com pesos transformados")
        elif self.algorithm == "bellman_ford":
            y = self.paragraph(surf, box, y, "Grafo com pesos originais agregados")
        field_width = (box.w - px(16)) // 2
        for index, (key, field) in enumerate((("origin", self.origin), ("destination", self.destination))):
            rect = pygame.Rect(box.x + index * (field_width + px(16)), y, field_width, px(35))
            was_focused = field.focused
            field.draw(ui, surf, rect)
            suggestion_area = pygame.Rect(rect.x, rect.bottom, rect.w, px(120))
            if was_focused and ui.hover(suggestion_area):
                field.focused = True
            if not field.value or field.value.lower() in self.community_set:
                continue
            if field.focused:
                from bisect import bisect_left
                prefix = field.value.lower()
                start = bisect_left(self.communities, prefix)
                for row, name in enumerate(self.communities[start:start + 4]):
                    if not name.startswith(prefix):
                        break
                    option = pygame.Rect(rect.x, rect.bottom + px(4 + row * 29), rect.w, px(27))
                    if ui.hover(option) and ui.pressed:
                        ui.active = ("community", key, name)
                    if ui.button(surf, ("community", key, name), option, name, align="left", size=13):
                        field.value = name
                        field.focused = False
        y += px(160)
        if ui.button(surf, "run-live", pygame.Rect(box.x, y, px(120), px(34)), "Executar", style="accent"):
            self.query()
        y += px(45)
        if self.result:
            y = self.draw_values(surf, box, y, self.result)
        return y

    def paragraph(self, surf, box, y, value, color=T.TEXT):
        font = Fonts.get(15)
        for line in wrap(str(value), font, box.w - px(14)):
            text(surf, line, font, color, (box.x + px(5), y))
            y += font.get_linesize() + px(4)
        return y + px(6)

    def draw_values(self, surf, box, y, data):
        for key, value in data.items():
            if value is None:
                value = "—"
            elif isinstance(value, list):
                value = " → ".join(map(str, value))
            elif isinstance(value, dict):
                value = " · ".join(f"{name} {number}" for name, number in value.items())
            elif isinstance(value, bool):
                value = "Sim" if value else "Não"
            y = self.paragraph(surf, box, y, f"{LABELS.get(key, key)} · {value}")
        return y

    def draw_saved(self, surf, ui, box, y):
        if self.report_error:
            return self.paragraph(surf, box, y, "Relatório indisponível · " + self.report_error, T.ERR)
        section = self.report["mandatory_cases"][self.algorithm]
        cases = []
        if self.algorithm == "bellman_ford":
            for key, item in section.items():
                label = " → ".join(item["pair"])
                name = "Com ciclo negativo" if key == "negative_cycle" else "Sem ciclo negativo"
                cases.append((f"{name} · {label}", "->".join(item["pair"]), item["result"]))
        else:
            for key, item in section["results"].items():
                cases.append((key.replace("->", " → "), key, item))
        selected, y = self.selector(surf, ui, box, y, "case", [c[0] for c in cases], self.case_index)
        self.case_index = selected
        _, metric_key, values = cases[selected]
        y = self.draw_values(surf, box, y, values)
        y = self.paragraph(surf, box, y + px(8), "Métricas do benchmark", T.ACCENT)
        for snapshot in self.report["scalability"]:
            metrics = snapshot[self.algorithm].get(metric_key)
            mean = f"{metrics['mean_seconds'] * 1000:.3f} ms · {len(metrics['runs_seconds'])} execuções" if metrics else "—"
            line = f"{snapshot['fraction']:.0%} · {snapshot['vertices']} vértices · {snapshot['edges']} arestas · {mean}"
            y = self.paragraph(surf, box, y, line)
        return y

    def selector(self, surf, ui, box, y, key, labels, selected):
        for delta, label, x in ((-1, "‹", box.x), (1, "›", box.right - px(38))):
            rect = pygame.Rect(x, y, px(38), px(36))
            if ui.button(surf, (key, delta), rect, label, enabled=len(labels) > 1):
                selected = (selected + delta) % len(labels)
        font = Fonts.get(16, bold=True)
        text(surf, text_fit(labels[selected], font, box.w - px(96)), font, T.TEXT,
             (box.centerx, y + px(18)), "center")
        return selected, y + px(54)

    def draw_figure(self, surf, ui, box, y):
        files = list(FIGURES)
        self.fig_index, y = self.selector(surf, ui, box, y, "figure",
                                          [item[0] for item in FIGURES.values()], self.fig_index)
        name = files[self.fig_index]
        try:
            if name not in self.images:
                self.images[name] = pygame.image.load(OUT / (name + ".png")).convert()
            image = self.images[name]
            width = min(box.w, image.get_width())
            height = image.get_height() * width // image.get_width()
            surf.blit(pygame.transform.smoothscale(image, (width, height)), (box.centerx - width // 2, y))
            y += height + px(16)
            note = FIGURES[name][1]
            if note:
                content = (ROOT / "docs" / (note + ".md")).read_text(encoding="utf-8")
                for paragraph in content.splitlines():
                    if paragraph.strip():
                        y = self.paragraph(surf, box, y, paragraph.replace("**", "").lstrip("# "))
        except (OSError, pygame.error) as error:
            y = self.paragraph(surf, box, y, str(error), T.ERR)
        return y
