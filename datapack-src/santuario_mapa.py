"""Convertir el schematic privado FreeMap9 sin importar el mundo ni sus entidades."""
import argparse
from copy import deepcopy
import gzip
import json
import os
from pathlib import Path
import subprocess
import shutil
import struct
import zlib

import numpy as np

from mapas import NBT, nbt_payload, nbt_string
from mapas_exploracion import repack
from portales_mapas import world_metadata

ROOT = Path(__file__).resolve().parent.parent


def write_nbt(path, tree):
    path.write_bytes(gzip.compress(bytes([tree[0]])+nbt_string('')+nbt_payload(tree), mtime=0))


def legacy_chunks(schematic, destination):
    plain = NBT(gzip.decompress(schematic.read_bytes())).root()
    typed = NBT(gzip.decompress(schematic.read_bytes()), typed=True).root()[1]
    shape = (plain['Height'], plain['Length'], plain['Width'])
    blocks = np.frombuffer(plain['Blocks'], dtype=np.uint8).copy().reshape(shape)
    data = np.frombuffer(plain['Data'], dtype=np.uint8).reshape(shape)
    if 'AddBlocks' in plain:
        raise ValueError('Se requieren IDs extendidos: no convertir silenciosamente.')
    # Command blocks, spawners, moving pistons and structure blocks are inert here.
    blocks[np.isin(blocks, [36, 52, 137, 210, 211, 255])] = 98
    origin = tuple(plain[f'WEOrigin{axis}'] for axis in 'XYZ')
    ox, oy, oz = origin
    height, length, width = shape
    destination.mkdir(parents=True, exist_ok=True)
    for cz in range(oz//16, (oz+length-1)//16+1):
        for cx in range(ox//16, (ox+width-1)//16+1):
            sections = []
            for sy in range(oy//16, (oy+height-1)//16+1):
                cube = np.zeros((16, 16, 16), dtype=np.uint8)
                meta = cube.copy()
                ax, bx = max(ox, cx*16), min(ox+width, cx*16+16)
                az, bz = max(oz, cz*16), min(oz+length, cz*16+16)
                ay, by = max(oy, sy*16), min(oy+height, sy*16+16)
                to = np.s_[ay-sy*16:by-sy*16, az-cz*16:bz-cz*16, ax-cx*16:bx-cx*16]
                source = np.s_[ay-oy:by-oy, az-oz:bz-oz, ax-ox:bx-ox]
                cube[to], meta[to] = blocks[source], data[source]
                if not np.any(cube):
                    continue
                meta = meta.reshape(-1)
                nibble = (meta[::2] & 15) | ((meta[1::2] & 15) << 4)
                sections.append((10, {'Y': (1, sy), 'Blocks': (7, cube.tobytes()),
                                     'Data': (7, nibble.tobytes()),
                                     'BlockLight': (7, bytes(2048)), 'SkyLight': (7, bytes(2048))}))
            if not sections:
                continue
            tiles = []
            for original in typed.get('TileEntities', (9, []))[1]:
                entity = deepcopy(original)
                value = entity[1]
                x, y, z = (value[k][1]+o for k, o in zip('xyz', origin))
                if x//16 != cx or z//16 != cz:
                    continue
                if any(k in value for k in ('Command', 'SpawnData', 'SpawnPotentials')):
                    continue
                for k, n in zip('xyz', (x, y, z)):
                    value[k] = (3, n)
                for k in ('Items', 'LootTable', 'LootTableSeed'):
                    value.pop(k, None)
                tiles.append(entity)
            level = {'xPos': (3, cx), 'zPos': (3, cz), 'LastUpdate': (4, 0),
                     'InhabitedTime': (4, 0), 'TerrainPopulated': (1, 1),
                     'LightPopulated': (1, 0), 'Sections': (9, sections),
                     'Biomes': (7, bytes([127])*256), 'HeightMap': (11, [0]*256),
                     'Entities': (9, []), 'TileEntities': (9, tiles)}
            write_nbt(destination/f'{cx}.{cz}.nbt',
                      (10, {'DataVersion': (3, 1343), 'Level': (10, level)}))
    return origin, shape


def package(directory, destination):
    regions = {}
    destination.mkdir(parents=True, exist_ok=True)
    for path in directory.glob('*.nbt'):
        tree = NBT(gzip.decompress(path.read_bytes()), typed=True).root()
        chunk = tree[1]
        if 'Level' in chunk:
            raise ValueError('La conversion no produjo un chunk moderno.')
        chunk.pop('Heightmaps', None)
        chunk['isLightOn'] = (1, 0)
        cx, cz = chunk['xPos'][1], chunk['zPos'][1]
        payload = zlib.compress(bytes([tree[0]])+nbt_string('')+nbt_payload(tree))
        record = struct.pack('>I', len(payload)+1)+b'\x02'+payload
        regions.setdefault((cx//32, cz//32), []).append(((cz%32)*32+cx%32, bytes(4), record))
    for (rx, rz), records in regions.items():
        (destination/f'r.{rx}.{rz}.mca').write_bytes(repack(sorted(records)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--schematic', type=Path, required=True)
    parser.add_argument('--java', type=Path, required=True)
    parser.add_argument('--server', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise SystemExit('La salida ya existe; conservarla y elegir otra.')
    origin, shape = legacy_chunks(args.schematic, args.out/'legacy')
    jars = sorted(args.server.glob('versions/*/paper-*.jar')) + sorted((args.server/'libraries').rglob('*.jar'))
    classpath = os.pathsep.join(str(p.resolve()) for p in jars)
    command = ['-Xmx1536M', '-cp', classpath, str(ROOT/'datapack-src/ConvertLegacyChunks.java'),
               str((args.out/'legacy').resolve()), str((args.out/'modern').resolve())]
    argfile = args.out/'java-args.txt'
    argfile.write_text('\n'.join('"'+v.replace('\\', '/')+'"' for v in command), encoding='utf-8')
    result = subprocess.run([str(args.java), '@'+str(argfile.resolve())],
                            capture_output=True, text=True, cwd=ROOT)
    (args.out/'conversion.log').write_text(result.stdout+'\n'+result.stderr, encoding='utf-8')
    if result.returncode:
        raise SystemExit('Conversion fallida; revisar conversion.log. No instalar.')
    package(args.out/'modern', args.out/'region')
    world = args.out/'santuario_freemap9'
    shutil.copytree(args.out/'region', world/'region')
    world_metadata('santuario_freemap9', (33.5, 103, -40.5, 180, 0),
                   base=args.server/'world', destination=world)
    print(json.dumps({'origin': origin, 'shape_yzx': shape,
                      'chunks': len(list((args.out/'modern').glob('*.nbt')))}))


if __name__ == '__main__':
    main()
