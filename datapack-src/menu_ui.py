"""Menu Astral (Estrella del slot 9): marco de Gemini e iconos pintados, sobre la grilla vanilla."""
import json
from pathlib import Path
from PIL import Image, ImageDraw
from escape_menu import text
from services_ui import png, SIZE, SPLIT, outlined, illustration
from market_ui import band_color

ROOT = Path(__file__).resolve().parent
FRAME = ('menu2', (214, 640, 1582, 2147))
FILL, EDGE, ACCENT = '#1c1526', '#c9a14f', '#b48cf0'
TITLE_Y = 35
START, END = '', ''
GLYPHS = tuple(chr(0xea10 + i) for i in range(4))
# Mismo orden que menus.principal_menu: casillas 10-16 y 19-25.
KEYS = ('bazar', 'minas', 'mazmorras', 'expediciones', 'portales', 'parkour', 'arenas',
        'misiones', 'mascotas', 'cosmeticos', 'skills', 'guia', 'comandos', 'spawn',
        'fragmentos', 'duelos')
SLOTS = tuple(range(10, 17)) + tuple(range(19, 26)) + (30, 32)
ICON_ART = dict(bosque='expediciones', fragmentos='skills', tienda='bazar', peluches='mascotas',
                subastas='bazar', vender='bazar', intercambio='bazar', gacha_rpg='skills',
                gacha_monturas='mascotas', gacha_cosmeticos='cosmeticos', duelos='arenas')
EXTRA_KEYS = ('mochilas','proteccion','recetas','tren','santuario','titulos',
              'subastas','vender','intercambio','tienda','peluches','bosque',
              'gacha_rpg','gacha_monturas','gacha_cosmeticos',
              'back','next','close','clear','lock','saldo','ranking','pagar','valor',
              'login','password','premium','panel','atlas','spiral','spiral2','paradise3',
              'colorescape','magmarun','batallanaval','dropper_facil','dropper_h4rs')
EXTRA_KEYS += tuple(f'dropper_{kind}_{n}' for kind,count in (('facil',6),('h4rs',10)) for n in range(1,count+1))
NEW_KEYS = ('fragmentos','duelos','cosmeticos',*EXTRA_KEYS)


def title():
    return '&f' + START + ''.join(GLYPHS) + END


# Iconos pintados por Gemini (hojas 12 y 28): ganan sobre el pixel art de reserva.
GEMINI_ICONS = ('fragmentos', 'duelos', 'cosmeticos', 'mochilas', 'proteccion', 'recetas', 'tren', 'santuario')


def icon(key):
    """Icono de Gemini en 18x18 (el modelo lo dibuja a escala 1.125 sobre la casilla)."""
    if key in NEW_KEYS and key not in GEMINI_ICONS:
        return painted_icon(key)
    art = illustration('menu_' + (key if key in GEMINI_ICONS else ICON_ART.get(key, key)))
    im = art.resize((72, 72), Image.Resampling.BOX).resize((18, 18), Image.Resampling.LANCZOS)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 17, 17), outline=EDGE)
    return im


def painted_icon(key):
    """Pixel art propio: siluetas legibles a 18 px, piedra oscura y oro."""
    im=Image.new('RGBA',(18,18),'#18202b');d=ImageDraw.Draw(im)
    g,c,w='#d6b264','#75dce0','#f6e6bd'
    d.rectangle((0,0,17,17),outline=g);d.line((2,1,15,1),fill=w)
    if key=='fragmentos':
        for x,y in ((5,8),(11,5),(12,12)):
            d.polygon(((x,y-3),(x+2,y),(x,y+3),(x-2,y)),fill=c,outline=g)
    elif key=='duelos':
        d.line((4,4,13,13),fill=w,width=2);d.line((13,4,4,13),fill=c,width=2)
        d.line((3,10,7,14),fill=g,width=2);d.line((10,14,14,10),fill=g,width=2)
    elif key=='cosmeticos':
        d.polygon(((4,11),(7,4),(11,5),(13,11)),fill='#9561b4',outline=g)
        d.ellipse((2,10,15,13),fill=g);d.rectangle((6,9,12,10),fill=c)
    elif key=='mochilas':
        d.arc((6,2,11,8),180,360,fill=g);d.rounded_rectangle((4,5,13,15),2,fill='#885738',outline=g)
        d.rectangle((6,10,11,13),outline=w);d.point((9,8),fill=c)
    elif key=='proteccion':
        d.polygon(((4,3),(13,3),(13,10),(9,15),(4,10)),fill='#3a716d',outline=g)
        d.line((6,8,11,8),fill=w);d.line((9,5,9,11),fill=w)
    elif key=='recetas':
        d.polygon(((3,4),(8,3),(9,5),(10,3),(15,4),(15,14),(10,13),(9,15),(8,13),(3,14)),fill='#597d50',outline=g)
        d.line((9,5,9,13),fill=w);d.line((4,7,7,7),fill=w);d.line((11,9,14,9),fill=c)
    elif key=='tren':
        d.rectangle((3,7,13,12),fill='#985a3c',outline=g);d.rectangle((10,3,14,9),fill=g)
        d.rectangle((4,3,6,7),fill=w);d.rectangle((11,4,13,6),fill=c)
        for x in (5,11):d.ellipse((x-1,12,x+2,15),fill='#101720',outline=g)
    elif key=='santuario':
        d.arc((3,2,14,17),180,360,fill=g,width=2);d.rectangle((3,8,5,14),fill=g);d.rectangle((12,8,14,14),fill=g)
        d.polygon(((9,4),(11,8),(9,12),(7,8)),fill=c)
    elif key=='titulos':
        d.polygon(((5,9),(6,16),(9,13),(12,16),(13,9)),fill='#8264ae')
        d.ellipse((4,2,13,11),fill=g);d.polygon(((9,3),(10,6),(12,7),(10,8),(9,10),(8,8),(6,7),(8,6)),fill=c)
    elif key=='subastas':
        d.line((5,13,11,5),fill=g,width=2);d.line((7,4,13,8),fill=w,width=3);d.rectangle((3,14,14,15),fill=g)
    elif key=='vender':
        d.ellipse((3,4,10,11),fill=g);d.line((8,13,14,13),fill=c,width=2);d.polygon(((14,13),(11,10),(11,16)),fill=c)
    elif key=='intercambio':
        d.line((3,6,14,6),fill=g,width=2);d.polygon(((14,6),(11,3),(11,9)),fill=g)
        d.line((3,12,14,12),fill=c,width=2);d.polygon(((3,12),(6,9),(6,15)),fill=c)
    elif key=='bosque':
        d.rectangle((8,11,10,15),fill=g);d.polygon(((9,2),(3,12),(15,12)),fill='#77ae65',outline=g)
    elif key=='tienda':
        d.rectangle((3,7,14,14),outline=g);d.rectangle((2,4,15,7),fill='#a05454',outline=g)
        d.rectangle((8,9,11,14),fill=c)
    elif key=='peluches':
        for x in (5,12):d.ellipse((x-2,3,x+1,6),fill=g)
        d.ellipse((4,5,13,13),fill='#b98a61',outline=g);d.point((7,8),fill=w);d.point((11,8),fill=w);d.point((9,11),fill='#18202b')
    elif key in ('back','next'):
        points=((3,9),(9,4),(9,7),(14,7),(14,11),(9,11),(9,14))
        d.polygon(points,fill=g)
        if key=='next':im=im.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    elif key in ('close','clear'):
        if key=='clear':d.ellipse((3,3,14,14),outline=g)
        d.line((5,5,12,12),fill='#df997d',width=2);d.line((12,5,5,12),fill=w,width=2)
    elif key in ('login','password','lock'):
        if key=='login':
            d.ellipse((3,3,8,8),outline=g,width=2);d.line((7,7,14,14),fill=g,width=2);d.line((11,12,13,10),fill=c)
        else:
            d.arc((5,2,12,10),180,360,fill=g,width=2);d.rectangle((4,8,13,14),fill='#4f7490' if key=='password' else '#6d6d79',outline=g);d.point((9,11),fill=w)
    elif key in ('saldo','ranking','pagar','valor'):
        if key=='ranking':
            for x,y in ((3,10),(7,5),(11,8)):d.rectangle((x,y,x+3,14),fill=g,outline=w)
        else:
            d.ellipse((4,3,13,12),fill=g,outline=w);d.line((8,5,8,10),fill='#735139')
            if key=='pagar':d.line((3,15,14,15),fill=c,width=2);d.polygon(((14,15),(11,12),(11,16)),fill=c)
            if key=='valor':d.line((12,10,15,14),fill=c,width=2)
    elif key=='premium':
        d.polygon(((3,5),(6,8),(9,3),(12,8),(15,5),(13,14),(5,14)),fill=g);d.rectangle((8,9,10,11),fill=c)
    elif key=='panel':
        d.rectangle((3,3,14,14),fill='#36435e',outline=g)
        for y in (6,9,12):d.line((6,y,12,y),fill=c if y==6 else w)
    elif key=='atlas':
        d.polygon(((9,2),(11,6),(15,8),(11,10),(9,15),(7,10),(3,8),(7,6)),fill=g)
        d.ellipse((7,6,10,9),fill=c)
    elif key.startswith(('dropper_facil_','dropper_h4rs_')):
        number=key.rsplit('_',1)[1]
        d.line((4,3,4,13),fill=g);d.line((14,3,14,13),fill=g)
        d.polygon(((9,8),(6,4),(12,4)),fill=c if '_facil_' in key else '#df997d')
        text(im,number,(9,9),color=w)
    elif key in ('spiral','spiral2','paradise3','colorescape','magmarun','batallanaval','dropper_facil','dropper_h4rs'):
        if key=='batallanaval':
            d.polygon(((3,10),(15,10),(12,14),(6,14)),fill=g);d.line((9,3,9,10),fill=w);d.polygon(((10,3),(14,8),(10,8)),fill=c)
        elif key=='colorescape':
            for x,y,col in ((4,4,'#e88d7c'),(10,4,'#84d3ba'),(4,10,'#b39bdc'),(10,10,'#e1d17c')):d.rectangle((x,y,x+4,y+4),fill=col)
        elif key.startswith('dropper'):
            d.line((4,3,4,14),fill=g);d.line((14,3,14,14),fill=g);d.line((9,3,9,12),fill=c if key.endswith('facil') else '#df997d',width=2);d.polygon(((9,14),(6,10),(12,10)),fill=w)
        else:
            color={'spiral':c,'spiral2':'#ae94da','paradise3':'#8bc97b','magmarun':'#df997d'}[key]
            for x,y in ((3,12),(6,9),(9,6),(12,3)):d.rectangle((x,y,x+3,y+2),fill=color,outline=g)
    else:  # Cada caja tiene su propio sello y color.
        color={'gacha_rpg':'#75dce0','gacha_monturas':'#9bd882','gacha_cosmeticos':'#cf8cdb'}[key]
        d.rectangle((3,5,14,14),fill='#735139',outline=g);d.line((3,9,14,9),fill=g)
        if key=='gacha_rpg':d.polygon(((9,6),(11,9),(9,12),(7,9)),fill=color)
        elif key=='gacha_monturas':d.arc((5,6,12,12),0,180,fill=color,width=2)
        else:d.ellipse((7,7,11,11),fill=color)
    return im


def button_model(key):
    key=key.removeprefix('cmd_')
    if key.startswith('facil') and key[5:].isdigit():key='dropper_facil_'+key[5:]
    elif key.startswith('h4rs') and key[4:].isdigit():key='dropper_h4rs_'+key[4:]
    aliases={'menu':'atlas','titulo':'titulos','sb':'panel','balance':'saldo','baltop':'ranking',
             'pay':'pagar','shop':'tienda','sellgui':'vender','worth':'valor','ah':'subastas',
             'trade':'intercambio','changepassword':'password','volver':'back','anterior':'back',
             'siguiente':'next','cerrar':'close','lobby':'spawn','mas_companeros':'next',
             'descubiertas':'expediciones','explorar':'expediciones','premios':'gacha_rpg'}
    key=aliases.get(key,key)
    return 'astral:menu/icon_'+key if key in (*KEYS,*EXTRA_KEYS) else None


def decorate(data):
    for key,item in data['items'].items():
        if 'item_model' not in item and any(k.endswith('commands') for k in item):
            model=button_model(key)
            if model:item['item_model']=model
    return data


def panel():
    art, (l, t, r, b) = FRAME
    source = Image.open(ROOT / f'pack-source/ref/{art}-frame.png').convert('RGBA')
    sx, sy = [0, l, r, source.width], [0, t, b, source.height]
    dx, dy = [0, 24, 200, 224], [0, 56, 258, 280]
    im = Image.new('RGBA', SIZE)
    for row in range(3):
        for col in range(3):
            piece = source.crop((sx[col], sy[row], sx[col + 1], sy[row + 1]))
            im.alpha_composite(piece.resize((dx[col + 1] - dx[col], dy[row + 1] - dy[row]), Image.Resampling.NEAREST), (dx[col], dy[row]))
    outlined(im, 'MENU ASTRAL', (112, TITLE_Y))
    d = ImageDraw.Draw(im)
    d.rectangle((24, 56, 199, 258), fill=FILL)
    # Vitrina de dos filas de iconos, con un brillo de estrellas a los costados.
    d.rectangle((46, 73, 177, 148), fill='#140f1d', outline='#6c5a3a')
    for cx, cy in ((46, 73), (177, 73), (46, 148), (177, 148)):
        d.polygon(((cx, cy - 2), (cx + 2, cy), (cx, cy + 2), (cx - 2, cy)), fill=EDGE)
    for slot in (*SLOTS, 4, 49):
        x, y = 31 + slot % 9 * 18, 57 + slot // 9 * 18
        d.rectangle((x, y, x + 17, y + 17), outline=EDGE)
        d.rectangle((x + 1, y + 1, x + 16, y + 16), fill=(0, 0, 0, 0))
    d.rectangle((31, 168, 192, 177), fill=band_color(EDGE))
    d.line((31, 167, 192, 167), fill=EDGE); d.line((31, 178, 192, 178), fill=EDGE)
    for row in (*range(3), 4):
        for col in range(9):
            x, y = 31 + col * 18, 179 + row * 18 if row < 3 else 237
            d.rectangle((x, y, x + 17, y + 17), outline=EDGE)
            d.rectangle((x + 1, y + 1, x + 16, y + 16), fill=(0, 0, 0, 0))
    return im


def assets():
    files, providers = {}, []
    advances = {START: -32, END: 32}
    a, b, c, d = GLYPHS
    im = panel()
    for n, (part, ascent, char, rewind) in enumerate(((im.crop((0, 0, 224, SPLIT)), 53, a, b), (im.crop((0, SPLIT, 224, 280)), -3, c, d))):
        resource = f'font/menu/principal_{n}.png'
        files['assets/astral/textures/' + resource] = png(part)
        providers.append({'type': 'bitmap', 'file': 'astral:' + resource, 'height': part.height, 'ascent': ascent, 'chars': [char]})
        advances[rewind] = -(part.getbbox()[2] + 1)
    providers.append({'type': 'space', 'advances': advances})
    for key in (*KEYS,*EXTRA_KEYS):
        name = 'icon_' + key
        files[f'assets/astral/textures/item/menu/{name}.png'] = png(icon(key))
        files[f'assets/astral/models/menu/{name}.json'] = json.dumps({'parent': 'minecraft:item/generated', 'gui_light': 'front',
            'textures': {'layer0': f'astral:item/menu/{name}'}, 'display': {'gui': {'scale': [1.125, 1.125, 1]}}}).encode()
        files[f'assets/astral/items/menu/{name}.json'] = json.dumps({'oversized_in_gui': True,
            'model': {'type': 'minecraft:model', 'model': f'astral:menu/{name}'}}).encode()
    return files, providers


def preview(folder):
    folder = Path(folder); folder.mkdir(parents=True, exist_ok=True)
    im = Image.new('RGBA', SIZE, '#22242a'); im.alpha_composite(panel())
    for key, slot in zip(KEYS, SLOTS):
        im.alpha_composite(icon(key), (31 + slot % 9 * 18, 57 + slot // 9 * 18))
    text(im, 'Inventario', (86, 169), color='#383c40')
    (folder / 'menu-astral.png').write_bytes(png(im.resize((672, 840), Image.Resampling.NEAREST)))


if __name__ == '__main__':
    preview(ROOT.parent / 'build/Servicios-preview')
