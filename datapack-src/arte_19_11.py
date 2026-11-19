# -*- coding: utf-8 -*-
"""Arte del 19/11/2026 recortado de las referencias del dueno (generadas con Codex) a piezas del pack.

Referencias (locales, no van al repo): .local/gemini/refs-19-11/{cavernas,portales,mareas,banco,efectos,forja}.png
Salida (propia, va al repo): datapack-src/pack-source/arte-19-11/<seccion>/<pieza>.png
Uso: python arte_19_11.py [cavernas|mareas|...]   (sin argumento: todas)
"""
import sys
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
REFS = HERE.parent / '.local/gemini/refs-19-11'
OUT = HERE / 'pack-source/arte-19-11'


def ref(nombre):
    return Image.open(REFS / f'{nombre}.png').convert('RGB')


def sin_fondo(im, box, tol=26):
    """Recorta box y vuelve transparente el fondo del panel conectado al borde (relleno por inundacion)."""
    a = np.asarray(im.crop(box).convert('RGB')).astype(int)
    h, w, _ = a.shape
    bg = np.median(np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]]), axis=0)
    close = np.abs(a - bg).sum(2) < tol * 3
    seen = np.zeros((h, w), bool)
    q = deque([(0, x) for x in range(w)] + [(h - 1, x) for x in range(w)] + [(y, 0) for y in range(h)] + [(y, w - 1) for y in range(h)])
    while q:
        y, x = q.popleft()
        if 0 <= y < h and 0 <= x < w and not seen[y, x] and close[y, x]:
            seen[y, x] = True
            q += [(y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)]
    o = Image.fromarray(np.dstack([a, np.where(seen, 0, 255)]).astype(np.uint8))
    return o.crop(o.getbbox())


def cuadrado(im, lado):
    """Centra en un cuadrado transparente y achica a lado x lado."""
    n = max(im.size)
    sq = Image.new('RGBA', (n, n))
    sq.alpha_composite(im.convert('RGBA'), ((n - im.width) // 2, (n - im.height) // 2))
    return sq.resize((lado, lado), Image.Resampling.LANCZOS)


def guardar(seccion, nombre, im):
    p = OUT / seccion / f'{nombre}.png'
    p.parent.mkdir(parents=True, exist_ok=True)
    im.save(p)
    return p


# ------------------------------------------------------------------ Cavernas
TIPOS_COL = ['rubi', 'zafiro', 'jade', 'topacio', 'amatista', 'opalo', 'onix']   # orden de la referencia
VETA_COLS = [(132, 208), (219, 292), (304, 377), (389, 461), (472, 546), (557, 630), (642, 714)]
VETA_FILAS = {'': (162, 236), '_honda': (249, 323)}


def cavernas():
    im = ref('cavernas')
    out = []
    for t, (x0, x1) in zip(TIPOS_COL, VETA_COLS):
        for suf, (y0, y1) in VETA_FILAS.items():
            out.append(guardar('cavernas', f'veta_{t}{suf}', im.crop((x0 + 3, y0 + 3, x1 - 3, y1 - 3)).resize((32, 32), Image.Resampling.LANCZOS)))
    out.append(guardar('cavernas', 'veta_cristal_caverna', im.crop((747, 188, 838, 279)).resize((32, 32), Image.Resampling.LANCZOS)))
    out.append(guardar('cavernas', 'veta_geoda_estelar', im.crop((863, 188, 952, 279)).resize((32, 32), Image.Resampling.LANCZOS)))
    for n, b in (('cristal_caverna', (1022, 132, 1172, 276)), ('geoda_estelar', (1180, 132, 1330, 276)),
                 ('polvo_cristal', (1355, 155, 1505, 272))):
        out.append(guardar('cavernas', n, cuadrado(sin_fondo(im, b), 64)))
    return out


# ------------------------------------------------------------------ Mareas (Oceano Astral): perla y coral
def _cara(im, lado, x0, xc, x1, y_lado, y_centro, y_bot, y_lado_bot, size=32):
    """Aplana una cara lateral del cubo isometrico de la referencia a una textura cuadrada."""
    if lado == 'izq':   # arriba-izq, abajo-izq, abajo-der, arriba-der
        quad = (x0 + 4, y_lado + 3, x0 + 4, y_lado_bot - 3, xc - 3, y_bot - 4, xc - 3, y_centro + 4)
    else:
        quad = (xc + 3, y_centro + 4, xc + 3, y_bot - 4, x1 - 4, y_lado_bot - 3, x1 - 4, y_lado + 3)
    return im.transform((256, 256), Image.Transform.QUAD, quad, Image.Resampling.BICUBIC).resize((size, size), Image.Resampling.LANCZOS)


def mareas():
    im = ref('mareas')
    return [guardar('mareas', 'coral_astral_ore', _cara(im, 'izq', 695, 896, 1097, 355, 457, 699, 597)),
            guardar('mareas', 'perla_abisal_ore', _cara(im, 'der', 695, 897, 1099, 874, 976, 1231, 1129)),
            guardar('mareas', 'coral_astral', cuadrado(sin_fondo(im, (110, 300, 540, 690), tol=30), 64)),
            guardar('mareas', 'perla_abisal', cuadrado(sin_fondo(im, (130, 840, 520, 1190), tol=30), 64))]


# ------------------------------------------------------------------ Portales: tarjetas Nether, End, Cavernas, Vacio
TARJETAS = {'nether': (160, 289, 352, 576), 'end': (362, 289, 552, 576), 'cavernas': (567, 289, 756, 576),
            'vacio': (789, 289, 947, 533)}


def portales():
    """pack-source/ref/portales-cards.png: las 4 pinturas lado a lado (travel_ui.illustration corta en 4)."""
    im = ref('portales')
    hoja = Image.new('RGBA', (4 * 180, 280))
    for i, box in enumerate(TARJETAS.values()):
        hoja.alpha_composite(im.crop(box).convert('RGBA').resize((180, 280), Image.Resampling.LANCZOS), (i * 180, 0))
    dest = HERE / 'pack-source/ref/portales-cards.png'
    hoja.save(dest)
    return [dest]


SECCIONES = {'cavernas': cavernas, 'mareas': mareas, 'portales': portales}

if __name__ == '__main__':
    for nombre in (sys.argv[1:] or list(SECCIONES)):
        print(nombre, len(SECCIONES[nombre]()), 'piezas ->', OUT / nombre)
