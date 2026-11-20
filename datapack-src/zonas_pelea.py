"""Medir cercos locales en solo lectura. El build normal usa solamente el JSON.

python zonas_pelea.py --maps ../.local/mapas/server-18-11
Las vistas son diagramas de medidas, sin terreno ni texturas de terceros.
"""
import argparse
from collections import defaultdict
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = Path(__file__).with_suffix('.json')
PISO = 8  # bloques que se puede bajar durante una pelea antes de volver


def catalog():
    from viajes_mazmorras import destinations
    from instancias import DUNGEON_WORLDS
    import infinita, oceano_fosa
    out = []
    for d in destinations():
        if not d.get('enabled'):
            continue
        for i, r in enumerate(d['rooms']):
            # Piso de pelea: 8 bloques bajo lo mas bajo de la sala (llegada, centro, apariciones).
            ys = [r['centro'][1], r.get('llegada', r['centro'])[1], *(p[1] for p in r.get('spawn_points') or [])]
            floor = min(ys) - PISO if r.get('spawn_points') else ''
            out.append(dict(id=f'{d["key"]}/{i+1}', world=DUNGEON_WORLDS[d['key']], floor=floor,
                            key=d['key'], name=r['name'], center=list(r['centro']),
                            arrival=list(r.get('llegada', r['centro']))[:3], radius=r['r'],
                            entry_radius=r.get('entry_r',r['r']),
                            controller='Control '+r['name']))
    out += [dict(id='inf/1', world=infinita.WORLDS[0], key='inf', name='Infinita',
                 center=[.5, 63, .5], arrival=[.5, 63, .5], radius=32, entry_radius=32, controller=''),
            dict(id='fosa/1', world=oceano_fosa.WORLDS[0], key='fosa', name='Fosa',
                 center=[2, 112, 94], arrival=[2, 112, 94], radius=59, entry_radius=60, controller='')]
    return out


def load():
    zones = json.loads(DATA.read_text('utf8'))
    if set(zones) != {r['id'] for r in catalog()}:
        raise ValueError('Catalogo cambio: regenerar zonas_pelea.json con mapas actuales')
    for r in catalog():
        a = zones[r['id']]
        if len(a) != 6 or a[0] >= a[2] or a[1] >= a[3] or a[4] not in (0, 1):
            raise ValueError('Zona invalida: '+r['id'])
        x, _, z = r['center']
        if not (a[0] < x < a[2] and a[1] < z < a[3]):
            raise ValueError('Controlador fuera de zona: '+r['id'])
    return zones


def read_barriers(folder, world, rooms):
    """Decodificar solo secciones/chunks cercanos, sin escribir ni exportar mapas."""
    from mapas import chunk_records, packed
    files = sorted((folder/world/'region').glob('*.mca'))
    if not files:
        raise FileNotFoundError(f'Sin regiones: {folder/world}')
    found = []
    for f in files:
        for c in chunk_records(f.read_bytes()):
            cx, cz = c['xPos']*16, c['zPos']*16
            nearby = [r for r in rooms if abs(cx+8-r['center'][0]) <= 116
                      and abs(cz+8-r['center'][2]) <= 116]
            if not nearby:
                continue
            for s in c.get('sections', []):
                sy = s['Y']*16
                if not any(r['center'][1]-30 <= sy <= r['center'][1]+70 for r in nearby):
                    continue
                st = s.get('block_states', {})
                pal = st.get('palette', [])
                ids = {i for i, p in enumerate(pal) if p['Name'] == 'minecraft:barrier'}
                if not ids:
                    continue
                bits = max(4, (len(pal)-1).bit_length())
                for i in range(4096):
                    if (packed(st['data'], i, bits) if len(pal)>1 else 0) in ids:
                        found.append((cx+i%16, sy+i//256, cz+i//16%16))
    return found


def detect(room, barriers):
    """El aire interior debe estar cerrado en XZ y contener centro y llegada.

    Ignora techos de una capa: requieren columnas con >=4 Y distintos. Flood fill
    no une cercos por sus ramas exteriores y rechaza paredes de un solo lado.
    Para recintos irregulares se admite una envolvente rectangular si >=80% de
    ella es interior; si no, se conserva el radio y se informa sin barreras.
    """
    x, y, z = room['center']
    cols = defaultdict(set)
    for a, b, c in barriers:
        if abs(a-x)<=100 and abs(c-z)<=100 and y-15<=b<=y+70:
            cols[a, c].add(b)
    walls = {k for k, v in cols.items() if len(v)>=4}
    fallback = [round(v,6) for v in (x-room['radius'], z-room['radius'], x+room['radius'], z+room['radius'])]
    seed = (math.floor(x), math.floor(z))
    if seed in walls:
        return fallback, set(), walls
    interior = {seed}
    queue = [seed]
    for a, c in queue:
        if abs(a-x)>=100 or abs(c-z)>=100:
            return fallback, set(), walls
        for n in ((a-1,c), (a+1,c), (a,c-1), (a,c+1)):
            if n not in interior and n not in walls:
                interior.add(n)
                queue.append(n)
    ax, _, az = room['arrival']
    if (math.floor(ax),math.floor(az)) not in interior:
        return fallback, set(), walls
    x1, z1 = min(a for a,c in interior), min(c for a,c in interior)
    x2, z2 = max(a for a,c in interior)+1, max(c for a,c in interior)+1
    if min(x2-x1,z2-z1)<10 or len(interior)/(x2-x1)/(z2-z1)<.8:
        return fallback, set(), walls
    # Rayos normales desde el aire junto a cada extremo: recogen el espesor
    # real sin seguir las prolongaciones tangenciales hacia caminos vecinos.
    selected = set()
    for a,c in interior:
        directions=[]
        if a-x1<4:directions.append((-1,0))
        if x2-a<=4:directions.append((1,0))
        if c-z1<4:directions.append((0,-1))
        if z2-c<=4:directions.append((0,1))
        for dx,dz in directions:
            n=(a+dx,c+dz)
            if n not in walls:continue
            for step in range(1,9):
                n=(a+dx*step,c+dz*step)
                if n not in walls:break
                selected.add(n)
    if not selected:return fallback,set(),walls
    # Cerrar las esquinas diagonales dentro de la envolvente medida por rayos.
    loX,hiX=min(a for a,c in selected),max(a for a,c in selected)
    loZ,hiZ=min(c for a,c in selected),max(c for a,c in selected)
    q=list(selected)
    for a,c in q:
        for n in ((a-1,c),(a+1,c),(a,c-1),(a,c+1)):
            if n in walls and n not in selected and loX<=n[0]<=hiX and loZ<=n[1]<=hiZ:
                selected.add(n);q.append(n)
    return [x1,z1,x2,z2], selected, walls


def boxes(points):
    """Cubos disjuntos de posiciones originales, sin agregar un solo bloque de aire."""
    todo = set(points)
    out = []
    while todo:
        x,y,z = min(todo)
        y2=y
        while (x,y2+1,z) in todo:
            y2+=1
        x2=x
        while all((x2+1,b,z) in todo for b in range(y,y2+1)):
            x2+=1
        z2=z
        while all((a,b,z2+1) in todo for a in range(x,x2+1) for b in range(y,y2+1)):
            z2+=1
        for a in range(x,x2+1):
            for b in range(y,y2+1):
                for c in range(z,z2+1):
                    todo.remove((a,b,c))
        out.append(((x,y,z),(x2,y2,z2)))
    return out


def preview(world, items):
    from PIL import Image, ImageDraw
    im = Image.new('RGB', (620*len(items),650), '#202530')
    draw = ImageDraw.Draw(im)
    for index,(r,rect,selected,walls) in enumerate(items):
        x,_,z=r['center'];bounds=[min(x-105,rect[0]-5),min(z-105,rect[1]-5),
                                max(x+105,rect[2]+5),max(z+105,rect[3]+5)]
        scale=min(560/(bounds[2]-bounds[0]),520/(bounds[3]-bounds[1]))
        def p(a,c):return (index*620+30+(a-bounds[0])*scale,55+(c-bounds[1])*scale)
        draw.text((index*620+20,15),r['name']+' / '+('cerco' if selected else 'sin barreras'),fill='white')
        for a,c in walls:
            px,pz=p(a,c);draw.rectangle((px,pz,px+2,pz+2),fill='#ef4545')
        a,c,b,d=rect
        draw.rectangle((*p(a,c),*p(b,d)),outline='#62ed99',width=2)
        for pt,color in ((r['center'],'cyan'),(r['arrival'],'yellow')):
            px,pz=p(pt[0],pt[2]);draw.ellipse((px-4,pz-4,px+4,pz+4),fill=color)
        draw.text((index*620+20,595),str(rect),fill='white')
        draw.text((index*620+20,620),'rojo=barrera verde=zona cyan=centro amarillo=llegada',fill='white')
    dest=ROOT/'build/previews'/f'zonas_{world}.png'
    dest.parent.mkdir(parents=True,exist_ok=True);im.save(dest)


def terrain_report(folder, room, rect):
    from mobs.terreno import get, solid, AIR
    x1,z1,x2,z2=map(int,rect);y=round(room['center'][1])
    lines=[]
    for side,points in [('oeste',[(x1-1,z) for z in range(z1,z2)]),
                        ('este',[(x2,z) for z in range(z1,z2)]),
                        ('norte',[(x,z1-1) for x in range(x1,x2)]),
                        ('sur',[(x,z2) for x in range(x1,x2)])]:
        walk=[];void=[]
        for x,z in points:
            try:
                floors=[h for h in range(y-15,y+6) if solid(get('bosque',x,h-1,z,folder))
                        and all(get('bosque',x,h+i,z,folder) in AIR for i in (0,1))]
                if floors:walk.append((x,min(floors,key=lambda h:abs(h-y)),z))
                elif all(get('bosque',x,h,z,folder) in AIR for h in range(y-15,y+2)):void.append((x,z))
            except FileNotFoundError:
                lines.append(f'- {side}: faltan chunks; revision obligatoria.');break
        lines.append(f'- {side}: {len(walk)}/{len(points)} columnas con piso y dos bloques libres a Y {y-15}..{y+5}; '
                     f'{len(void)} sin apoyo en ese rango. Ejemplos transitables: {walk[::max(1,len(walk)//4)][:4]}.')
    return '\n'.join(lines)


def generate(folder):
    rooms=catalog();byworld=defaultdict(list)
    for r in rooms:byworld[r['world']].append(r)
    zones={};report=[];terrain=[];removal=set();bosque_points=set()
    for world,group in byworld.items():
        points=read_barriers(folder,world,group);items=[]
        if world=='bosque':bosque_points=set(points)
        for r in group:
            rect,selected,walls=detect(r,points)
            original=rect[:]
            if r['key']=='bosque':
                if not selected:raise ValueError('Bosque sin cerco claro: '+r['id'])
                rect=[rect[0]-4,rect[1]-4,rect[2]+4,rect[3]+4]
                # Solo las posiciones realmente barrera; incluye toda su altura.
                removal.update(p for p in points if (p[0],p[2]) in selected)
            radius=math.ceil(math.sqrt(max((a-r['center'][0])**2+(c-r['center'][2])**2
                                 for a in (rect[0],rect[2]) for c in (rect[1],rect[3]))+70**2))
            zones[r['id']]=rect+[int(bool(selected)),radius]
            label='cerco' if selected else 'sin barreras (radio anterior)'
            row=f'| {world} | {r["name"]} | {rect[0]}..{rect[2]} | {rect[1]}..{rect[3]} | {label} | {radius} |'
            report.append(row);print(row,flush=True)
            items.append((r,rect,selected,walls))
            if r['key']=='bosque':
                terrain.extend(['',f'Interior original {r["name"]}: `{original}`.',
                               terrain_report(folder,r,rect),''])
        preview(world,items)
    DATA.write_text(json.dumps(zones,ensure_ascii=False,indent=2)+'\n','utf8')
    dest=ROOT/'build/deploy';dest.mkdir(parents=True,exist_ok=True)
    cuboids=boxes(removal)
    # Verificacion exhaustiva del respaldo, antes de emitir comandos destructivos.
    restored={(x,y,z) for lo,hi in cuboids for x in range(lo[0],hi[0]+1)
              for y in range(lo[1],hi[1]+1) for z in range(lo[2],hi[2]+1)}
    assert restored==removal
    # Retiro: regiones finas XZ con barrier->air. Inverso: cuboides 100% barrera.
    slabs=[]
    for lo,hi in boxes({(x,0,z) for x,y,z in removal}):
        pts=[p for p in removal if lo[0]<=p[0]<=hi[0] and lo[2]<=p[2]<=hi[2]]
        slabs.append(((lo[0],min(p[1] for p in pts),lo[2]),
                      (hi[0],max(p[1] for p in pts),hi[2])))
    affected={p for p in bosque_points if any(all(a<=v<=b for a,v,b in zip(lo,p,hi)) for lo,hi in slabs)}
    assert affected==removal, 'Una region de retiro toca barreras ajenas al cerco'
    for reverse in (False,True):
        lines=['# SOLO CONSOLA: un slash (world/pos1/pos2/replace/set son comandos / de WorldEdit).',
               '# En chat usar //world, //pos1, //pos2, //replace, //set.',
               '# Retiro/restauracion exacta de barreras; no modificar terreno entre ambas operaciones.',
               f'# {len(removal)} barreras originales; {len(slabs)} regiones de retiro / {len(cuboids)} cuboides de restauracion por mundo.']
        for world in ['bosque']+[f'bosque_{i}' for i in range(2,7)]:
            lines.append('/world '+world)
            for lo,hi in (cuboids if reverse else slabs):
                lines.extend(['/pos1 '+','.join(map(str,lo)), '/pos2 '+','.join(map(str,hi)),
                              '/set barrier' if reverse else '/replace barrier air'])
        (dest/('bosque-barreras-18-11'+('-deshacer' if reverse else '')+'.txt')).write_text('\n'.join(lines)+'\n','utf8')
    (dest/'zonas-pelea-medicion-18-11.md').write_text(
        '# Medicion de cercos (18/11/2026)\n\n'
        'Lectura local; sin cambios en mapas. Rectangulos en coordenadas de caras de bloque.\n'
        'Deteccion: columnas de >=4 barreras, busqueda ±100 XZ / -15..+70 Y; interior cerrado con centro y llegada.\n'
        'Techos y cercos incompletos no definen zonas. Envolvente del interior si ocupacion >=80%.\n'
        'Copias _2.._6 usan las mismas medidas; verificar igualdad con copia real antes de ejecutar comandos.\n\n'
        '| Mundo base | Sala | X | Z | Origen | Radio 3D hasta esquina (+70 Y) |\n|---|---|---|---|---|---|\n'
        +'\n'.join(report)+'\n\n'+'\n'.join(terrain)+'\n\n'
        '**Terreno Bosque:** un piso transitable fuera del +4 permite continuar; un vacio permite caer. '
        'Este muestreo de columnas NO certifica un cierre natural ni conectividad caminable. '
        'Retirar barreras queda pendiente de revision de Claude/dueno de los lados indicados; '
        'el plugin protege el rectangulo solo mientras hay pelea. No modificar otros cercos.\n'
        f'\nRespaldo exacto comprobado: {len(removal)} bloques originales por mundo, {len(cuboids)} cuboides disjuntos. '
        'El inverso usa set barrier exclusivamente sobre esos bloques. No usar replace air barrier.\n','utf8')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--maps',type=Path,required=True)
    generate(parser.parse_args().maps.resolve())
