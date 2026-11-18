"""Pisos naturales de combate medidos en las regiones locales. No modifica mapas."""
from mobs.terreno import get, clear
from collections import deque
from functools import lru_cache
import math

# Y de los pies; excluye subsuelos y tejados.
FLOORS = {
    'mina': ((-45,-45),(-39,-36),(-24,-24),(24,24)),
    'bosque': ((97,102),(100,101)),
    'tumba': ((58,60),(88,88),(72,72)),
    'cumbre': ((30,30),(30,30)),
    'forja': ((13,13),(13,13),(47,47)),
}
PADS = []
overlay = get


def safe(world, point, height=3):
    return clear(world, *point, height=height)


def supported(world, point):
    return False


def reachable(world, room, limits):
    """Componente del piso de juego desde la llegada; no admite cuevas aisladas.

    Es una comprobacion de navegacion por bloques, no una simulacion del jugador.
    Las regiones de terceros se leen exclusivamente dentro de .local.
    """
    anchor=room['centro'] if room.get('boss_room') else room['llegada']
    return _reachable(world,tuple(room['spawn_points'])+(tuple(room['llegada']),tuple(room['centro'])),tuple(anchor),limits)


@lru_cache(maxsize=128)
def _reachable(world, points, anchor, limits):
    x0, x1 = math.floor(min(p[0] for p in points))-4, math.floor(max(p[0] for p in points))+4
    z0, z1 = math.floor(min(p[2] for p in points))-4, math.floor(max(p[2] for p in points))+4
    def valid(p):
        x,y,z=p
        if not (x0<=x<=x1 and z0<=z<=z1 and limits[0]-2<=y<=limits[1]+3):
            return False
        # La llegada historica de Minas sala2 esta en el estanque. El agua
        # conecta el acceso con la orilla; nunca se utiliza como spawn.
        swim = get(world,x,y-1,z)=='minecraft:water' and all(
            get(world,x,y+dy,z) in ('minecraft:air','minecraft:cave_air','minecraft:water') for dy in (0,1))
        from mobs.terreno import AIR
        feet=get(world,x,y,z)
        step=(feet=='minecraft:snow' or feet.endswith(('_stairs','_slab','_carpet'))) and get(world,x,y+1,z) in AIR
        return swim or step or clear(world,x,y,z,height=2,allow_steps=True)
    ax,ay,az=anchor
    seeds=[(x,y,z) for x in range(math.floor(ax)-12,math.floor(ax)+13)
           for z in range(math.floor(az)-12,math.floor(az)+13) for y in range(limits[0]-2,limits[1]+4) if valid((x,y,z))]
    if not seeds:
        raise ValueError(f'Sin acceso al piso: {world}/{anchor}')
    start=min(seeds,key=lambda p:(p[0]+.5-ax)**2+(p[1]-ay)**2+(p[2]+.5-az)**2)
    seen={start}; queue=deque([start])
    while queue:
        x,y,z=queue.popleft()
        for dx,dz in ((1,0),(-1,0),(0,1),(0,-1)):
            for dy in (0,1,-1):
                p=(x+dx,y+dy,z+dz)
                # Al saltar tambien debe quedar espacio para la cabeza.
                if p not in seen and valid(p) and (dy==0 or get(world,x,max(y,p[1])+1,z) in ('minecraft:air','minecraft:cave_air')):
                    seen.add(p);queue.append(p)
    return seen


def configure(dungeon):
    key=dungeon['key']; world=dungeon['world']
    if key=='santuario': return
    for room, limits in zip(dungeon['rooms'], FLOORS[key], strict=True):
        room['floor_range']=limits
        accessible=reachable(world,room,limits)
        for field in ('spawn_points','golem_points'):
            if field not in room: continue
            valid=[p for p in room[field] if limits[0]<=p[1]<=limits[1] and safe(world,p)
                   and tuple(math.floor(v) for v in p) in accessible]
            room.setdefault('spawn_rejected', {})[field]=[p for p in room[field] if p not in valid]
            if not valid: raise ValueError(f'Sala sin piso natural seguro: {key}/{room["id"]}/{field}')
            room[field]=valid
        if room.get('boss_room'):
            p=room['centro']
            if not limits[0]<=p[1]<=limits[1] or not safe(world,p):
                raise ValueError(f'Jefe sin piso natural: {key} {p}')
            room['boss_spawn']=p
            chest={'bosque':(1604.5,101,1382.5),'tumba':(0.5,72,0.5)}.get(key,p)
            if not safe(world,chest): chest=p
            room.setdefault('final_npcs',{})['cofre']=chest
            # Distancia exacta de dos bloques, piso natural y tres bloques libres.
            x,y,z=chest
            candidates=[(x+dx,y,z+dz) for dx,dz in ((2,0),(-2,0),(0,2),(0,-2))]
            guide=next((p for p in candidates if safe(world,p)),None)
            if guide is None: raise ValueError(f'Sin piso para guia junto al cofre: {key} {chest}')
            room['final_npcs']['guia']=guide
            room['chest_platform']=key in ('bosque','tumba')


def install_commands():
    return []
