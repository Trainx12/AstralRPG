"""Renders CPU propios: todas las variantes y poses de esqueleto, sin arte ajeno."""
from copy import deepcopy
import math
from pathlib import Path
import re
import ast
from PIL import Image, ImageDraw
from mobs.build_models import preview3d
from mobs.creatures_tanda3b import skeleton, VARIANTS

ROOT=Path(__file__).resolve().parents[2]


def value(expression,t):
    if isinstance(expression,(int,float)): return expression
    linear=re.fullmatch(r'q.anim_time \* (-?[\d.]+)',expression)
    if linear:return t*float(linear[1])
    # El generador solo usa estas expresiones Molang; no evalua codigo libre.
    match=re.fullmatch(r'math.sin\(q.anim_time \* 360 \* ([\d.]+) \+ (-?[\d.]+)\) \* (-?[\d.]+)',expression)
    if not match:
        # Subconjunto aritmetico de Molang, sin acceso a Python ni atributos.
        source=expression.replace('q.anim_time','t')
        for fn in ('sin','cos','sqrt','atan'):source=source.replace('math.'+fn,fn)
        tree=ast.parse(source,mode='eval')
        allowed=(ast.Expression,ast.BinOp,ast.UnaryOp,ast.Constant,ast.Name,ast.Load,
                 ast.Call,ast.Add,ast.Sub,ast.Mult,ast.Div,ast.USub,ast.UAdd)
        if any(not isinstance(n,allowed) for n in ast.walk(tree)):raise ValueError(expression)
        functions={'sin':lambda x:math.sin(math.radians(x)),'cos':lambda x:math.cos(math.radians(x)),'atan':lambda x:math.degrees(math.atan(x)),'sqrt':math.sqrt,'t':t}
        if any(isinstance(n,ast.Name) and n.id not in functions for n in ast.walk(tree)):raise ValueError(expression)
        return eval(compile(tree,'<Molang preview>','eval'),{'__builtins__':{}},functions)
    speed,phase,amp=map(float,match.groups())
    return math.sin(math.radians(t*360*speed+phase))*amp


def keyframes(frames,t):
    """Fotogramas [(segundo,(x,y,z))]: interpolacion lineal (BetterModel usa catmullrom, aca alcanza)."""
    if t<=frames[0][0]: return frames[0][1]
    for (t0,a),(t1,b) in zip(frames,frames[1:]):
        if t<=t1:
            k=(t-t0)/(t1-t0) if t1>t0 else 1
            return tuple(x+(y-x)*k for x,y in zip(a,b))
    return frames[-1][1]


def posed(model,animation,t):
    model=deepcopy(model)
    for bone,channels in model.anims[animation][2].items():
        channels={c:(keyframes(v,t) if isinstance(v,list) else v) for c,v in channels.items()}
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
        if 'scale' in channels:
            factors=[value(v,t) for v in channels['scale']];origin=model.bones[bone]['origin']
            children={bone}
            while True:
                extra={b for b,d in model.bones.items() if d['parent'] in children}
                if extra<=children:break
                children|=extra
            for b in children:
                model.bones[b]['origin']=[o+(v-o)*f for o,v,f in zip(origin,model.bones[b]['origin'],factors)]
            for c in model.cubes:
                if c['bone'] in children:
                    for field in ('from','to','origin'):
                        if c.get(field) is not None:c[field]=[o+(v-o)*f for o,v,f in zip(origin,c[field],factors)]
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
    # Detalle del arquero, tres vistas por animacion.
    detail=Image.new('RGB',(1080,1020),'#171e27');dd=ImageDraw.Draw(detail)
    for row,(animation,t) in enumerate((('idle',.75),('walk',.25),('attack',.325))):
        m=posed(skeleton('arquero'),animation,t);texture=m.export()[1]
        for col,yaw in enumerate((0,90,35)):
            im=preview3d(m,texture,yaw=yaw,pitch=0,scale=8);im.thumbnail((330,300))
            detail.paste(im,(col*360+(330-im.width)//2,row*340+30))
            dd.text((col*360+10,row*340+8),f'{animation} | yaw {yaw} | render CPU',fill='white')
    detail.save(ROOT/'build/previews/arco-arquero-animaciones.png')
    dest=ROOT/'build/previews/esqueletos-brazos.png';dest.parent.mkdir(parents=True,exist_ok=True)
    sheet.save(dest)


if __name__=='__main__': generate()
