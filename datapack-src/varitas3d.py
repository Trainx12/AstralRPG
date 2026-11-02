# -*- coding: utf-8 -*-
"""
Varitas 3D: los 5 Bastones de Mago como modelos de bloques con partes que brillan.

Cada baston es una lista de cubos (como en Blockbench) y una textura chica de
"muestras de color" de 8x8 pixeles (con vetas, brillos y facetas). Las muestras que brillan estan animadas
(.mcmeta), asi el cristal late, el fuego titila y las chispas parpadean.

Uso:
  python varitas3d.py               vista previa animada -> ../build/previews/varitas_3d.gif
build_pack.py llama a assets() para meterlas en el resource pack.

Medidas: 16 unidades = 1 bloque. El baston va parado en x=8, z=8; la mano lo
agarra cerca de y=1 (mismo punto que los iconos planos vanilla).
"""
import io
import json
import math
import os
import random

from PIL import Image, ImageDraw

FRAMES = 8          # cuadros de la animacion de la textura
FRAMETIME = 3       # ticks por cuadro (8 x 3 = 1,2 s por ciclo)
TEX_DIR = "item/varitas"


# ---------------------------------------------------------------------------
# Paletas: nombre -> (color, tipo de animacion)
# tipos: "s" fijo, "pulse" late, "flicker" titila (fuego), "spark" chispas, "flow" corre hacia arriba
# ---------------------------------------------------------------------------
def hx(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


class Wand:
    def __init__(self, iid, name, palette, tilt=-30, tex_dir=TEX_DIR):
        self.iid = iid
        self.tilt = tilt                  # giro del icono del inventario para que se vea el volumen
        self.tex_dir = tex_dir
        self.name = name
        self.palette = palette            # {muestra: (color, tipo)}
        self.slots = {k: i for i, k in enumerate(palette)}
        assert len(self.slots) <= 16, iid
        self.els = []

    def box(self, a, b, sw, rot=None, glow=0):
        """Cubo de a=(x0,y0,z0) a b=(x1,y1,z1). rot=(eje, angulo, origen)."""
        a, b = [min(p, q) for p, q in zip(a, b)], [max(p, q) for p, q in zip(a, b)]
        self.els.append({"from": a, "to": b, "sw": sw, "rot": rot, "glow": glow})

    def cen(self, c, size, sw, rot=None, glow=0):
        """Cubo centrado en c con tamano size. rot=(eje, angulo); gira sobre su centro."""
        a = [c[i] - size[i] / 2 for i in range(3)]
        b = [c[i] + size[i] / 2 for i in range(3)]
        if rot:
            rot = (rot[0], rot[1], tuple(c))
        self.box(a, b, sw, rot, glow)

    def gem(self, c, s, sw, glow=12, tall=1.0):
        """Gema: dos cubos girados 45 grados (se ve como rombo de frente y de costado)."""
        self.cen(c, (s, s * tall, s * 0.75), sw, ("z", 45), glow)
        self.cen(c, (s * 0.75, s * tall, s), sw, ("x", 45), glow)

    def shaft(self, y0, y1, sw, w=2):
        self.box((8 - w / 2, y0, 8 - w / 2), (8 + w / 2, y1, 8 + w / 2), sw)

    def ring(self, y, h, sw, w=2.6):
        self.box((8 - w / 2, y, 8 - w / 2), (8 + w / 2, y + h, 8 + w / 2), sw)

    def seg(self, p, ang, ln, wd, sw, z=(7.6, 8.4), glow=0, off=0.0):
        """Barra que sale de p=(x,y) con direccion ang (grados, multiplo de 22.5) y largo ln.
        off la corre de costado (positivo = a la izquierda de la direccion). Devuelve el punto final."""
        a = math.radians(ang)
        d = (math.cos(a), math.sin(a))
        nx, ny = -d[1], d[0]
        cx = p[0] + d[0] * ln / 2 + nx * off
        cy = p[1] + d[1] * ln / 2 + ny * off
        r = ((ang + 90) % 180) - 90                    # angulo de la linea en (-90, 90]
        L = ln + 0.3                                   # un poco mas largo para que no queden huecos
        if abs(r) <= 45:
            size, rot = (L, wd), r
        else:
            size, rot = (wd, L), (r - 90 if r > 0 else r + 90)
        c = (cx, cy, (z[0] + z[1]) / 2)
        self.cen(c, (size[0], size[1], z[1] - z[0]), sw, ("z", rot) if rot else None, glow)
        return (p[0] + d[0] * ln, p[1] + d[1] * ln)

    def blade(self, p, segs, sw, edge=None, spine=None, side=-1, edge_w=0.7, spine_w=0.6,
              z=(7.6, 8.4), edge_glow=0, teeth=None):
        """Hoja curva: segs = [(angulo, largo, ancho[, color]), ...].
        edge = filo; side=-1 lo pone a la derecha de la direccion (abajo si la hoja va hacia -x).
        spine = lomo del otro lado; teeth = dientes sobre el lomo."""
        pts = []
        for k, sg in enumerate(segs):
            ang, ln, wd = sg[:3]
            col = sg[3] if len(sg) > 3 else sw
            q = self.seg(p, ang, ln, wd, col, z)
            if edge:
                self.seg(p, ang, ln, edge_w, edge, (z[0] + 0.15, z[1] - 0.15), edge_glow,
                         side * (wd / 2 + edge_w / 2 - 0.15))
            if spine:
                self.seg(p, ang, ln * 0.9, spine_w, spine, (z[0] - 0.12, z[1] + 0.12), 0,
                         -side * (wd / 2 - spine_w / 2))
            if teeth and k < len(segs) - 1:
                a = math.radians(ang)
                nx, ny = math.sin(a) * side, -math.cos(a) * side
                mx, my = p[0] + math.cos(a) * ln * 0.5, p[1] + math.sin(a) * ln * 0.5
                self.cen((mx + nx * wd / 2, my + ny * wd / 2, (z[0] + z[1]) / 2),
                         (1.1, 1.1, z[1] - z[0] - 0.1), teeth, ("z", 45))
            pts.append(q)
            p = q
        return pts


# ---------------------------------------------------------------------------
# 1. Baston del Aprendiz: rama retorcida de Madera Estelar, vendas, raices y un cristal flotando
# ---------------------------------------------------------------------------
def aprendiz():
    w = Wand("baston_1", "Baston del Aprendiz", {
        "wood": (hx("8f6640"), "s"), "wood2": (hx("a97c50"), "s"), "bark": (hx("664629"), "s"),
        "wrap": (hx("d8c39a"), "s"), "cord": (hx("a0603a"), "s"),
        "crystal": (hx("b07cff"), "pulse"), "crystal2": (hx("d9b8ff"), "pulse"), "spark": (hx("e8d4ff"), "spark"),
        "leaf": (hx("7fbf6a"), "s"), "leaf2": (hx("a8d98a"), "s"), "bead": (hx("9fd8ff"), "pulse"),
    })
    # raices
    w.box((7, -7, 7), (9, -5, 9), "bark")
    w.box((6.6, -6.5, 6.6), (9.4, -5.5, 9.4), "bark")
    w.box((5.6, -7.4, 7.6), (7.2, -6.4, 8.4), "bark", ("z", -22.5, (7.2, -6.9, 8)))
    w.box((8.8, -7.4, 7.6), (10.4, -6.4, 8.4), "bark", ("z", 22.5, (8.8, -6.9, 8)))
    w.box((7.6, -7.4, 8.8), (8.4, -6.4, 10.2), "bark", ("x", -22.5, (8, -6.9, 8.8)))
    # mango con venda cruzada
    w.box((7, -5, 7), (9, 3, 9), "wood")
    w.box((6.7, -1.5, 6.7), (9.3, 3, 9.3), "wrap")
    for y in (-1.2, 0.6, 2.4):
        w.box((6.6, y, 6.6), (9.4, y + 0.4, 9.4), "cord")
    w.box((6.55, -3.2, 7.6), (6.75, -1.5, 8.4), "cord")         # puntas sueltas de la venda
    w.box((6.35, -4.4, 7.7), (6.6, -3.0, 8.3), "cord", ("z", -22.5, (6.6, -3.2, 8)))
    # tramo torcido con nudos y corteza
    w.box((7.4, 3, 7), (9.4, 11, 9), "wood2")
    w.box((9.2, 5, 7.6), (9.8, 6.2, 8.6), "bark")
    w.box((7.1, 8.6, 8.8), (8.1, 9.8, 9.3), "bark")
    w.box((7, 11, 7), (9, 17, 9), "wood")
    w.box((6.7, 12.2, 7.4), (7.2, 15, 8.6), "bark")
    w.box((6.8, 13, 6.8), (9.2, 14, 9.2), "cord")
    # ramita con hojas
    w.box((8.6, 8, 7.6), (11, 9, 8.6), "wood2", ("z", 22.5, (8.6, 8.5, 8)))
    w.box((10.2, 9.4, 7.6), (11.6, 10.6, 8.2), "leaf", ("z", 22.5, (10.9, 10, 8)))
    w.box((10.8, 8.4, 7.9), (12.2, 9.4, 8.5), "leaf2", ("z", -22.5, (11.5, 8.9, 8.2)))
    # horquilla que sostiene el cristal
    w.box((6.2, 16, 7.3), (7.6, 21, 8.7), "wood", ("z", 22.5, (7.6, 16, 8)))
    w.box((8.4, 16, 7.3), (9.8, 21, 8.7), "wood", ("z", -22.5, (8.4, 16, 8)))
    w.box((7.3, 16, 6.2), (8.7, 20, 7.6), "wood2", ("x", -22.5, (8, 16, 7.6)))
    w.box((7.2, 16, 7.2), (8.8, 19, 8.8), "wood2")
    w.box((4.6, 20.3, 7.5), (5.8, 21.3, 8.5), "leaf", ("z", 22.5, (5.2, 20.8, 8)))
    w.box((10.3, 20.6, 7.5), (11.5, 21.6, 8.5), "leaf2", ("z", -22.5, (10.9, 21.1, 8)))
    # amuleto colgando de una cuerda
    w.box((6.1, 12.6, 7.9), (6.3, 16.4, 8.1), "cord")
    w.gem((6.2, 12, 8), 1.1, "bead", 12, 1.3)
    # cristal flotando + astillas + chispitas
    w.gem((8, 23, 8), 3, "crystal", 13, 1.25)
    w.cen((8, 23, 8), (1.6, 2.2, 1.6), "crystal2", None, 15)
    w.gem((5.7, 23.6, 8.3), 1.1, "crystal", 12, 1.4)
    w.gem((10.4, 24.4, 7.8), 0.9, "crystal2", 12, 1.4)
    for c in ((5.3, 25.8, 8), (10.8, 21.5, 8.5), (9.5, 26.8, 7.5), (7, 27.4, 8.6)):
        w.cen(c, (0.6, 0.6, 0.6), "spark", None, 15)
    return w


# ---------------------------------------------------------------------------
# 2. Baston del Hechicero: oro y madera roja, filigrana en espiral, garras con gema de fuego
# ---------------------------------------------------------------------------
def hechicero():
    w = Wand("baston_2", "Baston del Hechicero", {
        "wood": (hx("6e2f22"), "s"), "wood2": (hx("8c4030"), "s"),
        "gold": (hx("f2c14e"), "s"), "gold2": (hx("c68a2a"), "s"),
        "gem": (hx("ffd23a"), "pulse"), "gem2": (hx("fff2a0"), "pulse"),
        "ember": (hx("ff7a1a"), "flicker"), "flame": (hx("ffb02e"), "flicker"), "spark": (hx("ffe7a0"), "spark"),
        "tassel": (hx("b3261e"), "s"), "ruby": (hx("ff3b3b"), "pulse"),
    })
    # pomo con puas
    w.cen((8, -8, 8), (1, 1.2, 1), "ember", ("y", 45), 12)
    w.box((6.6, -7, 6.6), (9.4, -5, 9.4), "gold2")
    w.box((6.9, -7.4, 6.9), (9.1, -7, 9.1), "gold")
    for dx, dz, ax, ang in ((-1.6, 0, "z", -45), (1.6, 0, "z", 45), (0, -1.6, "x", 45), (0, 1.6, "x", -45)):
        w.cen((8 + dx, -7.2, 8 + dz), (0.8, 1.4, 0.8), "gold", (ax, ang))
    # vara con espiral de oro
    w.box((7, -5, 7), (9, 17, 9), "wood")
    w.box((7.01, -1, 7.01), (8.99, 3, 8.99), "wood2")
    for y in (-1.5, 3, 8.5, 13.5):
        w.ring(y, 1, "gold")
    sides = [((6.8, 7.6), (7.0, 8.4)), ((7.6, 9.0), (8.4, 9.2)), ((9.0, 7.6), (9.2, 8.4)), ((7.6, 6.8), (8.4, 7.0))]
    for k, y in enumerate((4.2, 5.3, 6.4, 7.5, 9.7, 10.8, 11.9, 13.0)):
        (x0, z0), (x1, z1) = sides[k % 4]
        w.box((x0, y, z0), (x1, y + 0.8, z1), "gold")
    # rubies en los aros
    for y in (-1.0, 9.0):
        w.box((7.6, y - 0.2, 6.6), (8.4, y + 0.6, 6.7), "ruby", None, 10)
        w.box((7.6, y - 0.2, 9.3), (8.4, y + 0.6, 9.4), "ruby", None, 10)
    # borla colgando
    w.box((9.3, 12.2, 7.9), (9.5, 14, 8.1), "tassel")
    w.box((9.0, 11.2, 7.6), (9.8, 12.2, 8.4), "gold")
    w.box((9.05, 9.6, 7.65), (9.75, 11.2, 8.35), "tassel")
    # cuello con brasas
    w.box((6, 16.5, 6), (10, 18.5, 10), "gold2")
    w.box((6.5, 18.5, 6.5), (9.5, 19.5, 9.5), "gold")
    w.box((5.6, 15.8, 5.6), (10.4, 16.5, 10.4), "gold")
    for x0, z0, x1, z1 in ((7.5, 5.9, 8.5, 6.0), (7.5, 10.0, 8.5, 10.1), (5.9, 7.5, 6.0, 8.5), (10.0, 7.5, 10.1, 8.5)):
        w.box((x0, 17, z0), (x1, 18, z1), "ember", None, 13)
    # cuatro garras con unas
    w.box((5.4, 18.5, 7.5), (6.4, 22.5, 8.5), "gold", ("z", 22.5, (6.4, 18.5, 8)))
    w.box((9.6, 18.5, 7.5), (10.6, 22.5, 8.5), "gold", ("z", -22.5, (9.6, 18.5, 8)))
    w.box((7.5, 18.5, 5.4), (8.5, 22, 6.4), "gold2", ("x", -22.5, (8, 18.5, 6.4)))
    w.box((7.5, 18.5, 9.6), (8.5, 22, 10.6), "gold2", ("x", 22.5, (8, 18.5, 9.6)))
    w.box((5.1, 22.3, 7.6), (5.9, 23.9, 8.4), "gold", ("z", -22.5, (5.5, 22.3, 8)))
    w.box((10.1, 22.3, 7.6), (10.9, 23.9, 8.4), "gold", ("z", 22.5, (10.5, 22.3, 8)))
    w.gem((8, 23, 8), 3.8, "gem", 15, 1.25)
    w.cen((8, 23, 8), (1.8, 2.4, 1.8), "gem2", None, 15)
    # llamas en espiral
    w.cen((8, 26.6, 8), (1.8, 1.8, 1.8), "flame", ("y", 45), 15)
    w.cen((7.4, 28.2, 8.3), (1.2, 1.2, 1.2), "ember", ("z", 45), 15)
    w.cen((8.7, 29.4, 7.8), (0.8, 0.8, 0.8), "flame", None, 15)
    w.cen((8.1, 30.6, 8), (0.5, 0.5, 0.5), "spark", None, 15)
    for c in ((4.6, 25, 8), (11.4, 26.2, 8.4), (6, 20, 5.2)):
        w.cen(c, (0.5, 0.5, 0.5), "spark", None, 15)
    return w


# ---------------------------------------------------------------------------
# 3. Baston del Invocador: vertebras de hueso, runas lilas, media luna con cadenas y cristal
# ---------------------------------------------------------------------------
def invocador():
    w = Wand("baston_3", "Baston del Invocador", {
        "bone": (hx("e9e4d6"), "s"), "bone2": (hx("c9c2b0"), "s"),
        "silver": (hx("b8c4d6"), "s"), "silver2": (hx("8894a8"), "s"),
        "rune": (hx("b77cff"), "flow"), "crystal": (hx("9a5cff"), "pulse"), "crystal2": (hx("d2b3ff"), "pulse"),
        "shard": (hx("7fe6ff"), "spark"), "chain": (hx("6f7a8c"), "s"),
    })
    # cristal de la base sostenido por garras de plata
    w.gem((8, -8, 8), 1.6, "crystal", 12)
    w.box((6.8, -6.5, 6.8), (9.2, -5, 9.2), "silver2")
    w.box((6.6, -7.6, 7.6), (7.4, -6.2, 8.4), "silver", ("z", -22.5, (7, -6.5, 8)))
    w.box((8.6, -7.6, 7.6), (9.4, -6.2, 8.4), "silver", ("z", 22.5, (9, -6.5, 8)))
    # columna de vertebras
    w.box((7.1, -5, 7.1), (8.9, 17, 8.9), "bone")
    for y in (-3.5, -2, 2.5, 4, 8.2, 9.7, 14, 15.2):
        w.box((6.8, y, 6.8), (9.2, y + 0.7, 9.2), "bone2")
    for y in (-0.5, 6, 12.5):
        w.ring(y, 1, "silver")
    # runas que brillan en los 4 costados
    for y0, y1 in ((1, 2.3), (4.9, 5.8), (7.2, 8.0), (10.6, 12)):
        w.box((7.5, y0, 6.75), (8.5, y1, 6.85), "rune", None, 10)
        w.box((7.5, y0, 9.15), (8.5, y1, 9.25), "rune", None, 10)
        w.box((6.75, y0, 7.5), (6.85, y1, 8.5), "rune", None, 10)
        w.box((9.15, y0, 7.5), (9.25, y1, 8.5), "rune", None, 10)
    w.box((6.5, 16, 6.5), (9.5, 18, 9.5), "silver2")
    w.box((6.2, 17.2, 6.2), (9.8, 17.8, 9.8), "silver")
    # media luna (dos brazos en V con puntas)
    w.box((6, 17, 7.25), (7.5, 23.5, 8.75), "bone2", ("z", 45, (7.5, 17, 8)))
    w.box((8.5, 17, 7.25), (10, 23.5, 8.75), "bone2", ("z", -45, (8.5, 17, 8)))
    w.box((5.4, 18.5, 7.15), (6.4, 21, 8.85), "silver", ("z", 45, (7.5, 17, 8)))
    w.box((9.6, 18.5, 7.15), (10.6, 21, 8.85), "silver", ("z", -45, (8.5, 17, 8)))
    w.box((2.2, 21, 7.4), (3.6, 24.2, 8.6), "silver", ("z", -22.5, (2.9, 21, 8)))
    w.box((12.4, 21, 7.4), (13.8, 24.2, 8.6), "silver", ("z", 22.5, (13.1, 21, 8)))
    # cadenas con colgantes
    for x in (2.9, 13.1):
        for k, y in enumerate((20.1, 19.0, 17.9)):
            sz = (0.5, 0.9, 0.25) if k % 2 == 0 else (0.25, 0.9, 0.5)
            w.cen((x, y, 8), sz, "chain")
        w.gem((x, 16.6, 8), 1.0, "crystal2", 12, 1.5)
    # cristal grande flotando con anillo de astillas
    w.gem((8, 24, 8), 4, "crystal", 14, 1.3)
    w.cen((8, 24, 8), (2, 3, 2), "crystal2", None, 15)
    for c in ((4.5, 27.5, 8), (11.5, 27.5, 8), (8, 29.8, 8), (5.2, 25, 10.2), (10.8, 25, 5.8)):
        w.cen(c, (0.8, 0.8, 0.8), "shard", ("z", 45), 15)
    return w


# ---------------------------------------------------------------------------
# 4. Baston del Archimago: azul noche, canal de energia, rombo de oro con nucleo de Shulker
# ---------------------------------------------------------------------------
def archimago():
    w = Wand("baston_4", "Baston del Archimago", {
        "navy": (hx("232a5c"), "s"), "navy2": (hx("343f80"), "s"),
        "gold": (hx("f5c84c"), "s"), "gold2": (hx("c28b28"), "s"),
        "channel": (hx("4fb8ff"), "flow"), "core": (hx("c58cff"), "pulse"), "core2": (hx("f0d8ff"), "pulse"),
        "blue": (hx("3d7dff"), "pulse"), "spark": (hx("bfe6ff"), "spark"), "tassel": (hx("2f5fd0"), "s"),
    })
    # pomo
    w.gem((8, -7.8, 8), 1.6, "blue", 12)
    w.box((6.5, -6.8, 6.5), (9.5, -5, 9.5), "gold2")
    w.box((6.2, -6.2, 6.2), (9.8, -5.6, 9.8), "gold")
    # vara
    w.box((7, -5, 7), (9, 16.5, 9), "navy")
    w.box((7.01, -1, 7.01), (8.99, 3, 8.99), "navy2")
    for y in (-1.5, 3, 9, 14.5):
        w.ring(y, 1, "gold")
    w.box((7.6, 4, 6.9), (8.4, 14.5, 7), "channel", None, 11)  # canal de energia
    w.box((7.6, 4, 9), (8.4, 14.5, 9.1), "channel", None, 11)
    w.cen((8, 7, 8), (2.4, 1.6, 2.4), "blue", ("y", 45), 12)
    w.cen((8, 7, 8), (3.2, 0.5, 3.2), "gold", ("y", 45))
    for y in (0.5, 11.8):                                       # rombitos de oro incrustados
        w.cen((8, y, 6.95), (1.1, 1.1, 0.2), "gold", ("z", 45))
        w.cen((8, y, 9.05), (1.1, 1.1, 0.2), "gold", ("z", 45))
    # borla azul
    w.box((9.6, 13.5, 7.9), (9.8, 15.8, 8.1), "gold2")
    w.box((9.3, 12.6, 7.6), (10.1, 13.5, 8.4), "gold")
    w.box((9.35, 10.8, 7.65), (10.05, 12.6, 8.35), "tassel")
    # alitas y volutas de oro en la base de la cabeza
    w.box((4.6, 15.5, 7.5), (7, 16.5, 8.5), "gold", ("z", -22.5, (7, 16, 8)))
    w.box((9, 15.5, 7.5), (11.4, 16.5, 8.5), "gold", ("z", 22.5, (9, 16, 8)))
    w.box((4.2, 16.4, 7.6), (5.2, 17.8, 8.4), "gold2")
    w.box((10.8, 16.4, 7.6), (11.8, 17.8, 8.4), "gold2")
    w.box((5.2, 14.4, 7.6), (6.2, 15.4, 8.4), "gold2")
    w.box((9.8, 14.4, 7.6), (10.8, 15.4, 8.4), "gold2")
    w.box((6.5, 15.5, 6.5), (9.5, 17.5, 9.5), "gold2")
    # rombo de oro (4 barras giradas 45 grados) con tachas en las puntas
    c = (8, 22.2, 8)
    h = 3.4
    for (x0, y0, x1, y1) in ((c[0] - h, c[1] + h - 1, c[0] + h, c[1] + h),
                             (c[0] - h, c[1] - h, c[0] + h, c[1] - h + 1),
                             (c[0] - h, c[1] - h, c[0] - h + 1, c[1] + h),
                             (c[0] + h - 1, c[1] - h, c[0] + h, c[1] + h)):
        w.box((x0, y0, 7.25), (x1, y1, 8.75), "gold", ("z", 45, c))
    # borde interior oscuro para que resalte el oro
    hi = h - 1
    for (x0, y0, x1, y1) in ((c[0] - hi, c[1] + hi - 0.4, c[0] + hi, c[1] + hi),
                             (c[0] - hi, c[1] - hi, c[0] + hi, c[1] - hi + 0.4),
                             (c[0] - hi, c[1] - hi, c[0] - hi + 0.4, c[1] + hi),
                             (c[0] + hi - 0.4, c[1] - hi, c[0] + hi, c[1] + hi)):
        w.box((x0, y0, 7.5), (x1, y1, 8.5), "gold2", ("z", 45, c))
    d = h * math.sqrt(2)
    for px, py in ((c[0] - d, c[1]), (c[0] + d, c[1])):
        w.gem((px, py, 8), 1.3, "blue", 13)
    w.cen((8, c[1] - d + 0.2, 8), (1.2, 1, 1.2), "gold2")
    w.cen(c, (3, 3, 3), "core", ("y", 45), 15)                  # nucleo de Shulker
    w.cen(c, (1.8, 1.8, 3.4), "core2", ("z", 45), 15)
    w.gem((8, c[1] + d + 1.4, 8), 1.4, "gold", 0, 1.6)          # punta
    w.cen((8, c[1] + d + 3.2, 8), (0.6, 0.6, 0.6), "spark", ("z", 45), 15)
    for c2 in ((1.6, 22.2, 8), (14.4, 22.2, 8), (4.4, 27.2, 8.5), (11.6, 17.4, 7.5)):
        w.cen(c2, (0.7, 0.7, 0.7), "spark", ("z", 45), 15)
    return w


# ---------------------------------------------------------------------------
# 5. Baston Astral: oro y azul profundo, alas, halo de sol con nucleo astral y estrellas
# ---------------------------------------------------------------------------
def astral():
    w = Wand("baston_5", "Baston Astral", {
        "deep": (hx("1b2a6b"), "s"), "deep2": (hx("2a3f99"), "s"),
        "gold": (hx("ffd84d"), "s"), "gold2": (hx("e0a12a"), "s"), "white": (hx("fff6d8"), "s"),
        "channel": (hx("4fe3ff"), "flow"), "core": (hx("4fd1ff"), "pulse"), "core2": (hx("e6fbff"), "pulse"),
        "ray": (hx("ffe680"), "pulse"), "star": (hx("fffbe0"), "spark"), "feather": (hx("fff0b8"), "s"),
    })
    # punta de cristal con garras
    w.gem((8, -8.2, 8), 1.8, "core", 13, 1.4)
    w.box((6.4, -7, 6.4), (9.6, -5, 9.6), "gold2")
    w.box((6.1, -6.4, 6.1), (9.9, -5.8, 9.9), "gold")
    w.box((6.5, -8.4, 7.6), (7.3, -6.8, 8.4), "gold", ("z", -22.5, (6.9, -7, 8)))
    w.box((8.7, -8.4, 7.6), (9.5, -6.8, 8.4), "gold", ("z", 22.5, (9.1, -7, 8)))
    # vara con estrellas incrustadas
    w.box((7, -5, 7), (9, 17, 9), "deep")
    w.box((7.01, -1, 7.01), (8.99, 3, 8.99), "deep2")
    for y in (-1.5, 3, 10.5, 14):
        w.ring(y, 1 if y != 14 else 0.6, "gold")
    for y in (-3.2, 1.0):
        w.cen((8, y, 6.95), (0.8, 0.8, 0.2), "star", ("z", 45), 13)
        w.cen((8, y, 9.05), (0.8, 0.8, 0.2), "star", ("z", 45), 13)
    w.cen((8, 7, 8), (2.8, 2.8, 2.8), "gold", ("y", 45))        # engarce con gema
    w.cen((8, 7, 8), (1.4, 1.4, 3.2), "core", None, 14)
    w.cen((8, 7, 8), (3.2, 1.4, 1.4), "core", None, 14)
    w.cen((8, 5.2, 8), (2.2, 0.6, 2.2), "gold2", ("y", 45))
    w.cen((8, 8.8, 8), (2.2, 0.6, 2.2), "gold2", ("y", 45))
    for z0, z1 in ((6.9, 7), (9, 9.1)):
        w.box((7.6, 9.4, z0), (8.4, 15.5, z1), "channel", None, 12)
    w.box((6.2, 15.5, 6.2), (9.8, 17.5, 9.8), "gold2")
    w.box((6.8, 17.5, 6.8), (9.2, 18.5, 9.2), "gold")
    # alas de plumas doradas
    for side in (-1, 1):
        for k, (dx, dy, ln, ang) in enumerate(((1.6, 16.6, 3.4, 22.5), (2.0, 15.6, 3.0, 45), (1.8, 14.7, 2.4, 45))):
            x0 = 8 + side * dx
            x1 = x0 + side * ln
            rot = ("z", ang * side, (x0, dy + 0.5, 8))
            w.box((min(x0, x1), dy, 7.55), (max(x0, x1), dy + 0.9, 8.45), "feather" if k else "gold", rot)
    # halo de sol: aro octogonal + rayos
    c = (8, 23.5, 8)
    r = 4.6
    for k in range(8):
        a = math.radians(k * 45)
        px, py = c[0] + r * math.sin(a), c[1] + r * math.cos(a)
        if k % 4 == 0:
            w.cen((px, py, 8), (3.8, 1, 1.4), "gold", None)
        elif k % 4 == 2:
            w.cen((px, py, 8), (1, 3.8, 1.4), "gold", None)
        else:
            ang = -45 if k in (1, 5) else 45
            w.box((px - 1.9, py - 0.5, 7.3), (px + 1.9, py + 0.5, 8.7), "gold", ("z", ang, (px, py, 8)))
        if k % 2 == 0:                                          # tachas blancas
            w.cen((px, py, 7.1), (0.8, 0.8, 0.3), "white")
            w.cen((px, py, 8.9), (0.8, 0.8, 0.3), "white")
    for k in range(8):                                          # rayos hacia afuera
        a = math.radians(k * 45 + 22.5)
        px, py = c[0] + (r + 1.6) * math.sin(a), c[1] + (r + 1.6) * math.cos(a)
        w.cen((px, py, 8), (0.9, 0.9, 0.9), "ray", ("z", 45), 13)
    for k in range(4):                                          # rayos largos en cruz
        a = math.radians(k * 90)
        px, py = c[0] + (r + 1.7) * math.sin(a), c[1] + (r + 1.7) * math.cos(a)
        size = (0.8, 1.8, 0.8) if k % 2 == 0 else (1.8, 0.8, 0.8)
        if k != 2:
            w.cen((px, py, 8), size, "ray", None, 14)
    # rayos finos entre el nucleo y el aro
    for ang in (45, -45):
        w.cen(c, (0.4, 7.2, 0.4), "gold2", ("z", ang))
    # nucleo astral
    w.gem(c, 3.4, "core", 15, 1.0)
    w.cen(c, (1.8, 1.8, 1.8), "core2", ("y", 45), 15)
    for p in ((3.0, 29.4, 8.4), (13.0, 28.8, 7.6), (2.4, 18.6, 8), (13.6, 19.2, 8), (8, 31.4, 8)):
        w.cen(p, (0.6, 0.6, 0.6), "star", None, 15)
    return w


WANDS = [aprendiz(), hechicero(), invocador(), archimago(), astral()]


# ---------------------------------------------------------------------------
# Textura animada (32x32 por cuadro: 16 muestras de 8x8 pixeles con dibujo segun el material)
# ---------------------------------------------------------------------------
TS = 8           # pixeles por muestra
TEX = TS * 4     # lado de la textura


def _pattern(name, x, y, n, seed):
    """Multiplicador de brillo fijo segun el material (vetas, bisel, facetas)."""
    r = random.Random(seed * 1000 + x * 37 + y)
    if name.startswith(("wood", "bark", "bone")):
        col = random.Random(seed * 50 + x).uniform(-1, 1)        # vetas verticales
        k = 1 + 0.10 * col + 0.05 * n
        if name.startswith("bark") and r.random() < 0.12:
            k -= 0.18
        if name.startswith("bone") and y % 4 == 3:
            k -= 0.08
        return k
    if name.startswith(("gold", "silver", "chain")):
        k = 1 + 0.04 * n
        if y == 0 or x == 0:
            k += 0.22                                               # brillo del borde
        if y == TS - 1 or x == TS - 1:
            k -= 0.22                                               # sombra del borde
        if (x, y) in ((2, 2), (3, 2), (2, 3)):
            k += 0.3                                                # destello
        return k
    if name.startswith(("wrap", "cord", "tassel")):
        return 1 + (0.12 if (x + y) % 4 < 2 else -0.10) + 0.04 * n   # trama cruzada
    if name.startswith(("crystal", "gem", "core", "blue", "bead", "ruby")):
        k = 1 + 0.28 * (1 - (x + y) / (2 * (TS - 1))) - 0.1          # facetas: luz arriba-izquierda
        if x == y or x + y == TS - 1:
            k += 0.12
        if (x, y) in ((1, 1), (2, 1), (1, 2)):
            k += 0.45
        return k
    if name.startswith("prism"):                                    # cristal con franjas diagonales
        return 1 + 0.05 * n + (0.22 if (x + y) // 2 % 3 == 0 else 0) - 0.12 * (y / TS)
    if name.startswith(("leaf", "feather")):
        return 1 + (0.15 if x == TS // 2 else 0) + 0.08 * n - 0.1 * (y / TS)
    if name.startswith(("navy", "deep")):
        return 1 + 0.06 * n + (0.9 if r.random() < 0.04 else 0)       # puntitos como estrellas
    return 1 + 0.09 * n


def _frame_color(base, kind, f, n, x, y, pat):
    r, g, b = base
    t = f / FRAMES * 2 * math.pi
    if kind == "s":
        k = pat
    elif kind == "pulse":
        k = pat + 0.22 * math.sin(t + 0.6 * n)
    elif kind == "flicker":
        k = pat * 0.85 + 0.35 * random.Random(f * 97 + x * 13 + y * 7).random()
    elif kind == "flow":
        band = (y / TS * 4 - f / FRAMES * 4) % 4                    # banda brillante que sube
        k = 0.75 + 0.55 * (1 - abs(band - 2) / 2) ** 2 + 0.05 * n
    elif kind == "spark":
        on = random.Random(f * 31 + x * 5 + y * 11).random() < 0.35
        k = 1.35 if on else 0.75
    else:
        k = pat
    if k > 1:   # brillo: se aclara hacia el blanco en vez de saturar
        m = k - 1
        return tuple(int(min(255, c + (255 - c) * m * 0.9)) for c in (r, g, b)) + (255,)
    return tuple(int(max(0, min(255, c * k))) for c in (r, g, b)) + (255,)


def texture(w):
    """Tira de FRAMES cuadros de 32x32."""
    animated = any(kind != "s" for _, kind in w.palette.values())
    n = FRAMES if animated else 1
    im = Image.new("RGBA", (TEX, TEX * n), (0, 0, 0, 0))
    px = im.load()
    rnd = random.Random(w.iid)
    noise = [[rnd.uniform(-1, 1) for _ in range(TEX)] for _ in range(TEX)]
    for name, slot in w.slots.items():
        base, kind = w.palette[name]
        sx, sy = slot % 4 * TS, slot // 4 * TS
        for yy in range(TS):
            for xx in range(TS):
                x, y = sx + xx, sy + yy
                pat = _pattern(name, xx, yy, noise[y][x], slot)
                for f in range(n):
                    px[x, f * TEX + y] = _frame_color(base, kind, f, noise[y][x], xx, yy, pat)
    return im, n


# ---------------------------------------------------------------------------
# Modelo de Minecraft
# ---------------------------------------------------------------------------
def _rx(a):
    c, s = math.cos(a), math.sin(a)
    return [[1, 0, 0], [0, c, -s], [0, s, c]]


def _ry(a):
    c, s = math.cos(a), math.sin(a)
    return [[c, 0, s], [0, 1, 0], [-s, 0, c]]


def _rz(a):
    c, s = math.cos(a), math.sin(a)
    return [[c, -s, 0], [s, c, 0], [0, 0, 1]]


def _mul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def _app(m, v):
    return [sum(m[i][k] * v[k] for k in range(3)) for i in range(3)]


def _euler_xyz(m):
    """Angulos (x,y,z) en grados con m = Rx*Ry*Rz (como rotationXYZ de Minecraft)."""
    y = math.asin(max(-1, min(1, m[0][2])))
    x = math.atan2(-m[1][2], m[2][2])
    z = math.atan2(-m[0][1], m[0][0])
    return [round(math.degrees(v), 2) for v in (x, y, z)]


def _rot_of(deg):
    x, y, z = (math.radians(v) for v in deg)
    return _mul(_mul(_rx(x), _ry(y)), _rz(z))


def _bounds(w):
    ys = [e["from"][1] for e in w.els] + [e["to"][1] for e in w.els]
    return min(ys) - 0.5, max(ys) + 0.5


def _xmid(w):
    xs = [c[0] for e in w.els for c in _corners(e)]
    return (min(xs) + max(xs)) / 2


def _fit(w, m, room=15.2):
    """Escala y traslado para que el modelo girado con m quede centrado en el casillero."""
    pts = [_app(m, [c[i] - 8 for i in range(3)]) for e in w.els for c in _corners(e)]
    x0, x1 = min(p[0] for p in pts), max(p[0] for p in pts)
    y0, y1 = min(p[1] for p in pts), max(p[1] for p in pts)
    s = round(min(1.0, room / max(x1 - x0, y1 - y0)), 3)
    return s, [round(-(x0 + x1) / 2 * s, 2), round(-(y0 + y1) / 2 * s, 2), 0]


def display(w):
    """Como se ve en la mano, el inventario, el piso y los marcos."""
    # Inventario: diagonal como los iconos vanilla, girado un poco para que se vea el volumen
    gui_m = _mul(_rz(math.radians(-45)), _ry(math.radians(w.tilt)))
    s, gui_t = _fit(w, gui_m)
    gui_r = _euler_xyz(gui_m)
    fixed_m = _mul(_ry(math.pi), gui_m)
    s2, fixed_t = _fit(w, fixed_m)
    return {
        # mismo angulo que una herramienta vanilla, menos 45 grados porque el modelo esta parado
        "thirdperson_righthand": {"rotation": [0, -90, 10], "translation": [0, 4, 0.5], "scale": [0.85, 0.85, 0.85]},
        "thirdperson_lefthand": {"rotation": [0, 90, -10], "translation": [0, 4, 0.5], "scale": [0.85, 0.85, 0.85]},
        "firstperson_righthand": {"rotation": [0, -90, -20], "translation": [1.13, 3.2, 1.13], "scale": [0.68, 0.68, 0.68]},
        "firstperson_lefthand": {"rotation": [0, 90, 20], "translation": [1.13, 3.2, 1.13], "scale": [0.68, 0.68, 0.68]},
        "gui": {"rotation": gui_r, "translation": gui_t, "scale": [s, s, s]},
        "fixed": {"rotation": _euler_xyz(fixed_m), "translation": fixed_t, "scale": [s2, s2, s2]},
        "ground": {"rotation": gui_r, "translation": [0, 3, 0], "scale": [0.32, 0.32, 0.32]},
        "head": {"rotation": [0, 0, -45], "translation": [0, 10, 0], "scale": [0.8, 0.8, 0.8]},
    }


def model_json(w):
    tex = f"astral:{w.tex_dir}/{w.iid}"
    els = []
    for e in w.els:
        slot = w.slots[e["sw"]]
        u, v = slot % 4 * 4, slot // 4 * 4
        uv = [u + 0.5, v + 0.5, u + 3.5, v + 3.5] if max(
            e["to"][i] - e["from"][i] for i in range(3)) < 1.5 else [u, v, u + 4, v + 4]
        el = {"from": [round(c, 3) for c in e["from"]], "to": [round(c, 3) for c in e["to"]],
              "faces": {f: {"uv": uv, "texture": "#t"} for f in ("north", "south", "east", "west", "up", "down")}}
        if e["rot"]:
            axis, ang, org = e["rot"]
            el["rotation"] = {"origin": [round(c, 3) for c in org], "axis": axis, "angle": ang}
        if e["glow"]:
            el["light_emission"] = e["glow"]
            el["shade"] = False
        els.append(el)
    return {"textures": {"t": tex, "particle": tex}, "elements": els, "display": display(w)}


def _png(im):
    b = io.BytesIO()
    im.save(b, "PNG")
    return b.getvalue()


def assets(items=None):
    """{ruta en el pack: bytes} para build_pack.py."""
    out = {}
    for w in items or WANDS:
        im, n = texture(w)
        out[f"assets/astral/textures/{w.tex_dir}/{w.iid}.png"] = _png(im)
        if n > 1:
            out[f"assets/astral/textures/{w.tex_dir}/{w.iid}.png.mcmeta"] = json.dumps(
                {"animation": {"frametime": FRAMETIME, "interpolate": True}}, indent=1).encode()
        out[f"assets/astral/models/item/{w.iid}.json"] = json.dumps(model_json(w), indent=1).encode()
        out[f"assets/astral/items/{w.iid}.json"] = json.dumps(
            {"model": {"type": "minecraft:model", "model": f"astral:item/{w.iid}"}}, indent=1).encode()
    return out


def check(items=None):
    """Revisa limites de Minecraft: coordenadas -16..32, angulos permitidos, 16 muestras."""
    problems = []
    for w in items or WANDS:
        for e in w.els:
            for c in e["from"] + e["to"]:
                if not -16 <= c <= 32:
                    problems.append(f"{w.iid}: coordenada fuera de rango {c}")
            if e["rot"] and e["rot"][1] not in (-45, -22.5, 0, 22.5, 45):
                problems.append(f"{w.iid}: angulo {e['rot'][1]}")
        # que el icono entre en el casillero (16x16)
        d = display(w)["gui"]
        m = _rot_of(d["rotation"])
        for e in w.els:
            for corner in _corners(e):
                p = _app(m, [(corner[i] - 8) * d["scale"][0] for i in range(3)])
                for i in (0, 1):
                    if abs(p[i] + d["translation"][i]) > 8.6:
                        problems.append(f"{w.iid}: el icono se sale del casillero ({p[i] + d['translation'][i]:.1f})")
                        break
    return sorted(set(problems))


# ---------------------------------------------------------------------------
# Vista previa (render de software, sin abrir el juego)
# ---------------------------------------------------------------------------
FACES = {  # cara: (normal, 4 esquinas como indices de (x,y,z) 0=min 1=max)
    "north": ((0, 0, -1), [(1, 1, 0), (0, 1, 0), (0, 0, 0), (1, 0, 0)]),
    "south": ((0, 0, 1), [(0, 1, 1), (1, 1, 1), (1, 0, 1), (0, 0, 1)]),
    "east": ((1, 0, 0), [(1, 1, 1), (1, 1, 0), (1, 0, 0), (1, 0, 1)]),
    "west": ((-1, 0, 0), [(0, 1, 0), (0, 1, 1), (0, 0, 1), (0, 0, 0)]),
    "up": ((0, 1, 0), [(0, 1, 0), (1, 1, 0), (1, 1, 1), (0, 1, 1)]),
    "down": ((0, -1, 0), [(0, 0, 1), (1, 0, 1), (1, 0, 0), (0, 0, 0)]),
}


def _elrot(e):
    if not e["rot"]:
        return None, None
    axis, ang, org = e["rot"]
    a = math.radians(ang)
    return {"x": _rx, "y": _ry, "z": _rz}[axis](a), org


def _corners(e):
    m, org = _elrot(e)
    pts = []
    for ix in (0, 1):
        for iy in (0, 1):
            for iz in (0, 1):
                p = [(e["from"], e["to"])[k][i] for i, k in enumerate((ix, iy, iz))]
                if m:
                    p = [a + b for a, b in zip(_app(m, [p[i] - org[i] for i in range(3)]), org)]
                pts.append(p)
    return pts


def render(w, frame_im, view, scale, size, center, xc=8):
    """Dibuja el baston con la matriz view. Devuelve imagen RGBA."""
    ss = 3
    img = Image.new("RGBA", (size[0] * ss, size[1] * ss), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    tex = frame_im.load()
    light = [0.35, 0.8, -0.5]
    ln = math.sqrt(sum(c * c for c in light))
    light = [c / ln for c in light]
    polys = []
    for e in w.els:
        m, org = _elrot(e)
        slot = w.slots[e["sw"]]
        su, sv = slot % 4 * 4, slot // 4 * 4
        for fname, (nrm, cs) in FACES.items():
            n = list(nrm)
            pts = []
            for c in cs:
                p = [(e["from"], e["to"])[c[i]][i] for i in range(3)]
                if m:
                    p = [a + b for a, b in zip(_app(m, [p[i] - org[i] for i in range(3)]), org)]
                pts.append(_app(view, [p[0] - xc, p[1] - center, p[2] - 8]))
            if m:
                n = _app(m, n)
            n = _app(view, n)
            if n[2] >= 0:   # mira para atras
                continue
            depth = sum(p[2] for p in pts) / 4
            shade = 1.0 if e["glow"] else 0.68 + 0.4 * max(0, -(n[0] * light[0] + n[1] * light[1] + n[2] * light[2]))
            polys.append((depth, pts, su, sv, shade))
    polys.sort(key=lambda t: -t[0])
    cx, cy = size[0] * ss / 2, size[1] * ss / 2
    k = scale * ss
    for _, pts, su, sv, shade in polys:
        a, b, c, d = pts
        for j in range(TS):
            for i in range(TS):
                def P(u, v):
                    top = [a[q] + (b[q] - a[q]) * u for q in range(2)]
                    bot = [d[q] + (c[q] - d[q]) * u for q in range(2)]
                    q2 = [top[q] + (bot[q] - top[q]) * v for q in range(2)]
                    return (cx + q2[0] * k, cy - q2[1] * k)
                quad = [P(i / TS, j / TS), P((i + 1) / TS, j / TS), P((i + 1) / TS, (j + 1) / TS), P(i / TS, (j + 1) / TS)]
                r, g, bb, _ = tex[su * TS // 4 + i, sv * TS // 4 + j]
                col = (int(r * shade), int(g * shade), int(bb * shade), 255)
                dr.polygon(quad, fill=col)
    return img.resize(size, Image.LANCZOS)


def preview(path, items=None, W=150):
    items = items or WANDS
    H, SC = 330, 7.0
    frames = []
    strips = [texture(w)[0] for w in items]
    steps = 36
    for k in range(steps):
        yaw = math.radians(k * 360 / steps)
        view = _mul(_rx(math.radians(-12)), _ry(yaw))
        bg = Image.new("RGBA", (W * len(items), H + 34), (34, 24, 52, 255))
        for i, w in enumerate(items):
            n = strips[i].size[1] // TEX
            f = (k * 2) % FRAMES if n > 1 else 0
            fim = strips[i].crop((0, f * TEX, TEX, f * TEX + TEX)) if n > 1 else strips[i]
            y0, y1 = _bounds(w)
            im = render(w, fim, view, SC, (W, H), (y0 + y1) / 2, _xmid(w))
            bg.alpha_composite(im, (i * W, 0))
            ImageDraw.Draw(bg).text((i * W + 10, H + 10), w.name, fill=(230, 220, 255, 255))
        frames.append(bg.convert("RGB").convert("P", palette=Image.ADAPTIVE, colors=255))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=70, loop=0, disposal=2)
    # tambien un PNG fijo grande y los iconos del inventario
    frames[3].convert("RGB").save(path.replace(".gif", ".png"))
    icons = Image.new("RGBA", (len(items) * 80, 80), (139, 139, 139, 255))
    for i, w in enumerate(items):
        d = display(w)["gui"]
        m = _rot_of(d["rotation"])
        s = d["scale"][0]
        fim = strips[i].crop((0, 0, TEX, TEX))
        mm = [[m[r][c] * s for c in range(3)] for r in range(3)]
        im = render(w, fim, mm, 4.0, (64, 64), 8 - 0)
        # la traslacion del gui va en pixeles del casillero
        icons.alpha_composite(im, (i * 80 + 8 + int(d["translation"][0] * 4), 8 - int(d["translation"][1] * 4)))
    icons.resize((len(items) * 160, 160), Image.NEAREST).save(path.replace(".gif", "_iconos.png"))


if __name__ == "__main__":
    probs = check()
    for p in probs:
        print("AVISO:", p)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "build", "previews", "varitas_3d.gif")
    preview(os.path.abspath(out))
    print("vista previa ->", os.path.abspath(out))
    print("cubos por baston:", {w.iid: len(w.els) for w in WANDS})
