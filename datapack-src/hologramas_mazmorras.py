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

# Acertijos (pedido del dueno 13/11/2026), con el formato del de la Cumbre: titulo dorado y texto celeste.
# Posicion: captura F3 del dueno, unos 4.5 bloques sobre sus pies (el texto es doble).
def riddle(tag, world, pos, place, lines):
    # Mismo tamano que el de la Cumbre en el server: escala 2, ancho 400, sin sombra, vista 1.0.
    return dict(tag=tag, world=world, pos=pos, scale=2.0, line_width=400, shadow=0, view_range=1.0,
                text=[{'text':f'\u2736 El acertijo {place} \u2736\n','color':'gold','bold':True},
                      {'text':'\n'.join(lines),'color':'aqua','bold':False,'italic':True}])


RIDDLES = [
    riddle('astral.acertijo.forja', 'forja', (1530.5,228.0,1910.5), 'de la Forja',
           ['Quien se aferra a la orilla jamás probará la gloria.',
            'Desciende de tu refugio seguro y atraviésame sin miedo;',
            'mi sangre naranja quema a los cobardes,',
            'pero guía a los valientes hacia un altar oscuro en medio de la nada.']),
    riddle('astral.acertijo.santuario', 'exp_santuario', (33.8,111.5,-39.2), 'del Santuario',
           ['No intentes forzar la entrada del santuario;',
            'busca lo único que respira en este patio de piedra.',
            'Alcanza su copa, sigue el camino estrecho de la muralla',
            'y cuélate en las sombras del interior.',
            'Un pasillo oculto te guiará hasta su morador.']),
    riddle('astral.acertijo.oceano', 'oceano', (-2.4,24.0,11.7), 'del Océano',
           ['Desde el meridiano cero donde convergen los ejes del mundo,',
            'desplázate 419 metros hacia donde muere el día',
            'y proyecta 472 metros hacia la latitud plus',
            'y encontrarás la plataforma que te lleva al crustáceo gigante.']),
]


def commands(hints=None):
    lines=['# Cavernas: pistas de Minas Olvidadas. No modifica el terreno.',
           '# Posiciones de las capturas del dueno, texto unos 2.5 bloques sobre sus pies.']
    for hint in HINTS if hints is None else hints:
        world=hint.get('world','cavernas')
        x,y,z=hint['pos']; tag=hint['tag']
        text=json.dumps(hint['text'],ensure_ascii=False,separators=(',',':'))
        settings=(f'{{Tags:["{tag}"],Pos:[{x}d,{y}d,{z}d],billboard:"center",'
                  f'text:{text},line_width:{hint.get("line_width",300)},alignment:"center",shadow:{hint.get("shadow",1)}b,see_through:0b,'
                  f'background:1073741824,brightness:{{block:15,sky:15}},view_range:{hint.get("view_range",0.6)}f'
                  + (f',transformation:{{translation:[0f,0f,0f],left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],'
                     f'scale:[{hint["scale"]}f,{hint["scale"]}f,{hint["scale"]}f]}}' if 'scale' in hint else '') + '}')
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
    riddles=commands(RIDDLES)
    (path.parent/'acertijos.txt').write_text('\n'.join(riddles)+'\n',encoding='utf-8')
    print(path)
