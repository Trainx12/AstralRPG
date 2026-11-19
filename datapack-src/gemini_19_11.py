# -*- coding: utf-8 -*-
"""Recorta las hojas de Gemini del 19/11 (fondo magenta) y pisa las piezas de pack-source/arte-19-11/ventanas.

Hojas: .local/gemini/refs-19-11/gemini/<hoja>.jpg (locales). Uso: python gemini_19_11.py <hoja> [...]
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

from gemas_arte import alfa
from gemini_recortes import piezas

HERE = Path(__file__).resolve().parent
HOJAS = HERE.parent / '.local/gemini/refs-19-11/gemini'
ART = HERE / 'pack-source/arte-19-11/ventanas'
# hoja: nombres en orden de lectura (filas de arriba a abajo, izquierda a derecha)
NOMBRES = {
    'forja_botones': ['forja_mejorar', 'forja_reparar', 'forja_gemas', 'forja_engarzar', 'forja_extraer', 'forja_forja',
                      'forja_atras', 'forja_cerrar'],
}


def recortar(hoja, nombres=None, destino=ART, minimo=2500, ultima_por_x=0):
    nombres = nombres or NOMBRES[hoja]
    im = Image.fromarray(alfa(np.asarray(Image.open(HOJAS / f'{hoja}.jpg').convert('RGB'))))
    cajas = piezas(im, minimo)
    assert len(cajas) == len(nombres), f'{hoja}: {len(cajas)} piezas, esperaba {len(nombres)}'
    if ultima_por_x:   # la ultima fila mezcla alturas: se ordena solo por x
        cajas = cajas[:-ultima_por_x] + sorted(cajas[-ultima_por_x:], key=lambda b: b[0])
    destino.mkdir(parents=True, exist_ok=True)
    out = []
    for n, b in zip(nombres, cajas):
        p = im.crop(b)
        p = p.crop(p.getbbox())
        p.save(destino / f'{n}.png')
        out.append(n)
    return out


def mareas():
    """Coral y perla (objeto 64x64) y sus menas (32x32) en pack-source/arte-19-11/mareas (las usa oceano_items)."""
    from arte_19_11 import cuadrado
    dest = HERE / 'pack-source/arte-19-11/mareas'
    tmp = HOJAS / 'tmp_mareas'
    nombres = ['coral_astral', 'coral_astral_ore', 'perla_abisal', 'perla_abisal_ore']
    recortar('mareas', nombres, tmp)
    for n in nombres:
        im = Image.open(tmp / f'{n}.png').convert('RGBA')
        (im.resize((32, 32), Image.Resampling.LANCZOS) if n.endswith('_ore') else cuadrado(im, 64)).save(dest / f'{n}.png')
    return nombres


def cavernas():
    """Vetas (32x32) e items (64x64) en pack-source/arte-19-11/cavernas. Fila 1 comun, fila 3 honda (la 2 se descarta)."""
    from arte_19_11 import cuadrado, TIPOS_COL
    dest = HERE / 'pack-source/arte-19-11/cavernas'
    tmp = HOJAS / 'tmp_cavernas'
    nombres = ([f'veta_{t}' for t in TIPOS_COL] + [f'descartar_{t}' for t in TIPOS_COL] + [f'veta_{t}_honda' for t in TIPOS_COL]
               + ['veta_cristal_caverna', 'veta_geoda_estelar', 'cristal_caverna', 'geoda_estelar', 'polvo_cristal'])
    recortar('cavernas', nombres, tmp, ultima_por_x=5)
    for n in nombres:
        if n.startswith('descartar'):
            continue
        im = Image.open(tmp / f'{n}.png').convert('RGBA')
        (im.resize((32, 32), Image.Resampling.LANCZOS) if n.startswith('veta_') else cuadrado(im, 64)).save(dest / f'{n}.png')
    return nombres


def por_filas(cajas, tamanos):
    """Agrupa por altura (centro y) en filas de los tamanos dados y ordena cada fila por x."""
    cajas = sorted(cajas, key=lambda b: (b[1] + b[3]) / 2)
    assert len(cajas) == sum(tamanos), f'{len(cajas)} piezas, esperaba {sum(tamanos)}'
    out, i = [], 0
    for n in tamanos:
        out += sorted(cajas[i:i + n], key=lambda b: b[0])
        i += n
    return out


def cajas_ordenadas(hoja, minimo=2500, grande=0):
    """(imagen sin magenta, cajas) con las 'grande' piezas mas grandes aparte y el resto por filas (y) y columnas (x)."""
    im = Image.fromarray(alfa(np.asarray(Image.open(HOJAS / f'{hoja}.jpg').convert('RGB'))))
    cajas = piezas(im, minimo)
    area = lambda b: (b[2] - b[0]) * (b[3] - b[1])
    grandes = sorted(cajas, key=area, reverse=True)[:grande]
    resto = [b for b in cajas if b not in grandes]
    alto = sum(b[3] - b[1] for b in resto) / max(1, len(resto))
    resto.sort(key=lambda b: (round((b[1] + b[3]) / 2 / (alto * 1.2)), b[0]))
    return im, resto, grandes


def guardar_cajas(im, cajas, nombres, destino=ART):
    assert len(cajas) == len(nombres), f'{len(cajas)} piezas, esperaba {len(nombres)}'
    for n, b in zip(nombres, cajas):
        p = im.crop(b)
        p.crop(p.getbbox()).save(destino / f'{n}.png')
    return nombres


def cavernas_ui():
    im, resto, grandes = cajas_ordenadas('cavernas_ui', grande=1)
    guardar_cajas(im, grandes, ['ilustracion'])
    return guardar_cajas(im, resto, ['cartel_comisiones', 'cartel_cavernas', 'badge_pendiente', 'badge_lista', 'badge_cobrada',
                                     'cobrar', 'entrar', 'volver', 'cristal_rojo', 'cristal_violeta', 'cristal_azul'])


def efectos():
    """Iconos de categoria, interruptores y tilde (la primera fila de la hoja salio encimada: no se usa)."""
    im = Image.fromarray(alfa(np.asarray(Image.open(HOJAS / 'efectos.jpg').convert('RGB'))))
    im = im.crop((0, int(im.height * 0.3), im.width, im.height))
    cajas = por_filas(piezas(im, 2500), (5, 2, 2))
    nombres = ['efectos_icono_armaduras', 'efectos_icono_armas', 'efectos_icono_bastones', 'efectos_icono_mascotas',
               'efectos_icono_jefes', 'efectos_on', 'efectos_off', 'descartar_off2', 'efectos_check']
    guardar_cajas(im, cajas, nombres)
    (ART / 'descartar_off2.png').unlink()
    return nombres


def banco_a():
    im = Image.fromarray(alfa(np.asarray(Image.open(HOJAS / 'banco_a.jpg').convert('RGB'))))
    cajas = por_filas(piezas(im, 2500), (3, 3, 4, 4))
    nombres = ['banco_cartel_banco', 'banco_cartel_depositar', 'banco_cartel_retirar', 'banco_cartel_mejorar',
               'banco_cartel_movimiento', 'banco_cartel_cuenta', 'banco_ilu_banco', 'banco_ilu_depositar', 'banco_ilu_retirar',
               'x1', 'banco_ilu_mejorar', 'banco_ilu_movimiento', 'x2', 'banco_ilu_cuenta']
    guardar_cajas(im, cajas, nombres)
    for x in ('x1', 'x2'):
        (ART / f'{x}.png').unlink()
    return nombres


ESPECIALES = {'banco_a': banco_a, 'mareas': mareas, 'cavernas': cavernas, 'cavernas_ui': cavernas_ui, 'efectos': efectos}

if __name__ == '__main__':
    for h in sys.argv[1:]:
        print(h, ESPECIALES[h]() if h in ESPECIALES else recortar(h))
