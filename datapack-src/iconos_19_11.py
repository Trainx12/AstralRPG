# -*- coding: utf-8 -*-
"""Iconos nuevos del 19/11: taladros, motosierras, materiales y materiales de elites.

El arte sale de las 3 laminas que mando el dueno (pack-source/art/ref_19_11/). Este archivo recorta cada
dibujo, le saca el fondo y lo baja a 64x64 (herramientas) o 32x32 (materiales). Se aplica al final de
build_pack.py, asi gana sobre las texturas viejas (tools/, redesign/, gen/).

Taladros y motosierras: el dibujo es horizontal (como una pistola), asi que en la mano se usa un modelo
propio que la sostiene apuntando hacia adelante en vez del angulo diagonal de las espadas.

Uso: python iconos_19_11.py   -> build/previews/iconos_19_11.png (para revisar los recortes)
"""
import io
import json
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
REF = HERE / 'pack-source' / 'art' / 'ref_19_11'

# id del item -> (lamina, caja x0, y0, x1, y1 donde esta el dibujo, sin el nombre)
TOOLS = {
    'taladro_diamante': ('herramientas', (38, 160, 322, 410)),
    'taladro_mitril': ('herramientas', (362, 160, 655, 410)),
    'taladro_amatista': ('herramientas', (695, 160, 998, 410)),
    'taladro_rubi': ('herramientas', (1038, 160, 1362, 410)),
    'taladro_topacio': ('herramientas', (1402, 160, 1740, 410)),
    # VI-IX: Gemini 19/11 con la lamina de herramientas como referencia (taladros_6_9.png)
    'taladro_titanio': ('taladros_6_9', (40, 520, 657, 1085)),
    'taladro_jaspe': ('taladros_6_9', (659, 520, 1317, 1085)),
    'taladro_gemas': ('taladros_6_9', (1319, 520, 1994, 1085)),
    'taladro_divan': ('taladros_6_9', (1996, 520, 2730, 1085)),
    'motosierra_basica': ('herramientas', (32, 505, 324, 730)),
    'motosierra_avanzada': ('herramientas', (358, 505, 657, 730)),
    'motosierra_industrial': ('herramientas', (690, 505, 1003, 730)),
    'motosierra_infernal': ('herramientas', (1032, 505, 1366, 730)),
    'motosierra_astral': ('herramientas', (1398, 505, 1745, 730)),
}
MATERIALS = {
    # Metal y soporte
    'shadowsteel': ('materiales', (55, 95, 240, 240)),
    'netherita_fundida': ('materiales', (255, 95, 430, 240)),
    'netherita_reforzada': ('materiales', (450, 95, 640, 240)),
    'cuero_tratado': ('materiales', (665, 95, 820, 240)),
    'madera_estelar': ('materiales', (840, 95, 1020, 240)),
    'palo_reforzado': ('materiales', (1040, 90, 1210, 240)),
    # Cristal arcano
    'cristal_arcano': ('materiales', (225, 320, 420, 460)),
    'fragmento_cristal': ('materiales', (560, 345, 700, 455)),
    'cristal_refinado': ('materiales', (895, 325, 1010, 460)),
    # Familia umbria
    'fragmento_umbrio': ('materiales', (185, 560, 310, 675)),
    'gema_umbria_fragmentada': ('materiales', (425, 555, 570, 675)),
    'gema_umbria': ('materiales', (680, 550, 820, 680)),
    'gema_umbria_perfecta': ('materiales', (935, 545, 1100, 685)),
    # Luz y furia
    'gema_luminica': ('materiales', (120, 780, 250, 900)),
    'gema_luminica_perfecta': ('materiales', (345, 775, 485, 905)),
    'nucleo_furia': ('materiales', (575, 770, 720, 893)),
    'nucleo_furia_pura': ('materiales', (800, 770, 960, 905)),
    'esencia_nether': ('materiales', (1020, 760, 1185, 905)),
    # Familia astral y nucleos
    'fragmento_astral': ('materiales', (90, 1005, 220, 1120)),
    'polvo_astral': ('materiales', (315, 1015, 460, 1110)),
    'nucleo_astral': ('materiales', (550, 995, 700, 1125)),
    'corazon_shulker': ('materiales', (785, 995, 950, 1120)),
    'nucleo_eolico': ('materiales', (1020, 990, 1175, 1125)),
    # Elites
    'esencia_elite': ('elites', (170, 140, 470, 610)),
    'alma_corrupta': ('elites', (700, 120, 1080, 610)),
    'chispa_astral': ('elites', (1200, 120, 1735, 620)),
}
# Talismanes (lamina del dueno 20/11): columnas I-III, filas vida/furia/viento/roca. 32x32 como los materiales.
_TAL_X = ((285, 495), (530, 800), (825, 1135))
_TAL_Y = {'vida': (195, 410), 'furia': (410, 630), 'viento': (630, 875), 'roca': (875, 1160)}
MATERIALS.update({
    f'talisman_{kind}_{n + 1}': ('talismanes', (x0, y0, x1, y1))
    for kind, (y0, y1) in _TAL_Y.items() for n, (x0, x1) in enumerate(_TAL_X)
})
TOOL_SIZE = 64
MATERIAL_SIZE = 32
HOLES = {'talismanes'}


def _bg_mask(rgb, tol=12):
    """Fondo = lo conectado al borde de la caja con color parecido al del borde."""
    h, w, _ = rgb.shape
    border = np.concatenate([rgb[0], rgb[-1], rgb[:, 0], rgb[:, -1]]).astype(int)
    bg = np.median(border, axis=0)
    near = (np.abs(rgb.astype(int) - bg).max(axis=2) <= tol)
    seen = np.zeros((h, w), bool)
    q = deque()
    for x in range(w):
        for y in (0, h - 1):
            if near[y, x] and not seen[y, x]:
                seen[y, x] = True
                q.append((y, x))
    for y in range(h):
        for x in (0, w - 1):
            if near[y, x] and not seen[y, x]:
                seen[y, x] = True
                q.append((y, x))
    while q:
        y, x = q.popleft()
        for ny, nx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
            if 0 <= ny < h and 0 <= nx < w and near[ny, nx] and not seen[ny, nx]:
                seen[ny, nx] = True
                q.append((ny, nx))
    return seen


def _drop_specks(fg, min_area):
    """Saca manchitas sueltas (ruido de compresion); las chispas reales del dibujo son mas grandes."""
    h, w = fg.shape
    label = np.zeros((h, w), int)
    keep = np.zeros((h, w), bool)
    comps = []
    n = 0
    for sy in range(h):
        for sx in range(w):
            if not fg[sy, sx] or label[sy, sx]:
                continue
            n += 1
            pts = [(sy, sx)]
            label[sy, sx] = n
            i = 0
            while i < len(pts):
                y, x = pts[i]
                i += 1
                for ny, nx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
                    if 0 <= ny < h and 0 <= nx < w and fg[ny, nx] and not label[ny, nx]:
                        label[ny, nx] = n
                        pts.append((ny, nx))
            ys, xs = zip(*pts)
            # Lo que toca el borde de la caja es un pedazo de titulo, nombre o flecha de la lamina.
            edge = min(ys) == 0 or min(xs) == 0 or max(ys) == h - 1 or max(xs) == w - 1
            comps.append((len(pts), edge, ys, xs))
    biggest = max((c[0] for c in comps), default=0)
    for area, edge, ys, xs in comps:
        if area >= min_area and (not edge or area == biggest):
            keep[list(ys), list(xs)] = True
    return keep


def cut(sheet, box):
    """Recorte a tamano completo (RGBA, fondo transparente, ajustado al dibujo)."""
    im = Image.open(REF / f'{sheet}.png').convert('RGB').crop(box)
    rgb = np.asarray(im)
    fg = ~_bg_mask(rgb)
    if sheet in HOLES:
        # Huecos de fondo encerrados por el dibujo (la pluma del Viento II): tambien son transparentes.
        border = np.concatenate([rgb[0], rgb[-1], rgb[:, 0], rgb[:, -1]]).astype(int)
        near = np.abs(rgb.astype(int) - np.median(border, axis=0)).max(axis=2) <= 12
        fg &= ~_drop_specks(near & fg, 150)
    fg = _drop_specks(fg, 40)
    rgba = np.dstack([rgb, (fg * 255).astype(np.uint8)])
    out = Image.fromarray(rgba, 'RGBA')
    return out.crop(out.getbbox())


def sprite(iid):
    sheet, box = TOOLS.get(iid) or MATERIALS[iid]
    size = TOOL_SIZE if iid in TOOLS else MATERIAL_SIZE
    big = cut(sheet, box)
    inner = size - 2  # 1 px de aire alrededor
    scale = inner / max(big.size)
    w, h = max(1, round(big.width * scale)), max(1, round(big.height * scale))
    # Promedio de color solo sobre lo opaco (sin halo oscuro del fondo) y alfa recortado (Minecraft no mezcla).
    arr = np.asarray(big).astype(float)
    a = arr[..., 3:4] / 255
    prem = Image.fromarray(np.dstack([arr[..., :3] * a, a[..., 0] * 255]).astype(np.uint8), 'RGBA')
    small = np.asarray(prem.resize((w, h), Image.Resampling.BOX)).astype(float)
    alpha = small[..., 3] / 255
    color = np.where(alpha[..., None] > 0, small[..., :3] / np.maximum(alpha[..., None], 1e-6), 0)
    color = np.clip(color, 0, 255)
    solid = alpha >= 0.5
    rgba = np.dstack([color, solid * 255]).astype(np.uint8)
    rgba[~solid] = 0
    tile = Image.new('RGBA', (size, size))
    piece = Image.fromarray(rgba, 'RGBA')
    tile.paste(piece, ((size - w) // 2, (size - h) // 2))
    return tile


# Taladro/motosierra en la mano: horizontal, la punta (que en el dibujo mira a la izquierda) hacia adelante.
# En la mano el "adelante" es el +Y del dibujo y el "arriba" es +Z (ItemInHandLayer gira X -90 e Y 180).
# Por eso las espadas (punta a 45 grados) giran Z+55: la punta queda a ~100 grados, casi sobre +Y.
# El 19/11 se uso Y=90 sin Z y los taladros quedaban apuntando para arriba. Ahora: mismo Y=-90 de las
# espadas y Z=-90, que lleva la punta (izquierda del dibujo, 180 grados) a +Y y el mango (abajo) a -Z.
# 1ra persona es el espacio de la camara (+Y arriba, -Z adelante): Y=-90 solo lleva la punta a -Z.
# La empunadura queda ~(+4.4, -3.6) px del centro del dibujo: la traslacion la pone donde las espadas
# vanilla tienen el mango (3ra persona ~(0, 0, 1.2); 1ra persona ~(1.13, 0, 0)).
HAND_DISPLAY = {
    'thirdperson_righthand': {'rotation': [0, -90, -90], 'translation': [0, 3.5, 4.1], 'scale': [0.8, 0.8, 0.8]},
    'thirdperson_lefthand': {'rotation': [0, 90, 90], 'translation': [0, 3.5, 4.1], 'scale': [0.8, 0.8, 0.8]},
    # 20/11: con Y=-90 y escala 0.7 se veia de canto, enorme y con el grosor negro. Y=-65 lo gira para mostrar
    # el costado y apuntar hacia la mira; Z=-8 levanta un poco la punta; mas chico.
    'firstperson_righthand': {'rotation': [0, -65, -8], 'translation': [0.1, 2.0, -2.2], 'scale': [0.55, 0.55, 0.55]},
    'firstperson_lefthand': {'rotation': [0, 65, 8], 'translation': [0.1, 2.0, -2.2], 'scale': [0.55, 0.55, 0.55]},
}


def _png(im):
    b = io.BytesIO()
    im.save(b, 'PNG')
    return b.getvalue()


def assets():
    files = {}
    for iid in list(TOOLS) + list(MATERIALS):
        tool = iid in TOOLS
        folder = 'iconos'
        files[f'assets/astral/textures/item/{folder}/{iid}.png'] = _png(sprite(iid))
        model = {'parent': 'minecraft:item/generated', 'textures': {'layer0': f'astral:item/{folder}/{iid}'}}
        if tool:
            model['display'] = HAND_DISPLAY
        files[f'assets/astral/models/item/{iid}.json'] = json.dumps(model, indent=1).encode()
        files[f'assets/astral/items/{iid}.json'] = json.dumps(
            {'model': {'type': 'minecraft:model', 'model': f'astral:item/{iid}'}}, indent=1).encode()
    return files


def preview():
    ids = list(TOOLS) + list(MATERIALS)
    cols = 6
    cell = 150
    rows = (len(ids) + cols - 1) // cols
    out = Image.new('RGB', (cols * cell, rows * cell + 30), '#191b28')
    d = ImageDraw.Draw(out)
    d.text((10, 8), 'Iconos 19/11: arriba ampliado, abajo a la derecha tamano real', fill='#e3c68a')
    for n, iid in enumerate(ids):
        x, y = (n % cols) * cell, (n // cols) * cell + 30
        im = sprite(iid)
        big = im.resize((128, 128), Image.Resampling.NEAREST)
        d.rectangle((x + 2, y + 2, x + cell - 3, y + cell - 3), fill='#292b38', outline='#575266')
        out.paste(big, (x + 11, y + 4), big)
        out.paste(im, (x + cell - im.width - 6, y + cell - im.height - 18) if im.width <= 32 else (x + 6, y + 6), im)
        d.text((x + 6, y + 133), iid[:22], fill='#e2deef')
    path = HERE.parent / 'build' / 'previews' / 'iconos_19_11.png'
    path.parent.mkdir(parents=True, exist_ok=True)
    out.save(path)
    # Cajas sobre las laminas, para ajustar recortes
    for sheet in ('herramientas', 'taladros_6_9', 'materiales', 'elites', 'talismanes'):
        im = Image.open(REF / f'{sheet}.png').convert('RGB')
        dd = ImageDraw.Draw(im)
        for iid, (s, box) in {**TOOLS, **MATERIALS}.items():
            if s == sheet:
                dd.rectangle(box, outline='#ff3060', width=3)
        im.save(path.parent / f'iconos_19_11_cajas_{sheet}.png')
    print(path)


if __name__ == '__main__':
    preview()
