# -*- coding: utf-8 -*-
"""
Guadanas 3D: las 5 Guadanas de Mago y la Guadana Umbria (gacha) como modelos de bloques.

Usa el mismo motor que los bastones (varitas3d.py): cubos + textura de muestras
de 8x8 con partes animadas. La vara va parada en x=8, z=8 y la hoja sale hacia
-x desde arriba, como el icono vanilla de la azada.

Uso:
  python guadanas3d.py   vista previa animada -> ../build/previews/guadanas_3d.gif
build_pack.py llama a assets() para meterlas en el resource pack.

Inspiracion (imagenes de otros autores, fuera del repo): docs/REFERENCIAS_ARMAS.md
"""
import os

import varitas3d as v
from varitas3d import Wand, hx

TEX_DIR = "item/guadanas"


def mids(start, pts):
    """Puntos del medio de cada tramo de una hoja."""
    prev = [start] + pts[:-1]
    return [((a[0] + b[0]) / 2, (a[1] + b[1]) / 2) for a, b in zip(prev, pts)]


def G(iid, name, palette):
    return Wand(iid, name, palette, tilt=-20, tex_dir=TEX_DIR)


# ---------------------------------------------------------------------------
# 1. Guadana Umbria Menor: acero con puas, mango forrado en cuero, pincho abajo
# ---------------------------------------------------------------------------
def umbria_menor():
    w = G("guadana_1", "Guadana Umbria Menor", {
        "steel": (hx("7c8496"), "s"), "steel2": (hx("525868"), "s"), "edge": (hx("f2f6ff"), "s"),
        "leather": (hx("7a3b28"), "s"), "leather2": (hx("5a2a1c"), "s"), "wood": (hx("4a3324"), "s"),
        "iron": (hx("5d6270"), "s"), "gem": (hx("8f4bff"), "pulse"), "gem2": (hx("d0b0ff"), "pulse"),
    })
    # pincho de abajo
    w.box((7.2, -6, 7.2), (8.8, -4.5, 8.8), "iron")
    p = w.seg((8, -6), 270, 1.6, 1.2, "steel", (7.5, 8.5))
    w.seg(p, 247.5, 1.6, 0.7, "edge", (7.7, 8.3))
    # mango forrado en cuero
    w.box((7.1, -4.5, 7.1), (8.9, 19.5, 8.9), "wood")
    for k, y in enumerate([-4 + 1.4 * i for i in range(16)]):
        w.box((6.9, y, 6.9), (9.1, y + 0.8, 9.1), "leather" if k % 2 else "leather2")
    w.box((6.7, 7.6, 6.7), (9.3, 8.4, 9.3), "iron")
    w.box((6.6, 18.5, 6.6), (9.4, 20, 9.4), "iron")
    # cuello de la hoja con puas hacia arriba
    w.box((6.8, 20, 7.3), (9.8, 26, 8.7), "steel")
    w.box((9.8, 21, 7.5), (10.4, 25.5, 8.5), "edge")
    w.cen((10.4, 26.4, 8), (1, 2.2, 0.8), "steel", ("z", -22.5))
    w.cen((11.4, 25.2, 8), (0.8, 1.8, 0.7), "steel2", ("z", -45))
    w.cen((8.4, 26.6, 8), (2.6, 1, 1.5), "steel2")
    # hoja
    bp = w.blade((7, 25.2), [(180, 4, 3.2), (180, 3.5, 2.9), (202.5, 3.4, 2.5), (202.5, 3, 2.1), (225, 2.6, 1.5), (247.5, 2, 0.8)],
            "steel", edge="edge", spine="steel2")
    # gema umbria incrustada en la raiz
    w.gem((7.6, 23.4, 8), 1.6, "gem", 12)
    w.cen((7.6, 23.4, 8), (0.8, 0.8, 1.9), "gem2", None, 14)
    # detalles: engarce de la gema, remaches, ranura en la hoja, mellas, borla y pomo
    w.cen((7.6, 23.4, 8), (2.4, 2.4, 1.5), "iron", ("z", 45))
    for y in (20.8, 22.2):
        for z in (7.2, 8.8):
            w.cen((9.2, y, z), (0.5, 0.5, 0.2), "iron")
    for x, y in mids((7, 25.2), bp)[:2]:
        for z in (7.55, 8.45):
            w.cen((x, y + 0.4, z), (2.6, 0.3, 0.1), "steel2")
    for x in (4.6, 1.4):
        w.cen((x, 23.0, 8), (0.5, 0.7, 0.7), "steel2")
    w.box((9.3, 16.6, 7.9), (9.5, 18.6, 8.1), "leather")
    w.box((9.0, 15.4, 7.6), (9.8, 16.6, 8.4), "iron")
    w.box((9.05, 13.4, 7.65), (9.75, 15.4, 8.35), "leather2")
    w.ring(-4.9, 0.5, "steel2", 2.2)
    w.cen((6.6, 27.6, 8), (0.7, 1.6, 0.7), "steel", ("z", 22.5))
    return w


# ---------------------------------------------------------------------------
# 2. Guadana del Ritual: vara quebrada, calavera con clavos, cadenas y candados
# ---------------------------------------------------------------------------
def ritual():
    w = G("guadana_2", "Guadana del Ritual", {
        "shaft": (hx("3d3d45"), "s"), "band": (hx("1a1a20"), "s"), "wood": (hx("5a3a24"), "s"),
        "blade": (hx("24242c"), "s"), "edge": (hx("b9bcc6"), "s"), "bone": (hx("e8dcc0"), "s"),
        "bone2": (hx("c8b898"), "s"), "eye": (hx("7dff6a"), "pulse"), "hole": (hx("17120e"), "s"),
        "nail": (hx("8a8f98"), "s"), "chain": (hx("6f747e"), "s"), "lock": (hx("d4a83a"), "s"),
        "curse": (hx("b6ff8a"), "spark"), "cloth": (hx("7a1414"), "s"), "runeg": (hx("7dff6a"), "flow"),
    })
    # punta de madera
    w.box((7.1, -7, 7.1), (8.9, -2.5, 8.9), "wood")
    w.ring(-3, 0.8, "band", 2.4)
    # vara quebrada en zigzag
    p = w.seg((8, -2.5), 90, 5.5, 1.8, "shaft", (7.1, 8.9))
    w.cen((p[0], p[1], 8), (2.4, 0.9, 2.4), "band")
    p = w.seg(p, 112.5, 5, 1.8, "shaft", (7.1, 8.9))
    w.cen((p[0], p[1], 8), (2.4, 0.9, 2.4), "band")
    p = w.seg(p, 67.5, 5, 1.8, "shaft", (7.1, 8.9))
    w.cen((p[0], p[1], 8), (2.4, 0.9, 2.4), "band")
    p = w.seg(p, 90, 3, 1.8, "shaft", (7.1, 8.9))
    w.box((7.1, p[1], 7.1), (8.9, 23.5, 8.9), "wood")
    for y in (p[1], 21.4):
        w.ring(y, 0.8, "band", 2.4)
    # hoja negra dentada con filo gris
    bp = w.blade((7.2, 23.4), [(180, 3.5, 3), (180, 3.5, 2.8), (202.5, 3.4, 2.4), (202.5, 3, 2.0), (225, 2.6, 1.4), (247.5, 2, 0.8)],
            "blade", edge="edge", teeth="blade", z=(7.65, 8.35))
    # calavera con clavos
    w.cen((9.6, 26.2, 8), (4.2, 3.6, 4.2), "bone")
    w.cen((9.6, 23.8, 8), (3.2, 1.3, 3.4), "bone2")
    for z in (5.85, 10.15):
        for x in (8.6, 10.6):
            w.cen((x, 26.2, z), (1.2, 1.2, 0.1), "hole")
            w.cen((x, 26.1, z + (0.06 if z > 8 else -0.06)), (0.5, 0.5, 0.1), "eye", None, 13)
        w.cen((9.6, 24.9, z), (0.6, 0.7, 0.1), "hole")
        for x in (8.7, 9.6, 10.5):
            w.cen((x, 23.6, z + (0.12 if z > 8 else -0.12)), (0.4, 0.5, 0.1), "bone")
    w.cen((8.4, 28.6, 8), (0.5, 2, 0.5), "nail", ("z", 22.5))
    w.cen((10.9, 28.7, 7.4), (0.5, 2, 0.5), "nail", ("z", -22.5))
    w.cen((9.8, 28.9, 8.6), (0.5, 2, 0.5), "nail", ("x", 22.5))
    for c in ((8.1, 29.6, 8), (11.3, 29.6, 7.4), (9.8, 29.8, 9)):
        w.cen(c, (0.9, 0.3, 0.9), "nail")
    # cadenas con candados
    for x0, y0 in ((9.4, 16.2), (6.0, 6.6)):
        for k in range(4):
            sz = (0.55, 0.9, 0.25) if k % 2 == 0 else (0.25, 0.9, 0.55)
            w.cen((x0 + (0.5 if x0 > 8 else -0.5), y0 - 0.85 * k, 8), sz, "chain")
        lx = x0 + (0.5 if x0 > 8 else -0.5)
        w.cen((lx, y0 - 3.9, 8), (1.1, 1.1, 0.6), "lock")
        w.cen((lx, y0 - 3.15, 8), (0.7, 0.5, 0.25), "chain")
        w.cen((lx, y0 - 4.0, 7.65), (0.3, 0.4, 0.1), "band")
    for c in ((5.6, 27.5, 8), (12.8, 25.4, 8), (4.2, 20.8, 8)):
        w.cen(c, (0.5, 0.5, 0.5), "curse", None, 14)
    # detalles: runas verdes en la hoja, trapo rojo, huesos cruzados, grietas y clavos en la vara
    for x, y in mids((7.2, 23.4), bp)[:4]:
        for z in (7.58, 8.42):
            w.cen((x, y, z), (0.8, 0.8, 0.1), "runeg", ("z", 45), 11)
    w.box((6.9, 21.9, 6.9), (9.1, 22.6, 9.1), "cloth")
    q = w.seg((6.9, 22.2), 247.5, 2.6, 0.8, "cloth", (7.7, 8.3))
    w.seg(q, 270, 1.6, 0.6, "cloth", (7.75, 8.25))
    w.cen((7.4, 22.6, 9.15), (2.6, 0.5, 0.5), "bone", ("z", 45))
    w.cen((7.4, 22.6, 9.15), (2.6, 0.5, 0.5), "bone2", ("z", -45))
    w.cen((10.5, 27.4, 5.85), (0.2, 1.2, 0.1), "hole")
    w.cen((10.7, 26.9, 5.85), (0.6, 0.2, 0.1), "hole")
    for c in ((8, 1.5, 6.95), (6.85, 9.5, 6.95), (8, 14.5, 6.95)):
        w.cen(c, (0.5, 0.5, 0.4), "nail")
    return w


# ---------------------------------------------------------------------------
# 3. Guadana del Vacio: negra con bordes de neon violeta, dos hojas, bobina y runa
# ---------------------------------------------------------------------------
def vacio():
    w = G("guadana_3", "Guadana del Vacio", {
        "dark": (hx("1d1426"), "s"), "dark2": (hx("2f2140"), "s"), "violet": (hx("5a2d8c"), "s"),
        "neon": (hx("ff3df5"), "flow"), "neon2": (hx("ff7bf8"), "pulse"), "metal": (hx("8d8d99"), "s"),
        "coil": (hx("3a2a50"), "s"), "void": (hx("e07bff"), "spark"),
    })
    # gancho del pomo con borde de neon
    w.blade((8, -3.5), [(270, 2, 1.8), (292.5, 1.8, 1.4), (315, 1.6, 1)], "dark2", edge="neon",
            side=1, edge_w=0.5, edge_glow=12)
    # empunadura con guarda en D
    w.box((7.1, -3.5, 7.1), (8.9, 5, 8.9), "dark")
    for y in (-3.2, 4.2):
        w.ring(y, 0.8, "violet", 2.4)
        w.box((6.75, y + 0.25, 6.75), (9.25, y + 0.55, 9.25), "neon2", None, 12)
    w.box((4.6, -1.2, 7.8), (5.1, 3.6, 8.2), "metal")
    w.box((4.6, -1.6, 7.8), (7.1, -1.1, 8.2), "metal")
    w.box((4.6, 3.6, 7.8), (7.1, 4.1, 8.2), "metal")
    # vara quebrada con uniones
    p = w.seg((8, 5), 90, 4.5, 1.6, "dark2", (7.2, 8.8))
    w.cen((p[0], p[1], 8), (2.2, 1, 2.2), "violet")
    p = w.seg(p, 112.5, 3, 1.6, "dark2", (7.2, 8.8))
    w.cen((p[0], p[1], 8), (2.2, 1, 2.2), "violet")
    p = w.seg(p, 67.5, 3, 1.6, "dark2", (7.2, 8.8))
    w.box((7.2, p[1], 7.2), (8.8, 27, 8.8), "dark")
    # emblema de runa
    w.cen((8, 17.4, 8), (3.4, 3.4, 1.6), "violet", ("z", 45))
    w.cen((8, 17.4, 8), (2.4, 2.4, 1.8), "neon2", ("z", 45), 13)
    w.cen((8, 17.4, 8), (1.6, 1.6, 2.0), "dark", ("z", 45))
    w.cen((8, 17.4, 8), (0.6, 0.6, 2.2), "neon2", ("z", 45), 15)
    # luces en la cabeza y punta
    for y in (21.2, 22.3, 23.4, 24.5):
        w.cen((8, y, 7.1), (0.6, 0.5, 0.2), "neon2", None, 13)
        w.cen((8, y, 8.9), (0.6, 0.5, 0.2), "neon2", None, 13)
    w.box((7.4, 27, 7.4), (8.6, 28.2, 8.6), "dark2")
    w.cen((8, 28.7, 8), (0.6, 1, 0.6), "neon2", None, 15)
    # bobina de aros hacia la derecha y contrahoja
    for k in range(5):
        x = 9.3 + 0.75 * k
        w.box((x, 21.6, 6.0), (x + 0.45, 26.4, 10.0), "coil" if k % 2 else "dark2")
        if k % 2:
            w.box((x + 0.1, 21.4, 5.8), (x + 0.35, 26.6, 10.2), "neon", None, 12)
    w.blade((12.9, 24), [(0, 1.8, 1.6), (22.5, 1.8, 1.3), (45, 1.6, 0.9)], "dark2", edge="neon",
            side=1, edge_w=0.5, edge_glow=12)
    # hoja grande y hoja chica
    bp = w.blade((7.4, 26), [(180, 4, 2.6), (180, 3.4, 2.4), (202.5, 3.2, 2.1), (225, 3, 1.7), (247.5, 2.4, 1.2), (270, 1.6, 0.7)],
            "dark2", edge="neon", edge_w=0.6, edge_glow=12, spine="violet")
    w.blade((7.4, 21.6), [(180, 3, 1.8), (202.5, 2.6, 1.5), (225, 2.2, 1.1), (247.5, 1.6, 0.6)],
            "dark2", edge="neon", edge_w=0.5, edge_glow=12)
    for c in ((3.4, 28.4, 8), (13.4, 28.6, 8), (2.2, 19.4, 8), (6.2, 14.2, 8)):
        w.cen(c, (0.6, 0.6, 0.6), "void", ("z", 45), 15)
    # detalles: cubos de vacio alrededor de la runa, luces en la vara, puas en la cabeza, puntos en la hoja
    for dx, dy in ((0, 3), (3, 0), (0, -3), (-3, 0)):
        w.cen((8 + dx, 17.4 + dy, 8), (0.6, 0.6, 0.6), "void", ("z", 45), 14)
    for z0, z1 in ((7.1, 7.2), (8.8, 8.9)):
        w.box((7.8, 5.6, z0), (8.2, 9.0, z1), "neon", None, 12)
    w.seg((8.8, 26.6), 45, 1.8, 0.6, "dark2", (7.7, 8.3))
    w.seg((8.8, 25.4), 22.5, 1.4, 0.5, "violet", (7.75, 8.25))
    for x, y in mids((7.4, 26), bp)[:4]:
        for z in (7.52, 8.48):
            w.cen((x, y, z), (0.5, 0.5, 0.1), "neon2", None, 13)
    w.cen((4.85, -2.0, 8), (0.4, 0.9, 0.4), "metal")
    w.cen((4.85, 4.5, 8), (0.4, 0.9, 0.4), "metal")
    return w


# ---------------------------------------------------------------------------
# 4. Guadana del Archimago: hoja de cristal turquesa, mango con marco abierto y aletas
# ---------------------------------------------------------------------------
def archimago():
    w = G("guadana_4", "Guadana del Archimago", {
        "navy": (hx("142235"), "s"), "navy2": (hx("22374f"), "s"), "prism": (hx("2fd6b0"), "pulse"),
        "prism2": (hx("4a7dd6"), "pulse"), "edge": (hx("b8fff2"), "pulse"), "fin": (hx("6fa8b8"), "s"),
        "fin2": (hx("3f6f86"), "s"), "gem": (hx("3fffe0"), "pulse"), "chip": (hx("9ffff0"), "spark"),
        "rune": (hx("4fd1ff"), "flow"),
    })
    # gancho de abajo
    w.blade((8, -4.5), [(270, 1.4, 1.8, "navy"), (202.5, 2.8, 1.6), (180, 2, 1.2), (157.5, 1.6, 0.8)],
            "navy2", edge="prism", side=1, edge_w=0.5, edge_glow=10)
    w.ring(-3.2, 0.8, "fin2", 2.4)
    w.box((7.0, -2.95, 7.0), (9.0, -2.65, 9.0), "gem", None, 12)
    # vara con marco abierto
    w.box((7.1, -4.5, 7.1), (8.9, 21, 8.9), "navy")
    w.box((7.15, -2.4, 7.15), (8.85, 3.5, 8.85), "navy2")
    w.box((10.2, 8.5, 7.5), (11.2, 15.5, 8.5), "fin")
    w.box((8.9, 7.6, 7.5), (11.2, 8.6, 8.5), "fin2")
    w.box((8.9, 15.4, 7.5), (11.2, 16.4, 8.5), "fin2")
    w.box((10.45, 10, 7.4), (10.95, 14, 8.6), "prism", None, 10)
    # guarda con aletas
    w.ring(16.6, 1.6, "navy2", 3)
    for side in (-1, 1):
        for k, (dy, ln, ang) in enumerate(((17.8, 3.4, 22.5), (17.0, 3.0, 45), (16.2, 2.4, 67.5))):
            a = 180 - ang if side < 0 else ang
            w.seg((8 + side * 1.2, dy), a, ln, 0.9, "fin" if k % 2 == 0 else "fin2", (7.45, 8.55))
    w.cen((8, 17.4, 6.4), (1.4, 1.4, 0.3), "gem", ("z", 45), 14)
    w.cen((8, 17.4, 9.6), (1.4, 1.4, 0.3), "gem", ("z", 45), 14)
    # cabeza
    w.cen((8, 23, 8), (3, 3.2, 3), "navy2")
    w.cen((8, 23.2, 6.45), (1.2, 1.2, 0.2), "gem", ("z", 45), 15)
    w.cen((8, 23.2, 9.55), (1.2, 1.2, 0.2), "gem", ("z", 45), 15)
    w.blade((9.4, 23.6), [(0, 1.8, 1.4), (22.5, 1.6, 1)], "prism", z=(7.65, 8.35))
    # hoja de cristal
    bp = w.blade((6.6, 23.6), [(180, 4.2, 3.4), (180, 3.6, 3.1), (202.5, 3.4, 2.7), (202.5, 3, 2.2), (225, 2.6, 1.6), (247.5, 2, 0.8)],
            "prism", edge="edge", edge_glow=12, spine="prism2", spine_w=0.8, z=(7.55, 8.45))
    for c in ((4.4, 27.8, 8), (0.4, 26.6, 8.6), (12.6, 27, 8)):
        w.cen(c, (0.7, 0.7, 0.7), "chip", ("z", 45), 15)
    # detalles: cristales que crecen del lomo, runas en la vara, puntas de las aletas, punta que brilla
    widths = (3.4, 3.1, 2.7, 2.2)
    for (x, y), wd, s in zip(bp[:4], widths, (1.3, 1.1, 0.9, 0.7)):
        w.gem((x + 0.4, y + wd / 2 + 0.5, 8), s, "prism2", 12, 1.7)
    for z0, z1 in ((7.0, 7.1), (8.9, 9.0)):
        w.box((7.7, 4.5, z0), (8.3, 7.4, z1), "rune", None, 11)
        w.box((7.7, 9.0, z0), (8.3, 16.4, z1), "rune", None, 11)
    import math as _m
    for side in (-1, 1):
        for dy, ln, ang in ((17.8, 3.4, 22.5), (17.0, 3.0, 45), (16.2, 2.4, 67.5)):
            a = _m.radians(180 - ang if side < 0 else ang)
            w.cen((8 + side * 1.2 + _m.cos(a) * ln, dy + _m.sin(a) * ln, 8), (0.6, 0.6, 0.6), "gem", ("z", 45), 13)
    w.cen((bp[-1][0], bp[-1][1], 8), (0.8, 0.8, 0.8), "edge", ("z", 45), 15)
    for c in ((2.4, 29.2, 8), (13.6, 21.6, 8)):
        w.cen(c, (0.6, 0.6, 0.6), "chip", ("z", 45), 15)
    return w


# ---------------------------------------------------------------------------
# 5. Guadana Astral: hoja de hueso y azul, mano de hueso, cristales turquesa y cadena flotante
# ---------------------------------------------------------------------------
def astral():
    w = G("guadana_5", "Guadana Astral", {
        "bone": (hx("efe6d6"), "s"), "bone2": (hx("c9b9a6"), "s"), "bone3": (hx("9d8c80"), "s"),
        "dark": (hx("1f1d26"), "s"), "dark2": (hx("2e2b36"), "s"), "blue": (hx("2a5677"), "s"),
        "blue2": (hx("1d3a55"), "s"), "tq": (hx("35c4c8"), "pulse"), "tq2": (hx("78ffe0"), "pulse"),
        "link": (hx("3a8fb0"), "spark"),
    })
    # pomo de hueso con cristal
    w.gem((8.2, -7.2, 8), 1.6, "tq", 13, 1.4)
    w.box((7, -6, 7), (9.4, -3.5, 9), "blue2")
    w.seg((9.4, -5), 337.5, 2.2, 0.9, "bone2", (7.55, 8.45))
    w.seg((7.0, -4.2), 202.5, 1.6, 0.8, "bone", (7.6, 8.4))
    # vara oscura con guarda turquesa
    w.box((7.15, -3.5, 7.15), (8.85, 22.5, 8.85), "dark")
    w.box((7.2, 2, 7.2), (8.8, 6, 8.8), "dark2")
    w.ring(7.2, 0.8, "bone2", 2.4)
    w.box((4.9, 1.2, 7.6), (5.9, 5.6, 8.4), "tq", None, 11)
    w.seg((5.4, 5.6), 45, 2.4, 0.9, "tq", (7.6, 8.4), 11)
    w.seg((5.4, 1.2), 315, 2.2, 0.9, "blue", (7.6, 8.4))
    # mano de hueso que agarra la cabeza
    w.cen((8.4, 24.4, 8), (2.8, 3.4, 2.8), "blue2")
    for k, y in enumerate((22.8, 23.9, 25.0)):
        w.box((6.8, y, 9.0), (10.2, y + 0.8, 9.8), "bone" if k % 2 == 0 else "bone2")
        w.box((10.0, y, 7.0), (10.6, y + 0.8, 9.8), "bone3")
    w.box((6.6, 23.2, 6.2), (9.6, 24.0, 7.0), "bone2")
    w.seg((9.8, 22.6), 300 - 7.5, 2.6, 0.8, "bone2", (7.6, 8.4))
    # cristales turquesa en la cabeza
    w.gem((10.6, 27.0, 8), 2.6, "tq", 14, 1.2)
    w.gem((9.0, 28.8, 8.4), 1.6, "tq2", 15, 1.3)
    w.gem((11.8, 25.2, 7.8), 1.2, "tq2", 13)
    # hoja: lomo de hueso blanco, cuerpo azul que se oscurece, punta blanca
    bp = w.blade((7.2, 25.4), [(180, 4.2, 3.2, "blue"), (180, 3.6, 3, "blue"), (180, 3.2, 2.6, "blue2"),
                          (202.5, 3, 2.1, "blue2"), (225, 2.4, 1.4, "blue2"), (247.5, 1.8, 0.8, "bone")],
            "blue", edge="dark2", edge_w=0.6, spine="bone", spine_w=1.0, side=-1)
    w.cen((5.8, 27.4, 8), (1.6, 0.6, 0.7), "bone2")
    w.cen((3.6, 27.2, 8), (1.2, 0.6, 0.7), "bone")
    # cadena turquesa flotando
    for k, (x, y) in enumerate(((12.6, 23.0), (13.1, 21.0), (13.3, 18.8), (13.0, 16.7), (12.4, 14.9), (11.9, 13.5))):
        w.cen((x, y, 8), (0.6, 1.3, 0.6), "link", ("z", -22.5 if k < 3 else 22.5), 13)
    # detalles: vertebras en la vara, venas turquesa en la hoja, cristales en el pomo, estrellas
    for y in (9.2, 11.4, 13.6, 15.8, 18.0, 20.2):
        w.ring(y, 0.55, "bone2", 2.2)
        w.box((7.6, y + 0.55, 6.85), (8.4, y + 1.1, 7.15), "bone3")
    for x, y in mids((7.2, 25.4), bp)[:4]:
        for z in (7.52, 8.48):
            w.cen((x, y - 0.3, z), (1.6, 0.35, 0.1), "tq", None, 12)
    w.gem((6.4, -5.2, 8), 0.9, "tq2", 13, 1.5)
    w.gem((10.0, -4.6, 8.2), 0.8, "tq2", 13, 1.5)
    for c in ((2.6, 29.4, 8), (14.2, 27.6, 8), (5.2, 18.6, 8)):
        w.cen(c, (0.5, 0.5, 0.5), "link", ("z", 45), 15)
    return w


# ---------------------------------------------------------------------------
# 6. Guadana Umbria (especial de la gacha): acero sombrio, filo violeta y gema umbria
# ---------------------------------------------------------------------------
def umbria():
    w = G("guadana_umbria", "Guadana Umbria", {
        "shadow": (hx("15101f"), "s"), "shadow2": (hx("2a2038"), "s"), "steel": (hx("4a3d5c"), "s"),
        "edge": (hx("c9a6ff"), "flow"), "rune": (hx("9b5cff"), "flow"), "gem": (hx("7d3cff"), "pulse"),
        "gem2": (hx("e0c8ff"), "pulse"), "smoke": (hx("b478ff"), "spark"),
    })
    # pomo con gema y pincho
    w.gem((8, -6.6, 8), 1.6, "gem", 13, 1.3)
    w.seg((8, -7.6), 270, 1.4, 0.6, "steel", (7.7, 8.3))
    w.box((6.8, -5.6, 6.8), (9.2, -3.8, 9.2), "steel")
    # vara con runas
    w.box((7.1, -3.8, 7.1), (8.9, 21, 8.9), "shadow")
    for y in (-1.5, 6.5, 14.5):
        w.ring(y, 0.9, "steel", 2.4)
    for y0, y1 in ((0, 5.5), (8, 13.5), (16, 20)):
        w.box((7.6, y0, 6.95), (8.4, y1, 7.05), "rune", None, 11)
        w.box((7.6, y0, 8.95), (8.4, y1, 9.05), "rune", None, 11)
    # garras que sostienen la gema umbria
    w.box((6.4, 20, 6.4), (9.6, 21.2, 9.6), "steel")
    w.seg((6.6, 21), 112.5, 3, 0.9, "steel", (7.55, 8.45))
    w.seg((9.4, 21), 67.5, 3, 0.9, "steel", (7.55, 8.45))
    w.gem((8, 23.2, 8), 2.8, "gem", 15, 1.3)
    w.cen((8, 23.2, 8), (1.2, 1.6, 2.6), "gem2", None, 15)
    # cabeza y contrapuas
    w.box((6.8, 25.2, 7.2), (9.6, 27.4, 8.8), "shadow2")
    w.blade((9.6, 26.4), [(22.5, 2.6, 1.3), (45, 1.6, 0.7)], "steel", z=(7.65, 8.35))
    w.cen((8.2, 28, 8), (0.8, 1.6, 0.8), "steel", ("z", 22.5))
    # hoja con filo de energia y cristales en el lomo
    pts = w.blade((7, 26.2), [(180, 4, 3.3), (180, 3.5, 3), (202.5, 3.4, 2.6), (202.5, 3, 2.1), (225, 2.6, 1.5), (247.5, 2, 0.8)],
                  "shadow2", edge="edge", edge_glow=13, spine="steel", spine_w=0.7)
    for (x, y), s in zip(pts[:3], (1.3, 1.1, 0.9)):
        w.gem((x + 0.6, y + 1.9, 8), s, "gem", 12, 1.5)
    for c in ((3.4, 29.6, 8), (12.6, 24.2, 8), (1.4, 22.0, 8.4), (11.2, 18.0, 7.6)):
        w.cen(c, (0.6, 0.6, 0.6), "smoke", ("z", 45), 15)
    # detalles: espiral de acero, anillo con gemas en el pomo, puas, zarcillos de sombra
    sides = [((6.9, 7.6), (7.1, 8.4)), ((7.6, 8.9), (8.4, 9.1)), ((8.9, 7.6), (9.1, 8.4)), ((7.6, 6.9), (8.4, 7.1))]
    for k, y in enumerate((-0.4, 0.6, 1.6, 2.6, 3.6, 4.6, 8.6, 9.6, 10.6, 11.6, 12.6)):
        (x0, z0), (x1, z1) = sides[k % 4]
        w.box((x0, y, z0), (x1, y + 0.6, z1), "steel")
    for c in ((6.7, -4.7, 8), (9.3, -4.7, 8), (8, -4.7, 6.7), (8, -4.7, 9.3)):
        w.cen(c, (0.5, 0.5, 0.5), "gem", ("y", 45), 13)
    w.seg((7.1, 19.6), 202.5, 1.6, 0.5, "steel", (7.75, 8.25))
    w.seg((8.9, 19.6), 337.5, 1.6, 0.5, "steel", (7.75, 8.25))
    for c, sz in (((10.4, 22.4, 8), 0.8), ((11.2, 21.2, 8.3), 0.6), ((11.6, 19.9, 7.8), 0.45),
                  ((5.6, 21.6, 8), 0.7), ((4.9, 20.4, 7.7), 0.5)):
        w.cen(c, (sz, sz, sz), "shadow2", ("z", 45))
    return w


SCYTHES = [umbria_menor(), ritual(), vacio(), archimago(), astral(), umbria()]


def assets():
    return v.assets(SCYTHES)


if __name__ == "__main__":
    for p in v.check(SCYTHES):
        print("AVISO:", p)
    out = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "build", "previews",
                                       "guadanas_3d.gif"))
    v.preview(out, SCYTHES, W=230)
    print("vista previa ->", out)
    print("cubos por guadana:", {w.iid: len(w.els) for w in SCYTHES})
