"""Atlas, cartografia y portales: interfaces propias sobre la grilla vanilla.

Comparte medidas y tecnica de glifos con los servicios. Los descubrimientos
siguen siendo personales; el arte nunca concede permisos ni ejecuta viajes.
"""
import json
from pathlib import Path
from PIL import Image, ImageDraw
from escape_menu import text
from services_ui import png, SIZE, SPLIT
from market_ui import band_color

THEMES = {
    'principal': ('ATLAS ASTRAL', '#151f35', '#c5aa65', '#7ecfdd'),
    'expediciones': ('EXPEDICIONES', '#24342d', '#c5ad77', '#90c8a0'),
    'mazmorras': ('PORTALES RUNICOS', '#27232f', '#93859c', '#c88bdb'),
}
START, END = '\ue600', '\ue601'
GLYPHS = {k: tuple(chr(0xe610+i*4+j) for j in range(4)) for i,k in enumerate(THEMES)}
DESTINATIONS = ('bosque', 'tumba', 'mina', 'cumbre', 'forja', 'santuario')
LABELS = ('BOSQUE', 'TUMBA', 'MINAS', 'CUMBRE', 'FORJA', 'SANTUARIO')
COLORS = ('#85b777', '#dcb779', '#8eb6c5', '#adddec', '#ea9862', '#ceb0ed')
MAIN = ('expediciones', 'mazmorras', 'misiones', 'bazar', 'mascotas', 'cosmeticos', 'guia', 'spawn')
MAIN_LABELS = ('EXPLORAR', 'MAZMORRAS', 'CRONISTA', 'BAZAR', 'MASCOTAS', 'COSMETICOS', 'GUIA', 'LOBBY')


def regions(kind):
    if kind == 'principal':
        return [(key, [row*9+col for col in range(start,start+4)])
                for key,(row,start) in zip(MAIN, [(r,c) for r in range(1,5) for c in (0,5)])]
    return [(key, [row*9+col for row in range(r,r+2) for col in range(c,c+3)])
            for key,(r,c) in zip(DESTINATIONS, [(r,c) for r in (1,3) for c in (0,3,6)])]


def title(kind):
    return '&f'+START+''.join(GLYPHS[kind])+END


def star(draw,x,y,color,r=3):
    draw.line((x-r,y,x+r,y),fill=color)
    draw.line((x,y-r,x,y+r),fill=color)
    draw.point((x,y),fill='#fff2d2')


def emblem(draw,key,x,y,color):
    """Siluetas pequenas propias de cada bioma o servicio."""
    if key == 'bosque':
        draw.rectangle((x-1,y+2,x+1,y+7),fill='#b59264')
        for dy,w in ((-6,3),(-3,5),(0,6)):
            draw.polygon([(x,y+dy-3),(x-w,y+dy+3),(x+w,y+dy+3)],fill=color)
    elif key == 'tumba':
        draw.polygon([(x,y-7),(x-8,y+6),(x+8,y+6)],fill=color)
        draw.line((x,y-7,x+3,y+6),fill='#866640')
    elif key == 'mina':
        draw.line((x-5,y+6,x+4,y-5),fill='#b59264',width=2)
        draw.line((x-6,y-5,x+5,y-5,x+8,y-1),fill=color,width=3)
    elif key == 'cumbre':
        draw.polygon([(x,y-7),(x-8,y+6),(x+8,y+6)],fill='#648ca1')
        draw.polygon([(x,y-7),(x-4,y),(x,y-2),(x+4,y)],fill=color)
    elif key == 'forja':
        draw.polygon([(x,y-8),(x+1,y-2),(x+5,y-5),(x+7,y+3),(x+3,y+7),(x-4,y+7),(x-7,y+2)],fill=color)
        draw.polygon([(x,y-1),(x+3,y+5),(x-3,y+5)],fill='#ffe2a3')
    elif key in ('santuario','mazmorras'):
        draw.rectangle((x-6,y-6,x+6,y+7),outline=color,width=2)
        draw.rectangle((x-3,y-3,x+3,y+7),fill='#675187')
        star(draw,x,y,color,2)
    else:
        draw.ellipse((x-7,y-7,x+7,y+7),outline=color)
        draw.polygon([(x,y-6),(x+3,y),(x,y+6),(x-3,y)],fill=color)
        draw.point((x,y),fill='#fff2d2')


def card(kind,key,locked=False):
    _,fill,edge,accent=THEMES[kind]
    main=kind=='principal'
    width,height=(72,18) if main else (54,36)
    im=Image.new('RGBA',(width,height),fill);d=ImageDraw.Draw(im)
    color=accent if main else COLORS[DESTINATIONS.index(key)]
    if locked: color='#7f7a84'
    d.rectangle((0,0,width-1,height-1),outline=edge)
    d.rectangle((2,2,width-3,height-3),outline='#47505a' if not locked else '#44414b')
    if main:
        star(d,7,8,color,2)
        text(im,MAIN_LABELS[MAIN.index(key)],(41,5),color='#f4e4be')
    else:
        emblem(d,key,27,12,color)
        text(im,LABELS[DESTINATIONS.index(key)],(27,25),color=color)
        if locked:
            d.rectangle((42,10,48,16),fill='#342f3c',outline='#b4a7b9')
            d.arc((43,6,47,13),180,360,fill='#b4a7b9')
    return im


def panel(kind):
    caption,fill,edge,accent=THEMES[kind]
    im=Image.new('RGBA',SIZE);d=ImageDraw.Draw(im)
    d.rectangle((7,10,216,275),fill='#10121c',outline=edge,width=2)
    d.rectangle((11,14,212,271),fill=fill,outline='#4a4351',width=2)
    # Bloques y remaches del marco: siempre fuera de las casillas utilizables.
    for y in range(40,264,14):
        for x in (12,201):
            d.rectangle((x,y,x+10,y+12),fill='#3d3945' if kind=='mazmorras' else '#3a403e',outline='#171b25')
            d.point((x+2,y+2),fill=edge)
    for x in (16,207):
        for y in (19,263):
            star(d,x,y,accent,5)
    d.rectangle((29,12,194,37),fill='#101923',outline=edge)
    text(im,caption,(112,20),color='#f8e7c0')
    # Bandeau decoratif: constellation, carte ou chaine runique.
    if kind=='expediciones':
        d.line((39,45,67,40,95,47,124,41,155,47,182,41),fill=edge)
        for x,y in ((39,45),(95,47),(155,47)):
            star(d,x,y,accent,2)
    elif kind=='mazmorras':
        for x in range(38,188,12):d.rectangle((x,42,x+7,46),outline=edge)
    else:
        d.line((40,45,73,40,112,47,153,40,184,45),fill='#56677e')
        for x,y in ((40,45),(73,40),(112,47),(153,40),(184,45)):star(d,x,y,accent,2)
    # El fondo cubre la ventana vanilla; solo las areas reales son transparentes.
    d.rectangle((24,56,199,258),fill=fill)
    for _,slots in regions(kind):
        s=slots[0];w,h=(72,18) if kind=='principal' else (54,36)
        x,y=31+s%9*18,57+s//9*18
        d.rectangle((x,y,x+w-1,y+h-1),fill=(0,0,0,0))
    for slot in (4,8,45,49,51,53):
        x,y=31+slot%9*18,57+slot//9*18
        d.rectangle((x,y,x+17,y+17),outline=edge)
        d.rectangle((x+1,y+1,x+16,y+16),fill=(0,0,0,0))
    d.rectangle((31,168,192,177),fill=band_color(edge))
    for row in (*range(3),4):
        for col in range(9):
            x,y=31+col*18,179+row*18 if row<3 else 237
            d.rectangle((x,y,x+17,y+17),outline=edge)
            d.rectangle((x+1,y+1,x+16,y+16),fill=(0,0,0,0))
    return im


def assets():
    files,providers={},[];advances={START:-32,END:32}
    for kind,(a,b,c,d) in GLYPHS.items():
        im=panel(kind)
        for n,(part,ascent,char,rewind) in enumerate(((im.crop((0,0,224,SPLIT)),53,a,b),(im.crop((0,SPLIT,224,280)),-3,c,d))):
            resource=f'font/aventuras/{kind}_{n}.png'
            files[f'assets/astral/textures/{resource}']=png(part)
            providers.append({'type':'bitmap','file':'astral:'+resource,'height':part.height,'ascent':ascent,'chars':[char]})
            advances[rewind]=-(part.getbbox()[2]+1)
        for key,_ in regions(kind):
            for locked in ((False,True) if kind=='mazmorras' else (False,)):
                image=card(kind,key,locked)
                for row in range(image.height//18):
                    for col in range(image.width//18):
                        index=row*(image.width//18)+col
                        name=f'{kind}_{key}'+('_locked' if locked else '')+f'_{index}'
                        tile=image.crop((col*18,row*18,col*18+18,row*18+18))
                        files[f'assets/astral/textures/item/aventuras/{name}.png']=png(tile)
                        files[f'assets/astral/models/aventuras/{name}.json']=json.dumps({'parent':'minecraft:item/generated','gui_light':'front','textures':{'layer0':f'astral:item/aventuras/{name}'},'display':{'gui':{'scale':[1.125,1.125,1]}}}).encode()
                        files[f'assets/astral/items/aventuras/{name}.json']=json.dumps({'oversized_in_gui':True,'model':{'type':'minecraft:model','model':f'astral:aventuras/{name}'}}).encode()
    providers.append({'type':'space','advances':advances})
    return files,providers


def previews(folder):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    sheet=Image.new('RGBA',(224*3,280),'#171920')
    for i,kind in enumerate(THEMES):
        im=Image.new('RGBA',SIZE,'#22242a');im.alpha_composite(panel(kind))
        for j,(key,slots) in enumerate(regions(kind)):
            slot=slots[0]
            im.alpha_composite(card(kind,key,kind=='mazmorras' and j>1),(31+slot%9*18,57+slot//9*18))
        for slot,label in ((4,'i'),(8,'$'),(45,'<'),(49,'O'),(51,'?'),(53,'X')):
            text(im,label,(39+slot%9*18,62+slot//9*18),color='#fff0d5')
        text(im,'Inventario',(86,169),color='#383c40')
        sheet.alpha_composite(im,(i*224,0))
        (folder/f'{kind}.png').write_bytes(png(im.resize((672,840),Image.Resampling.NEAREST)))
    (folder/'atlas-expediciones-mazmorras.png').write_bytes(png(sheet.resize((1344,560),Image.Resampling.NEAREST)))


if __name__=='__main__':previews(Path(__file__).resolve().parent.parent/'build/Servicios-preview')
