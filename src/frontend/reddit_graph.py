# [IA] Codex – sintaxe Pygame para a visão geral da rede e destaque da consulta.
from math import cos, hypot, pi, sin, sqrt

import pygame

from src.frontend import theme as T
from src.frontend.theme import Fonts, px
from src.frontend.widgets import text, text_fit


class RedditGraphView:
    def __init__(self, names, edges):
        self.indices = {name: index for index, name in enumerate(names)}
        self.edges = edges

        degrees = [0] * len(names)
        for source, destination in edges:
            degrees[source] += 1
            degrees[destination] += 1

        # Place densely connected communities near the center of the overview.
        self.layout = [(0.0, 0.0)] * len(names)
        golden_angle = pi * (3 - sqrt(5))
        for rank, index in enumerate(sorted(range(len(names)), key=lambda i: -degrees[i])):
            radius = sqrt(rank / max(1, len(names) - 1))
            angle = rank * golden_angle
            self.layout[index] = (radius * cos(angle), radius * sin(angle))
        self.base = None
        self.points = []

    def prepare(self, size):
        if self.base is not None and self.base.get_size() == size:
            return
        self.base = pygame.Surface(size)
        self.base.fill(T.BG)
        width, height = size
        self.points = [
            (int(width / 2 + x * width * 0.44), int(height / 2 + y * height * 0.42))
            for x, y in self.layout
        ]
        edge_color = T.lerp_color(T.BG, T.INFO, 0.12)
        node_color = T.lerp_color(T.BG, T.TEXT_DIM, 0.32)
        self.base.lock()
        try:
            for source, destination in self.edges:
                pygame.draw.line(self.base, edge_color, self.points[source], self.points[destination])
            for point in self.points:
                self.base.set_at(point, node_color)
        finally:
            self.base.unlock()

    def draw(self, surf, ui, rect, route=None, cycle=False):
        self.prepare(rect.size)
        surf.blit(self.base, rect.topleft)
        pygame.draw.rect(surf, T.BORDER, rect, 1, border_radius=4)
        if not route:
            return

        points = [(x + rect.x, y + rect.y) for x, y in (self.points[self.indices[name]] for name in route)]
        color = T.WARN if cycle else T.ACCENT
        width = max(2, px(3))
        for start, end in zip(points, points[1:]):
            self.draw_arc(surf, start, end, color, width)
        for index, (point, name) in enumerate(zip(points, route)):
            endpoint = index in (0, len(points) - 1)
            radius = px(6 if endpoint else 4)
            pygame.draw.circle(surf, T.BG, point, radius + px(2))
            pygame.draw.circle(surf, color, point, radius)
            if ui.hover(pygame.Rect(point[0] - radius, point[1] - radius, radius * 2, radius * 2)):
                ui.tooltip = f"r/{name}"
        if not cycle:
            self.draw_endpoint(surf, rect, points[0], route[0], above=True)
            if len(points) > 1:
                self.draw_endpoint(surf, rect, points[-1], route[-1], above=False)

    def draw_endpoint(self, surf, bounds, point, name, above):
        font = Fonts.get(12, bold=True)
        label = text_fit(f"r/{name}", font, bounds.w // 2)
        image = font.render(label, True, T.TEXT)
        box = image.get_rect().inflate(px(10), px(4))
        if above:
            box.midbottom = (point[0], point[1] - px(10))
        else:
            box.midtop = (point[0], point[1] + px(10))
        box.clamp_ip(bounds.inflate(-px(4), -px(4)))
        pygame.draw.rect(surf, T.PANEL, box, border_radius=4)
        text(surf, label, font, T.TEXT, box.center, "center")

    def draw_arc(self, surf, start, end, color, width):
        x, y = start
        dx, dy = end[0] - x, end[1] - y
        length = hypot(dx, dy)
        if start == end:
            center = (x + px(8), y - px(8))
            pygame.draw.circle(surf, color, center, px(9), width)
            return
        pygame.draw.line(surf, color, start, end, width)
        if length < px(16):
            return
        ux, uy = dx / length, dy / length
        tip = (x + 0.65 * dx, y + 0.65 * dy)
        base = (tip[0] - px(9) * ux, tip[1] - px(9) * uy)
        pygame.draw.polygon(surf, color, [
            tip, (base[0] - px(4) * uy, base[1] + px(4) * ux),
            (base[0] + px(4) * uy, base[1] - px(4) * ux),
        ])
