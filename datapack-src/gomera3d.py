# -*- coding: utf-8 -*-
"""Gomera en 3D (pedido del dueno 22/11/2026). Reemplaza los dibujos planos de historia_arte.py.

Horquilla de madera tallada (mango con venda de cuero y atadura de soga, brazos con nudos), dos gomas que salen
de las puntas y la bolsita de cuero con la piedra. Tres modelos, como el arco:
- gomera: quieta (la goma cuelga entre los brazos);
- gomera_media: tensando (la bolsita vuelve hacia el jugador);
- gomera_maxima: tensada a fondo (gomas estiradas al maximo, la piedra brilla un poco).
items/gomera.json elige el modelo con using_item + use_duration (igual que historia_arte).

Uso: python gomera3d.py   -> build/previews/gomera_3d.png
"""
import json
import os

import piezas3d as P
from piezas3d import Pieza, hx

PAL = {
    'wood_fork': (hx('#8a5a32'), 's'),
    'wood_dark': (hx('#5e3a1e'), 's'),
    'bark_knot': (hx('#4a2c16'), 's'),
    'leather_wrap': (hx('#6a3a22'), 's'),
    'leather_light': (hx('#9a6038'), 's'),
    'cord_rope': (hx('#d8c08a'), 's'),
    'rubber_band': (hx('#d6a85a'), 's'),
    'leather_pouch': (hx('#7a4a2a'), 's'),
    'stone_rock': (hx('#8e8a96'), 's'),
    'stone_hi': (hx('#c0bcc8'), 's'),
    'iron_ring': (hx('#6a6e78'), 's'),
    'core_glint': (hx('#ffe6a0'), 'pulse'),
}

# Donde queda la bolsita en cada estado (z = cuanto vuelve hacia el jugador)
ESTADOS = {
    'gomera': {'bolsa': (8, 11.2, 9.0), 'nombre': 'Gomera'},
    'gomera_media': {'bolsa': (8, 13.4, 14.5), 'nombre': 'Gomera (tensando)'},
    'gomera_maxima': {'bolsa': (8, 13.6, 19.5), 'nombre': 'Gomera (tensada)'},
}

AGARRE = (8, 1.6, 8)
PUNTAS = ((3.4, 15.2, 8), (12.6, 15.2, 8))


def horquilla(p):
    # mango: madera con venda de cuero, atadura de soga y pomo
    p.rbox((8, 2.2, 8), (2.6, 9.6, 2.6), 'wood_fork', r=0.6, eje='y')
    for y in (-0.8, 0.6, 2.0, 3.4):
        p.cen((8, y, 8), (2.9, 0.75, 2.9), 'leather_wrap' if y != 2.0 else 'leather_light')
    p.rbox((8, -2.8, 8), (3.0, 1.2, 3.0), 'wood_dark', r=0.5)
    p.cen((8, -3.5, 8), (1.6, 0.6, 1.6), 'bark_knot')
    # union: nudo grueso + soga cruzada
    p.rbox((8, 6.6, 8), (3.4, 2.8, 2.8), 'wood_fork', r=0.8)
    for y in (5.6, 6.4, 7.2):
        p.cen((8, y, 8), (3.6, 0.45, 3.0), 'cord_rope')
    p.cen((8, 6.4, 8), (0.5, 2.4, 3.1), 'cord_rope', ('z', 45))
    # brazos: suben abiertos y despues casi rectos, con nudos y puntas con muesca
    for s in (-1, 1):
        a = (8 + s * 1.0, 7.4, 8)
        b = (8 + s * 3.6, 11.6, 8)
        c = (8 + s * 4.6, 15.4, 8)
        p.barra(a, b, 2.3, 'wood_fork', plano='xy')
        p.barra(b, c, 2.1, 'wood_fork', plano='xy')
        p.cen((8 + s * 3.1, 10.4, 8), (1.2, 1.2, 2.5), 'bark_knot', ('z', 45))
        p.cen((8 + s * 4.6, 15.9, 8), (2.3, 1.0, 2.3), 'wood_dark')
        # venda de cuero en la punta y anillo de hierro donde se ata la goma
        p.cen((8 + s * 4.5, 14.2, 8), (2.5, 1.4, 2.5), 'leather_light')
        p.cen((8 + s * 4.5, 14.2, 9.4), (1.0, 1.0, 0.6), 'iron_ring')
        # vetas de la madera
        p.cen((8 + s * 2.5, 9.2, 6.85), (0.3, 1.6, 0.2), 'wood_dark', ('z', s * 22.5))


def gomas(p, bolsa):
    bx, by, bz = bolsa
    for s in (-1, 1):
        tip = (8 + s * 4.5, 14.2, 9.6)
        to = (bx + s * 1.3, by, bz)
        dz = to[2] - tip[2]
        if dz > 3:
            # estirada hacia atras: barra en el plano xz (y casi igual)
            p.barra((tip[0], 14.0, tip[2]), (to[0], 14.0, to[2]), 0.55, 'rubber_band', plano='xz')
            if abs(by - 14.0) > 0.2:
                p.cen((to[0], (14.0 + by) / 2, to[2]), (0.55, abs(by - 14.0) + 0.5, 0.55), 'rubber_band')
        else:
            # floja: cuelga de la punta a la bolsita (plano xy)
            mid = ((tip[0] + to[0]) / 2, to[1] + 0.6, tip[2] + 0.2)
            p.barra((tip[0], tip[1], tip[2]), mid, 0.55, 'rubber_band', plano='xy')
            p.barra(mid, (to[0], to[1], tip[2]), 0.55, 'rubber_band', plano='xy')
    # bolsita de cuero con la piedra
    p.rbox((bx, by, bz), (3.2, 2.4, 1.6), 'leather_pouch', r=0.5)
    p.cen((bx, by, bz), (3.6, 0.6, 1.2), 'leather_light')
    p.octo((bx, by + 0.2, bz - 0.9), 1.15, 1.4, 'z', 'stone_rock', lados=8)
    p.cen((bx - 0.35, by + 0.7, bz - 1.4), (0.6, 0.5, 0.4), 'stone_hi')


def gomera(iid):
    e = ESTADOS[iid]
    p = Pieza(iid, e['nombre'], PAL, tex_dir='item/historia3d', tex_name='gomera')
    horquilla(p)
    gomas(p, e['bolsa'])
    if iid == 'gomera_maxima':
        p.cen((e['bolsa'][0], e['bolsa'][1] + 1.6, e['bolsa'][2] - 0.9), (0.4, 0.4, 0.4), 'core_glint', glow=12)
    p.agarre = AGARRE
    if iid == 'gomera':
        p.poses = {
            'thirdperson_righthand': p.pose([72, 0, 0], (0, -2.0, 2.4), 0.72),
            'firstperson_righthand': p.pose([6, 12, 0], (-1.0, 2.6, 0.0), 0.6),
        }
    else:
        # brazo levantado (pose de arco): +Y de la mano mira arriba y +Z hacia el hombro
        p.poses = {
            'thirdperson_righthand': p.pose([-8, 0, 0], (0, -2.0, 2.4), 0.72),
            'firstperson_righthand': p.pose([0, -12, 0], (-4.3, -1.6, 0.6), 0.5),
        }
    p.gui_rot = [12, -28, 0]
    return p


def piezas():
    return [gomera(i) for i in ESTADOS]


def assets():
    out = P.assets(piezas(), items_json=False)
    out['assets/astral/items/gomera.json'] = json.dumps({'model': {
        'type': 'minecraft:condition', 'property': 'minecraft:using_item',
        'on_false': {'type': 'minecraft:model', 'model': 'astral:item/gomera'},
        'on_true': {'type': 'minecraft:range_dispatch', 'property': 'minecraft:use_duration', 'scale': 0.05,
                    'fallback': {'type': 'minecraft:model', 'model': 'astral:item/gomera_media'},
                    'entries': [{'threshold': 0.9, 'model': {'type': 'minecraft:model', 'model': 'astral:item/gomera_maxima'}}]}},
    }, indent=1).encode()
    return out


def check():
    return [x for p in piezas() for x in p.check()]


if __name__ == '__main__':
    for x in check():
        print('AVISO:', x)
    ps = piezas()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'build', 'previews', 'gomera_3d.png')
    P.hoja(ps[:1], out.replace('.png', '_quieta.png'), 'Gomera 3D quieta')
    P.hoja(ps[1:], out, 'Gomera 3D tensando / tensada (brazo levantado, 1ra persona con la cuenta del arco)',
           uso='bow', brazo='arriba')
    print({p.iid: len(p.els) for p in ps})
