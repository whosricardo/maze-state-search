# [IA] Claude Code (Opus 5.5) – interface pygame: janela, loop principal, troca de telas e notificações
import sys

import pygame

from src.frontend import theme as T
from src.frontend.theme import Fonts, px
from src.frontend.widgets import UI, rrect, text, wrap


def _setup_dpi():
    """No Windows, evita a janela borrada em telas com zoom (125%, 150%...)."""
    if sys.platform != "win32":
        return 1.0
    import ctypes
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            return 1.0
    try:
        return ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100.0
    except Exception:
        return 1.0


def _window_icon():
    icon = pygame.Surface((32, 32), pygame.SRCALPHA)
    for k, col in enumerate((T.ACCENT, (255, 160, 90), (255, 214, 170))):
        pygame.draw.rect(icon, col, (3, 20 - k * 8, 26, 9), border_radius=3)
    return icon


# [IA] Codex – sintaxe Pygame para a capa e o menu
class ProjectMenu:
    def __init__(self, app):
        self.app = app
        self.entered = False

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self.entered = True
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.cover()

    def update(self, dt):
        pass

    def draw(self, surf, ui):
        surf.fill(T.BG)
        cx, cy = surf.get_rect().center
        text(surf, "Teoria dos Grafos e AVD", Fonts.get(32, bold=True), T.TEXT,
             (cx, cy - px(126)), "center")
        pygame.draw.line(surf, T.ACCENT, (cx-px(55), cy-px(94)), (cx+px(55), cy-px(94)), px(3))
        if self.entered:
            choices = [("Parte 1", self.app.open_viewer),
                       ("Parte 2", self.app.open_reddit), ("Voltar à capa", self.cover)]
        else:
            members = ("Lucas Menezes Santana", "Ricardo Sergio Freitas",
                       "Thiago Medeiros", "Kauan Novello")
            for index, member in enumerate(members):
                text(surf, member, Fonts.get(17), T.TEXT, (cx, cy-px(60)+index*px(26)), "center")
            choices = [("Entrar", self.enter)]
        for index, (label, action) in enumerate(choices):
            width = min(px(380), surf.get_width() - px(24))
            rect = pygame.Rect(cx-width//2, cy+px(66)+index*px(54), width, px(42))
            if ui.button(surf, ("project-menu", index), rect, label, style="default" if label == "Voltar à capa" else "accent", bold=True):
                action()

    # [IA] Codex – navegação entre capa e menu
    def cover(self):
        self.entered = False

    def enter(self):
        self.entered = True


class App:
    TOAST_MS = 4200

    def __init__(self, extra_maps=(), initial=None, start_in_editor=False):
        T.set_scale(_setup_dpi())
        pygame.init()
        pygame.key.set_repeat(320, 45)

        desk_w, desk_h = pygame.display.get_desktop_sizes()[0]
        size = (min(px(1480), int(desk_w * 0.92)), min(px(920), int(desk_h * 0.86)))
        self.screen = pygame.display.set_mode(size, pygame.RESIZABLE)
        pygame.display.set_caption("Labirinto de Estados · Teoria dos Grafos")
        pygame.display.set_icon(_window_icon())

        self.clock = pygame.time.Clock()
        self.ui = UI()
        self.extra_maps = list(extra_maps)
        self.toasts = []

        # importados aqui para que o tema/escala já esteja configurado
        from src.frontend.viewer import Viewer
        from src.frontend.editor import Editor

        self.viewer = Viewer(self, initial)
        self.editor = Editor(self)
        self.menu = ProjectMenu(self)
        self.reddit = None
        self.current = self.editor if start_in_editor else self.viewer if initial else self.menu
        self.pending = None

    # -------------------------------------------------------------- API para as telas
    def toast(self, message, kind="info"):
        self.toasts.append((message, kind, pygame.time.get_ticks()))
        self.toasts = self.toasts[-4:]

    def open_menu(self):
        if self.current is self.reddit and self.reddit.running:
            self.reddit.stop()
        self.menu.entered = True
        self.pending = self.menu

    def open_reddit(self):
        from src.frontend.reddit import RedditScreen

        if self.reddit is None:
            self.reddit = RedditScreen(self)
        self.pending = self.reddit

    def open_editor(self):
        self.pending = self.editor

    def open_viewer(self):
        self.pending = self.viewer

    # -------------------------------------------------------------- loop
    def run(self):
        running = True
        while running:
            dt = min(self.clock.tick(60) / 1000.0, 0.1)
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.DROPFILE:
                    if event.file.lower().endswith(".txt"):
                        if self.viewer.load_path(event.file):
                            self.open_viewer()
                    else:
                        self.toast("Arraste um arquivo de mapa .txt", "warn")
                else:
                    self.current.handle_event(event)

            self.ui.begin(events)
            self.current.update(dt)
            self.current.draw(self.screen, self.ui)
            self.draw_toasts(self.screen)
            self.ui.draw_tooltip(self.screen)
            self.ui.end()
            pygame.display.flip()

            if self.pending is not None:
                self.current = self.pending
                self.pending = None
        if self.reddit is not None:
            self.reddit.stop()
        self.viewer.compare_executor.shutdown(wait=False, cancel_futures=True)
        pygame.quit()

    def draw_toasts(self, surf):
        now = pygame.time.get_ticks()
        self.toasts = [t for t in self.toasts if now - t[2] < self.TOAST_MS]
        W, H = surf.get_size()
        y = H - px(108)
        colors = {"ok": T.OK, "err": T.ERR, "warn": T.WARN, "info": T.INFO}
        font = Fonts.get(13)
        for message, kind, born in reversed(self.toasts):
            age = now - born
            alpha = 1.0
            if age > self.TOAST_MS - 400:
                alpha = (self.TOAST_MS - age) / 400
            lines = wrap(message, font, px(560))
            w = max(font.size(line)[0] for line in lines) + px(40)
            h = len(lines) * font.get_linesize() + px(18)
            box = pygame.Rect(0, 0, w, h)
            box.midbottom = (W // 2, y)
            layer = pygame.Surface(box.size, pygame.SRCALPHA)
            rrect(layer, (16, 16, 20, 240), layer.get_rect(), 8)
            pygame.draw.rect(layer, colors.get(kind, T.INFO), (0, 0, px(5), h),
                             border_top_left_radius=px(8), border_bottom_left_radius=px(8))
            for i, line in enumerate(lines):
                text(layer, line, font, T.TEXT, (px(20), px(9) + i * font.get_linesize()))
            layer.set_alpha(int(255 * max(0.0, alpha)))
            surf.blit(layer, box)
            y = box.y - px(8)
