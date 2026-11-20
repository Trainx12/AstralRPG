"""Bosque Astral nuevo: recorta 300x300 de 'Forested Plains' (mapa de terceros, privado) y lo limpia.

python tools/bosque_mapa.py
Entrada: .local/bosque-mapas/fuente/region (regiones del mapa original, nunca al repo).
Salida:  .local/bosque-mapas/datos/ (bloques + paleta + arboles extra + spawn) para tools/bosque_armar.py.

Limpieza: tapa cuevas (todo lo de abajo del suelo queda piedra), cambia la piedra oscura del suelo
(deepslate/tuff/basalto a la vista) por tierra gruesa, podzol, tierra con raices o musgo, deja las
hojas persistentes y elige claros para sumar arboles de Minecraft que el mapa no tiene.
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT / 'datapack-src'))
from bosque_mapa_leer import load_box  # noqa: E402
import bosque_talar as B  # noqa: E402

SRC = ROOT / '.local/bosque-mapas/fuente/region'
OUT = ROOT / '.local/bosque-mapas/datos'
SRC_X0, SRC_Z0 = 210, -510       # esquina del recorte en el mapa original
RENAME = {'minecraft:grass': 'minecraft:short_grass'}   # 1.18 -> 26.1
DARK = ('minecraft:deepslate', 'minecraft:tuff', 'minecraft:smooth_basalt', 'minecraft:cobbled_deepslate')
UNDER = ('cave_vines', 'spore_blossom', 'dripstone', 'glow_lichen', 'moss_carpet', 'azalea', 'big_dripleaf',
         'small_dripleaf', 'hanging_roots', 'lava', 'water', 'clay', 'mushroom', 'sculk', 'amethyst', 'ore')


def kind(names):
    air = np.array([n in ('minecraft:air', 'minecraft:cave_air', 'minecraft:void_air') for n in names])
    tree = np.array([('_log' in n or '_wood' in n or 'leaves' in n or n.endswith('bee_nest')) for n in names])
    water = np.array([('water' in n or 'seagrass' in n or 'kelp' in n) for n in names])
    plant = np.array([(not a and not t and not w and not n.endswith(('_block', 'stone', 'dirt', 'sand', 'gravel',
                       'deepslate', 'tuff', 'basalt', 'clay', 'andesite', 'diorite', 'granite', 'calcite', 'podzol',
                       'cobblestone', 'sandstone', 'bedrock', '_ore')))
                      for n, a, t, w in zip(names, air, tree, water)])
    return air, tree, water, plant


def build():
    W = B.SIZE
    y0, y1 = B.LIVE_BOTTOM, B.LIVE_TOP
    arr, pal = load_box(SRC, SRC_X0, SRC_X0 + W - 1, SRC_Z0, SRC_Z0 + W - 1, y0, y1)
    pal = [RENAME.get(p.split('[')[0], p.split('[')[0]) + (p[p.index('['):] if '[' in p else '') for p in pal]
    pal = [p.replace('persistent=false', 'persistent=true') for p in pal]
    index = {p: i for i, p in enumerate(pal)}

    def pid(state):
        if state not in index:
            index[state] = len(pal); pal.append(state)
        return index[state]

    names = [p.split('[')[0] for p in pal]
    air, tree, water, plant = kind(names)
    H = arr.shape[0]
    soft = (air | tree | water | plant)
    solid = ~soft[arr]
    ground = np.where(solid.any(0), H - 1 - np.argmax(solid[::-1], 0), 0)     # indice y del suelo
    stone, dirt = pid('minecraft:stone'), pid('minecraft:dirt')
    ys = np.arange(H)[:, None, None]
    below = ys < ground[None]
    # Cuevas y cosas de cueva debajo del suelo -> piedra (tierra en los 3 de arriba).
    under_bad = np.array([any(k in n for k in UNDER) for n in names]) | air | tree | plant
    fix = below & under_bad[arr]
    arr[fix & (ys >= ground[None] - 3)] = dirt
    arr[fix & (ys < ground[None] - 3)] = stone
    # Piedra oscura a la vista (arriba): tierra gruesa / podzol / tierra con raices / musgo, mezclado.
    names = [p.split('[')[0] for p in pal]
    air, tree, water, plant = kind(names)
    dark = np.isin(arr, [i for i, n in enumerate(names) if n in DARK])
    above_open = np.zeros_like(dark)
    above_open[:-1] = (air | plant)[arr[1:]]
    rng = np.random.default_rng(7)
    mix = np.array([pid('minecraft:coarse_dirt'), pid('minecraft:podzol'), pid('minecraft:rooted_dirt'),
                    pid('minecraft:moss_block'), pid('minecraft:coarse_dirt')])
    top_dark = dark & above_open
    arr[top_dark] = mix[rng.integers(0, len(mix), top_dark.sum())]
    # Costados a la vista: piedra con musgo / piedra / andesita.
    names = [p.split('[')[0] for p in pal]
    air, tree, water, plant = kind(names)
    dark = np.isin(arr, [i for i, n in enumerate(names) if n in DARK])
    op = (air | plant | water)[arr]
    side = np.zeros_like(dark)
    side[:, 1:, :] |= op[:, :-1, :]; side[:, :-1, :] |= op[:, 1:, :]
    side[:, :, 1:] |= op[:, :, :-1]; side[:, :, :-1] |= op[:, :, 1:]
    sd = dark & side
    side_mix = np.array([pid('minecraft:mossy_cobblestone'), pid('minecraft:stone'), pid('minecraft:andesite')])
    arr[sd] = side_mix[rng.integers(0, 3, sd.sum())]
    # Piso parejo abajo de todo: la caja no deja ver vacio.
    arr[0] = stone

    names = [p.split('[')[0] for p in pal]
    air, tree, water, plant = kind(names)
    gy = ground + y0                         # Y real del suelo
    treecol = tree[arr].any(0)
    watercol = water[arr].any(0)
    top_name = np.array(names)[arr[ground, np.arange(W)[:, None], np.arange(W)[None, :]]]

    # Spawn: claro plano cerca del centro.
    def free_area(cx, cz, r):
        a = slice(cz - r, cz + r + 1), slice(cx - r, cx + r + 1)
        return (not treecol[a].any() and not watercol[a].any() and gy[a].max() - gy[a].min() <= 1)
    best = None
    c = W // 2
    for r in range(0, 90, 2):
        for dz in range(-r, r + 1, 2):
            for dx in range(-r, r + 1, 2):
                if max(abs(dx), abs(dz)) != r:
                    continue
                if free_area(c + dx, c + dz, 5):
                    best = (c + dx, c + dz); break
            if best: break
        if best: break
    sx, sz = best
    sgy = int(gy[sz, sx])
    # Plataforma 7x7 de piedra con musgo a la altura del suelo del spawn.
    plat = pid('minecraft:mossy_stone_bricks')
    for z in range(sz - 3, sz + 4):
        for x in range(sx - 3, sx + 4):
            arr[sgy - y0, z, x] = plat
            arr[sgy - y0 - 3:sgy - y0, z, x] = dirt
            arr[sgy - y0 + 1:, z, x] = 0
    occupied = np.zeros((W, W), bool)
    occupied[sz - 8:sz + 9, sx - 8:sx + 9] = True

    # Arboles extra en claros: especies que el mapa no tiene (y abetos gigantes, los preferidos).
    okground = np.isin(top_name, ['minecraft:grass_block', 'minecraft:moss_block', 'minecraft:podzol',
                                  'minecraft:coarse_dirt', 'minecraft:rooted_dirt', 'minecraft:dirt'])
    extra = []
    rng2 = np.random.default_rng(11)
    plan = [f for f, n in B.EXTRA_TREES for _ in range(n)]
    rng2.shuffle(plan)
    # distancia a cualquier arbol (cuadrada, en columnas)
    from numpy.lib.stride_tricks import sliding_window_view as sw
    for feat in plan:
        r = 7 if feat.startswith(('mega', 'dark', 'fancy', 'pale')) else 5
        pad = np.pad(treecol | occupied | watercol, r, constant_values=True)
        busy = sw(pad, (2 * r + 1, 2 * r + 1)).any((2, 3))
        gpad = np.pad(gy, 1, mode='edge')
        flat = (sw(gpad, (3, 3)).max((2, 3)) - sw(gpad, (3, 3)).min((2, 3))) <= 1
        cand = ~busy & okground & flat
        cand[:10, :] = cand[-10:, :] = cand[:, :10] = cand[:, -10:] = False
        zz, xx = np.nonzero(cand)
        if len(zz) == 0:
            continue
        k = rng2.integers(len(zz))
        x, z = int(xx[k]), int(zz[k])
        extra.append((feat, x, int(gy[z, x]) + 1, z))
        occupied[max(0, z - r):z + r + 1, max(0, x - r):x + r + 1] = True
        if feat.startswith('mega'):
            # el mega arbol usa 2x2: el suelo vecino tiene que ser tierra tambien
            for dz in (0, 1):
                for dx in (0, 1):
                    arr[int(gy[z, x]) - y0, z + dz, x + dx] = pid('minecraft:podzol')
                    arr[int(gy[z, x]) - y0 + 1:int(gy[z, x]) - y0 + 3, z + dz, x + dx] = 0

    OUT.mkdir(parents=True, exist_ok=True)
    arr.astype('<u2').tofile(OUT / 'bloques.u16')
    (OUT / 'paleta.txt').write_text('\n'.join(pal) + '\n', encoding='utf-8')
    (OUT / 'extra.txt').write_text(''.join(f'{f} {x} {y} {z}\n' for f, x, y, z in extra), encoding='utf-8')
    info = {'size': W, 'y0': y0, 'y1': y1, 'shape_yzx': list(arr.shape), 'spawn': [sx, sgy, sz],
            'extra': len(extra), 'origen_mapa': [SRC_X0, SRC_Z0]}
    (OUT / 'info.json').write_text(json.dumps(info, indent=1), encoding='utf-8')
    print(json.dumps(info), 'paleta', len(pal))
    from collections import Counter
    print(Counter(f for f, *_ in extra))


if __name__ == '__main__':
    build()
