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
# Version de datos de Paper 26.1.2 en el servidor (leida de world/level.dat el 08/11/2026).
# Los mapas guardados en 26.2 (4903) solo usan bloques que ya existen en 26.1: se les baja el numero.
SERVER_DATA_VERSION = 4790
# Region del mundo principal: formato viejo (region/) o el de 26.x (dimensions/minecraft/overworld/region/).
REGION = re.compile(r'(?:dimensions/minecraft/overworld/)?(region|entities)/(r\.-?\d+\.-?\d+\.mca)')


def encode(tree):
    return bytes([tree[0]]) + nbt_string('') + nbt_payload(tree)


# Alcance de los selectores de mapas que conservan sus command blocks. Cada mini juego es su
# propio mundo, asi que alcanza con no salir de el: sin tope. Con 300 bloques Magma Run perdia el
# marcador que arma la torre al subir (y=357) y nunca terminaba de arrancar (08/11/2026).
RANGE = '0..'
# Texto JSON viejo con "true" entre comillas: en 26.x falla (y llena la consola cada tick).
TEXT_BOOL = re.compile(r'((?:"|\b)(?:bold|italic|underlined|strikethrough|obfuscated)"?\s*:\s*)"(true|false)"')


def local_selectors(command):
    """Que un command block del mapa solo toque a quien juega ahi (pedido del dueno, 08/11/2026).

    - @a/@r -> @p (el jugador que piso el boton o la placa).
    - `execute as/at @a` (chequeos repetidos para todos los del mapa) -> @a de ese mundo.
    - @e -> limitado al mundo del mapa (distance=0..): sin eso mata criaturas de otros mundos.
    - Un selector que ya tiene distance= se deja como esta.
    """
    pattern = re.compile(r'(?P<loop>execute (?:as|at) )?@(?P<kind>[aer])(?P<args>\[[^\]]*\])?')

    def fix(m):
        loop, kind, args = m.group('loop') or '', m.group('kind'), m.group('args') or ''
        if 'distance=' in args:
            return m.group(0)
        if kind == 'e' or (kind == 'a' and loop):
            inner = args[1:-1]
            return f"{loop}@{kind}[distance={RANGE}{',' + inner if inner else ''}]"
        return f'{loop}@p{args}'
    # El mapa pasa a aventura a todo el que no tenga `dev` (y le saca `dev` a todos menos a su
    # autor). Skript marca a los OP con astral.op dentro de los mini juegos.
    command = TEXT_BOOL.sub(r'\1\2', command)
    return pattern.sub(fix, command).replace('tag=!dev]', 'tag=!dev,tag=!astral.op]')


def keep_logic(tree, rewrite=None):
    """Para mapas que necesitan sus command blocks: solo se reescriben los comandos.

    Sin `rewrite`, se limitan los selectores por distancia (Color Escape). Con datapack
    adaptado (minijuegos_datapack.Adapter.command) se usan sus namespaces y puntajes.
    """
    rewrite = rewrite or local_selectors
    root = tree[1]
    chunk = root['Level'][1] if 'Level' in root else root
    changed = 0
    for key in ('block_entities', 'TileEntities'):
        for _, data in chunk.get(key, (9, []))[1]:
            if 'Command' in data:
                new = rewrite(data['Command'][1])
                if new != data['Command'][1]:
                    data['Command'] = (8, new)
                    changed += 1
    return changed


def clean_region(raw, keep_commands=False, rewrite=None):
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
        if keep_commands:
            keep_logic(tree, rewrite)
        else:
            sanitize(tree)
        version = tree[1].get('DataVersion')
        if version and version[1] > SERVER_DATA_VERSION:
            tree[1]['DataVersion'] = (3, SERVER_DATA_VERSION)
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


def prepare(source, destination, world, keep_commands=False, rewrite=None, source_dim=None):
    """Lista permitida: level.dat y regiones; excluye jugadores, entidades y datapacks."""
    if not destination.resolve().is_relative_to((ROOT / '.local').resolve()):
        raise ValueError('Los mundos de terceros solo pueden escribirse en .local')
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(source) as src, zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED) as dst:
        level = next(n for n in src.namelist() if n.endswith('/level.dat') and '__MACOSX' not in n)
        prefix = level[:-len('level.dat')]
        tree = NBT(gzip.decompress(src.read(level)), typed=True).root()
        data = tree[1]['Data'][1]
        for field in ('Player', 'DataPacks', 'CustomBossEvents', 'ScheduledEvents'):
            data.pop(field, None)
        data['LevelName'] = (8, world)
        if data.get('DataVersion', (3, 0))[1] > SERVER_DATA_VERSION:
            data['DataVersion'] = (3, SERVER_DATA_VERSION)
            version = data['Version'][1]
            version['Id'] = (3, SERVER_DATA_VERSION)
            version['Name'] = (8, '26.1.2')
        data['GameType'] = (3, 0)
        # El formato 1.21.11 usa game_rules; 1.12 requiere cadenas en GameRules.
        if 'game_rules' in data:
            data['game_rules'][1]['minecraft:command_blocks_work'] = (1, int(keep_commands))
            data['game_rules'][1]['minecraft:spawn_mobs'] = (1, 0)
            data['game_rules'][1]['minecraft:keep_inventory'] = (1, 1)
        dst.writestr(f'{world}/level.dat', gzip.compress(encode(tree), mtime=0))
        count = 0
        for name in src.namelist():
            relative = name.removeprefix(prefix)
            pattern = re.compile(rf'{source_dim}/(region|entities)/(r\.-?\d+\.-?\d+\.mca)') if source_dim else REGION
            match = pattern.fullmatch(relative) if name.startswith(prefix) else None
            # Entidades solo en los mapas que conservan su logica (marcos, mobs del puzzle).
            if match and (match.group(1) == 'region' or keep_commands):
                if '..' in PurePosixPath(relative).parts:
                    raise ValueError('Ruta invalida')
                # Entidades tambien: baja de version (mapas 26.2) sin tocar su contenido.
                raw = clean_region(src.read(name), keep_commands, rewrite)
                dst.writestr(f'{world}/{match.group(1)}/{match.group(2)}', raw)
                count += 1
        if not count:
            raise ValueError('No se encontraron regiones')
    return count


def main():
    folder = ROOT / '.local/mapas'
    import sys
    maps = [('parkour_spiral.zip', 'parkour_spiral'), ('arenapvp_3.zip', 'arenas_tft'),
            ('parkour_spiral2.zip', 'parkour_spiral2'), ('parkour_paradise3.zip', 'parkour_paradise3'),
            ('dropper.zip', 'dropper_facil'), ('dropper_h4rs.zip', 'dropper_h4rs'),
            ('colorescape.zip', 'colorescape'), ('battleship.zip', 'battleship'),
            ('towerdefence.zip', 'towerdefence'), ('towerdefence.zip', 'towerdefence_end'),
            ('magmarun.zip', 'magmarun')]
    dims = {'towerdefence_end': 'DIM1'}     # el End del Tower Defence es su propio mundo
    keep = {'colorescape', 'magmarun'}  # necesitan sus command blocks (selectores reescritos)
    from minijuegos_datapack import MAPS as DATAPACK_MAPS, Adapter
    only = set(sys.argv[1:])
    for filename, world in maps:
        if only and world not in only:
            continue
        rewrite = None
        owner = 'towerdefence' if world == 'towerdefence_end' else world
        if owner in DATAPACK_MAPS:   # mapas con datapack adaptado: comandos con sus namespaces
            c = DATAPACK_MAPS[owner]
            rewrite = Adapter(owner, folder / filename, c['prefix'], c.get('console'), c.get('dims'),
                              c.get('players_tag', False), c.get('keep_teams', False)).command
        count = prepare(folder / filename, folder / 'subir' / (world + '.zip'), world,
                        world in keep or rewrite is not None, rewrite, dims.get(world))
        print(f'{world}: {count} regiones preparadas en .local/mapas/subir/{world}.zip')


if __name__ == '__main__':
    main()
