"""Propuesta PRIVADA de terreno del lobby; nunca conecta ni modifica el servidor.

Requiere numpy y Pillow. Ver build/deploy/lobby-terreno.md.
Las coordenadas se conservan, incluyendo estados de bloques en los respaldos.
"""
import argparse
from collections import Counter
import gzip
import hashlib
import json
import math
from pathlib import Path
import re
import zipfile
import zlib

import numpy as np
from PIL import Image, ImageDraw
from mapas import NBT, nbt_payload, nbt_string

ROOT = Path(__file__).resolve().parents[1]
AIR = 'minecraft:air'
SOIL = {'grass_block', 'dirt', 'coarse_dirt', 'rooted_dirt', 'podzol', 'moss_block', 'gravel', 'mud'}
ROCK = {'deepslate', 'cobbled_deepslate', 'polished_deepslate', 'stone', 'andesite', 'tuff', 'cobblestone'}
PLANTS = {'short_grass', 'tall_grass', 'fern', 'large_fern', 'moss_carpet', 'vine', 'bamboo', 'bamboo_sapling', 'bush',
          'dead_bush', 'dandelion', 'poppy', 'pink_petals', 'wildflowers', 'leaf_litter'}


def base(state):
    return state.split('[', 1)[0].removeprefix('minecraft:')


def private(path):
    path = Path(path).resolve()
    if not path.is_relative_to(ROOT / '.local'):
        raise ValueError('Salidas del mapa y vistas: exclusivamente bajo .local/')
    return path


def state_name(entry):
    props = entry.get('Properties', {})
    return entry['Name'] + ('[' + ','.join(f'{k}={v}' for k, v in sorted(props.items())) + ']' if props else '')


class World:
    """Solo bloques modernos; chunks ausentes NO equivalen a aire conocido."""
    def __init__(self):
        self.names = [AIR]
        self.lookup = {AIR: 0}
        self.sections = {}
        self.chunks = set()
        self.tiles = set()
        self.version = 0
        self.sources = {}

    def ident(self, name):
        if name not in self.lookup:
            self.lookup[name] = len(self.names)
            self.names.append(name)
        return self.lookup[name]

    def add_region(self, name, raw, bounds):
        self.sources[name] = hashlib.sha256(raw).hexdigest()
        if len(raw) < 8192:
            raise ValueError(f'Region incompleta: {name}')
        for slot in range(1024):
            offset = int.from_bytes(raw[slot*4:slot*4+3], 'big')*4096
            if not offset:
                continue
            size = int.from_bytes(raw[offset:offset+4], 'big')
            kind = raw[offset+4]
            data = raw[offset+5:offset+4+size]
            if kind == 2:
                data = zlib.decompress(data)
            elif kind == 1:
                data = gzip.decompress(data)
            elif kind != 3:
                raise ValueError(f'Compresion no soportada {kind}: {name}; no se omite el chunk')
            c = NBT(data).root()
            if 'Level' in c:
                c = c['Level']
            cx, cz = c['xPos'], c['zPos']
            x0, z0, x1, z1 = bounds
            if cx*16 > x1 or cx*16+15 < x0 or cz*16 > z1 or cz*16+15 < z0:
                continue
            self.chunks.add((cx, cz))
            self.version = max(self.version, c.get('DataVersion', 0))
            for e in c.get('block_entities', []):
                self.tiles.add((e['x'], e['y'], e['z']))
            for s in c.get('sections', []):
                bs = s.get('block_states', {})
                palette = bs.get('palette', [])
                if not palette:
                    continue
                ids = np.array([self.ident(state_name(p)) for p in palette], dtype=np.uint16)
                if len(ids) == 1:
                    if ids[0] == 0:
                        continue
                    a = np.full(4096, ids[0], dtype=np.uint16)
                else:
                    bits = max(4, (len(ids)-1).bit_length())
                    words = np.array(bs['data'], dtype=np.int64).view(np.uint64)
                    loc = np.arange(4096, dtype=np.uint64)
                    indices = (words[loc//(64//bits)] >> ((loc % (64//bits))*bits)) & ((1 << bits)-1)
                    a = ids[indices.astype(int)]
                self.sections[cx, s['Y'], cz] = a.reshape(16, 16, 16)

    @classmethod
    def load(cls, path, bounds):
        world = cls()
        pattern = re.compile(r'r\.(-?\d+)\.(-?\d+)\.mca$')
        def wanted(name):
            m = pattern.fullmatch(Path(name).name)
            if not m:
                return False
            rx, rz = map(int, m.groups())
            x0, z0, x1, z1 = bounds
            return rx*512 <= x1 and rx*512+511 >= x0 and rz*512 <= z1 and rz*512+511 >= z0
        if path.suffix == '.zip':
            with zipfile.ZipFile(path) as archive:
                for n in archive.namelist():
                    # Solo overworld del original, nunca DIM1/DIM-1 ni datapacks.
                    if re.fullmatch(r'[^/]+/region/r\.-?\d+\.-?\d+\.mca', n) and wanted(n):
                        world.add_region(n, archive.read(n), bounds)
        else:
            for p in sorted(path.glob('*.mca')):
                if wanted(p.name):
                    world.add_region(p.name, p.read_bytes(), bounds)
        if not world.chunks:
            raise ValueError('No se encontraron chunks modernos en el area')
        return world

    def get(self, x, y, z):
        if (x//16, z//16) not in self.chunks:
            raise ValueError(f'Chunk sin descargar: {x//16}, {z//16}')
        a = self.sections.get((x//16, y//16, z//16))
        return self.names[int(a[y % 16, z % 16, x % 16])] if a is not None else AIR

    def surface(self, bounds, ground=False):
        x0, z0, x1, z1 = bounds
        heights = np.full((z1-z0+1, x1-x0+1), -32768, dtype=np.int16)
        tops = np.zeros_like(heights, dtype=np.uint16)
        valid = np.array([base(n) not in {'air', 'cave_air', 'void_air'} and
                          (not ground or (base(n) not in PLANTS and not any(t in base(n) for t in ('leaves', 'log', 'wood'))))
                          for n in self.names])
        for (cx, sy, cz), a in sorted(self.sections.items(), key=lambda kv: kv[0][1]):
            ax, bx = max(x0, cx*16), min(x1+1, cx*16+16)
            az, bz = max(z0, cz*16), min(z1+1, cz*16+16)
            if ax >= bx or az >= bz:
                continue
            section = a[:, az-cz*16:bz-cz*16, ax-cx*16:bx-cx*16]
            mask = valid[section]
            has = mask.any(axis=0)
            local = 15-np.argmax(mask[::-1], axis=0)
            view = heights[az-z0:bz-z0, ax-x0:bx-x0]
            view[has] = (local+sy*16)[has]
            topview = tops[az-z0:bz-z0, ax-x0:bx-x0]
            topview[has] = np.take_along_axis(section, local[None], axis=0)[0][has]
        return heights, tops


def noise(x, z, scale, seed):
    """Ruido de valor continuo; manchas, sin sal y pimienta por bloque."""
    def rand(a, b):
        return ((a*374761393 + b*668265263 + seed*1447) ^ ((a*1274126177+b*7919) >> 13)) % 65521 / 65521
    u, v = x/scale, z/scale
    a, b = math.floor(u), math.floor(v)
    u, v = u-a, v-b
    u, v = u*u*(3-2*u), v*v*(3-2*v)
    return (rand(a,b)*(1-u)+rand(a+1,b)*u)*(1-v)+(rand(a,b+1)*(1-u)+rand(a+1,b+1)*u)*v


def choose(counter, value):
    total = sum(counter.values())
    if not total:
        raise ValueError('Paleta de referencia vacia')
    target = value*total
    for name, count in sorted(counter.items()):
        target -= count
        if target < 0:
            return name
    return sorted(counter)[-1]


def patch_scale(original, heights, tops, config):
    """Mediana de tramos iguales en las dos direcciones del suelo de referencia."""
    eligible=np.array([base(n) in SOIL for n in original.names])[tops]
    eligible &= (heights>=config.get('soil_y_min',-64)) & (heights<=config.get('soil_y_max',319))
    runs=[]
    for ids,mask in ((tops,eligible),(tops.T,eligible.T)):
        for row,valid in zip(ids,mask):
            length=0;last=-1
            for ident,ok in zip(row,valid):
                if ok and ident==last:
                    length+=1
                else:
                    if length:runs.append(length)
                    length=1 if ok else 0
                last=ident if ok else -1
            if length:runs.append(length)
    return max(2.,float(np.median(runs))) if runs else 3.


def dilate(mask, radius):
    result = mask.copy()
    for _ in range(radius):
        p = np.pad(result, 1)
        result = p[1:-1,1:-1] | p[:-2,1:-1] | p[2:,1:-1] | p[1:-1,:-2] | p[1:-1,2:]
    return result


SEE_THROUGH = ('cobweb', 'glass', 'leaves', 'water', 'lava', 'vine', 'air')


def underside_palette(original, bounds, config):
    """Piel real de abajo de la isla original: los 3 bloques mas bajos de cada columna."""
    x0, z0, x1, z1 = bounds
    ref = config.get('reference_bounds', bounds)
    solid = np.array([base(n) not in {'air', 'cave_air', 'void_air'} for n in original.names])
    low = np.full((z1-z0+1, x1-x0+1), 32767, dtype=np.int32)
    for (cx, sy, cz), a in original.sections.items():
        ax, bx = max(x0, cx*16), min(x1+1, cx*16+16)
        az, bz = max(z0, cz*16), min(z1+1, cz*16+16)
        if ax >= bx or az >= bz:
            continue
        m = solid[a[:, az-cz*16:bz-cz*16, ax-cx*16:bx-cx*16]]
        has = m.any(axis=0)
        view = low[az-z0:bz-z0, ax-x0:bx-x0]
        view[has] = np.minimum(view[has], (np.argmax(m, axis=0)+sy*16)[has])
    skin = Counter()
    for z, x in zip(*np.nonzero(low < 32767)):
        wx, wz = int(x+x0), int(z+z0)
        if not (ref[0] <= wx <= ref[2] and ref[1] <= wz <= ref[3]):
            continue
        for y in range(int(low[z, x]), int(low[z, x])+3):
            name = original.get(wx, y, wz)
            if base(name) in PLANTS or any(t in base(name) for t in SEE_THROUGH):
                continue
            skin[name] += 1
    # Solo materiales con presencia real (>=2%), sin restos sueltos de construcciones.
    total = sum(skin.values())
    return Counter({n: c for n, c in skin.items() if total and c/total >= .02})


def edge_distance(mask):
    """Distancia (en bloques, 4 vecinos) desde cada columna del mask hasta su borde exterior."""
    d = np.zeros(mask.shape, dtype=np.int32)
    cur = mask.copy()
    k = 0
    while cur.any():
        k += 1
        d[cur] = k
        p = np.pad(cur, 1)
        cur = cur & p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:]
    return d


def analyse(current, original, bounds, config=None):
    config = config or {}
    h, t = current.surface(bounds, ground=True)
    oh, ot = original.surface(bounds, ground=True)
    x0, z0, _, _ = bounds
    soil, rock, bands = Counter(), Counter(), {}
    # Solo muestras realmente presentes en el original en su ubicacion original.
    for z, x in zip(*np.nonzero(oh > -32768)):
        ref=config.get('reference_bounds',bounds)
        if not (ref[0]<=x+x0<=ref[2] and ref[1]<=z+z0<=ref[3]):
            continue
        name = original.names[int(ot[z,x])]
        if base(name) in SOIL and config.get('soil_y_min', -64) <= oh[z,x] <= config.get('soil_y_max', 319):
            soil[name] += 1
        if base(name) in ROCK:
            rock[name] += 1
            bands.setdefault(str(int(oh[z,x])//8*8), Counter())[name] += 1
    if not soil or not rock:
        raise ValueError('No se pudo medir suelo y roca del original; comprobar alineacion')
    # Construcciones, agua, caminos de piedra y objetos siempre quedan protegidos.
    natural = np.array([base(n) in SOIL | ROCK for n in current.names])
    protected = (h > -32768) & ~natural[t]
    protected = dilate(protected, 5)
    for x, y, z in current.tiles:
        if x0 <= x <= bounds[2] and z0 <= z <= bounds[3]:
            protected[max(0,z-z0-6):z-z0+7, max(0,x-x0-6):x-x0+7] = True
    # Diferencia original/actual prueba que es una extension, no pasto original.
    soilids = np.array([base(n) in {'grass_block', 'dirt'} for n in current.names])
    added = (h > -32768) & soilids[t] & ((oh == -32768) | (np.abs(h.astype(int)-oh.astype(int)) > 2))
    flat = np.ones_like(added)
    for dz, dx in ((1,0),(-1,0),(0,1),(0,-1)):
        neighbour = np.roll(h, (dz,dx), axis=(0,1))
        flat &= np.abs(h.astype(int)-neighbour.astype(int)) <= 1
    added &= flat & ~protected
    return h, t, oh, ot, protected, added, soil, rock, bands


def propose(world, original, bounds, config):
    h,t,oh,ot,protected,added,soil,rock,bands = analyse(world,original,bounds,config)
    x0,z0,x1,z1 = bounds
    changes = {}
    def setblock(x,y,z,state, mountain=False):
        if not (x0 <= x <= x1 and z0 <= z <= z1) or protected[z-z0,x-x0]:
            return False
        before = world.get(x,y,z)
        if (x,y,z) in world.tiles or (mountain and base(before) not in SOIL | ROCK | {'air','cave_air','void_air'}):
            return False
        if before != state:
            changes[x,y,z] = state
        return True
    soil_scale=config.get('soil_scale') or patch_scale(original,oh,ot,config)
    candidates=[(noise(int(x+x0),int(z+z0),soil_scale,config['seed']),int(z),int(x)) for z,x in zip(*np.nonzero(added))]
    # Rangos del ruido: conserva la proporcion medida sin perder las manchas.
    for rank,(_,z,x) in enumerate(sorted(candidates)):
        xx,zz,y = int(x+x0),int(z+z0),int(h[z,x])
        setblock(xx,y,zz,choose(soil,(rank+.5)/len(candidates)))
    # Anillo parametrizado con poligono CERRADO revisable; no adivina accesos.
    ring = config.get('ring', [])
    if len(ring) < 3:
        raise ValueError('Definir al menos tres vertices del anillo en la configuracion privada')
    points = np.array(ring, dtype=float)
    distance = np.full(h.shape, np.inf)
    inside = np.zeros(h.shape,dtype=bool)
    zz,xx = np.indices(h.shape);xx=xx+x0;zz=zz+z0
    for a,b in zip(points,np.roll(points,-1,axis=0)):
        delta=b-a;length=float(delta@delta)
        if length == 0:
            raise ValueError('Vertices repetidos en el anillo')
        f=np.clip(((xx-a[0])*delta[0]+(zz-a[1])*delta[1])/length,0,1)
        distance=np.minimum(distance,np.hypot(xx-a[0]-f*delta[0],zz-a[1]-f*delta[1]))
        if a[1] != b[1]:
            inside ^= ((a[1]>zz)!=(b[1]>zz)) & (xx < (b[0]-a[0])*(zz-a[1])/(b[1]-a[1])+a[0])
    # Desplazar la cresta a ambos lados del poligono; evita una muralla regular.
    signed=distance*np.where(inside,-1,1)
    outward=np.zeros(h.shape,dtype=bool)
    for z in range(h.shape[0]):
        for x in range(h.shape[1]):
            value=signed[z,x]+(noise(x+x0,z+z0,17,config['seed']+20)-.5)*12
            distance[z,x]=abs(value);outward[z,x]=value>0
    mountain_mask=(distance < config['width']) & ~protected
    if mountain_mask[0].any() or mountain_mask[-1].any() or mountain_mask[:,0].any() or mountain_mask[:,-1].any():
        raise ValueError('Anillo cortado por los limites: ampliar bounds y descargar esos chunks')
    excluded = np.zeros_like(protected)
    for ax,az,bx,bz in config.get('exclude',[]):
        excluded[max(0,az-z0):min(h.shape[0],bz-z0+1),max(0,ax-x0):min(h.shape[1],bx-x0+1)] = True
    mountain_mask &= ~excluded
    # Excluir tambien el suelo; zonas de servicios se mantienen completas.
    for p in list(changes):
        if excluded[p[2]-z0,p[0]-x0]:
            del changes[p]
    ref=config.get('reference_bounds',bounds)
    refmask=(xx>=ref[0]) & (xx<=ref[2]) & (zz>=ref[1]) & (zz<=ref[3])
    reference_heights=oh[refmask & np.isin(ot,[i for i,n in enumerate(original.names) if base(n) in ROCK])]
    peak=int(np.percentile(reference_heights,95))
    floor=config['floor_y']
    if not (-64 <= floor < peak <= 319):
        raise ValueError('Alturas originales/anillo fuera de rango: comprobar configuracion')
    if not 1 <= config['foundation_depth'] <= floor+64:
        raise ValueError('Profundidad de apoyo invalida')
    summits={}
    cap=Counter({n:c for n,c in soil.items() if base(n) in {'moss_block','grass_block'}})
    if not cap:
        raise ValueError('El original no tiene cobertura verde medida')
    # Unir el borde a la isla a nivel bajo; no dejar un foso de vacio entre
    # protecciones y montanas. Solo columnas totalmente vacias, sin construir
    # por encima del piso ni tocar el mapa existente.
    # Base de isla FLOTANTE: la profundidad crece desde el borde exterior hacia
    # adentro (medido en el original: ~30 bloques en el borde, ~50 al centro),
    # con ruido y puntas colgantes. Evita el fondo plano y la pared vertical.
    foundation_mask=inside & (h == -32768) & ~excluded
    edge=edge_distance((h > -32768) | mountain_mask | foundation_mask)
    under=underside_palette(original,bounds,config) or rock
    smin=config.get('underside_min',6)
    slope=config.get('underside_slope',1.6)
    smax=min(config.get('underside_max',config['foundation_depth']),floor+64)
    def underside_bottom(x,z):
        wx,wz=int(x+x0),int(z+z0)
        depth=min(smax,smin+slope*(int(edge[z,x])-1))
        depth*=.7+.6*noise(wx,wz,11,config['seed']+30)
        if noise(wx,wz,3,config['seed']+31) > .78:
            depth+=3+9*noise(wx,wz,2,config['seed']+32)
        return floor-int(max(smin,min(smax+12,depth)))
    def under_state(wx,y,wz):
        return choose(under,noise(wx+y*.3,wz-y*.3,3,config['seed']+33))
    foundation_columns=0
    for z,x in zip(*np.nonzero(foundation_mask)):
        wx,wz=int(x+x0),int(z+z0)
        bottom=underside_bottom(x,z)
        if all(base(world.get(wx,y,wz)) in {'air','cave_air','void_air'} for y in range(bottom,floor+1)):
            for y in range(bottom,floor+1):
                if y == floor:
                    changes[wx,y,wz]=choose(cap,noise(wx,wz,7,config['seed']+3))
                elif y < floor-4:
                    changes[wx,y,wz]=under_state(wx,y,wz)
                else:
                    changes[wx,y,wz]=choose(rock,noise(wx+y*.4,wz,4,config['seed']+2))
            foundation_columns+=1
    for z,x in zip(*np.nonzero(mountain_mask)):
        wx,wz=int(x+x0),int(z+z0)
        f=1-distance[z,x]/config['width']
        rough=.48+.42*noise(wx,wz,13,config['seed']+1)+.1*noise(wx,wz,4,config['seed']+21)
        # Ladera exterior mas tendida: sin franja vertical debajo del borde.
        top=floor+int((peak-floor)*f**(config.get('outer_exponent',1.1) if outward[z,x] else .48)*rough)
        # Extender desde abajo sin cavidades; nunca borrar bloques existentes.
        bottom=int(h[z,x])+1 if h[z,x] > -32768 else underside_bottom(x,z)
        if bottom > top:
            continue
        # Columna completa: si hay decoracion se omite, en vez de enterrarla.
        if any(base(world.get(wx,y,wz)) not in SOIL | ROCK | {'air','cave_air','void_air'} for y in range(bottom,top+1)):
            continue
        for y in range(bottom,top+1):
            if y < floor-4 and h[z,x] == -32768:
                state=under_state(wx,y,wz)
            else:
                palette=bands.get(str(y//8*8),rock)
                state=choose(palette,noise(wx+y*.4,wz,4,config['seed']+2))
            if y == top and f < .85 and noise(wx,wz,5,config['seed']+22) > .3:
                state=choose(cap,noise(wx,wz,7,config['seed']+3))
            setblock(wx,y,wz,state,True)
        if top >= floor and f < .85:
            summits[wx,wz]=top
    vegetation=Counter()
    # Flora sintetica con los estados del original, nunca copia arboles del mapa.
    bamboo=[n for n in original.names if base(n)=='bamboo']
    leaves=[n for n in original.names if base(n)=='jungle_leaves']
    trunk=[n for n in original.names if base(n) in {'jungle_log','jungle_wood','acacia_wood'} and 'axis=y' in n]
    for (wx,wz),top in sorted(summits.items()):
        if base(changes.get((wx,top,wz),world.get(wx,top,wz))) not in {'moss_block','grass_block'}:
            continue
        if wx % 7 == 0 and wz % 7 == 0 and bamboo and noise(wx,wz,2,config['seed']+8) < .45:
            height=3+int(noise(wx,wz,5,config['seed']+9)*5)
            plant={(wx,y,wz):next((n for n in bamboo if f'leaves={"large" if y==top+height else "small" if y==top+height-1 else "none"}' in n),bamboo[0])
                   for y in range(top+1,top+height+1)}
            kind='bamboo'
        elif wx % 23 == 0 and wz % 23 == 0 and leaves and trunk:
            height=6+int(noise(wx,wz,5,config['seed']+10)*3)
            plant={(wx,y,wz):trunk[0] for y in range(top+1,top+height+1)}
            for dy,radius in ((-1,2),(0,3),(1,2),(2,1)):
                for dx in range(-radius,radius+1):
                    for dz in range(-radius,radius+1):
                        if dx*dx+dz*dz <= radius*radius+1 and (dx or dz or dy>0):
                            plant[wx+dx,top+height+dy,wz+dz]=leaves[0]
            kind='tree'
        else:
            continue
        if all(x0<=px<=x1 and z0<=pz<=z1 and py<=319 and not protected[pz-z0,px-x0] and
               not excluded[pz-z0,px-x0] and base(changes.get((px,py,pz),world.get(px,py,pz))) in {'air','cave_air','void_air'}
               for px,py,pz in plant):
            changes.update(plant);vegetation[kind]+=1
    report={'bounds_xz':list(bounds),'original_soil':dict(soil),'original_rock':dict(rock),
            'rock_by_height':{k:dict(v) for k,v in sorted(bands.items())},'peak_reference_y':peak,
            'extension_candidates':int(added.sum()),'protected_columns':int(protected.sum()),
            'changed_blocks':len(changes),'vegetation':dict(vegetation),'foundation_columns':foundation_columns,'soil_noise_scale':soil_scale,
            'ring_excluded_columns':int(((distance < config['width']) & ~mountain_mask).sum()),
            'warning':'Propuesta para revision visual; protecciones automaticas pueden interrumpir el anillo.'}
    return changes,report


def varints(values):
    data=bytearray()
    for value in values:
        value=int(value)
        while value > 127:
            data.append((value & 127)|128);value >>= 7
        data.append(value)
    return bytes(data)


def schematic(path, world, bounds, changes, after):
    x0,y0,z0,x1,y1,z1=bounds
    names=[];lookup={};values=[]
    # Cubo completo en AMBAS versiones: respaldo incluye aire y estados exactos.
    # Nada de entidades/biomas: se rechaza cualquier bloque con datos en el cubo.
    if any(x0<=x<=x1 and y0<=y<=y1 and z0<=z<=z1 for x,y,z in world.tiles):
        raise ValueError('Sector incluye block entity: reducir sector, no perder sus datos')
    for y in range(y0,y1+1):
        for z in range(z0,z1+1):
            for x in range(x0,x1+1):
                state=changes.get((x,y,z),world.get(x,y,z)) if after else world.get(x,y,z)
                if state not in lookup:
                    lookup[state]=len(names);names.append(state)
                values.append(lookup[state])
    s={'Version':(3,3),'DataVersion':(3,world.version),'Width':(2,x1-x0+1),
       'Height':(2,y1-y0+1),'Length':(2,z1-z0+1),'Offset':(11,[0,0,0]),
       'Metadata':(10,{'Name':(8,path.stem)}),
       'Blocks':(10,{'Palette':(10,{n:(3,i) for i,n in enumerate(names)}),'Data':(7,varints(values))})}
    root=(10,{'Schematic':(10,s)})
    path.write_bytes(gzip.compress(b'\x0a'+nbt_string('')+nbt_payload(root),mtime=0))


def export(world, changes, out):
    groups={}
    # Sectores 16x16x16: evita copiar torres enteras por un solo bloque de piso.
    for p,state in changes.items():
        groups.setdefault(tuple(v//16 for v in p),{})[p]=state
    # Partir sectores que contengan un cofre/cartel ajeno al delta, para que el
    # respaldo nunca pierda NBT ni sobrescriba inventarios al aplicar el cubo.
    def split(delta):
        coords=list(delta)
        lo=[min(p[j] for p in coords) for j in range(3)]
        hi=[max(p[j] for p in coords) for j in range(3)]
        if not any(all(lo[j]<=p[j]<=hi[j] for j in range(3)) for p in world.tiles):
            return [delta]
        axis=max(range(3),key=lambda j:hi[j]-lo[j])
        if hi[axis]==lo[axis]:raise ValueError('Intento de cambiar block entity')
        mid=(hi[axis]+lo[axis])//2
        return split({p:s for p,s in delta.items() if p[axis]<=mid})+split({p:s for p,s in delta.items() if p[axis]>mid})
    safe_groups=[part for _,delta in sorted(groups.items()) for part in split(delta)]
    manifest=[]
    schems=out/'schematics';schems.mkdir()
    commands=['# EJECUTAR SOLO TRAS APROBACION; jugador OP en lobby; sin rotar ni voltear.']
    rollback=[]
    for i,delta in enumerate(safe_groups):
        coords=list(delta)
        lo=[min(p[j] for p in coords) for j in range(3)]
        hi=[max(p[j] for p in coords) for j in range(3)]
        bounds=(*lo,*hi)
        name=f'lobby_{i:04d}'
        hashes={}
        for suffix,after in [('antes',False),('despues',True)]:
            path=schems/f'{name}_{suffix}.schem'
            schematic(path,world,bounds,delta,after)
            hashes[suffix]=hashlib.sha256(path.read_bytes()).hexdigest()
        position=f'/minecraft:tp @s {lo[0]} {lo[1]} {lo[2]}'
        commands += [f'# {name}: {len(delta)} cambios; esquina minima {lo}',position,
                     f'//schem load {name}_despues','//paste -a']
        # NO -a: restaurar el aire que ocupaban las nuevas montanas.
        rollback += [position,f'//schem load {name}_antes','//paste']
        manifest.append({'id':name,'bounds_xyz':list(bounds),'changed_blocks':len(delta),'sha256':hashes,
                         'local_before':f'schematics/{name}_antes.schem','local_after':f'schematics/{name}_despues.schem',
                         'remote_directory':'plugins/WorldEdit/schematics/'})
    (out/'pegar.txt').write_text('\n'.join(commands)+'\n',encoding='utf8')
    (out/'restaurar.txt').write_text('\n'.join(rollback)+'\n',encoding='utf8')
    return manifest


def verify_export(world, out, sectors, expected_count):
    """Releer todos los schematics y comparar cada respaldo con la descarga."""
    checked=changed=air_restored=0
    for item in sectors:
        decoded=[]
        for kind in ('before','after'):
            path=out/item[f'local_{kind}']
            suffix='antes' if kind=='before' else 'despues'
            if hashlib.sha256(path.read_bytes()).hexdigest()!=item['sha256'][suffix]:
                raise ValueError(f'Hash distinto del manifest: {path.name}')
            s=NBT(gzip.decompress(path.read_bytes())).root()['Schematic']
            if s['Version']!=3 or s['Offset']!=[0,0,0] or s['DataVersion']!=world.version:
                raise ValueError(f'Cabecera incorrecta: {path.name}')
            if any(k in s for k in ('Entities','Biomes')) or s['Blocks'].get('BlockEntities'):
                raise ValueError('El sector no debe copiar entidades ni biomas')
            palette={i:n for n,i in s['Blocks']['Palette'].items()}
            values=[];value=shift=0
            for b in s['Blocks']['Data']:
                value |= (b & 127) << shift
                if b & 128:shift+=7
                else:values.append(palette[value]);value=shift=0
            volume=s['Width']*s['Height']*s['Length']
            box=item['bounds_xyz']
            if (s['Width'],s['Height'],s['Length'])!=tuple(box[j+3]-box[j]+1 for j in range(3)):
                raise ValueError('Dimensiones distintas del manifest')
            if shift or len(values)!=volume:raise ValueError('Varints/volumen incompletos')
            decoded.append(values)
        x0,y0,z0,x1,y1,z1=item['bounds_xyz']
        coords=((x,y,z) for y in range(y0,y1+1) for z in range(z0,z1+1) for x in range(x0,x1+1))
        delta=0
        for p,before,after in zip(coords,*decoded,strict=True):
            if before!=world.get(*p):raise ValueError(f'Respaldo distinto de la fuente: {p}')
            if before!=after:
                if base(before) not in {'air','cave_air','void_air','grass_block','dirt'}:
                    raise ValueError(f'Se altero un bloque ajeno al suelo liso: {p}')
                if base(after) in {'air','cave_air','void_air'}:raise ValueError('La propuesta no debe borrar bloques')
                delta+=1;air_restored+=base(before) in {'air','cave_air','void_air'}
            checked+=1
        if delta!=item['changed_blocks']:raise ValueError('Cantidad de cambios distinta del manifest')
        changed+=delta
    if changed!=expected_count:raise ValueError('Cantidad total distinta del delta')
    report={'sectors_verified':len(sectors),'voxel_pairs_verified':checked,'changed_blocks':changed,
            'air_blocks_in_rollback':air_restored,'original_states_preserved':True,
            'block_entities_excluded':True,'worldedit_runtime_test':'pendiente; no se pego en ningun servidor'}
    (out/'validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    return report


def write_delivery(out,report):
    """Documentacion propia publica; mapas, configuracion y vistas quedan privados."""
    rel=out.resolve().relative_to(ROOT).as_posix()
    count=len(report['sectors']);last=count-1
    validation=json.loads((out/'validation.json').read_text(encoding='utf8'))
    doc=f'''# Terreno del lobby — propuesta del 17/11/2026

Generado por `datapack-src/lobby_terreno.py`. Estado: **borrador para aprobacion visual;
no instalado ni pegado**. Solo Parte B. Doble salto del lobby conservado; Parte A
ya instalada en `054db88`, no se genera ni se sube ningun Skript en esta entrega.
Empower es el servidor principal; Aternos conserva una copia.

## Archivos y reproduccion

Original intacto: `C:/Users/Trainx/Downloads/Parrot Spawn.zip` (Parrot Spawn, terceros).
Nueve regiones actuales descargadas por lectura oficial a `.local/lobby/actual/region/`:
`r.X.Z.mca` para cada combinacion X/Z de -1, 0 y 1. No se descargo ni ejecuto codigo
del mapa. La copia leida con el servidor activo es una referencia de trabajo,
no reemplaza un respaldo coherente del panel ni garantiza que el lobby siga igual.

Configuracion privada revisada: `.local/lobby/config-v3.json`.
Salida vigente: `{rel}/`. Conservar las propuestas v1/v2 como historial, no instalarlas.
Los archivos privados NO estan en GitHub. En otra maquina se necesita acceso a estas
copias y su configuracion; no reconstruir el mapa desde el repositorio publico.

```powershell
.\\.local\\tanda17-venv\\Scripts\\python.exe datapack-src/lobby_terreno.py --actual .local/lobby/actual/region --original 'C:/Users/Trainx/Downloads/Parrot Spawn.zip' --config .local/lobby/config-v3.json --out .local/lobby/propuesta-revision --delivery
```

Requiere Python con `numpy` y `Pillow`. Usar una carpeta de salida nueva; el generador
rechaza sobrescribir respaldos/propuestas. La accion `download` de `tools/empower_api.py`
usa `/files/download` oficial, exige HTTPS y no imprime claves ni URLs firmadas:

```text
python tools/empower_api.py --yes download /world/dimensions/minecraft/lobby/region/r.0.0.mca .local/lobby/nueva-lectura/region/r.0.0.mca
```

Repetir para las nueve regiones. Sin `--yes` simula sin leer claves ni conectar.
No se usa ninguna API privada de Aternos ni se modifica el mundo remoto en esta tarea.

## Propuesta y protecciones

Se comparan alturas del original y del lobby actual en las mismas coordenadas.
Las muestras de referencia excluyen la torre del loro del sur. Suelo medido a Y94–102;
roca medida por bandas de ocho bloques. El original no tiene la paleta supuesta en las
capturas: se usan los materiales efectivamente presentes, sin inventar podzol/rooted dirt.
Los conteos y proporciones exactos estan en `manifest.json` (privado).

- Suelo medido: {', '.join(f'{base(n)} {c}' for n,c in sorted(report['original_soil'].items()))}.
- Roca medida: {', '.join(f'{base(n)} {c}' for n,c in sorted(report['original_rock'].items()))}.
- Altura de referencia P95 de roca: Y{report['peak_reference_y']}; se modula hacia abajo con ruido.
- Manchas: escala {report['soil_noise_scale']} bloques, mediana de tramos de suelo originales;
  se ordena el ruido para respetar las proporciones de la paleta superficial.
- {report['extension_candidates']} columnas candidatas de pasto/tierra agregados. Solo una capa
  superficial; se conserva el pasto original y el suelo cerca de edificios/caminos.
- Anillo cerrado con cresta irregular, base solida y cobertura de musgo/pasto;
  {report['vegetation'].get('bamboo',0)} bambues y {report['vegetation'].get('tree',0)} arboles sinteticos.
  Hojas de jungla y madera vertical presentes en el original; no se copian arboles enteros.
- {report['protected_columns']} columnas protegidas por construcciones, agua/caminos no naturales
  y margen de cinco bloques; block entities con margen adicional. Exclusion explicita
  del centro de servicios/spawn en la configuracion. La union baja solo rellena columnas
  vacias hasta Y97; no levanta montanas dentro de los margenes protegidos.
- Los caminos de piedra, edificios, portales, carteles, cofres e inventarios no se cambian.
  No se copian entidades ni biomas. Se rechazan chunks sin descargar y anillos recortados.

Limite: las detecciones automaticas no reconocen todos los usos del lobby. Revisar
especialmente accesos al tren, laterales del castillo, portales, senderos y bordes
de las extensiones. Las protecciones pueden dejar una ladera mas baja junto a un edificio.
La propuesta aun requiere aprobacion del dueno con las vistas y, preferiblemente,
una copia de prueba del lobby. No se verifico carga/pegado con WorldEdit real.

## Revision privada

Ver en `{rel}/previews/`:

- `lobby_terreno_antes_planta.png` y `lobby_terreno_despues_planta.png`.
- `lobby_terreno_antes_tres_cuartos.png` y `lobby_terreno_despues_tres_cuartos.png`.

Son renders CPU con colores de materiales y caras de voxeles; no capturas en Minecraft.
No publicarlos en `build/previews/` ni en GitHub: son derivados de un mapa de terceros.
Este criterio sigue `docs/TERCEROS.md` y corrige la ruta publica sugerida en el plan.

## Lista exacta para instalar DESPUES de aprobar

Origen local: `{rel}/schematics/`.
Destino remoto unico: `plugins/WorldEdit/schematics/`.

Son {count*2} archivos: por cada entero N entre **0000 y {last:04d}, inclusive**, subir
`lobby_N_antes.schem` y `lobby_N_despues.schem` (cuatro digitos, sin saltos).
**No mezclar archivos de propuestas distintas**: los mismos nombres se reutilizan.
Conservar tambien el manifest/respaldos locales de esta version. El listado individual
con SHA-256, caja XYZ, esquina de pegado y destino esta en `{rel}/manifest.json`.
No subir `manifest.json`, `validation.json`, vistas, `.mca`, ZIP original ni configuracion
privada al servidor o al repositorio publico.

1. Cerrar el acceso al lobby para mantenimiento y verificar que no hubo ediciones
   desde la descarga. Si cambio, volver a descargar/regenerar y aprobar la nueva propuesta.
2. Antes de pegar: **apagar el servidor para obtener un respaldo coherente del panel**;
   comprobar que termino y que contiene el lobby. Reiniciar sin reemplazar mundos.
   Los backups de antes de esta tarea no sustituyen el respaldo inmediatamente previo.
3. Subir solamente los schematics indicados. WorldEdit los lee al cargar: **sin comando
   de recarga de plugins, datapack ni resource pack**. Pegarlos con el servidor encendido,
   un unico jugador OP y acceso al lobby cerrado. No hace falta otro reinicio por terreno.
4. Probar primero un sector en una copia de prueba. Verificar que WorldEdit instalado
   reconoce Sponge v3 y DataVersion {report['data_version']}. Hay muchos sectores: aplicar
   de a uno o en tandas cortas, esperar que termine cada operacion y revisar consola/TPS.
   No aumentar limites globales ni automatizar los {count} pegados en el servidor activo.
5. Seguir en orden `{rel}/pegar.txt`. Contiene {count} bloques de comandos exactos,
   cada uno con el TP a la **esquina minima XYZ** especifica del sector, seguido por:

   ```text
   //schem load lobby_N_despues
   //paste -a
   ```

   Ejecutar como jugador OP en **lobby** (`/mvtp w:lobby` antes del primer TP).
   El TP es `/minecraft:tp @s X Y Z`; pasar a espectador para evitar quedar atrapado
   y restaurar el modo previo al terminar. Offset `[0,0,0]`: no rotar, voltear ni
   usar `//paste -o`. El TP fija la esquina, no el centro del schematic.
6. Revisar consola por errores y recorrer en cliente la union, accesos y suelo.
   Solo afirmar despliegue tras verificar el resultado. No ejecutar setup del lobby.

Nunca usar Worlds > Upload en la fila `world`, ni sustituir mundos ni regiones.
No se cambia el datapack, JAR, pack FINAL/R2, gameplay o MythicMobs en esta entrega.

## Reversion

Para el ultimo pegado de la misma sesion: `//undo` (conservar la sesion y el historial).
Para restaurar los sectores aplicados, usar sus lineas correspondientes en
`{rel}/restaurar.txt`: mismo mundo y esquina, `//schem load lobby_N_antes` y **`//paste`
sin `-a`**. El aire del respaldo retira roca, plantas y arboles nuevos. No restaurar
sectores que no se aplicaron ni hacerlo sobre ediciones posteriores de otros usuarios.
Los cubos completos conservan estados originales; no incluyen cofres/carteles con NBT.
El respaldo del panel queda como recuperacion independiente si se pierde el historial.

## Verificaciones de esta propuesta

- {validation['sectors_verified']} pares Sponge v3 releidos; {validation['voxel_pairs_verified']:,} posiciones comparadas
  contra los bloques descargados; {validation['changed_blocks']:,} cambios.
- {validation['air_blocks_in_rollback']:,} posiciones de aire incluidas en los respaldos. No se elimina
  ningun bloque en la propuesta y los cambios sobre bloques existentes son solo pasto/tierra.
- Propiedades de bloques conservadas; block entities, entidades y biomas excluidos.
- Pruebas de lector MCA moderno, coordenadas negativas, varints >127, respaldo con aire,
  division alrededor de cofres, exclusiones, limites, descarga binaria y simulacion sin red.
- Carga de WorldEdit real, aprobacion visual y despliegue remoto: **pendientes**.

Formato: [especificacion oficial Sponge v3](https://github.com/SpongePowered/Schematic-Specification/blob/master/versions/schematic-3.md).
'''
    (ROOT/'build/deploy/lobby-terreno.md').write_text(doc,encoding='utf8')


def rgb(name,y):
    n=base(name)
    if n in {'air','cave_air','void_air'}:return (20,27,39)
    if n in {'dirt','coarse_dirt','rooted_dirt','podzol','mud'}:c=(119,83,50)
    elif any(t in n for t in ('grass','moss','leaves','bamboo','fern')):c=(67,125,57)
    elif 'deepslate' in n:c=(61,65,73)
    elif 'water' in n:c=(46,103,158)
    elif any(t in n for t in ('wood','log','planks')):c=(139,105,65)
    else:c=(137,140,141)
    factor=max(.6,min(1.25,.8+(y-80)/130))
    return tuple(int(v*factor) for v in c)


def previews(world,changes,bounds,out):
    h,t=world.surface(bounds)
    x0,z0,_,_=bounds
    before=h.copy();tops=t.copy()
    for (x,y,z),state in changes.items():
        if y >= h[z-z0,x-x0]:
            h[z-z0,x-x0]=y;tops[z-z0,x-x0]=world.ident(state)
    out.mkdir()
    for label,heights,ids in [('antes',before,t),('despues',h,tops)]:
        a=np.array([[rgb(world.names[int(v)],int(y)) for v,y in zip(row,hr)] for row,hr in zip(ids,heights)],dtype=np.uint8)
        im=Image.fromarray(a).resize((1024,1024),Image.Resampling.NEAREST)
        d=ImageDraw.Draw(im);d.text((12,12),f'LOBBY {label.upper()} - CPU PRIVADO - NORTE ARRIBA',fill='white')
        for x in range(math.ceil(x0/64)*64,bounds[2]+1,64):
            px=int((x-x0)/a.shape[1]*1024);d.line((px,30,px,1024),fill=(70,70,70));d.text((px+2,32),str(x),fill='white')
        for z in range(math.ceil(z0/64)*64,bounds[3]+1,64):
            py=int((z-z0)/a.shape[0]*1024);d.line((0,py,1024,py),fill=(70,70,70));d.text((2,py+2),str(z),fill='white')
        im.save(out/f'lobby_terreno_{label}_planta.png')
        oblique(world,changes if label=='despues' else {},bounds,out/f'lobby_terreno_{label}_tres_cuartos.png',label)


def oblique(world,changes,bounds,path,label):
    """Caras expuestas de voxeles, sin texturas del mapa ni renderer externo."""
    x0,z0,x1,z1=bounds
    ys=[sy*16 for (_,sy,_) in world.sections]
    ymin=min([*ys,*[y for _,y,_ in changes]])
    ymax=max([*[y+15 for y in ys],*[y for _,y,_ in changes]])
    a=np.zeros((ymax-ymin+1,z1-z0+1,x1-x0+1),dtype=np.uint16)
    for (cx,sy,cz),section in world.sections.items():
        ax,bx=max(x0,cx*16),min(x1+1,cx*16+16)
        az,bz=max(z0,cz*16),min(z1+1,cz*16+16)
        if ax<bx and az<bz:
            a[sy*16-ymin:sy*16-ymin+16,az-z0:bz-z0,ax-x0:bx-x0]=section[:,az-cz*16:bz-cz*16,ax-cx*16:bx-cx*16]
    for (x,y,z),state in changes.items():a[y-ymin,z-z0,x-x0]=world.ident(state)
    solid=np.array([base(n) not in {'air','cave_air','void_air'} for n in world.names])[a]
    p=np.pad(solid,1)
    top=solid & ~p[2:,1:-1,1:-1]
    south=solid & ~p[1:-1,2:,1:-1]
    east=solid & ~p[1:-1,1:-1,2:]
    yy,zz,xx=np.nonzero(top|south|east)
    if not len(xx):raise ValueError('Vista vacia')
    u=xx-zz;v=(xx+zz)*.5-(yy+ymin)
    scale=min(1280/(float(u.max()-u.min())+4),860/(float(v.max()-v.min())+4))
    offsetx=700-(float(u.max()+u.min())/2)*scale
    offsety=510-(float(v.max()+v.min())/2)*scale
    im=Image.new('RGB',(1400,1000),(20,27,39));d=ImageDraw.Draw(im)
    for i in np.argsort(xx+zz+yy*.001,kind='stable'):
        x,z,y=int(xx[i]),int(zz[i]),int(yy[i])
        sx=offsetx+(x-z)*scale;sy=offsety+((x+z)*.5-y-ymin)*scale
        c=rgb(world.names[int(a[y,z,x])],y+ymin)
        if south[y,z,x]:d.polygon([(sx-scale,sy),(sx,sy+scale*.5),(sx,sy-scale*.5),(sx-scale,sy-scale)],fill=tuple(int(v*.65) for v in c))
        if east[y,z,x]:d.polygon([(sx,sy+scale*.5),(sx+scale,sy),(sx+scale,sy-scale),(sx,sy-scale*.5)],fill=tuple(int(v*.8) for v in c))
        if top[y,z,x]:d.polygon([(sx,sy-scale*1.5),(sx+scale,sy-scale),(sx,sy-scale*.5),(sx-scale,sy-scale)],fill=c)
    d.text((12,12),f'LOBBY {label.upper()} - CARAS DE VOXELES CPU PRIVADAS, NO CAPTURA',fill='white')
    im.save(path)


ACCESS = ('rail', 'nether_portal', 'end_gateway', 'end_portal', 'end_portal_frame', 'oak_sign', 'wall_sign',
          'hanging_sign', 'command_block')


def accesses(world, bounds, changes, radius=3, clearance=6):
    """Vias del tren, portales y carteles del lobby actual; ninguno puede quedar tapado."""
    x0, z0, x1, z1 = bounds
    want = np.array([any(base(n) == t or base(n).endswith('_' + t) for t in ACCESS) for n in world.names])
    found = []
    for (cx, sy, cz), a in world.sections.items():
        if not want[a].any():
            continue
        for y, z, x in zip(*np.nonzero(want[a])):
            wx, wy, wz = cx*16+int(x), sy*16+int(y), cz*16+int(z)
            if x0 <= wx <= x1 and z0 <= wz <= z1:
                found.append((wx, wy, wz, base(world.names[int(a[y, z, x])])))
    blocked = []
    for wx, wy, wz, kind in found:
        for dx in range(-radius, radius+1):
            for dz in range(-radius, radius+1):
                for dy in range(0, clearance+1):
                    if (wx+dx, wy+dy, wz+dz) in changes:
                        blocked.append((wx, wy, wz, kind))
                        break
                else:
                    continue
                break
            else:
                continue
            break
    groups = Counter(kind for *_, kind in found)
    return dict(total=len(found), por_tipo=dict(groups), tapados=blocked[:50], tapados_total=len(blocked))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--actual',type=Path,required=True,help='Carpeta region descargada (solo lectura)')
    p.add_argument('--original',type=Path,required=True,help='ZIP Parrot Spawn intacto')
    p.add_argument('--config',type=Path,required=True,help='JSON privado: bounds, ring, exclusiones')
    p.add_argument('--out',type=Path,required=True,help='Carpeta NUEVA bajo .local')
    p.add_argument('--delivery',action='store_true',help='Regenerar build/deploy/lobby-terreno.md con esta propuesta')
    args=p.parse_args();out=private(args.out)
    if out.exists():raise ValueError('Usar salida nueva; conservar propuestas y respaldos anteriores')
    config=json.loads(args.config.read_text(encoding='utf-8-sig'))
    bounds=config['bounds']
    if len(bounds)!=4 or bounds[2]<bounds[0] or bounds[3]<bounds[1] or (bounds[2]-bounds[0]+1)*(bounds[3]-bounds[1]+1)>1048576:
        raise ValueError('Limites invalidos o mayores a 1024x1024')
    world=World.load(args.actual,bounds);original=World.load(args.original,bounds)
    for cz in range(bounds[1]//16,bounds[3]//16+1):
        for cx in range(bounds[0]//16,bounds[2]//16+1):
            if (cx,cz) not in world.chunks:raise ValueError(f'Falta descargar chunk actual {cx},{cz}')
    changes,report=propose(world,original,bounds,config)
    if not changes:raise ValueError('Propuesta vacia')
    report['accesos']=accesses(world,bounds,changes)
    if report['accesos']['tapados_total']:
        print('ATENCION: accesos con bloques nuevos encima/al lado:',report['accesos']['tapados'][:10])
    out.mkdir(parents=True)
    sectors=export(world,changes,out)
    verify_export(world,out,sectors,len(changes))
    previews(world,changes,bounds,out/'previews')
    report.update({'config':config,'actual_sha256':world.sources,'original_sha256':original.sources,
                   'sectors':sectors,'status':'BORRADOR, NO APROBADO NI PEGADO','data_version':world.version})
    (out/'manifest.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    if args.delivery:write_delivery(out,report)
    print(f'Propuesta privada: {out}; {len(changes)} cambios; {len(sectors)} sectores. NO desplegada.')


if __name__=='__main__':main()
