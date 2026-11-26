"""Manzanas de Mazmorra (21/11/2026): curan mas que la de oro, una por tier T2-T10.

Pedido del dueno: el Bosque (T1) se aguanta con manzanas de oro/Notch; desde las Minas no.
Cada manzana cura una cantidad FIJA pensada para la vida del jugador de su tier (escala.VIDA_SET):
la mitad al instante y la otra mitad en 5 segundos. Fuera de su tier rinde poco (una T3 en T8 casi no
cura). Enfriamiento compartido entre todas: no se pueden encadenar.

Caen con probabilidad baja de los mobs de mazmorra (salas T2-T5 y la Infinita) del mismo tier.
Arte: hoja de referencia del dueno `.local/gemini/refs-manzanas/manzanas_ref.webp` (3x3, T2..T10),
recortada a `pack-source/manzanas/manzana_t#.png` (32x32). Si cambia la hoja, borrar los PNG y regenerar.
"""
import json
from pathlib import Path

from escala import VIDA_SET, COLOR_TIER

ROOT = Path(__file__).resolve().parents[1]
NS = 'astral'
TIERS = range(2, 11)
NOMBRES = {2: 'Mineral', 3: 'Ancestral', 4: 'Glacial', 5: 'Ignea', 6: 'del Ocaso', 7: 'del Eclipse',
           8: 'Supernova', 9: 'del Vacio', 10: 'del Fin'}
DONDE = {2: 'Minas Olvidadas', 3: 'Tumba del Rey de Arena', 4: 'Cumbre Helada', 5: 'Corazon de la Forja',
         **{t: f'Mazmorra Infinita {"VI VII VIII IX X".split()[t - 6]}' for t in range(6, 11)}}

# Cura total = CURA_PCT de la vida con el set completo de su tier (la de oro rinde menos y el jugador
# no queda inmortal: un mob comun de su tier saca ~1-10% por golpe, un jefe mucho mas).
CURA_PCT = 0.45
CURA = {t: int(round(VIDA_SET[t] * CURA_PCT, -1)) for t in TIERS}
INSTANTE = 0.5          # parte que cura al comer; el resto en REGEN_SEGUNDOS
REGEN_SEGUNDOS = 5
ENFRIAMIENTO = 20       # segundos, compartido por todas las manzanas de mazmorra
COMER_SEGUNDOS = 1.0    # la de oro tarda 1,6
# Probabilidad de caida por mob de su tier en una mazmorra.
PROB = {'comun': 0.03, 'elite': 0.12}


def iid(t):
    return f'manzana_t{t}'


def nombre(t):
    return f'Manzana {NOMBRES[t]}'


def _fmt(n):
    return f'{n:,}'.replace(',', '.')


def register(add, txt):
    for t in TIERS:
        cura = CURA[t]
        lore = [txt(f'Cura {_fmt(cura)} de vida:', 'gray'),
                txt(f'  {_fmt(round(cura * INSTANTE))} al instante y {_fmt(cura - round(cura * INSTANTE))} en {REGEN_SEGUNDOS} s', 'white'),
                txt(f'Pensada para el Tier {t}. Espera {ENFRIAMIENTO} s entre manzanas.', 'gray'),
                txt(f'Cae en: {DONDE[t]}', 'dark_gray')]
        extra = {'minecraft:max_stack_size': 16,
                 'minecraft:food': {'nutrition': 4, 'saturation': 9.6, 'can_always_eat': True},
                 'minecraft:consumable': {'consume_seconds': COMER_SEGUNDOS, 'animation': 'eat',
                                          'sound': 'minecraft:entity.generic.eat'},
                 'minecraft:use_cooldown': {'seconds': ENFRIAMIENTO, 'cooldown_group': f'{NS}:manzana_mazmorra'},
                 'minecraft:rarity': 'epic' if t >= 6 else 'rare'}
        add(iid(t), 'minecraft:apple', nombre(t), COLOR_TIER[t], lore, {'type': 'consumable', 'tier': t},
            extra=extra, model=f'{NS}:{iid(t)}', pdc={f'{NS}:consumible': iid(t)})


def runtime_data():
    """Para AstralDecor (manzanas.json): cuanto cura cada una."""
    return {iid(t): {'cura': CURA[t], 'instante': INSTANTE, 'segundos': REGEN_SEGUNDOS, 'nombre': nombre(t),
                     'color': COLOR_TIER[t]} for t in TIERS}


def mob_roll_tag(tiers_mazmorra):
    """Lineas para mob/roll: marca astral.maz a los mobs que aparecen en una mazmorra (#dg 1)."""
    return ['execute if score #dg astral.tmp matches 1 run tag @s add astral.maz']


def generate(put, fn, chance):
    """Advancements de muerte: mob de tier t en mazmorra (astral.maz) o en la Infinita (inf.mob)."""
    nbt = lambda tag: {'condition': 'minecraft:entity_properties', 'entity': 'this',
                       'predicate': {'nbt': f'{{Tags:["{tag}"]}}'}}
    elite = nbt('astral.elite')
    for t in TIERS:
        for kind, p in PROB.items():
            cond = [nbt(f'astral.mt{t}'),
                    {'condition': 'minecraft:any_of', 'terms': [nbt('astral.maz'), nbt('inf.mob')]},
                    elite if kind == 'elite' else {'condition': 'minecraft:inverted', 'term': elite}]
            name = f'manzana{t}_{kind}'
            put(f'data/{NS}/advancement/kill/{name}.json', {
                'criteria': {'kill': {'trigger': 'minecraft:player_killed_entity', 'conditions': {'entity': cond}}},
                'rewards': {'function': f'{NS}:drop/{name}'}})
            fn(f'drop/{name}', [
                f'advancement revoke @s only {NS}:kill/{name}',
                f'execute if predicate {chance(p)} run function {NS}:drop/give {{id:"{iid(t)}",name:"{nombre(t)}"}}'])


# ---------------------------------------------------------------------------
# Arte
# ---------------------------------------------------------------------------
REF = ROOT / '.local/gemini/refs-manzanas/manzanas_ref.webp'
ARTE = ROOT / 'datapack-src/pack-source/manzanas'
# Cajas de la hoja 1254x1254 (filas T2-T4, T5-T7, T8-T10), con margen.
FILAS = [(100, 400), (455, 760), (830, 1135)]
COLUMNAS = [(90, 420), (470, 800), (850, 1170)]
FONDO = (12, 17, 36)


def recortar(size=32):
    """Recorta cada manzana de la hoja de referencia: fondo azul oscuro -> transparente."""
    import numpy as np
    from PIL import Image, ImageDraw
    im = Image.open(REF).convert('RGB')
    a = np.asarray(im).astype(int)
    ARTE.mkdir(parents=True, exist_ok=True)
    t = 2
    for y0, y1 in FILAS:
        for x0, x1 in COLUMNAS:
            cell = a[y0:y1, x0:x1]
            fg = np.abs(cell - np.array(FONDO)).sum(2) > 60
            # Fondo = lo oscuro conectado al borde (los oscuros de adentro, como el Eclipse, quedan).
            m = Image.fromarray((fg * 255).astype('uint8'), 'L')
            m = m.crop((-1, -1, m.width + 1, m.height + 1))
            ImageDraw.floodfill(m, (0, 0), 128)
            keep = (np.asarray(m)[1:-1, 1:-1] != 128)
            ys, xs = np.nonzero(keep)
            cy0, cy1, cx0, cx1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
            side = max(cy1 - cy0, cx1 - cx0)
            rgba = np.dstack([cell, keep * 255]).astype('uint8')
            crop = Image.fromarray(rgba).crop((cx0, cy0, cx1, cy1))
            sq = Image.new('RGBA', (side, side))
            sq.paste(crop, ((side - crop.width) // 2, (side - crop.height) // 2))
            small = sq.resize((size, size), Image.BOX)
            px = np.asarray(small).copy()
            px[..., 3] = np.where(px[..., 3] >= 110, 255, 0)
            Image.fromarray(px).save(ARTE / f'{iid(t)}.png')
            t += 1


def pack_assets():
    if not all((ARTE / f'{iid(t)}.png').exists() for t in TIERS):
        recortar()
    files = {}
    for t in TIERS:
        i = iid(t)
        tex = f'{NS}:item/manzanas/{i}'
        files[f'assets/{NS}/textures/item/manzanas/{i}.png'] = (ARTE / f'{i}.png').read_bytes()
        files[f'assets/{NS}/models/manzanas/{i}.json'] = json.dumps(
            {'parent': 'minecraft:item/generated', 'textures': {'layer0': tex}}).encode()
        files[f'assets/{NS}/items/{i}.json'] = json.dumps(
            {'model': {'type': 'minecraft:model', 'model': f'{NS}:manzanas/{i}'}}).encode()
    return files


if __name__ == '__main__':
    recortar()
    for t in TIERS:
        print(t, nombre(t), CURA[t])
