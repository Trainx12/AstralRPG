"""Preparar Reino y Cavernas para explorar, conservando los chunks originales.

Los ZIP de terceros y resultados permanecen en .local, fuera del repositorio.
No instala mundos, crea plataformas, coloca NPCs ni modifica mapas existentes.
"""
import argparse
from collections import deque
import gzip
import hashlib
import json
import math
from pathlib import Path
import re
import struct
import zipfile
import zlib

from mapas import NBT, block, nbt_string, nbt_payload
from inspeccionar_expediciones import get as inspect_block

ROOT = Path(__file__).resolve().parent.parent
DEFAULT = ROOT / '.local/mapas/astral-nuevos'
DEFINITIONS = {
    'reino': dict(file='medivalspawn.zip', name='Reino de las Mazmorras',
                  spawn=(5.5, 67, 0.5, 180, 0),
                  reason='Sendero original del bosque, orientado hacia el sector norte del reino.'),
    'cavernas': dict(file='coalcave.zip', name='Cavernas de las Mazmorras',
                     spawn=(172.5, 102, 89.5, 0, 0),
                     reason='Camino original de tierra junto a la llegada del autor, mirando al interior.'),
    'exp_desierto': dict(file='mapa_desierto.zip', name='Expedicion al Desierto',
                        spawn=(180.233,102,134.266,-124.8,0),
                        reason='Paso elevado original elegido por el dueno en su captura, orientado hacia el recorrido.'),
    'exp_hielo': dict(file='ice-lobby.zip', name='Expedicion a la Cumbre',
                     spawn=(8.5,65,8.5,180,0),
                     reason='Plaza de ladrillos original, bajo las barreras antiguas del mapa.'),
    'exp_santuario': dict(file='mapa_santuario.zip', name='Expedicion al Santuario',
                         spawn=(26.5,103,-31.5,180,0), component=True, inert_commands=True,
                         reason='Paseo original de madera junto al jardin, sin usar el spawn enterrado del autor.'),
}
AIR = {'minecraft:air', 'minecraft:cave_air', 'minecraft:void_air', 'minecraft:light'}
FLOORS = {'minecraft:' + name for name in (
    'dirt', 'dirt_path', 'rooted_dirt', 'coarse_dirt', 'packed_mud',
    'grass_block', 'stone', 'cobblestone', 'mossy_cobblestone', 'andesite',
    'granite', 'diorite', 'stone_bricks', 'mossy_stone_bricks', 'mud_bricks')}
FLOORS.update('minecraft:'+name for name in (
    'cracked_stone_bricks','snow_block','white_wool','oak_planks','spruce_planks',
    'sand','sandstone','smooth_sandstone','cut_sandstone','quartz_block','white_terracotta',
    'smooth_stone','bone_block','gold_ore','nether_quartz_ore','light_gray_terracotta',
    'birch_log','birch_planks','orange_glazed_terracotta','brown_glazed_terracotta'))
LOGIC = {'minecraft:' + name for name in (
    'command_block', 'chain_command_block', 'repeating_command_block',
    'spawner', 'trial_spawner', 'structure_block', 'jigsaw')}


def records(raw):
    """Leer los registros completos, incluyendo compresion, sin reescribir NBT."""
    if not raw:
        return
    if len(raw) < 8192:
        raise ValueError('Cabecera de region incompleta')
    for slot in range(1024):
        sector = int.from_bytes(raw[slot*4:slot*4+3], 'big')
        size = raw[slot*4+3]
        if not sector:
            continue
        offset = sector * 4096
        # Algunos editores omiten el relleno del ultimo sector del archivo.
        if sector < 2 or not size or offset + 5 > len(raw):
            raise ValueError('Sector fuera de la region')
        length = int.from_bytes(raw[offset:offset+4], 'big')
        if length < 1 or length + 4 > size*4096 or offset+4+length>len(raw):
            raise ValueError('Longitud de chunk invalida')
        record = raw[offset:offset+4+length]
        yield slot, raw[4096+slot*4:4100+slot*4], record


def decode(record):
    compression, payload = record[4], record[5:]
    if compression == 2:
        payload = zlib.decompress(payload)
    elif compression == 1:
        payload = gzip.decompress(payload)
    elif compression != 3:
        raise ValueError(f'Compresion no soportada: {compression}')
    tree = NBT(payload).root()
    return tree.get('Level', tree)


def repack(selected):
    header = bytearray(8192)
    parts = []
    sector = 2
    for slot, timestamp, record in selected:
        count = (len(record)+4095)//4096
        if count > 255:
            raise ValueError('Registro demasiado grande')
        header[slot*4:slot*4+4] = sector.to_bytes(3,'big') + bytes([count])
        header[4096+slot*4:4100+slot*4] = timestamp
        parts.append(record.ljust(count*4096,b'\0'))
        sector += count
    return bytes(header)+b''.join(parts)


def get_block(chunks, x, y, z):
    return inspect_block(chunks,x,y,z)


def safe(chunks, x, y, z):
    return (get_block(chunks,x,y-1,z) in FLOORS and
            all(get_block(chunks,x,y+h,z) in AIR for h in range(3)))


def arrival_audit(chunks, spawn):
    x,y,z = map(math.floor,spawn[:3])
    footprint = []
    for dx in range(-1,2):
        for dz in range(-1,2):
            if not safe(chunks,x+dx,y,z+dz):
                raise ValueError(f'Llegada sin piso o espacio libre: {x+dx,y,z+dz}')
            footprint.append([x+dx,y-1,z+dz,get_block(chunks,x+dx,y-1,z+dz)])
    queue = deque([(x,y,z)])
    seen = {(x,y,z)}
    while queue:
        px,py,pz = queue.popleft()
        for dx,dz in ((-1,0),(1,0),(0,-1),(0,1)):
            nx,nz=px+dx,pz+dz
            if abs(nx-x)>24 or abs(nz-z)>24:
                continue
            for ny in (py,py+1,py-1):
                if abs(ny-y)>12 or (nx,ny,nz) in seen:
                    continue
                if safe(chunks,nx,ny,nz):
                    # No atravesar un bloque con la cabeza al subir/bajar.
                    high=max(py,ny)
                    if any(get_block(chunks,xx,high+1,zz) not in AIR
                           for xx,zz in ((px,pz),(nx,nz))):
                        continue
                    seen.add((nx,ny,nz));queue.append((nx,ny,nz))
                    break
    extent=max(abs(px-x)+abs(pz-z) for px,py,pz in seen)
    if len(seen)<30 or extent<12:
        raise ValueError('La llegada no conecta con un recorrido suficiente')
    return dict(piso_3x3=footprint, altura_libre=3, posiciones_conectadas=len(seen),
                alcance_manhattan=extent,
                nota='Comprobacion conservadora de bloques; falta revision visual en Minecraft.')


def prepare(key, base=DEFAULT):
    definition=DEFINITIONS[key]
    original=base/'originales'/definition['file']
    destination=base/'preparados'/key
    source_hash=hashlib.sha256(original.read_bytes()).hexdigest()
    chunks={}; nonempty=[]; regions={}; logical=[]; neutralized=[]
    with zipfile.ZipFile(original) as source:
        levelpaths=[n for n in source.namelist() if n.endswith('/level.dat')]
        if len(levelpaths)!=1:
            raise ValueError('Se esperaba un solo mundo')
        prefix=levelpaths[0][:-len('level.dat')]
        pattern=re.compile(re.escape(prefix)+r'(region|entities|poi)/r\.(-?\d+)\.(-?\d+)\.mca')
        for name in source.namelist():
            match=pattern.fullmatch(name)
            if not match:
                continue
            kind,rx,rz=match[1],int(match[2]),int(match[3])
            rows=list(records(source.read(name)))
            regions[kind,rx,rz]=rows
            if kind!='region':
                continue
            for slot,stamp,record in rows:
                chunk=decode(record)
                coord=(rx*32+slot%32,rz*32+slot//32)
                if (chunk['xPos'],chunk['zPos'])!=coord:
                    raise ValueError('Coordenada de chunk inconsistente')
                chunks[coord]=chunk
                palette={e['Name'] for s in chunk.get('sections',chunk.get('Sections',[]))
                         for e in s.get('block_states',{}).get('palette',s.get('Palette',[]))}
                legacy_ids={v for s in chunk.get('Sections',[]) for v in s.get('Blocks',b'')}
                if palette-AIR or legacy_ids-{0}:
                    nonempty.append(coord)
                if palette & LOGIC or legacy_ids & {137,210,211,52,255}:
                    logical.append([*coord,sorted(palette & LOGIC)])
        if logical and not definition.get('inert_commands'):
            raise ValueError(f'Hay logica original que requiere revisar sin reemplazar bloques: {logical}')
        if not nonempty:
            raise ValueError('Mapa vacio')
        # Excluir solo islas tecnicas desconectadas (marcador a 1000,1000 del Santuario).
        if definition.get('component'):
            occupied=set(nonempty); start=min(occupied,key=lambda c:c[0]**2+c[1]**2)
            component={start}; queue=deque([start])
            while queue:
                px,pz=queue.popleft()
                for dx in (-1,0,1):
                    for dz in (-1,0,1):
                        p=(px+dx,pz+dz)
                        if p in occupied and p not in component:component.add(p);queue.append(p)
            nonempty=sorted(component)
        # Todo el escenario mas un chunk de margen. No corta ninguna construccion.
        xmin=min(x for x,z in nonempty)-1; xmax=max(x for x,z in nonempty)+1
        zmin=min(z for x,z in nonempty)-1; zmax=max(z for x,z in nonempty)+1
        audit=arrival_audit(chunks,definition['spawn'])
        destination.mkdir(parents=True,exist_ok=True)
        digests={}; counts={}; selected_source={}
        for (kind,rx,rz),rows in regions.items():
            chosen=[r for r in rows if xmin<=rx*32+r[0]%32<=xmax and zmin<=rz*32+r[0]//32<=zmax]
            if not chosen:
                continue
            if definition.get('inert_commands') and kind=='region':
                inert=[]
                for slot,stamp,record in chosen:
                    root=NBT(zlib.decompress(record[5:]) if record[4]==2 else gzip.decompress(record[5:]) if record[4]==1 else record[5:],typed=True).root()
                    chunk=root[1].get('Level',root)[1] if 'Level' in root[1] else root[1]
                    changed=False
                    for _,entity in chunk.get('TileEntities',chunk.get('block_entities',(9,[])))[1]:
                        if 'Command' in entity:
                            neutralized.append([entity['x'][1],entity['y'][1],entity['z'][1]])
                            entity['Command']=(8,'')
                            for field in ('auto','powered','conditionMet'):
                                if field in entity:entity[field]=(1,0)
                            changed=True
                    if changed:
                        payload=zlib.compress(bytes([root[0]])+nbt_string('')+nbt_payload(root))
                        record=struct.pack('>I',len(payload)+1)+b'\x02'+payload
                    inert.append((slot,stamp,record))
                chosen=inert
            relative=f'{kind}/r.{rx}.{rz}.mca'
            target=destination/relative;target.parent.mkdir(exist_ok=True)
            raw=repack(chosen);target.write_bytes(raw)
            # Comparar todos los registros exportados, incluidos entidades y POI.
            assert list(records(raw))==chosen, f'Chunk modificado: {relative}'
            digests[relative]=hashlib.sha256(raw).hexdigest()
            counts[kind]=counts.get(kind,0)+len(chosen)
            selected_source[relative]=chosen
        zip_path=destination.parent/f'{key}-regiones.zip'
        with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as result:
            for relative in digests:
                result.write(destination/relative,relative)
        with zipfile.ZipFile(zip_path) as result:
            for relative,expected in selected_source.items():
                assert list(records(result.read(relative)))==expected
        assert hashlib.sha256(original.read_bytes()).hexdigest()==source_hash
    manifest=dict(mundo=key,nombre=definition['name'],original=definition['file'],
                  sha256_original=source_hash,spawn=definition['spawn'],motivo=definition['reason'],
                  limites_bloques=[xmin*16,zmin*16,xmax*16+15,zmax*16+15],
                  escenario_chunks=len(nonempty),chunks=counts,archivos_sha256=digests,
                  bloques_modificados=0,registros_identicos=not neutralized,comandos_desactivados=neutralized,aparicion=audit,
                  npcs='Pendientes de las posiciones que elija el dueno.',
                  instalado=False)
    (destination.parent/f'{key}-informe.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
    commands=ROOT/'build/mapas_exploracion'/key/'comandos.txt'
    commands.parent.mkdir(parents=True,exist_ok=True)
    commands.write_text(installation_commands(key,definition),encoding='utf-8')
    print(json.dumps(manifest,ensure_ascii=False),flush=True)
    return manifest


def installation_commands(key, definition):
    x,y,z,yaw,pitch=definition['spawn']
    return f'''# {definition['name']}: mapa aparte para explorar. Sin aldeanos ni combates configurados.
# Crear SOLO si el nombre {key} esta libre; conservar todos los mundos anteriores.
mv create {key} normal --world-type FLAT --no-structures --no-adjust-spawn --generator-settings {{"layers":[{{"block":"minecraft:air","height":1}}],"biome":"minecraft:the_void"}}
# Aplicar estas reglas al mundo vacio ANTES de subir el escenario:
mv modify {key} set gamemode adventure
mv modify {key} set difficulty peaceful
mv modify {key} set pvp false
mv modify {key} set allow-weather false
mv modify {key} set adjust-spawn false
mv gamerule set minecraft:spawn_mobs false {key}
mv gamerule set minecraft:random_tick_speed 0 {key}
mv gamerule set minecraft:fire_spread_radius_around_player 0 {key}
mv gamerule set minecraft:mob_griefing false {key}
mv gamerule set minecraft:keep_inventory true {key}
mv gamerule set minecraft:log_admin_commands false {key}
rg flag -w {key} __global__ build deny
rg flag -w {key} __global__ chest-access deny
rg flag -w {key} __global__ interact allow
rg flag -w {key} __global__ use deny
rg flag -w {key} __global__ pvp deny
# Apagar el servidor y subir SOLO .local/mapas/astral-nuevos/preparados/{key}/region/*.mca
# al NUEVO mundo world/dimensions/minecraft/{key}/region.
# Copiar tambien entities/ o poi/ si aparecen en el informe. Nunca Worlds -> Upload sobre world.
# Encender y fijar la llegada sobre el camino original:
# Orden comprobado en Multiverse 5.8.2: X,Y,Z,yaw,pitch.
mv setspawn {key}:{x},{y},{z},{yaw},{pitch}
# Revision: no mover jugadores automaticamente. Sustituir <jugador> cuando quiera explorar.
# execute in minecraft:{key} run minecraft:tp <jugador> {x} {y} {z} {yaw} {pitch}
# Volver al lobby: /spawn. No usar /setspawn: cambiaria Essentials.
# No ejecutar fill, setblock, //set, //paste ni crear plataformas.
'''


def generate_travel_commands():
    """Solo aldeanos de enlace. No crea entradas ni cambia las mazmorras."""
    path=ROOT/'build/mapas_exploracion/enlaces.txt'
    path.parent.mkdir(parents=True,exist_ok=True)
    lines=['# Generado por mapas_exploracion.py --enlaces.',
           '# Instalar los tres bloques NPC de mobs/mythic.py en mobs/astral.yml y ejecutar mm reload.',
           '# Expediciones y todos los guias abren ahora la interfaz de seis busquedas.',
           '# No ejecutar el montaje viejo de ambiente/expediciones ni crear plataformas.']
    for world,npc,x,y,z,yaw,floor in [
        ('reino','astral_npc_guia_cavernas',7.5,67,0.5,90,'dirt_path'),
        ('cavernas','astral_npc_guia_reino',172.5,102,91.5,180,'packed_mud')]:
        bx,bz=int(x),int(z)
        selector=f'@e[type=minecraft:villager,x={x},y={y},z={z},distance=..0.8]'
        lines += [f'execute in minecraft:{world} run forceload add {bx} {bz}',
                  f'rg flag -w {world} __global__ mob-spawning allow',
                  f'execute in minecraft:{world} if block {bx} {y-1} {bz} minecraft:{floor} '
                  f'if block {bx} {y} {bz} minecraft:air if block {bx} {y+1} {bz} minecraft:air '
                  f'unless entity {selector} run mm mobs spawn {npc} 1 {world},{x},{y},{z}',
                  f'execute in minecraft:{world} as {selector} run data merge entity @s {{Rotation:[{yaw}f,0f]}}',
                  f'execute in minecraft:{world} run forceload remove {bx} {bz}']
    lines += ['# Actualizar la definicion del guardian del lobby sin recrearlo ni moverlo.',
              '# Los tres guias nuevos salen de viajes_mazmorras.py: guias-expediciones.txt.']
    path.write_text('\n'.join(lines)+'\n',encoding='utf-8')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base',type=Path,default=DEFAULT)
    parser.add_argument('--map',choices=DEFINITIONS)
    parser.add_argument('--enlaces',action='store_true',help='Generar solo comandos de los aldeanos de enlace')
    args=parser.parse_args()
    if not args.enlaces:
        for key in ([args.map] if args.map else DEFINITIONS):
            prepare(key,args.base)
    generate_travel_commands()
