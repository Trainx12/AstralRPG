"""Atlas, cartografia y portales: interfaces propias sobre la grilla vanilla.

Comparte medidas y tecnica de glifos con los servicios. Los descubrimientos
siguen siendo personales; el arte nunca concede permisos ni ejecuta viajes.
"""
import json
from pathlib import Path
from PIL import Image, ImageDraw
from escape_menu import text
from services_ui import png, SIZE, SPLIT, outlined, illustration, header, tall, glyph_parts
from market_ui import band_color

THEMES = {
    'principal': ('ATLAS ASTRAL', '#151f35', '#c5aa65', '#7ecfdd'),
    'expediciones': ('EXPEDICIONES ASTRALES', '#162930', '#c5ad77', '#90c8a0'),
    'mazmorras': ('MAZMORRAS', '#1f1329', '#b28fd0', '#c88bdb'),
}
# Marcos de Gemini (noviembre 2026) e interior medido sobre cada original.
FRAMES = {'expediciones': ('expediciones2', (290, 753, 1566, 2102)),
          'mazmorras': ('mazmorras2', (278, 888, 1502, 2026))}
START, END = '\ue600', '\ue601'
GLYPHS = {k: tuple(chr(0xe610+i*4+j) for j in range(4)) for i,k in enumerate(THEMES)}
DESTINATIONS = ('bosque', 'mina', 'tumba', 'cumbre', 'forja', 'santuario')
LABELS = ('BOSQUE', 'MINAS', 'TUMBA', 'CUMBRE', 'FORJA', 'SANTUARIO')
COLORS = ('#85b777', '#8eb6c5', '#dcb779', '#adddec', '#ea9862', '#ceb0ed')
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


def label(image, caption, center, max_width, color):
    """Texto centrado; si no entra en el boton, junta las letras en vez de pisar el borde."""
    from escape_menu import ROOT
    font = Image.open(ROOT / 'vanilla-base/font/ascii.png').convert('RGBA')
    chars = json.loads((ROOT / 'vanilla-base/font/ascii.json').read_text(encoding='utf-8'))['chars']
    glyphs = {}
    for row, line in enumerate(chars):
        for col, char in enumerate(line):
            glyph = font.crop((col * 8, row * 8, col * 8 + 8, row * 8 + 8))
            box = glyph.getbbox()
            glyphs[char] = (glyph, box[2] if box else 3)
    def width(gap):
        return sum(glyphs.get(c, glyphs['?'])[1] + gap for c in caption) - gap
    gap = 1 if width(1) <= max_width else 0
    x, y = round(center[0] - width(gap) / 2), center[1]
    for char in caption:
        glyph, advance = glyphs.get(char, glyphs['?'])
        alpha = glyph.getchannel('A')
        for offset, tint in (((1, 1), '#51331d'), ((0, 0), color)):
            layer = Image.new('RGBA', (8, 8), tint)
            layer.putalpha(alpha)
            image.alpha_composite(layer, (x + offset[0], y + offset[1]))
        x += advance + gap


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
    d.line((3,1,width-4,1),fill='#d6be85' if kind!='mazmorras' else '#bcb1cd')
    d.line((3,height-2,width-4,height-2),fill='#0b101c')
    for x in (1,width-2):
        for y in (1,height-2):d.point((x,y),fill='#f3dcab')
    if main:
        star(d,7,8,color,2)
        label(im,MAIN_LABELS[MAIN.index(key)],(41,5),55,'#f4e4be')
    else:
        # Ilustracion de Gemini de fondo y el nombre abajo, con contorno.
        art=illustration(f'{kind}_{key}')
        ch=round(art.width*height/width);top=max(0,(art.height-ch)//2)
        pic=art.crop((0,top,art.width,top+ch)).resize((width,height),Image.Resampling.LANCZOS)
        if locked:
            from PIL import ImageOps
            alpha=pic.getchannel('A');pic=ImageOps.grayscale(pic).convert('RGBA');pic.putalpha(alpha)
            pic=Image.blend(pic,Image.new('RGBA',pic.size,'#1b1820'),.45)
        im.alpha_composite(pic);d=ImageDraw.Draw(im)
        shade=Image.new('RGBA',(width,11),(8,6,12,170));im.alpha_composite(shade,(0,height-11))
        d.rectangle((0,0,width-1,height-1),outline='#d8b25a' if not locked else '#7f7a84')
        d.rectangle((1,1,width-2,height-2),outline='#2a2030')
        label(im,LABELS[DESTINATIONS.index(key)],(27,height-10),50,'#fff0d5' if not locked else '#b9b3bf')
        if locked:
            d.rectangle((42,5,49,11),fill='#342f3c',outline='#d4c9a8')
            d.arc((43,1,48,8),180,360,fill='#d4c9a8')
        return im
    if False:
        # Nichos de piedra, cartelas y pequenos brillos del bioma.
        d.line((7,21,width-8,21),fill='#47534d' if kind=='expediciones' else '#494054')
        d.line((5,23,width-6,23),fill='#101923')
        for x in (6,width-7):star(d,x,12,color,1)
        emblem(d,key,27,12,color)
        label(im,LABELS[DESTINATIONS.index(key)],(27,25),48,color)
        if locked:
            d.rectangle((42,10,48,16),fill='#342f3c',outline='#b4a7b9')
            d.arc((43,6,47,13),180,360,fill='#b4a7b9')
    return im


def panel(kind):
    caption,fill,edge,accent=THEMES[kind]
    if kind in FRAMES:
        art,(l,t,r,b)=FRAMES[kind]
        source=Image.open(Path(__file__).resolve().parent/f'pack-source/ref/{art}-frame.png').convert('RGBA')
        sx,sy=[0,l,r,source.width],[0,t,b,source.height]
    else:
        source=Image.open(Path(__file__).resolve().parent/f'pack-source/ref/{kind}-illustrated-frame.png').convert('RGBA')
        sx=[0,round(source.width*.13),round(source.width*.87),source.width]
        sy=[0,320,round(source.height*.92),source.height]
    dx,dy=[0,24,200,224],[0,56,258,280]
    im=Image.new('RGBA',SIZE)
    for row in range(3):
        for col in range(3):
            piece=source.crop((sx[col],sy[row],sx[col+1],sy[row+1]))
            im.alpha_composite(piece.resize((dx[col+1]-dx[col],dy[row+1]-dy[row]),Image.Resampling.NEAREST),(dx[col],dy[row]))
    # El titulo queda dentro del cartel ilustrado.
    ty={'principal':39,'expediciones':42,'mazmorras':39}[kind]
    outlined(im,caption,(112,ty))
    d=ImageDraw.Draw(im)
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
    # Placa de Inventario con bordes y remates del tema (el juego escribe la palabra encima).
    d.rectangle((31,168,192,177),fill=band_color(edge))
    d.line((31,167,192,167),fill=edge)
    d.line((31,178,192,178),fill=edge)
    d.line((33,169,190,169),fill='#ffffff60')
    for x in (31,192):
        d.polygon([(x,172),(x+(3 if x<100 else -3),169),(x+(6 if x<100 else -6),172),(x+(3 if x<100 else -3),175)],fill=edge)
    if kind=='principal':
        # Columna del medio: separador con estrellas en vez de un hueco vacio.
        x0=31+4*18
        d.rectangle((x0+2,75,x0+15,146),fill=fill)
        d.line((x0+8,77,x0+8,144),fill=edge)
        d.line((x0+9,77,x0+9,144),fill='#0b101c')
        for y in (84,102,120,138):
            d.polygon([(x0+8,y-4),(x0+12,y),(x0+8,y+4),(x0+4,y)],fill=edge)
            d.point((x0+8,y),fill=accent)
    for row in (*range(3),4):
        for col in range(9):
            x,y=31+col*18,179+row*18 if row<3 else 237
            d.rectangle((x,y,x+17,y+17),outline=edge)
            d.rectangle((x+1,y+1,x+16,y+16),fill=(0,0,0,0))
    return im


# Marcos con encabezado alto: se dibujan a su proporcion real en vez de aplastarlos a 56 px.
TALL = ('expediciones',)


def full_panel(kind, image=None):
    image = panel(kind) if image is None else image
    if kind not in TALL:
        return image, SPLIT
    caption, fill = THEMES[kind][:2]
    head = header(FRAMES[kind][0], FRAMES[kind][1], caption, {'expediciones': 42, 'mazmorras': 39}[kind], fill)
    return tall(image, head), head.height


def assets():
    files,providers={},[];advances={START:-32,END:32}
    for kind,(a,b,c,d) in GLYPHS.items():
        im,head_height=full_panel(kind)
        for n,((part,ascent),char,rewind) in enumerate(zip(glyph_parts(im,head_height),(a,c),(b,d))):
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
        im,_=full_panel(kind,im);out=Image.new('RGBA',im.size,'#22242a');out.alpha_composite(im)
        sheet.alpha_composite(out.crop((0,out.height-280,224,out.height)),(i*224,0))
        (folder/f'{kind}.png').write_bytes(png(out.resize((out.width*3,out.height*3),Image.Resampling.NEAREST)))
    (folder/'atlas-expediciones-mazmorras.png').write_bytes(png(sheet.resize((1344,560),Image.Resampling.NEAREST)))


if __name__=='__main__':previews(Path(__file__).resolve().parent.parent/'build/Servicios-preview')
