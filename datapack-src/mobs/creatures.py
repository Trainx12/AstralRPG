# -*- coding: utf-8 -*-
"""
Las 17 criaturas de AstralRPG, copiadas de las imagenes de referencia.
Frente = norte (-Z). 16 unidades = 1 bloque. Altura del piso = 0.

Caras (calcos pintados): y=0 es arriba.
  norte: x=0 es el lado +X | este: x=0 es el lado +Z (atras) | oeste/sur se espejan solos (quedan simetricos)
  arriba: x=0 es -X, y=0 es -Z (adelante)

Lo que en la referencia sobresale (ojos, cejas, dientes, anillos, plumas, rejas, vendas, correas...) va como
piezas en relieve, no pintado.

Monturas: cada una tiene
  - un hueso 'silla' (montura, correas, hebillas) que se oculta hasta que el jugador le pone una montura;
  - un hueso 'p_seat' (asiento de BetterModel) donde se sienta el jugador y desde donde la maneja.
"""
from bbmodel import Model, swing


# ------------------------------------------------------------------ ayudas
def merge(*dicts):
    out = {}
    for d in dicts:
        for k, v in d.items():
            out.setdefault(k, {}).update(v)
    return out


def walk4(legs, amp=30, speed=1.5):
    """legs: [del_izq, del_der, tras_izq, tras_der] -> trote diagonal."""
    return {b: {"rotation": (swing(amp, speed, 0 if i in (0, 3) else 180), 0, 0)} for i, b in enumerate(legs)}


def border(w, h, col):
    return [(0, 0, w, 1, col), (0, h - 1, w, 1, col), (0, 0, 1, h, col), (w - 1, 0, 1, h, col)]


def box(m, bone, a, b, col, dec=None, pat=None):
    m.cube(bone, a, b, col, dec, pat=pat)


def mirror(m, bone, a, b, col, dec=None, pat=None):
    """Pieza y su copia del otro lado (espejo en X)."""
    m.cube(bone, a, b, col, dec, pat=pat)
    m.cube(bone, (-b[0], a[1], a[2]), (-a[0], b[1], b[2]), col, dec, pat=pat)


def eye_front(m, bone, x0, x1, y0, y1, z, iris, pupil="#111111", white=None, glow=None):
    """Ojo saltado que mira al frente, en la superficie z. Se hace del lado +X y su espejo."""
    if white:
        mirror(m, bone, (x0 - 0.4, y0 - 0.3, z - 0.4), (x1 + 0.4, y1 + 0.3, z), white)
        z -= 0.4
    mirror(m, bone, (x0, y0, z - 0.5), (x1, y1, z), iris, {"north": [(0, 0, 1, 1, glow or "#ffffff")]})
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    if pupil:
        mirror(m, bone, (cx - 0.5, cy - 0.6, z - 0.75), (cx + 0.4, cy + 0.5, z - 0.5), pupil)


def eye_side(m, bone, x, y0, y1, z0, z1, iris, pupil="#111111", white=None):
    """Ojo saltado al costado (superficie x>0) y su espejo."""
    if white:
        mirror(m, bone, (x, y0 - 0.4, z0 - 0.4), (x + 0.4, y1 + 0.4, z1 + 0.4), white)
        x += 0.4
    mirror(m, bone, (x, y0, z0), (x + 0.5, y1, z1), iris, {"east": [(0, 0, 1, 1, "#ffffff")]})
    cy, cz = (y0 + y1) / 2, (z0 + z1) / 2
    if pupil:
        mirror(m, bone, (x + 0.5, cy - 0.6, cz - 0.6), (x + 0.75, cy + 0.5, cz + 0.4), pupil)


def saddle(m, parent, cx, y, z0, z1, w, strap=6, col="#c0602a", trim="#6a3216", buckle="#e8c24a", horn=True):
    """Montura: asiento acolchado, respaldo, cabezal, cinchas con hebilla, estribos y manta con borde."""
    zm = (z0 + z1) / 2
    m.bone("silla", (cx, y, zm), parent)
    dz = z1 - z0
    m.cube("silla", (cx - w / 2 - 0.6, y - 0.4, z0 - 0.6), (cx + w / 2 + 0.6, y + 0.4, z1 + 0.6), trim,
           {"up": border(int(w + 1.2), int(dz + 1.2), buckle)})                                               # manta con borde
    m.cube("silla", (cx - w / 2, y + 0.4, z0), (cx + w / 2, y + 1.6, z1), col,
           {"up": border(int(w), int(dz), trim)}, pat="cloth")                                                 # asiento
    for k in range(1, int(dz) - 1, 2):                                                                          # acolchado
        m.cube("silla", (cx - w / 2 + 1, y + 1.6, z0 + k), (cx + w / 2 - 1, y + 1.9, z0 + k + 0.5), "#d87838")
    m.cube("silla", (cx - w / 2, y + 1.6, z1 - 1.5), (cx + w / 2, y + 4, z1), col,
           {"north": [(0, 0, int(w), 1, trim)], "south": border(int(w), 3, trim)})                           # respaldo
    m.cube("silla", (cx - w / 2 - 0.3, y + 3.7, z1 - 1.8), (cx + w / 2 + 0.3, y + 4.3, z1 + 0.3), trim)       # borde respaldo
    if horn:
        m.cube("silla", (cx - 1, y + 1.6, z0), (cx + 1, y + 4, z0 + 1.5), trim)
        m.cube("silla", (cx - 1.4, y + 4, z0 - 0.3), (cx + 1.4, y + 4.8, z0 + 1.8), buckle)                   # pomo
    for s in (1, -1):
        xa, xb = sorted((cx + s * w / 2, cx + s * (w / 2 + 0.6)))
        m.cube("silla", (xa, y - strap, zm - 1), (xb, y + 1, zm + 1), trim)                                     # cincha
        xa, xb = sorted((cx + s * (w / 2 + 0.6), cx + s * (w / 2 + 1.0)))
        m.cube("silla", (xa, y - strap / 2 - 1, zm - 1.3), (xb, y - strap / 2 + 1, zm + 1.3), buckle,
               {"east": [(1, 1, 1, 1, trim)]})                                                                  # hebilla
        xa, xb = sorted((cx + s * (w / 2 + 0.6), cx + s * (w / 2 + 1.2)))
        m.cube("silla", (xa, y - 3, z0 + 1), (xb, y + 0.5, z0 + 1.6), trim)                                   # correa estribo
        xa, xb = sorted((cx + s * (w / 2 + 0.4), cx + s * (w / 2 + 2.0)))
        m.cube("silla", (xa, y - 4, z0 + 0.5), (xb, y - 3, z0 + 2.1), "#9aa0a8")                              # estribo
        xa, xb = sorted((cx + s * (w / 2 + 0.6), cx + s * (w / 2 + 1.0)))
        m.cube("silla", (xa, y - 1.5, z1 - 2), (xb, y + 1, z1 - 0.5), buckle)                                 # anilla trasera
    # asiento de BetterModel (queda escondido adentro del cuerpo)
    m.bone("p_seat", (cx, y + 1, zm), parent)
    m.cube("p_seat", (cx - 1, y - 3, zm - 1), (cx + 1, y - 1, zm + 1), col)


def reins(m, bone, x, y, z0, z1, col="#7a3a1a", ring="#e8c24a"):
    """Riendas: dos tiras desde la boca hasta la montura, con argolla en la boca."""
    mirror(m, bone, (x - 0.3, y - 0.3, z0), (x + 0.3, y + 0.3, z1), col)
    mirror(m, bone, (x - 0.5, y - 0.8, z0 - 0.5), (x + 0.5, y + 0.8, z0 + 0.5), ring)


# ------------------------------------------------------------------ 1 mapache
def mapache():
    m = Model("astral_mapache")
    m.bone("body", (0, 8, 0))
    m.cube("body", (-4, 4, -6), (4, 11, 7), "#8a6e5a",
           {"down": [(1, 1, 6, 11, "#cdb89e")], "east": [(0, 5, 13, 2, "#a88c74")]}, pat="fur")
    m.cube("body", (-3.5, 4.5, -7), (3.5, 10, -6), "#9a7e68", pat="fur")                                   # pecho
    for x0, y0, y1 in ((-2.5, 4.2, 6.5), (-0.8, 4.5, 7.5), (0.9, 4.2, 6.8)):                                # mechones del pecho
        box(m, "body", (x0, y0, -7.5), (x0 + 1.6, y1, -7), "#d8c6aa", pat="fur")
    for z in (-4, 0, 4):                                                                                    # lomo rayado
        box(m, "body", (-1.2, 11, z), (1.2, 11.5, z + 2), "#6e5444", pat="fur")
    for z in (-5, -1, 3):                                                                                   # mechones del lomo a los lados
        mirror(m, "body", (4, 8, z), (4.4, 10.5, z + 1.5), "#7a604e", pat="fur")
    m.bone("head", (0, 9, -7), "body")
    m.cube("head", (-4.5, 6, -13), (4.5, 13, -7), "#9a7e68",
           {"north": [(0, 5, 9, 2, "#e8dccb"), (4, 0, 1, 4, "#e8dccb")], "up": [(3, 0, 3, 6, "#6e5444")]}, pat="fur")
    box(m, "head", (-4.5, 9, -13.3), (4.5, 11, -13), "#3a2e28")                                             # antifaz
    eye_front(m, "head", 0.8, 2.6, 9.3, 10.8, -13.3, "#1a1414", pupil=None)
    mirror(m, "head", (0.6, 11, -13.5), (3.0, 11.8, -13), "#e8dccb")                                         # cejas blancas
    m.cube("head", (-2, 6, -15), (2, 9, -13), "#e2d4c0", {"north": [(1, 2, 2, 1, "#8a6a5a")]})               # hocico
    box(m, "head", (-1, 8.4, -15.5), (1, 9.4, -14.6), "#1d1d1d", {"north": [(0, 0, 1, 1, "#5a5a5a")]})        # nariz
    mirror(m, "head", (4.5, 6.5, -11), (5.6, 9.5, -8), "#e2d4c0", pat="fur")                                # cachetes
    mirror(m, "head", (5.6, 7, -10.5), (6.1, 8.5, -9), "#e2d4c0")                                           # punta del cachete
    mirror(m, "head", (2.2, 13, -10), (4.6, 15.5, -8.5), "#6b5040")                                         # orejas
    mirror(m, "head", (2.7, 13.2, -10.4), (4.1, 15, -10), "#e0a0a0")                                         # adentro rosa
    mirror(m, "head", (2.6, 15.5, -10), (4.2, 16.1, -9), "#3a2e28")                                         # punta
    box(m, "head", (-1.5, 13, -10), (1.5, 14, -8), "#6e5444", pat="fur")                                     # copete
    m.bone("tail", (0, 9.5, 7), "body", rotation=(-20, 0, 0))
    m.cube("tail", (-2, 7.5, 7), (2, 11.5, 19), "#8a6e5a", pat="fur")
    for z in (8, 12, 16):                                                                                   # anillos en relieve
        box(m, "tail", (-2.3, 7.2, z), (2.3, 11.8, z + 2), "#3a2e28", pat="fur")
    m.cube("tail", (-1.6, 8, 19), (1.6, 11, 21.5), "#2e241e", pat="fur")
    box(m, "tail", (-0.8, 8.6, 21.5), (0.8, 10.4, 22.5), "#2e241e")
    legs = []
    for n, x, z in (("leg_fl", -2.5, -3.5), ("leg_fr", 2.5, -3.5), ("leg_bl", -2.5, 4.5), ("leg_br", 2.5, 4.5)):
        m.bone(n, (x, 5, z), "body")
        m.cube(n, (x - 1.3, 1, z - 1.3), (x + 1.3, 5, z + 1.3), "#5a463a", pat="fur")
        m.cube(n, (x - 1.5, 0, z - 1.8), (x + 1.5, 1, z + 1.3), "#2e241e")
        for dx in (-1.1, -0.25, 0.6):                                                                       # garritas
            box(m, n, (x + dx, 0, z - 2.3), (x + dx + 0.5, 0.6, z - 1.8), "#d8d0c0")
        legs.append(n)
    m.anim("walk", 1, merge(walk4(legs, 35, 2), {"tail": {"rotation": (-20, swing(15, 2), 0)},
                                                 "head": {"rotation": (swing(3, 2), 0, 0)}}))
    m.anim("idle", 3, {"tail": {"rotation": (-20, swing(10, 0.33), 0)}, "head": {"rotation": (swing(3, 0.33), swing(8, 0.2), 0)}})
    return m


# ------------------------------------------------------------------ 2 pinguino de cristal
def pinguino():
    m = Model("astral_pinguino")
    m.bone("body", (0, 2, 0))
    m.cube("body", (-4, 2, -3.5), (4, 12, 3.5), "#78b6e6", {"south": [(3, 6, 2, 3, "#5a9fd6")]}, pat="feather")
    box(m, "body", (-3, 3, -3.9), (3, 11, -3.5), "#e4f4ff", pat="feather")                                   # panza
    for y in (4.5, 6.5, 8.5):                                                                               # plumas en V de la panza
        box(m, "body", (-2.5, y, -4.2), (-0.5, y + 0.6, -3.9), "#b8dcf4")
        box(m, "body", (0.5, y, -4.2), (2.5, y + 0.6, -3.9), "#b8dcf4")
        box(m, "body", (-0.5, y - 0.6, -4.2), (0.5, y, -3.9), "#b8dcf4")
    for k, x in enumerate((-1.8, 0.2)):                                                                     # colita de plumas
        box(m, "body", (x - 0.4, 2, 3.5), (x + 1.6, 4 - k * 0.5, 6.5), "#4a88c0", pat="feather")
    for x0, x1 in ((-3.5, -0.5), (0.5, 3.5)):                                                               # patas con dedos y unas
        m.cube("body", (x0, 0, -3.5), (x1, 1.5, 0), "#e8752a", pat="scale")
        for k in range(3):
            box(m, "body", (x0 + k * 1.1, 0, -4.4), (x0 + k * 1.1 + 0.8, 0.8, -3.5), "#e8752a")
            box(m, "body", (x0 + k * 1.1 + 0.15, 0, -4.8), (x0 + k * 1.1 + 0.65, 0.5, -4.4), "#5a2a10")
    m.bone("head", (0, 12, 0), "body")
    m.cube("head", (-4.5, 12, -4), (4.5, 19, 4), "#6aaee0", {"up": [(2, 2, 5, 4, "#4a88c0")]}, pat="feather")
    box(m, "head", (-4.5, 18, -4.3), (4.5, 19, -4), "#3f7cc0")                                               # frente oscura
    box(m, "head", (-1.5, 17.4, -4.6), (1.5, 18.6, -4.3), "#3f7cc0")                                         # pico de la frente (ceno)
    eye_front(m, "head", 1.4, 3.6, 14.2, 16.8, -4, "#111111", pupil="#2a2a40", white="#ffffff")
    mirror(m, "head", (4.5, 13, -3), (5.1, 16, -0.5), "#8ac8f0", pat="feather")                              # cachetes de plumas
    box(m, "head", (-1.5, 13.8, -6.2), (1.5, 15.6, -4), "#ff8a3a")                                           # pico
    box(m, "head", (-0.8, 13.2, -6.8), (0.8, 15.2, -6.2), "#d8601a")                                         # gancho
    box(m, "head", (-1, 12.6, -5.6), (1, 13.8, -4), "#d8601a")                                               # pico de abajo
    for k, (dx, dy, dz) in enumerate(((3.0, 19, -1.5), (3.8, 20.5, -0.8), (4.6, 22, 0), (5.2, 23.3, 0.6))):  # penachos dorados
        sz = 1.4 if k < 3 else 0.9
        mirror(m, "head", (dx - sz, dy, dz - 1), (dx, dy + 1.6, dz + 1), "#f2c94c" if k % 2 == 0 else "#e0b030",
               {"north": [(0, 0, 1, 1, "#fff0a0")]})
    mirror(m, "head", (2, 19, -0.5), (3.2, 20, 1.5), "#c89a2a")                                              # base del penacho
    for n, s in (("flip_l", 1), ("flip_r", -1)):
        m.bone(n, (4 * s, 11, 0), "body")
        a, b = sorted((4 * s, 5.2 * s))
        m.cube(n, (a, 4, -2), (b, 11, 2), "#3f7cc0", pat="feather")
        a, b = sorted((5.2 * s, 5.6 * s))
        for y in (4, 6.5, 9):                                                                                # plumas del borde
            m.cube(n, (a, y, -1.6), (b, y + 1.8, 1.6), "#8ac8f0")
    # cristal rosa en la aleta (con facetas y puntas)
    m.bone("cristal", (-7, 7, -2), "flip_r")
    m.cube("cristal", (-9, 5, -4), (-5.5, 9.5, -0.5), "#ff9fc8",
           {"north": [(0, 0, 1, 1, "#ffffff"), (1, 1, 1, 1, "#ffe0f0"), (2, 3, 2, 2, "#d86aa0")], "up": [(1, 1, 1, 1, "#ffffff")]})
    m.cube("cristal", (-8.3, 9.5, -3.3), (-6.2, 11, -1.2), "#ffc0dc", {"up": [(0, 0, 1, 1, "#ffffff")]})
    m.cube("cristal", (-7.7, 11, -2.7), (-6.8, 11.8, -1.8), "#ffe0f0")
    m.cube("cristal", (-8.3, 3.8, -3.3), (-6.2, 5, -1.2), "#d86aa0")
    m.cube("cristal", (-9.6, 6, -3.3), (-9, 8.5, -1.2), "#ffb0d4")                                          # faceta saliente
    m.cube("cristal", (-7.5, 6, -4.4), (-6, 8, -4), "#ffffff")                                              # brillo
    m.anim("walk", 1, {"body": {"rotation": (0, 0, swing(8, 2))}, "flip_l": {"rotation": (0, 0, swing(-20, 2))},
                       "flip_r": {"rotation": (0, 0, swing(10, 2))}, "head": {"rotation": (0, 0, swing(-5, 2))}})
    m.anim("idle", 2, {"head": {"rotation": (0, swing(10, 0.5), 0)}, "cristal": {"rotation": (0, swing(12, 0.5), 0)}})
    return m


# ------------------------------------------------------------------ 3 espantapajaros (vuela)
def espantapajaros():
    m = Model("astral_espantapajaros")
    m.bone("body", (0, 12, 0))
    m.cube("body", (-3.5, 9, -2), (3.5, 17, 2), "#c9a23c", pat="straw")
    box(m, "body", (-0.5, 12, -2.4), (2.5, 15, -2), "#7a3fb0", {"north": [(0, 0, 3, 1, "#9a5fd0"), (1, 1, 1, 1, "#e8c24a")]}, pat="cloth")  # parche
    for y in (12.2, 14.6):                                                                                 # puntadas del parche
        box(m, "body", (2.5, y, -2.3), (3.0, y + 0.3, -2), "#e8c24a")
    box(m, "body", (-3, 13.5, -2.4), (-1.2, 15.5, -2), "#5a2f8a", pat="cloth")
    box(m, "body", (-2, 11.5, 2), (2, 14.5, 2.4), "#7a3fb0", pat="cloth")                                   # parche de atras
    box(m, "body", (-3.8, 10.6, -2.3), (3.8, 11.6, 2.3), "#7a5a2a", pat="wood")                             # cinturon de soga
    box(m, "body", (-0.8, 9.4, -2.8), (0.8, 11.9, -2.2), "#8a6a3a")                                         # nudo
    box(m, "body", (-0.4, 8.2, -2.7), (0.4, 9.4, -2.4), "#8a6a3a")
    for k, x in enumerate((-3.5, -2.2, -0.9, 0.4, 1.7, 3.0)):                                             # falda de paja
        ln = 3 + (k * 7) % 3
        for z0 in (-2.2, 1.4):
            m.cube("body", (x, 9 - ln, z0), (x + 0.9, 9, z0 + 0.8), "#e3c04a" if k % 2 else "#c99a2a",
                   {"north": [(0, ln - 1, 1, 1, "#c86ad8")]}, pat="straw")
    for n, x in (("leg_l", 1.6), ("leg_r", -1.6)):                                                          # piernas colgando
        m.bone(n, (x, 9, 0), "body")
        m.cube(n, (x - 1, 2, -1), (x + 1, 9, 1), "#5a3f7a", pat="cloth")
        for y in (7, 4.5):
            m.cube(n, (x - 1.2, y, -1.2), (x + 1.2, y + 0.8, 1.2), "#c99a2a")                              # ataduras
        for dx in (-0.9, 0.1):
            m.cube(n, (x + dx - 0.2, -1, -0.6), (x + dx + 0.6, 2, 0.4), "#e3c04a", {"north": [(0, 2, 1, 1, "#e48fd0")]}, pat="straw")
    for x, z in ((-1.6, -1.2), (0.8, -1.2), (-1.6, 0.6), (0.8, 0.6), (-0.4, -1.5)):                        # paja del cuello
        box(m, "body", (x, 16.5, z), (x + 0.8, 18.5, z + 0.7), "#e8c850", pat="straw")
    # cabeza de calabaza tallada
    m.bone("head", (0, 18, 0), "body")
    carve = [(1, 2, 3, 2, "#5a1f8a"), (6, 2, 3, 2, "#5a1f8a"), (2, 2, 1, 1, "#e8a0ff"), (7, 2, 1, 1, "#e8a0ff"),
             (1, 3, 1, 1, "#b04af0"), (3, 3, 1, 1, "#b04af0"), (6, 3, 1, 1, "#b04af0"), (8, 3, 1, 1, "#b04af0"),
             (4, 4, 2, 1, "#5a1f8a"), (1, 6, 8, 2, "#5a1f8a"), (3, 6, 1, 1, "#d070f0"), (5, 7, 1, 1, "#d070f0")]
    m.cube("head", (-5, 18, -5), (5, 27, 5), "#f0a01c", {"north": carve})
    for z in (-3.5, -1.5, 1.5, 3.5):                                                                        # gajos en relieve
        mirror(m, "head", (5, 18.4, z - 0.5), (5.5, 26.6, z + 0.5), "#d8761a")
        box(m, "head", (z - 0.5, 18.4, 5), (z + 0.5, 26.6, 5.5), "#d8761a")
    mirror(m, "head", (4.3, 18.4, -5.5), (5.2, 26.6, -5), "#d8761a")                                         # gajos del frente (bordes)
    mirror(m, "head", (0.8, 25, -5.6), (4.2, 25.8, -5), "#f6b030")                                           # ceno sobre los ojos
    mirror(m, "head", (3.0, 25.8, -5.6), (4.4, 26.5, -5), "#f6b030")
    mirror(m, "head", (0.8, 22.4, -5.4), (4.2, 23, -5), "#d8761a")                                           # borde de abajo del ojo
    box(m, "head", (-4.4, 21, -5.6), (4.4, 21.6, -5), "#f6b030")                                             # labio de arriba
    box(m, "head", (-4.4, 18.4, -5.6), (4.4, 19, -5), "#d8761a")                                             # labio de abajo
    for x in (2, -1.5):                                                                                      # dientes de arriba
        box(m, "head", (x, 20, -5.6), (x + 1, 21, -5), "#f6b030")
    for x in (-3, 0.5, 3):                                                                                   # dientes de abajo
        box(m, "head", (x, 19, -5.6), (x + 1, 20, -5), "#f6b030")
    for x, z in ((-5.5, -3), (4.5, -3), (-5.5, 2), (4.5, 2), (-2, -5.6), (1, -5.6), (-4, -5.6), (3, -5.6)):  # paja bajo el sombrero
        m.cube("head", (x, 24.5, z), (x + 1, 27, z + 1), "#e8c850", pat="straw")
    # sombrero de paja con cinta y paja suelta en el ala
    m.cube("head", (-7.5, 26.5, -7.5), (7.5, 27.5, 7.5), "#e0b84a", {"up": border(15, 15, "#b8902a")}, pat="straw")
    m.cube("head", (-4, 27.5, -4), (4, 31.5, 4), "#d8b040", {"up": [(2, 2, 4, 4, "#c09a30")]}, pat="straw")
    box(m, "head", (-3, 31.5, -3), (3, 32, 3), "#c09a30", pat="straw")                                       # copa
    m.cube("head", (-4.3, 28.5, -4.3), (4.3, 29.7, 4.3), "#5a5f6e")                                          # cinta
    box(m, "head", (2.5, 28.2, -4.6), (4.6, 30, -4.3), "#7a3fb0")                                            # mono de la cinta
    for x, z, ln in ((-7, -7.4, 2), (-3, -7.4, 1.5), (5, -7.4, 2.5), (7, 3, 2), (-7.4, 1, 1.5), (2, 7, 2)):  # paja colgando del ala
        box(m, "head", (x, 26.5 - ln, z), (x + 0.6, 26.5, z + 0.6), "#e8c850")
    # brazos de paja abiertos con manos de mechones
    for n, s in (("arm_l", 1), ("arm_r", -1)):
        m.bone(n, (3.5 * s, 16, 0), "body")
        a, b = sorted((3.5 * s, 10 * s))
        m.cube(n, (a, 14, -1), (b, 16, 1), "#c9a23c", pat="straw")
        for xx in (5.5, 8.5):                                                                                # ataduras
            a, b = sorted((xx * s, (xx + 0.8) * s))
            m.cube(n, (a, 13.8, -1.2), (b, 16.2, 1.2), "#7a5a2a")
        for dy, dz in ((-1, -0.8), (0, 0.3), (1.2, -0.3), (0.4, 0.9)):
            a, b = sorted((10 * s, 12.5 * s))
            m.cube(n, (a, 14.5 + dy * 0.8, dz - 0.4), (b, 15.3 + dy * 0.8, dz + 0.4), "#e3c04a",
                   {"north": [(0, 0, 1, 1, "#e48fd0")], "up": [(0, 0, 1, 1, "#e48fd0")]})
        for xx in (4.5, 7):                                                                                  # paja suelta de la manga
            a, b = sorted((xx * s, (xx + 0.7) * s))
            m.cube(n, (a, 12, -0.3), (b, 14, 0.4), "#e8c850")
    # hoces violetas (una en cada mano)
    for n, s in (("hoz_l", 1), ("hoz_r", -1)):
        m.bone(n, (11 * s, 15, 0), "arm_l" if s > 0 else "arm_r")
        x = 11 * s
        m.cube(n, (x - 0.5, 8, -0.5), (x + 0.5, 19, 0.5), "#6a2f9a", pat="wood")
        for y in (10, 13.5):                                                                                 # empunadura con vueltas
            m.cube(n, (x - 0.7, y, -0.7), (x + 0.7, y + 0.8, 0.7), "#e8c24a")
        m.cube(n, (x - 0.7, 7.3, -0.7), (x + 0.7, 8, 0.7), "#3a1a5a")                                       # pomo
        blade = [((-1, 19, -1), (1, 21, 0.5)), ((-1, 20, -4), (1, 21.5, -1)), ((-1, 19.5, -6.5), (1, 21, -4)),
                 ((-1, 17.5, -8), (1, 20, -6.5)), ((-1, 15.5, -8.5), (1, 17.5, -7.5))]
        for (fx, fy, fz), (tx, ty, tz) in blade:
            m.cube(n, (x + fx * 0.4, fy, fz), (x + tx * 0.4, ty, tz), "#d070f0", {"up": [(0, 0, 1, 1, "#f8d8ff")]})
        m.cube(n, (x - 0.15, 18.8, -7.7), (x + 0.15, 20.2, -1), "#f8d8ff")                                   # filo brillante
    hover = {"body": {"position": (0, swing(1.2, 0.5), 0), "rotation": (swing(3, 0.5), 0, 0)},
             "leg_l": {"rotation": (swing(14, 0.7), 0, swing(4, 0.5))}, "leg_r": {"rotation": (swing(-14, 0.7), 0, swing(-4, 0.5))},
             "arm_l": {"rotation": (0, 0, swing(6, 0.5))}, "arm_r": {"rotation": (0, 0, swing(-6, 0.5))},
             "head": {"rotation": (0, 0, swing(6, 0.33))}, "hoz_l": {"rotation": (swing(10, 0.5), 0, 0)},
             "hoz_r": {"rotation": (swing(-10, 0.5), 0, 0)}}
    for a in ("idle", "walk", "idle_fly", "walk_fly"):
        m.anim(a, 2, hover)
    m.anim("attack", 0.6, merge(hover, {"arm_r": {"rotation": (swing(-70, 1.6), 0, -20)}, "hoz_r": {"rotation": (swing(-60, 1.6), 0, 0)},
                                        "arm_l": {"rotation": (swing(-70, 1.6, 90), 0, 20)}}), loop="once")
    return m


# ------------------------------------------------------------------ 4 abejorro sombrio (vuela)
def abejorro():
    m = Model("astral_abejorro")
    m.bone("body", (0, 10, 0))
    m.cube("body", (-4, 7, -3), (4, 13, 4), "#23283a", pat="fur")                                         # torax
    for x, z in ((-3, -2), (1, -1.5), (-1, 1.5), (2, 2)):                                                  # pelusa del torax
        box(m, "body", (x, 13, z), (x + 1.5, 13.8, z + 1.5), "#2e3550", pat="fur")
    mirror(m, "body", (4, 9, -2), (4.5, 12, 3), "#2e3550", pat="fur")
    m.cube("body", (-5, 5, 4), (5, 13, 14), "#1e2232", {"south": [(2, 2, 6, 4, "#151821")]}, pat="chitin")  # abdomen
    for z in (5.5, 8.5, 11.5):                                                                             # anillos naranjas en relieve
        box(m, "body", (-5.3, 4.7, z), (5.3, 13.3, z + 1.2), "#e0a83a", pat="chitin")
    box(m, "body", (-4.2, 5.8, 14), (4.2, 12.2, 14.6), "#1a1e2c")                                          # punta del abdomen
    m.cube("body", (-1, 7.5, 14.6), (1, 9.5, 17), "#151821")                                              # aguijon
    box(m, "body", (-0.4, 8.1, 17), (0.4, 8.9, 18.5), "#e0a83a")
    m.cube("body", (-3.5, 7, -8), (3.5, 13, -3), "#1b1f2d", pat="fur")                                     # cabeza
    box(m, "body", (-3.8, 7.5, -3.6), (3.8, 12.5, -2.6), "#2e3550", pat="fur")                              # cuello peludo
    eye_front(m, "body", 0.5, 3.4, 9, 12.2, -8, "#ffd34d", pupil="#c07a10", glow="#fff6c0")
    mirror(m, "body", (0.3, 12.2, -8.6), (3.6, 12.8, -7.8), "#151821")                                      # ceno
    mirror(m, "body", (0.6, 6, -9.5), (2, 7.5, -7.5), "#e0a83a")                                            # mandibulas
    mirror(m, "body", (0.3, 5.4, -9.5), (1, 6.2, -8.8), "#e0a83a")
    for n, s in (("ant_l", 1), ("ant_r", -1)):
        m.bone(n, (1.5 * s, 13, -7), "body")
        m.cube(n, (1.5 * s - 0.4, 13, -7.4), (1.5 * s + 0.4, 17, -6.6), "#151821")
        m.cube(n, (1.5 * s - 0.4, 16.6, -10), (1.5 * s + 0.4, 17.4, -7.4), "#151821")
        m.cube(n, (1.5 * s - 0.6, 16.4, -10.8), (1.5 * s + 0.6, 17.6, -10), "#e0a83a")
    for n, s in (("wing_l", 1), ("wing_r", -1)):
        m.bone(n, (3.5 * s, 13, 0), "body", rotation=(0, 0, 18 * s))
        a, b = sorted((3.5 * s, 15 * s))
        m.cube(n, (a, 13, -2), (b, 13.5, 8), "#2c3550", pat="membrane")
        a, b = sorted((3.5 * s, 15 * s))
        m.cube(n, (a, 13.5, -2.2), (b, 14, -1.2), "#e0a83a")                                              # nervadura del borde
        for xx, z1 in ((7, 7), (10.5, 7.5)):
            a, b = sorted((xx * s, (xx + 0.6) * s))
            m.cube(n, (a, 13.5, -1.2), (b, 13.8, z1), "#c88a2a")                                          # nervaduras
        a, b = sorted((14.4 * s, 15 * s))
        m.cube(n, (a, 13.5, -1.2), (b, 13.8, 8), "#e0a83a")
        a, b = sorted((3.5 * s, 11 * s))
        m.cube(n, (a, 12.6, 6), (b, 13, 12), "#323c5c", {"up": border(8, 6, "#e0a83a")}, pat="membrane")  # ala trasera
    for i, z in enumerate((-2, 1, 3.5)):                                                                   # patas con rodilla y pelos
        a, b = (3, 4)
        mirror(m, "body", (a, 4, z), (b, 7, z + 1), "#151821")
        mirror(m, "body", (3.6, 1, z + 0.5 + i * 0.5), (4.6, 4, z + 1.5 + i * 0.5), "#101219")
        mirror(m, "body", (4.6, 2, z + 0.7 + i * 0.5), (5.0, 2.6, z + 1.3 + i * 0.5), "#e0a83a")
    fly = {"wing_l": {"rotation": (0, 0, swing(35, 4, 0))}, "wing_r": {"rotation": (0, 0, swing(-35, 4, 0))},
           "body": {"position": (0, swing(1, 0.5), 0)}, "ant_l": {"rotation": (swing(8, 1), 0, 0)}, "ant_r": {"rotation": (swing(-8, 1), 0, 0)}}
    for a in ("idle", "walk", "idle_fly", "walk_fly"):
        m.anim(a, 1, fly)
    m.anim("attack", 0.5, merge(fly, {"body": {"rotation": (swing(-25, 2), 0, 0)}}), loop="once")
    return m


# ------------------------------------------------------------------ 5 arana amatista
def arana():
    m = Model("astral_arana")
    m.bone("body", (0, 6, 0))
    m.cube("body", (-6, 4, -4), (6, 10, 8), "#5e4e8c", pat="chitin")
    for s in (1, -1):                                                                                      # dos placas del caparazon
        a, b = sorted((0.3 * s, 6.6 * s))
        m.cube("body", (a, 9.5, -4.6), (b, 12, 8.6), "#8a7ab8", pat="chitin")
        for z in (-1.5, 2.5, 6.5):                                                                         # bordes de cada segmento
            a, b = sorted((0.5 * s, 6.4 * s))
            m.cube("body", (a, 12, z), (b, 12.5, z + 0.6), "#a898d8")
        a, b = sorted((6.6 * s, 7.0 * s))
        m.cube("body", (a, 9.8, -4.3), (b, 11.6, 8.3), "#6a5a98")                                         # labio de la placa
    box(m, "body", (-0.3, 11.5, -4.6), (0.3, 12.8, 8.6), "#3e2e6c")                                        # costura del medio
    for x, z, h in ((-2.5, 2, 3), (1.5, 4, 2), (-1, 6, 2.5), (3.5, 0, 1.8)):                              # cristales de amatista
        box(m, "body", (x, 12, z), (x + 1.2, 12 + h, z + 1.2), "#c890ff", {"north": [(0, 0, 1, 1, "#f0e0ff")]})
        box(m, "body", (x + 0.3, 12 + h, z + 0.3), (x + 0.9, 12.6 + h, z + 0.9), "#f0e0ff")
    m.cube("body", (-4, 3, -10), (4, 8, -4), "#6a5a98", {"up": [(2, 1, 4, 3, "#7a6aa8")]}, pat="chitin")
    box(m, "body", (-1, 5.2, -10.6), (1, 7.2, -10), "#e8c0ff", {"north": [(0, 0, 1, 1, "#ffffff")]})       # ojos grandes del medio
    eye_front(m, "body", 2, 3, 6, 7, -10, "#d8a0ff", pupil=None)                                           # ojos chicos
    eye_front(m, "body", 1.1, 2, 4.4, 5.3, -10, "#2a1e40", pupil=None, glow="#8a6ab8")
    mirror(m, "body", (0.5, 7.6, -10.4), (3.6, 8.3, -9.5), "#4e3e7c")                                       # ceja
    for s in (1, -1):                                                                                      # colmillos
        a, b = sorted((0.8 * s, 2.2 * s))
        m.cube("body", (a, 1.5, -10.6), (b, 3.5, -9.4), "#e8a0d0")
        a, b = sorted((1.1 * s, 1.9 * s))
        m.cube("body", (a, 0.7, -10.4), (b, 1.5, -9.8), "#5a1e40")
    box(m, "body", (-1.2, 5, 8), (1.2, 7, 9.5), "#4e3e7c")                                                 # hileras
    legs = []
    for i, z in enumerate((-3.5, -0.5, 2.5, 5.5)):
        for s, side in ((1, "l"), (-1, "r")):
            n = f"leg_{side}{i}"
            m.bone(n, (6 * s, 7, z), "body")
            a, b = sorted((6 * s, 11 * s))
            m.cube(n, (a, 7, z - 0.6), (b, 8.4, z + 0.6), "#5e4e8c", pat="chitin")                       # muslo
            for xx in (7.5, 9.5):                                                                          # pelos
                a, b = sorted((xx * s, (xx + 0.4) * s))
                m.cube(n, (a, 8.4, z - 0.2), (b, 9.2, z + 0.2), "#3e2e6c")
            a, b = sorted((10.5 * s, 12.5 * s))
            m.cube(n, (a, 6.5, z - 0.8), (b, 9.5, z + 0.8), "#7a6aa8")                                    # rodilla
            a, b = sorted((11.1 * s, 12 * s))
            m.cube(n, (a, 9.5, z - 0.4), (b, 10.3, z + 0.4), "#c890ff")                                   # punta de la rodilla
            a, b = sorted((11.8 * s, 13.2 * s))
            m.cube(n, (a, 1, z - 0.6), (b, 6.5, z + 0.6), "#4e3e7c", pat="chitin")                       # pierna
            a, b = sorted((12.2 * s, 13.6 * s))
            m.cube(n, (a, 0, z - 0.5), (b, 1, z + 0.5), "#2a1e40")                                        # punta
            legs.append((n, i, s))
    ch = {n: {"rotation": (0, swing(15, 2, 0 if (i + (s > 0)) % 2 else 180), swing(6, 2, 90 if (i + (s > 0)) % 2 else 270))} for n, i, s in legs}
    m.anim("walk", 1, ch)
    m.anim("idle", 2, {"body": {"position": (0, swing(0.3, 0.5), 0)}})
    m.anim("attack", 0.5, {"body": {"rotation": (swing(-12, 2), 0, 0)}}, loop="once")
    return m


# ------------------------------------------------------------------ 6 cara voladora
def cara():
    m = Model("astral_cara")
    m.bone("body", (0, 12, 0))
    m.cube("body", (-6, 10, -6), (6, 20, 6), "#b8405a", {"up": [(2, 2, 3, 3, "#d06078"), (7, 6, 3, 2, "#8c2e48")]}, pat="stone")
    box(m, "body", (-4, 14, -6.6), (4, 19, -6), "#e8f0d8", {"north": [(0, 0, 1, 1, "#c8c8b0"), (7, 4, 1, 1, "#c8c8b0")]})   # ojo
    box(m, "body", (-2.2, 14.3, -7.2), (2.2, 18.7, -6.6), "#3fb84a", {"north": [(0, 0, 1, 1, "#c8ffd0"), (3, 3, 1, 1, "#2a8a30")]})
    box(m, "body", (-1, 15.2, -7.6), (1, 17.8, -7.2), "#0d200f", {"north": [(0, 0, 1, 1, "#5aff6a")]})
    box(m, "body", (-5, 19, -6.9), (5, 20, -6), "#8c2e48")                                                  # ceno
    box(m, "body", (-4.5, 13.3, -6.5), (4.5, 14, -6), "#8c2e48")                                            # parpado de abajo
    for x, y0, y1 in ((4.6, 10.5, 13), (-5.2, 11, 14), (5, 15, 17.5)):                                      # venas en relieve
        box(m, "body", (x, y0, -6.3), (x + 0.6, y1, -6), "#7a2a40")
    for z0, y0 in ((-3, 12), (2, 15)):
        mirror(m, "body", (6, y0, z0), (6.3, y0 + 3, z0 + 0.6), "#7a2a40")
    box(m, "body", (-6.3, 9.8, -6.6), (6.3, 10.5, 6.3), "#9a3048")                                          # labio de arriba
    m.cube("body", (-5.5, 7.5, -5.5), (5.5, 10, 5.5), "#3a0c18")                                           # boca abierta
    for k in range(6):                                                                                      # dientes de arriba
        x = -5.5 + k * 2
        m.cube("body", (x, 8, -6.2), (x + 1, 10, -5.5), "#f2e6c8")
        mirror(m, "body", (5.5, 8, x), (6.2, 10, x + 1), "#f2e6c8")
    m.bone("jaw", (0, 8, 5), "body")
    m.cube("jaw", (-6, 3, -6), (6, 7.5, 6), "#a83c5a", pat="stone")
    box(m, "jaw", (-6.3, 7, -6.6), (6.3, 7.6, 6.3), "#9a3048")                                              # labio de abajo
    for k in range(6):                                                                                      # dientes de abajo
        x = -4.5 + k * 2
        m.cube("jaw", (x, 7.5, -6.2), (x + 1, 9, -5.5), "#f2e6c8")
    m.cube("jaw", (-2, 7, -8.5), (2, 8, -2), "#5ac85a", {"up": [(1, 0, 2, 1, "#3a9a3a")]})                  # lengua
    m.cube("jaw", (-1.5, 6.4, -9.2), (1.5, 7.6, -8.5), "#5ac85a")                                           # punta de la lengua
    for n, s in (("wing_l", 1), ("wing_r", -1)):                                                            # tentaculos ramificados
        m.bone(n, (3 * s, 20, 0), "body")
        for (x0, y0, x1, y1, col) in ((2.5, 20, 3.5, 25, "#8c2e48"), (3.5, 24, 8, 25, "#8c2e48"), (7, 25, 8, 29, "#8c2e48"),
                                      (8, 28, 11, 29, "#a83c5a"), (10, 26, 11, 28, "#a83c5a"), (4.5, 25, 5.5, 27, "#a83c5a"),
                                      (5.5, 26.5, 7, 27.5, "#a83c5a"), (2.5, 22, 1.5, 23, "#a83c5a"), (1.5, 23, 0.5, 25, "#a83c5a")):
            a, b = sorted((x0 * s, x1 * s))
            m.cube(n, (a, y0, -0.5), (b, y1, 0.5), col)
        a, b = sorted((10.2 * s, 11.2 * s))
        m.cube(n, (a, 25.3, -0.6), (b, 26.3, 0.6), "#e86a8a")                                             # puntas
        a, b = sorted((6.8 * s, 8.2 * s))
        m.cube(n, (a, 29, -0.6), (b, 29.8, 0.6), "#e86a8a")
    fly = {"wing_l": {"rotation": (0, 0, swing(15, 1))}, "wing_r": {"rotation": (0, 0, swing(-15, 1))},
           "body": {"position": (0, swing(1.5, 0.7), 0)}, "jaw": {"rotation": (swing(8, 0.7), 0, 0)}}
    for a in ("idle", "walk", "idle_fly", "walk_fly"):
        m.anim(a, 1, fly)
    m.anim("attack", 0.5, merge(fly, {"jaw": {"rotation": (swing(30, 4), 0, 0)}}), loop="once")
    return m


# ------------------------------------------------------------------ 7 lagarto (montura, nada)
def lagarto():
    m = Model("astral_lagarto")
    m.bone("body", (0, 9, 0))
    m.cube("body", (-6, 5, -8), (6, 12, 12), "#b7c24a", {"down": [(2, 0, 8, 20, "#e2e6a8")], "east": [(0, 5, 20, 2, "#e2e6a8")]}, pat="scale")
    for z in range(-6, 12, 3):                                                                             # escamas del lomo
        mirror(m, "body", (1.5, 12, z), (3, 13, z + 1.5), "#8a9a30")
        mirror(m, "body", (4, 11.6, z + 1), (5.2, 12.4, z + 2.2), "#9aaa38")
    for x, z in ((2, -5), (-4, 1), (3, 6), (-2, 9)):                                                      # manchas en relieve
        box(m, "body", (x, 12, z), (x + 1.8, 12.3, z + 1.8), "#8a9a30")
    m.bone("head", (0, 9, -8), "body")
    m.cube("head", (-5, 5, -17), (5, 11, -8), "#c8d15a", {"down": [(1, 1, 8, 7, "#e2e6a8")]}, pat="scale")
    mirror(m, "head", (2, 11, -15), (5, 13.5, -12), "#c8d15a", pat="scale")                                  # ojos saltones
    mirror(m, "head", (2.5, 11.5, -15.4), (4.5, 13.3, -15), "#ffffff", {"north": [(0, 0, 1, 1, "#e8e8e8")]})
    mirror(m, "head", (3.2, 11.8, -15.7), (4.0, 13, -15.4), "#111111")
    mirror(m, "head", (1.8, 13.5, -15.2), (5.2, 14.1, -12), "#9aaa38")                                       # parpado
    m.cube("head", (-4, 6, -25), (4, 9.5, -17), "#bfc95a", {"east": [(0, 2, 8, 1, "#6a7a2a")]}, pat="scale")
    m.cube("head", (-3.5, 5, -24), (3.5, 6, -17), "#e2e6a8")                                               # mandibula
    for z in range(-24, -17, 2):                                                                           # dientes salidos
        mirror(m, "head", (3.6, 5, z), (4.2, 6.4, z + 0.8), "#ffffff")
    for z in (-25.6,):
        mirror(m, "head", (2.5, 5.2, z), (3.3, 6.5, z + 0.8), "#ffffff")                                    # colmillos de adelante
    mirror(m, "head", (0.8, 9.5, -24.6), (2.0, 10.2, -23.4), "#9aaa38", {"up": [(0, 0, 1, 1, "#3a4a1a")]})   # fosas nasales
    m.bone("tail", (0, 9, 12), "body")
    m.cube("tail", (-3.5, 6, 12), (3.5, 11, 24), "#a8b340", pat="scale")
    m.cube("tail", (-2.5, 7, 24), (2.5, 10, 30), "#a8b340", pat="scale")
    m.cube("tail", (-1.5, 7.5, 30), (1.5, 9.5, 36), "#ecece4", {"up": [(0, 0, 3, 1, "#c8c8b8")]})
    for z in range(13, 23, 3):                                                                             # pinches de la cola
        mirror(m, "tail", (0.6, 11, z), (1.6, 12.2, z + 1.4), "#8a9a30")
    for z in (25, 27.5):
        box(m, "tail", (-0.5, 10, z), (0.5, 11, z + 1.4), "#8a9a30")
    legs = []
    for n, x, z in (("leg_fl", -7, -5), ("leg_fr", 7, -5), ("leg_bl", -7, 8), ("leg_br", 7, 8)):
        m.bone(n, (x, 7, z), "body")
        m.cube(n, (x - 1.5, 1, z - 1.5), (x + 1.5, 7, z + 1.5), "#7aa03a", pat="scale")
        m.cube(n, (x - 2, 0, z - 3), (x + 2, 1, z + 1.5), "#6a8a2a")
        for dx in (-1.8, -0.4, 1.0):                                                                      # garras
            m.cube(n, (x + dx, 0, z - 3.8), (x + dx + 0.8, 0.7, z - 3), "#ecece4")
        legs.append(n)
    saddle(m, "body", 0, 12.3, -4, 5, 9, strap=6)
    reins(m, "head", 3.2, 8, -22, -8)
    m.anim("walk", 1, merge(walk4(legs, 30, 1.5), {"tail": {"rotation": (0, swing(18, 1.5), 0)},
                                                  "body": {"rotation": (0, swing(4, 1.5), 0)}}))
    m.anim("idle", 3, {"tail": {"rotation": (0, swing(8, 0.33), 0)}, "head": {"rotation": (swing(2, 0.33), 0, 0)}})
    return m


# ------------------------------------------------------------------ 8 escarabajo azul (montura lenta)
def escarabajo():
    m = Model("astral_escarabajo")
    m.bone("body", (0, 9, 0))
    m.cube("body", (-8, 4, -10), (8, 13, 12), "#5b67b8", pat="chitin")
    m.cube("body", (-7, 13, -9), (7, 15, 11), "#6a76c8", pat="chitin")
    for z in range(-8, 12, 4):                                                                             # segmentos en relieve
        box(m, "body", (-7.3, 13, z), (7.3, 15.4, z + 0.8), "#4a56a8")
        box(m, "body", (-8.3, 5, z), (8.3, 13, z + 0.8), "#4a56a8")
    for z in (-6, -2, 2, 6):                                                                               # brillos de cada placa
        mirror(m, "body", (2, 15, z), (5, 15.3, z + 1.5), "#8a96e0")
    m.cube("body", (-6, 4, 12), (6, 11, 14), "#4a55a0", pat="chitin")                                     # cola redondeada
    box(m, "body", (-4, 5, 14), (4, 9, 14.8), "#3e4a98")
    m.cube("body", (-5, 3, -10), (5, 4, 12), "#8a94d0")                                                   # panza
    m.bone("head", (0, 8, -10), "body")
    m.cube("head", (-5, 4, -15), (5, 11, -10), "#4a55a0", {"north": [(3, 5, 4, 1, "#30366a")]}, pat="chitin")
    box(m, "head", (-5.3, 10, -15.4), (5.3, 11.4, -9.8), "#5b67b8")                                      # casco
    eye_front(m, "head", 2, 4, 7, 9, -15, "#e8e8f0", pupil="#30366a")
    mirror(m, "head", (1.5, 3.5, -17), (3.5, 5.5, -15), "#cfd6ef")                                        # pinzas
    mirror(m, "head", (1.2, 3.5, -18), (2.2, 4.8, -17), "#b8c0e0")
    mirror(m, "head", (2.5, 11.4, -14), (3.2, 14, -13.3), "#30366a")                                       # antenitas
    mirror(m, "head", (2.3, 14, -14.5), (3.4, 14.8, -13.1), "#d9632a")
    legs = []
    for i, z in enumerate((-7, -2, 3, 8)):
        for s, side in ((1, "l"), (-1, "r")):
            n = f"leg_{side}{i}"
            m.bone(n, (8 * s, 6, z), "body")
            a, b = sorted((7.5 * s, 10 * s))
            m.cube(n, (a, 3, z - 1), (b, 6, z + 1), "#cfd6ef")
            a, b = sorted((9.6 * s, 10.6 * s))
            m.cube(n, (a, 3.5, z - 1.2), (b, 5.5, z + 1.2), "#a8b0d8")                                    # rodilla
            a, b = sorted((9 * s, 11 * s))
            m.cube(n, (a, 0, z - 0.8), (b, 3, z + 0.8), "#b8c0e0")
            a, b = sorted((9.4 * s, 10.6 * s))
            m.cube(n, (a, 0, z - 1.4), (b, 0.6, z - 0.8), "#6a74a8")                                       # unita
            legs.append((n, i, s))
    saddle(m, "body", 0, 15.4, -5, 5, 10, strap=9)
    for s in (1, -1):                                                                                     # manijas naranjas
        m.cube("silla", (2.5 * s - 0.5, 16.8, -5), (2.5 * s + 0.5, 22, -4), "#d9632a")
        m.cube("silla", (2.5 * s - 0.5, 21, -8), (2.5 * s + 0.5, 22, -5), "#d9632a")
        m.cube("silla", (2.5 * s - 0.5, 19, -9), (2.5 * s + 0.5, 22, -8), "#d9632a")
        m.cube("silla", (2.5 * s - 0.8, 18.2, -9.3), (2.5 * s + 0.8, 19.2, -7.7), "#ffb060")             # puntas redondas
    m.anim("walk", 2, {n: {"rotation": (swing(20, 1, 0 if (i + (s > 0)) % 2 else 180), 0, 0)} for n, i, s in legs})
    m.anim("idle", 3, {"head": {"rotation": (swing(3, 0.5), 0, 0)}, "body": {"position": (0, swing(0.2, 0.33), 0)}})
    return m


# ------------------------------------------------------------------ 9 chocobo (montura rapida)
def chocobo():
    m = Model("astral_chocobo")
    m.bone("body", (0, 18, 0))
    m.cube("body", (-6, 13, -7), (6, 25, 9), "#f4d24a", {"down": [(2, 2, 8, 12, "#fff0a0")]}, pat="feather")
    m.cube("body", (-5, 14, -9), (5, 23, -7), "#fae070", pat="feather")                                     # pechuga
    for row, (y, z) in enumerate(((21, -9.6), (18, -9.4), (15, -9.2))):                                     # plumas del pecho en capas
        box(m, "body", (-4.5 + row * 0.5, y, z), (4.5 - row * 0.5, y + 2, z + 0.6), "#fff0a0", pat="feather")
        for k in range(4 - row % 2):
            x = -4 + row * 0.5 + k * 2.4 + (row % 2) * 1.2
            box(m, "body", (x, y - 1, z), (x + 1.2, y, z + 0.6), "#f8e080")
    for x, z in ((-4, 0), (2, -3), (-1, 5), (3, 3)):                                                         # plumas del lomo
        box(m, "body", (x, 25, z), (x + 2, 25.8, z + 2), "#f0c83a", pat="feather")
    for k, (x, y) in enumerate(((-3, 20), (0, 22), (3, 20), (-1.5, 18), (1.5, 18))):                       # cola de plumas
        box(m, "body", (x - 1.5, y, 9), (x + 1.5, y + 6, 14 + k % 2 * 2), "#f0c83a", {"south": [(0, 0, 3, 1, "#d8a830")]}, pat="feather")
        box(m, "body", (x - 1, y + 5, 14 + k % 2 * 2), (x + 1, y + 7, 15.5 + k % 2 * 2), "#d8a830")
    for n, s in (("wing_l", 1), ("wing_r", -1)):
        m.bone(n, (6 * s, 23, -2), "body")
        a, b = sorted((6 * s, 7.5 * s))
        m.cube(n, (a, 15, -4), (b, 23.5, 7), "#e8c040", pat="feather")
        for k, z in enumerate(range(-3, 7, 2)):                                                             # puntas de las plumas
            a, b = sorted((6.3 * s, 7.8 * s))
            m.cube(n, (a, 13.5 - (k % 2), z), (b, 15, z + 1.6), "#d8a830")
        a, b = sorted((7.5 * s, 8 * s))
        m.cube(n, (a, 18, -3), (b, 23, 6), "#f4d24a", pat="feather")                                      # capa de arriba
    m.bone("head", (0, 24, -6), "body")
    m.cube("head", (-3, 23, -9.5), (3, 31, -4.5), "#f4d24a", pat="feather")                                # cuello
    for y in (24, 27):                                                                                     # plumas del cuello
        box(m, "head", (-3.4, y, -10), (3.4, y + 1.5, -5), "#fae070", pat="feather")
    m.cube("head", (-4, 30, -14), (4, 37, -5), "#f8dc5c", pat="feather")
    eye_side(m, "head", 4, 33.3, 35.7, -10.2, -7.6, "#3a7ad8", white="#ffffff")
    mirror(m, "head", (3.8, 36, -11), (4.6, 36.8, -7), "#d8a830")                                           # ceja
    box(m, "head", (-2, 34, -5), (2, 37, -3.5), "#f0c83a", pat="feather")                                  # plumas de la nuca
    m.cube("head", (-2, 31.5, -18), (2, 34, -14), "#9a6a3a")
    m.cube("head", (-1.5, 30.5, -17), (1.5, 31.5, -14), "#7a4a22")                                          # pico abajo
    m.cube("head", (-1, 30.5, -19), (1, 33.5, -18), "#5a3418")                                              # gancho
    mirror(m, "head", (0.6, 33.2, -17.2), (1.2, 33.8, -16.4), "#3a2010")                                    # fosas
    for k, (z, h) in enumerate(((-11, 4), (-9, 5), (-7, 3.5), (-5.5, 2.5))):                               # cresta
        box(m, "head", (-1 + k * 0.2, 37, z), (1 - k * 0.2, 37 + h, z + 1.5), "#f0c83a", pat="feather")
        box(m, "head", (-0.6 + k * 0.2, 36.5 + h, z + 0.4), (0.6 - k * 0.2, 37.3 + h, z + 1.5), "#fff0a0")
    reins(m, "head", 2.2, 32.5, -16, -5)
    for n, x in (("leg_l", 3), ("leg_r", -3)):
        m.bone(n, (x, 14, 1), "body")
        m.cube(n, (x - 2.2, 7, -1.5), (x + 2.2, 15, 3.5), "#8a6b4a", pat="fur")                             # muslo
        for dx in (-2.2, -0.7, 0.8):                                                                       # flecos del muslo
            m.cube(n, (x + dx, 6, -1.8), (x + dx + 1.4, 7.2, 3.8), "#7a5b3a", pat="fur")
        m.cube(n, (x - 1, 1, 0), (x + 1, 7, 2), "#e8e0d0", pat="scale")                                    # canilla
        for y in (2, 4):
            m.cube(n, (x - 1.2, y, -0.2), (x + 1.2, y + 0.6, 2.2), "#c8c0b0")                             # escamas
        for dx, ln in ((-1.6, 3), (-0.4, 3.5), (0.8, 3)):                                                  # dedos con garras
            m.cube(n, (x + dx, 0, -ln), (x + dx + 0.9, 1, 1), "#e8e0d0")
            m.cube(n, (x + dx + 0.1, 0, -ln - 0.7), (x + dx + 0.8, 0.7, -ln), "#3a3a3a")
        m.cube(n, (x - 0.5, 0, 2), (x + 0.5, 1, 3.5), "#e8e0d0")
    saddle(m, "body", 0, 25.3, -3, 6, 10, strap=8)
    m.anim("walk", 1, {"leg_l": {"rotation": (swing(40, 2.5), 0, 0)}, "leg_r": {"rotation": (swing(-40, 2.5), 0, 0)},
                       "head": {"rotation": (swing(6, 2.5), 0, 0)}, "wing_l": {"rotation": (0, 0, swing(8, 2.5))},
                       "wing_r": {"rotation": (0, 0, swing(-8, 2.5))}})
    m.anim("idle", 3, {"head": {"rotation": (swing(4, 0.33), swing(6, 0.2), 0)}})
    return m


# ------------------------------------------------------------------ 10 grillo (montura que salta)
def grillo():
    m = Model("astral_grillo")
    m.bone("body", (0, 12, 0))
    m.cube("body", (-5.5, 8, -8), (5.5, 15, 2), "#c9c832", {"down": [(1, 1, 9, 8, "#e8e870")]}, pat="chitin")  # torax
    box(m, "body", (-5.8, 13.5, -8.3), (5.8, 15.3, 2.3), "#b8b82a", pat="chitin")                           # escudo del torax
    m.cube("body", (-5, 7, 2), (5, 14, 16), "#b8b82a", pat="chitin")
    for z in range(3, 16, 3):                                                                              # anillos del abdomen
        box(m, "body", (-5.3, 6.7, z), (5.3, 13.6, z + 0.7), "#8a9a22")
    for s in (1, -1):                                                                                      # alas plegadas
        a, b = sorted((0.2 * s, 5.4 * s))
        m.cube("body", (a, 14, -2), (b, 15.2, 17), "#9fb02a", pat="membrane")
        a, b = sorted((2.4 * s, 3.0 * s))
        m.cube("body", (a, 15.2, -2), (b, 15.6, 17), "#d8e070")                                           # nervadura
        for z in (2, 7, 12):
            a, b = sorted((0.6 * s, 5 * s))
            m.cube("body", (a, 15.2, z), (b, 15.5, z + 0.5), "#7a8a1a")
    m.bone("head", (0, 12, -8), "body")
    m.cube("head", (-5, 7, -15), (5, 16, -8), "#d4d23a", pat="chitin")
    box(m, "head", (-3, 8.5, -15.5), (3, 10.5, -15), "#8a9a22")                                            # boca
    mirror(m, "head", (0.8, 7, -16.3), (2.5, 9, -15), "#6a7a12")                                           # mandibulas
    mirror(m, "head", (2.6, 6, -15.6), (3.4, 9, -14.8), "#8a9a22")                                         # palpos
    box(m, "head", (-4, 15, -15.4), (4, 16.6, -9), "#c9c832")                                              # frente
    for s in (1, -1):                                                                                      # ojos grandes
        a, b = sorted((4.5 * s, 6 * s))
        m.cube("head", (a, 11, -14), (b, 15, -10), "#8a2a1a")
        a, b = sorted((6 * s, 6.5 * s))
        m.cube("head", (a, 11.5, -13.5), (b, 14.5, -10.5), "#b03a1a", {"east": [(2, 0, 1, 1, "#ffb08a")]})
        a, b = sorted((6.5 * s, 6.8 * s))
        m.cube("head", (a, 13, -12.8), (b, 14, -11.8), "#ffb08a")
    for n, s in (("ant_l", 1), ("ant_r", -1)):                                                             # antenas largas
        m.bone(n, (2 * s, 16, -13), "head")
        m.cube(n, (2 * s - 0.4, 16.6, -13.4), (2 * s + 0.4, 21, -12.6), "#8a9a22")
        m.cube(n, (2 * s - 0.4, 20.6, -12.6), (2 * s + 0.4, 21.4, 0), "#8a9a22")
        m.cube(n, (2 * s - 0.4, 19, 0), (2 * s + 0.4, 21.4, 0.8), "#6a7a12")
        m.cube(n, (2 * s - 0.7, 16.4, -13.7), (2 * s + 0.7, 17.4, -12.3), "#6a7a12")                     # base
    for n, s in (("hleg_l", 1), ("hleg_r", -1)):                                                           # patas de salto
        m.bone(n, (5.5 * s, 12, 5), "body")
        a, b = sorted((5.5 * s, 8.5 * s))
        m.cube(n, (a, 10, 1), (b, 19, 12), "#9fb02a", pat="chitin")
        a, b = sorted((8.5 * s, 9 * s))
        for y in (12, 15):                                                                                 # dibujo en espina de pescado
            m.cube(n, (a, y, 2), (b, y + 1, 11), "#c9c832")
        a, b = sorted((6 * s, 8 * s))
        m.cube(n, (a, 1, 11), (b, 11, 13), "#8a9a22")
        for y in (3, 6, 9):                                                                                # espinas de la canilla
            m.cube(n, (a + 0.5, y, 13), (b - 0.5, y + 0.7, 14), "#5a6a12")
        m.cube(n, (a, 0, 8), (b, 1, 13), "#6a7a12")
        m.cube(n, (a + 0.4, 0, 7), (b - 0.4, 0.6, 8), "#3a4a0a")
    for n, s, z in (("fleg_l", 1, -5), ("fleg_r", -1, -5), ("mleg_l", 1, 0), ("mleg_r", -1, 0)):
        m.bone(n, (5 * s, 9, z), "body")
        a, b = sorted((5 * s, 8 * s))
        m.cube(n, (a, 6, z - 0.8), (b, 9, z + 0.8), "#9fb02a")
        a, b = sorted((7 * s, 8.5 * s))
        m.cube(n, (a, 0, z - 0.8), (b, 6, z + 0.8), "#8a9a22")
        a, b = sorted((7.2 * s, 8.3 * s))
        m.cube(n, (a, 0, z - 1.6), (b, 0.6, z - 0.8), "#5a6a12")
    saddle(m, "body", 0, 15.6, -6, 2, 8, strap=6, col="#a8401e", trim="#5a200e")
    m.cube("silla", (-0.5, 17.2, -7.5), (0.5, 21, -6.5), "#5a200e")                                       # manubrio
    m.cube("silla", (-4, 20.5, -7.5), (4, 21.5, -6.5), "#5a200e")
    mirror(m, "silla", (2.6, 20.2, -7.8), (4.6, 21.8, -6.2), "#3a3a3a")                                    # punos
    m.anim("walk", 1, {"fleg_l": {"rotation": (swing(25, 2), 0, 0)}, "fleg_r": {"rotation": (swing(-25, 2), 0, 0)},
                       "mleg_l": {"rotation": (swing(-25, 2), 0, 0)}, "mleg_r": {"rotation": (swing(25, 2), 0, 0)},
                       "ant_l": {"rotation": (swing(6, 1), 0, 0)}, "ant_r": {"rotation": (swing(-6, 1), 0, 0)}})
    m.anim("jump", 0.6, {"hleg_l": {"rotation": ("-40", 0, 0)}, "hleg_r": {"rotation": ("-40", 0, 0)},
                         "body": {"rotation": ("-10", 0, 0)}}, loop="once")
    m.anim("idle", 2, {"body": {"position": (0, swing(0.3, 0.5), 0)}, "ant_l": {"rotation": (swing(8, 0.5), 0, 0)},
                       "ant_r": {"rotation": (swing(-8, 0.5), 0, 0)}})
    return m


# ------------------------------------------------------------------ 11 gran ave (montura voladora)
def ave():
    m = Model("astral_ave")
    m.bone("body", (0, 22, 0))
    m.cube("body", (-6, 17, -9), (6, 28, 11), "#7a4a2a", {"down": [(1, 1, 10, 18, "#f0ece4")]}, pat="feather")
    m.cube("body", (-5, 17.5, -11), (5, 26, -9), "#f0ece4", pat="feather")                                  # pecho blanco
    for y in (19, 22):                                                                                    # plumas del pecho
        for k in range(4):
            x = -4 + k * 2.2 + (y == 22) * 1
            box(m, "body", (x, y - 0.8, -11.5), (x + 1.4, y + 1.5, -11), "#e0dcd2")
    for x, z in ((-5, -6), (3, -4), (-2, 2), (2, 6), (-4, 8)):                                             # plumas del lomo
        box(m, "body", (x, 28, z), (x + 2.2, 28.6, z + 2.5), "#6a4a2a", pat="feather")
    for k, x in enumerate((-4, -1.5, 1, 3.5)):                                                             # cola en abanico, plumas separadas
        box(m, "body", (x - 1.1, 21 + (k % 2), 11), (x + 1.1, 23 + (k % 2), 21 + (k % 2) * 2), "#6a4a2a", pat="feather")
        box(m, "body", (x - 1.1, 21.2 + (k % 2), 21 + (k % 2) * 2), (x + 1.1, 22.6 + (k % 2), 23 + (k % 2) * 2), "#f0ece4")
    m.bone("head", (0, 27, -10), "body")
    m.cube("head", (-4.5, 25, -13), (4.5, 30, -8), "#f0ece4", pat="fur")                                     # collar de plumas
    for x in (-4.5, -2, 0.5, 3):                                                                           # flecos del collar
        box(m, "head", (x, 24, -13.5), (x + 1.5, 25.5, -12.5), "#e0dcd2")
        box(m, "head", (x, 24, -8.5), (x + 1.5, 25.5, -7.5), "#e0dcd2")
    mirror(m, "head", (4.5, 25.5, -12.5), (5.2, 29.5, -8.5), "#e0dcd2", pat="fur")
    m.cube("head", (-4, 28, -17), (4, 35, -10), "#e8a890", {"north": [(0, 1, 8, 1, "#c88a7a")]})
    eye_front(m, "head", 1, 2.8, 31, 32.8, -17, "#111111", pupil=None)
    mirror(m, "head", (0.6, 32.8, -17.6), (3.6, 33.6, -16.8), "#c88a7a")                                   # ceja pelada
    mirror(m, "head", (4, 30, -14), (4.4, 32, -12), "#c88a7a")                                            # oido
    box(m, "head", (-1.5, 29.5, -21), (1.5, 33.5, -17), "#5a5a5a", {"up": [(0, 0, 3, 1, "#8a8a8a")]})
    box(m, "head", (-1, 28, -21.8), (1, 30, -20.4), "#3a3a3a")                                             # gancho del pico
    box(m, "head", (-1.8, 32, -18), (1.8, 34, -17), "#8a8a8a")                                             # cera del pico
    for n, s in (("wing_l", 1), ("wing_r", -1)):
        m.bone(n, (6 * s, 26, 0), "body")
        a, b = sorted((6 * s, 20 * s))
        m.cube(n, (a, 25, -6), (b, 27, 8), "#6a4a2a", pat="feather")
        a, b = sorted((6 * s, 20 * s))
        m.cube(n, (a, 27, -6.3), (b, 27.6, -1), "#9a6a3a", pat="feather")                                 # cobertoras en capa
        for k in range(6):                                                                                 # plumas del borde de atras
            xx = 7 + k * 2.2
            a, b = sorted((xx * s, (xx + 2) * s))
            m.cube(n, (a, 25.3, 8), (b, 26.7, 10 + (k % 2)), "#f0ece4")
        m.bone(n + "2", (20 * s, 26, 0), n)
        a, b = sorted((20 * s, 32 * s))
        m.cube(n + "2", (a, 25.3, -5), (b, 26.8, 7), "#7a5a3a", pat="feather")
        a, b = sorted((20 * s, 32 * s))
        m.cube(n + "2", (a, 26.8, -5.3), (b, 27.3, -1), "#9a6a3a")
        for k in range(5):                                                                                 # plumas largas de la punta
            a, b = sorted((31 * s, (37 - k) * s))
            m.cube(n + "2", (a, 25.6, -4 + k * 2.6), (b, 26.6, -2.2 + k * 2.6), "#4a3a2a")
            a, b = sorted(((36.3 - k) * s, (37 - k) * s))
            m.cube(n + "2", (a, 25.6, -4 + k * 2.6), (b, 26.6, -2.2 + k * 2.6), "#f0ece4")
    for x in (-2.5, 2.5):                                                                                  # patas recogidas con garras
        box(m, "body", (x - 1.8, 13, -2), (x + 1.8, 17, 2), "#f0ece4", pat="fur")
        box(m, "body", (x - 1, 10, -1), (x + 1, 13, 1), "#c8a050", pat="scale")
        for dx in (-1.5, -0.4, 0.7):
            box(m, "body", (x + dx, 9, -2.5), (x + dx + 0.8, 10, 0.5), "#c8a050")
            box(m, "body", (x + dx, 8.4, -3), (x + dx + 0.8, 9.2, -2.2), "#2a2a2a")
    saddle(m, "body", 0, 28.6, -5, 4, 10, strap=8, col="#c03a2a", trim="#6a1a12")
    reins(m, "head", 3.5, 30, -15, -5, col="#c03a2a")
    fly = {"wing_l": {"rotation": (0, 0, swing(30, 1.2))}, "wing_r": {"rotation": (0, 0, swing(-30, 1.2))},
           "wing_l2": {"rotation": (0, 0, swing(15, 1.2, 40))}, "wing_r2": {"rotation": (0, 0, swing(-15, 1.2, 40))},
           "body": {"position": (0, swing(1.5, 0.6), 0)}}
    for a in ("walk", "idle_fly", "walk_fly"):
        m.anim(a, 1, fly)
    m.anim("idle", 3, {"wing_l": {"rotation": (0, 0, -60)}, "wing_r": {"rotation": (0, 0, 60)},
                       "wing_l2": {"rotation": (0, 0, -100)}, "wing_r2": {"rotation": (0, 0, 100)},
                       "head": {"rotation": (swing(4, 0.33), swing(10, 0.2), 0)}})
    return m


# ------------------------------------------------------------------ 12 pterodactilo (montura voladora)
def pterodactilo():
    m = Model("astral_pterodactilo")
    m.bone("body", (0, 22, 0))
    m.cube("body", (-5, 16, -8), (5, 27, 9), "#3a5aa8", {"down": [(1, 1, 8, 15, "#c89a4a")]}, pat="scale")
    for z in range(-7, 8, 3):                                                                              # placas de la panza
        box(m, "body", (-3.5, 15.6, z), (3.5, 16, z + 2.4), "#d8aa5a")
    mirror(m, "body", (5, 20, -7), (5.3, 23, 8), "#c89a4a")                                                 # franja clara del costado
    m.cube("body", (-2, 19, 9), (2, 23, 22), "#3a5aa8", pat="scale")                                        # cola
    m.cube("body", (-3, 20, 21), (3, 21, 25), "#e07a2a")                                                    # punta de la cola
    box(m, "body", (-2, 20.2, 25), (2, 20.8, 26.5), "#b8561a")
    for z in range(-6, 21, 3):
        box(m, "body", (-0.5, 27 if z < 9 else 23, z), (0.5, 28.5 if z < 9 else 24.2, z + 1.5), "#2a4a90")   # cresta del lomo
    m.bone("head", (0, 27, -8), "body")
    m.cube("head", (-3, 25, -11), (3, 32, -6), "#3a5aa8", pat="scale")                                     # cuello
    for y in (26, 28.5):
        box(m, "head", (-2.2, y, -11.5), (2.2, y + 1.6, -11), "#c89a4a")                                   # placas de la garganta
    m.cube("head", (-4, 30, -16), (4, 37, -8), "#4a6ab8", pat="scale")
    eye_side(m, "head", 4, 33, 35.5, -12.5, -10, "#f2d24a", pupil="#111111")
    mirror(m, "head", (3.6, 35.5, -13.2), (4.6, 36.5, -9.4), "#2a4a90")                                   # ceja
    m.cube("head", (-2, 31, -29), (2, 35, -16), "#c89a4a", {"up": [(1, 0, 2, 13, "#d8aa5a")]})
    box(m, "head", (-2.4, 33, -16.5), (2.4, 34, -15.5), "#8a6a2a")                                          # comisura
    for z in range(-28, -17, 2):                                                                           # dientes salidos
        mirror(m, "head", (1.5, 30.2, z), (2.1, 31.2, z + 0.7), "#ffffff")
    box(m, "head", (-0.6, 30, -29.6), (0.6, 31.5, -28.6), "#ffffff")                                        # diente de la punta
    mirror(m, "head", (0.6, 35, -27), (1.4, 35.5, -25.8), "#8a6a2a")                                        # fosas
    for k, (z, h) in enumerate(((-12, 7), (-9, 9), (-6, 6))):                                                 # cresta verde
        box(m, "head", (-0.8, 36, z), (0.8, 36 + h, z + 2.2), "#a8c86a", {"north": [(0, 0, 2, 1, "#d8f0a0")]})
        box(m, "head", (-0.5, 36 + h, z + 0.6), (0.5, 37 + h, z + 1.6), "#d8f0a0")
    reins(m, "head", 2.2, 32, -20, -8)
    for n, s in (("wing_l", 1), ("wing_r", -1)):
        m.bone(n, (5 * s, 25, -2), "body")
        a, b = sorted((5 * s, 30 * s))
        m.cube(n, (a, 25, -5), (b, 27, -3), "#3a5aa8", pat="scale")                                       # brazo del ala
        a, b = sorted((16 * s, 18 * s))
        m.cube(n, (a, 24.7, -5.3), (b, 27.3, -2.7), "#2a4a90")                                             # codo
        a, b = sorted((5 * s, 30 * s))
        m.cube(n, (a, 25.3, -3), (b, 26.5, 10), "#e07a2a", pat="membrane")
        for xx, z1 in ((12, 9), (19, 10), (26, 8)):                                                         # dedos del ala en relieve
            a, b = sorted((xx * s, (xx + 0.7) * s))
            m.cube(n, (a, 26.5, -3), (b, 27, z1), "#b8561a")
        a, b = sorted((30 * s, 32 * s))
        m.cube(n, (a, 24, -6), (b, 26, -4), "#f2d24a")                                                     # garritas
        a, b = sorted((31 * s, 32.5 * s))
        m.cube(n, (a, 23, -7), (b, 24.2, -5.5), "#f2d24a")
    for x in (-2.5, 2.5):
        box(m, "body", (x - 1.5, 10, 0), (x + 1.5, 16, 4), "#2a4a90", pat="scale")
        box(m, "body", (x - 2, 9, -1), (x + 2, 10, 4), "#c89a4a")
        for dx in (-1.8, -0.4, 1.0):
            box(m, "body", (x + dx, 9, -2), (x + dx + 0.8, 9.7, -1), "#ffffff")
    saddle(m, "body", 0, 27.4, -4, 4, 9, strap=8, col="#9a5a2a", trim="#5a2e12")
    fly = {"wing_l": {"rotation": (0, 0, swing(28, 1))}, "wing_r": {"rotation": (0, 0, swing(-28, 1))},
           "body": {"position": (0, swing(1.5, 0.5), 0)}, "head": {"rotation": (swing(4, 0.5), 0, 0)}}
    for a in ("walk", "idle_fly", "walk_fly"):
        m.anim(a, 1, fly)
    m.anim("idle", 3, {"wing_l": {"rotation": (0, 35, -70)}, "wing_r": {"rotation": (0, -35, 70)},
                       "head": {"rotation": (swing(4, 0.33), swing(12, 0.2), 0)}})
    return m


# ------------------------------------------------------------------ jefes
def biped(m, leg_col, arm_col, size=1.0, pat=None):
    s = size
    m.bone("body", (0, 12 * s, 0))
    for n, x in (("leg_l", 2 * s), ("leg_r", -2 * s)):
        m.bone(n, (x, 12 * s, 0), "body")
        m.cube(n, (x - 2 * s, 0, -2 * s), (x + 2 * s, 12 * s, 2 * s), leg_col, pat=pat)
    for n, x0, x1, ox in (("arm_l", 4 * s, 8 * s, 6 * s), ("arm_r", -8 * s, -4 * s, -6 * s)):
        m.bone(n, (ox, 22 * s, 0), "body")
        m.cube(n, (x0, 10 * s, -2 * s), (x1, 24 * s, 2 * s), arm_col, pat=pat)
    m.bone("head", (0, 24 * s, 0), "body")
    m.anim("walk", 1.2, {"leg_l": {"rotation": (swing(30, 1.4), 0, 0)}, "leg_r": {"rotation": (swing(-30, 1.4), 0, 0)},
                         "arm_l": {"rotation": (swing(-30, 1.4), 0, 0)}, "arm_r": {"rotation": (swing(30, 1.4), 0, 0)}})
    m.anim("idle", 3, {"head": {"rotation": (swing(3, 0.33), 0, 0)}, "arm_l": {"rotation": (0, 0, swing(3, 0.33))},
                       "arm_r": {"rotation": (0, 0, swing(-3, 0.33))}})
    m.anim("attack", 0.6, {"arm_l": {"rotation": (swing(-80, 1.6), 0, 0)}, "arm_r": {"rotation": (swing(-80, 1.6), 0, 0)}}, loop="once")


def ring(m, bone, x0, x1, z0, z1, y, h, col, out=0.3):
    """Anillo en relieve alrededor de una pieza (vendas, bandas)."""
    m.cube(bone, (x0 - out, y, z0 - out), (x1 + out, y + h, z1 + out), col, pat="wrap")


def strips(m, bone, pts, col="#c8b890", dark="#9a8a68"):
    """Tiras de venda sueltas colgando."""
    for (x, y, z, ln) in pts:
        m.cube(bone, (x, y - ln, z), (x + 1, y, z + 0.5), col, {"north": [(0, ln - 1, 1, 1, dark)]})


def momia():
    m = Model("astral_momia")
    biped(m, "#c8b890", "#d8c8a0", pat="wrap")
    m.cube("body", (-4, 12, -2), (4, 24, 2), "#d8c8a0", pat="wrap")
    for y, col in ((13.5, "#c8b890"), (16.8, "#e0d0a8"), (20.5, "#c8b890")):                                # vendas del torso
        ring(m, "body", -4, 4, -2, 2, y, 1.2, col)
    box(m, "body", (-1.2, 18, -2.8), (1.2, 20, -2.2), "#3aff6a", {"north": [(0, 0, 1, 1, "#c8ffd0")]})     # gema del pecho
    box(m, "body", (-1.6, 17.6, -2.5), (1.6, 20.4, -2.2), "#8a7a50")
    for n, x in (("arm_l", 6), ("arm_r", -6)):
        for y in (12, 16, 20):
            ring(m, n, x - 2, x + 2, -2, 2, y, 1, "#c8b890")
        m.cube(n, (x - 1.6, 9, -1.6), (x + 1.6, 10, 1.6), "#8a7a50")                                       # mano seca
    for n, x in (("leg_l", 2), ("leg_r", -2)):
        for y in (2, 6, 9.5):
            ring(m, n, x - 2, x + 2, -2, 2, y, 1, "#c8b890")
    m.cube("head", (-4, 24, -4), (4, 32, 4), "#e0d0a8", {"north": [(5, 3, 2, 2, "#1a1a1a"), (3, 6, 3, 1, "#5a4a30")],
                                                       "up": [(2, 2, 4, 4, "#c8b890")]}, pat="wrap")
    for y in (25, 28.6, 30.6):
        ring(m, "head", -4, 4, -4, 4, y, 0.9, "#c8b890")
    box(m, "head", (1, 27.4, -4.6), (3, 28.6, -4), "#1a1a1a")                                               # cuenca
    box(m, "head", (1.5, 27.6, -4.8), (2.5, 28.4, -4.6), "#3aff6a")                                         # ojo verde
    box(m, "head", (-3, 27.4, -4.4), (-1, 28.6, -4), "#1a1a1a")
    box(m, "head", (-1, 32, -1), (1, 32.8, 1), "#3aff6a")                                                   # gema de la coronilla
    strips(m, "body", [(-3.5, 13, -2.6, 4), (1.5, 14, -2.6, 3), (-1, 12.5, 2.2, 5), (2.5, 13, 2.2, 3)])
    strips(m, "head", [(3.6, 30, -1, 5), (-4.6, 29, 1, 4), (-2, 25, -4.5, 3)])
    for n, x in (("arm_l", 6), ("arm_r", -6)):
        strips(m, n, [(x - 0.5, 12, 2.2, 5), (x - 1.5, 15, -2.6, 3)])
    m.anim("idle", 3, {"arm_l": {"rotation": (-75, 0, swing(4, 0.33))}, "arm_r": {"rotation": (-75, 0, swing(-4, 0.33))},
                       "head": {"rotation": (swing(4, 0.33), 0, swing(3, 0.2))}})
    m.anim("walk", 1.4, {"leg_l": {"rotation": (swing(25, 1.2), 0, 0)}, "leg_r": {"rotation": (swing(-25, 1.2), 0, 0)},
                         "arm_l": {"rotation": (-75, swing(8, 1.2), 0)}, "arm_r": {"rotation": (-75, swing(-8, 1.2), 0)},
                         "body": {"rotation": (0, 0, swing(4, 1.2))}})
    return m


def yeti():
    m = Model("astral_yeti")
    s = 1.6
    biped(m, "#e0e8f0", "#e8eef4", s, pat="shag")
    m.cube("body", (-7 * s, 9 * s, -3.5 * s), (7 * s, 25 * s, 3.5 * s), "#f0f4f8", pat="shag")
    for k in range(7):                                                                                     # pelo largo que cuelga
        x = -7 * s + k * 2 * s
        ln = 5 + (k % 3)
        m.cube("body", (x, (10 - ln) * s, -3.9 * s), (x + 1.8 * s, 10 * s, -3.4 * s), "#e8eef4", pat="shag")
        m.cube("body", (x, (10 - ln) * s, 3.4 * s), (x + 1.8 * s, 10 * s, 3.9 * s), "#e8eef4", pat="shag")
    for x0, y0, z0 in ((-6, 18, -4.1), (-2, 21, -4.1), (2.5, 17, -4.1), (-4, 13, -4.1), (3, 12, -4.1)):    # mechones del pecho
        m.cube("body", (x0 * s, y0 * s, z0 * s), ((x0 + 2.5) * s, (y0 + 3) * s, (z0 + 0.6) * s), "#ffffff", pat="shag")
    mirror(m, "body", (6.5 * s, 22 * s, -3 * s), (8.8 * s, 26 * s, 3 * s), "#f0f4f8", pat="shag")           # hombros peludos
    m.cube("head", (-5 * s, 24 * s, -5 * s), (5 * s, 33 * s, 4 * s), "#e8eef4", pat="shag")
    m.cube("head", (-3.8 * s, 24.8 * s, -5.3 * s), (3.8 * s, 30.5 * s, -5 * s), "#3a4a6a")                  # cara oscura
    eye_front(m, "head", 1.0 * s, 3.0 * s, 28 * s, 29.2 * s, -5.3 * s, "#6af0ff", pupil=None, glow="#ffffff")
    m.cube("head", (-4.5 * s, 29.5 * s, -6 * s), (4.5 * s, 31 * s, -5 * s), "#ffffff", pat="shag")           # cejas peludas
    m.cube("head", (-1 * s, 26.6 * s, -5.6 * s), (1 * s, 27.6 * s, -5.3 * s), "#2a3a5a")                    # nariz
    mirror(m, "head", (1.2 * s, 25 * s, -5.6 * s), (1.9 * s, 26.4 * s, -5.3 * s), "#ffffff")                 # colmillos
    for x in (-3.2, -1.6, 0, 1.6):                                                                         # mechones de la cabeza
        m.cube("head", (x * s, 33 * s, -3 * s), ((x + 1.5) * s, 35 * s, 1 * s), "#f0f4f8", pat="shag")
    mirror(m, "head", (5 * s, 25 * s, -3 * s), (5.6 * s, 30 * s, 2 * s), "#f0f4f8", pat="shag")              # patillas
    for sx in (1, -1):                                                                                     # cuernos de carnero en espiral
        for (a0, a1, y0, y1, z0, z1, col) in ((4.5, 7, 31, 34, -2, 2, "#7a5030"), (7, 9, 30, 34, -1, 3, "#8a5a38"),
                                             (8, 10, 27, 31, 0, 3.5, "#7a5030"), (7, 9.5, 25.5, 28, -2.5, 1, "#6a4428"),
                                             (6.5, 8.5, 26, 28.5, -4, -2, "#5a3a20"), (7.2, 8, 27, 28, -4.6, -4, "#d8c0a0")):
            a, b = sorted((a0 * s * sx, a1 * s * sx))
            m.cube("head", (a, y0 * s, z0 * s), (b, y1 * s, z1 * s), col, {"up": [(0, 1, 3, 1, "#5a3a20")]})
        for y in (31.5, 32.8):                                                                             # estrias del cuerno
            a, b = sorted((7.4 * s * sx, 7.8 * s * sx))
            m.cube("head", (a, y * s, -1.2 * s), (b, (y + 0.4) * s, 3.2 * s), "#5a3a20")
    for n, x in (("arm_l", 6), ("arm_r", -6)):                                                             # manos oscuras con garras
        a, b = sorted(((x - 2) * s, (x + 2) * s))
        m.cube(n, (a, 8 * s, -2 * s), (b, 10 * s, 2 * s), "#3a4a6a")
        for dx in (-1.6, -0.4, 0.8):
            m.cube(n, ((x + dx) * s, 7 * s, -2.4 * s), ((x + dx + 0.6) * s, 8 * s, -1.8 * s), "#ffffff")
        m.cube(n, (a - 0.4, 18 * s, -2.4 * s), (b + 0.4, 22 * s, 2.4 * s), "#f0f4f8", pat="shag")         # pelo del brazo
    for n, x in (("leg_l", 2), ("leg_r", -2)):
        for dx in (-1.6, -0.4, 0.8):
            m.cube(n, ((x + dx) * s, 0, -2.6 * s), ((x + dx + 0.6) * s, 0.6 * s, -2 * s), "#3a4a6a")
    return m


def golem_forja():
    m = Model("astral_golem_forja")
    m.bone("body", (0, 10, 0))
    m.cube("body", (-8, 10, -8), (8, 28, 8), "#8a2a2a",
           {"north": [(3, 6, 10, 9, "#1e1210")] + [(3 + k, 7, 1, 7, "#ffb030" if k % 2 else "#ff7a10") for k in range(10)]}, pat="brick")
    for x in (-4, -2, 0, 2, 4):                                                                             # rejas de la rejilla
        box(m, "body", (x - 0.4, 13, -8.8), (x + 0.4, 22, -8), "#3a3a40", {"north": [(0, 0, 1, 1, "#6a6a70")]})
    box(m, "body", (-5.6, 21.5, -9), (5.6, 22.6, -8), "#3a3a40")                                           # marco
    box(m, "body", (-5.6, 12.4, -9), (5.6, 13.5, -8), "#3a3a40")
    mirror(m, "body", (5, 12.4, -9), (5.8, 22.6, -8), "#3a3a40")
    box(m, "body", (-4.5, 12.6, -9.4), (4.5, 13.2, -9), "#ff9a20")                                          # brasas que caen
    zig = [(k, 1 + (k % 4 if k % 4 < 2 else 3 - k % 4), 1, 1, "#e8c8a8") for k in range(17)]
    m.cube("body", (-8.4, 23.5, -8.4), (8.4, 26, 8.4), "#7a2222", {f: zig for f in ("north", "south", "east", "west")})  # guarda en zigzag
    m.cube("body", (-8.6, 26, -8.6), (8.6, 28.5, 8.6), "#5a1a1a", {"up": border(17, 17, "#3a1010")}, pat="brick")  # cornisa
    m.cube("body", (-8.5, 9, -8.5), (8.5, 11, 8.5), "#3a3a40", pat="stone")                                # base
    for (a, b) in (((8, 16, -3), (8.6, 18, 0)), ((-8.6, 19, 2), (-8, 21, 5)), ((2, 12, 8), (5, 14, 8.6)),   # ladrillos salidos
                   ((-6, 17, 8), (-3, 19, 8.6)), ((6, 15, -8.6), (7.8, 17, -8)), ((-7.8, 18, -8.6), (-6, 20, -8))):
        box(m, "body", a, b, "#9a3434", pat="brick")
    m.bone("head", (0, 28, 0), "body")
    m.cube("head", (-5, 28, -5), (5, 46, 5), "#8a2e2e", pat="brick")
    box(m, "head", (-3, 42, -5.8), (3, 43, -5), "#ff9a20")                                                  # aro de la ventana de fuego
    box(m, "head", (-3, 37, -5.8), (3, 38, -5), "#ff9a20")
    mirror(m, "head", (3, 38, -5.8), (4, 42, -5), "#ff9a20")
    box(m, "head", (-2, 38, -5.4), (2, 42, -5), "#ff6a10")
    box(m, "head", (-1, 39, -5.8), (1, 41, -5.4), "#fff0a0")                                                # nucleo
    box(m, "head", (-3.6, 43, -6.2), (3.6, 44, -5), "#e8c8a8")                                               # dintel
    for y in (33, 31):                                                                                     # bandas claras
        m.cube("head", (-5.4, y, -5.4), (5.4, y + 1, 5.4), "#e8c8a8")
    m.cube("head", (-6, 44, -6), (6, 47, 6), "#6a2222", {"up": [(2, 2, 8, 8, "#100808"), (4, 4, 4, 4, "#3a1a10")]}, pat="brick")
    for x, z in ((-6, -6), (4.5, -6), (-6, 4.5), (4.5, 4.5)):                                               # almenas
        box(m, "head", (x, 47, z), (x + 1.5, 48.5, z + 1.5), "#6a2222", pat="brick")
    m.cube("head", (-6, 27, -6), (6, 29, 6), "#5a1a1a", pat="brick")
    legs = []
    for n, x, z in (("leg_fl", -8, -8), ("leg_fr", 8, -8), ("leg_bl", -8, 8), ("leg_br", 8, 8)):
        m.bone(n, (x, 10, z), "body")
        m.cube(n, (x - 4, 2, z - 4), (x + 4, 11, z + 4), "#2e2a30", pat="brick")
        m.cube(n, (x - 4.3, 8, z - 4.3), (x + 4.3, 9, z + 4.3), "#4a4450")                                 # junta
        m.cube(n, (x - 4.5, 0, z - 4.5), (x + 4.5, 2.5, z + 4.5), "#a83a3a", pat="stone")
        for dx, dz in ((-4.8, -2), (3.2, -4.9), (-2, 3.4), (3.4, 2)):                                       # bultos carmesi
            m.cube(n, (x + dx, 0, z + dz), (x + dx + 1.6, 1.8, z + dz + 1.5), "#c84a3a", {"up": [(0, 0, 1, 1, "#ff6a3a")]})
        legs.append(n)
    m.anim("walk", 1.5, walk4(legs, 15, 1))
    m.anim("idle", 2, {"head": {"rotation": (0, swing(5, 0.5), 0)}})
    m.anim("attack", 0.8, {"head": {"rotation": (swing(-15, 1.2), 0, 0)}, "body": {"rotation": (swing(-6, 1.2), 0, 0)}}, loop="once")
    return m


def cangrejo():
    m = Model("astral_cangrejo")
    m.bone("body", (0, 6, 0))
    m.cube("body", (-6.5, 6, -4), (6.5, 19, 9), "#d8b8a0", {"north": [(0, 0, 13, 2, "#b89880")]}, pat="shell")
    for (y0, y1, z0, z1) in ((16, 17, -2, 7), (8, 9, -2, 7), (9, 16, -2, -1), (9, 16, 6, 7),              # espiral en relieve
                             (14, 15, 0, 5), (10, 11, 0, 5), (11, 14, 0, 1), (11, 14, 4, 5)):
        mirror(m, "body", (6.5, y0, z0), (7, y1, z1), "#b89880")
    mirror(m, "body", (6.5, 12, 2), (7.5, 13.5, 3.5), "#8a6a5a")                                           # centro de la espiral
    box(m, "body", (-5.5, 19, -3), (5.5, 19.6, 8), "#c8a890", pat="shell")                                   # tope del caracol
    for (x, z, h, w) in ((-5, 2, 2, 2), (-3.5, 5, 3, 2), (2, 6, 2, 2.5), (0, -1, 1.5, 3), (3.5, 1, 1, 2)):   # musgo y hojitas
        box(m, "body", (x, 19.6, z), (x + w, 19.6 + h, z + 1.4), "#5a9a3a", {"north": [(0, 0, 1, 1, "#9ad86a")]})
    mirror(m, "body", (6.5, 16, -3), (7, 19, 0), "#5a9a3a")                                                 # musgo que cae
    m.cube("body", (-5, 1.5, -7), (5, 7, 2), "#d0502a", pat="chitin")
    for x, z in ((-3, -5), (2, -3), (0, 0)):
        box(m, "body", (x, 7, z), (x + 1.5, 7.5, z + 1.5), "#5a9a3a")                                      # algas en el cuerpo
    for x in (-3, 3):                                                                                       # ojos en tallos
        m.cube("body", (x - 0.5, 7, -7), (x + 0.5, 11, -6), "#d0502a")
        m.cube("body", (x - 1.2, 11, -8), (x + 1.2, 13.5, -5.6), "#f2d24a")
        m.cube("body", (x - 0.6, 11.6, -8.5), (x + 0.6, 12.8, -8), "#111111", {"north": [(0, 0, 1, 1, "#ffffff")]})
    for n, s, big in (("claw_l", 1, True), ("claw_r", -1, False)):
        m.bone(n, (5 * s, 5, -6), "body")
        sz = 1.4 if big else 1.0
        a, b = sorted((4 * s, (4 + 3 * sz) * s))
        m.cube(n, (a, 3, -9), (b, 6, -6), "#b8401a", pat="chitin")                                          # brazo
        a, b = sorted(((4 + 1 * sz) * s, (4 + 6 * sz) * s))
        m.cube(n, (a, 2, -9 - 5 * sz), (b, 3 + 5 * sz, -9), "#d0502a", pat="chitin")                       # pinza
        a, b = sorted(((4 + 1 * sz) * s, (4 + 3 * sz) * s))
        m.cube(n, (a, 2, -11 - 5 * sz), (b, 3.5, -9 - 5 * sz), "#f2e6c8")                                   # punta de abajo
        a, b = sorted(((4 + 3.5 * sz) * s, (4 + 6 * sz) * s))
        m.cube(n, (a, 2 + 3 * sz, -11 - 5 * sz), (b, 3 + 5 * sz, -9 - 5 * sz), "#f2e6c8")                 # punta de arriba
        for k in range(3):                                                                                  # bultitos de la pinza
            a, b = sorted(((4.5 + k * 1.6) * sz * s, (5.3 + k * 1.6) * sz * s))
            m.cube(n, (a, 3 + 5 * sz, -8 - 4 * sz + k), (b, 3.6 + 5 * sz, -7.2 - 4 * sz + k), "#f07a4a")
    legs = []
    for i, z in enumerate((-4, -1, 2)):
        for s, side in ((1, "l"), (-1, "r")):
            n = f"leg_{side}{i}"
            m.bone(n, (5 * s, 4, z), "body")
            a, b = sorted((5 * s, 9 * s))
            m.cube(n, (a, 3, z - 0.75), (b, 5, z + 0.75), "#d0502a")
            a, b = sorted((6.5 * s, 7.3 * s))
            m.cube(n, (a, 5, z - 0.3), (b, 5.6, z + 0.3), "#f07a4a")                                       # pinchito
            a, b = sorted((8.5 * s, 10 * s))
            m.cube(n, (a, 0, z - 0.6), (b, 4, z + 0.6), "#b8401a")
            legs.append((n, i, s))
    ch = {n: {"rotation": (0, 0, swing(12, 2, 0 if (i + (s > 0)) % 2 else 180))} for n, i, s in legs}
    ch["claw_l"] = {"rotation": (swing(10, 1), 0, 0)}
    ch["claw_r"] = {"rotation": (swing(-10, 1), 0, 0)}
    m.anim("walk", 1, ch)
    m.anim("idle", 2, {"claw_l": {"rotation": (swing(6, 0.5), 0, 0)}, "claw_r": {"rotation": (swing(-6, 0.5), 0, 0)}})
    m.anim("attack", 0.6, {"claw_l": {"rotation": (swing(-40, 1.6), 0, 0)}, "claw_r": {"rotation": (swing(-40, 1.6, 90), 0, 0)}}, loop="once")
    return m


def chaman():
    m = Model("astral_chaman")
    biped(m, "#4a6a2a", "#6a8a3a", pat="cloth")
    m.cube("body", (-6, 2, -4), (6, 24, 5), "#6a8a3a", {"south": [(3, 4, 3, 3, "#4a6a2a")]}, pat="cloth")
    box(m, "body", (-6.3, 15, -4.3), (6.3, 16.2, 5.3), "#5a3a1a", pat="wood")                               # cinturon
    box(m, "body", (-3.5, 12.5, -4.9), (-1, 15.4, -4), "#8a6a3a", {"north": [(0, 0, 3, 1, "#6a4a2a")]})     # bolsita
    box(m, "body", (-1, 16.6, -4.7), (1, 18.8, -4), "#8a5aa8", {"north": [(0, 0, 1, 1, "#d8a0ff")]})        # amuleto
    for k in range(7):                                                                                     # collar de huesitos
        x = -3.3 + k * 1.1
        y = 20.5 - abs(k - 3) * 0.4
        box(m, "body", (x, y, -4.6), (x + 0.8, y + 0.8, -4), "#e8e8e0")
    for x, y0 in ((-5, 9), (-2, 6), (1.5, 8), (4, 5)):                                                     # remiendos y jirones
        box(m, "body", (x, y0, -4.4), (x + 1.8, y0 + 2.2, -4), "#4a6a2a", pat="cloth")
    for k in range(6):                                                                                     # flecos rotos abajo
        x = -6 + k * 2
        m.cube("body", (x, 0, -4.4), (x + 1, 2 + (k % 2), -3.6), "#4a6a2a")
        m.cube("body", (x + 1, 0.5, 4.4), (x + 2, 2, 5.2), "#4a6a2a")
    mirror(m, "body", (6, 21, -3), (6.6, 24, 4), "#4a6a2a", pat="cloth")                                    # hombreras de trapo
    m.cube("head", (-5, 22, -6), (5, 33, 4), "#5a7a30", {"north": [(2, 3, 6, 6, "#1e2a12")], "up": [(4, 2, 2, 6, "#4a6a2a")]}, pat="cloth")
    box(m, "head", (-4.6, 31, -6.6), (4.6, 32.6, -6), "#4a6a2a", pat="cloth")                               # borde de la capucha
    mirror(m, "head", (3.2, 23, -6.6), (4.6, 31, -6), "#4a6a2a", pat="cloth")
    m.cube("head", (-3, 25, -6.4), (3, 31, -5.8), "#e8e8e0", {"north": [(2, 3, 2, 1, "#3a3a3a")]})          # mascara calavera
    eye_front(m, "head", 0.8, 2.2, 28.6, 30, -6.4, "#b04aff", pupil=None, glow="#e8b0ff")
    box(m, "head", (-3, 30.2, -6.8), (3, 30.8, -6.4), "#d8d8d0")                                             # ceja de hueso
    box(m, "head", (-2.5, 24.2, -6.7), (2.5, 25.4, -6), "#e8e8e0", {"north": [(0, 0, 5, 1, "#3a3a3a"), (1, 0, 1, 1, "#e8e8e0"), (3, 0, 1, 1, "#e8e8e0")]})  # mandibula
    m.cube("head", (-2, 33, -3), (2, 35, 1), "#5a7a30", pat="cloth")                                        # punta capucha
    for s in (1, -1):                                                                                      # cuernitos de hueso
        a, b = sorted((3 * s, 4 * s))
        m.cube("head", (a, 33, -4), (b, 37, -3), "#e8e8e0")
        a, b = sorted((4 * s, 6 * s))
        m.cube("head", (a, 36, -4), (b, 37, -3), "#e8e8e0")
        a, b = sorted((5 * s, 6 * s))
        m.cube("head", (a, 37, -4), (b, 38.5, -3), "#e8e8e0")
    # baston con plumas y cintas
    m.cube("arm_r", (-10, 0, -6), (-9, 36, -5), "#8a6a3a", pat="wood")
    for y in (8, 18, 27):                                                                                  # ataduras del baston
        m.cube("arm_r", (-10.3, y, -6.3), (-8.7, y + 1, -4.7), "#5a3a1a")
    m.cube("arm_r", (-12, 34, -6), (-7, 35, -5), "#8a6a3a")
    for k, col in enumerate(("#e84a4a", "#4ae8a8", "#f2d24a", "#4a8ae8", "#e84a4a")):                     # plumas y cintas
        x = -12 + (k % 3) * 2
        m.cube("arm_r", (x, 29 - k, -6.5), (x + 1, 34 - k % 2, -6), col)
        m.cube("arm_r", (x + 0.2, 28 - k, -6.4), (x + 0.8, 29 - k, -6.1), "#ffffff")
    m.cube("arm_r", (-11, 36, -7), (-8, 38, -4), "#e8e8e0", {"north": [(0, 0, 1, 1, "#3a3a3a"), (2, 0, 1, 1, "#3a3a3a")]})  # calavera
    m.cube("arm_r", (-11.5, 38, -6), (-10.5, 41, -5), "#e8e8e0")
    m.cube("arm_r", (-8.5, 38, -6), (-7.5, 41, -5), "#e8e8e0")
    m.cube("arm_r", (-12.5, 40, -6), (-11.5, 41, -5), "#e8e8e0")
    m.cube("arm_r", (-7.5, 40, -6), (-6.5, 41, -5), "#e8e8e0")
    m.anim("idle", 3, {"head": {"rotation": (swing(3, 0.33), 0, 0)}, "arm_l": {"rotation": (swing(-10, 0.33), 0, swing(4, 0.33))},
                       "arm_r": {"rotation": (-10, 0, swing(-3, 0.33))}})
    m.anim("attack", 0.8, {"arm_r": {"rotation": (swing(-50, 1.2), 0, 0)}, "arm_l": {"rotation": (-90, 0, swing(20, 2))}}, loop="once")
    return m


ALL = [mapache, pinguino, espantapajaros, abejorro, arana, cara, lagarto, escarabajo, chocobo, grillo, ave,
       pterodactilo, momia, yeti, golem_forja, cangrejo, chaman]

# Monturas con hueso 'silla' (se muestra al ponerle montura) y asiento 'p_seat'
MOUNTS = {"astral_lagarto", "astral_escarabajo", "astral_chocobo", "astral_grillo", "astral_ave", "astral_pterodactilo"}
