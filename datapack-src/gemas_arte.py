"""Recorta la hoja de gemas de Gemini (fondo magenta) en las 35 texturas 64x64 de gemas.py.

Hoja: .local/gemini/gemas/hoja_gemas.jpg (7 filas = gemas en el orden de gemas.TIPOS; 6 columnas: Cruda, otra cruda
que NO se usa, Pulida, Impecable, Perfecta, Estelar). Uso: python gemas_arte.py [hoja] [--columnas 0,2,3,4,5]
Salida: pack-source/assets/astral/textures/item/gemas/<tipo>_<calidad>.png (pisa las provisorias).
"""
import argparse
from pathlib import Path

import numpy as np
from PIL import Image

import gemas as G

ROOT = Path(__file__).resolve().parents[1]
HOJA = ROOT / '.local/gemini/gemas/hoja_gemas.jpg'
LADO = 64


def bandas(p, umbral=3):
    out, on = [], False
    for i, v in enumerate(p):
        if v > umbral and not on:
            s, on = i, True
        if v <= umbral and on:
            out.append((s, i)); on = False
    if on:
        out.append((s, len(p)))
    return out


def alfa(rgb):
    """Alfa por distancia al magenta (borde suave) y quita el tinte magenta de los bordes."""
    a = rgb.astype(float)
    d = np.sqrt((a[..., 0] - 255) ** 2 + a[..., 1] ** 2 + (a[..., 2] - 255) ** 2)
    al = np.clip((d - 90) / (170 - 90), 0, 1)
    # despill: en pixeles parcialmente magenta, bajar rojo y azul hacia el verde
    spill = np.clip(np.minimum(a[..., 0], a[..., 2]) - a[..., 1], 0, None) * (1 - al)
    a[..., 0] -= spill; a[..., 2] -= spill
    return np.dstack([np.clip(a, 0, 255), al * 255]).astype(np.uint8)


def recortar(hoja=HOJA, columnas=(0, 2, 3, 4, 5)):
    im = np.asarray(Image.open(hoja).convert('RGB'))
    rgba = alfa(im)
    m = rgba[..., 3] > 150
    filas = [b for b in bandas(m.sum(1)) if b[1] - b[0] > 60]
    cols = [b for b in bandas(m.sum(0)) if b[1] - b[0] > 60]
    assert len(filas) == len(G.TIPOS), f'filas: {len(filas)}'
    assert len(cols) > max(columnas), f'columnas: {len(cols)}'
    G.TEX.mkdir(parents=True, exist_ok=True)
    out = []
    for (y0, y1), t in zip(filas, G.TIPOS):
        for q, c in enumerate(columnas, 1):
            x0, x1 = cols[c]
            cel = Image.fromarray(rgba[y0:y1, x0:x1])
            cel = cel.crop(cel.getbbox())
            lado = int(max(cel.size) * 1.06)
            sq = Image.new('RGBA', (lado, lado))
            sq.alpha_composite(cel, ((lado - cel.width) // 2, (lado - cel.height) // 2))
            p = G.TEX / f'{t}_{q}.png'
            sq.resize((LADO, LADO), Image.Resampling.LANCZOS).save(p)
            out.append(p)
    return out


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('hoja', nargs='?', default=str(HOJA))
    ap.add_argument('--columnas', default='0,2,3,4,5')
    a = ap.parse_args()
    print(len(recortar(Path(a.hoja), tuple(int(x) for x in a.columnas.split(',')))), 'texturas ->', G.TEX)
