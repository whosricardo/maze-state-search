# [IA] Claude Code (Opus 5.5) – interface pygame: widgets em modo imediato (botões, sliders, texto, ícones)
import math

import pygame

from src.frontend import theme as T
from src.frontend.theme import Fonts, px


# ---------------------------------------------------------------- desenho básico
def rrect(surf, color, rect, radius=6, width=0):
    pygame.draw.rect(surf, color, rect, width, border_radius=px(radius))


def text(surf, value, font, color, pos, anchor="topleft"):
    img = font.render(str(value), True, color)
    rect = img.get_rect(**{anchor: pos})
    surf.blit(img, rect)
    return rect


def text_fit(value, font, max_width):
    """Corta o texto com reticências para caber na largura."""
    value = str(value)
    if font.size(value)[0] <= max_width:
        return value
    while value and font.size(value + "…")[0] > max_width:
        value = value[:-1]
    return value + "…"


def wrap(value, font, max_width):
    lines = []
    for paragraph in str(value).split("\n"):
        words = paragraph.split(" ")
        line = ""
        for word in words:
            candidate = f"{line} {word}".strip()
            if font.size(candidate)[0] <= max_width:
                line = candidate
            else:
                if line:
                    lines.append(line)
                line = word
        lines.append(line)
    return lines


def draw_icon(surf, name, center, size, color):
    cx, cy = center
    s = size / 2
    if name == "play":
        pts = [(cx - s * 0.55, cy - s * 0.8), (cx - s * 0.55, cy + s * 0.8), (cx + s * 0.8, cy)]
        pygame.draw.polygon(surf, color, pts)
    elif name == "pause":
        w = max(2, int(s * 0.45))
        pygame.draw.rect(surf, color, (cx - s * 0.65, cy - s * 0.75, w, s * 1.5), border_radius=1)
        pygame.draw.rect(surf, color, (cx + s * 0.65 - w, cy - s * 0.75, w, s * 1.5), border_radius=1)
    elif name in ("next", "prev"):
        d = 1 if name == "next" else -1
        pts = [(cx - d * s * 0.6, cy - s * 0.7), (cx - d * s * 0.6, cy + s * 0.7), (cx + d * s * 0.45, cy)]
        pygame.draw.polygon(surf, color, pts)
        w = max(2, int(s * 0.25))
        x = cx + d * s * 0.5 - (w if d > 0 else 0)
        pygame.draw.rect(surf, color, (x, cy - s * 0.7, w, s * 1.4))
    elif name in ("first", "last"):
        d = 1 if name == "last" else -1
        for off in (-0.45, 0.25):
            ox = cx + d * off * s
            pts = [(ox - d * s * 0.4, cy - s * 0.65), (ox - d * s * 0.4, cy + s * 0.65), (ox + d * s * 0.35, cy)]
            pygame.draw.polygon(surf, color, pts)
        w = max(2, int(s * 0.22))
        x = cx + d * s * 0.7 - (w if d > 0 else 0)
        pygame.draw.rect(surf, color, (x, cy - s * 0.65, w, s * 1.3))
    elif name == "check":
        pts = [(cx - s * 0.6, cy), (cx - s * 0.15, cy + s * 0.5), (cx + s * 0.65, cy - s * 0.55)]
        pygame.draw.lines(surf, color, False, pts, max(2, int(s * 0.3)))
    elif name == "cross":
        w = max(2, int(s * 0.28))
        pygame.draw.line(surf, color, (cx - s * 0.5, cy - s * 0.5), (cx + s * 0.5, cy + s * 0.5), w)
        pygame.draw.line(surf, color, (cx - s * 0.5, cy + s * 0.5), (cx + s * 0.5, cy - s * 0.5), w)
    elif name in ("left", "right"):
        d = 1 if name == "right" else -1
        pts = [(cx - d * s * 0.35, cy - s * 0.6), (cx + d * s * 0.45, cy), (cx - d * s * 0.35, cy + s * 0.6)]
        pygame.draw.lines(surf, color, False, pts, max(2, int(s * 0.28)))
    elif name == "dot":
        pygame.draw.circle(surf, color, (cx, cy), max(2, int(s * 0.5)))


# ---------------------------------------------------------------- UI em modo imediato
class UI:
    """Cada frame a tela chama ui.button(...) etc.; o retorno diz se houve clique.

    Isso evita manter uma árvore de widgets e deixa o layout ser recalculado
    livremente quando a janela muda de tamanho.
    """

    def __init__(self):
        self.mouse = (0, 0)
        self.down = False
        self.pressed = False
        self.released = False
        self.right_pressed = False
        self.wheel = 0
        self.active = None
        self.tooltip = None
        self.clip = None
        self.blocked = False

    def begin(self, events):
        self.pressed = self.released = self.right_pressed = False
        self.wheel = 0
        self.tooltip = None
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.pressed = True
                self.down = True
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                self.right_pressed = True
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.released = True
                self.down = False
            elif event.type == pygame.MOUSEWHEEL:
                self.wheel += event.y
        self.mouse = pygame.mouse.get_pos()

    def end(self):
        if self.released:
            self.active = None

    def hover(self, rect):
        if self.blocked:
            return False
        if self.clip is not None and not self.clip.collidepoint(self.mouse):
            return False
        return rect.collidepoint(self.mouse)

    # -------------------------------------------------------------- botão
    def button(self, surf, wid, rect, label="", *, active=False, enabled=True,
               icon=None, style="default", tooltip=None, size=14, align="center",
               swatch=None, hint=None, bold=False):
        rect = pygame.Rect(rect)
        hovered = enabled and self.hover(rect)
        if hovered and self.pressed:
            self.active = wid
        clicked = hovered and self.released and self.active == wid
        held = hovered and self.down and self.active == wid

        if style == "accent":
            bg = T.ACCENT_HOVER if hovered else T.ACCENT
            fg = (255, 255, 255)
        elif style == "ghost":
            bg = T.PANEL_3 if active else (T.PANEL_2 if hovered else None)
            fg = T.TEXT if (active or hovered) else T.TEXT_DIM
        else:
            if active:
                bg = T.ACCENT
                fg = (255, 255, 255)
            else:
                bg = T.PANEL_3 if hovered else T.PANEL_2
                fg = T.TEXT
        if not enabled:
            bg = T.PANEL_2 if bg is not None else None
            fg = T.TEXT_FAINT
        if held and bg is not None:
            bg = tuple(max(0, c - 18) for c in bg)

        if bg is not None:
            rrect(surf, bg, rect, 6)
        if style == "default" and not active:
            rrect(surf, T.BORDER, rect, 6, 1)

        font = Fonts.get(size, bold=bold or active)
        x_text = rect.x + px(10)
        if icon:
            isz = min(rect.h * 0.5, px(18))
            if label:
                draw_icon(surf, icon, (rect.x + px(10) + isz / 2, rect.centery), isz, fg)
                x_text = rect.x + px(16) + isz
            else:
                draw_icon(surf, icon, rect.center, isz, fg)
        if swatch is not None:
            sw = pygame.Rect(0, 0, px(12), px(12))
            sw.midleft = (rect.x + px(10), rect.centery)
            rrect(surf, swatch, sw, 3)
            x_text = sw.right + px(8)
        if label:
            right_pad = px(10)
            if hint and font.size(label)[0] + Fonts.get(11).size(hint)[0] + px(26) > rect.right - x_text:
                hint = None
            if hint:
                hint_font = Fonts.get(11)
                hint_img = hint_font.render(hint, True, fg if active else T.TEXT_FAINT)
                surf.blit(hint_img, hint_img.get_rect(midright=(rect.right - px(8), rect.centery)))
                right_pad += hint_img.get_width() + px(6)
            if align == "center" and not icon and swatch is None and not hint:
                text(surf, text_fit(label, font, rect.w - px(12)), font, fg, rect.center, "center")
            else:
                max_w = rect.right - right_pad - x_text
                text(surf, text_fit(label, font, max_w), font, fg, (x_text, rect.centery), "midleft")

        if hovered and tooltip:
            self.tooltip = tooltip
        return clicked

    # -------------------------------------------------------------- slider
    def slider(self, surf, wid, rect, t, *, color=None, ticks=None):
        """Slider horizontal; t em [0, 1]. Retorna (novo_t, mudou)."""
        rect = pygame.Rect(rect)
        grab = rect.inflate(px(10), px(18))
        hovered = self.hover(grab)
        if hovered and self.pressed:
            self.active = wid
        changed = False
        if self.active == wid and (self.down or self.released):
            new_t = (self.mouse[0] - rect.x) / max(1, rect.w)
            new_t = max(0.0, min(1.0, new_t))
            changed = abs(new_t - t) > 1e-9
            t = new_t

        color = color or T.ACCENT
        track = pygame.Rect(rect.x, rect.centery - px(3), rect.w, px(6))
        rrect(surf, T.PANEL_3, track, 3)
        fill = track.copy()
        fill.w = int(track.w * t)
        if fill.w > 0:
            rrect(surf, color, fill, 3)
        if ticks:
            for tick_t, tick_color in ticks:
                x = track.x + int(track.w * tick_t)
                pygame.draw.line(surf, tick_color, (x, track.y - px(4)), (x, track.bottom + px(3)), max(1, px(2)))
        knob_r = px(8) if (hovered or self.active == wid) else px(7)
        knob = (track.x + int(track.w * t), track.centery)
        pygame.draw.circle(surf, (255, 255, 255), knob, knob_r)
        pygame.draw.circle(surf, color, knob, knob_r - px(3))
        return t, changed

    def draw_tooltip(self, surf):
        if not self.tooltip:
            return
        font = Fonts.get(12)
        lines = wrap(self.tooltip, font, px(300))
        w = max(font.size(line)[0] for line in lines) + px(16)
        h = len(lines) * font.get_linesize() + px(10)
        x, y = self.mouse[0] + px(14), self.mouse[1] + px(18)
        sw, sh = surf.get_size()
        x = min(x, sw - w - px(4))
        if y + h > sh:
            y = self.mouse[1] - h - px(8)
        box = pygame.Rect(x, y, w, h)
        rrect(surf, (12, 12, 14), box, 6)
        rrect(surf, T.BORDER, box, 6, 1)
        for i, line in enumerate(lines):
            text(surf, line, font, T.TEXT, (x + px(8), y + px(5) + i * font.get_linesize()))


# ---------------------------------------------------------------- campo de texto
class TextInput:
    ALLOWED = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-")

    def __init__(self, value="", max_len=40, placeholder=""):
        self.value = value
        self.max_len = max_len
        self.placeholder = placeholder
        self.focused = False

    def handle_event(self, event):
        if not self.focused:
            return False
        if event.type == pygame.TEXTINPUT:
            for ch in event.text:
                if ch in self.ALLOWED and len(self.value) < self.max_len:
                    self.value += ch
            return True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.value = self.value[:-1]
            elif event.key in (pygame.K_RETURN, pygame.K_ESCAPE, pygame.K_TAB):
                self.focused = False
            return True
        return False

    def draw(self, ui, surf, rect):
        rect = pygame.Rect(rect)
        if ui.pressed:
            self.focused = ui.hover(rect)
        rrect(surf, T.PANEL if self.focused else T.PANEL_2, rect, 6)
        rrect(surf, T.ACCENT if self.focused else T.BORDER, rect, 6, 1)
        font = Fonts.get(14)
        shown = self.value or self.placeholder
        color = T.TEXT if self.value else T.TEXT_FAINT
        r = text(surf, text_fit(shown, font, rect.w - px(20)), font, color, (rect.x + px(10), rect.centery), "midleft")
        if self.focused and (pygame.time.get_ticks() // 500) % 2 == 0:
            x = r.right + 1 if self.value else rect.x + px(10)
            pygame.draw.line(surf, T.TEXT, (x, rect.centery - px(8)), (x, rect.centery + px(8)), max(1, px(1)))


def ease_out(t):
    return 1 - (1 - t) ** 3


def pulse(period_ms=900):
    return 0.5 + 0.5 * math.sin(pygame.time.get_ticks() / period_ms * 2 * math.pi)
