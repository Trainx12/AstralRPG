"""Inspeccion de bloques y vistas CPU PRIVADAS, no capturas de Minecraft."""
import argparse
from collections import Counter, deque
import gzip
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'datapack-src'))
from mapas import NBT, color
from santuario_azeroth import ARRIVAL, BOSSES, CHEST, GUIDE, BOUNDS


def inspect(root):
    root=root.resolve()
    if not root.is_relative_to(ROOT/'.local'):
        raise ValueError('Las vistas del mapa ajeno deben quedar en .local')
    x0,z0,x1,z1=BOUNDS
    names=['minecraft:air'];indices={names[0]:0}
    a=np.zeros((384,z1-z0+1,x1-x0+1),dtype=np.uint16)
    tiles=Counter();versions=set();signs={};original_signs={}
    for path in (root/'legacy').glob('*.nbt'):
        c=NBT(gzip.decompress(path.read_bytes())).root()['Level']
        for e in c.get('TileEntities',[]):
            if e['id']=='Sign':
                original_signs[(e['x'],e['y'],e['z'])]=tuple(e.get(f'Text{i}','') for i in range(1,5))
    for path in (root/'trimmed').glob('*.nbt'):
        c=NBT(gzip.decompress(path.read_bytes())).root();versions.add(c['DataVersion'])
        cx,cz=c['xPos']*16-x0,c['zPos']*16-z0
        for s in c['sections']:
            state=s.get('block_states',{});palette=state.get('palette',[])
            if not palette:continue
            lookup=[]
            for entry in palette:
                n=entry['Name']
                if n not in indices:indices[n]=len(names);names.append(n)
                lookup.append(indices[n])
            if len(palette)==1:decoded=np.full(4096,lookup[0],dtype=np.uint16)
            else:
                bits=max(4,(len(palette)-1).bit_length());per=64//bits
                words=np.array(state['data'],dtype=np.int64).view(np.uint64)
                loc=np.arange(4096,dtype=np.uint64)
                decoded=np.array(lookup,dtype=np.uint16)[((words[loc//per]>>((loc%per)*bits))&((1<<bits)-1)).astype(int)]
            yy=s['Y']*16+64
            a[yy:yy+16,cz:cz+16,cx:cx+16]=decoded.reshape(16,16,16)
        for e in c.get('block_entities',[]):
            tiles[e['id']]+=1
            if e['id']=='minecraft:sign':
                signs[(e['x'],e['y'],e['z'])]=tuple(m.get('text','') for m in e['front_text']['messages'])
            if e.get('Items') or e.get('LootTable') or e.get('RecordItem'):
                raise ValueError('Inventario original no vaciado')
    if signs!=original_signs or len(signs)!=8:
        raise ValueError('La conversion altero o perdio carteles')
    air=np.isin(a,[i for i,n in enumerate(names) if n in ('minecraft:air','minecraft:cave_air','minecraft:void_air')])
    count=int(np.count_nonzero(~air))
    source=json.loads((root/'conversion.json').read_text())
    if count!=source['non_air_before']:raise ValueError(f'Perdida de bloques: {count} != {source["non_air_before"]}')
    def clear(p,width,height):
        x,y,z=int(p[0])-x0,int(p[1])+64,int(p[2])-z0;r=width//2
        return bool(np.all(~air[y-1,z-r:z+r+1,x-r:x+r+1]) and np.all(air[y:y+height,z-r:z+r+1,x-r:x+r+1]))
    for p in BOSSES:
        if not clear(p,5,9):raise ValueError(f'Jefe sin espacio: {p}')
    for p in (ARRIVAL,CHEST,GUIDE):
        if not clear(p,1,3):raise ValueError(f'Punto obstruido: {p}')
    y=57+64;walk=(~air[y-1]) & np.all(air[y:y+3],axis=0)
    start=(int(ARRIVAL[2])-z0,int(ARRIVAL[0])-x0);seen={start};q=deque([start])
    while q:
        z,x=q.popleft()
        for dz,dx in ((1,0),(-1,0),(0,1),(0,-1)):
            to=z+dz,x+dx
            if 0<=to[0]<walk.shape[0] and 0<=to[1]<walk.shape[1] and walk[to] and to not in seen:
                seen.add(to);q.append(to)
    for p in (*BOSSES,CHEST,GUIDE):
        if (int(p[2])-z0,int(p[0])-x0) not in seen:raise ValueError(f'Punto sin camino: {p}')
    previews=root/'build/previews';previews.mkdir(parents=True,exist_ok=True)
    ys=np.max(np.where(~air,np.arange(384)[:,None,None],0),axis=0)
    tops=np.take_along_axis(a,ys[None],axis=0)[0]
    rgb=np.array([[color(names[int(v)],int(h)-64) for v,h in zip(row,hr)] for row,hr in zip(tops,ys)],dtype=np.uint8)
    im=Image.fromarray(rgb).resize((1040,1040));draw=ImageDraw.Draw(im)
    for label,p in [('Entrada',ARRIVAL),*[(str(i+1),p) for i,p in enumerate(BOSSES)],('Cofre',CHEST)]:
        x,z=(p[0]-x0)*5,(p[2]-z0)*5
        draw.ellipse((x-4,z-4,x+4,z+4),fill='red');draw.text((x+6,z),label,fill='white')
    draw.text((10,10),'VISTA CPU DEL MAPA - NO ES CAPTURA EN JUEGO',fill='white')
    im.save(previews/'santuario-azeroth-planta.png')
    # Proyeccion de las superficies con color por material, sin texturas ajenas.
    im=Image.new('RGB',(1200,1000),(12,10,20));draw=ImageDraw.Draw(im)
    yy,zz,xx=np.nonzero(~air & np.concatenate((air[1:],np.ones_like(air[:1])),axis=0))
    order=np.argsort(xx+zz+yy*.01)
    for i in order:
        x,z,y=int(xx[i]),int(zz[i]),int(yy[i])-64
        sx=600+(x-z)*2.4;sy=330+(x+z)*.95-y*2.4
        draw.rectangle((sx,sy,sx+3,sy+2),fill=color(names[int(a[yy[i],z,x])],y))
    draw.text((10,10),'PROYECCION CPU PRIVADA - SIN CLIENTE MINECRAFT',fill='white')
    im.save(previews/'santuario-azeroth-oblicua.png')
    report={'non_air_after':count,'blocks_preserved':True,'block_entities':dict(tiles),'sign_texts_preserved':True,
            'data_versions':sorted(versions),'boss_space':'5x5x9','connected_walkable_cells':len(seen),
            'all_points_connected':True,'previews':str(previews)}
    (root/'inspection.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('root',type=Path)
    inspect(p.parse_args().root)
