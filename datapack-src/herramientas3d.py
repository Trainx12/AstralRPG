# -*- coding: utf-8 -*-
"""Taladros I-IX y motosierras en 3D (pedido del dueno 22/11/2026).

Siguen el diseno de los iconos del dueno (pack-source/art/ref_19_11, iconos_19_11.py) pero esculpidos con volumen:
- Taladro: broca en espiral (secciones en cruz que giran 22,5 grados cada una, con brillo que corre), collar con
  anillo de luz, carcasa redonda con tapas de engranaje a los dos lados y la gema que brilla, aletas, luces atras,
  mango de pistola inclinado con vendas y remaches, gatillo y manguera.
- Motosierra: espada (barra) con ranura y vetas, cadena que se mueve (textura animada) con dientes de verdad,
  nariz redondeada, motor con rejillas que brillan, tapa del pinon, guardamano, asa de arriba, tirador, escape
  y el mango de pistola de atras.
Cada tier cambia colores y agrega lo suyo (cristales, oro, chispas, fuego, cristal astral).

En el inventario se ven de costado (como el icono); en la mano se agarran del mango y apuntan adelante.

Uso: python herramientas3d.py   -> build/previews/herramientas_3d.png (lamina de revision)
build_pack.py llama a assets() despues de iconos_19_11 (gana sobre los modelos planos).
"""
import os

import piezas3d as P
from piezas3d import Pieza, hx, aclarar, oscurecer

Y0 = 11.0   # altura del eje (canon) en el modelo

# Agarre en la mano (pixeles del espacio de la mano, ver piezas3d._mano3/_mano1)
MANO3 = {'rot': [80, 0, 0], 'destino': (0, -2.0, 2.6), 'escala': 0.6}
MANO1 = {'rot': [4, 24, -3], 'destino': (-1.5, 0.6, 0.0), 'escala': 0.5}

GRIS = '#727c8e'
OSC = '#3a404c'
MANGO = '#7a3328'


def _paleta(c):
    """Muestras de una herramienta a partir de sus colores."""
    b, bl, bd = hx(c['broca']), hx(c.get('broca_luz') or '#ffffff'), hx(c.get('broca_osc') or '#000000')
    if not c.get('broca_luz'):
        bl = aclarar(b, 0.55)
    if not c.get('broca_osc'):
        bd = oscurecer(b, 0.45)
    cuerpo = hx(c.get('cuerpo', GRIS))
    acento = hx(c.get('acento', '#3a4252'))
    gema = hx(c['gema'])
    pal = {
        'prism_fin': (b, 'flow'),
        'prism_fin2': (c.get('broca2') and hx(c['broca2']) or bl, 'flow'),
        'steel_bitcore': (bd, 's'),
        'crystal_tip': (aclarar(b, 0.7), 'pulse'),
        'steel_body': (cuerpo, 's'),
        'steel_hi': (aclarar(cuerpo, 0.25), 's'),
        'iron_dark': (hx(c.get('oscuro', OSC)), 's'),
        'plate_acc': (acento, 's'),
        'plate_acc2': (aclarar(acento, 0.22), 's'),
        'plate_disc': (hx(c.get('disco', '#4a5262')), 's'),
        'gold_trim': (hx(c.get('trim', '#9aa3b4')), 's'),
        'silver_rivet': (hx('#b9c3cf'), 's'),
        'gem_core': (gema, 'pulse'),
        'gem_hi': (aclarar(gema, 0.6), 'pulse'),
        'core_vent': (hx(c.get('luz', c['gema'])), c.get('luz_anim', 'pulse')),
        'wood_grip': (hx(c.get('mango', MANGO)), 's'),
        'wrap_grip': (oscurecer(hx(c.get('mango', MANGO)), 0.35), 's'),
        'rubber_hose': (hx(c.get('manguera', '#3fb6d0')), 's'),
        'rubber_grip': (hx('#24262c'), 's'),
        'silver_face': (hx('#e8eef2'), 's'),
        'core_needle': (hx('#ff3a3a'), 's'),
        'crystal_fuel': (hx(c.get('nafta', '#ffb030')), 'pulse'),
    }
    for k, col in (c.get('cristales') or {}).items():
        pal['crystal_' + k] = (hx(col), 'pulse')
    if c.get('chispas'):
        pal['crystal_spark'] = (hx(c['chispas']), 'spark')
    if c.get('teeth'):
        pal['teeth_chain'] = (hx(c['teeth']), c.get('teeth_anim', 'flow'))
    return pal


# ============================================================================================= taladros
TALADROS = {
    'taladro_diamante': dict(nombre='Taladro de Diamante', broca='#3ed6ea', gema='#7ff4ff', acento='#3a4252',
                             manguera='#3fc4dc', extra={'manguera'}),
    'taladro_mitril': dict(nombre='Taladro de Mitril', broca='#27b8a2', gema='#7ff4ff', acento='#2f8f6a',
                           disco='#3a6a5c', manguera='#2fae96', extra={'manguera', 'placas'}),
    'taladro_amatista': dict(nombre='Taladro de Amatista', broca='#9a4dff', gema='#c98aff', acento='#2f6f6a',
                             disco='#3a5c5c', cristales={'a': '#a45cff', 'b': '#d9b0ff'}, extra={'placas', 'cristales'}),
    'taladro_rubi': dict(nombre='Taladro de Rubi', broca='#d3203c', gema='#a46cff', acento='#4a2a30',
                         cuerpo='#4f5565', luz='#ffa02a', luz_anim='flicker', extra={'rejilla'}),
    'taladro_topacio': dict(nombre='Taladro de Topacio', broca='#f2a91e', broca2='#5e3510', gema='#ffb02a',
                            acento='#c8901e', trim='#e8b840', disco='#6a4a20', luz='#ff4a3a', extra={'oro', 'luces'}),
    'taladro_titanio': dict(nombre='Taladro de Titanio', broca='#8fa6bc', gema='#d8f6ff', acento='#4a5262',
                            cuerpo='#6c7686', manguera='#5ab8d8', extra={'manguera'}),
    'taladro_jaspe': dict(nombre='Taladro de Jaspe', broca='#e3307e', gema='#ff5aa8', acento='#3a1420',
                          cuerpo='#2e1a24', oscuro='#1c0e16', disco='#4a1a2e', luz='#ff3a8a', luz_anim='flow',
                          extra={'vetas', 'rejilla'}),
    'taladro_gemas': dict(nombre='Taladro de Gemas', broca='#9a5cff', gema='#3dff8a', acento='#3a3048',
                          cristales={'a': '#9a5cff', 'b': '#3dff9a', 'c': '#5ad8ff'}, extra={'arcoiris', 'cristales', 'aro'}),
    'taladro_divan': dict(nombre='Taladro Divino', broca='#ffc21e', broca2='#4a3010', gema='#2fe07a',
                          acento='#d8a020', cuerpo='#5a4a2a', trim='#ffd860', disco='#c89020', oscuro='#3a2a10',
                          luz='#ffe070', chispas='#fff2a0', extra={'oro', 'chispas', 'aro'}),
}

ARCOIRIS = ('#b05cff', '#7a6cff', '#4a9cff', '#3ad8ff', '#3dffc8', '#5aff7a', '#d8ff5a')


def taladro(iid, c):
    pal = _paleta(c)
    ex = c.get('extra', set())
    if 'arcoiris' in ex:
        for i, col in enumerate(ARCOIRIS):
            pal[f'prism_rb{i}'] = (hx(col), 'flow')
    p = Pieza(iid, c['nombre'], pal, tex_dir='item/herramientas3d')
    y = Y0

    # ---- broca: cono suave de 10 tramos que giran (espiral), dos surcos en helice y punta de cristal
    import math
    n, z0, z1, r0, r1 = 10, 7.0, -6.8, 4.2, 0.7
    L = abs(z1 - z0) / n + 0.15
    for k in range(n):
        t = (k + 0.5) / n
        z, h = z0 + (z1 - z0) * t, r0 + (r1 - r0) * t
        a = (0, 22.5, 45, -22.5)[k % 4]
        kr = min(6, k * 7 // n)
        fa = f'prism_rb{kr}' if 'arcoiris' in ex else ('prism_fin2' if 'broca2' in c and k % 2 else 'prism_fin')
        fb = f'prism_rb{kr}' if 'arcoiris' in ex else ('prism_fin' if 'broca2' in c and k % 2 else 'prism_fin2' if 'broca2' in c else 'prism_fin')
        p.cen((8, y, z), (1.5 * h, 1.5 * h, L), 'steel_bitcore', ('z', a))
        p.cen((8, y, z), (2 * h, 0.85, L), fa, ('z', a))
        p.cen((8, y, z), (0.85, 2 * h, L), fb, ('z', a))
    for hel, mat in ((0, 'steel_bitcore'), (180, 'prism_fin2')):
        for k in range(13):
            t = (k + 0.5) / 13
            z, r = z0 + (z1 - z0) * t, (r0 + (r1 - r0) * t) * 1.0
            ang = math.radians(hel + k * 42)
            sz = 0.75 - 0.35 * t
            p.cen((8 + r * math.cos(ang), y + r * math.sin(ang), z), (sz, sz, 1.15), mat)
    p.gema((8, y, -7.6), 1.3, 'crystal_tip', eje='z', glow=10, largo=1.6)
    p.cen((8, y, -8.3), (0.5, 0.5, 0.8), 'crystal_tip', glow=10)

    # ---- collar con anillo de luz y tornillos
    p.octo((8, y, 8.4), 4.6, 2.4, 'z', 'iron_dark')
    p.octo((8, y, 7.1), 3.9, 0.4, 'z', 'core_vent', glow=12)
    for z in (7.5, 9.3):
        p.octo((8, y, z), 4.95, 0.45, 'z', 'steel_hi', lados=8)
    for k in range(8):
        a = math.radians(k * 45 + 22.5)
        p.cen((8 + 4.6 * math.cos(a), y + 4.6 * math.sin(a), 8.4), (0.8, 0.8, 1.1), 'silver_rivet', ('z', 45))

    # ---- carcasa redonda
    p.octo((8, y, 14.8), 5.1, 9.6, 'z', 'steel_body')
    for z in (10.2, 19.4):
        p.octo((8, y, z), 5.5, 1.1, 'z', 'gold_trim' if 'oro' in ex else 'iron_dark')
    # placa de arriba (color del tier) con aletas
    p.rbox((8, y + 5.0, 14.8), (5.2, 1.0, 7.6), 'plate_acc', r=0.4, eje='y')
    for z in (12.2, 14.8, 17.4):
        p.cen((8, y + 5.9, z), (3.2, 1.1, 0.7), 'iron_dark')
    # tapas de engranaje a los dos lados con la gema
    for s in (-1, 1):
        x = 8 + s * 5.25
        p.octo((x, y, 14.8), 4.1, 0.9, 'x', 'plate_disc')
        for k in range(8):
            a = math.radians(k * 45)
            big = k % 2 == 0
            p.cen((x, y + 4.5 * math.sin(a), 14.8 + 4.5 * math.cos(a)), (1.1 if big else 0.9, 1.8 if big else 1.2, 1.8 if big else 1.2),
                  'steel_hi' if big else 'iron_dark', None if big else ('x', 45))
        p.octo((x + s * 0.2, y, 14.8), 3.4, 0.5, 'x', 'iron_dark', lados=8)
        p.octo((x + s * 0.4, y, 14.8), 2.5, 0.5, 'x', 'gold_trim')
        p.gema((x + s * 0.75, y, 14.8), 2.6, 'gem_core', eje='x', glow=15, largo=0.7)
        p.gema((x + s * 1.05, y + 0.35, 14.45), 1.0, 'gem_hi', eje='x', glow=15, largo=0.3)
        for (dy, dz) in ((2.6, 2.6), (-2.6, 2.6), (2.6, -2.6), (-2.6, -2.6)):
            p.cen((x + s * 0.5, y + dy, 14.8 + dz), (0.5, 0.6, 0.6), 'silver_rivet')
    # parte de atras: bloque con puerto redondo (anillos y nucleo que brilla), leds, rejilla
    p.rbox((8, y, 21.4), (8.4, 8.4, 2.4), 'iron_dark', r=1.6, eje='z')
    p.octo((8, y - 0.4, 22.7), 2.9, 0.4, 'z', 'steel_hi')
    p.octo((8, y - 0.4, 22.95), 2.1, 0.4, 'z', 'iron_dark')
    p.octo((8, y - 0.4, 23.15), 1.1, 0.3, 'z', 'core_vent', glow=13)
    for dx in (-2.2, 0, 2.2):
        p.cen((8 + dx, y + 3.3, 22.7), (1.0, 0.6, 0.3), 'core_vent', glow=12)
    for dy in (-1.2, 0, 1.2):
        for sx in (-1, 1):
            p.cen((8 + sx * 4.25, y + dy, 21.4), (0.2, 0.5, 1.6), 'steel_bitcore')
    # manometro arriba atras
    p.octo((5.7, y + 5.7, 18.4), 1.4, 0.7, 'y', 'steel_hi', lados=8)
    p.octo((5.7, y + 6.08, 18.4), 1.05, 0.12, 'y', 'silver_face', lados=8)
    p.cen((5.7, y + 6.18, 18.15), (0.18, 0.1, 0.9), 'core_needle', ('y', 45))
    # ---- lo que se ve en la mano (1ra persona: costado -X, atras y arriba)
    for (dx, dy) in ((-3.2, 3.2), (3.2, 3.2), (-3.2, -3.6), (3.2, -3.6)):                  # tornillos de la tapa de atras
        p.cen((8 + dx, y + dy, 22.65), (0.6, 0.6, 0.25), 'silver_rivet', ('z', 45))
    for k in range(4):                                                                     # barra de carga
        p.cen((6.6 + k * 0.95, y - 3.3, 22.7), (0.75, 0.6, 0.25), 'core_vent' if k < 3 else 'iron_dark', glow=13 if k < 3 else 0)
    p.octo((8, y - 0.4, 22.62), 3.3, 0.25, 'z', 'plate_acc2', lados=8)                     # aro del color del tier
    p.octo((8, y + 6.3, 11.6), 0.75, 3.2, 'z', 'iron_dark', lados=8)                       # mira de arriba con lente
    p.octo((8, y + 6.3, 9.95), 0.55, 0.15, 'z', 'gem_hi', glow=14, lados=8)
    for z in (10.8, 12.4):
        p.cen((8, y + 5.75, z), (0.6, 0.8, 0.5), 'iron_dark')
    p.cen((3.1, y + 2.4, 21.4), (1.4, 0.4, 0.4), 'steel_hi')                                # palanca con perilla roja
    p.cen((2.3, y + 2.4, 21.4), (0.7, 0.7, 0.7), 'core_needle')
    # canos a los costados de abajo (del bloque de atras al collar)
    for sx in (-1, 1):
        p.cen((8 + sx * 3.9, y - 3.9, 14.6), (0.8, 0.8, 10.6), 'steel_hi')
        for z in (9.8, 19.6):
            p.cen((8 + sx * 3.9, y - 3.9, z), (1.2, 1.2, 0.6), 'iron_dark')
    # emblema del tier en la placa de arriba
    p.gema((8, y + 5.75, 11.2), 1.5, 'gem_core', eje='y', glow=14, largo=0.5)

    # ---- mango de pistola inclinado + gatillo
    p.rbox((8, y - 5.2, 18.0), (4.2, 2.6, 6.0), 'steel_body', r=0.8)
    gc = (8, y - 9.0, 19.6)
    rot = ('x', -22.5, gc)
    p.box((8 - 1.75, gc[1] - 4.9, gc[2] - 2.1), (8 + 1.75, gc[1] + 4.9, gc[2] + 2.1), 'wood_grip', rot)
    for t in (-2.9, -0.9, 1.1, 3.1):
        p.box((8 - 1.95, gc[1] + t - 0.35, gc[2] - 2.3), (8 + 1.95, gc[1] + t + 0.35, gc[2] + 2.3), 'wrap_grip', rot)
    for t in (2.1, -1.9):
        for s in (-1, 1):
            p.box((8 + s * 1.75 - 0.25, gc[1] + t - 0.45, gc[2] - 0.45), (8 + s * 1.75 + 0.25, gc[1] + t + 0.45, gc[2] + 0.45),
                  'silver_rivet', rot)
    p.box((8 - 2.0, gc[1] - 5.8, gc[2] - 2.4), (8 + 2.0, gc[1] - 4.7, gc[2] + 2.4), 'iron_dark', rot)
    for dz in (-0.9, 0.9):                                                   # anilla
        p.box((8 - 0.25, gc[1] - 7.2, gc[2] + dz - 0.25), (8 + 0.25, gc[1] - 5.8, gc[2] + dz + 0.25), 'steel_hi', rot)
    p.box((8 - 0.25, gc[1] - 7.5, gc[2] - 1.15), (8 + 0.25, gc[1] - 7.0, gc[2] + 1.15), 'steel_hi', rot)
    for t in (-2.0, 0.0, 2.0):                                               # dedos marcados adelante
        p.box((8 - 1.5, gc[1] + t - 0.45, gc[2] - 2.45), (8 + 1.5, gc[1] + t + 0.45, gc[2] - 2.0), 'wood_grip', rot)
    p.cen((8, y - 6.4, 15.6), (0.9, 2.4, 0.8), 'plate_acc2', ('x', 22.5))   # gatillo
    if 'manguera' in ex:
        q = (8, y - 5.0, 11.8)
        for nxt in ((8, y - 7.6, 11.9), (8, y - 10.0, 13.0), (8, y - 12.0, 15.4), (8, y - 13.0, 18.2)):
            q = p.barra(q, nxt, 1.15, 'rubber_hose')
    else:
        q = (8, y - 5.2, 13.2)
        for nxt in ((8, y - 8.2, 13.6), (8, y - 8.6, 16.4)):
            q = p.barra(q, nxt, 0.8, 'iron_dark')

    # ---- extras por tier
    if 'placas' in ex:
        for s in (-1, 1):
            p.rbox((8 + s * 3.4, y + 3.6, 12.0), (1.4, 2.6, 3.4), 'plate_acc2', r=0.4)
            p.rbox((8 + s * 3.4, y - 3.6, 17.6), (1.4, 2.6, 3.4), 'plate_acc2', r=0.4)
    if 'rejilla' in ex:
        for s in (-1, 1):
            p.rbox((8 + s * 4.1, y + 3.2, 12.4), (1.2, 2.6, 3.6), 'iron_dark', r=0.3)
            for dz in (-1.1, 0, 1.1):
                p.cen((8 + s * 4.75, y + 3.2, 12.4 + dz), (0.3, 1.9, 0.55), 'core_vent', glow=12)
    if 'luces' in ex:
        for s in (-1, 1):
            p.cen((8 + s * 3.6, y + 3.4, 18.0), (1.0, 1.0, 1.6), 'core_vent', glow=13)
    if 'vetas' in ex:
        for (dx, dy, dz, h) in ((-5.0, 2.0, 11.6, 3.0), (5.0, -1.8, 18.0, 3.4), (2.0, 5.15, 11.0, 0.6), (-2.2, -5.1, 13.5, 0.6)):
            sx = 0.3 if abs(dx) > 4 else 2.6
            sy = h if abs(dx) > 4 else 0.3
            p.cen((8 + dx, y + dy, dz), (sx, sy, 0.5), 'core_vent', glow=12)
    if 'oro' in ex:
        for s in (-1, 1):
            p.cen((8 + s * 2.6, y + 5.15, 14.8), (0.6, 0.6, 7.2), 'gold_trim')
        for z in (9.6, 20.1):
            for (dx, dy) in ((3.9, 3.9), (-3.9, 3.9), (3.9, -3.9), (-3.9, -3.9)):
                p.cen((8 + dx, y + dy, z), (1.4, 1.4, 1.4), 'gold_trim', ('z', 45))
    if 'cristales' in ex:
        cr = [k for k in pal if k.startswith('crystal_') and k not in ('crystal_tip', 'crystal_spark', 'crystal_fuel')]
        for i, (dx, h, z, a) in enumerate(((0, 3.8, 13.6, 0), (-1.8, 2.8, 15.6, 22.5), (1.8, 2.6, 15.0, -22.5),
                                          (0.4, 2.2, 17.4, 22.5), (-1.2, 1.8, 11.8, -22.5))):
            col = cr[i % len(cr)]
            p.cen((8 + dx, y + 6.2 + h / 2, z), (1.1, h, 1.1), col, ('z', a), glow=11)
            p.cen((8 + dx, y + 6.2 + h - 0.3, z), (0.6, 0.6, 0.6), 'gem_hi', ('y', 45), glow=13)
        if len(cr) > 1:
            for s in (-1, 1):
                p.cen((8 + s * 5.0, y + 4.2, 11.2), (0.9, 2.0, 0.9), cr[1], ('z', -s * 22.5), glow=11)
                p.cen((8 + s * 5.0, y - 4.2, 18.6), (0.9, 1.8, 0.9), cr[-1], ('z', s * 22.5), glow=11)
    if 'aro' in ex:
        p.octo((8, y, 6.1), 4.9, 0.35, 'z', 'gem_hi', glow=13, lados=8)
    if 'chispas' in ex:
        for (x, yy, z, s) in ((2.0, y + 7.6, 4.0, 0.7), (13.6, y + 5.4, 0.5, 0.6), (3.2, y - 4.8, -2.5, 0.55),
                              (14.0, y - 2.6, 9.0, 0.6), (8.0, y + 9.0, 18.0, 0.7), (1.8, y + 2.0, 22.0, 0.5)):
            p.cen((x, yy, z), (s, s * 2.2, s), 'crystal_spark', glow=15)
            p.cen((x, yy, z), (s * 2.2, s, s), 'crystal_spark', glow=15)

    p.agarre = (8, gc[1] + 0.9, gc[2] - 0.35)
    _poses(p)
    return p


# ============================================================================================= motosierras
MOTOSIERRAS = {
    'motosierra_basica': dict(nombre='Motosierra Basica', broca='#aeb6c2', gema='#d8e0ea', cuerpo='#7a8290',
                              acento='#5a606c', atras='#8a3a32', teeth='#7a808c', luz='#c8d0da', extra=set()),
    'motosierra_avanzada': dict(nombre='Motosierra Avanzada', broca='#b8c0cc', gema='#7ff4ff', cuerpo='#2a9cae',
                                acento='#1f6e7c', teeth='#8a909c', luz='#9ff6ff', extra={'placas'}),
    'motosierra_industrial': dict(nombre='Motosierra Industrial', broca='#b0b8c4', gema='#ffe04a', cuerpo='#3f8f3a',
                                  acento='#2a5e28', teeth='#868c98', luz='#ffe04a', extra={'placas', 'escape2'}),
    'motosierra_infernal': dict(nombre='Motosierra Infernal', broca='#8a8f9c', gema='#ff7a1a', cuerpo='#3a3236',
                                acento='#d05a14', oscuro='#1c1618', teeth='#ff7a1a', teeth_anim='flicker',
                                luz='#ff6a1a', luz_anim='flicker', extra={'fuego'}),
    'motosierra_astral': dict(nombre='Motosierra Astral', broca='#b8c4e0', gema='#6ff0ff', cuerpo='#6a3ad0',
                              acento='#4a22a0', teeth='#6ff0ff', teeth_anim='pulse', luz='#6ff0ff',
                              cristales={'a': '#a45cff', 'b': '#d9b0ff'}, extra={'cristales', 'gema'}),
}


def motosierra(iid, c):
    import math
    pal = _paleta(c)
    pal['steel_bar'] = (hx(c['broca']), 's')
    pal['prism_bar'] = (aclarar(hx(c['broca']), 0.35), 's')
    if 'teeth_chain' not in pal:
        pal['teeth_chain'] = (hx('#7a808c'), 'flow')
    pal['plate_back'] = (hx(c.get('atras') or c.get('acento', '#3a4252')), 's')
    pal['teeth_tooth'] = (aclarar(pal['teeth_chain'][0], 0.25), pal['teeth_chain'][1] if c.get('teeth_anim') else 's')
    ex = c.get('extra', set())
    glow_d = 12 if c.get('teeth_anim') else 0
    p = Pieza(iid, c['nombre'], pal, tex_dir='item/herramientas3d')
    y = 10.6

    # ---- espada (barra) con ranura, vetas y nariz redondeada
    p.cen((8, y, -0.5), (1.3, 4.8, 21), 'steel_bar')
    p.cen((8, y, -11.6), (1.3, 3.4, 1.4), 'steel_bar')
    p.cen((8, y, -12.6), (1.3, 1.8, 0.8), 'steel_bar')
    p.cen((8, y, -1.0), (1.42, 0.7, 19), 'iron_dark')
    for z in (-8.5, -4.5, -0.5, 3.5):
        for s in (-1, 1):
            p.cen((8 + s * 0.7, y + 1.2, z), (0.12, 0.5, 2.6), 'prism_bar', ('x', 45))
            p.cen((8 + s * 0.7, y - 1.2, z + 1.6), (0.12, 0.5, 2.6), 'prism_bar', ('x', 45))
    p.octo((8, y, -11.3), 1.3, 1.5, 'x', 'steel_hi', lados=8)                  # pinon de la punta
    p.cen((8, y, -11.3), (1.6, 0.6, 0.6), 'silver_rivet')
    for z in (5.4, 7.2):                                                       # remaches de la raiz y agujero de aceite
        for sx in (-1, 1):
            p.cen((8 + sx * 0.7, y + 1.1, z), (0.2, 0.8, 0.8), 'silver_rivet')
    p.cen((8, y - 1.2, 6.3), (1.45, 0.6, 0.6), 'iron_dark')
    # eslabones a los costados de la cadena (textura rayada que corre)
    for sx in (-1, 1):
        for dy in (2.55, -2.55):
            p.cen((8 + sx * 0.68, y + dy, -1.0), (0.12, 0.75, 22.4), 'teeth_chain', glow=glow_d)
    # ---- cadena (textura que corre) y dientes
    p.cen((8, y + 2.65, -1.0), (0.95, 0.5, 22.4), 'teeth_chain', glow=glow_d)
    p.cen((8, y - 2.65, -1.0), (0.95, 0.5, 22.4), 'teeth_chain', glow=glow_d)
    p.cen((8, y, -13.25), (0.95, 3.2, 0.5), 'teeth_chain', glow=glow_d)
    for z in range(-11, 9, 2):
        p.cen((8, y + 3.1, z), (0.85, 0.8, 1.35), 'teeth_tooth', ('x', 22.5), glow_d)
        p.cen((8, y - 3.1, z + 1), (0.85, 0.8, 1.35), 'teeth_tooth', ('x', -22.5), glow_d)
        p.cen((8 + (0.25 if z % 4 else -0.25), y + 3.45, z - 0.3), (0.45, 0.35, 0.9), 'steel_hi')   # diente en L
        p.cen((8 + (0.25 if z % 4 else -0.25), y - 3.45, z + 0.7), (0.45, 0.35, 0.9), 'steel_hi')
    for (dy, dz, a) in ((2.4, -12.9, 45), (-2.4, -12.9, -45), (0, -13.7, 0)):
        p.cen((8, y + dy, dz), (0.85, 0.8, 1.1), 'teeth_tooth', ('x', a) if a else None, glow_d)

    # ---- motor
    p.rbox((8, y + 0.2, 15.0), (8.6, 11.0, 12.0), 'steel_body', r=2.0)
    p.rbox((8, y + 5.9, 15.0), (6.0, 0.8, 9.0), 'plate_acc', r=0.4, eje='y')
    for s in (-1, 1):
        x = 8 + s * 4.35
        p.rbox((x, y - 0.4, 15.8), (0.6, 7.4, 8.6), 'plate_acc', r=0.6, eje='x')
        if s < 0:   # el lado que se ve en el inventario: rejilla con luces (como el icono)
            p.rbox((x + s * 0.3, y - 0.4, 16.6), (0.3, 5.0, 4.4), 'iron_dark', r=0.4, eje='x')
            for dz in (-1.3, 0, 1.3):
                p.cen((x + s * 0.5, y - 0.4, 16.6 + dz), (0.2, 3.8, 0.7), 'core_vent', glow=13)
        else:       # tapa redonda del arranque con ranuras y el tirador
            p.octo((x + 0.35, y - 0.2, 16.4), 3.0, 0.5, 'x', 'plate_acc2')
            p.octo((x + 0.6, y - 0.2, 16.4), 1.1, 0.4, 'x', 'iron_dark', lados=8)
            p.cen((x + 0.62, y - 0.2, 16.4), (0.15, 4.4, 0.35), 'iron_dark')            # ranuras en estrella
            p.cen((x + 0.62, y - 0.2, 16.4), (0.15, 0.35, 4.4), 'iron_dark')
            p.cen((x + 0.62, y - 0.2, 16.4), (0.15, 4.0, 0.35), 'iron_dark', ('x', 45))
            p.cen((x + 0.62, y - 0.2, 16.4), (0.15, 0.35, 4.0), 'iron_dark', ('x', 45))
            p.cen((x + 0.9, y + 2.4, 18.6), (0.8, 1.0, 2.6), 'rubber_grip')
            p.cen((x + 0.7, y + 2.4, 17.2), (0.3, 0.3, 1.2), 'steel_hi')
            p.cen((x + 0.35, y - 3.6, 12.4), (0.3, 1.3, 2.6), 'crystal_fuel', glow=9)   # visor de nafta
        # puas de tronco adelante, abajo de la espada
        for dx in (1.6, 3.0):
            p.cen((8 + s * dx, y - 3.4, 8.7), (0.7, 1.3, 1.3), 'iron_dark', ('x', 45))
        # tapa del pinon (donde entra la espada)
        p.octo((8 + s * 4.6, y, 9.4), 3.1, 0.9, 'x', 'plate_disc')
        p.octo((8 + s * 5.15, y, 9.4), 1.5, 0.5, 'x', 'iron_dark')
        p.cen((8 + s * 5.5, y, 9.4), (0.4, 0.9, 0.9), 'silver_rivet')
        for (dy, dz) in ((2.2, 2.2), (-2.2, 2.2), (2.2, -2.2), (-2.2, -2.2)):
            p.cen((8 + s * 5.05, y + dy, 9.4 + dz), (0.4, 0.5, 0.5), 'silver_rivet')
    # guardamano adelante y asa arriba
    p.rbox((8, y + 7.6, 8.4), (7.4, 5.8, 0.9), 'iron_dark', r=0.8, eje='z')
    p.rbox((8, y + 7.4, 11.0), (2.0, 4.6, 1.8), 'iron_dark', r=0.5, eje='z')
    p.rbox((8, y + 7.4, 18.6), (2.0, 4.6, 1.8), 'iron_dark', r=0.5, eje='z')
    p.rbox((8, y + 9.6, 14.8), (2.2, 1.8, 9.4), 'rubber_grip', r=0.6, eje='z')
    for z in (12.4, 14.8, 17.2):
        p.cen((8, y + 9.6, z), (2.4, 2.0, 0.4), 'iron_dark')
    # tapa de nafta, tirador y escape
    p.octo((10.6, y + 5.9, 12.2), 1.0, 0.9, 'y', 'plate_acc2')
    # filtro de aire con tornillos, bujia y rejillas del escape
    for z in (12.6, 17.4):
        p.cen((6.0, y + 6.35, z), (0.6, 0.2, 0.6), 'silver_rivet')
    p.octo((5.8, y + 6.6, 19.6), 0.7, 1.4, 'y', 'rubber_grip', lados=8)
    p.cen((5.8, y + 7.4, 19.6), (0.5, 0.4, 0.5), 'steel_hi')
    for dz in (-0.7, 0.0, 0.7):
        p.cen((12.15, y - 3.6, 21.6 + dz), (0.15, 1.2, 0.3), 'steel_bitcore')
    # soportes del guardamano
    for sx in (-1, 1):
        p.cen((8 + sx * 3.4, y + 5.4, 9.0), (0.6, 2.2, 1.4), 'iron_dark')
    # ---- lo que se ve en la mano (1ra persona: costado -X, atras y arriba)
    for (dx, dy) in ((-3.0, 3.6), (3.0, 3.6), (-3.0, -2.6), (3.0, -2.6)):                  # tornillos de la tapa de atras
        p.cen((8 + dx, y + 0.6 + dy, 22.15), (0.55, 0.55, 0.25), 'silver_rivet', ('z', 45))
    p.cen((8, y - 1.8, 22.2), (2.6, 1.2, 0.3), 'iron_dark')                                 # interruptor
    p.cen((8.5, y - 1.8, 22.4), (0.8, 0.8, 0.35), 'core_needle')
    for k in range(3):                                                                     # barra de nafta
        p.cen((6.4 + k * 1.0, y + 3.6, 22.2), (0.8, 0.5, 0.25), 'crystal_fuel', glow=10)
    p.octo((6.2, y + 6.6, 17.2), 0.6, 0.9, 'y', 'core_needle', lados=8)                     # perilla del cebador
    p.octo((3.45, y - 3.2, 10.4), 0.9, 0.5, 'x', 'plate_acc2', lados=8)                     # tapa del aceite de cadena
    p.cen((3.15, y - 3.2, 10.4), (0.2, 0.3, 1.2), 'iron_dark')
    for k in range(4):                                                                     # franja de advertencia
        p.cen((3.6, y + 3.6, 11.2 + k * 1.1), (0.2, 1.0, 0.55), 'core_vent' if k % 2 else 'iron_dark', glow=10 if k % 2 else 0)
    for z in (11.6, 20.0):                                                                 # tornillos del costado
        for dy in (-3.4, 3.0):
            p.cen((3.25, y + dy, z), (0.2, 0.45, 0.45), 'silver_rivet')
    p.rbox((11.2, y - 3.6, 21.6), (1.8, 1.8, 2.4), 'iron_dark', r=0.4, eje='z')
    if 'escape2' in ex:
        p.rbox((4.8, y - 3.6, 21.6), (1.8, 1.8, 2.4), 'iron_dark', r=0.4, eje='z')
    # tapa de atras con luces
    p.rbox((8, y + 0.6, 21.4), (7.6, 8.0, 1.4), 'plate_back', r=1.0, eje='z')
    for dx in (-1.8, 0, 1.8):
        p.cen((8 + dx, y + 1.4, 22.2), (0.8, 2.8, 0.3), 'core_vent', glow=12)

    # ---- mango de pistola atras
    gc = (8, y - 7.2, 19.4)
    rot = ('x', -22.5, gc)
    p.box((8 - 1.7, gc[1] - 4.4, gc[2] - 2.0), (8 + 1.7, gc[1] + 4.4, gc[2] + 2.0), 'wood_grip', rot)
    for t in (-2.5, -0.6, 1.3, 3.2):
        p.box((8 - 1.9, gc[1] + t - 0.35, gc[2] - 2.2), (8 + 1.9, gc[1] + t + 0.35, gc[2] + 2.2), 'wrap_grip', rot)
    for t in (1.9, -1.6):
        for s in (-1, 1):
            p.box((8 + s * 1.7 - 0.25, gc[1] + t - 0.45, gc[2] - 0.45), (8 + s * 1.7 + 0.25, gc[1] + t + 0.45, gc[2] + 0.45),
                  'silver_rivet', rot)
    p.box((8 - 1.95, gc[1] - 5.2, gc[2] - 2.3), (8 + 1.95, gc[1] - 4.2, gc[2] + 2.3), 'iron_dark', rot)
    p.cen((8, y - 6.0, 15.4), (0.9, 2.2, 0.8), 'plate_acc2', ('x', 22.5))
    q = (8, y - 5.0, 13.2)
    for nxt in ((8, y - 8.0, 13.6), (8, y - 8.6, 16.2)):
        q = p.barra(q, nxt, 0.8, 'iron_dark')

    # ---- extras por tier
    if 'placas' in ex:
        for s in (-1, 1):
            p.rbox((8 + s * 3.9, y + 4.0, 12.2), (1.2, 2.4, 3.6), 'plate_acc2', r=0.4)
    if 'fuego' in ex:
        for (x, z, h) in ((6.2, 13.0, 2.4), (8.0, 15.4, 3.4), (9.8, 17.6, 2.2), (7.2, 18.8, 1.6)):
            p.cen((x, y + 6.6 + h / 2, z), (0.9, h, 0.9), 'core_vent', ('y', 45), 15)
        for s in (-1, 1):
            p.cen((8 + s * 4.75, y + 3.6, 12.0), (0.25, 0.8, 3.0), 'core_vent', glow=14)
    if 'cristales' in ex:
        cr = [k for k in pal if k.startswith('crystal_') and k not in ('crystal_tip', 'crystal_fuel')]
        for i, (dx, h, z, a) in enumerate(((0.0, 3.6, 19.6, 0), (-1.6, 2.6, 20.6, 22.5), (1.6, 2.8, 20.2, -22.5),
                                          (0.6, 2.0, 21.4, 22.5))):
            p.cen((8 + dx, y + 4.8 + h / 2, z), (1.1, h, 1.1), cr[i % len(cr)], ('z', a), 11)
    if 'gema' in ex:
        for s in (-1, 1):
            p.gema((8 + s * 5.55, y, 9.4), 1.6, 'gem_core', eje='x', glow=15, largo=0.5)

    p.agarre = (8, gc[1] + 0.8, gc[2] - 0.3)
    _poses(p)
    return p


def _poses(p):
    p.poses = {
        'thirdperson_righthand': p.pose(MANO3['rot'], MANO3['destino'], MANO3['escala']),
        'firstperson_righthand': p.pose(MANO1['rot'], MANO1['destino'], MANO1['escala']),
    }
    p.gui_rot = [18, 118, 0]


def piezas():
    return [taladro(i, c) for i, c in TALADROS.items()] + [motosierra(i, c) for i, c in MOTOSIERRAS.items()]


# 23/11 (dueno): en el inventario (y en el piso o marcos) el icono plano de antes (iconos_19_11); 3D solo en la mano.
PLANO_EN = ('gui', 'ground', 'fixed')


def assets():
    import json
    out = {}
    for ruta, data in P.assets(piezas(), items_json=False).items():
        if ruta.startswith('assets/astral/models/item/') and ruta.endswith('.json'):
            ruta = ruta[:-5] + '_3d.json'
        out[ruta] = data
    for p in piezas():
        out[f'assets/astral/items/{p.iid}.json'] = json.dumps({'model': {
            'type': 'minecraft:select', 'property': 'minecraft:display_context',
            'cases': [{'when': list(PLANO_EN), 'model': {'type': 'minecraft:model', 'model': f'astral:item/{p.iid}'}}],
            'fallback': {'type': 'minecraft:model', 'model': f'astral:item/{p.iid}_3d'}}}, indent=1).encode()
    return out


def check():
    return [x for p in piezas() for x in p.check()]


if __name__ == '__main__':
    for x in check():
        print('AVISO:', x)
    ps = piezas()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'build', 'previews')
    P.hoja(ps[:9], os.path.join(out, 'taladros_3d.png'), 'Taladros 3D (22/11): 3/4, costado, inventario, mano y 1ra persona')
    P.hoja(ps[9:], os.path.join(out, 'motosierras_3d.png'), 'Motosierras 3D (22/11)')
    print({p.iid: len(p.els) for p in ps})
