"""Preparar copias privadas de mundos de terceros, sin extraer rutas del ZIP.

python minijuegos_mapas.py  # lee .local/mapas y escribe .local/mapas/subir
No contiene ni publica geometria de terceros.
"""
import gzip
import math
from pathlib import Path, PurePosixPath
import re
import struct
import zipfile
import zlib

from mapas import NBT, nbt_payload, nbt_string, sanitize

ROOT = Path(__file__).resolve().parent.parent


def encode(tree):
    return bytes([tree[0]]) + nbt_string('') + nbt_payload(tree)


def clean_region(raw):
    header = bytearray(raw[:8192])
    records = []
    sector = 2
    for slot in range(1024):
        offset = int.from_bytes(raw[slot * 4:slot * 4 + 3], 'big') * 4096
        if not offset:
            continue
        length = int.from_bytes(raw[offset:offset + 4], 'big')
        compression = raw[offset + 4]
        payload = raw[offset + 5:offset + 4 + length]
        if compression == 2:
            payload = zlib.decompress(payload)
        elif compression == 1:
            payload = gzip.decompress(payload)
        elif compression != 3:
            raise ValueError(f'Compresion de region no soportada: {compression}')
        tree = NBT(payload, typed=True).root()
        sanitize(tree)
        chunk = tree[1].get('Level', tree)[1]
        # Los bloques numericos del mapa 1.12 no tienen paleta moderna.
        for _, section in chunk.get('Sections', (9, []))[1]:
            if 'Blocks' in section:
                blocks = bytearray(section['Blocks'][1])
                add = bytearray(section.get('Add', (7, bytes(2048)))[1])
                for i, low in enumerate(blocks):
                    high = (add[i // 2] >> (4 * (i % 2))) & 15
                    if low + high * 256 in (52, 137, 210, 211, 255):
                        blocks[i] = 98  # stone bricks: spawners y command/structure blocks
                        add[i // 2] &= ~(15 << (4 * (i % 2)))
                section['Blocks'] = (7, bytes(blocks))
                if 'Add' in section:
                    section['Add'] = (7, bytes(add))
        data = zlib.compress(encode(tree))
        record = struct.pack('>I', len(data) + 1) + b'\x02' + data
        sectors = math.ceil(len(record) / 4096)
        if sectors > 255:
            raise ValueError('Chunk demasiado grande')
        header[slot * 4:slot * 4 + 4] = sector.to_bytes(3, 'big') + bytes([sectors])
        records.append(record.ljust(sectors * 4096, b'\0'))
        sector += sectors
    return bytes(header) + b''.join(records)


def prepare(source, destination, world):
    """Lista permitida: level.dat y regiones; excluye jugadores, entidades y datapacks."""
    if not destination.resolve().is_relative_to((ROOT / '.local').resolve()):
        raise ValueError('Los mundos de terceros solo pueden escribirse en .local')
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(source) as src, zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED) as dst:
        level = next(n for n in src.namelist() if n.endswith('/level.dat'))
        prefix = level[:-len('level.dat')]
        tree = NBT(gzip.decompress(src.read(level)), typed=True).root()
        data = tree[1]['Data'][1]
        for field in ('Player', 'DataPacks', 'CustomBossEvents', 'ScheduledEvents'):
            data.pop(field, None)
        data['LevelName'] = (8, world)
        data['GameType'] = (3, 0)
        # El formato 1.21.11 usa game_rules; 1.12 requiere cadenas en GameRules.
        if 'game_rules' in data:
            data['game_rules'][1]['minecraft:command_blocks_work'] = (1, 0)
            data['game_rules'][1]['minecraft:spawn_mobs'] = (1, 0)
            data['game_rules'][1]['minecraft:keep_inventory'] = (1, 1)
        dst.writestr(f'{world}/level.dat', gzip.compress(encode(tree), mtime=0))
        count = 0
        for name in src.namelist():
            relative = name.removeprefix(prefix)
            if name.startswith(prefix) and re.fullmatch(r'region/r\.-?\d+\.-?\d+\.mca', relative):
                if '..' in PurePosixPath(relative).parts:
                    raise ValueError('Ruta invalida')
                dst.writestr(f'{world}/{relative}', clean_region(src.read(name)))
                count += 1
        if not count:
            raise ValueError('No se encontraron regiones')
    return count


def main():
    folder = ROOT / '.local/mapas'
    for filename, world in [('parkour_spiral.zip', 'parkour_spiral'), ('arenapvp_3.zip', 'arenas_tft')]:
        count = prepare(folder / filename, folder / 'subir' / (world + '.zip'), world)
        print(f'{world}: {count} regiones preparadas en .local/mapas/subir/{world}.zip')


if __name__ == '__main__':
    main()
