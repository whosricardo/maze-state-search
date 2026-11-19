# [IA] Claude Code (Opus 5.5) – interface pygame: tela principal (labirinto interativo)
import math
from collections import Counter

import pygame

from src.frontend import theme as T
from src.frontend.theme import Fonts, px, SYMBOL_INFO
from src.frontend.widgets import rrect, text, text_fit, wrap, draw_icon
from src.frontend.board import Board
from src.frontend.model import (
    ALGORITHMS,
    MODELS,
    STATUS_COLORS,
    OUT_DIR,
    MapSession,
    MapError,
    discover_maps,
    layer_label,
)

STATUS_RGB = {"ok": T.OK, "err": T.ERR, "warn": T.WARN, "info": T.INFO}
EDGE_NAMES = [("TREE", "árvore"), ("BACK", "retorno"), ("FORWARD", "avanço"), ("CROSS", "cruzamento")]

SPEED_MIN, SPEED_MAX = 0.5, 240.0


def speed_to_t(speed):
    return math.log(speed / SPEED_MIN) / math.log(SPEED_MAX / SPEED_MIN)


def t_to_speed(t):
    return SPEED_MIN * (SPEED_MAX / SPEED_MIN) ** t


def fmt_num(value):
    if value is None or value == "":
        return "—"
    if isinstance(value, float):
        return f"{value:.4f}" if abs(value) < 1 else f"{value:.2f}"
    if isinstance(value, int) and abs(value) >= 10000:
        return f"{value:,}".replace(",", ".")
    return str(value)


# ---------------------------------------------------------------- player
class Player:
    def __init__(self):
        self.pos = 0.0
        self.length = 0
        self.playing = False
        self.loop = False
        self.laps = 0

    @property
    def last(self):
        return max(0, self.length - 1)

    def reset(self, length, loop=False, autoplay=True):
        self.pos = 0.0
        self.length = length
        self.loop = loop
        self.laps = 0
        self.playing = autoplay and length > 1

    def update(self, dt, speed):
        if not self.playing or self.length <= 1:
            return
        self.pos += speed * dt
        if self.pos >= self.last:
            if self.loop:
                while self.pos >= self.last:
                    self.pos -= self.last
                    self.laps += 1
            else:
                self.pos = float(self.last)
                self.playing = False

    def toggle(self):
        if self.length <= 1:
            return
        if not self.playing and not self.loop and self.pos >= self.last:
            self.pos = 0.0
        self.playing = not self.playing

    def step(self, delta):
        self.playing = False
        target = int(round(self.pos)) + delta
        if self.loop and self.last > 0:
            while target > self.last:
                target -= self.last
                self.laps += 1
            while target < 0:
                if self.laps > 0:
                    target += self.last
                    self.laps -= 1
                else:
                    target = 0
        self.pos = float(max(0, min(self.last, target)))

    def seek(self, index):
        self.playing = False
        self.pos = float(max(0, min(self.last, index)))


# ---------------------------------------------------------------- tela
class Viewer:
    def __init__(self, app, initial=None):
        self.app = app
        self.entries = discover_maps(app.extra_maps)
        self.session = None
        self.boards = []
        self.index = -1
        self.algo = "Dijkstra"
        self.algo_b = "BFS"
        self.model = "estados"
        self.compare = False
        self.explore_mode = False
        self.show_heat = False
        self.show_traps = False
        self.layer = None
        self.player = Player()
        self.speeds = {"path": 5.0, "explore": 45.0}
        self.show_help = False
        self.list_scroll = 0
        self.panel_scroll = 0
        self.panel_content_h = 0

        if initial is not None:
            self.load_path(initial)
        if self.session is None and self.entries:
            names = [p.stem for p, _ in self.entries]
            start = names.index("m03_tres_chaves") if "m03_tres_chaves" in names else 0
            for i in [start] + list(range(len(self.entries))):
                if self.load_index(i, quiet=True):
                    break

    # -------------------------------------------------------------- dados
    def refresh_maps(self):
        current = self.entries[self.index][0] if 0 <= self.index < len(self.entries) else None
        self.entries = discover_maps(self.app.extra_maps)
        if current is not None:
            for i, (path, _) in enumerate(self.entries):
                if path.resolve() == current.resolve():
                    self.index = i

    def load_path(self, path):
        from pathlib import Path
        path = Path(path)
        self.refresh_maps()
        for i, (p, _) in enumerate(self.entries):
            if p.resolve() == path.resolve():
                return self.load_index(i)
        self.app.extra_maps.append(path)
        self.refresh_maps()
        for i, (p, _) in enumerate(self.entries):
            if p.resolve() == path.resolve():
                return self.load_index(i)
        return False

    def load_index(self, index, quiet=False):
        if not (0 <= index < len(self.entries)):
            return False
        path, _ = self.entries[index]
        try:
            session = MapSession(path)
        except MapError as error:
            self.app.toast(str(error), "err")
            return False
        except Exception as error:  # mapa inesperado não pode derrubar a interface
            self.app.toast(f"Erro ao abrir {path.name}: {error}", "err")
            return False
        self.session = session
        self.index = index
        self.boards = [Board(session.grid), Board(session.grid)]
        self.layer = None
        self.panel_scroll = 0
        self.restart()
        if not quiet:
            self.app.toast(
                f"{session.name}: {session.n_states} estados alcançáveis "
                f"({session.build_ms:.1f} ms para construir o G_est)", "info")
        return True

    def runs(self):
        if self.session is None:
            return []
        runs = [self.session.run(self.algo, self.model)]
        if self.compare:
            runs.append(self.session.run(self.algo_b, self.model))
        return runs

    def restart(self, autoplay=True):
        runs = self.runs()
        if not runs:
            self.player.reset(0)
            return
        if self.explore_mode:
            length = max(len(r.explore) for r in runs)
            loop = False
        else:
            length = max(len(r.frames) for r in runs)
            loop = runs[0].loop and not self.compare
        self.player.reset(length, loop, autoplay)

    @property
    def speed(self):
        return self.speeds["explore" if self.explore_mode else "path"]

    @speed.setter
    def speed(self, value):
        self.speeds["explore" if self.explore_mode else "path"] = max(SPEED_MIN, min(SPEED_MAX, value))

    # -------------------------------------------------------------- ações
    def set_algo(self, name, secondary=False):
        if secondary:
            self.algo_b = name
        else:
            self.algo = name
        self.restart()

    def set_model(self, model):
        self.model = model
        self.restart()

    def toggle(self, what):
        if what == "explore":
            self.explore_mode = not self.explore_mode
            self.restart()
        elif what == "heat":
            self.show_heat = not self.show_heat
        elif what == "traps":
            self.show_traps = not self.show_traps
        elif what == "compare":
            self.compare = not self.compare
            self.restart()

    def cycle_layer(self, delta):
        if self.session is None:
            return
        options = [None] + self.session.layer_names
        i = options.index(self.layer) if self.layer in options else 0
        self.layer = options[(i + delta) % len(options)]
        self.show_heat = True
        if self.model != "estados":
            self.set_model("estados")

    def cycle_map(self, delta):
        if not self.entries:
            return
        n = len(self.entries)
        for k in range(1, n + 1):
            if self.load_index((self.index + delta * k) % n):
                return

    def export_png(self):
        if self.session is None:
            return
        s = self.session
        run = self.runs()[0]
        if not run.frames:
            self.app.toast("Nada para exportar: este algoritmo não produziu caminho neste mapa.", "warn")
            return
        cell = max(10, min(40, 1600 // s.cols))
        title_h, legend_h, pad = 64, 52, 20
        width = s.cols * cell + pad * 2
        height = s.rows * cell + title_h + legend_h + pad
        img = pygame.Surface((width, height))
        img.fill((255, 255, 255))
        board = Board(s.grid)
        board.fit(pygame.Rect(pad, title_h, s.cols * cell, s.rows * cell), max_cell=cell)
        last = run.frames[-1]
        trail = self.trail(board, run.frames, len(run.frames) - 1, 0)
        invalid = [f.pos for f in run.frames if f.invalid]
        board.draw(img, opened=s.doors_open(run.model, last.keys), consumed=last.bonus,
                   trail=trail, agent=(trail[-1][0], s.color_of_keys(last.keys)),
                   invalid=invalid or None, numbers=False)
        title = f"{s.name} · {run.algorithm} · {MODELS[run.model]}"
        sub = f"status: {run.status} · custo {fmt_num(run.path_cost)} · {run.moves} movimentos"
        if run.loop:
            sub = f"status: {run.status} · ciclo com custo {fmt_num(run.path_cost)} por volta"
        text(img, title, Fonts.raw(20, bold=True), (30, 30, 30), (pad, 12))
        text(img, sub, Fonts.raw(15), (90, 90, 90), (pad, 38))
        x = pad
        y = title_h + s.rows * cell + 16
        seen = []
        for f in run.frames:
            name = layer_label(f.keys)
            if name not in seen:
                seen.append(name)
        text(img, "camadas (chaves):", Fonts.raw(14), (90, 90, 90), (x, y + 2))
        x += 130
        for name in seen:
            pygame.draw.rect(img, s.color_of_keys(frozenset(name) if name != "-" else frozenset()),
                             (x, y + 3, 16, 16), border_radius=3)
            r = text(img, name, Fonts.raw(14, bold=True), (40, 40, 40), (x + 22, y + 2))
            x = r.right + 18
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        slug = run.algorithm.lower().replace("-", "_")
        suffix = "" if run.model == "estados" else f"_{run.model}"
        out = OUT_DIR / f"percurso_{s.name}_{slug}{suffix}.png"
        pygame.image.save(img, str(out))
        self.app.toast(f"PNG salvo em out/parte1/{out.name}", "ok")

    # -------------------------------------------------------------- eventos
    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return
        shift = bool(event.mod & pygame.KMOD_SHIFT)
        key = event.key
        if self.show_help:
            if key in (pygame.K_ESCAPE, pygame.K_F1) or event.unicode == "?":
                self.show_help = False
            return
        if key == pygame.K_SPACE:
            self.player.toggle()
        elif key == pygame.K_RIGHT:
            self.player.step(10 if shift else 1)
        elif key == pygame.K_LEFT:
            self.player.step(-10 if shift else -1)
        elif key == pygame.K_HOME:
            self.player.seek(0)
        elif key == pygame.K_END:
            self.player.seek(self.player.last)
        elif key == pygame.K_UP:
            self.speed = self.speed * 1.35
        elif key == pygame.K_DOWN:
            self.speed = self.speed / 1.35
        elif key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
            name = ALGORITHMS[key - pygame.K_1]
            if shift:
                if not self.compare:
                    self.toggle("compare")
                self.set_algo(name, secondary=True)
            else:
                self.set_algo(name)
        elif key == pygame.K_m:
            models = list(MODELS)
            self.set_model(models[(models.index(self.model) + (-1 if shift else 1)) % len(models)])
        elif key == pygame.K_x:
            self.toggle("explore")
        elif key == pygame.K_h:
            self.toggle("heat")
        elif key == pygame.K_t:
            self.toggle("traps")
        elif key == pygame.K_c:
            self.toggle("compare")
        elif key == pygame.K_l:
            self.cycle_layer(-1 if shift else 1)
        elif key in (pygame.K_TAB, pygame.K_PAGEDOWN):
            self.cycle_map(-1 if shift else 1)
        elif key == pygame.K_PAGEUP:
            self.cycle_map(-1)
        elif key == pygame.K_r:
            self.restart()
        elif key == pygame.K_p:
            self.export_png()
        elif key == pygame.K_e:
            self.app.open_editor()
        elif key == pygame.K_F1 or event.unicode == "?":
            self.show_help = True

    def update(self, dt):
        self.player.update(dt, self.speed)

    # -------------------------------------------------------------- estado visual
    def frame_at(self, run):
        frames = run.frames
        if not frames:
            return None, 0, 0.0, 0
        i = min(int(self.player.pos), len(frames) - 1)
        frac = self.player.pos - int(self.player.pos) if int(self.player.pos) < len(frames) - 1 else 0.0
        lap = self.player.laps if (run.loop and self.player.loop) else 0
        return frames[i], i, frac, lap

    def trail(self, board, frames, i, frac):
        """Pontos do percurso até o frame i. Cada camada (conjunto de chaves) é
        deslocada um pouco na diagonal, como linhas de metrô: assim, quando o
        caminho volta pelo mesmo corredor com outra chave, as duas passagens
        aparecem lado a lado em vez de uma cobrir a outra."""
        s = self.session
        order = []
        for f in frames:
            name = layer_label(f.keys)
            if name not in order:
                order.append(name)
        spacing = board.cell * 0.18 if len(order) > 1 else 0.0
        middle = (len(order) - 1) / 2

        def point(f):
            cx, cy = board.center(f.pos)
            o = (order.index(layer_label(f.keys)) - middle) * spacing
            return (cx + o, cy + o)

        pts = [(point(f), s.color_of_keys(f.keys)) for f in frames[:i + 1]]
        if frac > 0 and i + 1 < len(frames):
            a, b = point(frames[i]), point(frames[i + 1])
            e = frac * frac * (3 - 2 * frac)  # smoothstep
            pts.append(((a[0] + (b[0] - a[0]) * e, a[1] + (b[1] - a[1]) * e), s.color_of_keys(frames[i + 1].keys)))
        return pts

    def snapshot(self, board, run):
        s = self.session
        model = run.model
        d = {"opened": s.doors_open(model, frozenset()), "consumed": frozenset()}
        if self.explore_mode:
            n = min(len(run.explore), int(self.player.pos) + 1) if run.explore else 0
            if n:
                verts = run.explore[:n]
                last = verts[-1]
                d["explore"] = Counter(s.pos_of(v, model) for v in verts)
                d["explore_last"] = s.pos_of(last, model)
                d["opened"] = s.doors_open(model, s.keys_of(last, model))
                if n >= len(run.explore) and run.frames:
                    d["trail"] = self.trail(board, run.frames, len(run.frames) - 1, 0)
        else:
            frame, i, frac, _ = self.frame_at(run)
            if frame is not None:
                pts = self.trail(board, run.frames, i, frac)
                d["trail"] = pts
                d["agent"] = (pts[-1][0], s.color_of_keys(frame.keys))
                d["opened"] = s.doors_open(model, frame.keys)
                d["consumed"] = frame.bonus
                invalid = [f.pos for f in run.frames[:i + 1] if f.invalid]
                if invalid:
                    d["invalid"] = invalid
                if run.loop:
                    d["ghost"] = self.trail(board, run.frames, len(run.frames) - 1, 0)
        if model == "estados":
            if self.show_heat:
                d["heat"] = s.cell_counts.get(self.layer) or None
                d["marks"] = s.layer_change_cells
                if self.layer is not None:
                    d["opened"] = frozenset() if self.layer == "-" else frozenset(self.layer)
            if self.show_traps and s.trap_cells:
                d["traps"] = s.trap_cells
        return d

    # -------------------------------------------------------------- desenho
    def draw(self, surf, ui):
        W, H = surf.get_size()
        top = pygame.Rect(0, 0, W, px(58))
        side = pygame.Rect(0, top.bottom, px(256), H - top.bottom)
        right = pygame.Rect(W - px(344), top.bottom, px(344), H - top.bottom)
        bottom = pygame.Rect(side.right, H - px(96), right.x - side.right, px(96))
        center = pygame.Rect(side.right, top.bottom, right.x - side.right, bottom.y - top.bottom)

        surf.fill(T.BG)
        ui.blocked = self.show_help
        if self.session is not None:
            self.draw_center(surf, ui, center)
        else:
            text(surf, "Nenhum mapa válido encontrado em data/mapas/", Fonts.get(16), T.TEXT_DIM, center.center, "center")
        self.draw_top(surf, ui, top)
        self.draw_side(surf, ui, side)
        self.draw_right(surf, ui, right)
        self.draw_bottom(surf, ui, bottom)
        ui.blocked = False
        if self.show_help:
            self.draw_help(surf, ui)

    # ---------------------------------------------------------------- topo
    def draw_top(self, surf, ui, rect):
        pygame.draw.rect(surf, T.PANEL, rect)
        pygame.draw.line(surf, T.BORDER, rect.bottomleft, (rect.right, rect.bottom), 1)
        # "logo": três camadas empilhadas
        lx, ly = rect.x + px(20), rect.centery
        for k, col in enumerate((T.ACCENT, (255, 160, 90), (255, 214, 170))):
            r = pygame.Rect(0, 0, px(22), px(9))
            r.center = (lx + px(11), ly + px(7) - k * px(7))
            rrect(surf, col, r, 3)
        r = text(surf, "Labirinto de Estados", Fonts.get(18, bold=True), T.TEXT, (lx + px(34), ly), "midleft")
        r = text(surf, "Teoria dos Grafos · Parte 1", Fonts.get(13), T.TEXT_FAINT, (r.right + px(12), ly + px(1)), "midleft")

        if self.session is not None:
            s = self.session
            tag = self.entries[self.index][1] if 0 <= self.index < len(self.entries) else ""
            chip_text = f"{s.name}   {s.rows}×{s.cols}   {len(s.map_keys)} chave(s)"
            font = Fonts.get(13, bold=True)
            cw = font.size(chip_text)[0] + px(28)
            chip = pygame.Rect(0, 0, cw, px(30))
            chip.midleft = (r.right + px(28), ly)
            rrect(surf, T.PANEL_2, chip, 15)
            pygame.draw.circle(surf, T.ACCENT if tag == "fornecido" else T.OK, (chip.x + px(14), chip.centery), px(4))
            text(surf, chip_text, font, T.TEXT, (chip.x + px(24), chip.centery), "midleft")

        bx = rect.right - px(16)
        for label, action, style, tip in (
            ("?", "help", "default", "Atalhos de teclado (F1)"),
            ("Editor de mapas", "editor", "default", "Criar e testar mapas do grupo (E)"),
            ("Exportar PNG", "png", "accent", "Salva o percurso atual em out/parte1/ com cor por camada (P)"),
        ):
            w = px(36) if label == "?" else Fonts.get(13, bold=True).size(label)[0] + px(28)
            b = pygame.Rect(0, 0, w, px(34))
            b.midright = (bx, rect.centery)
            bx = b.x - px(8)
            if ui.button(surf, ("top", action), b, label, style=style, tooltip=tip, size=13, bold=True):
                if action == "help":
                    self.show_help = True
                elif action == "editor":
                    self.app.open_editor()
                else:
                    self.export_png()

    # ---------------------------------------------------------------- lateral
    def section(self, surf, x, y, title):
        text(surf, title.upper(), Fonts.get(11, bold=True), T.TEXT_FAINT, (x, y))
        return y + px(20)

    def toggle_row(self, surf, ui, wid, rect, label, hint, value, enabled=True, tooltip=None):
        hovered = enabled and ui.hover(rect)
        if hovered and ui.pressed:
            ui.active = wid
        clicked = hovered and ui.released and ui.active == wid
        if hovered:
            rrect(surf, T.PANEL_2, rect, 6)
        fg = T.TEXT if enabled else T.TEXT_FAINT
        font = Fonts.get(13)
        text(surf, text_fit(label, font, rect.w - px(80)), font, fg, (rect.x + px(8), rect.centery), "midleft")
        if hint:
            text(surf, hint, Fonts.get(11), T.TEXT_FAINT, (rect.right - px(52), rect.centery), "midright")
        pill = pygame.Rect(0, 0, px(34), px(18))
        pill.midright = (rect.right - px(8), rect.centery)
        on = value and enabled
        rrect(surf, T.ACCENT if on else T.PANEL_3, pill, 9)
        kx = pill.right - px(9) if on else pill.x + px(9)
        pygame.draw.circle(surf, (255, 255, 255) if enabled else T.TEXT_FAINT, (kx, pill.centery), px(6))
        if hovered and tooltip:
            ui.tooltip = tooltip
        return clicked

    def draw_side(self, surf, ui, rect):
        pygame.draw.rect(surf, T.PANEL, rect)
        pygame.draw.line(surf, T.BORDER, rect.topright, rect.bottomright, 1)
        x, w = rect.x + px(14), rect.w - px(28)
        y = rect.y + px(14)

        # ---- mapas
        y = self.section(surf, x, y, f"Mapas ({len(self.entries)})")
        item_h = px(30)
        total = len(self.entries) * item_h
        area_h = min(total, max(px(120), int(surf.get_height() * 0.30)))
        area = pygame.Rect(x - px(4), y, w + px(8), area_h)
        max_scroll = max(0, total - area_h)
        if ui.hover(area) and ui.wheel:
            self.list_scroll -= ui.wheel * item_h
        self.list_scroll = max(0, min(max_scroll, self.list_scroll))
        surf.set_clip(area)
        ui.clip = area
        for i, (path, tag) in enumerate(self.entries):
            r = pygame.Rect(area.x, area.y + i * item_h - self.list_scroll, area.w, item_h - px(3))
            if r.bottom < area.y or r.y > area.bottom:
                continue
            hint = None if tag == "fornecido" else tag
            if ui.button(surf, ("map", i), r, path.stem, active=i == self.index, style="ghost",
                         align="left", hint=hint, size=13, tooltip=str(path)):
                self.load_index(i)
        surf.set_clip(None)
        ui.clip = None
        if max_scroll:
            bar_h = max(px(20), int(area_h * area_h / total))
            bar_y = area.y + int((area_h - bar_h) * self.list_scroll / max_scroll)
            rrect(surf, T.PANEL_3, pygame.Rect(area.right - px(3), bar_y, px(3), bar_h), 2)
        y = area.bottom + px(16)

        # ---- algoritmo
        y = self.section(surf, x, y, "Algoritmo")
        bw, bh, gap = (w - px(8)) // 2, px(34), px(8)
        for k, name in enumerate(ALGORITHMS):
            r = pygame.Rect(x + (k % 2) * (bw + gap), y + (k // 2) * (bh + gap), bw, bh)
            if ui.button(surf, ("algo", k), r, name, active=self.algo == name, align="left", hint=str(k + 1), size=13):
                self.set_algo(name)
        y += 2 * (bh + gap) + px(8)

        if self.compare:
            y = self.section(surf, x, y, "Comparar com")
            bh2 = px(28)
            for k, name in enumerate(ALGORITHMS):
                r = pygame.Rect(x + (k % 2) * (bw + gap), y + (k // 2) * (bh2 + px(6)), bw, bh2)
                if ui.button(surf, ("algob", k), r, name, active=self.algo_b == name, align="left",
                             tooltip=f"Shift+{k + 1}", size=12):
                    self.set_algo(name, secondary=True)
            y += 2 * (bh2 + px(6)) + px(8)

        # ---- modelo
        y = self.section(surf, x, y, "Modelo do grafo")
        tips = {
            "estados": "Nó = (posição, chaves, bônus). É onde os algoritmos devem rodar.",
            "chao": "Modelo ingênuo: porta tratada como chão. Pode atravessar porta trancada (INVÁLIDO).",
            "parede": "Modelo ingênuo: porta tratada como parede. Pode não chegar à saída (FALHA).",
        }
        for key, label in MODELS.items():
            r = pygame.Rect(x, y, w, px(30))
            if ui.button(surf, ("model", key), r, label, active=self.model == key, style="ghost",
                         align="left", size=13, tooltip=tips[key],
                         hint="M" if key == self.model else None):
                self.set_model(key)
            y += px(33)
        y += px(10)

        # ---- visualização
        y = self.section(surf, x, y, "Visualização")
        is_est = self.model == "estados"
        rows = [
            ("explore", "Exploração passo a passo", "X", self.explore_mode, True,
             "Anima a ordem em que o algoritmo descobre os estados."),
            ("heat", "Mapa de calor (estados/casa)", "H", self.show_heat, is_est,
             "Multiplicidade: quantos estados do G_est existem em cada casa."),
            ("traps", "Estados-armadilha", "T", self.show_traps, is_est,
             "Estados alcançáveis a partir do início que não chegam ao ALVO (busca no transposto)."),
            ("compare", "Comparar lado a lado", "C", self.compare, True,
             "Mostra dois algoritmos ao mesmo tempo na mesma linha do tempo."),
        ]
        for key, label, hint, value, enabled, tip in rows:
            r = pygame.Rect(x - px(4), y, w + px(8), px(32))
            if self.toggle_row(surf, ui, ("tog", key), r, label, hint, value, enabled,
                               tip if enabled else "Disponível apenas no grafo de estados."):
                self.toggle(key)
            y += px(34)

        if self.show_heat and is_est and self.session is not None:
            y += px(4)
            r_prev = pygame.Rect(x, y, px(30), px(30))
            r_next = pygame.Rect(x + w - px(30), y, px(30), px(30))
            if ui.button(surf, "layer_prev", r_prev, icon="left", tooltip="Camada anterior (Shift+L)"):
                self.cycle_layer(-1)
            if ui.button(surf, "layer_next", r_next, icon="right", tooltip="Próxima camada (L)"):
                self.cycle_layer(1)
            label = "todas as camadas" if self.layer is None else f"camada  {self.layer}"
            mid = pygame.Rect(r_prev.right + px(6), y, r_next.x - r_prev.right - px(12), px(30))
            rrect(surf, T.PANEL_2, mid, 6)
            if self.layer is not None:
                pygame.draw.circle(surf, self.session.layer_color.get(self.layer, T.ACCENT),
                                   (mid.x + px(14), mid.centery), px(5))
            text(surf, label, Fonts.get(13, bold=True), T.TEXT, mid.center, "center")

    # ---------------------------------------------------------------- centro
    def draw_center(self, surf, ui, rect):
        runs = self.runs()
        s = self.session
        if len(runs) == 2:
            half_w, half_h = rect.w // 2, rect.h // 2
            horiz = [pygame.Rect(rect.x, rect.y, half_w, rect.h),
                     pygame.Rect(rect.x + half_w, rect.y, rect.w - half_w, rect.h)]
            vert = [pygame.Rect(rect.x, rect.y, rect.w, half_h),
                    pygame.Rect(rect.x, rect.y + half_h, rect.w, rect.h - half_h)]

            def cell_for(r):
                return min((r.w - px(32)) // s.cols, (r.h - px(70)) // s.rows)

            areas = horiz if cell_for(horiz[0]) >= cell_for(vert[0]) else vert
        else:
            areas = [rect]
        for board, run, area in zip(self.boards, runs, areas):
            self.draw_board(surf, ui, board, run, area)

    def status_chip(self, surf, x, cy, status):
        color = STATUS_RGB.get(STATUS_COLORS.get(status, "info"), T.INFO)
        font = Fonts.get(12, bold=True)
        w = font.size(status)[0] + px(18)
        chip = pygame.Rect(x, 0, w, px(22))
        chip.centery = cy
        rrect(surf, T.lerp_color(T.PANEL, color, 0.22), chip, 11)
        text(surf, status, font, color, chip.center, "center")
        return chip

    def draw_board(self, surf, ui, board, run, area):
        s = self.session
        header = pygame.Rect(area.x + px(18), area.y + px(12), area.w - px(36), px(28))
        inner = pygame.Rect(area.x + px(18), header.bottom + px(10), area.w - px(36),
                            area.bottom - header.bottom - px(22))
        board.fit(inner)
        frame_rect = board.rect.inflate(px(10), px(10))
        rrect(surf, (8, 8, 10), frame_rect.move(0, px(4)), 8)
        rrect(surf, (14, 14, 17), frame_rect, 8)
        rrect(surf, T.BORDER, frame_rect, 8, 1)
        board.draw(surf, **self.snapshot(board, run))

        # cabeçalho
        r = text(surf, run.algorithm, Fonts.get(16, bold=True), T.TEXT, (header.x, header.centery), "midleft")
        r = text(surf, MODELS[run.model], Fonts.get(13), T.TEXT_DIM, (r.right + px(10), header.centery), "midleft")
        chip = self.status_chip(surf, r.right + px(12), header.centery, run.status)
        parts = []
        if run.loop:
            parts.append(f"volta {self.player.laps + 1}")
            parts.append(f"{fmt_num(run.path_cost)}/volta")
        elif run.frames:
            parts.append(f"custo {fmt_num(run.path_cost)}")
            parts.append(f"{run.moves} mov.")
        parts.append(f"{run.elapsed_ms:.2f} ms")
        summary = "  ·  ".join(parts)
        font = Fonts.get(13)
        if font.size(summary)[0] < header.right - chip.right - px(16):
            text(surf, summary, font, T.TEXT_DIM, (header.right, header.centery), "midright")

        # aviso quando não há o que animar
        empty = (not run.explore) if self.explore_mode else (not run.frames)
        if (empty or (not self.explore_mode and run.status in ("Recusado", "Sem Caminho"))) and run.message:
            msg_font = Fonts.get(14)
            lines = wrap(run.message, msg_font, min(px(420), board.rect.w - px(20)))
            bw = max(msg_font.size(line)[0] for line in lines) + px(40)
            bh = len(lines) * msg_font.get_linesize() + px(52)
            box = pygame.Rect(0, 0, bw, bh)
            box.center = board.rect.center
            shade = pygame.Surface(box.size, pygame.SRCALPHA)
            pygame.draw.rect(shade, (18, 18, 22, 235), shade.get_rect(), border_radius=px(10))
            surf.blit(shade, box)
            color = STATUS_RGB.get(STATUS_COLORS.get(run.status, "info"), T.INFO)
            rrect(surf, color, box, 10, 2)
            text(surf, run.status.upper(), Fonts.get(13, bold=True), color, (box.centerx, box.y + px(20)), "center")
            for k, line in enumerate(lines):
                text(surf, line, msg_font, T.TEXT, (box.centerx, box.y + px(38) + k * msg_font.get_linesize()), "midtop")

        # tooltip da casa sob o mouse
        pos = board.pos_at(ui.mouse)
        if pos is not None and ui.tooltip is None and not self.show_help:
            symbol = s.symbol_at(pos)
            name, cost = SYMBOL_INFO.get(symbol, (symbol, "?"))
            tip = f"({pos[0]},{pos[1]})  {name} · custo {cost}"
            if symbol != '#':
                tip += f"\n{s.cell_counts[None].get(pos, 0)} estado(s) nesta casa"
                if s.trap_cells.get(pos):
                    tip += f" · {s.trap_cells[pos]} armadilha(s)"
                if pos in s.layer_change_cells:
                    tip += "\nmuda de camada ao entrar aqui"
            ui.tooltip = tip

    # ---------------------------------------------------------------- painel direito
    def kv(self, surf, x, y, w, label, value, color=T.TEXT, mono=False):
        font_l = Fonts.get(13)
        text(surf, label, font_l, T.TEXT_DIM, (x, y))
        font_v = Fonts.get(13, bold=True, mono=mono)
        text(surf, text_fit(value, font_v, int(w * 0.6)), font_v, color, (x + w, y), "topright")
        return y + px(22)

    def key_chips(self, surf, x, y, held, color):
        s = self.session
        if not s.map_keys:
            text(surf, "mapa sem chaves", Fonts.get(13), T.TEXT_FAINT, (x, y + px(2)))
            return
        for k in s.map_keys:
            r = pygame.Rect(x, y, px(26), px(24))
            if k in held:
                rrect(surf, T.TILE['key'], r, 6)
                text(surf, k, Fonts.get(14, bold=True), (120, 84, 0), r.center, "center")
            else:
                rrect(surf, T.BORDER, r, 6, 1)
                text(surf, k, Fonts.get(14), T.TEXT_FAINT, r.center, "center")
            x += px(31)

    def panel_state(self, surf, x, y, w, run, compact=False):
        s = self.session
        y = self.section(surf, x, y, f"Estado atual · {run.algorithm}")
        frame, i, _, lap = self.frame_at(run)
        if frame is None:
            for line in wrap(run.message or "Sem caminho para animar.", Fonts.get(13), w):
                text(surf, line, Fonts.get(13), T.TEXT_DIM, (x, y))
                y += px(19)
            return y + px(12)

        lap_cost = run.frames[-1].cost if run.loop else 0
        cost = frame.cost + lap * lap_cost
        color = s.color_of_keys(frame.keys)
        big = Fonts.get(30 if not compact else 22, bold=True)
        r = text(surf, fmt_num(cost), big, T.ACCENT if cost >= 0 else T.WARN, (x, y))
        text(surf, "custo acumulado", Fonts.get(12), T.TEXT_FAINT, (x, r.bottom))
        total = len(run.frames) - 1
        step_txt = f"{i} / {total}"
        r2 = text(surf, step_txt, Fonts.get(20 if not compact else 16, bold=True), T.TEXT, (x + w, y + px(4)), "topright")
        text(surf, "volta " + str(lap + 1) if run.loop else "passo", Fonts.get(12), T.TEXT_FAINT, (x + w, r.bottom), "topright")
        y = r.bottom + px(24)

        if not compact:
            symbol = s.symbol_at(frame.pos)
            name, c = SYMBOL_INFO.get(symbol, (symbol, "?"))
            y = self.kv(surf, x, y, w, "Posição (linha, coluna)", f"({frame.pos[0]}, {frame.pos[1]})")
            y = self.kv(surf, x, y, w, "Casa", f"{name} · custo {c}")
            if run.model == "estados":
                ids = sorted(s.bonus_ids[p] for p in frame.bonus)
                bonus = "{" + ",".join(map(str, ids)) + "}" if ids else "nenhum"
            else:
                bonus = "ignorado (modelo ingênuo)"
            y = self.kv(surf, x, y, w, "Bônus consumidos", bonus)
        text(surf, "Chaves", Fonts.get(13), T.TEXT_DIM, (x, y + px(4)))
        self.key_chips(surf, x + px(70), y, frame.keys, color)
        y += px(32)

        # rótulo obrigatório do estado
        box = pygame.Rect(x, y, w, px(30))
        rrect(surf, T.PANEL_2, box, 6)
        pygame.draw.rect(surf, color, (box.x, box.y, px(4), box.h), border_top_left_radius=px(6), border_bottom_left_radius=px(6))
        mono = Fonts.get(14, bold=True, mono=True)
        text(surf, text_fit(frame.label, mono, w - px(24)), mono, T.TEXT, (box.x + px(14), box.centery), "midleft")
        y = box.bottom + px(6)
        if frame.invalid:
            text(surf, "porta atravessada sem a chave!", Fonts.get(12, bold=True), T.ERR, (x, y))
            y += px(18)
        return y + px(14)

    def panel_explore(self, surf, x, y, w, runs):
        s = self.session
        y = self.section(surf, x, y, "Exploração")
        for run in runs:
            total = len(run.explore)
            n = min(total, int(self.player.pos) + 1) if total else 0
            text(surf, run.algorithm, Fonts.get(14, bold=True), T.TEXT, (x, y))
            text(surf, f"{n} / {total} vértices", Fonts.get(13), T.TEXT_DIM, (x + w, y), "topright")
            y += px(22)
            bar = pygame.Rect(x, y, w, px(8))
            rrect(surf, T.PANEL_3, bar, 4)
            if total:
                fill = bar.copy()
                fill.w = max(px(4), int(bar.w * n / total))
                rrect(surf, T.ACCENT, fill, 4)
            y += px(16)
            if n:
                last = run.explore[n - 1]
                label = s._frames([last], run.model)[0].label if last is not None else ""
                mono = Fonts.get(13, mono=True)
                text(surf, text_fit("último: " + label, mono, w), mono, T.TEXT_DIM, (x, y))
                y += px(22)
        note = ("Cor mais forte = mais estados daquela casa já descobertos "
                "(a mesma casa aparece em várias camadas). O contorno branco é o último descoberto.")
        for line in wrap(note, Fonts.get(12), w):
            text(surf, line, Fonts.get(12), T.TEXT_FAINT, (x, y))
            y += px(17)
        return y + px(14)

    def panel_result(self, surf, x, y, w, runs):
        s = self.session
        y = self.section(surf, x, y, "Todos os algoritmos · " + MODELS[self.model])
        cols = [x, x + int(w * 0.36), x + int(w * 0.70), x + w]
        font = Fonts.get(12)
        text(surf, "algoritmo", font, T.TEXT_FAINT, (cols[0], y))
        text(surf, "status", font, T.TEXT_FAINT, (cols[1], y))
        text(surf, "mov.", font, T.TEXT_FAINT, (cols[2], y))
        text(surf, "custo", font, T.TEXT_FAINT, (cols[3], y), "topright")
        y += px(20)
        for name in ALGORITHMS[:3]:
            run = s.run(name, self.model)
            sel = name in [r.algorithm for r in runs]
            if sel:
                rrect(surf, T.PANEL_2, pygame.Rect(x - px(6), y - px(3), w + px(12), px(24)), 5)
            color = STATUS_RGB.get(STATUS_COLORS.get(run.status, "info"), T.INFO)
            text(surf, name, Fonts.get(13, bold=sel), T.TEXT, (cols[0], y))
            text(surf, text_fit(run.status, Fonts.get(12, bold=True), cols[2] - cols[1] - px(4)),
                 Fonts.get(12, bold=True), color, (cols[1], y + px(1)))
            moves = run.moves if (run.frames and not run.loop) else "—"
            cost = "−∞" if run.loop else fmt_num(run.path_cost if run.frames else None)
            text(surf, str(moves), Fonts.get(13), T.TEXT, (cols[2], y))
            text(surf, cost, Fonts.get(13, bold=True), T.TEXT, (cols[3], y), "topright")
            y += px(26)
        y += px(6)

        for run in runs:
            if run.algorithm == "DFS":
                y = self.section(surf, x, y, "DFS · classificação dos arcos")
                for code, label in EDGE_NAMES:
                    y = self.kv(surf, x, y, w, f"arcos de {label}", fmt_num(run.dfs_counts.get(code, 0)))
                y = self.kv(surf, x, y, w, "tem ciclo (arco de retorno)?", "sim" if run.has_cycle else "não",
                            T.WARN if run.has_cycle else T.OK)
                y += px(6)
            if run.message and run.frames:
                color = T.WARN if run.status in ("Ciclo Negativo", "Recusado") else (
                    T.ERR if run.status == "Caminho Inválido" else T.TEXT_DIM)
                for line in wrap(f"{run.algorithm}: {run.message}", Fonts.get(12), w):
                    text(surf, line, Fonts.get(12), color, (x, y))
                    y += px(17)
                y += px(8)
            elif run.message and run.status == "Recusado":
                for line in wrap(f"{run.algorithm} recusou: {run.message}", Fonts.get(12), w):
                    text(surf, line, Fonts.get(12), T.WARN, (x, y))
                    y += px(17)
                y += px(8)
        return y + px(8)

    def panel_metrics(self, surf, x, y, w):
        s = self.session
        m = s.metrics
        y = self.section(surf, x, y, "Métricas do mapa")
        y = self.kv(surf, x, y, w, "Casas livres · chaves · bônus", f"{m['free']} · {m['n_keys']} · {m['n_bonus']}")
        y = self.kv(surf, x, y, w, "G_pos  |V| · |E|", f"{m['gpos'][0]} · {m['gpos'][1]}")
        y = self.kv(surf, x, y, w, "G_pos  densidade", f"{m['gpos'][2]:.5f}")
        y = self.kv(surf, x, y, w, "G_est  |V| · |E|", f"{fmt_num(m['gest'][0])} · {fmt_num(m['gest'][1])}")
        y = self.kv(surf, x, y, w, "G_est  densidade", f"{m['gest'][2]:.6f}")
        y = self.kv(surf, x, y, w, "Teto teórico", fmt_num(m['teto']))
        y = self.kv(surf, x, y, w, "Ocupação (alcançáveis/teto)", f"{m['ocupacao'] * 100:.2f}%")
        y = self.kv(surf, x, y, w, "Becos (grau de saída 0)", str(m['becos']))
        trap_color = T.WARN if s.traps else T.TEXT
        y = self.kv(surf, x, y, w, "Estados-armadilha", f"{len(s.traps)} ({s.trap_ratio * 100:.1f}%)", trap_color)
        y = self.kv(surf, x, y, w, "ALVO alcançável?", "sim" if s.has_target else "não",
                    T.OK if s.has_target else T.ERR)
        return y + px(14)

    def panel_layers(self, surf, ui, x, y, w):
        s = self.session
        y = self.section(surf, x, y, f"Camadas ({len(s.layer_names)}) · clique para filtrar")
        options = [(None, "todas", sum(c["ordem"] for c in s.layers["camadas"].values()), None)]
        for name in s.layer_names:
            info = s.layers["camadas"][name]
            options.append((name, name, info["ordem"], info["tamanho"]))
        for name, label, order, size in options:
            r = pygame.Rect(x - px(6), y, w + px(12), px(26))
            active = self.show_heat and self.layer == name and self.model == "estados"
            swatch = s.layer_color.get(name) if name else T.TEXT_FAINT
            hint = f"|V| {order}" + (f" · |E| {size}" if size is not None else "")
            visible = ui.clip is None or ui.clip.contains(r)
            if visible and ui.button(surf, ("layer", label), r, label, active=active, style="ghost",
                                     align="left", swatch=swatch, hint=hint, size=13):
                self.layer = name
                self.show_heat = True
                if self.model != "estados":
                    self.set_model("estados")
            elif not visible:
                text(surf, label, Fonts.get(13), T.TEXT, (r.x + px(30), r.centery), "midleft")
            y += px(28)
        n_arcs = len(s.layers["arcos_entre_camadas"])
        y += px(4)
        y = self.kv(surf, x, y, w, "Arcos entre camadas", str(n_arcs))
        if s.layer_change_cells:
            cells = ", ".join(f"({r},{c})" for r, c in sorted(s.layer_change_cells))
            for line in wrap("Casas que mudam de camada: " + cells, Fonts.get(12), w):
                text(surf, line, Fonts.get(12), T.TEXT_FAINT, (x, y))
                y += px(17)
        return y + px(16)

    def draw_right(self, surf, ui, rect):
        pygame.draw.rect(surf, T.PANEL, rect)
        pygame.draw.line(surf, T.BORDER, rect.topleft, rect.bottomleft, 1)
        if self.session is None:
            return
        if ui.hover(rect) and ui.wheel:
            self.panel_scroll -= ui.wheel * px(48)
        max_scroll = max(0, self.panel_content_h - rect.h + px(24))
        self.panel_scroll = max(0, min(max_scroll, self.panel_scroll))

        surf.set_clip(rect)
        ui.clip = rect
        x, w = rect.x + px(20), rect.w - px(40)
        y0 = rect.y + px(18) - self.panel_scroll
        y = y0
        runs = self.runs()
        if self.explore_mode:
            y = self.panel_explore(surf, x, y, w, runs)
        else:
            y = self.panel_state(surf, x, y, w, runs[0])
            if len(runs) > 1:
                y = self.panel_state(surf, x, y, w, runs[1], compact=True)
        y = self.panel_result(surf, x, y, w, runs)
        y = self.panel_metrics(surf, x, y, w)
        y = self.panel_layers(surf, ui, x, y, w)
        self.panel_content_h = y - y0
        surf.set_clip(None)
        ui.clip = None
        if max_scroll:
            bar_h = max(px(30), int(rect.h * rect.h / (self.panel_content_h + px(24))))
            bar_y = rect.y + int((rect.h - bar_h) * self.panel_scroll / max_scroll)
            rrect(surf, T.PANEL_3, pygame.Rect(rect.right - px(5), bar_y, px(3), bar_h), 2)

    # ---------------------------------------------------------------- barra inferior
    def draw_bottom(self, surf, ui, rect):
        pygame.draw.rect(surf, T.PANEL, rect)
        pygame.draw.line(surf, T.BORDER, rect.topleft, rect.topright, 1)
        p = self.player
        cy = rect.centery
        x = rect.x + px(18)
        has = p.length > 1
        for icon, action, size, tip in (
            ("first", "first", 36, "Início (Home)"),
            ("prev", "prev", 36, "Passo anterior (←, Shift+← = 10)"),
            ("pause" if p.playing else "play", "play", 46, "Reproduzir / pausar (Espaço)"),
            ("next", "next", 36, "Próximo passo (→, Shift+→ = 10)"),
            ("last", "last", 36, "Fim (End)"),
        ):
            b = pygame.Rect(0, 0, px(size), px(size))
            b.midleft = (x, cy)
            style = "accent" if action == "play" else "default"
            if ui.button(surf, ("ctl", action), b, icon=icon, style=style, enabled=has, tooltip=tip):
                if action == "first":
                    p.seek(0)
                elif action == "prev":
                    p.step(-1)
                elif action == "play":
                    p.toggle()
                elif action == "next":
                    p.step(1)
                else:
                    p.seek(p.last)
            x = b.right + px(8)

        # ---- linha do tempo (linha de cima) e velocidade (linha de baixo)
        tx = x + px(18)
        tw = rect.right - px(22) - tx
        mode = "Exploração" if self.explore_mode else ("Ciclo negativo" if p.loop else "Percurso")
        idx = int(round(p.pos)) if has else 0
        text(surf, f"{mode}  ·  passo {idx} de {p.last}", Fonts.get(13, bold=True), T.TEXT, (tx, rect.y + px(12)))
        if self.session and not self.explore_mode:
            run = self.runs()[0]
            frame, *_ = self.frame_at(run)
            if frame is not None:
                text(surf, f"camada {layer_label(frame.keys)}", Fonts.get(12, bold=True),
                     self.session.color_of_keys(frame.keys), (tx + tw, rect.y + px(13)), "topright")
        ticks = []
        if self.session and not self.explore_mode and has:
            frames = self.runs()[0].frames
            for k in range(1, len(frames)):
                if frames[k].keys != frames[k - 1].keys:
                    ticks.append((k / p.last, self.session.color_of_keys(frames[k].keys)))
        t = p.pos / p.last if has else 0.0
        new_t, changed = ui.slider(surf, "timeline", pygame.Rect(tx, rect.y + px(36), tw, px(14)), t, ticks=ticks)
        if changed and has:
            p.seek(round(new_t * p.last))

        sy = rect.y + px(72)
        r = text(surf, "Velocidade", Fonts.get(12, bold=True), T.TEXT_DIM, (tx, sy), "midleft")
        speed_w = min(px(220), max(px(80), tw - (r.right - tx) - px(130)))
        st, changed = ui.slider(surf, "speed", pygame.Rect(r.right + px(14), sy - px(7), speed_w, px(14)),
                                speed_to_t(self.speed), color=T.INFO)
        if changed:
            self.speed = t_to_speed(st)
        text(surf, f"{self.speed:.1f} passos/s", Fonts.get(12), T.TEXT_DIM, (r.right + px(28) + speed_w, sy), "midleft")

    # ---------------------------------------------------------------- ajuda
    def draw_help(self, surf, ui):
        W, H = surf.get_size()
        shade = pygame.Surface((W, H), pygame.SRCALPHA)
        shade.fill((0, 0, 0, 170))
        surf.blit(shade, (0, 0))
        box = pygame.Rect(0, 0, min(W - px(40), px(760)), min(H - px(40), px(560)))
        box.center = (W // 2, H // 2)
        rrect(surf, T.PANEL, box, 12)
        rrect(surf, T.BORDER, box, 12, 1)
        text(surf, "Atalhos de teclado", Fonts.get(20, bold=True), T.TEXT, (box.x + px(28), box.y + px(24)))
        left = [
            ("Espaço", "reproduzir / pausar"),
            ("← / →", "passo anterior / próximo"),
            ("Shift + ← / →", "10 passos"),
            ("Home / End", "início / fim"),
            ("↑ / ↓", "mais rápido / mais lento"),
            ("R", "reiniciar a animação"),
            ("Tab / Shift+Tab", "próximo / anterior mapa"),
            ("arrastar .txt", "abrir mapa surpresa"),
        ]
        right = [
            ("1 – 4", "BFS · Dijkstra · Bellman-Ford · DFS"),
            ("Shift + 1 – 4", "algoritmo para comparar"),
            ("M", "trocar modelo do grafo"),
            ("X", "exploração passo a passo"),
            ("H / L", "mapa de calor / trocar camada"),
            ("T", "estados-armadilha"),
            ("C", "comparar lado a lado"),
            ("P / E", "exportar PNG / editor"),
        ]
        col_w = (box.w - px(56)) // 2
        for c, items in enumerate((left, right)):
            y = box.y + px(72)
            x = box.x + px(28) + c * (col_w + px(12))
            for key, desc in items:
                kfont = Fonts.get(13, bold=True)
                kw = kfont.size(key)[0] + px(16)
                kr = pygame.Rect(x, y, kw, px(26))
                rrect(surf, T.PANEL_3, kr, 5)
                text(surf, key, kfont, T.TEXT, kr.center, "center")
                text(surf, text_fit(desc, Fonts.get(13), col_w - kw - px(12)), Fonts.get(13), T.TEXT_DIM,
                     (kr.right + px(12), kr.centery), "midleft")
                y += px(36)
        note = ("Os algoritmos e o grafo de estados são os do grupo (src/graphs/). "
                "A interface só chama as funções e anima o resultado.")
        yy = box.bottom - px(56)
        for line in wrap(note, Fonts.get(12), box.w - px(56)):
            text(surf, line, Fonts.get(12), T.TEXT_FAINT, (box.x + px(28), yy))
            yy += px(17)
        close = pygame.Rect(0, 0, px(34), px(34))
        close.topright = (box.right - px(14), box.y + px(14))
        if ui.button(surf, "help_close", close, icon="cross", style="ghost") or (ui.pressed and not box.collidepoint(ui.mouse)):
            self.show_help = False
