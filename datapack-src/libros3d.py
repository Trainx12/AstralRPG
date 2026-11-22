# -*- coding: utf-8 -*-
"""Libros del Invocador en 3D (pedido del dueno 22/11/2026). Modelos propios para astral:libro_invocador_<tier>.

El dueno eligio los temas de Iron's Spells (podrido, muneco maldito, evocador, piel de dragon, necronomicon,
dorado); aca son disenos propios con esos temas: tapas gruesas, lomo con nervios, hojas, esquineros, broche y
el adorno de cada uno en relieve, con partes que brillan.

En la mano: parado al costado de la pierna, con la tapa hacia afuera (3ra persona); en 1ra persona se ve la tapa.
La animacion de invocar (poses_jugador.py) lo levanta.

Uso: python libros3d.py   -> build/previews/libros_3d.png
"""
import os

import piezas3d as P
from piezas3d import Pieza, hx, aclarar, oscurecer

TIERS = (1, 3, 5, 7, 9, 10)

# Libro: tapa de adelante mira a -Z, lomo a +X (asi, mirando la tapa, el lomo queda a la izquierda).
X0, X1, Y0, Y1 = 3.0, 13.0, 1.6, 14.4
ZF, ZB = 5.6, 10.4          # caras de afuera de las tapas
T = 0.9                      # grosor de cada tapa


def base_paleta(tapa, lomo, metal, hoja='#e8dcb8', **extra):
    pal = {
        'leather_cover': (hx(tapa), 's'),
        'leather_dark': (oscurecer(hx(tapa), 0.35), 's'),
        'leather_spine': (hx(lomo), 's'),
        'page_block': (hx(hoja), 's'),
        'page_edge': (oscurecer(hx(hoja), 0.18), 's'),
        'gold_metal': (hx(metal), 's'),
        'gold_metal2': (oscurecer(hx(metal), 0.3), 's'),
        'cloth_ribbon': (hx('#b8323a'), 's'),
        'cloth_ribbon2': (hx('#d8b040'), 's'),
    }
    for k, val in extra.items():
        pal[k] = val
    return pal


def libro_base(p, broche=True, esquinas=True):
    # tapas (un poco mas grandes que las hojas) y hojas
    p.rbox(((X0 + X1) / 2, (Y0 + Y1) / 2, ZF + T / 2), (X1 - X0, Y1 - Y0, T), 'leather_cover', r=0.5, eje='z')
    p.rbox(((X0 + X1) / 2, (Y0 + Y1) / 2, ZB - T / 2), (X1 - X0, Y1 - Y0, T), 'leather_cover', r=0.5, eje='z')
    p.cen(((X0 + X1) / 2 - 0.3, (Y0 + Y1) / 2, (ZF + ZB) / 2), (X1 - X0 - 1.2, Y1 - Y0 - 0.9, ZB - ZF - 2 * T + 0.02),
          'page_block')
    for y in (Y0 + 1.5, Y0 + 4.0, Y0 + 6.5, Y0 + 9.0, Y0 + 11.5):
        p.cen((X0 + 0.3, y, (ZF + ZB) / 2), (0.1, 0.25, ZB - ZF - 2 * T), 'page_edge')
    # lomo redondeado con nervios
    p.rbox((X1 - 0.2, (Y0 + Y1) / 2, (ZF + ZB) / 2), (1.4, Y1 - Y0 + 0.2, ZB - ZF + 0.2), 'leather_spine', r=0.7, eje='y')
    for y in (Y0 + 1.6, Y0 + 4.4, Y0 + 7.2, Y0 + 10.0, Y1 - 1.6):
        p.rbox((X1 + 0.15, y, (ZF + ZB) / 2), (1.0, 0.7, ZB - ZF + 0.5), 'gold_metal2', r=0.3, eje='y')
    if esquinas:
        for (x, y) in ((X0 + 0.9, Y0 + 0.9), (X0 + 0.9, Y1 - 0.9), (X1 - 1.6, Y0 + 0.9), (X1 - 1.6, Y1 - 0.9)):
            for z in (ZF - 0.15, ZB + 0.15):
                p.cen((x, y, z + (0.0 if z > 8 else 0.0)), (2.0, 2.0, 0.5), 'gold_metal')
                p.cen((x, y, z), (0.7, 0.7, 0.62), 'gold_metal2')
    if broche:   # dos broches con bisagra y boton
        for yb in ((Y0 + Y1) / 2 + 3.6, (Y0 + Y1) / 2 - 3.6):
            p.cen((X0 - 0.3, yb, (ZF + ZB) / 2), (0.7, 1.8, ZB - ZF + 0.6), 'leather_dark')
            p.cen((X0 + 0.9, yb, ZF - 0.3), (2.4, 1.8, 0.5), 'leather_dark')
            p.cen((X0 + 1.7, yb, ZF - 0.55), (1.2, 1.3, 0.4), 'gold_metal')
            p.cen((X0 + 1.7, yb, ZF - 0.78), (0.5, 0.5, 0.2), 'gold_metal2')
            p.cen((X0 - 0.3, yb, ZB + 0.05), (0.9, 1.0, 0.5), 'gold_metal2')
    # hojas: lineas arriba y abajo
    for x in (X0 + 1.6, X0 + 3.6, X0 + 5.6, X0 + 7.6):
        for yy in (Y1 - 0.4, Y0 + 0.4):
            p.cen((x, yy, (ZF + ZB) / 2), (0.3, 0.12, ZB - ZF - 2 * T), 'page_edge')
    # dos cintas marcapaginas que asoman abajo, con la punta en V
    for (x, l, col) in ((5.8, 3.4, 'cloth_ribbon'), (7.4, 2.4, 'cloth_ribbon2')):
        p.cen((x, Y0 - l / 2 + 0.5, (ZF + ZB) / 2 + 0.5), (0.9, l, 0.2), col)
        for sx in (-1, 1):
            p.cen((x + sx * 0.25, Y0 - l + 0.4, (ZF + ZB) / 2 + 0.5), (0.4, 0.8, 0.2), col, ('z', sx * 22.5))
    # lomo: tapas de metal arriba y abajo y plaquita del titulo
    for yy in (Y1 + 0.05, Y0 - 0.05):
        p.cen((X1 - 0.1, yy, (ZF + ZB) / 2), (1.7, 0.5, ZB - ZF + 0.5), 'gold_metal')
    p.cen((X1 + 0.62, Y0 + 8.6, (ZF + ZB) / 2), (0.25, 2.0, 2.4), 'gold_metal')
    p.cen((X1 + 0.7, Y0 + 8.6, (ZF + ZB) / 2), (0.2, 1.2, 1.6), 'gold_metal2')
    # relieve: marco en bajo relieve en las dos tapas
    marco(p, 'leather_dark', z=ZF - 0.05, inset=0.75, w=0.32)
    marco(p, 'leather_dark', z=ZB + 0.05, inset=0.75, w=0.32)


def marco(p, mat, z=ZF - 0.12, inset=1.4, w=0.5):
    cx, cy = (X0 + X1) / 2 - 0.4, (Y0 + Y1) / 2
    ww, hh = X1 - X0 - 2 * inset - 0.8, Y1 - Y0 - 2 * inset
    p.cen((cx, cy + hh / 2, z), (ww, w, 0.3), mat)
    p.cen((cx, cy - hh / 2, z), (ww, w, 0.3), mat)
    p.cen((cx - ww / 2, cy, z), (w, hh, 0.3), mat)
    p.cen((cx + ww / 2, cy, z), (w, hh, 0.3), mat)


CX, CY = (X0 + X1) / 2 - 0.4, (Y0 + Y1) / 2 + 0.2


# --------------------------------------------------------------------------------------------- tiers
def podrido():
    p = Pieza('libro_invocador_1', 'Grimorio Podrido', base_paleta(
        '#5a6630', '#3e4420', '#d8ccae', hoja='#c8bc8c',
        leather_rot=(hx('#7e8a3a'), 's'), leather_wound=(hx('#6a2a24'), 's'), stitch_thread=(hx('#2a2418'), 's'),
        bone_shard=(hx('#e2d6b6'), 's'), core_eye=(hx('#9dff4a'), 'pulse'), core_pupil=(hx('#1a2a08'), 's'),
        leather_cap=(hx('#9a4a2a'), 's'), bone_stem=(hx('#d8cca8'), 's'), core_slime=(hx('#8ae83a'), 'pulse'),
        bone_worm=(hx('#efe6c8'), 's')), tex_dir='item/libros3d')
    libro_base(p)
    for (x, l) in ((4.6, 2.6), (6.0, 1.4), (9.4, 3.2), (11.4, 1.8)):                     # baba que chorrea
        p.cen((x, Y0 - l / 2 + 0.2, ZF - 0.25), (0.6, l, 0.4), 'core_slime', glow=8)
        p.cen((x, Y0 - l + 0.1, ZF - 0.25), (0.9, 0.8, 0.6), 'core_slime', glow=8)
    p.cen((X0 - 0.9, 10.2, 7.6), (2.4, 3.0, 0.15), 'page_block', ('z', 22.5))              # hoja rota que asoma
    p.cen((X0 - 1.6, 9.4, 7.6), (0.9, 1.2, 0.18), 'page_edge', ('z', -22.5))
    for (x, y, a) in ((10.0, 7.6, 22.5), (5.2, 8.4, -22.5), (8.8, 12.6, 45)):              # gusanos
        p.cen((x, y, ZF - 0.3), (1.6, 0.5, 0.4), 'bone_worm', ('z', a))
    # manchas de podrido y una herida cosida
    for (x, y, w, h) in ((5.0, 11.6, 3.0, 2.0), (10.2, 4.2, 2.4, 2.6), (6.2, 3.4, 1.6, 1.4), (10.6, 12.0, 1.4, 1.2)):
        p.cen((x, y, ZF - 0.1), (w, h, 0.3), 'leather_rot')
    p.cen((7.2, 5.6, ZF - 0.12), (4.4, 0.8, 0.3), 'leather_wound', ('z', 22.5))
    for dx in (-1.4, 0, 1.4):
        p.cen((7.2 + dx, 5.6 + dx * 0.4, ZF - 0.25), (0.3, 1.8, 0.3), 'stitch_thread', ('z', -22.5))
    # ojo que mira (brilla) con parpados de cuero
    p.rbox((CX, CY + 1.2, ZF - 0.35), (4.2, 3.0, 0.6), 'leather_dark', r=0.6, eje='z')
    p.gema((CX, CY + 1.2, ZF - 0.6), 2.6, 'core_eye', eje='z', glow=13, largo=0.4)
    p.cen((CX, CY + 1.2, ZF - 0.85), (0.6, 1.6, 0.2), 'core_pupil')
    # huesos asomando y hongos en el lomo
    p.cen((4.4, 13.0, ZF - 0.3), (0.9, 2.6, 0.7), 'bone_shard', ('z', 22.5))
    p.cen((11.6, 2.8, ZF - 0.3), (0.8, 2.2, 0.7), 'bone_shard', ('z', -22.5))
    for (y, s) in ((4.2, 1.0), (10.4, 1.3), (12.6, 0.8)):
        p.cen((X1 + 0.9, y, 8.0), (0.5, 0.9 * s, 0.5), 'bone_stem')
        p.cen((X1 + 1.2, y + 0.6 * s, 8.0), (1.0 * s, 0.5, 1.6 * s), 'leather_cap')
    return p


def muneco():
    p = Pieza('libro_invocador_3', 'Grimorio del Muneco Maldito', base_paleta(
        '#a8865a', '#6a4a2a', '#8a8f98', hoja='#e0d4b4',
        cloth_patch=(hx('#7a5a3a'), 's'), cloth_patch2=(hx('#b85a4a'), 's'), stitch_red=(hx('#c22a2a'), 's'),
        stitch_black=(hx('#1e1a1a'), 's'), plate_button=(hx('#1a1a20'), 's'), plate_button2=(hx('#3a3a46'), 's'),
        silver_pin=(hx('#c8ccd4'), 's'), core_pin=(hx('#ff3a5a'), 'pulse'), core_pin2=(hx('#5affa0'), 'pulse'),
        cord_yarn=(hx('#d8543a'), 's'), cord_yarn2=(hx('#f08a3a'), 's'), cloth_heart=(hx('#d82a4a'), 's')),
        tex_dir='item/libros3d')
    libro_base(p, esquinas=False)
    for k, (x, h, a) in enumerate(((4.0, 2.4, 22.5), (5.4, 3.2, 0), (6.8, 2.6, -22.5), (8.2, 3.4, 22.5), (9.6, 2.8, 0),
                                   (11.0, 2.2, -22.5))):                                     # pelo de lana arriba
        p.cen((x, Y1 + h / 2 - 0.2, ZF + 0.6), (0.6, h, 0.6), 'cord_yarn' if k % 2 else 'cord_yarn2', ('z', a) if a else None)
    for (dx, dy, a) in ((-0.45, 0, 45), (0.45, 0, -45)):                                    # corazon cosido
        p.cen((10.6 + dx, 6.6 + dy, ZF - 0.2), (1.2, 1.2, 0.3), 'cloth_heart', ('z', a))
    p.cen((10.6, 5.9, ZF - 0.2), (1.0, 1.0, 0.3), 'cloth_heart', ('z', 45))
    p.cen((X1 + 0.9, 6.0, 8.0), (0.25, 0.25, 6.6), 'silver_pin')                           # aguja y hilo por el lomo
    p.cen((X1 + 0.9, 6.0, 4.5), (0.5, 0.5, 0.4), 'silver_pin')
    p.cen((X1 + 1.0, 4.6, 11.2), (0.2, 3.0, 0.2), 'stitch_red', ('x', 22.5))
    for k in ('leather_cover',):
        p.palette[k] = (hx('#a8865a'), 's')
    # remiendos cosidos
    p.cen((5.2, 11.8, ZF - 0.1), (3.2, 2.8, 0.3), 'cloth_patch')
    p.cen((10.4, 3.6, ZF - 0.1), (2.6, 2.4, 0.3), 'cloth_patch2')
    for (x, y) in ((3.8, 11.8), (6.6, 11.8), (9.2, 3.6), (11.6, 3.6)):
        p.cen((x, y, ZF - 0.28), (0.25, 2.2, 0.2), 'stitch_black')
    # cara de muneco: ojos de boton y boca cosida
    for dx in (-1.9, 1.9):
        p.octo((CX + dx, CY + 1.8, ZF - 0.4), 1.2, 0.6, 'z', 'plate_button', lados=8)
        for (ex, ey) in ((-0.35, 0.35), (0.35, 0.35), (-0.35, -0.35), (0.35, -0.35)):
            p.cen((CX + dx + ex, CY + 1.8 + ey, ZF - 0.72), (0.3, 0.3, 0.1), 'plate_button2')
    p.cen((CX, CY - 1.6, ZF - 0.2), (4.6, 0.3, 0.3), 'stitch_red')
    for dx in (-1.8, -0.6, 0.6, 1.8):
        p.cen((CX + dx, CY - 1.6, ZF - 0.32), (0.3, 1.3, 0.2), 'stitch_red')
    # costura en X en el lomo y alfileres clavados
    for y in (4.0, 8.0, 12.0):
        p.cen((X1 + 0.55, y, 8.0), (0.3, 1.6, 0.3), 'stitch_red', ('x', 45))
        p.cen((X1 + 0.55, y, 8.0), (0.3, 1.6, 0.3), 'stitch_red', ('x', -45))
    for (x, y, a, head) in ((10.8, 12.6, 22.5, 'core_pin'), (4.6, 4.4, -22.5, 'core_pin2'), (11.4, 9.0, 45, 'core_pin')):
        p.cen((x, y, ZF - 1.0), (0.22, 0.22, 2.2), 'silver_pin', ('x', a))
        p.cen((x, y + (0.7 if a > 0 else -0.7), ZF - 1.9), (0.7, 0.7, 0.7), head, glow=12)
    return p


def evocador():
    p = Pieza('libro_invocador_5', 'Grimorio del Evocador', base_paleta(
        '#2e3a52', '#1e2436', '#d8a83a', hoja='#e6dcc0',
        plate_robe=(hx('#4a5a7a'), 's'), bone_fang=(hx('#eef2f6'), 's'), bone_fang2=(hx('#b8c0c8'), 's'),
        gem_emerald=(hx('#2fe07a'), 'pulse'), core_magic=(hx('#6af0d8'), 'pulse'), leather_red=(hx('#7a1e24'), 's')),
        tex_dir='item/libros3d')
    libro_base(p)
    marco(p, 'gold_metal')
    marco(p, 'gold_metal2', inset=2.2, w=0.3)
    # colmillos del evocador saliendo de un circulo magico
    p.octo((CX, CY - 0.4, ZF - 0.2), 2.8, 0.3, 'z', 'core_magic', glow=11, lados=8)
    p.octo((CX, CY - 0.4, ZF - 0.3), 2.2, 0.32, 'z', 'leather_dark', lados=8)
    for (dx, h, a) in ((-1.2, 3.4, -22.5), (0, 4.2, 0), (1.2, 3.2, 22.5)):
        p.cen((CX + dx, CY + 0.4 + h / 2 - 1.2, ZF - 0.7), (0.9, h, 0.7), 'bone_fang', ('z', a) if a else None)
        p.cen((CX + dx, CY + h - 1.5, ZF - 0.75), (0.5, 0.8, 0.6), 'bone_fang2', ('z', a) if a else None)
    # esmeralda arriba y cinta roja (marcador)
    p.octo((CX, Y1 - 2.4, ZF - 0.25), 1.3, 0.3, 'z', 'gold_metal', lados=8)
    p.gema((CX, Y1 - 2.4, ZF - 0.4), 1.6, 'gem_emerald', eje='z', glow=13, largo=0.5)
    for k in range(5):                                                                      # colmillos en el borde
        x = 4.6 + k * 1.7
        p.cen((x, Y0 + 1.75, ZF - 0.28), (0.7, 0.7, 0.2), 'bone_fang', ('z', 45))
        p.cen((x, Y1 - 1.75, ZF - 0.28), (0.7, 0.7, 0.2), 'bone_fang', ('z', 45))
    for sx in (-1, 1):                                                                      # alitas de vex a los costados
        for k, (dy, l) in enumerate(((0.0, 2.6), (-0.9, 2.0), (-1.7, 1.4))):
            p.cen((CX + sx * (3.2 + l / 2), CY - 0.2 + dy, ZF - 0.35), (l, 0.6, 0.25), 'bone_fang2', ('z', sx * 22.5))
    p.cen((9.0, Y0 - 1.4, 8.0), (0.9, 3.0, 0.3), 'leather_red')
    p.cen((9.0, Y0 - 3.0, 8.0), (1.2, 0.6, 0.3), 'leather_red', ('z', 45))
    return p


def dragon():
    p = Pieza('libro_invocador_7', 'Grimorio de Piel de Dragon', base_paleta(
        '#8a1e1e', '#5a1010', '#3a2a24', hoja='#e8d8b0',
        scale_red=(hx('#a8302a'), 's'), scale_dark=(hx('#5a1414'), 's'), bone_horn=(hx('#e8dcc0'), 's'),
        bone_horn2=(hx('#a89a80'), 's'), core_iris=(hx('#ffb020'), 'pulse'), core_slit=(hx('#1a0a04'), 's'),
        gold_claw=(hx('#2a1e1a'), 's')), tex_dir='item/libros3d')
    p.palette['leather_cover'] = (hx('#8a1e1e'), 's')
    libro_base(p, esquinas=False)
    # escamas en relieve (filas alternadas)
    for row, y in enumerate((3.0, 5.0, 11.4, 13.0)):
        for k in range(4):
            x = 4.6 + k * 2.2 + (1.1 if row % 2 else 0)
            if x < X1 - 1.2:
                p.cen((x, y, ZF - 0.15), (1.5, 1.5, 0.4), 'scale_red' if (k + row) % 2 else 'scale_dark', ('z', 45))
    # ojo de dragon con parpado
    p.rbox((CX, CY, ZF - 0.3), (5.0, 3.6, 0.6), 'scale_dark', r=0.8, eje='z')
    p.gema((CX, CY, ZF - 0.55), 3.0, 'core_iris', eje='z', glow=14, largo=0.4)
    p.cen((CX, CY, ZF - 0.82), (0.5, 2.6, 0.2), 'core_slit')
    for s in (-1, 1):
        p.cen((CX + s * 2.6, CY + 1.4, ZF - 0.5), (1.6, 0.7, 0.6), 'bone_horn2', ('z', -s * 22.5))
    # garras en las esquinas y cuernos en el lomo
    for (x, y, a) in ((X0 + 0.8, Y0 + 0.8, 45), (X0 + 0.8, Y1 - 0.8, -45), (X1 - 1.4, Y0 + 0.8, -45), (X1 - 1.4, Y1 - 0.8, 45)):
        p.cen((x, y, ZF - 0.2), (2.2, 0.8, 0.6), 'gold_claw', ('z', a))
    for (y, h) in ((3.4, 1.8), (6.6, 2.4), (9.8, 2.4), (12.8, 1.8)):
        p.cen((X1 + 1.0 + h / 2 * 0.6, y, 8.0), (h, 0.9, 0.9), 'bone_horn', ('z', 22.5))
        p.cen((X1 + 1.2 + h * 0.7, y + 0.5, 8.0), (0.7, 0.5, 0.6), 'bone_horn2', ('z', 45))
    for (y, a) in ((Y1 - 1.2, 22.5), (Y0 + 1.2, -22.5)):                                     # membranas de ala del lomo
        p.cen((X1 + 2.6, y, 8.0), (3.6, 2.6, 0.2), 'scale_dark', ('z', a))
        p.cen((X1 + 2.6, y, 8.0), (3.8, 0.3, 0.32), 'bone_horn2', ('z', a))
    for row, y in enumerate((7.2, 9.2)):                                                     # escamas a los costados del ojo
        for x in (4.4, 12.0):
            p.cen((x, y, ZF - 0.15), (1.5, 1.5, 0.4), 'scale_red' if row else 'scale_dark', ('z', 45))
    for (x, a) in ((X0 - 0.4, 22.5), (X0 - 0.4, -22.5)):                                     # garras que cierran el libro
        y = (Y0 + Y1) / 2 + (2.6 if a > 0 else -2.6)
        p.cen((x, y, 8.0), (0.8, 2.4, 0.8), 'bone_horn', ('z', a))
        p.cen((x - 0.6, y + (0.9 if a > 0 else -0.9), ZF - 0.2), (0.7, 1.6, 0.7), 'bone_horn2', ('x', 45))
    return p


def necronomicon():
    p = Pieza('libro_invocador_9', 'Necronomicon', base_paleta(
        '#2c1c1e', '#1a1012', '#6a6e78', hoja='#d0c4a4',
        bone_skull=(hx('#e4dac2'), 's'), bone_skull2=(hx('#b8ac90'), 's'), core_eye=(hx('#c25aff'), 'pulse'),
        stitch_skin=(hx('#4a2e2a'), 's'), chain_link=(hx('#7a7e88'), 's'), chain_dark=(hx('#4a4e58'), 's'),
        core_rune=(hx('#9a4aff'), 'flow'), iron_lock=(hx('#8a6a3a'), 's')), tex_dir='item/libros3d')
    libro_base(p, broche=False)
    # cara de calavera en relieve
    p.rbox((CX, CY + 0.6, ZF - 0.45), (5.2, 4.8, 0.9), 'bone_skull', r=1.0, eje='z')
    p.rbox((CX, CY - 2.2, ZF - 0.4), (3.6, 1.6, 0.8), 'bone_skull2', r=0.4, eje='z')
    for dx in (-1.3, 1.3):
        p.cen((CX + dx, CY + 1.0, ZF - 0.95), (1.4, 1.5, 0.2), 'core_eye', glow=14)
    p.cen((CX, CY - 0.4, ZF - 0.95), (0.6, 0.9, 0.2), 'stitch_skin', ('z', 45))
    for dx in (-1.2, -0.4, 0.4, 1.2):
        p.cen((CX + dx, CY - 2.0, ZF - 0.85), (0.5, 0.9, 0.2), 'bone_skull' if dx % 0.8 else 'bone_skull2')
    # costuras de piel y runas que brillan
    for (x, y, a) in ((4.6, 12.0, 45), (11.2, 12.4, -45), (4.4, 3.8, -45), (11.0, 3.4, 45)):
        p.cen((x, y, ZF - 0.12), (2.4, 0.3, 0.3), 'stitch_skin', ('z', a))
    for y in (3.4, 7.2, 11.0):
        p.cen((X1 + 0.5, y, 8.0), (0.3, 1.8, 0.6), 'core_rune', glow=12)
    # dos cadenas que rodean el libro y candado
    for y in (5.0, 11.4):
        p.cen(((X0 + X1) / 2, y, ZF - 0.55), (X1 - X0 + 0.6, 0.6, 0.4), 'chain_link')
        p.cen(((X0 + X1) / 2, y, ZB + 0.55), (X1 - X0 + 0.6, 0.6, 0.4), 'chain_link')
        p.cen((X0 - 0.45, y, 8.0), (0.4, 0.6, ZB - ZF + 1.4), 'chain_dark')
        p.cen((X1 + 0.75, y, 8.0), (0.4, 0.6, ZB - ZF + 1.4), 'chain_dark')
        for x in (4.0, 6.0, 8.0, 10.0, 12.0):
            p.cen((x, y, ZF - 0.75), (0.8, 0.9, 0.2), 'chain_dark')
    p.rbox((X0 + 0.4, 5.0, ZF - 0.9), (1.8, 2.0, 0.8), 'iron_lock', r=0.3)
    for k in range(6):                                                                       # el libro muerde: dientes
        y = 3.0 + k * 1.9
        p.cen((X0 - 0.15, y, 7.25), (0.5, 0.9, 0.6), 'bone_skull', ('z', 45))
        p.cen((X0 - 0.15, y + 0.95, 8.75), (0.5, 0.9, 0.6), 'bone_skull', ('z', 45))
    p.cen((X1 + 0.75, Y1 - 2.4, 8.0), (0.3, 1.6, 2.2), 'bone_skull2')                         # ojo en el lomo
    p.cen((X1 + 0.85, Y1 - 2.4, 8.0), (0.25, 0.9, 1.2), 'core_eye', glow=14)
    for (x, y) in ((X0 + 1.0, Y0 + 1.0), (X1 - 1.6, Y0 + 1.0), (X0 + 1.0, Y1 - 1.0), (X1 - 1.6, Y1 - 1.0)):
        for d in (-0.5, 0.5):                                                                # costillas en las esquinas
            p.cen((x + d * 0.6, y + d, ZF - 0.3), (2.2, 0.4, 0.3), 'bone_skull2', ('z', 45 if (x < 8) == (y < 8) else -45))
    p.cen((X0 + 0.4, 6.3, ZF - 0.9), (1.2, 0.9, 0.3), 'chain_dark')
    return p


def dorado():
    p = Pieza('libro_invocador_10', 'Grimorio Dorado', base_paleta(
        '#ece4cc', '#d8b040', '#f2c040', hoja='#f4e8c4',
        gold_trim=(hx('#ffd860'), 's'), gold_dark=(hx('#a87a1c'), 's'), gem_sun=(hx('#5ae8ff'), 'pulse'),
        gem_sun2=(hx('#e8fcff'), 'pulse'), gem_ruby=(hx('#ff4a6a'), 'pulse'), crystal_rune=(hx('#ffe890'), 'spark'),
        page_gold=(hx('#f0c850'), 's')), tex_dir='item/libros3d')
    p.palette['page_edge'] = (hx('#e8b830'), 's')
    libro_base(p)
    marco(p, 'gold_trim', inset=1.2, w=0.6)
    marco(p, 'gold_dark', inset=2.1, w=0.3)
    # sol central con rayos y gema
    p.octo((CX, CY, ZF - 0.3), 2.6, 0.5, 'z', 'gold_trim')
    for a in (0, 45):
        p.cen((CX, CY, ZF - 0.2), (7.2, 0.7, 0.3), 'gold_dark', ('z', a))
        p.cen((CX, CY, ZF - 0.2), (0.7, 7.2 if a == 0 else 7.2, 0.3), 'gold_dark', ('z', a))
    p.gema((CX, CY, ZF - 0.7), 3.0, 'gem_sun', eje='z', glow=15, largo=0.6)
    p.gema((CX - 0.4, CY + 0.4, ZF - 0.95), 1.0, 'gem_sun2', eje='z', glow=15, largo=0.2)
    # gemas rojas en los esquineros, lomo dorado y runas flotando
    for (x, y) in ((X0 + 0.9, Y0 + 0.9), (X0 + 0.9, Y1 - 0.9), (X1 - 1.6, Y0 + 0.9), (X1 - 1.6, Y1 - 0.9)):
        p.gema((x, y, ZF - 0.5), 0.9, 'gem_ruby', eje='z', glow=12, largo=0.3)
    for (dy, a, l) in ((0.0, 22.5, 4.2), (-1.2, 45, 3.4), (-2.3, 45, 2.6)):                 # alas doradas del lomo
        for (yb, sg) in ((Y1 - 2.0, 1), (Y0 + 2.6, -1)):
            p.cen((X1 + 1.0 + l / 2, yb + sg * dy, 8.0), (l, 0.9, 0.35), 'gold_trim', ('z', sg * a))
            p.cen((X1 + 1.2 + l / 2, yb + sg * dy - 0.35 * sg, 8.0), (l * 0.8, 0.3, 0.38), 'gold_dark', ('z', sg * a))
    import math as _m
    for k in range(8):                                                                       # aureola (anillo de 8 tramos)
        a = k * 45
        px, pz = CX + 2.7 * _m.cos(_m.radians(a)), 8.0 + 2.7 * _m.sin(_m.radians(a))
        size = (0.4, 0.3, 2.3) if a % 180 == 0 else (2.3, 0.3, 0.4) if a % 180 == 90 else (2.3, 0.3, 0.4)
        rot = None if a % 90 == 0 else ('y', 45 if a in (45, 225) else -45)
        p.cen((px, Y1 + 2.2, pz), size, 'crystal_rune', rot, 15)
    for (x, y) in ((X0 + 2.4, Y0 + 2.4), (X1 - 3.0, Y0 + 2.4), (X0 + 2.4, Y1 - 2.4), (X1 - 3.0, Y1 - 2.4)):
        p.cen((x, y, ZF - 0.35), (0.6, 0.6, 0.4), 'page_block')                              # perlas
    for (x, y, z, s) in ((1.4, 15.6, 4.0, 0.7), (14.8, 12.0, 3.6, 0.6), (15.4, 3.2, 6.0, 0.55), (2.0, 1.0, 3.4, 0.6)):
        p.cen((x, y, z), (s, s * 2.2, 0.25), 'crystal_rune', glow=15)
        p.cen((x, y, z), (s * 2.2, s, 0.25), 'crystal_rune', glow=15)
    return p


CONSTRUCTORES = {1: podrido, 3: muneco, 5: evocador, 7: dragon, 9: necronomicon, 10: dorado}

# Espacio de la mano: tapa de adelante (-Z) hacia afuera (+X de la mano), arriba del libro arriba, lomo atras.
MANO3 = {'rot': [0, -90, -90], 'destino': (0.8, -2.0, 1.6), 'escala': 0.72}
MANO1 = {'rot': [8, 158, -6], 'destino': (-6.2, 3.4, -1.5), 'escala': 0.5}


def contratapa(p):
    """Tapa de atras: medallon con el mismo metal del libro y un circulo de invocacion grabado."""
    z = ZB + 0.15
    p.octo((CX, CY, z), 2.6, 0.3, 'z', 'gold_metal2', lados=8)
    p.octo((CX, CY, z + 0.1), 1.9, 0.32, 'z', 'leather_dark', lados=8)
    p.cen((CX, CY, z + 0.2), (0.6, 2.8, 0.2), 'gold_metal')
    p.cen((CX, CY, z + 0.2), (2.8, 0.6, 0.2), 'gold_metal')
    p.cen((CX, CY, z + 0.25), (1.0, 1.0, 0.25), 'gold_metal', ('z', 45))
    for (x, y) in ((CX, Y1 - 1.6), (CX, Y0 + 1.6)):
        p.cen((x, y, z), (5.0, 0.4, 0.3), 'gold_metal2')


def libro(t):
    p = CONSTRUCTORES[t]()
    contratapa(p)
    p.agarre = (X1 - 1.0, Y0 + 3.0, (ZF + ZB) / 2)
    p.poses = {
        'thirdperson_righthand': p.pose(MANO3['rot'], MANO3['destino'], MANO3['escala']),
        'firstperson_righthand': p.pose(MANO1['rot'], MANO1['destino'], MANO1['escala']),
    }
    p.gui_rot = [14, 205, 0]
    return p


def piezas():
    return [libro(t) for t in TIERS]


def assets():
    return P.assets(piezas())


def check():
    return [x for p in piezas() for x in p.check()]


if __name__ == '__main__':
    import numpy as np
    R = np.array(P.rot_xyz(MANO3['rot']))
    print('3ra persona: tapa(-Z) ->', (R @ [0, 0, -1]).round(2), ' arriba(+Y) ->', (R @ [0, 1, 0]).round(2))
    for x in check():
        print('AVISO:', x)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'build', 'previews', 'libros_3d.png')
    P.hoja(piezas(), out, 'Libros del Invocador 3D (22/11)')
    print({p.iid: len(p.els) for p in piezas()})
