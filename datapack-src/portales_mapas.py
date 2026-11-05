"""Preparar los mapas privados de Santuario y del cruce de portales.

Los ZIP originales y sus construcciones se conservan fuera del repositorio.
Solo se exportan bloques. No se importan entidades, datapacks ni inventarios.
"""
from functools import lru_cache
import gzip
import json
import math
from pathlib import Path
import struct
from zipfile import ZipFile
import zlib

import numpy as np

from mapas import NBT, chunk_records, nbt_payload, nbt_string

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / '.local/portales'
AIR = {'minecraft:air', 'minecraft:cave_air', 'minecraft:void_air'}
LOGIC = {'minecraft:command_block', 'minecraft:chain_command_block',
         'minecraft:repeating_command_block', 'minecraft:structure_block',
         'minecraft:jigsaw', 'minecraft:spawner', 'minecraft:trial_spawner'}
NETHER_BOUNDS = (-200, 79, -2, -90, 170, 36)
NETHER_MOVED_ORIGIN = (-2248, 79, -3)


def separate_portal_scene(palette, blocks, origin):
    """Retirar la conexion y mover/girar la construccion completa del Nether."""
    def selection(bounds):
        x0, y0, z0, x1, y1, z1 = bounds
        return (slice(y0-origin[1], y1-origin[1]+1),
                slice(z0-origin[2], z1-origin[2]+1),
                slice(x0-origin[0], x1-origin[0]+1))

    nether = blocks[selection(NETHER_BOUNDS)].copy()[:, ::-1, ::-1]
    nether_palette = [rotate_half(name) for name in palette]
    blocks[selection(NETHER_BOUNDS)] = 0
    terracotta = palette.index('minecraft:black_terracotta')
    # Conservar las bases propias de los dos escenarios. Retirar el puente,
    # el distribuidor central y los tramos que quedan fuera de cada base.
    for bounds in [(-207, 79, 116, 207, 80, 136), (-20, 79, 105, 20, 80, 145),
                   (-154, 79, 37, -136, 80, 125), (136, 79, 104, 154, 80, 125)]:
        view = blocks[selection(bounds)]
        view[view == terracotta] = 0
    for x in range(-198, 199, 18):
        for z in (116, 136):
            for y, name in [(81, 'minecraft:polished_blackstone_wall'),
                            (82, 'minecraft:lantern')]:
                iy, iz, ix = y-origin[1], z-origin[2], x-origin[0]
                if palette[int(blocks[iy, iz, ix])].split('[')[0] == name:
                    blocks[iy, iz, ix] = 0
    return nether_palette, nether


def state_name(entry):
    properties = entry.get('Properties', {})
    suffix = '[' + ','.join(f'{k}={v}' for k, v in sorted(properties.items())) + ']' if properties else ''
    return entry['Name'] + suffix


def state_tag(name):
    block, _, properties = name.partition('[')
    value = {'Name': (8, block)}
    if properties:
        value['Properties'] = (10, {k: (8, v) for k, v in
                                    (p.split('=') for p in properties.rstrip(']').split(','))})
    return (10, value)


def unpack_padded(data, count, bits):
    raw = np.asarray([int(v) & ((1 << 64) - 1) for v in data], dtype=np.uint64)
    indices = np.arange(count, dtype=np.uint64)
    per = 64 // bits
    return ((raw[indices // per] >> ((indices % per) * bits)) & ((1 << bits) - 1)).astype(np.uint16)


def unpack_continuous(data, count, bits):
    raw = np.asarray([int(v) & ((1 << 64) - 1) for v in data] + [0], dtype=np.uint64)
    offsets = np.arange(count, dtype=np.uint64) * bits
    words, shifts = offsets // 64, offsets % 64
    values = raw[words] >> shifts
    crossing = shifts + bits > 64
    values[crossing] |= raw[words[crossing] + 1] << (64 - shifts[crossing])
    return (values & ((1 << bits) - 1)).astype(np.uint16)


def load_schematic(path):
    root = NBT(gzip.decompress(path.read_bytes())).root()
    root = root.get('Schematic', root)
    width, height, length = (root[k] for k in ('Width', 'Height', 'Length'))
    storage = root.get('Blocks', root)
    palette = [None] * len(storage['Palette'])
    for name, index in storage['Palette'].items():
        palette[index] = name
    blocks = np.empty(width * height * length, dtype=np.uint16)
    index = value = shift = 0
    for byte in storage.get('Data', storage.get('BlockData', b'')):
        value |= (byte & 127) << shift
        if byte & 128:
            shift += 7
        else:
            blocks[index] = value
            index += 1
            value = shift = 0
    if index != blocks.size or shift:
        raise ValueError('Datos incompletos en el schematic')
    palette, blocks = canonical_air(palette, blocks)
    return palette, blocks.reshape(height, length, width)


def canonical_air(palette, blocks):
    names = ['minecraft:air']
    lookup = {names[0]: 0}
    mapping = []
    for name in palette:
        if name.split('[')[0] in AIR:
            mapping.append(0)
        else:
            if name not in lookup:
                lookup[name] = len(names)
                names.append(name)
            mapping.append(lookup[name])
    return names, np.asarray(mapping, dtype=np.uint16)[blocks]


def load_litematic(path):
    root = NBT(gzip.decompress(path.read_bytes())).root()
    if len(root['Regions']) != 1:
        raise ValueError('Se espera una unica seleccion en el Santuario')
    region = next(iter(root['Regions'].values()))
    width, height, length = (abs(region['Size'][k]) for k in 'xyz')
    palette = [state_name(entry) for entry in region['BlockStatePalette']]
    bits = max(2, (len(palette) - 1).bit_length())
    blocks = unpack_continuous(region['BlockStates'], width * height * length, bits)
    palette, blocks = canonical_air(palette, blocks)
    return palette, blocks.reshape(height, length, width)


def load_world(path):
    archive = ZipFile(path)
    level = next(n for n in archive.namelist() if n.endswith('/level.dat'))
    prefix = level[:-9] + 'region/'
    names = {Path(n).name: n for n in archive.namelist() if n.startswith(prefix) and n.endswith('.mca')}

    @lru_cache(maxsize=20)
    def region(rx, rz):
        name = names.get(f'r.{rx}.{rz}.mca')
        return {(c['xPos'], c['zPos']): c for c in chunk_records(archive.read(name))} if name else {}

    return archive, names, region


def world_box(path, bounds):
    x0, y0, z0, x1, y1, z1 = bounds
    archive, names, region = load_world(path)
    palette = ['minecraft:air']
    lookup = {palette[0]: 0}
    blocks = np.zeros((y1 - y0 + 1, z1 - z0 + 1, x1 - x0 + 1), dtype=np.uint16)
    for cz in range(z0 // 16, z1 // 16 + 1):
        for cx in range(x0 // 16, x1 // 16 + 1):
            chunk = region(cx // 32, cz // 32).get((cx, cz))
            if not chunk:
                continue
            for section in chunk.get('sections', chunk.get('Sections', [])):
                sy = int(section['Y']) * 16
                if sy + 15 < y0 or sy > y1:
                    continue
                state = section.get('block_states', {'palette': section.get('Palette', []),
                                                     'data': section.get('BlockStates', [])})
                entries = state.get('palette', [])
                if not entries:
                    continue
                mapping = []
                for entry in entries:
                    name = state_name(entry)
                    if name not in lookup:
                        lookup[name] = len(palette)
                        palette.append(name)
                    mapping.append(lookup[name])
                indices = (np.zeros(4096, dtype=np.uint16) if len(entries) == 1 else
                           unpack_padded(state['data'], 4096, max(4, (len(entries) - 1).bit_length())))
                values = np.asarray(mapping, dtype=np.uint16)[indices].reshape(16, 16, 16)
                ax, bx = max(x0, cx * 16), min(x1 + 1, cx * 16 + 16)
                az, bz = max(z0, cz * 16), min(z1 + 1, cz * 16 + 16)
                ay, by = max(y0, sy), min(y1 + 1, sy + 16)
                blocks[ay-y0:by-y0, az-z0:bz-z0, ax-x0:bx-x0] = values[ay-sy:by-sy, az-cz*16:bz-cz*16, ax-cx*16:bx-cx*16]
    archive.close()
    return palette, blocks


def sanitize(palette, blocks):
    for index, name in enumerate(palette):
        block = name.split('[')[0]
        if block in AIR or block in LOGIC:
            blocks[blocks == index] = 0
    return palette, blocks


def schematic(path, palette, blocks):
    height, length, width = blocks.shape
    unique, inverse = np.unique(blocks.reshape(-1), return_inverse=True)
    names = [palette[int(i)] for i in unique]
    data = bytearray()
    for value in inverse:
        value = int(value)
        while value >= 128:
            data.append((value & 127) | 128)
            value >>= 7
        data.append(value)
    root = {'Version': (3, 2), 'DataVersion': (3, 3465),
            'Width': (2, width), 'Height': (2, height), 'Length': (2, length),
            'Offset': (11, [0, 0, 0]), 'PaletteMax': (3, len(names)),
            'Palette': (10, {name: (3, i) for i, name in enumerate(names)}),
            'BlockData': (7, bytes(data)), 'BlockEntities': (9, [])}
    path.write_bytes(gzip.compress(b'\x0a' + nbt_string('Schematic') + nbt_payload((10, root)), mtime=0))


def pack_padded(values, bits):
    per = 64 // bits
    padded = np.zeros(math.ceil(len(values) / per) * per, dtype=np.uint64)
    padded[:len(values)] = values
    words = np.bitwise_or.reduce(padded.reshape(-1, per) << (np.arange(per, dtype=np.uint64) * bits), axis=1)
    return words.view(np.int64).tolist()


def write_world(directory, palette, blocks, origin, data_version=3465):
    directory.mkdir(parents=True, exist_ok=True)
    x0, y0, z0 = origin
    height, length, width = blocks.shape
    regions = {}
    for cz in range(z0 // 16, (z0 + length - 1) // 16 + 1):
        for cx in range(x0 // 16, (x0 + width - 1) // 16 + 1):
            sections = []
            for sy in range(y0 // 16, (y0 + height - 1) // 16 + 1):
                cube = np.zeros((16, 16, 16), dtype=np.uint16)
                ax, bx = max(x0, cx*16), min(x0+width, cx*16+16)
                az, bz = max(z0, cz*16), min(z0+length, cz*16+16)
                ay, by = max(y0, sy*16), min(y0+height, sy*16+16)
                cube[ay-sy*16:by-sy*16, az-cz*16:bz-cz*16, ax-cx*16:bx-cx*16] = blocks[ay-y0:by-y0, az-z0:bz-z0, ax-x0:bx-x0]
                unique, inverse = np.unique(cube.reshape(-1), return_inverse=True)
                if len(unique) == 1 and int(unique[0]) == 0:
                    continue
                state = {'palette': (9, [state_tag(palette[int(i)]) for i in unique])}
                if len(unique) > 1:
                    state['data'] = (12, pack_padded(inverse, max(4, (len(unique)-1).bit_length())))
                sections.append((10, {'Y': (1, sy), 'block_states': (10, state),
                                      'biomes': (10, {'palette': (9, [(8, 'minecraft:the_void')])})}))
            if not sections:
                continue
            chunk = {'DataVersion': (3, data_version), 'xPos': (3, cx), 'zPos': (3, cz), 'yPos': (3, -4),
                     'Status': (8, 'minecraft:full'), 'LastUpdate': (4, 0), 'InhabitedTime': (4, 0),
                     'isLightOn': (1, 0), 'sections': (9, sections), 'block_entities': (9, [])}
            payload = zlib.compress(b'\x0a' + nbt_string('') + nbt_payload((10, chunk)))
            record = struct.pack('>I', len(payload)+1) + b'\x02' + payload
            slot = (cz % 32) * 32 + cx % 32
            regions.setdefault((cx//32, cz//32), {})[slot] = record
    for (rx, rz), records in regions.items():
        header, data, sector = bytearray(8192), bytearray(), 2
        for slot, record in sorted(records.items()):
            size = math.ceil(len(record)/4096)
            header[slot*4:slot*4+4] = sector.to_bytes(3, 'big') + bytes([size])
            data.extend(record.ljust(size*4096, b'\x00'))
            sector += size
        (directory / f'r.{rx}.{rz}.mca').write_bytes(header + data)


def rotate_half(name):
    block, _, props = name.partition('[')
    if not props:
        return name
    pairs = dict(p.split('=') for p in props.rstrip(']').split(','))
    opposite = {'north': 'south', 'south': 'north', 'east': 'west', 'west': 'east'}
    rotated = {}
    for key, value in pairs.items():
        new_key = opposite.get(key, key)
        if key == 'facing':
            value = opposite.get(value, value)
        if key == 'rotation':
            value = str((int(value) + 8) % 16)
        rotated[new_key] = value
    return block + '[' + ','.join(f'{k}={v}' for k, v in sorted(rotated.items())) + ']'


def prepare_portals(downloads):
    # Llegada mirando al norte. End a la derecha (este), Nether a la izquierda.
    palette = ['minecraft:air']
    lookup = {palette[0]: 0}
    origin = (-224, 64, -104)
    blocks = np.zeros((224, 256, 496), dtype=np.uint16)

    def material(name):
        if name not in lookup:
            lookup[name] = len(palette)
            palette.append(name)
        return lookup[name]

    def paste(source_palette, source, xyz):
        x, y, z = (v-o for v, o in zip(xyz, origin))
        height, length, width = source.shape
        mapping = np.asarray([material(n) for n in source_palette], dtype=np.uint16)
        target = blocks[y:y+height, z:z+length, x:x+width]
        if target.shape != source.shape:
            raise ValueError('Construccion fuera de los limites del mundo')
        mask = source != 0
        target[mask] = mapping[source[mask]]

    def fill(x0, y0, z0, x1, y1, z1, name):
        blocks[y0-origin[1]:y1-origin[1]+1, z0-origin[2]:z1-origin[2]+1,
               x0-origin[0]:x1-origin[0]+1] = material(name)

    # Plataforma central y dos ramales a las entradas de las construcciones.
    fill(-207, 79, 116, 207, 80, 136, 'minecraft:black_terracotta')
    fill(-154, 79, 25, -136, 80, 125, 'minecraft:black_terracotta')
    fill(136, 79, 25, 154, 80, 125, 'minecraft:black_terracotta')
    fill(-20, 79, 105, 20, 80, 145, 'minecraft:black_terracotta')
    fill(-200, 79, -2, -90, 80, 36, 'minecraft:black_terracotta')
    # Base discreta bajo el escenario del End, sin las colinas de hormigon.
    for z in range(-95, 104):
        for x in range(40, 251):
            if ((x-145)/105)**2 + ((z-4)/100)**2 <= 1:
                fill(x, 79, z, x, 80, z, 'minecraft:black_terracotta')

    nether_palette, nether = load_schematic(OUTPUT / 'GuardianNPv3-92.schem')
    nether_palette = [rotate_half(n) for n in nether_palette]
    nether = nether[:, ::-1, ::-1].copy()
    # El marco original tiene 15x23 bloques. Activar su interior de 13x21.
    nether_palette.append('minecraft:nether_portal[axis=x]')
    nether[3:24, 6, 47:60] = len(nether_palette)-1
    paste(nether_palette, nether, (-198, 80, 0))

    end_palette, end = world_box(downloads/'Mapa_Endportal.zip', (-118, 69, -6, 92, 261, 188))
    # La torre empieza en Z=62. Excluir el fondo situado detras de ella,
    # conservando el suelo negro y la ornamentacion del primer plano.
    removed = int(np.count_nonzero(end[:, :66, :]))
    end[:, :66, :] = 0
    for index, name in enumerate(end_palette):
        basic = name.split('[')[0].removeprefix('minecraft:')
        # Vegetacion del mundo natural fuera de la construccion seleccionada.
        if basic in ('grass_block', 'dirt', 'water', 'tall_grass', 'grass', 'short_grass') or basic.endswith(('_leaves', '_log')):
            removed += int(np.count_nonzero(end == index))
            end[end == index] = 0
    sanitize(end_palette, end)
    paste(end_palette, end, (40, 80, -95))

    # Luz y bordes bajos en las pasarelas de terracota.
    for x in range(-198, 199, 18):
        for z in (116, 136):
            fill(x, 81, z, x, 81, z, 'minecraft:polished_blackstone_wall')
            fill(x, 82, z, x, 82, z, 'minecraft:lantern[hanging=false,waterlogged=false]')
    moved_palette, moved = separate_portal_scene(palette, blocks, origin)
    write_world(OUTPUT/'portales_astrales/region', palette, blocks, origin)
    write_world(OUTPUT/'portales_astrales/region', moved_palette, moved, NETHER_MOVED_ORIGIN)
    schematic(OUTPUT/'portales-astrales.schem', palette, blocks)
    return {'mundo': 'portales_astrales', 'llegada': [145.5, 81, 70.5, 180, 0],
            'end': [145.5, 81, 70.5, 180, 0], 'nether': [-2192.5, 81, -1.5, 0, 0],
            'bloques_de_fondo_excluidos': removed, 'origen': origin,
            'dimensiones_yzx': list(blocks.shape)}


def prepare_sanctuary():
    palette, blocks = load_litematic(OUTPUT/'interstellar.litematic')
    sanitize(palette, blocks)
    write_world(OUTPUT/'santuario_interstellar/region', palette, blocks, (-152, 48, -152))
    schematic(OUTPUT/'santuario-interstellar.schem', palette, blocks)
    # El punto se selecciona despues de inspeccionar la superficie original.
    return palette, blocks


def world_metadata(world, spawn):
    """Metadatos de Paper 26.1, con generacion vacia fuera de las construcciones."""
    base = ROOT/'.local/asw-native/server/world'
    template = base/'dimensions/minecraft/overworld/data'

    def read(path):
        return NBT(gzip.decompress(path.read_bytes()), typed=True).root()

    def write(relative, tree):
        path = OUTPUT/world/relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(gzip.compress(bytes([tree[0]]) + nbt_string('') + nbt_payload(tree), mtime=0))

    x, y, z, yaw, pitch = spawn
    root = read(base/'level.dat')
    data = root[1]['Data'][1]
    data['LevelName'] = (8, world)
    data['initialized'] = (1, 1)
    data['spawn'] = (10, {'pos': (11, [math.floor(x), y, math.floor(z)]),
                         'yaw': (5, yaw), 'pitch': (5, pitch),
                         'dimension': (8, 'minecraft:' + world)})
    data['paperSpawnDimension'] = (8, 'minecraft:' + world)
    data['DataPacks'] = (10, {'Enabled': (9, [(8, 'vanilla'), (8, 'file/bukkit'), (8, 'paper')]),
                             'Disabled': (9, [])})
    write('level.dat', root)
    generator = read(template/'minecraft/world_gen_settings.dat')
    dimensions = generator[1]['data'][1]['dimensions'][1]
    dimensions['minecraft:overworld'][1]['generator'] = (10, {
        'type': (8, 'minecraft:flat'), 'settings': (10, {
            'layers': (9, [(10, {'block': (8, 'minecraft:air'), 'height': (3, 1)})]),
            'features': (1, 0), 'lakes': (1, 0), 'biome': (8, 'minecraft:the_void')})})
    generator[1]['data'][1]['generate_structures'] = (1, 0)
    write('data/minecraft/world_gen_settings.dat', generator)
    overrides = read(template/'paper/level_overrides.dat')
    overrides[1]['data'][1]['spawn'] = (10, {
        'pos': (11, [math.floor(x), y, math.floor(z)]), 'yaw': (5, yaw), 'pitch': (5, pitch)})
    overrides[1]['data'][1]['difficulty_settings'] = (10, {
        'locked': (1, 0), 'difficulty': (8, 'hard'), 'hardcore': (1, 0)})
    write('data/paper/level_overrides.dat', overrides)
    rules = read(template/'minecraft/game_rules.dat')
    for name in ('spawn_mobs', 'spawn_monsters', 'mob_griefing', 'block_explosion_drop_decay',
                 'tnt_explodes', 'projectiles_can_break_blocks', 'advance_weather'):
        rules[1]['data'][1]['minecraft:' + name] = (1, 0)
    rules[1]['data'][1]['minecraft:keep_inventory'] = (1, 1)
    rules[1]['data'][1]['minecraft:pvp'] = (1, 0)
    rules[1]['data'][1]['minecraft:random_tick_speed'] = (3, 0)
    write('data/minecraft/game_rules.dat', rules)


def main():
    downloads = Path.home()/'Downloads'
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for zip_name in ('mapa_Santuari_Mazmorra.zip', 'nether_portal_Guardianes.zip'):
        with ZipFile(downloads/zip_name) as archive:
            for name in archive.namelist():
                if name.endswith(('.schem', '.litematic')):
                    (OUTPUT/Path(name).name).write_bytes(archive.read(name))
    report = prepare_portals(downloads)
    (OUTPUT/'portales-informe.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report), flush=True)
    palette, blocks = prepare_sanctuary()
    world_metadata('portales_astrales', (145.5, 81, 70.5, 180, 0))
    world_metadata('santuario_interstellar', (34.5, 180, 40.5, -56, 0))
    print('Santuario convertido', blocks.shape, len(palette), flush=True)
    # La entrada se exporta de la construccion original de Gates of Hell.
    entry_palette, entry = world_box(downloads/'Entrada_Del_nether.zip', (-186, 0, -50, 180, 255, 68))
    sanitize(entry_palette, entry)
    occupied = np.nonzero(entry)
    if not len(occupied[0]):
        raise ValueError('La entrada del Nether esta vacia')
    y0, z0, x0 = (int(a.min()) for a in occupied)
    y1, z1, x1 = (int(a.max())+1 for a in occupied)
    entry = entry[y0:y1, z0:z1, x0:x1]
    schematic(OUTPUT/'entrada-del-nether.schem', entry_palette, entry)
    print('Entrada Nether', entry.shape, 'origen original', (x0-186, y0, z0-50), flush=True)


if __name__ == '__main__':
    main()
