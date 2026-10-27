# -*- coding: utf-8 -*-
"""
Las 17 criaturas de AstralRPG (inspiradas en las imagenes de referencia).
Frente = norte (-Z). 16 unidades = 1 bloque. Altura del piso = 0.
"""
from bbmodel import Model, swing


def walk4(m, legs, amp=30, speed=1.5):
    """legs: [del_izq, del_der, tras_izq, tras_der] -> trote diagonal."""
    ch = {}
    for i, b in enumerate(legs):
        ph = 0 if i in (0, 3) else 180
        ch[b] = {"rotation": (swing(amp, speed, ph), 0, 0)}
    return ch


def merge(*dicts):
    out = {}
    for d in dicts:
        for k, v in d.items():
            out.setdefault(k, {}).update(v)
    return out


def leg(m, name, x, z, top, w, d, color, parent="body", foot=None):
    m.bone(name, (x, top, z), parent)
    m.cube(name, (x - w / 2, 0, z - d / 2), (x + w / 2, top, z + d / 2), color,
           decals={"north": [(0, top - 1, w, 1, foot)]} if foot else None)


# ------------------------------------------------------------------ 1 mapache
def mapache():
    m = Model("astral_mapache")
    m.bone("body", (0, 8, 0))
    m.cube("body", (-4, 5, -6), (4, 11, 7), "#8a6e5a", {"down": [(1, 2, 6, 9, "#c9b49c")]})
    m.bone("head", (0, 10, -6), "body")
    m.cube("head", (-4, 6, -12), (4, 13, -6), "#9a7e68",
           {"north": [(0, 2, 8, 2, "#3a2e28"), (2, 2, 1, 1, "#0d0d0d"), (5, 2, 1, 1, "#0d0d0d"), (0, 5, 8, 2, "#e8dccb")]})
    m.cube("head", (-2, 6, -14), (2, 9, -12), "#e2d4c0", {"north": [(1, 0, 2, 1, "#1d1d1d")]})
    m.cube("head", (-4, 13, -9), (-2, 15, -7), "#6b5040", {"north": [(0, 0, 2, 2, "#e0a0a0")]})
    m.cube("head", (2, 13, -9), (4, 15, -7), "#6b5040", {"north": [(0, 0, 2, 2, "#e0a0a0")]})
    m.bone("tail", (0, 10, 7), "body")
    rings = [(2, 0, 2, 3, "#3a2e28"), (6, 0, 2, 3, "#3a2e28")]
    m.cube("tail", (-1.5, 8, 7), (1.5, 11, 17), "#8a6e5a", {"east": rings, "west": rings, "up": [(0, 2, 3, 2, "#3a2e28"), (0, 6, 3, 2, "#3a2e28")]})
    legs = []
    for n, x, z in (("leg_fl", -2.5, -3.5), ("leg_fr", 2.5, -3.5), ("leg_bl", -2.5, 4.5), ("leg_br", 2.5, 4.5)):
        leg(m, n, x, z, 5, 2.5, 2.5, "#5a463a")
        legs.append(n)
    m.anim("walk", 1, merge(walk4(m, legs, 35, 2), {"tail": {"rotation": (0, swing(15, 2), 0)}}))
    m.anim("idle", 3, {"tail": {"rotation": (0, swing(10, 0.33), 0)}, "head": {"rotation": (swing(3, 0.33), 0, 0)}})
    return m


# ------------------------------------------------------------------ 2 pinguino
def pinguino():
    m = Model("astral_pinguino")
    m.bone("body", (0, 2, 0))
    m.cube("body", (-4, 2, -3.5), (4, 13, 3.5), "#6fb0e0", {"north": [(2, 3, 4, 7, "#eaf6ff")]})
    m.cube("body", (-3, 0, -4.5), (-0.5, 2, -1), "#e8752a")
    m.cube("body", (0.5, 0, -4.5), (3, 2, -1), "#e8752a")
    m.bone("head", (0, 13, 0), "body")
    m.cube("head", (-4, 13, -4), (4, 19, 4), "#5a9fd6",
           {"north": [(1, 1, 2, 2, "#ffffff"), (5, 1, 2, 2, "#ffffff"), (2, 2, 1, 1, "#111111"), (5, 2, 1, 1, "#111111")]})
    m.cube("head", (-1.5, 14, -6), (1.5, 16, -4), "#ff8a3a")
    m.cube("head", (-4, 19, -1), (-3, 21, 0), "#f2c94c")
    m.cube("head", (3, 19, -1), (4, 21, 0), "#f2c94c")
    m.bone("flip_l", (4, 12, 0), "body")
    m.cube("flip_l", (4, 5, -2), (5, 12, 2), "#4a88c0")
    m.bone("flip_r", (-4, 12, 0), "body")
    m.cube("flip_r", (-5, 5, -2), (-4, 12, 2), "#4a88c0")
    m.cube("flip_r", (-8, 5, -3), (-5, 9, 0), "#ff9fc8", {"north": [(1, 1, 1, 1, "#ffffff")]})
    m.anim("walk", 1, {"body": {"rotation": (0, 0, swing(8, 2))}, "flip_l": {"rotation": (0, 0, swing(-20, 2))},
                       "flip_r": {"rotation": (0, 0, swing(20, 2))}})
    m.anim("idle", 2, {"head": {"rotation": (0, swing(10, 0.5), 0)}})
    return m


# ------------------------------------------------------------------ 3 espantapajaros
def espantapajaros():
    m = Model("astral_espantapajaros")
    m.bone("body", (0, 9, 0))
    m.cube("body", (-4, 9, -2.5), (4, 19, 2.5), "#d9b23c",
           {"north": [(1, 2, 3, 3, "#7a3fb0"), (5, 6, 2, 3, "#5a2f8a")], "south": [(2, 4, 4, 3, "#7a3fb0")]})
    for n, x in (("leg_l", 2), ("leg_r", -2)):
        m.bone(n, (x, 9, 0), "body")
        m.cube(n, (x - 1.5, 0, -1.5), (x + 1.5, 9, 1.5), "#5a3f7a", {"north": [(0, 7, 3, 2, "#e3b83a")]})
    m.bone("head", (0, 19, 0), "body")
    face = [(2, 3, 2, 2, "#5a1f8a"), (6, 3, 2, 2, "#5a1f8a"), (2, 6, 6, 2, "#5a1f8a"), (4, 6, 1, 1, "#f08a1c"),
            (6, 7, 1, 1, "#f08a1c"), (1, 0, 1, 10, "#d8761a"), (8, 0, 1, 10, "#d8761a")]
    m.cube("head", (-5, 19, -5), (5, 29, 5), "#f08a1c", {"north": face})
    m.cube("head", (-6, 28, -6), (6, 29, 6), "#5a5f6e")
    m.cube("head", (-3.5, 29, -3.5), (3.5, 33, 3.5), "#4a4f5c", {"north": [(0, 3, 7, 1, "#c8a24a")]})
    for n, x0, x1, ox in (("arm_l", 4, 7, 4.5), ("arm_r", -7, -4, -4.5)):
        m.bone(n, (ox, 18, 0), "body")
        m.cube(n, (x0, 8, -1.5), (x1, 18, 1.5), "#d9b23c")
        m.cube(n, (x0, 6, -1.5), (x1, 8, 1.5), "#e48fd0")
    m.cube("arm_r", (-6.5, 7, -12), (-5.5, 8, 6), "#b05fd8")
    m.cube("arm_r", (-6.5, 8, -14), (-5.5, 15, -11), "#e07af0", {"east": [(0, 0, 3, 1, "#ffffff")]})
    m.anim("walk", 1, {"leg_l": {"rotation": (swing(30, 1.5), 0, 0)}, "leg_r": {"rotation": (swing(-30, 1.5), 0, 0)},
                       "arm_l": {"rotation": (swing(-25, 1.5), 0, 0)}, "arm_r": {"rotation": (swing(25, 1.5), 0, 0)}})
    m.anim("idle", 3, {"head": {"rotation": (0, 0, swing(6, 0.33))}})
    return m


# ------------------------------------------------------------------ 4 abejorro sombrio (volador)
def abejorro():
    m = Model("astral_abejorro")
    m.bone("body", (0, 9, 0))
    m.cube("body", (-4, 6, -4), (4, 12, 8), "#23283a", {"up": [(0, 3, 8, 1, "#e0a83a"), (0, 7, 8, 1, "#e0a83a")]})
    m.cube("body", (-3, 6, -8), (3, 11, -4), "#1b1f2d", {"north": [(1, 1, 1, 1, "#ffd34d"), (4, 1, 1, 1, "#ffd34d")]})
    for n, s in (("wing_l", 1), ("wing_r", -1)):
        m.bone(n, (4 * s, 12, 0), "body")
        a, b = sorted((4 * s, 14 * s))
        m.cube(n, (a, 12, -2), (b, 12.5, 6), "#2c3550", {"up": [(0, 2, 10, 1, "#e0a83a"), (0, 5, 10, 1, "#e0a83a")]})
    for i, z in enumerate((-2, 1, 4)):
        for s in (1, -1):
            a, b = sorted((3 * s, 4 * s))
            m.cube("body", (a, 2, z), (b, 6, z + 1), "#151821")
    fly = {"wing_l": {"rotation": (0, 0, swing(35, 4))}, "wing_r": {"rotation": (0, 0, swing(-35, 4))},
           "body": {"position": (0, swing(1, 0.5), 0)}}
    for a in ("idle", "walk", "idle_fly", "walk_fly"):
        m.anim(a, 1, fly)
    return m


# ------------------------------------------------------------------ 5 arana purpura
def arana():
    m = Model("astral_arana")
    m.bone("body", (0, 6, 0))
    m.cube("body", (-6, 4, -5), (6, 10, 7), "#7a6aa8", {"up": [(5, 0, 2, 12, "#5e4e8c")]})
    m.cube("body", (-4, 3, -9), (4, 8, -5), "#6a5a98",
           {"north": [(1, 1, 1, 1, "#2a1e40"), (3, 1, 1, 1, "#2a1e40"), (5, 1, 1, 1, "#2a1e40")]})
    legs = []
    for i, z in enumerate((-4, -1, 2, 5)):
        for s, side in ((1, "l"), (-1, "r")):
            n = f"leg_{side}{i}"
            m.bone(n, (6 * s, 6, z), "body")
            a, b = sorted((6 * s, 13 * s))
            m.cube(n, (a, 5, z - 0.75), (b, 6.5, z + 0.75), "#5e4e8c")
            a, b = sorted((12 * s, 13.5 * s))
            m.cube(n, (a, 0, z - 0.75), (b, 6, z + 0.75), "#4e3e7c")
            legs.append((n, i, s))
    ch = {n: {"rotation": (0, swing(15, 2, 0 if (i + (s > 0)) % 2 else 180), 0)} for n, i, s in legs}
    m.anim("walk", 1, ch)
    m.anim("idle", 2, {"body": {"position": (0, swing(0.3, 0.5), 0)}})
    return m


# ------------------------------------------------------------------ 6 cara voladora
def cara():
    m = Model("astral_cara")
    m.bone("body", (0, 12, 0))
    face = [(2, 1, 8, 4, "#e8f0d8"), (5, 2, 2, 2, "#3fb84a"), (5, 2, 1, 1, "#0d200f"), (1, 6, 10, 4, "#3a0c18")]
    face += [(1 + 2 * k, 6, 1, 1, "#f2e6c8") for k in range(5)] + [(2 + 2 * k, 9, 1, 1, "#f2e6c8") for k in range(5)]
    m.cube("body", (-6, 6, -6), (6, 18, 6), "#a83c5a", {"north": face, "up": [(0, 0, 12, 1, "#7a2a40")]})
    for n, s in (("wing_l", 1), ("wing_r", -1)):
        m.bone(n, (6 * s, 15, 0), "body")
        a, b = sorted((6 * s, 16 * s))
        m.cube(n, (a, 14, -1), (b, 15, 1), "#8c2e48")
        a, b = sorted((15 * s, 17 * s))
        m.cube(n, (a, 15, -1), (b, 22, 1), "#8c2e48")
    fly = {"wing_l": {"rotation": (0, 0, swing(30, 3))}, "wing_r": {"rotation": (0, 0, swing(-30, 3))},
           "body": {"position": (0, swing(1.5, 0.7), 0)}}
    for a in ("idle", "walk", "idle_fly", "walk_fly"):
        m.anim(a, 1, fly)
    return m


# ------------------------------------------------------------------ 7 lagarto (montura, nada)
def lagarto():
    m = Model("astral_lagarto")
    m.bone("body", (0, 9, 0))
    spots = [(2, 3, 2, 2, "#8a9a30"), (8, 10, 2, 2, "#8a9a30"), (4, 15, 3, 2, "#8a9a30")]
    m.cube("body", (-6, 6, -8), (6, 12, 12), "#b7c24a", {"up": spots, "down": [(2, 0, 8, 20, "#e2e6a8")]})
    m.bone("head", (0, 9, -8), "body")
    eyes = [(1, 0, 2, 2, "#ffffff"), (2, 1, 1, 1, "#111111")]
    m.cube("head", (-5, 6, -18), (5, 11, -8), "#c8d15a", {"east": eyes, "west": eyes})
    m.cube("head", (-4, 6, -24), (4, 9, -18), "#bfc95a", {"north": [(1, 2, 1, 1, "#ffffff"), (6, 2, 1, 1, "#ffffff")]})
    m.bone("tail", (0, 9, 12), "body")
    m.cube("tail", (-3, 7, 12), (3, 11, 24), "#a8b340")
    m.cube("tail", (-2, 8, 24), (2, 10, 32), "#ecece4")
    legs = []
    for n, x, z in (("leg_fl", -7, -5), ("leg_fr", 7, -5), ("leg_bl", -7, 8), ("leg_br", 7, 8)):
        leg(m, n, x, z, 6, 3, 3, "#7aa03a")
        legs.append(n)
    m.anim("walk", 1, merge(walk4(m, legs, 30, 1.5), {"tail": {"rotation": (0, swing(18, 1.5), 0)},
                                                      "body": {"rotation": (0, swing(4, 1.5), 0)}}))
    m.anim("idle", 3, {"tail": {"rotation": (0, swing(8, 0.33), 0)}})
    return m


# ------------------------------------------------------------------ 8 escarabajo azul (montura lenta)
def escarabajo():
    m = Model("astral_escarabajo")
    m.bone("body", (0, 10, 0))
    m.cube("body", (-8, 6, -10), (8, 14, 12), "#5b67b8", {"up": [(7, 0, 2, 22, "#3e4a98")]})
    m.cube("body", (-5, 5, -15), (5, 11, -10), "#4a55a0", {"north": [(2, 2, 1, 1, "#e8e8f0"), (7, 2, 1, 1, "#e8e8f0")]})
    for n, x in (("ant_l", 2.5), ("ant_r", -2.5)):
        m.bone(n, (x, 11, -13), "body")
        m.cube(n, (x - 0.5, 11, -14), (x + 0.5, 18, -13), "#d9632a")
        m.cube(n, (x - 1, 18, -15), (x + 1, 19, -12), "#d9632a")
    legs = []
    for i, z in enumerate((-7, 1, 9)):
        for s, side in ((1, "l"), (-1, "r")):
            n = f"leg_{side}{i}"
            m.bone(n, (8 * s, 7, z), "body")
            a, b = sorted((8 * s, 11 * s))
            m.cube(n, (a, 0, z - 1), (b, 7, z + 1), "#cfd6ef")
            legs.append((n, i, s))
    m.anim("walk", 2, {n: {"rotation": (swing(20, 1, 0 if (i + (s > 0)) % 2 else 180), 0, 0)} for n, i, s in legs})
    m.anim("idle", 3, {"ant_l": {"rotation": (swing(8, 0.5), 0, 0)}, "ant_r": {"rotation": (swing(-8, 0.5), 0, 0)}})
    return m


# ------------------------------------------------------------------ 9 chocobo (montura rapida)
def chocobo():
    m = Model("astral_chocobo")
    m.bone("body", (0, 18, 0))
    m.cube("body", (-6, 14, -7), (6, 25, 9), "#f4d24a", {"up": [(1, 2, 10, 1, "#e8c03a")]})
    m.cube("body", (-4, 18, 9), (4, 26, 14), "#f0c83a")
    m.cube("body", (6, 16, -4), (7, 23, 7), "#e8c040")
    m.cube("body", (-7, 16, -4), (-6, 23, 7), "#e8c040")
    m.bone("head", (0, 24, -6), "body")
    m.cube("head", (-3, 24, -9), (3, 32, -5), "#f4d24a")
    eye = [(2, 2, 2, 2, "#3a7ad8"), (3, 3, 1, 1, "#111111")]
    m.cube("head", (-4, 30, -14), (4, 37, -5), "#f8dc5c", {"east": eye, "west": eye})
    m.cube("head", (-2, 31, -18), (2, 34, -14), "#b48a5a")
    m.cube("head", (-1, 37, -10), (1, 40, -7), "#f0c83a")
    for n, x in (("leg_l", 3), ("leg_r", -3)):
        m.bone(n, (x, 14, 1), "body")
        m.cube(n, (x - 2, 6, -1), (x + 2, 14, 3), "#8a6b4a")
        m.cube(n, (x - 1, 0, 0), (x + 1, 6, 2), "#d8d0c0")
        m.cube(n, (x - 2, 0, -3), (x + 2, 1, 2), "#d8d0c0")
    m.anim("walk", 1, {"leg_l": {"rotation": (swing(40, 2.5), 0, 0)}, "leg_r": {"rotation": (swing(-40, 2.5), 0, 0)},
                       "head": {"rotation": (swing(6, 2.5), 0, 0)}})
    m.anim("idle", 3, {"head": {"rotation": (swing(4, 0.33), swing(6, 0.2), 0)}})
    return m


# ------------------------------------------------------------------ 10 grillo (montura que salta)
def grillo():
    m = Model("astral_grillo")
    m.bone("body", (0, 12, 0))
    m.cube("body", (-6, 8, -8), (6, 16, 10), "#c9c832", {"up": [(1, 0, 1, 18, "#9fb02a"), (10, 0, 1, 18, "#9fb02a")]})
    eye = [(1, 1, 4, 4, "#8a2a1a"), (2, 2, 1, 1, "#ffb08a")]
    m.cube("body", (-5, 8, -14), (5, 16, -8), "#d4d23a", {"east": eye, "west": eye})
    for x in (-2.5, 2.5):
        m.cube("body", (x - 0.5, 15, -26), (x, 16, -14), "#8a9a22")
    legs = []
    for n, s in (("hleg_l", 1), ("hleg_r", -1)):
        m.bone(n, (7 * s, 14, 6), "body")
        a, b = sorted((6 * s, 9 * s))
        m.cube(n, (a, 8, 2), (b, 16, 10), "#9fb02a")
        a, b = sorted((6 * s, 8 * s))
        m.cube(n, (a, 0, 8), (b, 8, 10), "#8a9a22")
        legs.append(n)
    for n, s, z in (("fleg_l", 1, -6), ("fleg_r", -1, -6), ("mleg_l", 1, 0), ("mleg_r", -1, 0)):
        m.bone(n, (6 * s, 8, z), "body")
        a, b = sorted((6 * s, 8 * s))
        m.cube(n, (a, 0, z - 1), (b, 8, z + 1), "#8a9a22")
    m.anim("walk", 1, {"fleg_l": {"rotation": (swing(25, 2), 0, 0)}, "fleg_r": {"rotation": (swing(-25, 2), 0, 0)},
                       "mleg_l": {"rotation": (swing(-25, 2), 0, 0)}, "mleg_r": {"rotation": (swing(25, 2), 0, 0)}})
    m.anim("jump", 0.6, {"hleg_l": {"rotation": ("-40", 0, 0)}, "hleg_r": {"rotation": ("-40", 0, 0)},
                         "body": {"rotation": ("-10", 0, 0)}}, loop="once")
    m.anim("idle", 2, {"body": {"position": (0, swing(0.3, 0.5), 0)}})
    return m


# ------------------------------------------------------------------ 11 ave (montura voladora)
def ave():
    m = Model("astral_ave")
    m.bone("body", (0, 26, 0))
    m.cube("body", (-7, 20, -10), (7, 32, 12), "#8a5a3a", {"north": [(2, 4, 10, 8, "#f0ece4")]})
    m.cube("body", (-5, 22, 12), (5, 25, 22), "#6a4a2a", {"up": [(0, 8, 10, 2, "#f0ece4")]})
    m.bone("head", (0, 31, -10), "body")
    m.cube("head", (-5, 30, -18), (5, 38, -9), "#e8b49a",
           {"north": [(1, 2, 2, 2, "#111111"), (7, 2, 2, 2, "#111111"), (0, 6, 10, 2, "#c84a3a")]})
    m.cube("head", (-2, 30, -22), (2, 34, -18), "#3a3a3a")
    for n, s in (("wing_l", 1), ("wing_r", -1)):
        m.bone(n, (7 * s, 30, 0), "body")
        a, b = sorted((7 * s, 28 * s))
        m.cube(n, (a, 29, -6), (b, 31, 10), "#6a4a2a", {"up": [(0, 12, 21, 4, "#f0ece4")]})
        a, b = sorted((27 * s, 42 * s))
        m.cube(n, (a, 29, -6), (b, 30.5, 10), "#8a6a4a", {"up": [(0, 13, 15, 3, "#4a3a2a")]})
    for x in (-2.5, 2.5):
        m.cube("body", (x - 1.5, 10, -2), (x + 1.5, 20, 1), "#e8e8e8")
        m.cube("body", (x - 2, 10, -4), (x + 2, 11, 1), "#c8a050")
    fly = {"wing_l": {"rotation": (0, 0, swing(30, 1.2))}, "wing_r": {"rotation": (0, 0, swing(-30, 1.2))},
           "body": {"position": (0, swing(1.5, 0.6), 0)}}
    for a in ("idle", "walk", "idle_fly", "walk_fly"):
        m.anim(a, 1, fly)
    return m


# ------------------------------------------------------------------ 12 pterodactilo (montura voladora)
def pterodactilo():
    m = Model("astral_pterodactilo")
    m.bone("body", (0, 24, 0))
    m.cube("body", (-6, 18, -8), (6, 30, 10), "#3a5aa8", {"down": [(2, 2, 8, 14, "#c89a4a")]})
    m.cube("body", (-2, 20, 10), (2, 24, 26), "#3a5aa8")
    m.bone("head", (0, 30, -8), "body")
    m.cube("head", (-4, 28, -14), (4, 36, -6), "#4a6ab8",
           {"east": [(1, 2, 2, 2, "#f2d24a"), (2, 3, 1, 1, "#111111")], "west": [(1, 2, 2, 2, "#f2d24a"), (2, 3, 1, 1, "#111111")]})
    m.cube("head", (-2, 30, -26), (2, 34, -14), "#c8a050",
           {"east": [(k * 2, 3, 1, 1, "#ffffff") for k in range(6)], "west": [(k * 2, 3, 1, 1, "#ffffff") for k in range(6)]})
    m.cube("head", (-1, 36, -10), (1, 44, -4), "#a8c86a")
    for n, s in (("wing_l", 1), ("wing_r", -1)):
        m.bone(n, (6 * s, 28, 0), "body")
        a, b = sorted((6 * s, 30 * s))
        m.cube(n, (a, 27, -6), (b, 28.5, 8), "#c89a4a")
        m.cube(n, (a, 28, -7), (b, 30, -5), "#3a5aa8")
    for x in (-2.5, 2.5):
        m.cube("body", (x - 1.5, 8, 0), (x + 1.5, 18, 4), "#2a4a90")
    fly = {"wing_l": {"rotation": (0, 0, swing(28, 1))}, "wing_r": {"rotation": (0, 0, swing(-28, 1))},
           "body": {"position": (0, swing(1.5, 0.5), 0)}}
    for a in ("idle", "walk", "idle_fly", "walk_fly"):
        m.anim(a, 1, fly)
    return m


# ------------------------------------------------------------------ jefes
def biped(m, body_col, leg_col, arm_col, size=1.0, head=None):
    s = size
    m.bone("body", (0, 12 * s, 0))
    for n, x in (("leg_l", 2 * s), ("leg_r", -2 * s)):
        m.bone(n, (x, 12 * s, 0), "body")
        m.cube(n, (x - 2 * s, 0, -2 * s), (x + 2 * s, 12 * s, 2 * s), leg_col)
    for n, x0, x1, ox in (("arm_l", 4 * s, 8 * s, 6 * s), ("arm_r", -8 * s, -4 * s, -6 * s)):
        m.bone(n, (ox, 22 * s, 0), "body")
        m.cube(n, (x0, 10 * s, -2 * s), (x1, 24 * s, 2 * s), arm_col)
    m.bone("head", (0, 24 * s, 0), "body")
    m.anim("walk", 1.2, {"leg_l": {"rotation": (swing(30, 1.4), 0, 0)}, "leg_r": {"rotation": (swing(-30, 1.4), 0, 0)},
                         "arm_l": {"rotation": (swing(-30, 1.4), 0, 0)}, "arm_r": {"rotation": (swing(30, 1.4), 0, 0)}})
    m.anim("idle", 3, {"head": {"rotation": (swing(3, 0.33), 0, 0)}, "arm_l": {"rotation": (0, 0, swing(3, 0.33))},
                       "arm_r": {"rotation": (0, 0, swing(-3, 0.33))}})


def momia():
    m = Model("astral_momia")
    biped(m, "#d8c8a0", "#c8b890", "#d8c8a0")
    strips = [(0, 2, 8, 1, "#9a8a68"), (0, 6, 8, 1, "#9a8a68"), (0, 10, 8, 1, "#9a8a68")]
    m.cube("body", (-4, 12, -2), (4, 24, 2), "#d8c8a0", {"north": strips + [(3, 4, 2, 2, "#4a8a3a")], "south": strips})
    m.cube("head", (-4, 24, -4), (4, 32, 4), "#e0d0a8",
           {"north": [(0, 1, 8, 1, "#9a8a68"), (2, 3, 2, 1, "#3aff6a"), (5, 3, 2, 1, "#1a1a1a"), (0, 6, 8, 1, "#9a8a68")]})
    for n, x in (("arm_l", 6), ("arm_r", -6)):
        m.cube(n, (x - 0.5, 4, 1), (x + 0.5, 12, 2), "#c8b890")
    return m


def yeti():
    m = Model("astral_yeti")
    s = 1.6
    biped(m, "#f0f4f8", "#e0e8f0", "#e8eef4", s)
    m.cube("body", (-7 * s, 12 * s, -3 * s), (7 * s, 25 * s, 3.5 * s), "#f0f4f8", {"south": [(4, 4, 6, 6, "#d8e2ec")]})
    m.cube("head", (-5 * s, 24 * s, -5 * s), (5 * s, 33 * s, 4 * s), "#e8eef4",
           {"north": [(2, 4, 12, 9, "#3a4a6a"), (4, 6, 2, 2, "#6af0ff"), (10, 6, 2, 2, "#6af0ff"), (5, 10, 6, 1, "#ffffff")]})
    for sx in (1, -1):
        a, b = sorted((5 * s * sx, 8 * s * sx))
        m.cube("head", (a, 30 * s, -2 * s), (b, 35 * s, 2 * s), "#7a5030")
        a, b = sorted((7 * s * sx, 9 * s * sx))
        m.cube("head", (a, 27 * s, -4 * s), (b, 31 * s, -1 * s), "#5a3a20")
    return m


def golem_forja():
    m = Model("astral_golem_forja")
    m.bone("body", (0, 10, 0))
    brick = [(0, k, 16, 1, "#4a1a1a") for k in range(0, 20, 4)]
    m.cube("body", (-8, 10, -8), (8, 30, 8), "#7a2a2a",
           {"north": brick + [(4, 8, 8, 6, "#2a1a1a"), (5, 9, 6, 4, "#ffb030"), (6, 9, 1, 4, "#5a2a1a"), (8, 9, 1, 4, "#5a2a1a")],
            "south": brick, "east": brick, "west": brick})
    m.bone("head", (0, 30, 0), "body")
    m.cube("head", (-6, 30, -6), (6, 48, 6), "#8a2e2e",
           {"north": [(0, k, 12, 1, "#5a1a1a") for k in range(0, 18, 4)] + [(3, 4, 6, 6, "#ff9a20"), (5, 6, 2, 2, "#fff0a0")]})
    legs = []
    for n, x, z in (("leg_fl", -7, -7), ("leg_fr", 7, -7), ("leg_bl", -7, 7), ("leg_br", 7, 7)):
        m.bone(n, (x, 10, z), "body")
        m.cube(n, (x - 4, 0, z - 4), (x + 4, 10, z + 4), "#3a3a40", {"north": [(0, 8, 8, 2, "#c84a3a")]})
        legs.append(n)
    m.anim("walk", 1.5, walk4(m, legs, 15, 1))
    m.anim("idle", 2, {"head": {"rotation": (0, swing(5, 0.5), 0)}})
    return m


def cangrejo():
    m = Model("astral_cangrejo")
    m.bone("body", (0, 6, 0))
    m.cube("body", (-6, 6, -4), (6, 18, 8), "#d8b8a0",
           {"east": [(2, 2, 8, 8, "#b89880"), (4, 4, 4, 4, "#d8b8a0")], "west": [(2, 2, 8, 8, "#b89880"), (4, 4, 4, 4, "#d8b8a0")],
            "up": [(1, 1, 4, 3, "#5a9a3a")]})
    m.cube("body", (-5, 2, -7), (5, 7, 2), "#d0502a")
    for x in (-3, 3):
        m.cube("body", (x - 0.5, 7, -7), (x + 0.5, 11, -6), "#d0502a")
        m.cube("body", (x - 1, 11, -8), (x + 1, 13, -6), "#f2d24a", {"north": [(0, 0, 1, 1, "#111111")]})
    for n, s in (("claw_l", 1), ("claw_r", -1)):
        m.bone(n, (5 * s, 5, -6), "body")
        a, b = sorted((4 * s, 10 * s))
        m.cube(n, (a, 3, -12), (b, 8, -6), "#d0502a", {"north": [(2, 2, 2, 3, "#8a2a1a")]})
    legs = []
    for i, z in enumerate((-3, 0)):
        for s, side in ((1, "l"), (-1, "r")):
            n = f"leg_{side}{i}"
            m.bone(n, (5 * s, 4, z), "body")
            a, b = sorted((5 * s, 9 * s))
            m.cube(n, (a, 0, z - 0.75), (b, 4, z + 0.75), "#b8401a")
            legs.append((n, i, s))
    ch = {n: {"rotation": (0, 0, swing(12, 2, 0 if (i + (s > 0)) % 2 else 180))} for n, i, s in legs}
    ch["claw_l"] = {"rotation": (swing(10, 1), 0, 0)}
    ch["claw_r"] = {"rotation": (swing(-10, 1), 0, 0)}
    m.anim("walk", 1, ch)
    m.anim("idle", 2, {"claw_l": {"rotation": (swing(6, 0.5), 0, 0)}, "claw_r": {"rotation": (swing(-6, 0.5), 0, 0)}})
    return m


def chaman():
    m = Model("astral_chaman")
    biped(m, "#6a8a3a", "#4a6a2a", "#6a8a3a")
    rag = [(k, 10, 1, 2, "#3a5a1a") for k in range(0, 12, 2)]
    m.cube("body", (-6, 4, -4), (6, 24, 5), "#6a8a3a", {"north": rag + [(4, 2, 4, 4, "#8a5aa8")], "south": rag})
    m.cube("head", (-5, 22, -6), (5, 32, 4), "#5a7a30",
           {"north": [(2, 3, 6, 5, "#e8e8e0"), (3, 4, 1, 1, "#b04aff"), (6, 4, 1, 1, "#b04aff"), (3, 7, 4, 1, "#2a2a2a")]})
    m.cube("arm_r", (-10, 0, -6), (-9, 34, -5), "#8a6a3a")
    for k, col in enumerate(("#e84a4a", "#4ae8a8", "#f2d24a", "#4a8ae8")):
        m.cube("arm_r", (-11 + (k % 2) * 2, 30 + k, -7), (-10 + (k % 2) * 2, 34 + k, -6), col)
    m.cube("arm_r", (-11, 34, -7), (-8, 36, -4), "#e8e8e0")
    return m


ALL = [mapache, pinguino, espantapajaros, abejorro, arana, cara, lagarto, escarabajo, chocobo, grillo, ave,
       pterodactilo, momia, yeti, golem_forja, cangrejo, chaman]
