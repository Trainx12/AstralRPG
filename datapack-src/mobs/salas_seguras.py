"""Pisos naturales de combate medidos en las regiones locales. No modifica mapas."""
from mobs.terreno import get, clear

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


def configure(dungeon):
    key=dungeon['key']; world=dungeon['world']
    if key=='santuario': return
    for room, limits in zip(dungeon['rooms'], FLOORS[key], strict=True):
        room['floor_range']=limits
        for field in ('spawn_points','golem_points'):
            if field not in room: continue
            valid=[p for p in room[field] if limits[0]<=p[1]<=limits[1] and safe(world,p)]
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
