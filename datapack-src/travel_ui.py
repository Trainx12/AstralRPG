"""Arte pixel original para Portales y Minas; casillas reales de 16 px."""
import io
import json
from pathlib import Path
from PIL import Image, ImageDraw
from escape_menu import text

KINDS = ('portales', 'minas', 'minas-venta')
ROWS = {'portales': 3, 'minas': 6, 'minas-venta': 3}
USED = {'portales': {10, 12, 14, 16, 22, 26},
        'minas': {4, 9, 18, 27, 45, 49, 53, *range(10, 16), *range(19, 26), *range(28, 35)},
        'minas-venta': {13, 22}}
CAPTIONS = {'portales': 'PORTALES ASTRALES', 'minas': 'MINAS ASTRALES', 'minas-venta': 'VENTA DE MINERALES'}


def title(kind):
    i = KINDS.index(kind)
    return '&f' + chr(0xe900+i*6) + chr(0xe901+i*6) + chr(0xe902+i*6) + chr(0xe903+i*6) + chr(0xe904+i*6) + chr(0xe905+i*6)


def panel(kind):
    rows = ROWS[kind]; h = 172 + rows*18
    im = Image.new('RGBA', (224, h)); d = ImageDraw.Draw(im)
    arcane = kind == 'portales'
    edge, bright, floor = ('#453459', '#b693e5', '#171321') if arcane else ('#694329', '#c99a50', '#242521')
    d.rectangle((16, 14, 207, h-3), fill='#111018', outline=bright, width=2)
    d.rectangle((20, 18, 203, h-7), fill=floor, outline=edge, width=3)
    # Pilares y juntas: piedra violeta o vigas de mina con remaches.
    for x in (17, 199):
        d.rectangle((x, 17, x+7, h-6), fill=edge, outline='#100e14')
        for y in range(22, h-8, 16):
            d.line((x+1, y, x+6, y), fill=bright)
            d.point((x+3, y+3), fill='#e4cfa0')
    d.rectangle((29, 19, 194, 48), fill=edge, outline=bright)
    d.line((31,21,192,21),fill='#d6ad76' if not arcane else '#807095')
    d.line((31,46,192,46),fill='#39281e' if not arcane else '#251b33')
    text(im, CAPTIONS[kind], (112, 28), color='#fff0cf')
    if arcane:
        for x,y in ((11,32),(212,32),(12,90),(211,115),(11,184),(212,185)):
            d.line((x-3,y,x+3,y),fill=bright); d.line((x,y-3,x,y+3),fill=bright)
        for x in range(35,190,17): d.point((x,51),fill='#b693e5')
        for label,center in (('NETHER',58),('END',94),('SALTOS',130),('PVP',166)):
            text(im,label,(center,63),color='#d2b8ec')
    else:
        for x in (9,207):
            d.line((x+3,22,x+3,40),fill='#968a71')
            d.rectangle((x,40,x+6,49),fill='#ffcf68',outline='#805324')
            d.line((x+1,42,x+5,42),fill='#fff3b5')
        # Rieles bajo los destinos, sin ocupar sus casillas.
        y=40+17+rows*18-2
        for x in range(32,192,10): d.rectangle((x,y,x+4,y+5),fill=edge)
        d.line((31,y,192,y),fill='#a09c8b'); d.line((31,y+4,192,y+4),fill='#a09c8b')
        for x in (18,200):
            for y in range(57,h-12,32):
                d.line((x,y,x+4,y+9),fill='#35271e')
                d.point((x+3,y+4),fill='#d2ab63')
        if kind=='minas':
            text(im,'ELEGI TU PROXIMA VETA',(112,134),color='#cab895')
        else:
            text(im,'VENDER TODO',(112,64),color='#9ed8ae')
    for slot in USED[kind]:
        x,y=31+slot%9*18,57+slot//9*18
        color = bright
        if kind=='minas' and 9<=slot<=34:
            color = ('#a6aaa3','#cb9f59','#61cdd0')[(slot//9)-1]
        d.rectangle((x,y,x+17,y+17),fill='#10131a',outline=color)
        d.rectangle((x+1,y+1,x+16,y+16),fill=(0,0,0,0))
    shift=(6-rows)*18
    text(im, 'INVENTARIO', (112,168-shift), color='#b3a999')
    for row in range(4):
        for col in range(9):
            x=31+col*18; y=(180+row*18 if row<3 else 238)-shift
            d.rectangle((x,y,x+17,y+17),fill=floor,outline=edge)
            d.rectangle((x+1,y+1,x+16,y+16),fill=(0,0,0,0))
    return im


def icon(name):
    im=Image.new('RGBA',(16,16)); d=ImageDraw.Draw(im)
    if name in ('nether','end'):
        color = '#de615f' if name=='nether' else '#ece7ac'
        d.rectangle((2,1,13,14),fill='#30243f',outline='#8e789b')
        d.rectangle((5,3,10,12),fill=color)
        d.line((6,4,6,10),fill='#fff1d5')
        for x,y in ((1,5),(14,9),(4,14)): d.point((x,y),fill=color)
    elif name=='parkour':
        for x,y in ((1,11),(6,7),(11,3)):
            d.rectangle((x,y,x+4,y+3),fill='#7d5eac',outline='#e0d0fa')
    elif name=='arenas':
        for flip in (False, True):
            blade=Image.new('RGBA',(16,16)); b=ImageDraw.Draw(blade)
            b.line((3,12,12,3),fill='#cde9ed',width=3); b.line((3,9,6,12),fill='#e5b85b',width=2)
            b.line((1,14,4,11),fill='#875c37',width=2)
            im.alpha_composite(blade.transpose(Image.Transpose.FLIP_LEFT_RIGHT) if flip else blade)
    elif name=='lobby':
        d.polygon(((1,7),(8,1),(14,7)),fill='#9bdac5'); d.rectangle((3,7,12,14),fill='#4d8b82');d.rectangle((7,9,9,14),fill='#172d39')
    elif name=='cerrar':
        d.line((4,4,11,11),fill='#ed8c86',width=3);d.line((4,11,11,4),fill='#ed8c86',width=3)
    elif name=='sell':
        d.polygon(((8,1),(14,6),(8,14),(2,6)),fill='#62d39c',outline='#d1ffe5'); d.line((5,5,8,3),fill='#e0ffdf',width=2)
    elif name.startswith('tier'):
        c={'tier1':'#b9b7a8','tier2':'#d0a35b','tier3':'#64dae2'}[name]
        d.rectangle((0,0,15,15),fill='#24292a',outline=c)
        text(im,{'tier1':'I','tier2':'II','tier3':'III'}[name],(8,4),color=c)
    else:
        colors={'tier1':'#b9b7a8','tier2':'#d0a35b','tier3':'#64dae2','info':'#e7bf58'}
        c=colors.get(name,'#b9b7a8')
        d.rectangle((3,3,12,12),fill='#3c4447',outline=c)
        for x,y in ((5,5),(9,8),(5,10)):d.rectangle((x,y,x+2,y+1),fill=c)
    return im


def assets():
    files={}; providers=[]; advances={}
    def put(path,im):
        out=io.BytesIO();im.save(out,'PNG');files[path]=out.getvalue()
    for kind in KINDS:
        im=panel(kind); i=KINDS.index(kind); base=0xe900+i*6
        advances[chr(base)]=-32; advances[chr(base+5)]=32
        for n,(start,end,ascent) in enumerate(((0,56,53),(56,im.height,-3))):
            part=im.crop((0,start,224,end)); name=f'font/viajes/{kind}_{n}'
            put(f'assets/astral/textures/{name}.png',part)
            providers.append({'type':'bitmap','file':f'astral:{name}.png','height':part.height,'ascent':ascent,'chars':[chr(base+1+n*2)]})
            advances[chr(base+2+n*2)]=-(part.getbbox()[2]+1)
    providers.append({'type':'space','advances':advances})
    for name in ('nether','end','parkour','arenas','lobby','cerrar','sell','tier1','tier2','tier3','info'):
        put(f'assets/astral/textures/item/viajes/{name}.png',icon(name))
        files[f'assets/astral/models/viajes/{name}.json']=json.dumps({'parent':'minecraft:item/generated','textures':{'layer0':f'astral:item/viajes/{name}'}}).encode()
        files[f'assets/astral/items/viajes/{name}.json']=json.dumps({'model':{'type':'minecraft:model','model':f'astral:viajes/{name}'}}).encode()
    return files,providers


def previews(folder):
    from minas import MINES, slot
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    mapping={'portales':{10:'nether',12:'end',14:'parkour',16:'arenas',22:'lobby',26:'cerrar'},
             'minas':{4:'info',9:'tier1',18:'tier2',27:'tier3',45:'info',49:'lobby',53:'cerrar'},
             'minas-venta':{13:'sell',22:'cerrar'}}
    for kind in KINDS:
        im=Image.new('RGBA',panel(kind).size,'#34373a'); im.alpha_composite(panel(kind))
        for s,name in mapping[kind].items(): im.alpha_composite(icon(name),(32+s%9*18,58+s//9*18))
        if kind=='minas':
            for i,mine in enumerate(MINES,1):
                s=slot(i); material=mine[2]
                path=Path(__file__).parent/f'pack-source/vanilla-base/item/{material}.png'
                if path.exists():
                    art=Image.open(path).convert('RGBA').crop((0,0,16,16))
                else:
                    # Representación original de cada mineral vanilla para la maqueta.
                    colors={'coal':'#575359','copper':'#c88861','iron':'#d5baa7','gold':'#f1ca55',
                            'emerald':'#69d59b','diamond':'#8ae2e1','netherite':'#82737a','ancient':'#82737a'}
                    color=next((c for key,c in colors.items() if key in material),'#aaa89b')
                    art=Image.new('RGBA',(16,16)); block=ImageDraw.Draw(art)
                    block.polygon(((1,4),(8,1),(14,4),(14,12),(8,15),(1,12)),fill='#565b5d',outline='#989a91')
                    for x,y in ((4,5),(9,4),(10,9),(4,10)):block.rectangle((x,y,x+2,y+2),fill=color)
                im.alpha_composite(art,(32+s%9*18,58+s//9*18))
        im.resize((im.width*4,im.height*4),Image.Resampling.NEAREST).save(folder/f'{kind}.png')


if __name__=='__main__':
    previews(Path(__file__).resolve().parents[1]/'build/Interfaces-preview')
