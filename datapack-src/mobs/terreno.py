"""Lectura de regiones locales, siempre en modo solo lectura. Nunca exporta mapas."""
from functools import lru_cache
from pathlib import Path
import math
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from mapas import block, chunk_records

ROOT = Path(__file__).resolve().parents[2]
AIR = {'minecraft:air', 'minecraft:cave_air', 'minecraft:void_air'}
BAD = ('air', 'water', 'lava', 'fire', 'leaves', 'fence', 'wall', 'slab', 'stairs',
       'carpet', 'torch', 'lantern', 'grass', 'flower', 'vine', 'chain', 'pane', 'snow',
       'trapdoor', 'button', 'rail', 'sign', 'cactus', 'campfire', 'soul_sand')

@lru_cache(maxsize=32)
def region(world, rx, rz):
    path = ROOT / '.local/mapas/server' / world / 'region' / f'r.{rx}.{rz}.mca'
    if not path.exists():
        raise FileNotFoundError(f'Falta region local de {world}: {path.name}')
    return {(c['xPos'], c['zPos']): c for c in chunk_records(path.read_bytes())}

def get(world, x, y, z):
    x,y,z = math.floor(x), math.floor(y), math.floor(z)
    chunk = region(world, x // 512, z // 512).get((x // 16,z // 16))
    return block(chunk, x % 16, y, z % 16) if chunk else 'minecraft:void_air'

def solid(name):
    return name == 'minecraft:snow_block' or not any(s in name.removeprefix('minecraft:') for s in BAD)

def clear(world, x, y, z, width=1, height=3, allow_steps=False):
    offset=width//2 if width % 2 else 0
    for dx in range(-offset,width-offset):
        for dz in range(-offset,width-offset):
            floor=get(world,x+dx,y-1,z+dz)
            if not solid(floor) and not (allow_steps and floor.endswith('_stairs')):
                return False
            if any(get(world,x+dx,y+dy,z+dz) not in AIR for dy in range(height)):
                return False
    return True

@lru_cache(maxsize=None)
def points(world, bounds, width=1, white=False, origin=None, limit=24):
    low = tuple(min(a,b) for a,b in zip(*bounds))
    high = tuple(max(a,b) for a,b in zip(*bounds))
    found=[]
    for x in range(low[0],high[0]+1):
        for z in range(low[2],high[2]+1):
            if origin and math.hypot(x+.5-origin[0],z+.5-origin[2]) > 25:
                continue
            for y in range(low[1],high[1]+1):
                floor=get(world,x,y-1,z)
                if white and floor not in {'minecraft:snow_block','minecraft:quartz_block',
                        'minecraft:smooth_quartz','minecraft:white_concrete','minecraft:white_wool'}:
                    continue
                if clear(world,x,y,z,width) and all(math.hypot(x+.5-p[0],z+.5-p[2]) >= 3 for p in found):
                    found.append((x+.5,y,z+.5))
                    break
    if not found:
        raise ValueError(f'Sin puntos seguros: {world} {bounds}')
    # Repartir en toda la seleccion, sin concentrar los primeros en una esquina.
    if len(found)>limit:
        found=[found[round(i*(len(found)-1)/(limit-1))] for i in range(limit)]
    return found
