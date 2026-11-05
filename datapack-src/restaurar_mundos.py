"""Preparar una restauracion selectiva; los mapas privados nunca van a build/.

No se reemplaza world, level.dat ni datos de jugadores. Los archivos preparados
se instalan con el servidor apagado, solo en las dos dimensiones indicadas.
"""
from collections import deque
from copy import deepcopy
import gzip
import hashlib
import json
from pathlib import Path
import shutil

import numpy as np

from mapas import NBT, block, chunk_records, nbt_payload, nbt_string
from portales_mapas import load_schematic, write_world

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / '.local/restauracion-mundos-2026-11-05'
NATURAL = set('stone andesite granite diorite dirt grass_block gravel sand sandstone '
              'clay mud water lava bubble_column glow_lichen seagrass tall_seagrass '
              'short_grass tall_grass grass sugar_cane poppy dandelion oxeye_daisy '
              'cornflower azure_bluet pumpkin deepslate'.split())


def void_generator(tree):
    """Cambiar solo el generador de Overworld, conservando semilla y otros datos."""
    tree = deepcopy(tree)
    data = tree[1]['data'][1]
    data['generate_structures'] = (1, 0)
    data['dimensions'][1]['minecraft:overworld'][1]['generator'] = (10, {
        'type': (8, 'minecraft:flat'), 'settings': (10, {
            'features': (1, 0), 'lakes': (1, 0),
            'biome': (8, 'minecraft:the_void'),
            'layers': (9, [(10, {'block': (8, 'minecraft:air'), 'height': (3, 1)})])})})
    return tree


def end_scene(path):
    root = NBT(gzip.decompress(path.read_bytes())).root()
    root = root.get('Schematic', root)
    palette, blocks = load_schematic(path)
    for i, name in enumerate(palette):
        basic = name.split('[')[0].removeprefix('minecraft:')
        if basic in NATURAL or basic.endswith(('_ore', '_leaves', '_log')):
            blocks[blocks == i] = 0
    # Equivalente al //paste original en 146 82 78, incluido el Offset de WorldEdit.
    origin = tuple(a+b for a, b in zip((146, 82, 78), root['Offset']))
    # Tapar solo huecos encerrados por el piso, sin extender su borde exterior.
    floor = blocks[83-origin[1]]
    outside = np.zeros(floor.shape, dtype=bool)
    queue = deque()
    h, w = floor.shape
    for z in range(h):
        queue.extend(((z, 0), (z, w-1)))
    for x in range(w):
        queue.extend(((0, x), (h-1, x)))
    while queue:
        z, x = queue.popleft()
        if not (0 <= z < h and 0 <= x < w) or outside[z, x] or floor[z, x]:
            continue
        outside[z, x] = True
        queue.extend(((z-1, x), (z+1, x), (z, x-1), (z, x+1)))
    concrete = palette.index('minecraft:black_concrete')
    holes = (floor == 0) & ~outside
    floor[holes] = concrete
    # Eliminar soporte natural no debe provocar que caiga el piso de polvo.
    powder = palette.index('minecraft:black_concrete_powder')
    for y in range(1, blocks.shape[0]):
        support = (blocks[y] == powder) & (blocks[y-1] == 0)
        blocks[y-1][support] = concrete
    return palette, blocks, origin, root['DataVersion'], int(holes.sum())


def read_at(directory, x, y, z):
    path = directory / f'r.{x//512}.{z//512}.mca'
    chunk = next(c for c in chunk_records(path.read_bytes())
                 if (c['xPos'], c['zPos']) == (x//16, z//16))
    return block(chunk, x % 16, y, z % 16)


def main():
    downloads = Path.home() / 'Downloads'
    portals = OUTPUT / 'portales_astrales/region'
    if OUTPUT.exists():
        raise SystemExit('La salida ya existe; conservarla y usar una carpeta nueva para otra ejecucion.')
    palette, blocks, origin, version, holes = end_scene(downloads/'portal_END.schem')
    write_world(portals, palette, blocks, origin, data_version=version)
    report = json.loads((ROOT/'.local/portales/separacion/informe.json').read_text())
    nether = np.load(ROOT/'.local/portales/separacion/nether.npy')
    # La construccion recuperada se alinea a la llegada elegida por el dueno.
    # La copia separada original estaba 92 bloques al norte de esa llegada.
    write_world(portals, report['paleta_nether'], nether, (-2248, 79, 89))
    for x, y, z, expected in [(146, 83, 68, 'minecraft:black_concrete'),
                              (146, 84, 68, 'minecraft:air'),
                              (146, 85, 68, 'minecraft:air'),
                              (145, 96, 0, 'minecraft:end_portal'),
                              (-2193, 80, 90, 'minecraft:black_terracotta'),
                              (-2193, 81, 90, 'minecraft:air'),
                              (-2193, 82, 90, 'minecraft:air')]:
        actual = read_at(portals, x, y, z)
        assert actual == expected, ((x, y, z), actual, expected)
    forja = OUTPUT / 'forja_volcano'
    shutil.copytree(ROOT/'.local/mapas/forja-volcano/forja_volcano/region', forja/'region')
    water = 0
    for path in (forja/'region').glob('*.mca'):
        for chunk in chunk_records(path.read_bytes()):
            for section in chunk.get('sections', []):
                water += sum(e['Name'] == 'minecraft:water'
                             for e in section.get('block_states', {}).get('palette', []))
    assert water == 0, 'La copia de Forja contiene agua: no instalar.'
    assert read_at(forja/'region', 82, 51, -56) == 'minecraft:blackstone'
    assert read_at(forja/'region', 82, 52, -56) == 'minecraft:air'
    assert read_at(forja/'region', 82, 53, -56) == 'minecraft:air'
    generator_path = downloads/'world_gen_settings.dat'
    tree = NBT(gzip.decompress(generator_path.read_bytes()), typed=True).root()
    tree = void_generator(tree)
    target = forja/'data/minecraft/world_gen_settings.dat'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(gzip.compress(bytes([tree[0]])+nbt_string('')+nbt_payload(tree), mtime=0))
    files = {str(p.relative_to(OUTPUT)): hashlib.sha256(p.read_bytes()).hexdigest()
             for p in OUTPUT.rglob('*') if p.is_file()}
    manifest = {'archivos_sha256': files, 'end_huecos_tapados': holes,
                'forja_agua': water, 'nether_origen': [-2248, 79, 89],
                'instalado': False, 'verificaciones_locales': 'pisos, aire y portal End OK'}
    (OUTPUT/'informe.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    main()
