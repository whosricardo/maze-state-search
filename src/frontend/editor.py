# [IA] Claude Code (Opus 5.5) – interface pygame: editor de mapas com validação e análise ao vivo
import copy

import pygame

from src.frontend import theme as T
from src.frontend.theme import Fonts, px, SYMBOL_INFO, PALETTE_ORDER
from src.frontend.widgets import rrect, text, text_fit, wrap, draw_icon, TextInput
from src.frontend.board import Board, draw_tile
from src.frontend.model import GROUP_MAPS_DIR, quick_analysis, validation_problems

MIN_ROWS, MIN_COLS = 3, 3
MAX_ROWS, MAX_COLS = 40, 90


def blank_grid(rows=9, cols=15):
    grid = []
    for r in range(rows):
        if r in (0, rows - 1):
            grid.append(['#'] * cols)
        else:
            grid.append(['#'] + ['.'] * (cols - 2) + ['#'])
    grid[1][1] = 'S'
    grid[rows - 2][cols - 2] = 'G'
    return grid


class Editor:
    def __init__(self, app):
        self.app = app
        self.grid = blank_grid()
        self.board = Board(self.grid)
        self.symbol = '#'
        self.name = TextInput("mapa_grupo_01", max_len=40, placeholder="nome_do_mapa")
        self.undo_stack = []
        self.painting = None
        self.dirty = True
        self.analysis = None

    # -------------------------------------------------------------- grid
    def load_grid(self, grid, name=None):
        self.grid = [list(row) for row in grid]
        self.board.grid = self.grid
        self.board.invalidate()
        if name:
            self.name.value = name
        self.undo_stack.clear()
        self.dirty = True

    def push_undo(self):
        self.undo_stack.append(copy.deepcopy(self.grid))
        if len(self.undo_stack) > 80:
            self.undo_stack.pop(0)

    def undo(self):
        if not self.undo_stack:
            self.app.toast("Nada para desfazer.", "info")
            return
        self.grid = self.undo_stack.pop()
        self.board.grid = self.grid
        self.board.invalidate()
        self.dirty = True

    def set_cell(self, pos, symbol):
        r, c = pos
        if self.grid[r][c] == symbol:
            return
        if symbol in ('S', 'G'):
            for rr, row in enumerate(self.grid):
                for cc, cell in enumerate(row):
                    if cell == symbol:
                        self.grid[rr][cc] = '.'
        self.grid[r][c] = symbol
        self.board.invalidate()
        self.dirty = True

    def resize(self, d_rows=0, d_cols=0):
        rows, cols = len(self.grid), len(self.grid[0])
        if not (MIN_ROWS <= rows + d_rows <= MAX_ROWS and MIN_COLS <= cols + d_cols <= MAX_COLS):
            self.app.toast("Tamanho no limite.", "warn")
            return
        self.push_undo()
        if d_rows > 0:
            self.grid.insert(rows - 1, ['#'] + ['.'] * (cols - 2) + ['#'])
        elif d_rows < 0:
            self.grid.pop(rows - 2)
        if d_cols > 0:
            for i, row in enumerate(self.grid):
                row.insert(len(row) - 1, '#' if i in (0, len(self.grid) - 1) else '.')
        elif d_cols < 0:
            for row in self.grid:
                row.pop(len(row) - 2)
        self.board.invalidate()
        self.dirty = True

    def save(self, test=False):
        problems = validation_problems(self.grid)
        if problems:
            self.app.toast("Mapa inválido: " + " ".join(problems), "err")
            return
        name = self.name.value.strip() or "mapa_grupo"
        GROUP_MAPS_DIR.mkdir(parents=True, exist_ok=True)
        path = GROUP_MAPS_DIR / f"{name}.txt"
        existed = path.exists()
        path.write_text("\n".join("".join(row) for row in self.grid) + "\n", encoding="utf-8")
        self.app.toast(f"{'Sobrescrito' if existed else 'Salvo'}: data/mapas_grupo/{path.name}", "ok")
        self.app.viewer.refresh_maps()
        if test:
            if self.app.viewer.load_path(path):
                self.app.open_viewer()

    # -------------------------------------------------------------- eventos
    def handle_event(self, event):
        if self.name.handle_event(event):
            return
        if event.type == pygame.KEYDOWN:
            ctrl = bool(event.mod & pygame.KMOD_CTRL)
            if event.key == pygame.K_ESCAPE:
                self.app.open_viewer()
            elif ctrl and event.key == pygame.K_z:
                self.undo()
            elif ctrl and event.key == pygame.K_s:
                self.save()
        elif event.type == pygame.TEXTINPUT:
            if event.text in SYMBOL_INFO:
                self.symbol = event.text

    def update(self, dt):
        if self.dirty and self.painting is None:
            try:
                self.analysis = quick_analysis(self.grid)
            except Exception as error:  # análise é auxiliar: nunca derruba o editor
                self.analysis = {"valid": False, "problems": [f"Erro na análise: {error}"]}
            self.dirty = False

    # -------------------------------------------------------------- desenho
    def draw(self, surf, ui):
        W, H = surf.get_size()
        top = pygame.Rect(0, 0, W, px(58))
        side = pygame.Rect(0, top.bottom, px(256), H - top.bottom)
        right = pygame.Rect(W - px(344), top.bottom, px(344), H - top.bottom)
        bottom = pygame.Rect(side.right, H - px(78), right.x - side.right, px(78))
        center = pygame.Rect(side.right, top.bottom, right.x - side.right, bottom.y - top.bottom)
        surf.fill(T.BG)
        self.draw_canvas(surf, ui, center)
        self.draw_top(surf, ui, top)
        self.draw_palette(surf, ui, side)
        self.draw_analysis(surf, ui, right)
        self.draw_bottom(surf, ui, bottom)

    def draw_top(self, surf, ui, rect):
        pygame.draw.rect(surf, T.PANEL, rect)
        pygame.draw.line(surf, T.BORDER, rect.bottomleft, (rect.right, rect.bottom), 1)
        back = pygame.Rect(0, 0, px(200), px(34))
        back.midleft = (rect.x + px(16), rect.centery)
        if ui.button(surf, "ed_back", back, "Voltar ao labirinto", icon="left", align="left", size=13,
                     tooltip="Esc", bold=True):
            self.app.open_viewer()
        r = text(surf, "Editor de mapas", Fonts.get(18, bold=True), T.TEXT, (back.right + px(20), rect.centery), "midleft")
        text(surf, "esquerdo pinta · direito vira parede · digite o símbolo para escolhê-lo · Ctrl+Z desfaz · Ctrl+S salva",
             Fonts.get(12), T.TEXT_FAINT, (r.right + px(16), rect.centery + px(1)), "midleft")

    def draw_palette(self, surf, ui, rect):
        pygame.draw.rect(surf, T.PANEL, rect)
        pygame.draw.line(surf, T.BORDER, rect.topright, rect.bottomright, 1)
        x, w = rect.x + px(14), rect.w - px(28)
        y = rect.y + px(14)
        text(surf, "PALETA", Fonts.get(11, bold=True), T.TEXT_FAINT, (x, y))
        y += px(20)
        bw, bh, gap = (w - px(8)) // 2, px(36), px(6)
        for k, symbol in enumerate(PALETTE_ORDER):
            r = pygame.Rect(x + (k % 2) * (bw + px(8)), y + (k // 2) * (bh + gap), bw, bh)
            name, cost = SYMBOL_INFO[symbol]
            if ui.button(surf, ("pal", symbol), r, "", active=self.symbol == symbol, style="ghost",
                         tooltip=f"{name} · custo {cost} · tecla '{symbol}'"):
                self.symbol = symbol
            tile = pygame.Rect(r.x + px(6), r.y + px(5), bh - px(10), bh - px(10))
            draw_tile(surf, symbol, tile, opened=frozenset())
            pygame.draw.rect(surf, T.BORDER, tile, 1)
            label = name.replace("Esteira ", "")
            text(surf, text_fit(label, Fonts.get(12), bw - tile.w - px(30)), Fonts.get(12), T.TEXT,
                 (tile.right + px(8), r.centery), "midleft")
            text(surf, symbol, Fonts.get(12, bold=True, mono=True), T.TEXT_FAINT, (r.right - px(8), r.centery), "midright")
        y += (len(PALETTE_ORDER) + 1) // 2 * (bh + gap) + px(14)

        text(surf, "TAMANHO", Fonts.get(11, bold=True), T.TEXT_FAINT, (x, y))
        y += px(22)
        rows, cols = len(self.grid), len(self.grid[0])
        for label, value, dr, dc in (("Linhas", rows, 1, 0), ("Colunas", cols, 0, 1)):
            text(surf, f"{label}", Fonts.get(13), T.TEXT_DIM, (x, y + px(15)), "midleft")
            text(surf, str(value), Fonts.get(14, bold=True), T.TEXT, (x + px(110), y + px(15)), "center")
            minus = pygame.Rect(x + w - px(70), y, px(32), px(30))
            plus = pygame.Rect(x + w - px(32), y, px(32), px(30))
            if ui.button(surf, ("rs-", label), minus, "−", size=16, bold=True):
                self.resize(-dr, -dc)
            if ui.button(surf, ("rs+", label), plus, "+", size=16, bold=True):
                self.resize(dr, dc)
            y += px(38)

    def draw_canvas(self, surf, ui, rect):
        inner = rect.inflate(-px(48), -px(48))
        self.board.fit(inner, max_cell=56)
        frame = self.board.rect.inflate(px(10), px(10))
        rrect(surf, (8, 8, 10), frame.move(0, px(4)), 8)
        rrect(surf, (14, 14, 17), frame, 8)
        rrect(surf, T.BORDER, frame, 8, 1)
        self.board.draw(surf, opened=frozenset())

        pos = self.board.pos_at(ui.mouse) if not ui.blocked else None
        buttons = pygame.mouse.get_pressed()
        if pos is not None and (ui.pressed or ui.right_pressed) and not self.name.focused:
            self.push_undo()
            self.painting = 'L' if ui.pressed else 'R'
        if self.painting == 'L' and not buttons[0]:
            self.painting = None
        if self.painting == 'R' and not buttons[2]:
            self.painting = None
        if pos is not None and self.painting:
            self.set_cell(pos, self.symbol if self.painting == 'L' else '#')
        if pos is not None:
            cell = self.board.cell_rect(pos)
            pygame.draw.rect(surf, T.ACCENT, cell, max(2, px(2)))
            name, cost = SYMBOL_INFO.get(self.grid[pos[0]][pos[1]], ("?", "?"))
            ui.tooltip = f"({pos[0]},{pos[1]})  {name} · custo {cost}"

    def check_row(self, surf, x, y, w, ok, label, detail="", neutral=False):
        color = T.TEXT_FAINT if neutral else (T.OK if ok else T.ERR)
        draw_icon(surf, "check" if ok else ("dot" if neutral else "cross"), (x + px(8), y + px(10)), px(14), color)
        text(surf, label, Fonts.get(13), T.TEXT, (x + px(24), y + px(1)))
        if detail:
            text(surf, detail, Fonts.get(13, bold=True), T.TEXT_DIM, (x + w, y + px(1)), "topright")
        return y + px(24)

    def draw_analysis(self, surf, ui, rect):
        pygame.draw.rect(surf, T.PANEL, rect)
        pygame.draw.line(surf, T.BORDER, rect.topleft, rect.bottomleft, 1)
        x, w = rect.x + px(20), rect.w - px(40)
        y = rect.y + px(18)
        a = self.analysis
        text(surf, "VALIDAÇÃO (io.py do grupo)", Fonts.get(11, bold=True), T.TEXT_FAINT, (x, y))
        y += px(22)
        if a is None:
            text(surf, "analisando…", Fonts.get(13), T.TEXT_DIM, (x, y))
            return
        if not a["valid"]:
            for problem in a["problems"]:
                lines = wrap(problem, Fonts.get(13), w - px(24))
                draw_icon(surf, "cross", (x + px(8), y + px(10)), px(14), T.ERR)
                for line in lines:
                    text(surf, line, Fonts.get(13), T.TEXT, (x + px(24), y + px(1)))
                    y += px(19)
                y += px(6)
            return
        y = self.check_row(surf, x, y, w, True, "Mapa válido", f"{a['size'][0]}×{a['size'][1]}")
        y += px(12)

        text(surf, "GRAFO DE ESTADOS", Fonts.get(11, bold=True), T.TEXT_FAINT, (x, y))
        y += px(22)
        if a.get("too_big"):
            for line in wrap(f"Teto teórico {a['teto']:,} estados: grande demais para analisar ao vivo.".replace(",", "."),
                             Fonts.get(13), w):
                text(surf, line, Fonts.get(13), T.WARN, (x, y))
                y += px(19)
        else:
            def kv(label, value, color=T.TEXT):
                nonlocal y
                text(surf, label, Fonts.get(13), T.TEXT_DIM, (x, y))
                text(surf, str(value), Fonts.get(13, bold=True), color, (x + w, y), "topright")
                y += px(22)

            kv("Estados alcançáveis", a["states"])
            kv("ALVO alcançável?", "sim" if a["solvable"] else "não", T.OK if a["solvable"] else T.ERR)
            if a["solvable"]:
                kv("BFS (passos até ALVO)", a["bfs_steps"])
                cost = a["bf_cost"] if a["bf_status"] == "Encontrado" else a["bf_status"]
                kv("Bellman-Ford (custo)", cost, T.WARN if a["bf_status"] != "Encontrado" else T.TEXT)
            kv("Estados-armadilha", f"{a['traps']} ({a['trap_ratio'] * 100:.1f}%)")
        y += px(12)

        text(surf, "REQUISITOS DO MAPA DO GRUPO", Fonts.get(11, bold=True), T.TEXT_FAINT, (x, y))
        y += px(22)
        y = self.check_row(surf, x, y, w, a["keys"] >= 3, "3 chaves", f"{a['keys']} chave(s), {a['doors']} porta(s)")
        y = self.check_row(surf, x, y, w, a["conveyors"] > 0, "Esteiras", str(a["conveyors"]))
        y = self.check_row(surf, x, y, w, a["bonus"] > 0, "Bônus (+)", str(a["bonus"]))
        if not a.get("too_big"):
            ok = a["trap_ratio"] >= 0.20
            y = self.check_row(surf, x, y, w, ok, "≥ 20% armadilhas*", f"{a['trap_ratio'] * 100:.1f}%")
        y += px(6)
        for line in wrap("* exigido em um dos dois mapas (o \"mapa armadilha\"). "
                         "Mapas salvos vão para data/mapas_grupo/ e aparecem na lista do labirinto.",
                         Fonts.get(12), w):
            text(surf, line, Fonts.get(12), T.TEXT_FAINT, (x, y))
            y += px(17)

    def draw_bottom(self, surf, ui, rect):
        pygame.draw.rect(surf, T.PANEL, rect)
        pygame.draw.line(surf, T.BORDER, rect.topleft, rect.topright, 1)
        cy = rect.centery
        x = rect.x + px(18)
        text(surf, "Nome", Fonts.get(13, bold=True), T.TEXT_DIM, (x, cy), "midleft")
        x += px(48)
        buttons = [
            ("Novo", "new", "default", "Mapa em branco 9×15"),
            ("Copiar aberto", "copy", "default", "Copia o mapa aberto no labirinto para editar"),
            ("Salvar", "save", "default", "Salva em data/mapas_grupo/<nome>.txt (Ctrl+S)"),
            ("Salvar e testar", "test", "accent", "Salva e abre no labirinto interativo"),
        ]
        font = Fonts.get(13, bold=True)
        widths = [font.size(label)[0] + px(28) for label, *_ in buttons]
        total_buttons = sum(widths) + px(8) * (len(buttons) - 1)
        input_w = max(px(140), rect.right - px(18) - total_buttons - px(16) - x)
        self.name.draw(ui, surf, pygame.Rect(x, cy - px(17), input_w, px(34)))
        bx = x + input_w + px(16)
        for (label, action, style, tip), bw in zip(buttons, widths):
            b = pygame.Rect(bx, cy - px(17), bw, px(34))
            if ui.button(surf, ("ed", action), b, label, style=style, tooltip=tip, size=13, bold=True):
                if action == "new":
                    self.load_grid(blank_grid(), None)
                elif action == "copy":
                    session = self.app.viewer.session
                    if session is not None:
                        self.load_grid(session.grid, session.name + "_copia")
                elif action == "save":
                    self.save()
                else:
                    self.save(test=True)
            bx = b.right + px(8)
