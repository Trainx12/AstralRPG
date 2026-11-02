"""Pistas elegidas por el dueno mediante capturas. Solo text_display, sin bloques."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HINTS = [
    dict(tag='astral.pista.tumba.inicio', world='exp_desierto', pos=(180.3,107.8,134.783),
         text=[{'text':'Para encontrar la mazmorra\n','color':'white'},
               {'text':'"Tumba del Rey de Arena"\n','color':'gold','bold':True},
               {'text':'debes primero ver lo que queda del Rey','color':'white','bold':False}]),
    dict(tag='astral.pista.minas.inicio', pos=(154.9,105.6,108.976),
         text=[{'text':'Para encontrar la mazmorra de\n','color':'white'},
               {'text':'"Minas Olvidadas"\n','color':'gold','bold':True},
               {'text':'debes buscarla en las profundidades\nde este mapa','color':'white','bold':False}]),
    dict(tag='astral.pista.minas.profundidad1', pos=(137.421,74.5,109.607),
         text=[{'text':'Sigue explorando las profundidades\ny lo encontrarás','color':'gold'}]),
    dict(tag='astral.pista.minas.profundidad2', pos=(164.186,73.4,150.652),
         text=[{'text':'Sigue explorando las profundidades\ny lo encontrarás','color':'gold'}]),
    dict(tag='astral.pista.minas.cerca1', pos=(98.366,46.5,165.289),
         text=[{'text':'Cada vez más cerca','color':'gold'}]),
    dict(tag='astral.pista.minas.cerca2', pos=(122.815,44.6,179.578),
         text=[{'text':'Cada vez más cerca','color':'gold'}]),
    dict(tag='astral.pista.minas.cerca3', pos=(176.924,51.3,99.376),
         text=[{'text':'Cada vez más cerca','color':'gold'}]),
    dict(tag='astral.pista.minas.tramo1', pos=(166.119,25.8,179.571),
         text=[{'text':'Estás en el último tramo','color':'#B86AFF'}]),
    dict(tag='astral.pista.minas.tramo2', pos=(157.513,50.6,185.689),
         text=[{'text':'Estás en el último tramo','color':'#B86AFF'}]),
    dict(tag='astral.pista.minas.tramo3', pos=(140.838,-5.2,109.671),
         text=[{'text':'Estás en el último tramo','color':'#B86AFF'}]),
]


def commands(hints=None):
    lines=['# Cavernas: pistas de Minas Olvidadas. No modifica el terreno.',
           '# Posiciones de las capturas del dueno, texto unos 2.5 bloques sobre sus pies.']
    for hint in HINTS if hints is None else hints:
        world=hint.get('world','cavernas')
        x,y,z=hint['pos']; tag=hint['tag']
        text=json.dumps(hint['text'],ensure_ascii=False,separators=(',',':'))
        settings=(f'{{Tags:["{tag}"],Pos:[{x}d,{y}d,{z}d],billboard:"center",'
                  f'text:{text},line_width:300,alignment:"center",shadow:1b,see_through:0b,'
                  'background:1073741824,brightness:{block:15,sky:15},view_range:0.6f}')
        lines += [f'execute in minecraft:{world} run forceload add {int(x)} {int(z)}',
                  f'execute in minecraft:{world} unless entity @e[type=minecraft:text_display,tag={tag}] '
                  f'run summon minecraft:text_display {x} {y} {z} {settings}',
                  f'execute in minecraft:{world} as @e[type=minecraft:text_display,tag={tag}] run data merge entity @s {settings}',
                  f'execute in minecraft:{world} run data get entity @e[type=minecraft:text_display,tag={tag},limit=1] text',
                  f'execute in minecraft:{world} run forceload remove {int(x)} {int(z)}']
    return lines


if __name__=='__main__':
    path=ROOT/'build/mapas_exploracion/pistas-minas.txt'
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text('\n'.join(commands())+'\n',encoding='utf-8')
    private=ROOT/'.local/mapas/astral-nuevos/pistas-minas.json'
    private.parent.mkdir(parents=True,exist_ok=True)
    private.write_text(json.dumps(commands(),ensure_ascii=False),encoding='utf-8')
    desert=commands([h for h in HINTS if h.get('world')=='exp_desierto'])
    (path.parent/'pistas-tumba.txt').write_text('\n'.join(desert)+'\n',encoding='utf-8')
    (private.parent/'pistas-tumba.json').write_text(json.dumps(desert,ensure_ascii=False),encoding='utf-8')
    print(path)
