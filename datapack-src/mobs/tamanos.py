"""Caja estatica del modelo existente y atributos vanilla desde un mismo dato."""
from functools import lru_cache
import itertools
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
VANILLA={'FOX':(.6,.7),'CHICKEN':(.4,.7),'VEX':(.4,.8),'SPIDER':(1.4,.9),
         'PHANTOM':(.9,.5),'HUSK':(.6,1.95),'RAVAGER':(1.95,2.2),'IRON_GOLEM':(1.4,2.7),'EVOKER':(.6,1.95)}
SPECIAL={'astral_yeti_cumbre':('astral_yeti',16.0),
         'astral_golem_forja_mazmorra':('astral_golem_forja',8.0)}

def rotate(p, origin, angles):
    x,y,z=[p[i]-origin[i] for i in range(3)]
    for axis,a in enumerate(angles):
        s,c=math.sin(math.radians(a)),math.cos(math.radians(a))
        if axis==0: y,z=y*c-z*s,y*s+z*c
        elif axis==1: x,z=x*c+z*s,-x*s+z*c
        else: x,y=x*c-y*s,x*s+y*c
    return tuple(v+o for v,o in zip((x,y,z),origin))

@lru_cache(maxsize=None)
def bounds(model):
    d=json.loads((ROOT/'build/models'/f'{model}.bbmodel').read_text(encoding='utf-8'))
    elements={e['uuid']:e for e in d['elements'] if e.get('type','cube')=='cube'}
    groups={g['uuid']:g for g in d.get('groups',[])}
    points=[]
    def visit(node,parents):
        if isinstance(node,str):
            e=elements.get(node)
            if not e: return
            inflate=e.get('inflate',0)
            for corner in itertools.product(*[(e['from'][i]-inflate,e['to'][i]+inflate) for i in range(3)]):
                p=rotate(corner,e.get('origin',[0,0,0]),e.get('rotation',[0,0,0]))
                for g in reversed(parents): p=rotate(p,g.get('origin',[0,0,0]),g.get('rotation',[0,0,0]))
                points.append(p)
        else:
            g=groups.get(node['uuid'],node)
            for child in node.get('children',[]): visit(child,parents+[g])
    for node in d['outliner']: visit(node,[])
    return tuple((min(p[i] for p in points)/16,max(p[i] for p in points)/16) for i in range(3))

def dimensions(model,s):
    return tuple((hi-lo)*s for lo,hi in bounds(model))

def scale(model,s,entity):
    return round(min(16,dimensions(model,s)[1]/VANILLA[entity][1]),6)

def skills(model,s,entity):
    sc=scale(model,s,entity)
    guard='execute unless dimension minecraft:santuario unless dimension minecraft:santuario_interstellar run '
    return [f'command{{c="execute at <caster.uuid> run {guard}attribute <caster.uuid> minecraft:scale base set {sc}"}} @self',
            f'command{{c="execute at <caster.uuid> run {guard}attribute <caster.uuid> minecraft:step_height base set {max(.6,min(8,sc*.6)):.6f}"}} @self']

def rows():
    from mobs.mythic import MOBS,ELITES,ANCESTRALES
    out=[]
    for mid,d in MOBS.items():
        if d['kind']=='montura': continue
        s=2.0 if d['kind']=='jefe' else 1.0
        out.append((mid,mid,s,d['type']))
        if mid in ELITES: out.append((mid+'_elite',mid,1.35,d['type']))
        if mid in ANCESTRALES: out.append((mid+'_ancestral',mid,2.0,d['type']))
    out.extend((mid,model,s,MOBS[model]['type']) for mid,(model,s) in SPECIAL.items())
    out.append(('astral_mina_guardian','astral_golem_forja',2.0,'IRON_GOLEM'))
    return out

def preview():
    from PIL import Image,ImageDraw,ImageFont
    data=rows(); unit=14; cellw=540; cols=4
    heights=[max(dimensions(m,s)[1] for _,m,s,_ in data[i:i+cols])*unit+125 for i in range(0,len(data),cols)]
    offsets=[65+sum(heights[:i]) for i in range(len(heights))]
    im=Image.new('RGB',(cols*cellw,math.ceil(sum(heights))+75),(19,24,35)); draw=ImageDraw.Draw(im)
    try: font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',15)
    except OSError: font=ImageFont.load_default()
    draw.text((20,12),'AstralRPG - tamanos medidos de los modelos existentes (pose de reposo)',font=font,fill='#ffffff')
    draw.text((20,35),'Escala unica: 14 px = 1 bloque. Azul: modelo / naranja: caja vanilla. Blanco: jugador de 1,8 bloques.',font=font,fill='#99dce9')
    for i,(mid,model,s,entity) in enumerate(data):
        x=(i%cols)*cellw+10; bottom=offsets[i//cols]+heights[i//cols]-100
        w,h,_=dimensions(model,s); sc=scale(model,s,entity)
        draw.line((x,bottom,x+510,bottom),fill='#687386')
        draw.rectangle((x+12,bottom-1.8*unit,x+18,bottom-1.3*unit),fill='#ffffff')
        draw.rectangle((x+10,bottom-1.3*unit,x+20,bottom-.6*unit),fill='#ffffff')
        draw.rectangle((x+11,bottom-.6*unit,x+14,bottom),fill='#ffffff')
        draw.rectangle((x+16,bottom-.6*unit,x+19,bottom),fill='#ffffff')
        draw.text((x,bottom+4),'Jugador 1,8 b',font=font,fill='#ffffff')
        draw.rectangle((x+55,bottom-h*unit,x+55+w*unit,bottom),fill='#287494',outline='#6ed4ef',width=2)
        draw.rectangle((x+55,bottom-VANILLA[entity][1]*sc*unit,x+55+VANILLA[entity][0]*sc*unit,bottom),outline='#ffbf6b',width=2)
        draw.text((x,bottom+23),mid.removeprefix('astral_').replace('_',' '),font=font,fill='#ffffff')
        draw.text((x,bottom+43),f's={s:g} | alto {h:.2f} b | scale {sc:g}',font=font,fill='#99dce9')
        draw.text((x,bottom+62),f'Caja vanilla: alto {VANILLA[entity][1]*sc:.2f} b',font=font,fill='#ffbf6b')
    dest=ROOT/'build/previews/tamanos-jefes.png'; dest.parent.mkdir(parents=True,exist_ok=True); im.save(dest)

if __name__=='__main__': preview()
