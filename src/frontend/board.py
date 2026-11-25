# [IA] Claude Code (Opus 5.5) – interface pygame: desenho do mapa, sobreposições e percurso animado
import math

import pygame

from src.frontend import theme as T
from src.frontend.theme import Fonts


def _darker(color, amount=30):
    return tuple(max(0, c - amount) for c in color)


def draw_tile(surf, symbol, rect, opened=frozenset(), consumed=False):
    """Desenha uma casa do mapa. `opened` = chaves que abrem portas; `consumed` = bônus já usado."""
    cell = rect.w
    detail = cell >= 12
    letter_font = Fonts.raw(cell * 0.56, bold=True)

    if symbol == '#':
        pygame.draw.rect(surf, T.TILE['#'], rect)
        if cell >= 10:
            pygame.draw.line(surf, (74, 74, 84), rect.topleft, (rect.right - 1, rect.top))
        return

    inner = rect.inflate(-1, -1) if cell >= 8 else rect

    def letter(ch, color):
        if cell >= 11:
            img = letter_font.render(ch, True, color)
            surf.blit(img, img.get_rect(center=rect.center))

    if symbol in ('.',):
        pygame.draw.rect(surf, T.TILE['.'], inner)
    elif symbol == 'S':
        pygame.draw.rect(surf, T.TILE['S'], inner)
        letter('S', (27, 94, 32))
    elif symbol == 'G':
        pygame.draw.rect(surf, T.TILE['G'], inner)
        letter('G', (150, 70, 0))
    elif symbol == ',':
        pygame.draw.rect(surf, T.TILE[','], inner)
        if detail:
            r = max(1, cell // 10)
            for fx, fy in ((0.3, 0.35), (0.65, 0.3), (0.45, 0.68), (0.75, 0.7)):
                pygame.draw.circle(surf, (150, 112, 62), (rect.x + cell * fx, rect.y + cell * fy), r)
    elif symbol == '~':
        pygame.draw.rect(surf, T.TILE['~'], inner)
        if detail:
            w = max(1, cell // 14)
            for fy in (0.38, 0.66):
                pts = [
                    (rect.x + cell * (0.15 + 0.7 * k / 8),
                     rect.y + cell * fy + math.sin(k / 8 * 2 * math.pi) * cell * 0.06)
                    for k in range(9)
                ]
                pygame.draw.lines(surf, (230, 244, 252), False, pts, w)
    elif symbol in 'abcd':
        pygame.draw.rect(surf, T.TILE['key'], inner)
        if cell >= 16:
            # pequeno ícone de chave + letra
            cx, cy = rect.x + cell * 0.32, rect.y + cell * 0.5
            rr = cell * 0.13
            pygame.draw.circle(surf, (160, 120, 0), (cx, cy), rr, max(1, cell // 14))
            pygame.draw.line(surf, (160, 120, 0), (cx + rr, cy), (cx + cell * 0.36, cy), max(1, cell // 14))
            img = Fonts.raw(cell * 0.46, bold=True).render(symbol, True, (120, 84, 0))
            surf.blit(img, img.get_rect(center=(rect.x + cell * 0.7, rect.centery)))
        else:
            letter(symbol, (120, 84, 0))
    elif symbol in 'ABCD':
        is_open = symbol.lower() in opened
        if is_open:
            pygame.draw.rect(surf, T.TILE['door_open'], inner)
            if cell >= 10:
                pygame.draw.rect(surf, T.TILE['door'], inner, max(1, cell // 12))
            letter(symbol, T.TILE['door'])
        else:
            pygame.draw.rect(surf, T.TILE['door'], inner)
            if cell >= 14:
                bar = pygame.Rect(0, 0, cell * 0.6, max(2, cell // 9))
                bar.center = (rect.centerx, rect.y + cell * 0.82)
                pygame.draw.rect(surf, (90, 60, 150), bar, border_radius=2)
            letter(symbol, (255, 255, 255))
    elif symbol in '><^v':
        pygame.draw.rect(surf, T.TILE['conveyor'], inner)
        cx, cy = rect.center
        s = cell * 0.32
        dirs = {'>': (1, 0), '<': (-1, 0), '^': (0, -1), 'v': (0, 1)}
        dx, dy = dirs[symbol]
        tip = (cx + dx * s, cy + dy * s)
        base1 = (cx - dx * s * 0.6 - dy * s * 0.8, cy - dy * s * 0.6 - dx * s * 0.8)
        base2 = (cx - dx * s * 0.6 + dy * s * 0.8, cy - dy * s * 0.6 + dx * s * 0.8)
        pygame.draw.polygon(surf, (84, 98, 120), [tip, base1, base2])
    elif symbol == '+':
        pygame.draw.rect(surf, T.TILE['+used'] if consumed else T.TILE['+'], inner)
        color = (176, 176, 168) if consumed else (46, 125, 50)
        w = max(1, cell // 7)
        s = cell * 0.28
        pygame.draw.line(surf, color, (rect.centerx - s, rect.centery), (rect.centerx + s, rect.centery), w)
        pygame.draw.line(surf, color, (rect.centerx, rect.centery - s), (rect.centerx, rect.centery + s), w)
    elif symbol == '*':
        pygame.draw.rect(surf, T.TILE['*'], inner)
        cx, cy = rect.centerx, rect.y + cell * 0.58
        r = cell * 0.2
        pygame.draw.circle(surf, (2, 136, 209), (cx, cy), r)
        pygame.draw.polygon(surf, (2, 136, 209), [(cx - r * 0.95, cy - r * 0.3), (cx + r * 0.95, cy - r * 0.3), (cx, cy - r * 2.1)])
    else:
        pygame.draw.rect(surf, T.TILE['.'], inner)


class Board:
    """Desenha um grid em um retângulo, com zoom automático."""

    def __init__(self, grid):
        self.grid = grid
        self.version = 0
        self.cell = 8
        self.rect = pygame.Rect(0, 0, 0, 0)
        self._cache = {}

    @property
    def rows(self):
        return len(self.grid)

    @property
    def cols(self):
        return len(self.grid[0]) if self.grid else 0

    def invalidate(self):
        self.version += 1
        self._cache.clear()

    # [IA] Codex – suporte de encaixe para quatro tabuleiros
    def fit(self, area, max_cell=64, min_cell=3):
        cell = max(min_cell, min(area.w // max(1, self.cols), area.h // max(1, self.rows), max_cell))
        w, h = cell * self.cols, cell * self.rows
        self.cell = cell
        self.rect = pygame.Rect(area.x + (area.w - w) // 2, area.y + (area.h - h) // 2, w, h)
        return self.rect

    def cell_rect(self, pos):
        r, c = pos
        return pygame.Rect(self.rect.x + c * self.cell, self.rect.y + r * self.cell, self.cell, self.cell)

    def center(self, pos):
        r, c = pos
        return (self.rect.x + (c + 0.5) * self.cell, self.rect.y + (r + 0.5) * self.cell)

    def pos_at(self, point):
        if not self.rect.collidepoint(point):
            return None
        c = (point[0] - self.rect.x) // self.cell
        r = (point[1] - self.rect.y) // self.cell
        if 0 <= r < self.rows and 0 <= c < self.cols:
            return (int(r), int(c))
        return None

    # -------------------------------------------------------------- base
    def base(self, opened=frozenset(), consumed=frozenset()):
        key = (self.cell, self.version, frozenset(opened), frozenset(consumed))
        surf = self._cache.get(key)
        if surf is None:
            if len(self._cache) > 48:
                self._cache.clear()
            surf = pygame.Surface((self.cell * self.cols, self.cell * self.rows))
            surf.fill(T.GRID_LINE)
            for r, row in enumerate(self.grid):
                for c, symbol in enumerate(row):
                    rect = pygame.Rect(c * self.cell, r * self.cell, self.cell, self.cell)
                    draw_tile(surf, symbol, rect, opened, (r, c) in consumed)
            self._cache[key] = surf
        return surf

    # -------------------------------------------------------------- desenho completo
    def draw(self, surf, *, opened=frozenset(), consumed=frozenset(), heat=None,
             explore=None, explore_last=None, traps=None, marks=None, trail=None,
             agent=None, invalid=None, ghost=None, numbers=True):
        surf.blit(self.base(opened, consumed), self.rect.topleft)
        cell = self.cell

        if heat or explore or traps:
            overlay = pygame.Surface(self.rect.size, pygame.SRCALPHA)
            if heat:
                top = max(heat.values())
                for pos, n in heat.items():
                    r = pygame.Rect(pos[1] * cell, pos[0] * cell, cell, cell)
                    t = n / top if top else 0
                    overlay.fill(T.with_alpha(T.heat_color(t), 150 + 70 * t), r)
            if explore:
                top = max(explore.values())
                for pos, n in explore.items():
                    r = pygame.Rect(pos[1] * cell, pos[0] * cell, cell, cell)
                    t = n / top if top else 0
                    overlay.fill(T.with_alpha(T.ACCENT, 70 + 120 * t), r)
            if traps:
                w = max(1, cell // 10)
                for pos in traps:
                    r = pygame.Rect(pos[1] * cell, pos[0] * cell, cell, cell)
                    overlay.fill((229, 57, 53, 70), r)
                    overlay.set_clip(r)
                    step = max(4, cell // 3)
                    for k in range(-cell, cell, step):
                        pygame.draw.line(overlay, (198, 40, 40, 200), (r.x + k, r.bottom), (r.x + k + cell, r.y), w)
                    overlay.set_clip(None)
            surf.blit(overlay, self.rect.topleft)

            counts = heat or explore or traps
            if numbers and cell >= 20 and isinstance(counts, dict):
                font = Fonts.raw(cell * 0.42, bold=True)
                for pos, n in counts.items():
                    img = font.render(str(n), True, (20, 20, 20))
                    shadow = font.render(str(n), True, (255, 255, 255))
                    rc = self.cell_rect(pos)
                    surf.blit(shadow, shadow.get_rect(center=(rc.centerx + 1, rc.centery + 1)))
                    surf.blit(img, img.get_rect(center=rc.center))

        if marks:
            w = max(1, cell // 9)
            for pos in marks:
                pygame.draw.rect(surf, (255, 214, 0), self.cell_rect(pos).inflate(-w, -w), w, border_radius=max(1, cell // 6))

        if explore_last is not None:
            rc = self.cell_rect(explore_last)
            pygame.draw.rect(surf, (255, 255, 255), rc.inflate(4, 4), max(2, cell // 8), border_radius=3)

        if ghost:
            self._draw_trail(surf, ghost, faded=True)
        if trail:
            self._draw_trail(surf, trail)

        if invalid:
            w = max(2, cell // 6)
            for pos in invalid:
                rc = self.cell_rect(pos).inflate(-cell // 4, -cell // 4)
                pygame.draw.line(surf, (211, 47, 47), rc.topleft, rc.bottomright, w)
                pygame.draw.line(surf, (211, 47, 47), rc.bottomleft, rc.topright, w)

        if agent:
            point, color = agent
            radius = max(3, int(cell * 0.36))
            halo = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
            pygame.draw.circle(halo, T.with_alpha(color, 70), (radius * 2, radius * 2), radius * 2)
            surf.blit(halo, (point[0] - radius * 2, point[1] - radius * 2))
            pygame.draw.circle(surf, (255, 255, 255), point, radius + max(1, cell // 14))
            pygame.draw.circle(surf, color, point, radius)

    def _draw_trail(self, surf, trail, faded=False):
        """trail = [(ponto_xy, cor), ...] — cada segmento usa a cor do ponto de destino."""
        if not trail:
            return
        width = max(2, self.cell // 5)
        if faded:
            width = max(1, self.cell // 7)
        layer = pygame.Surface(surf.get_size(), pygame.SRCALPHA) if faded else surf
        alpha = 110 if faded else 255
        for (a, _), (b, color) in zip(trail, trail[1:]):
            col = T.with_alpha(color, alpha)
            pygame.draw.line(layer, col, a, b, width)
            pygame.draw.circle(layer, col, b, width // 2)
        first_point, first_color = trail[0]
        pygame.draw.circle(layer, T.with_alpha(first_color, alpha), first_point, width // 2 + 1)
        if faded:
            surf.blit(layer, (0, 0))
