# -*- coding: utf-8 -*-
"""
Armas 3D: espadas, hachas, Guantes de Puno Meteoro y arcos (con sus 3 modelos de tensado).

Mismo motor que los bastones y guadanas (varitas3d.py): cubos + textura de muestras
de 8x8 con partes animadas. Todo va parado en x=8, z=8; la mano agarra cerca de y=1
(los arcos, en el medio: y=8). La hoja del hacha sale hacia -x, como el icono vanilla.

Uso:
  python armas3d.py   vistas previas -> ../build/previews/{espadas,hachas,arcos}_3d.gif
build_pack.py llama a assets() para meterlas en el resource pack.

Inspiracion (imagenes de otros autores, fuera del repo): docs/REFERENCIAS_ARMAS.md
"""
import json
import os

import varitas3d as v
from varitas3d import Wand, hx

TEX_DIR = "item/armas3d"


def W(iid, name, palette, **kw):
    return Wand(iid, name, palette, tilt=kw.pop("tilt", -25), tex_dir=TEX_DIR, **kw)


# ---------------------------------------------------------------------------
# Piezas comunes
# ---------------------------------------------------------------------------
def add_sw(w, name, color, kind="s"):
    """Agrega una muestra de color a un arma ya creada (los modelos de un arco comparten la paleta)."""
    if name not in w.slots:
        w.palette[name] = (hx(color), kind)
        w.slots[name] = len(w.slots)
    assert len(w.slots) <= 16, w.iid


def sword_blade(w, y0, y1, wd, sw, edge=None, fuller=None, tip=4.0, z=(7.5, 8.5), glow=0, edge_glow=0,
                fuller_glow=0, tip_sw=None, ridge=None, bevel=None):
    """Hoja recta con volumen: nervio central grueso, cuerpo, biseles mas finos y filos finitos a los costados."""
    yb = y1 - tip
    rd = max(0.8, wd * 0.34)
    bv = min(0.7, wd * 0.18)
    w.box((8 - wd / 2 + bv, y0, z[0]), (8 + wd / 2 - bv, yb, z[1]), sw, None, glow)
    for sd in (-1, 1):
        xa, xb = 8 + sd * (wd / 2 - bv), 8 + sd * wd / 2
        w.box((min(xa, xb), y0 + 0.2, z[0] + 0.18), (max(xa, xb), yb, z[1] - 0.18), bevel or sw, None, glow)
    w.box((8 - rd / 2, y0, z[0] - 0.22), (8 + rd / 2, yb + tip * 0.3, z[1] + 0.22), ridge or sw, None, glow)
    steps = 4
    for k in range(steps):
        f = 1 - (k + 1) / (steps + 1.2)
        h = tip / (steps + 1)
        w.box((8 - wd * f / 2, yb + h * k, z[0] + 0.08 * k), (8 + wd * f / 2, yb + h * (k + 1), z[1] - 0.08 * k),
              tip_sw or sw, None, glow)
    w.cen((8, y1 - tip / (steps + 1) * 0.6, 8), (wd * 0.22, wd * 0.22, z[1] - z[0] - 0.3), tip_sw or edge or sw,
          ("z", 45), glow or edge_glow)
    if edge:
        for sd in (-1, 1):
            x0 = 8 + sd * wd / 2
            w.box((min(x0, x0 + sd * 0.45), y0 + 0.5, z[0] + 0.32), (max(x0, x0 + sd * 0.45), yb, z[1] - 0.32),
                  edge, None, edge_glow)
            # el filo sigue por la punta en escalones
            for k in range(3):
                f = 1 - (k + 1) / (steps + 1.2)
                h = tip / (steps + 1)
                xe = 8 + sd * wd * f / 2
                w.box((min(xe, xe + sd * 0.4), yb + h * k, z[0] + 0.35), (max(xe, xe + sd * 0.4), yb + h * (k + 1),
                      z[1] - 0.35), edge, None, edge_glow)
    if fuller:
        for zz in (z[0] - 0.27, z[1] + 0.27):
            w.box((8 - rd * 0.25, y0 + 1, zz - 0.04), (8 + rd * 0.25, yb - 0.5, zz + 0.04), fuller, None, fuller_glow)


def grip(w, y0, y1, a, b, wd=1.6, step=1.0):
    """Mango con vendas alternadas que sobresalen un poco (se ven enrolladas)."""
    w.box((8 - wd / 2, y0, 8 - wd / 2), (8 + wd / 2, y1, 8 + wd / 2), b)
    k = 0
    y = y0
    while y < y1 - 0.01:
        h = min(step, y1 - y)
        if k % 2 == 0:
            e = 0.12
            w.box((8 - wd / 2 - e, y + 0.05, 8 - wd / 2 - e), (8 + wd / 2 + e, y + h - 0.05, 8 + wd / 2 + e), a)
        y += h
        k += 1


def axe_head(w, x_in, x_out, yc, h_in, h_out, sw, edge=None, edge_glow=0, z=(7.4, 8.6), cols=6, sw2=None,
             beard=0.0, rim=None):
    """Hoja de hacha: columnas que se abren desde x_in hasta x_out (sirve para los dos lados).
    Es mas gruesa junto al mango y se afina hacia el filo; rim pone un borde en relieve arriba y abajo."""
    s = 1 if x_out > x_in else -1
    cw = abs(x_out - x_in) / cols
    for k in range(cols):
        f = (k + 0.5) / cols
        h = h_in + (h_out - h_in) * f ** 1.4
        xa = x_in + s * cw * k
        yo = -beard * f ** 2
        zt = 0.3 - 0.5 * f
        z0, z1 = z[0] - zt, z[1] + zt
        lo, hi = yc - h / 2 + yo, yc + h / 2 + yo * 0.3
        x0, x1 = min(xa, xa + s * cw), max(xa, xa + s * cw) + 0.02
        w.box((x0, lo, z0), (x1, hi, z1), sw2 if (sw2 and k % 2) else sw)
        if rim:
            w.box((x0, hi - 0.45, z0 - 0.08), (x1, hi, z1 + 0.08), rim)
            w.box((x0, lo, z0 - 0.08), (x1, lo + 0.45, z1 + 0.08), rim)
    if edge:
        xe = x_out
        w.box((min(xe, xe + s * 0.6), yc - h_out / 2 - beard - 0.2, z[0] + 0.3),
              (max(xe, xe + s * 0.6), yc + h_out / 2 - beard * 0.3 + 0.2, z[1] - 0.3), edge, None, edge_glow)


# ---------------------------------------------------------------------------
# ESPADAS
# ---------------------------------------------------------------------------
# Los perfiles, biseles y monturas detalladas de las cinco espadas viven en
# su propio generador. Hachas, arcos y guantelete conservan sus constructores.
from espadas3d import (espada_saqueador, espada_carnicero, espada_ensangrentada,
                      espada_coloso, espada_dios_guerra)


# ---------------------------------------------------------------------------
# HACHAS
# ---------------------------------------------------------------------------
def hacha_desollador():
    w = W("hacha_1", "Hacha del Desollador", {
        "stone": (hx("8a8e96"), "s"), "stone2": (hx("5a5e66"), "s"), "edge": (hx("d6dbe2"), "s"),
        "wood": (hx("6a4a2e"), "s"), "wood2": (hx("4a3220"), "s"), "wrap": (hx("8a5a3a"), "s"),
        "gem": (hx("e0303a"), "pulse"), "iron": (hx("4a4e56"), "s"),
    })
    w.box((7.1, -6, 7.1), (8.9, 25, 8.9), "wood")
    grip(w, -5, 3, "wrap", "wood2", 2.0)
    w.ring(-6.4, 0.9, "iron", 2.2)
    w.box((6.6, 19, 6.6), (9.6, 26, 9.4), "stone2")
    axe_head(w, 6.6, 0.6, 22.6, 5.0, 9.0, "stone", edge="edge", cols=6, sw2="stone2", beard=1.4, rim="stone2")
    w.blade((9.6, 24), [(0, 1.8, 1.2), (337.5, 1.8, 0.9), (292.5, 1.4, 0.6)], "iron")   # gancho de desollar
    w.cen((5.0, 22.6, 7.3), (1.2, 1.2, 0.2), "gem", ("z", 45), 13)
    w.cen((5.0, 22.6, 8.7), (1.2, 1.2, 0.2), "gem", ("z", 45), 13)
    w.box((7.0, 26, 7.0), (9.0, 27, 9.0), "iron")
    # detalles: correas de cuero que atan la cabeza, remaches, mellas, pua arriba
    add_sw(w, "notch", "2a2c30")
    for y in (19.4, 25.4):
        w.box((6.4, y, 6.4), (9.8, y + 0.6, 9.6), "wrap")
    for (x, y) in ((5.6, 25), (5.6, 20.2), (3.4, 24.4), (3.4, 20.6)):
        for z in (7.05, 8.95):
            w.cen((x, y, z), (0.45, 0.45, 0.12), "iron")
    for y in (20.0, 24.2):
        w.cen((0.7, y, 8), (0.6, 0.7, 0.8), "notch")
    w.seg((8, 27), 90, 1.8, 0.7, "iron", (7.65, 8.35))
    return w


def hacha_verdugo():
    w = W("hacha_2", "Hacha del Verdugo", {
        "black": (hx("2e3038"), "s"), "black2": (hx("1f2026"), "s"), "edge": (hx("c9ced6"), "s"),
        "stud": (hx("8a8f98"), "s"), "shaft": (hx("1f1d22"), "s"), "band": (hx("7a1414"), "s"),
        "bone": (hx("e8dcc0"), "s"), "hole": (hx("17120e"), "s"), "eye": (hx("ff3b3b"), "pulse"),
    })
    w.box((7.1, -6.5, 7.1), (8.9, 25.5, 8.9), "shaft")
    for y in (-5.5, -1, 3.5, 12, 17):
        w.ring(y, 0.8, "band", 2.3)
    w.box((6.5, 17.5, 6.5), (9.7, 26.5, 9.5), "black2")
    axe_head(w, 6.5, -0.6, 22.0, 7.5, 12.5, "black", edge="edge", cols=7, sw2="black2", beard=2.2, rim="black2")
    for (x, y) in ((4.6, 25), (2.2, 25.6), (4.6, 18.6), (2.2, 17.4), (0.6, 21.6)):
        for z in (7.32, 8.68):
            w.cen((x, y, z), (0.6, 0.6, 0.15), "stud")
    # calavera chica en la cabeza
    w.cen((10.6, 22.4, 8), (2.4, 2.4, 2.4), "bone")
    for z in (6.75, 9.25):
        for x in (10.1, 11.1):
            w.cen((x, 22.7, z), (0.6, 0.6, 0.1), "hole")
            w.cen((x, 22.7, z + (-0.04 if z < 8 else 0.04)), (0.3, 0.3, 0.1), "eye", None, 12)
    w.cen((8, 27, 8), (1.2, 1.2, 1.2), "stud", ("y", 45))
    # detalles: manchas de sangre, cadena con gancho, martillo atras, pua arriba
    add_sw(w, "blood", "7a1414", "pulse")
    for (x, y, sz) in ((3.0, 22.8, 1.2), (1.4, 19.2, 0.9), (4.2, 20.0, 0.7)):
        for z in (7.12, 8.88):
            w.cen((x, y, z), (sz, sz * 1.3, 0.1), "blood", None, 8)
    for k in range(4):
        sz = (0.5, 0.9, 0.25) if k % 2 == 0 else (0.25, 0.9, 0.5)
        w.cen((9.9, 17.0 - 0.85 * k, 8), sz, "stud")
    w.seg((9.9, 13.6), 270, 1.0, 0.4, "stud", (7.8, 8.2))
    w.box((9.7, 20.2, 7.1), (11.6, 21.6, 8.9), "black2")
    w.seg((8, 27.6), 90, 1.6, 0.8, "stud", (7.6, 8.4))
    return w


def hacha_carmesi():
    w = W("hacha_3", "Hacha Carmesi", {
        "red": (hx("c0182c"), "s"), "red2": (hx("7a0c18"), "s"), "edge": (hx("ff7a1a"), "flicker"),
        "wood": (hx("3a2418"), "s"), "wood2": (hx("5a3a24"), "s"), "gold": (hx("d4a83a"), "s"),
        "ember": (hx("ffb02e"), "pulse"), "drop": (hx("ff4d5e"), "spark"),
    })
    w.box((7.1, -6, 7.1), (8.9, 25, 8.9), "wood")
    grip(w, -5, 3, "wood2", "red2", 2.0)
    for y in (3.5, 16.5):
        w.ring(y, 0.8, "gold", 2.4)
    w.box((6.6, 18.5, 6.6), (9.5, 26, 9.4), "red2")
    axe_head(w, 6.6, 0.2, 22.4, 5.5, 10.5, "red", edge="edge", edge_glow=13, cols=6, sw2="red2", beard=1.8, rim="gold")
    w.blade((9.5, 22.4), [(0, 1.6, 2.4), (0, 1.4, 1.6), (0, 1.0, 0.8)], "red", z=(7.6, 8.4))
    for (x, y) in ((4.6, 22.6), (2.4, 21.6)):
        for z in (7.32, 8.68):
            w.cen((x, y, z), (1.0, 1.0, 0.15), "ember", ("z", 45), 13)
    w.gem((8, -7.0, 8), 1.4, "ember", 13, 1.4)
    for c in ((0.4, 16.0, 8), (1.6, 14.2, 8)):
        w.cen(c, (0.5, 0.7, 0.5), "drop", None, 14)
    # detalles: lineas doradas grabadas, puas en el martillo de atras, borla roja, gema en el ojo del hacha
    for z in (7.04, 8.96):
        w.seg((6.2, 24.6), 157.5, 3.6, 0.3, "gold", (z - 0.04, z + 0.04))
        w.seg((6.2, 20.2), 202.5, 3.6, 0.3, "gold", (z - 0.04, z + 0.04))
    for y in (21.6, 23.2):
        w.cen((13.4, y, 8), (0.7, 0.7, 0.7), "gold", ("z", 45))
    w.box((7.0, 16.0, 6.95), (9.0, 17.0, 9.05), "red2")
    w.box((9.1, 14.2, 7.9), (9.3, 16.4, 8.1), "gold")
    w.box((8.85, 12.4, 7.65), (9.55, 14.2, 8.35), "red")
    w.cen((8, 22.4, 6.5), (1.2, 1.2, 0.3), "ember", ("z", 45), 13)
    w.cen((8, 22.4, 9.5), (1.2, 1.2, 0.3), "ember", ("z", 45), 13)
    return w


def hacha_coloso():
    w = W("hacha_4", "Hacha del Coloso", {
        "ice": (hx("8fc3ff"), "s"), "ice2": (hx("cfe8ff"), "s"), "ice3": (hx("5f8fd6"), "s"),
        "rune": (hx("4fb8ff"), "flow"), "shaft": (hx("3a1f45"), "s"), "shaft2": (hx("55306a"), "s"),
        "gold": (hx("d9c38a"), "s"), "crystal": (hx("5ff0f0"), "pulse"), "frost": (hx("e6fbff"), "spark"),
    })
    w.gem((8, -7.8, 8), 2.0, "crystal", 14, 1.4)
    w.ring(-6.6, 1.2, "gold", 2.4)
    w.box((7.1, -5.4, 7.1), (8.9, 25.5, 8.9), "shaft")
    for y in (-5.4, 4, 15):
        w.ring(y, 1.0, "gold", 2.5)
    w.box((7.15, 6, 7.15), (8.85, 7.2, 8.85), "rune", None, 11)
    w.box((6.4, 18, 6.4), (9.6, 27, 9.6), "ice3")
    for s in (-1, 1):                                           # hacha doble de hielo
        axe_head(w, 8 + s * 1.6, 8 + s * 7.6, 22.5, 6.5, 12.0, "ice", edge="ice2", edge_glow=8, cols=6,
                 sw2="ice3", z=(7.35, 8.65), rim="ice2")
        for y in (20.4, 22.5, 24.6):
            for z in (7.29, 8.71):
                w.box((min(8 + s * 2.6, 8 + s * 6.0), y - 0.25, z - 0.03), (max(8 + s * 2.6, 8 + s * 6.0), y + 0.25, z + 0.03),
                      "rune", None, 12)
    w.cen((8, 27.6, 8), (1.6, 1.6, 1.6), "crystal", ("y", 45), 14)
    for c in ((1.0, 28.6, 8), (15.0, 17.0, 8), (2.4, 15.4, 8.3)):
        w.cen(c, (0.5, 0.5, 0.5), "frost", ("z", 45), 15)
    # detalles: carambanos colgando, corona de cristales, aro con gemas, escarcha en el mango
    for sd in (-1, 1):
        for (dx, ln) in ((3.0, 1.6), (4.6, 2.2), (6.2, 1.4)):
            w.seg((8 + sd * dx, 17.0), 270, ln, 0.5, "ice2", (7.8, 8.2), 8)
        w.gem((8 + sd * 1.6, 28.0, 8), 1.0, "crystal", 13, 1.8)
    for (dx, dz) in ((1.3, 0), (-1.3, 0), (0, 1.3), (0, -1.3)):
        w.cen((8 + dx, 4.5, 8 + dz), (0.6, 0.6, 0.6), "crystal", ("y", 45), 13)
    for y in (8.0, 11.0):
        for z in (7.0, 9.0):
            w.cen((8, y, z), (0.6, 0.6, 0.12), "frost", ("z", 45), 13)
    return w


def hacha_apocalipsis():
    w = W("hacha_5", "Hacha del Apocalipsis", {
        "iron": (hx("3a3a40"), "s"), "iron2": (hx("26262c"), "s"), "steel": (hx("8a8e96"), "s"),
        "lava": (hx("ff5a1a"), "flicker"), "lava2": (hx("ffc040"), "flicker"), "bone": (hx("e8dcc0"), "s"),
        "hole": (hx("17120e"), "s"), "horn": (hx("b3261e"), "s"), "horn2": (hx("6d1410"), "s"),
        "gem": (hx("ff2a2a"), "pulse"), "ember": (hx("ffcf6a"), "spark"),
    })
    # pomo con aro y gema
    w.blade((8, -5.6), [(270, 1.2, 1.4, "iron2"), (315, 1.6, 1.0), (22.5, 1.6, 0.8)], "horn")
    w.gem((8, -6.6, 8), 1.2, "gem", 13, 1.2)
    w.box((7.1, -5.6, 7.1), (8.9, 26, 8.9), "iron2")
    for k, y in enumerate([-4.8 + 1.6 * i for i in range(10)]):
        w.ring(y, 0.5, "steel" if k % 2 else "iron", 2.3)
    for y in (12, 14, 16):                                      # puas de la vara
        for s in (-1, 1):
            w.cen((8 + s * 1.3, y, 8), (0.7, 0.7, 0.7), "steel", ("z", 45))
    w.box((7.4, 10, 6.95), (8.6, 17, 7.05), "lava", None, 13)
    w.box((7.4, 10, 8.95), (8.6, 17, 9.05), "lava", None, 13)
    w.box((6.2, 18, 6.2), (9.8, 27.5, 9.8), "iron")
    for s in (-1, 1):                                           # hacha doble con vetas de lava
        axe_head(w, 8 + s * 1.8, 8 + s * 8.2, 22.8, 7.0, 13.0, "iron", edge="steel", cols=6, sw2="iron2",
                 z=(7.35, 8.65), beard=0.8, rim="steel")
        for (dx, dy, sz) in ((3.4, 24.8, 1.3), (4.8, 21.0, 1.1), (6.4, 25.6, 0.9), (6.6, 18.8, 0.9)):
            for z in (7.29, 8.71):
                w.cen((8 + s * dx, dy, z), (sz, sz, 0.08), "lava", ("z", 45), 13)
        # cuernos rojos que suben
        p = w.seg((8 + s * 1.6, 26.4), 90 + s * 22.5, 2.2, 1.2, "horn", (7.4, 8.6))
        p = w.seg(p, 90 - s * 22.5, 1.6, 0.9, "horn2", (7.5, 8.5))
        w.seg(p, 90 - s * 45, 1.4, 0.6, "horn", (7.55, 8.45))
    # calavera en el centro
    w.cen((8, 22.8, 8), (3.2, 3.0, 3.8), "bone")
    for z in (6.05, 9.95):
        for x in (7.3, 8.7):
            w.cen((x, 23.2, z), (0.8, 0.8, 0.1), "hole")
            w.cen((x, 23.2, z + (-0.04 if z < 8 else 0.04)), (0.4, 0.4, 0.1), "lava2", None, 14)
        w.cen((8, 22.0, z), (0.5, 0.5, 0.1), "hole")
    for c in ((1.0, 30.0, 8), (15.2, 29.0, 8), (2.4, 14.6, 8), (13.8, 15.6, 8)):
        w.cen(c, (0.6, 0.6, 0.6), "ember", ("z", 45), 15)
    # detalles: llamas sobre la calavera, mandibula, cadenas cortas a los lados
    for (x, y, sz) in ((7.2, 25.2, 0.9), (8.0, 25.8, 1.1), (8.8, 25.2, 0.9)):
        w.cen((x, y, 8), (sz, sz * 1.5, sz), "lava", ("y", 45), 14)
    w.cen((8, 21.0, 8), (2.4, 0.8, 3.2), "bone")
    for x in (7.3, 8.0, 8.7):
        for z in (6.35, 9.65):
            w.cen((x, 21.0, z), (0.3, 0.5, 0.1), "hole")
    return w


# ---------------------------------------------------------------------------
# GUANTES DE PUNO METEORO
# ---------------------------------------------------------------------------
def guantes_meteoro():
    w = W("guantes_meteoro", "Guantes de Puno Meteoro", {
        "red": (hx("c0392b"), "s"), "red2": (hx("8a2318"), "s"), "plate": (hx("e05a2a"), "s"),
        "dark": (hx("3a2a2a"), "s"), "steel": (hx("a0a4ac"), "s"), "core": (hx("ffb02e"), "flicker"),
        "core2": (hx("fff0b0"), "pulse"), "flame": (hx("ff6a1a"), "flicker"), "ember": (hx("ffcf6a"), "spark"),
    }, tilt=-35)
    # puno cerrado (con bordes biselados para que no parezca una caja)
    w.box((4.6, 1.0, 4.8), (11.4, 7.0, 11.2), "red")
    for s in (-1, 1):
        w.box((8 + s * 3.4 - 0.4, 1.4, 5.2), (8 + s * 3.4 + 0.4, 6.6, 10.8), "red2")
    w.box((5.0, 7.0, 6.0), (11.0, 7.6, 10.6), "red2")
    for c in ((6.0, 8.6, 8.4), (8.0, 9.4, 8.8), (10.0, 8.8, 8.2)):
        w.cen(c, (1.2, 1.8, 1.2), "flame", ("y", 45), 14)
    w.cen((8.0, 10.6, 8.6), (0.7, 1.0, 0.7), "core", None, 15)
    for k, x in enumerate((4.8, 6.5, 8.2, 9.9)):               # dedos con nudillos
        w.box((x, 4.6, 4.2), (x + 1.5, 7.4, 6.0), "plate" if k % 2 == 0 else "red2")
        w.box((x + 0.1, 4.2, 3.7), (x + 1.4, 5.4, 4.3), "plate")
        w.cen((x + 0.75, 6.0, 4.0), (0.9, 0.9, 0.9), "steel", ("z", 45))
    w.box((4.0, 1.4, 6.0), (4.8, 4.8, 9.0), "plate")            # pulgar
    w.box((4.2, 4.0, 4.6), (5.4, 5.0, 6.4), "plate")
    # placas del dorso y nucleo de meteoro
    w.box((5.2, 1.4, 11.2), (10.8, 6.6, 11.8), "red2")
    w.cen((8, 4.0, 11.9), (2.6, 2.6, 0.6), "dark", ("z", 45))
    w.cen((8, 4.0, 12.1), (1.8, 1.8, 0.5), "core", ("z", 45), 15)
    w.cen((8, 4.0, 12.3), (0.8, 0.8, 0.4), "core2", ("z", 45), 15)
    for s in (-1, 1):
        w.cen((8 + s * 2.6, 6.2, 11.6), (1.2, 0.8, 0.6), "steel")
    # puno de abajo: munequera con llamas
    w.box((4.4, -5.5, 5.0), (11.6, 1.0, 11.0), "dark")
    for y in (-5.0, -2.2, 0.2):
        w.box((4.2, y, 4.8), (11.8, y + 0.8, 11.2), "plate")
    for k, x in enumerate((5.0, 7.0, 9.0, 11.0)):              # puas de la munequera
        w.cen((x, -1.0, 4.6), (0.8, 0.8, 0.8), "steel", ("z", 45))
        w.cen((x, -1.0, 11.4), (0.8, 0.8, 0.8), "steel", ("z", 45))
    for c, sz in (((4.0, -3.8, 8.0), 1.4), ((12.0, -3.0, 8.0), 1.2), ((3.4, -1.6, 9.0), 0.9),
                  ((12.6, -0.8, 7.0), 0.8)):
        w.cen(c, (sz, sz * 1.4, sz), "flame", ("y", 45), 14)
    for c in ((3.2, 8.4, 8), (12.6, 9.2, 8), (8, 10.4, 6)):
        w.cen(c, (0.6, 0.6, 0.6), "ember", ("z", 45), 15)
    # detalles: segunda fila de nudillos, grietas de lava en las placas, remaches, placas del antebrazo en capas
    for x in (5.55, 7.25, 8.95, 10.65):
        w.box((x - 0.6, 2.2, 4.4), (x + 0.6, 3.6, 4.9), "red2")
    for (x, y, ang) in ((5.6, 2.0, 67.5), (10.4, 2.4, 112.5)):
        for z in (11.84,):
            w.seg((x, y), ang, 2.2, 0.25, "core", (z - 0.04, z + 0.06), 13)
    for x in (5.0, 11.0):
        for y in (2.0, 6.0):
            w.cen((x, y, 11.85), (0.45, 0.45, 0.12), "steel")
    for k, y in enumerate((-4.6, -3.2, -1.8)):
        w.box((4.0 - 0.1 * k, y, 6.0), (4.4, y + 1.1, 10.0), "red")
        w.box((11.6, y, 6.0), (12.0 + 0.1 * k, y + 1.1, 10.0), "red")
    return w


# ---------------------------------------------------------------------------
# ARCOS: 4 modelos cada uno (quieto y 3 de tensado). Empunadura en (6, 8); la cuerda a +x.
# ---------------------------------------------------------------------------
PULLS = (0.0, 1.6, 3.0, 4.4)   # cuanto se tira la cuerda en cada modelo
ARROW = {"ashaft": (hx("8a6a44"), "s"), "ahead": (hx("c9ced6"), "s"), "afletch": (hx("f2f2f2"), "s")}


def _string(w, top, bot, pull, sw, glow=0, th=0.32):
    """Cuerda como linea de pixeles: recta o en V hacia +x."""
    if pull == 0:
        x = top[0]
        w.box((x - th / 2, bot[1], 8 - th / 2), (x + th / 2, top[1], 8 + th / 2), sw, None, glow)
        return
    mid = (top[0] + pull, 8.0)
    for a, b in ((top, mid), (mid, bot)):
        # Pasos suficientemente finos para que la cuerda diagonal sea continua.
        # Con nueve barras quedaban huecos visibles al tensar al maximo.
        n = max(9, int(abs(b[0]-a[0])/(th*.55))+1, int(abs(b[1]-a[1])/.45)+1)
        for k in range(n):
            y0 = a[1] + (b[1] - a[1]) * k / n
            y1 = a[1] + (b[1] - a[1]) * (k + 1) / n
            x = a[0] + (b[0] - a[0]) * (k + 0.5) / n
            w.box((x - th / 2, min(y0, y1), 8 - th / 2), (x + th / 2, max(y0, y1) + 0.02, 8 + th / 2), sw, None, glow)


def _arrow(w, nock_x):
    tip = nock_x - 15
    w.box((tip + 1.2, 7.8, 7.8), (nock_x, 8.2, 8.2), "ashaft")
    w.cen((tip + 0.8, 8, 8), (1.4, 1.4, 0.3), "ahead", ("z", 45))
    for s in (-1, 1):
        w.box((nock_x - 2.6, 8 + s * 0.2, 7.9), (nock_x - 0.4, 8 + s * 0.75, 8.1), "afletch")


def bow(iid, name, palette, build, string_sw, string_glow=0):
    """Arma los 4 modelos de un arco. build(w) dibuja el arco y devuelve (punta_arriba, punta_abajo)."""
    out = []
    pal = dict(palette, **ARROW)
    for k, pull in enumerate(PULLS):
        mid = iid if k == 0 else f"{iid}_pulling_{k - 1}"
        w = Wand(mid, name, pal, tilt=-20, tex_dir=TEX_DIR, hand="bow", tex_name=iid)
        top, bot = build(w)
        _string(w, top, bot, pull, string_sw, string_glow)
        if pull:
            _arrow(w, top[0] + pull)
        out.append(w)
    return out


def _limbs(w, segs, sw, grip_sw, start=(6.0, 8.0), half=1.6, spine=None, edge=None, cap=None):
    """Brazos simetricos desde la empunadura. segs = [(angulo hacia arriba, largo, ancho[, color])].
    spine = lomo de atras, edge = franja del lado de la cuerda, cap = puntas con muesca."""
    top = w.blade((start[0], start[1] + half), segs, sw, spine=spine, edge=edge, side=-1, edge_w=0.35,
                  spine_w=0.45, z=(7.3, 8.7))
    down = [(360 - a if a else 0, l, wd) + tuple(r) for a, l, wd, *r in segs]
    bot = w.blade((start[0], start[1] - half), down, sw, spine=spine, edge=edge, side=1, edge_w=0.35,
                  spine_w=0.45, z=(7.3, 8.7))
    # empunadura con bordes y apoyo para la flecha
    w.box((start[0] - 0.9, start[1] - half - 0.2, 7.0), (start[0] + 0.9, start[1] + half + 0.2, 9.0), grip_sw)
    for dy in (-half - 0.2, half - 0.2):
        w.box((start[0] - 1.1, start[1] + dy, 6.85), (start[0] + 1.1, start[1] + dy + 0.4, 9.15), spine or grip_sw)
    w.box((start[0] + 0.9, start[1] - 0.1, 7.7), (start[0] + 1.4, start[1] + 0.5, 8.3), spine or grip_sw)
    if cap:
        for t in (top[-1], bot[-1]):
            w.cen((t[0], t[1], 8), (1.1, 1.1, 1.6), cap, ("z", 45))
    return top, bot


def arco_rastreador():
    def build(w):
        top, bot = _limbs(w, [(90, 2.4, 1.6), (67.5, 3.4, 1.4), (45, 3.4, 1.2, "wood2"), (22.5, 1.8, 0.9)],
                          "wood", "leather", spine="wood2", edge="leather2", cap="leather2")
        for y in (6.6, 8.0, 9.4):
            w.box((5.0, y - 0.25, 7.0), (7.0, y + 0.25, 9.0), "leather2")
        for s in (1, -1):                                       # hojas en las puntas y en los brazos
            t = (top if s > 0 else bot)[-1]
            w.cen((t[0] - 0.4, t[1] - s * 0.4, 8), (1.4, 0.8, 0.5), "leaf", ("z", s * 22.5))
            w.cen((6.9, 8 + s * 4.8, 8.6), (1.2, 0.7, 0.4), "leaf2", ("z", -s * 22.5))
        w.box((5.1, 3.0, 7.9), (5.3, 5.2, 8.1), "leather2")      # pluma colgando
        w.cen((5.2, 2.4, 8), (0.8, 1.4, 0.3), "feather")
        # detalles: enredadera que sube por los brazos, plumas en la pluma, nudos de cuero
        for pts, sd in ((top, 1), (bot, -1)):
            for k, (x, y) in enumerate(pts[:3]):
                w.cen((x - 0.5, y, 8.75 if k % 2 else 7.25), (0.8, 0.5, 0.3), "leaf2" if k % 2 else "leaf", ("z", sd * 45))
        w.cen((5.2, 1.4, 8), (0.5, 0.9, 0.25), "feather")
        w.box((4.9, 5.0, 7.7), (5.5, 5.5, 8.3), "leather")
        return top[-1], bot[-1]
    return bow("arco_1", "Arco del Rastreador", {
        "wood": (hx("7a5230"), "s"), "wood2": (hx("5a3a20"), "s"), "leather": (hx("8a5a3a"), "s"),
        "leather2": (hx("5a3a24"), "s"), "leaf": (hx("6aa84f"), "s"), "leaf2": (hx("8fd06a"), "s"),
        "string": (hx("d8cfb8"), "s"), "feather": (hx("e8e2d0"), "s"),
    }, build, "string")


def arco_explorador():
    def build(w):
        top, bot = _limbs(w, [(90, 2.2, 1.8), (67.5, 3.4, 1.6), (45, 3.2, 1.3), (22.5, 1.6, 1.0, "cap")],
                          "gold", "teal", spine="gold2", edge="silver", cap="cap")
        for y in (5.6, 10.4):
            w.box((4.9, y - 0.4, 6.9), (7.1, y + 0.4, 9.1), "silver")
        for s in (1, -1):                                       # aletas verdes
            w.seg((6.6, 8 + s * 3.4), 0 + s * 22.5, 2.6, 0.7, "teal2", (7.6, 8.4))
            w.seg((6.6, 8 + s * 4.4), 0 + s * 45, 2.0, 0.6, "teal", (7.6, 8.4))
            w.cen((7.0, 8 + s * 7.0, 8), (0.9, 0.9, 1.6), "gem", ("z", 45), 12)
        # detalles: brujula en la empunadura, filigrana dorada, vendas verdes
        add_sw(w, "dial", "f2f2e6")
        for z in (6.75, 9.25):
            w.cen((6.0, 8.0, z), (1.4, 1.4, 0.2), "gold2", ("z", 45))
            w.cen((6.0, 8.0, z + (-0.06 if z < 8 else 0.06)), (0.8, 0.8, 0.12), "dial")
        for pts in (top, bot):
            for (x, y) in pts[1:3]:
                w.cen((x, y, 8), (1.6, 0.5, 1.7), "teal2", ("z", 45))
        return top[-1], bot[-1]
    return bow("arco_2", "Arco del Explorador", {
        "gold": (hx("e0a83a"), "s"), "gold2": (hx("b07a20"), "s"), "teal": (hx("2f7f74"), "s"),
        "teal2": (hx("4fa894"), "s"), "silver": (hx("b8bcc4"), "s"), "cap": (hx("9a9ea6"), "s"),
        "string": (hx("d8c8a0"), "s"), "gem": (hx("5fe0c8"), "pulse"),
    }, build, "string")


def arco_francotirador():
    def build(w):
        top, bot = _limbs(w, [(90, 2.0, 1.4, "wood"), (90, 2.4, 2.0), (67.5, 3.6, 1.8), (45, 3.6, 1.4),
                              (22.5, 1.4, 0.9, "gold")], "silver", "wood", spine="silver2", edge="gold", cap="gold")
        for s in (1, -1):
            w.cen((6.0, 8 + s * 3.1, 8), (1.4, 1.4, 2.4), "gem", ("y", 45), 13)
            w.box((4.6, 8 + s * 4.4 - 0.4, 7.2), (7.4, 8 + s * 4.4 + 0.4, 8.8), "gold")
            w.seg((5.4, 8 + s * 5.4), 180 + s * 22.5, 2.0, 0.7, "wood2", (7.7, 8.3))
            w.box((5.2, 8 + s * 6.6 - 0.3, 7.0), (6.2, 8 + s * 9.0, 7.2), "silver2")
        for y in (7.0, 8.0, 9.0):
            w.box((5.0, y - 0.25, 7.0), (7.0, y + 0.25, 9.0), "gold")
        # detalles: mira telescopica arriba de la empunadura y estabilizador abajo
        add_sw(w, "lens", "6fd8ff", "pulse")
        w.box((5.6, 10.0, 7.6), (7.4, 10.6, 8.4), "silver2")
        w.box((3.6, 10.6, 7.5), (9.2, 11.6, 8.5), "silver2")
        w.box((3.4, 10.5, 7.4), (3.8, 11.7, 8.6), "gold")
        w.box((9.0, 10.5, 7.4), (9.4, 11.7, 8.6), "gold")
        w.box((9.4, 10.75, 7.75), (9.55, 11.45, 8.25), "lens", None, 13)
        w.box((3.25, 10.75, 7.75), (3.4, 11.45, 8.25), "lens", None, 13)
        w.box((1.6, 4.2, 7.8), (5.4, 4.6, 8.2), "silver2")
        w.cen((1.4, 4.4, 8), (0.9, 0.9, 0.9), "gold", ("x", 45))
        return top[-1], bot[-1]
    return bow("arco_3", "Arco del Francotirador", {
        "silver": (hx("e8eaee"), "s"), "silver2": (hx("9aa0a8"), "s"), "gold": (hx("f2c14e"), "s"),
        "wood": (hx("6a4a2e"), "s"), "wood2": (hx("8a6a3a"), "s"), "gem": (hx("9fe6ff"), "pulse"),
        "string": (hx("8a8e96"), "s"),
    }, build, "string")


def arco_viento():
    def build(w):
        top, bot = _limbs(w, [(90, 2.0, 1.4, "tan"), (67.5, 2.8, 1.3, "violet"), (45, 2.4, 1.3, "tan"),
                              (45, 2.6, 1.6), (22.5, 2.0, 1.2)], "crystal", "violet", spine="tan2", cap="ring")
        for s in (1, -1):
            for dy in (1.8, 4.6):
                w.box((5.0, 8 + s * dy - 0.5, 6.9), (7.6, 8 + s * dy + 0.5, 9.1), "tan2")
            t = top if s > 0 else bot
            for k, (dx, dy, sz) in enumerate(((-1.6, 0.6, 1.0), (-2.6, -0.4, 0.8), (-1.0, 1.8, 0.7))):
                w.cen((t[2][0] + dx, t[2][1] + s * dy, 8), (sz * 1.6, sz * 0.5, 0.4), "wind", ("z", s * 22.5), 12)
        # anillo de viento flotando
        c = (13.6, 19.0)
        for k, (dx, dy) in enumerate(((0, 1.4), (1.4, 0), (0, -1.4), (-1.4, 0))):
            w.cen((c[0] + dx, c[1] + dy, 8), (1.4 if k % 2 == 0 else 0.5, 0.5 if k % 2 == 0 else 1.4, 0.5),
                  "ring", None, 13)
        # detalles: plumas de viento en los brazos y chispas
        for pts, sd in ((top, 1), (bot, -1)):
            for (x, y) in pts[:2]:
                w.seg((x - 0.4, y), 180 + sd * 22.5, 1.8, 0.4, "wind", (7.85, 8.15), 12)
        for c in ((2.0, 14.0, 8), (2.6, 2.0, 8), (12.4, 15.4, 8)):
            w.cen(c, (0.5, 0.5, 0.5), "ring", ("z", 45), 14)
        return top[-1], bot[-1]
    return bow("arco_4", "Arco del Viento", {
        "crystal": (hx("5fd3e6"), "pulse"), "tan": (hx("e0b77a"), "s"), "tan2": (hx("c08a4a"), "s"),
        "violet": (hx("6a3f8a"), "s"), "wind": (hx("c8f6ff"), "flow"), "ring": (hx("a8fff0"), "pulse"),
        "string": (hx("b05a9a"), "s"),
    }, build, "string")


def arco_astral():
    def build(w):
        top, bot = _limbs(w, [(90, 2.4, 1.8, "bone2"), (67.5, 3.0, 1.6), (45, 3.0, 1.4), (90, 1.4, 1.2),
                              (22.5, 2.0, 1.0)], "bone", "deep", spine="bone2", edge="core", cap="core2")
        for s in (1, -1):                                       # nucleo turquesa y salientes de hueso
            w.seg((6.2, 8 + s * 3.0), 180 - s * 0, 2.2, 1.0, "bone2", (7.4, 8.6))
            w.box((5.4, 8 + s * 0.6, 7.0), (6.6, 8 + s * 2.4, 9.0), "core")
        w.box((5.2, 6.6, 6.9), (6.8, 9.4, 9.1), "core", None, 12)
        w.cen((6.0, 8, 6.7), (1.0, 1.0, 0.3), "core2", ("z", 45), 15)
        w.cen((6.0, 8, 9.3), (1.0, 1.0, 0.3), "core2", ("z", 45), 15)
        for c in ((2.6, 20.0, 8), (3.0, -4.0, 8), (14.0, 17.0, 8)):
            w.cen(c, (0.6, 0.6, 0.6), "star", ("z", 45), 15)
        # detalles: costillas de hueso a lo largo de los brazos y grietas turquesa
        for pts in (top, bot):
            for (x, y) in pts[:4]:
                w.cen((x, y, 8), (0.5, 0.5, 2.0), "bone2")
                w.cen((x - 0.2, y, 7.25), (0.4, 0.4, 0.1), "core2", None, 13)
        return top[-1], bot[-1]
    return bow("arco_5", "Arco Astral", {
        "bone": (hx("efe9d6"), "s"), "bone2": (hx("c9c2ab"), "s"), "deep": (hx("0f3d4a"), "s"),
        "core": (hx("1f8fa8"), "pulse"), "core2": (hx("8ffcff"), "pulse"), "string": (hx("3fe0f0"), "flow"),
        "star": (hx("e6fbff"), "spark"),
    }, build, "string", string_glow=13)


SWORDS = [espada_saqueador(), espada_carnicero(), espada_ensangrentada(), espada_coloso(), espada_dios_guerra()]
AXES = [hacha_desollador(), hacha_verdugo(), hacha_carmesi(), hacha_coloso(), hacha_apocalipsis()]
GAUNTLET = [guantes_meteoro()]
BOWS = [arco_rastreador(), arco_explorador(), arco_francotirador(), arco_viento(), arco_astral()]
from weapon_details import refine_axe, refine_bow, refine_gauntlet
for _axe in AXES:
    refine_axe(_axe)
for _models in BOWS:
    for _bow in _models:
        refine_bow(_bow)
for _gauntlet in GAUNTLET:
    refine_gauntlet(_gauntlet)


def assets():
    out = v.assets(SWORDS + AXES + GAUNTLET)
    for models in BOWS:
        base = models[0]
        im, n = v.texture(base)
        out[f"assets/astral/textures/{TEX_DIR}/{base.iid}.png"] = v._png(im)
        if n > 1:
            out[f"assets/astral/textures/{TEX_DIR}/{base.iid}.png.mcmeta"] = json.dumps(
                {"animation": {"frametime": v.FRAMETIME, "interpolate": True}}, indent=1).encode()
        # los items/arco_N.json los arma build_pack.py (cambian de modelo al tensar)
        for w in models:
            out[f"assets/astral/models/item/{w.iid}.json"] = json.dumps(v.model_json(w), indent=1).encode()
    return out


if __name__ == "__main__":
    allw = SWORDS + AXES + GAUNTLET + [m for b in BOWS for m in b]
    for p in v.check(allw):
        print("AVISO:", p)
    base = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "build", "previews"))
    v.preview(os.path.join(base, "espadas_3d.gif"), SWORDS, W=170)
    v.preview(os.path.join(base, "hachas_3d.gif"), AXES + GAUNTLET, W=200)
    v.preview(os.path.join(base, "arcos_3d.gif"), [b[0] for b in BOWS] + [b[3] for b in BOWS], W=170)
    print("vistas previas ->", base)
    print("cubos:", {w.iid: len(w.els) for w in allw})
