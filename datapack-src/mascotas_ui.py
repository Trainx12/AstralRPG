"""Santuario de las seis mascotas, con retratos de sus modelos reales."""
import json
from functools import lru_cache
from pathlib import Path
from PIL import Image,ImageDraw,ImageOps
from escape_menu import text
from services_ui import png,SPLIT
from market_ui import band_color
from mobs.mascotas import MASCOTAS

ROOT=Path(__file__).resolve().parent
SIZE=(224,300)
FILL,EDGE='#142c2b','#a8894d'
START,END='\ue800','\ue801'
GLYPHS=tuple(chr(0xe810+i) for i in range(4))
LABELS={'lobo':'LOBO','cuervo':'CUERVO','golem':'GOLEM','zorro':'ZORRO','dragon':'DRAGON','fenix':'FENIX'}
BONUS={'lobo':'FUERZA I','cuervo':'VISION','golem':'DEFENSA','zorro':'RAPIDEZ','dragon':'ANTI FUEGO','fenix':'RESCATE'}
REST_SLOTS=tuple(range(47,52))


def title():
    return '&f'+START+''.join(GLYPHS)+END


def regions():
    return [(pid,[row*9+col for row in range(r,r+2) for col in range(c,c+3)])
            for pid,(r,c) in zip(MASCOTAS,((1,0),(1,3),(1,6),(3,0),(3,3),(3,6)))]


@lru_cache(maxsize=6)
def portrait(pid):
    from mobs import build_models
    model=getattr(build_models.creatures,'mascota_'+pid)()
    texture=model.export()[1]
    image=build_models.preview3d(model,texture,yaw=30,pitch=18,scale=3,background=(0,0,0,0))
    image=image.crop(image.getbbox())
    image.thumbnail((42,14),Image.Resampling.NEAREST)
    return image


def card(pid,locked=False):
    color=MASCOTAS[pid]['color']
    im=Image.new('RGBA',(54,36),FILL);d=ImageDraw.Draw(im)
    d.rectangle((0,0,53,35),outline=EDGE)
    d.rectangle((2,2,51,33),outline='#3e5550')
    # Nicho y pedestal arriba; nombre, filete dorado y bonus abajo, sin pisarse.
    d.rectangle((4,3,49,17),fill='#0d2025')
    d.ellipse((13,13,40,18),fill='#28443e',outline='#496052')
    image=portrait(pid)
    im.alpha_composite(image,((54-image.width)//2,3+(14-image.height)//2))
    text(im,LABELS[pid],(27,18),color=color)
    d.line((8,26,45,26),fill=EDGE)
    d.point((7,26),fill='#ddc98c');d.point((46,26),fill='#ddc98c')
    # Fuente de 3x5 dibujada a su resolucion nativa para el beneficio compacto.
    tiny_text(im,BONUS[pid],28,'#f3e4b8')
    for x in (1,52):
        for y in (1,34):d.point((x,y),fill='#ddc98c')
    if locked:
        im=Image.blend(ImageOps.grayscale(im).convert('RGBA'),Image.new('RGBA',im.size,'#22322f'),.45)
        d=ImageDraw.Draw(im)
        d.rectangle((42,7,49,13),fill='#172623',outline='#b1b9aa')
        d.arc((43,3,48,10),180,360,fill='#d7d5c0')
        d.point((45,10),fill='#d7d5c0')
    return im


def tiny_text(im,caption,y,color):
    alphabet={
        'A':('010','101','111','101','101'),'C':('011','100','100','100','011'),
        'D':('110','101','101','101','110'),'E':('111','100','110','100','111'),
        'F':('111','100','110','100','100'),'G':('011','100','101','101','011'),
        'I':('111','010','010','010','111'),'L':('100','100','100','100','111'),
        'N':('101','111','111','111','101'),'O':('010','101','101','101','010'),
        'P':('110','101','110','100','100'),'R':('110','101','110','101','101'),
        'S':('011','100','010','001','110'),'T':('111','010','010','010','010'),
        'U':('101','101','101','101','111'),'V':('101','101','101','101','010'),
        'Z':('111','001','010','100','111'),' ':('000',)*5}
    d=ImageDraw.Draw(im);x=(im.width-(len(caption)*4-1))//2
    for letter in caption:
        for row,line in enumerate(alphabet[letter]):
            for col,pixel in enumerate(line):
                if pixel=='1':d.point((x+col,y+row),fill=color)
        x+=4


def nav_icon(kind):
    """Botones del marco en madera, musgo y oro del santuario."""
    im=Image.new('RGBA',(18,18),FILL);d=ImageDraw.Draw(im)
    d.rectangle((0,0,17,17),outline=EDGE);d.rectangle((1,1,16,16),fill='#1d3a33',outline='#3e5550')
    d.line((2,1,15,1),fill='#e4d2a5')
    gold,ivory,teal='#d9b766','#eee3be','#7fe0c8'
    if kind=='info':      # huella
        d.ellipse((6,8,11,13),fill=gold)
        for x,y in ((4,6),(7,4),(10,4),(13,6)):d.ellipse((x-1,y-1,x+1,y+1),fill=ivory)
    elif kind=='gacha':   # montura con gema
        d.polygon(((3,9),(6,6),(11,6),(14,9),(12,12),(5,12)),fill='#8a5a32',outline=gold)
        d.line((6,12,6,15),fill=gold);d.line((11,12,11,15),fill=gold)
        d.rectangle((8,7,9,8),fill=teal);d.point((14,3),fill=teal);d.point((15,5),fill=gold)
    elif kind=='back':    # flecha dorada
        d.polygon(((3,9),(8,4),(8,7),(14,7),(14,11),(8,11),(8,14)),fill=gold)
        d.line((9,8,13,8),fill=ivory)
    else:                 # cerrar
        d.line((5,5,12,12),fill=ivory,width=2);d.line((12,5,5,12),fill=ivory,width=2)
        d.point((8,8),fill='#e07a5f')
    return im


def rest_button():
    im=Image.new('RGBA',(90,18),'#294438');d=ImageDraw.Draw(im)
    d.rectangle((0,0,89,17),outline=EDGE);d.rectangle((2,2,87,15),outline='#57705a')
    d.line((3,1,86,1),fill='#e4d2a5')
    text(im,'DESCANSAR',(45,5),color='#eee3be')
    return im


def panel():
    source=Image.open(ROOT/'pack-source/ref/mascotas-illustrated-frame.png').convert('RGBA')
    sx=[0,round(source.width*.15),round(source.width*.85),source.width]
    # El pie mas alto conserva al golem y al zorro debajo del inventario real.
    sy=[0,round(source.height*.25),round(source.height*.68),source.height]
    dx,dy=[0,24,200,224],[0,56,258,300]
    im=Image.new('RGBA',SIZE)
    for row in range(3):
        for col in range(3):
            piece=source.crop((sx[col],sy[row],sx[col+1],sy[row+1]))
            im.alpha_composite(piece.resize((dx[col+1]-dx[col],dy[row+1]-dy[row]),Image.Resampling.NEAREST),(dx[col],dy[row]))
    text(im,'MASCOTAS',(112,38),color='#f3e4b8')
    d=ImageDraw.Draw(im);d.rectangle((24,56,199,258),fill=FILL)
    for _,slots in regions():
        slot=slots[0];x,y=31+slot%9*18,57+slot//9*18
        d.rectangle((x,y,x+53,y+35),fill=(0,0,0,0))
    for slot in (4,8,45,53):
        x,y=31+slot%9*18,57+slot//9*18
        d.rectangle((x,y,x+17,y+17),outline=EDGE)
        d.rectangle((x+1,y+1,x+16,y+16),fill=(0,0,0,0))
    d.rectangle((67,147,156,164),fill=(0,0,0,0))
    d.rectangle((31,168,192,177),fill=band_color(EDGE))
    d.line((31,167,192,167),fill=EDGE);d.line((31,178,192,178),fill=EDGE)
    d.line((33,169,190,169),fill='#ffffff60')
    for x,s in ((31,1),(192,-1)):
        d.polygon(((x,172),(x+3*s,169),(x+6*s,172),(x+3*s,175)),fill=EDGE)
    for row in (*range(3),4):
        for col in range(9):
            x,y=31+col*18,179+row*18 if row<3 else 237
            d.rectangle((x,y,x+17,y+17),outline='#546a57')
            d.rectangle((x+1,y+1,x+16,y+16),fill=(0,0,0,0))
    return im


def assets():
    files,providers={},[];advances={START:-32,END:32}
    a,b,c,d=GLYPHS;im=panel()
    for n,(part,ascent,char,rewind) in enumerate(((im.crop((0,0,224,SPLIT)),53,a,b),(im.crop((0,SPLIT,224,300)),-3,c,d))):
        path=f'font/mascotas/santuario_{n}.png'
        files['assets/astral/textures/'+path]=png(part)
        providers.append({'type':'bitmap','file':'astral:'+path,'height':part.height,'ascent':ascent,'chars':[char]})
        advances[rewind]=-(part.getbbox()[2]+1)
    providers.append({'type':'space','advances':advances})
    def model(name,image):
        files[f'assets/astral/textures/item/mascotas/{name}.png']=png(image)
        files[f'assets/astral/models/mascotas/{name}.json']=json.dumps({'parent':'minecraft:item/generated','gui_light':'front',
            'textures':{'layer0':f'astral:item/mascotas/{name}'},'display':{'gui':{'scale':[1.125,1.125,1]}}}).encode()
        files[f'assets/astral/items/mascotas/{name}.json']=json.dumps({'oversized_in_gui':True,
            'model':{'type':'minecraft:model','model':f'astral:mascotas/{name}'}}).encode()
    for pid,_ in regions():
        for locked in (False,True):
            image=card(pid,locked)
            for row in range(2):
                for col in range(3):
                    index=row*3+col
                    model(pid+('_locked' if locked else '')+f'_{index}',image.crop((col*18,row*18,col*18+18,row*18+18)))
    for kind in ('info','gacha','back','close'):model('nav_'+kind,nav_icon(kind))
    image=rest_button()
    for i in range(5):model(f'rest_{i}',image.crop((i*18,0,i*18+18,18)))
    return files,providers


def previews(folder):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    for sample in ('mixta','completa'):
        im=Image.new('RGBA',SIZE,'#202c29');im.alpha_composite(panel())
        for i,(pid,slots) in enumerate(regions()):
            slot=slots[0]
            im.alpha_composite(card(pid,sample=='mixta' and i in (2,4,5)),(31+slot%9*18,57+slot//9*18))
        im.alpha_composite(rest_button(),(67,147))
        for slot,kind in ((4,'info'),(8,'gacha'),(45,'back'),(53,'close')):
            im.alpha_composite(nav_icon(kind),(31+slot%9*18,57+slot//9*18))
        text(im,'Inventario',(86,169),color='#383c40')
        (folder/f'mascotas-{sample}.png').write_bytes(png(im.resize((672,900),Image.Resampling.NEAREST)))


if __name__=='__main__':previews(ROOT.parent/'build/Servicios-preview')
