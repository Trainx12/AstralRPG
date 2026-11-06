"""Arte y zonas de clic para subastas y las tres invocaciones del refugio."""
import json
from pathlib import Path
from PIL import Image, ImageDraw
from escape_menu import text
from services_ui import png, button, OFFSET, SIZE, SPLIT

ROOT = Path(__file__).resolve().parent
THEMES = {
    'subastas': ('CASA DE SUBASTAS', '#302019', '#c59b51'),
    'gacha_rpg': ('ARSENAL ARCANO', '#1e1226', '#ae83e3'),
    'gacha_monturas': ('SENDAS SALVAJES', '#23261c', '#c9a85a'),
    'gacha_cosmeticos': ('GALERIA CELESTE', '#16292f', '#7fd3d6'),
}
# Marcos de Gemini (noviembre 2026) e interior medido sobre cada original.
FRAMES = {'gacha_rpg': ('gacha_rpg2', (220, 773, 1582, 2068)),
          'gacha_monturas': ('gacha_monturas2', (254, 411, 1588, 2031)),
          'gacha_cosmeticos': ('gacha_cosmeticos2', (196, 587, 1516, 1943))}
# Gachas con iconos de tirada dibujados por Gemini.
TIER_ART = ('gacha_rpg', 'gacha_monturas')


def frame_source(kind):
    """Imagen del marco y cortes de nueve partes (x, y) en el original."""
    art, box = FRAMES.get(kind, (kind, None))
    source = Image.open(ROOT/f'pack-source/ref/{art}-frame.png').convert('RGBA')
    if box is None:
        box = (round(source.width*.13), round(source.height*.20), round(source.width*.87), round(source.height*.92))
    l, t, r, b = box
    return source, [0, l, r, source.width], [0, t, b, source.height]
# Titulo claro con contorno oscuro: se lee sobre carteles dorados, rosas o oscuros.
# Altura del titulo, centrada en el cartel de cada marco (Sendas Salvajes es la referencia).
TITLE_Y = {'subastas': 21, 'gacha_rpg': 41, 'gacha_monturas': 34, 'gacha_cosmeticos': 39}
TITLE_OUTLINE = {'subastas': '#3b2108', 'gacha_rpg': '#1c1030', 'gacha_monturas': '#0f2418', 'gacha_cosmeticos': '#0a1c22'}
# Casillas de la fila de abajo que usa cada menu: volver, cerrar y, en las
# gachas, garantia, premios y probabilidades.
NAV = {'subastas': [45, 53]}
NAV_GACHA = [45, 47, 49, 51, 53]


def band_color(edge):
    """Franja de Inventario: el color del tema, aclarado para que se lea el texto gris."""
    rgb = [int(edge[i:i+2], 16) for i in (1, 3, 5)]
    return '#' + ''.join(f'{round(c + (255 - c) * .62):02x}' for c in rgb)


# Bloque propio: no altera los glifos de los servicios anteriores.
START, END = '\ue500', '\ue501'
GLYPHS = {k: tuple(chr(0xe510 + i*4+j) for j in range(4)) for i,k in enumerate(THEMES)}
GLYPHS['subastas_catalogo']=tuple(chr(0xe530+j) for j in range(4))
# CrazyAuctions reconoce cada ventana buscando su titulo con "contains": las
# tres ventanas del catalogo llevan una marca invisible distinta (avance 0)
# para que el mismo marco no confunda el mercado con las otras dos.
CATALOG_TAGS = {'GUIName': '', 'Players-Current-Items': '', 'Cancelled/Expired-Items': ''}


def title(kind):
    a,b,c,d = GLYPHS[kind]
    return '&f'+START+a+b+c+d+END


def regions(kind):
    if kind == 'subastas':
        keys = ['mercado', 'publicaciones', 'retirar', 'publicar']
    else:
        keys = ['x1', 'x10', 'x25', 'x50']
    return [(key, [r*9+c for r in rows for c in cols]) for key,cols,rows in zip(
        keys, [range(0,4),range(5,9)]*2, [range(1,3)]*2+[range(3,5)]*2)]


def tile_card(kind, key):
    _,fill,edge = THEMES[kind]
    from lobby import GACHAS, money
    if kind == 'subastas':
        caption, sub = {'mercado':('EXPLORAR','MERCADO'), 'publicaciones':('MIS VENTAS','EN VENTA'),
                        'retirar':('RETIRAR','OBJETOS'), 'publicar':('PUBLICAR','COMO VENDER')}[key]
    else:
        caption,sub = 'TIRAR '+key.upper(),money(GACHAS[kind]['cost']*int(key[1:]))
    im=Image.new('RGBA',(72,36),fill); d=ImageDraw.Draw(im)
    d.rectangle((0,0,71,35),outline=edge);d.rectangle((2,2,69,33),outline='#100f19')
    if kind in TIER_ART:
        # Icono de Gemini a la izquierda; TIRAR / X10 / precio a la derecha.
        art=Image.open(ROOT/f'pack-source/ref/gemini/{kind}_{key}.png').convert('RGBA').resize((30,30),Image.Resampling.LANCZOS)
        im.alpha_composite(art,(3,3))
        text(im,'TIRAR',(53,3),color='#fff0d5');text(im,key.upper(),(53,13),color='#fff0d5')
        price=Image.new('RGBA',(80,10));text(price,sub,(40,0),color=edge);price=price.crop(price.getbbox())
        if price.width>36:price=price.resize((36,price.height),Image.Resampling.NEAREST)
        im.alpha_composite(price,(53-price.width//2,25))
        return im
    d.line((4,3,67,3),fill=edge)
    text(im,caption,(36,9),color='#fff0d5');text(im,sub,(36,23),color=edge)
    return im


def panel(kind, catalog=False):
    if kind=='subastas_catalogo':kind,catalog='subastas',True
    caption,fill,edge=THEMES[kind]
    # Nueve cortes: motivos en el borde, centro libre para las acciones reales.
    source,sx,sy=frame_source(kind)
    dx=[0,24,200,224];dy=[0,56,258,280]
    im=Image.new('RGBA',SIZE)
    # Fondo debajo del cartel: algunos marcos dejan ahi pixeles transparentes
    # y en el juego se veia el mundo a traves del menu.
    ImageDraw.Draw(im).rectangle((24,36,199,56),fill=fill)
    for r in range(3):
        for c in range(3):
            piece=source.crop((sx[c],sy[r],sx[c+1],sy[r+1]))
            im.alpha_composite(piece.resize((dx[c+1]-dx[c],dy[r+1]-dy[r]),Image.Resampling.NEAREST),(dx[c],dy[r]))
    d=ImageDraw.Draw(im);ox,oy=OFFSET
    d.rectangle((ox,oy+16,ox+175,oy+218),fill=fill)
    for dx_,dy_ in ((-1,0),(1,0),(0,-1),(0,1)):
        text(im,caption,(112+dx_,TITLE_Y[kind]+dy_),color=TITLE_OUTLINE[kind])
    text(im,caption,(112,TITLE_Y[kind]),color='#fff0d5')
    slots=list(range(54)) if catalog else [4,8,*NAV.get(kind,NAV_GACHA)]
    for slot in slots:
        x,y=ox+7+slot%9*18,oy+17+slot//9*18
        d.rectangle((x,y,x+17,y+17),outline=edge)
        d.rectangle((x+1,y+1,x+16,y+16),fill=(0,0,0,0))
    for row in [*range(3),4]:
        for col in range(9):
            x,y=ox+7+col*18,oy+(139+row*18 if row<3 else 197)
            d.rectangle((x,y,x+17,y+17),outline=edge)
            d.rectangle((x+1,y+1,x+16,y+16),fill=(0,0,0,0))
    d.rectangle((ox+7,oy+128,ox+168,oy+137),fill=band_color(edge))
    if not catalog:
        for key,slots in regions(kind):
            first=slots[0]
            d.rectangle((ox+7+first%9*18,oy+17+first//9*18,ox+78+first%9*18,oy+52+first//9*18),fill=(0,0,0,0))
    return im


def assets():
    files,providers={},[];advances={START:-32,END:32,**{tag:0 for tag in CATALOG_TAGS.values()}}
    def model(name,im):
        base='assets/astral/'
        files[base+f'textures/item/servicios/{name}.png']=png(im)
        files[base+f'models/servicios/{name}.json']=json.dumps({'parent':'minecraft:item/generated','gui_light':'front',
            'textures':{'layer0':f'astral:item/servicios/{name}'},
            'display':{'gui':{'scale':[im.width/16,im.height/16,1]}}}).encode()
        files[base+f'items/servicios/{name}.json']=json.dumps({'oversized_in_gui':True,
            'model':{'type':'minecraft:model','model':f'astral:servicios/{name}'}}).encode()
    for kind,(a,b,c,d) in GLYPHS.items():
        im=panel(kind)
        for n,(part,ascent,char,rewind) in enumerate([(im.crop((0,0,224,SPLIT)),53,a,b),(im.crop((0,SPLIT,224,280)),-3,c,d)]):
            resource=f'font/servicios/{kind}_{n}.png'
            files[f'assets/astral/textures/{resource}']=png(part)
            providers.append({'type':'bitmap','file':'astral:'+resource,'height':part.height,'ascent':ascent,'chars':[char]})
            advances[rewind]=-(part.getbbox()[2]+1)
        for key,_ in ([] if kind=='subastas_catalogo' else regions(kind)):
            card=tile_card(kind,key)
            for r in range(2):
                for col in range(4):model(f'{kind}_{key}_{r*4+col}',card.crop((col*18,r*18,col*18+18,r*18+18)))
    providers.append({'type':'space','advances':advances})
    return files,providers


def previews(folder):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    sheet=Image.new('RGBA',(224*4,280),'#171920')
    for i,kind in enumerate(THEMES):
        im=Image.new('RGBA',SIZE,'#25252d');im.alpha_composite(panel(kind))
        for key,slots in regions(kind):
            slot=slots[0];im.alpha_composite(tile_card(kind,key),(31+slot%9*18,57+slot//9*18))
        for slot,label in [(4,'$'),(8,'?'),(45,'<'),(53,'X')]+([] if kind=='subastas' else [(47,'G'),(49,'P'),(51,'%')]):
            text(im,label,(39+slot%9*18,62+slot//9*18),color='#fff0d5')
        text(im,'Inventario',(90,169),color='#383c40')
        sheet.alpha_composite(im,(i*224,0))
        (folder/f'{kind}.png').write_bytes(png(im.resize((672,840),Image.Resampling.NEAREST)))
    (folder/'subastas-y-gachas.png').write_bytes(png(sheet.resize((1792,560),Image.Resampling.NEAREST)))
    (folder/'subastas-catalogo.png').write_bytes(png(panel('subastas_catalogo').resize((672,840),Image.Resampling.NEAREST)))


if __name__=='__main__':previews(ROOT.parent/'build/Servicios-preview')
