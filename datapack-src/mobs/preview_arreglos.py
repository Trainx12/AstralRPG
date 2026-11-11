"""Renders CPU propios: todas las variantes y poses de esqueleto, sin arte ajeno."""
from copy import deepcopy
import math
from pathlib import Path
import re
from PIL import Image, ImageDraw
from mobs.build_models import preview3d
from mobs.creatures_tanda3b import skeleton, VARIANTS

ROOT=Path(__file__).resolve().parents[2]


def value(expression,t):
    if isinstance(expression,(int,float)): return expression
    # El generador solo usa estas expresiones Molang; no evalua codigo libre.
    match=re.fullmatch(r'math.sin\(q.anim_time \* 360 \* ([\d.]+) \+ (-?[\d.]+)\) \* (-?[\d.]+)',expression)
    if not match: raise ValueError(expression)
    speed,phase,amp=map(float,match.groups())
    return math.sin(math.radians(t*360*speed+phase))*amp


def posed(model,animation,t):
    model=deepcopy(model)
    for bone,channels in model.anims[animation][2].items():
        if 'rotation' in channels:
            model.bones[bone]['rotation']=[a+value(b,t) for a,b in zip(model.bones[bone]['rotation'],channels['rotation'])]
        if 'position' in channels:
            delta=[value(v,t) for v in channels['position']]
            children={bone}
            while True:
                extra={b for b,d in model.bones.items() if d['parent'] in children}
                if extra<=children:break
                children|=extra
            for b in children:
                model.bones[b]['origin']=[a+b for a,b in zip(model.bones[b]['origin'],delta)]
            for c in model.cubes:
                if c['bone'] in children:
                    for field in ('from','to','origin'):
                        if c.get(field) is not None:c[field]=[a+b for a,b in zip(c[field],delta)]
    return model


def generate():
    w,h=1120,340
    sheet=Image.new('RGB',(w,h*len(VARIANTS)),'#171e27')
    draw=ImageDraw.Draw(sheet)
    for row,kind in enumerate(VARIANTS):
        model=skeleton(kind)
        for col,(animation,t) in enumerate((('idle',.75),('walk',.25),('attack',.325))):
            m=posed(model,animation,t);texture=m.export()[1]
            for side,yaw in enumerate((0,90)):
                im=preview3d(m,texture,yaw=yaw,pitch=0,scale=6)
                im.thumbnail((178,292))
                x=col*372+side*180;y=row*h+30
                sheet.paste(im,(x+(178-im.width)//2,y))
            draw.text((col*372+5,row*h+8),f'{kind} | {animation} t={t}s | frente / costado',fill='white')
    dest=ROOT/'build/previews/esqueletos-brazos.png';dest.parent.mkdir(parents=True,exist_ok=True)
    sheet.save(dest)


if __name__=='__main__': generate()
