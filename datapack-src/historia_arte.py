# -*- coding: utf-8 -*-
"""Arte de los items del Modo Historia (22/11): recortado de la lamina del dueno.

pack-source/art/ref_22_11/historia.png -> texturas astral:item/historia/<id>. Se aplica al final de
build_pack.py. La Gomera tiene tres dibujos (quieta, media carga y carga maxima) y cambia sola mientras
se mantiene el clic derecho, como el arco. La piedra que tira es gomera_piedra (la usa AstralGomera).

Uso: python historia_arte.py   -> build/previews/historia_22_11.png (para revisar los recortes)
"""
import json
from pathlib import Path

from PIL import Image, ImageDraw

import iconos_19_11 as base

HERE = Path(__file__).resolve().parent
SHEET = 'historia'
base.REF_HISTORIA = HERE / 'pack-source' / 'art' / 'ref_22_11'

# Las tres gomeras usan cajas del mismo ancho, alineadas en el mango: asi no salta al estirarse.
GOMERA_W = 330
GOMERA = {
    'gomera': (98, 90),
    'gomera_media': (420, 90),
    'gomera_maxima': (782, 90),
}
GOMERA_H = 260
ICONS = {
    'gomera_piedra': (1230, 200, 1340, 290),
    'amuleto_espantapajaros': (55, 395, 335, 675),
    'caparazon_cangrejo': (380, 440, 750, 665),
    'brebaje_chaman': (820, 405, 1040, 675),
    'farol_capataz': (1170, 395, 1385, 680),
    'venda_momia': (55, 755, 360, 1005),
    'colmillo_yeti': (470, 735, 670, 1000),
    'martillo_golem': (795, 720, 1055, 1005),
    'eco_estrella': (1170, 750, 1395, 990),
}
GOMERA_SIZE = 48
ICON_SIZE = 32


def _cut(box):
    """Mismo recorte que las laminas del 19/11 (fondo conectado al borde = transparente)."""
    old = base.REF
    base.REF = base.REF_HISTORIA
    # Huecos de fondo encerrados (entre la goma y la gomera, el asa del farol): tambien transparentes.
    base.HOLES.add(SHEET)
    try:
        return base.cut(SHEET, box)
    finally:
        base.REF = old
        base.HOLES.discard(SHEET)


def _shrink(big, size, scale=None, anchor=None):
    """Achica sin halo (promedio solo de lo opaco) y alfa recortado, como iconos_19_11.sprite."""
    import numpy as np
    scale = scale or (size - 2) / max(big.size)
    w, h = max(1, round(big.width * scale)), max(1, round(big.height * scale))
    arr = np.asarray(big).astype(float)
    a = arr[..., 3:4] / 255
    prem = Image.fromarray(np.dstack([arr[..., :3] * a, a[..., 0] * 255]).astype(np.uint8), 'RGBA')
    small = np.asarray(prem.resize((w, h), Image.Resampling.BOX)).astype(float)
    alpha = small[..., 3] / 255
    color = np.clip(np.where(alpha[..., None] > 0, small[..., :3] / np.maximum(alpha[..., None], 1e-6), 0), 0, 255)
    solid = alpha >= 0.5
    rgba = np.dstack([color, solid * 255]).astype(np.uint8)
    rgba[~solid] = 0
    tile = Image.new('RGBA', (size, size))
    tile.paste(Image.fromarray(rgba, 'RGBA'), anchor or ((size - w) // 2, (size - h) // 2))
    return tile


def sprite(iid):
    if iid in GOMERA:
        x0, y0 = GOMERA[iid]
        big = _cut((x0, y0, x0 + GOMERA_W, y0 + GOMERA_H))
        # Escala comun a las tres: el ancho de la caja entra justo; el mango queda abajo a la izquierda.
        scale = (GOMERA_SIZE - 2) / GOMERA_W
        # Posicion: lo recortado empieza donde empieza el dibujo dentro de la caja (getbbox).
        full = Image.open(base.REF_HISTORIA / f'{SHEET}.png').convert('RGB').crop((x0, y0, x0 + GOMERA_W, y0 + GOMERA_H))
        import numpy as np
        mask = ~base._bg_mask(np.asarray(full))
        ys, xs = np.nonzero(base._drop_specks(mask, 40))
        left, top = xs.min(), ys.min()
        h = round(big.height * scale)
        return _shrink(big, GOMERA_SIZE, scale, (1 + round(left * scale), GOMERA_SIZE - 1 - h))
    return _shrink(_cut(ICONS[iid]), ICON_SIZE)


def _png(im):
    import io
    b = io.BytesIO()
    im.save(b, 'PNG')
    return b.getvalue()


def _model(iid):
    return {'parent': 'minecraft:item/generated', 'textures': {'layer0': f'astral:item/historia/{iid}'}}


def assets():
    files = {}
    for iid in list(GOMERA) + list(ICONS):
        files[f'assets/astral/textures/item/historia/{iid}.png'] = _png(sprite(iid))
        files[f'assets/astral/models/item/{iid}.json'] = json.dumps(_model(iid), indent=1).encode()
    for iid in ICONS:
        files[f'assets/astral/items/{iid}.json'] = json.dumps(
            {'model': {'type': 'minecraft:model', 'model': f'astral:item/{iid}'}}, indent=1).encode()
    # Gomera: se estira mientras se usa (use_duration en segundos: 20 ticks = 1 = carga completa).
    files['assets/astral/items/gomera.json'] = json.dumps({'model': {
        'type': 'minecraft:condition', 'property': 'minecraft:using_item',
        'on_false': {'type': 'minecraft:model', 'model': 'astral:item/gomera'},
        'on_true': {'type': 'minecraft:range_dispatch', 'property': 'minecraft:use_duration', 'scale': 0.05,
                    'fallback': {'type': 'minecraft:model', 'model': 'astral:item/gomera_media'},
                    'entries': [{'threshold': 0.9, 'model': {'type': 'minecraft:model', 'model': 'astral:item/gomera_maxima'}}]}},
    }, indent=1).encode()
    return files


def preview():
    ids = list(GOMERA) + list(ICONS)
    cell = 170
    cols = 6
    rows = (len(ids) + cols - 1) // cols
    out = Image.new('RGB', (cols * cell, rows * cell + 30), '#191b28')
    d = ImageDraw.Draw(out)
    d.text((10, 8), 'Items de historia: grande = ampliado; chico abajo a la derecha = tamano real', fill='#e3c68a')
    for n, iid in enumerate(ids):
        x, y = (n % cols) * cell, (n // cols) * cell + 30
        im = sprite(iid)
        big = im.resize((144, 144), Image.Resampling.NEAREST)
        d.rectangle((x + 2, y + 2, x + cell - 3, y + cell - 3), fill='#8b8b8b' if n % 2 else '#3a3a3a', outline='#575266')
        out.paste(big, (x + 13, y + 4), big)
        out.paste(im, (x + cell - im.width - 6, y + cell - im.height - 6), im)
        d.text((x + 6, y + cell - 16), iid[:20], fill='#ffffff')
    path = HERE.parent / 'build' / 'previews' / 'historia_22_11.png'
    path.parent.mkdir(parents=True, exist_ok=True)
    out.save(path)
    im = Image.open(base.REF_HISTORIA / f'{SHEET}.png').convert('RGB')
    dd = ImageDraw.Draw(im)
    for iid, (x0, y0) in GOMERA.items():
        dd.rectangle((x0, y0, x0 + GOMERA_W, y0 + GOMERA_H), outline='#ff3060', width=3)
    for box in ICONS.values():
        dd.rectangle(box, outline='#30ff60', width=3)
    im.save(path.parent / 'historia_22_11_cajas.png')
    print(path)


if __name__ == '__main__':
    preview()
