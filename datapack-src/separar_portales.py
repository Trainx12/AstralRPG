"""Separar los portales sobre un respaldo real, conservando el NBT restante."""
from copy import deepcopy
import gzip
import json
from pathlib import Path
import struct
from zipfile import ZipFile
import zlib

import numpy as np

from mapas import NBT, nbt_payload, nbt_string
from mapas_exploracion import records, repack
from portales_mapas import (NETHER_BOUNDS, NETHER_MOVED_ORIGIN, OUTPUT,
                            pack_padded, separate_portal_scene, state_name, state_tag,
                            unpack_padded, world_box, write_world)

REVISION = OUTPUT/'separacion'
ORIGIN = (-224, 64, -104)


def decode_record(record):
    kind, payload = record[4], record[5:]
    if kind == 2:
        payload = zlib.decompress(payload)
    elif kind == 1:
        payload = gzip.decompress(payload)
    elif kind != 3:
        raise ValueError(f'Compresion desconocida: {kind}')
    return NBT(payload, typed=True).root()


def encode_record(tree):
    raw = bytes([tree[0]]) + nbt_string('') + nbt_payload(tree)
    payload = zlib.compress(raw)
    return struct.pack('>I', len(payload)+1) + b'\x02' + payload


def palette_name(tag):
    entry = tag[1]
    return state_name({'Name': entry['Name'][1],
                       'Properties': {k: v[1] for k, v in entry.get('Properties', (10, {}))[1].items()}})


def move_position(x, y, z):
    return -2338-x, y, 33-z


def inside_nether(x, y, z):
    x0, y0, z0, x1, y1, z1 = NETHER_BOUNDS
    return x0 <= x <= x1 and y0 <= y <= y1 and z0 <= z <= z1


def rewrite_regions(source, destination, palette, blocks):
    lookup = {name: i for i, name in enumerate(palette)}
    moved_entities = []
    changed_chunks = 0
    for path in source.glob('r.*.mca'):
        packed = []
        for slot, timestamp, record in records(path.read_bytes()):
            tree = decode_record(record)
            root = tree[1]
            chunk = root['Level'][1] if 'Level' in root else root
            cx, cz = chunk['xPos'][1], chunk['zPos'][1]
            modified = False
            for tag in chunk.get('sections', (9, []))[1]:
                section = tag[1]
                sy = section['Y'][1] * 16
                ax, bx = max(ORIGIN[0], cx*16), min(ORIGIN[0]+blocks.shape[2], cx*16+16)
                az, bz = max(ORIGIN[2], cz*16), min(ORIGIN[2]+blocks.shape[1], cz*16+16)
                ay, by = max(ORIGIN[1], sy), min(ORIGIN[1]+blocks.shape[0], sy+16)
                if ax >= bx or az >= bz or ay >= by or 'block_states' not in section:
                    continue
                state = section['block_states'][1]
                entries = state['palette'][1]
                mapping = []
                for entry in entries:
                    name = palette_name(entry)
                    if name not in lookup:
                        lookup[name] = len(palette)
                        palette.append(name)
                    mapping.append(lookup[name])
                indices = (np.zeros(4096, dtype=np.uint16) if len(entries) == 1 else
                           unpack_padded(state['data'][1], 4096, max(4, (len(entries)-1).bit_length())))
                original = np.asarray(mapping, dtype=np.uint16)[indices].reshape(16, 16, 16)
                updated = original.copy()
                updated[ay-sy:by-sy, az-cz*16:bz-cz*16, ax-cx*16:bx-cx*16] = blocks[
                    ay-ORIGIN[1]:by-ORIGIN[1], az-ORIGIN[2]:bz-ORIGIN[2], ax-ORIGIN[0]:bx-ORIGIN[0]]
                if np.array_equal(original, updated):
                    continue
                unique, inverse = np.unique(updated.reshape(-1), return_inverse=True)
                state.clear()
                state['palette'] = (9, [state_tag(palette[int(i)]) for i in unique])
                if len(unique) > 1:
                    state['data'] = (12, pack_padded(inverse, max(4, (len(unique)-1).bit_length())))
                modified = True
            retained = []
            for entity in chunk.get('block_entities', (9, []))[1]:
                data = entity[1]
                x, y, z = (data[k][1] for k in ('x', 'y', 'z'))
                if inside_nether(x, y, z):
                    moved = deepcopy(entity)
                    for key, value in zip(('x', 'y', 'z'), move_position(x, y, z)):
                        moved[1][key] = (3, value)
                    moved_entities.append(moved)
                    modified = True
                else:
                    retained.append(entity)
            if modified:
                chunk['block_entities'] = (9, retained)
                # Minecraft reconstruye los mapas de altura y luz al cargar.
                chunk.pop('Heightmaps', None)
                chunk['isLightOn'] = (1, 0)
                record = encode_record(tree)
                changed_chunks += 1
            packed.append((slot, timestamp, record))
        (destination/path.name).write_bytes(repack(packed))
    return changed_chunks, moved_entities


def append_entities(directory, entities):
    for path in directory.glob('r.*.mca'):
        packed = []
        for slot, timestamp, record in records(path.read_bytes()):
            tree = decode_record(record)
            chunk = tree[1]
            matching = [e for e in entities if (e[1]['x'][1]//16, e[1]['z'][1]//16) ==
                        (chunk['xPos'][1], chunk['zPos'][1])]
            if matching:
                chunk['block_entities'] = (9, matching)
                record = encode_record(tree)
            packed.append((slot, timestamp, record))
        path.write_bytes(repack(packed))


def main():
    backup = REVISION/'respaldo/region'
    destination = REVISION/'region'
    destination.mkdir(parents=True, exist_ok=True)
    archive = REVISION/'respaldo.zip'
    with ZipFile(archive, 'w') as output:
        output.writestr('world/level.dat', b'')
        for path in backup.glob('*.mca'):
            output.write(path, 'world/region/'+path.name)
    palette, blocks = world_box(archive, (-224, 64, -104, 271, 287, 151))
    before = blocks.copy()
    moved_palette, moved = separate_portal_scene(palette, blocks, ORIGIN)
    if np.count_nonzero(moved) < 10000:
        raise ValueError('No se encontro la construccion del Nether esperada')
    changed, entities = rewrite_regions(backup, destination, palette, blocks)
    far = REVISION/'nether/region'
    write_world(far, moved_palette, moved, NETHER_MOVED_ORIGIN)
    if {p.name for p in far.glob('*.mca')} & {p.name for p in backup.glob('*.mca')}:
        raise ValueError('La nueva ubicacion pisaria una region existente')
    append_entities(far, entities)
    for path in far.glob('*.mca'):
        (destination/path.name).write_bytes(path.read_bytes())
    np.save(REVISION/'escena.npy', blocks)
    np.save(REVISION/'nether.npy', moved)
    report = {'chunks_modificados': changed, 'bloques_movidos': int(np.count_nonzero(moved)),
              'cambios_en_origen': int(np.count_nonzero(before != blocks)),
              'block_entities_trasladadas': len(entities), 'origen_nether': NETHER_MOVED_ORIGIN,
              'paleta': palette, 'paleta_nether': moved_palette}
    (REVISION/'informe.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print({k: v for k, v in report.items() if not k.startswith('paleta')})


if __name__ == '__main__':
    main()
