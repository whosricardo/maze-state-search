# [IA] Claude Code (Opus 5.5) – interface pygame: paleta, fontes, escala de DPI e metadados dos símbolos
import pygame

# ---------------------------------------------------------------- escala (DPI)
SCALE = 1.0


def set_scale(value):
    global SCALE
    SCALE = max(1.0, min(2.5, float(value)))


def px(value):
    """Converte um tamanho "lógico" (pensado para 100% de zoom) em pixels reais."""
    return int(round(value * SCALE))


# ---------------------------------------------------------------- cores da UI
BG = (20, 20, 24)
PANEL = (30, 30, 35)
PANEL_2 = (40, 40, 47)
PANEL_3 = (52, 52, 61)
BORDER = (62, 62, 72)
TEXT = (238, 238, 242)
TEXT_DIM = (165, 165, 178)
TEXT_FAINT = (112, 112, 124)
ACCENT = (255, 102, 0)          # laranja CESAR
ACCENT_HOVER = (255, 133, 51)
ACCENT_DARK = (120, 52, 10)
OK = (102, 187, 106)
WARN = (255, 193, 7)
ERR = (239, 83, 80)
INFO = (79, 195, 247)

# ---------------------------------------------------------------- cores dos tiles
GRID_LINE = (205, 200, 190)
TILE = {
    '#': (58, 58, 66),
    '.': (247, 244, 237),
    'S': (129, 199, 132),
    'G': (255, 183, 110),
    ',': (196, 160, 104),
    '~': (120, 172, 214),
    'key': (255, 232, 150),
    'door': (149, 117, 205),
    'door_open': (226, 216, 247),
    'conveyor': (214, 222, 232),
    '+': (200, 236, 190),
    '+used': (236, 238, 230),
    '*': (178, 229, 245),
}

# cor do percurso por camada (conjunto de chaves). A ordem segue o nº de chaves.
LAYER_COLORS = [
    (229, 57, 53), (30, 136, 229), (67, 160, 71), (142, 36, 170),
    (245, 124, 0), (0, 151, 167), (216, 27, 96), (93, 64, 55),
    (124, 179, 66), (57, 73, 171), (255, 179, 0), (0, 121, 107),
    (94, 53, 177), (192, 202, 51), (244, 81, 30), (84, 110, 122),
]

HEAT_STOPS = [
    (255, 245, 157),
    (255, 183, 77),
    (239, 83, 80),
    (123, 31, 162),
]


def lerp(a, b, t):
    return a + (b - a) * t


def lerp_color(c1, c2, t):
    return tuple(int(lerp(c1[i], c2[i], t)) for i in range(3))


def heat_color(t):
    t = max(0.0, min(1.0, t))
    span = len(HEAT_STOPS) - 1
    idx = min(int(t * span), span - 1)
    local = t * span - idx
    return lerp_color(HEAT_STOPS[idx], HEAT_STOPS[idx + 1], local)


def with_alpha(color, alpha):
    return (color[0], color[1], color[2], int(alpha))


# ---------------------------------------------------------------- símbolos
SYMBOL_INFO = {
    '#': ("Parede", "—"),
    '.': ("Chão", "1"),
    'S': ("Início", "1"),
    'G': ("Saída", "1"),
    ',': ("Lama", "3"),
    '~': ("Água", "5"),
    'a': ("Chave a", "1"),
    'b': ("Chave b", "1"),
    'c': ("Chave c", "1"),
    'd': ("Chave d", "1"),
    'A': ("Porta A", "1"),
    'B': ("Porta B", "1"),
    'C': ("Porta C", "1"),
    'D': ("Porta D", "1"),
    '>': ("Esteira →", "1"),
    '<': ("Esteira ←", "1"),
    '^': ("Esteira ↑", "1"),
    'v': ("Esteira ↓", "1"),
    '+': ("Bônus", "−4 / 1"),
    '*': ("Fonte", "−2"),
}

PALETTE_ORDER = [
    '#', '.', 'S', 'G', ',', '~',
    'a', 'A', 'b', 'B', 'c', 'C', 'd', 'D',
    '>', '<', '^', 'v', '+', '*',
]


# ---------------------------------------------------------------- fontes
class Fonts:
    _cache = {}

    SANS = "segoeui,helveticaneue,arial,dejavusans"
    MONO = "consolas,cascadiamono,couriernew,dejavusansmono"

    @classmethod
    def get(cls, size, bold=False, mono=False):
        real = max(6, px(size))
        key = (real, bold, mono)
        if key not in cls._cache:
            names = cls.MONO if mono else cls.SANS
            cls._cache[key] = pygame.font.SysFont(names, real, bold=bold)
        return cls._cache[key]

    @classmethod
    def raw(cls, real_size, bold=False):
        """Fonte com tamanho já em pixels reais (usada dentro dos tiles)."""
        real = max(6, int(real_size))
        key = ("raw", real, bold)
        if key not in cls._cache:
            cls._cache[key] = pygame.font.SysFont(cls.SANS, real, bold=bold)
        return cls._cache[key]
