"""Marcos e iconos exclusivos de los servicios, sin reemplazar GUI globales."""
import io
import json
from pathlib import Path
from PIL import Image, ImageDraw
from escape_menu import text
from items import MEJORAS

ROOT = Path(__file__).resolve().parent
OFFSET = (24, 40)
SIZE = (224, 280)
SPLIT = 56
THEMES = {
    'herrero': ('herrero', (132, 220, 990, 1270), 'HERRERO ASTRAL', 29, '#25272a', '#776345'),
    'bazar': ('bazar', (150, 325, 977, 1275), 'BAZAR DEL REFUGIO', 13, '#2a211a', '#86612e'),
    'tienda': ('comercio', (180, 255, 935, 1260), 'TIENDA', 35, '#22252b', '#787a80'),
    'compra': ('comercio', (180, 255, 935, 1260), 'COMPRAR', 35, '#22252b', '#787a80'),
    'venta': ('comercio', (180, 255, 935, 1260), 'VENTA RAPIDA', 35, '#22252b', '#787a80'),
    'venta_tienda': ('comercio', (180, 255, 935, 1260), 'VENDER', 35, '#22252b', '#787a80'),
}
GLYPHS = {name: (chr(0xe450+i*2), chr(0xe451+i*2)) for i,name in enumerate(THEMES)}
START, BACK, END = '\ue460', '\ue461', '\ue462'
REWINDS = {name:(chr(0xe470+i*2),chr(0xe471+i*2)) for i,name in enumerate(THEMES)}


def png(image):
    out=io.BytesIO();image.save(out,'PNG');return out.getvalue()


def frame(kind):
    art, (left, top, right, bottom), caption, ty, fill, edge = THEMES[kind]
    source=Image.open(ROOT/f'pack-source/ref/{art}-frame.png').convert('RGBA')
    # Nueve cortes mantienen las esquinas y colocan el borde FUERA de los slots.
    sx=[0,left,right,source.width]; sy=[0,top,bottom,source.height]
    dx=[0,24,200,224];dy=[0,56,258,280]
    out=Image.new('RGBA',SIZE)
    for row in range(3):
        for col in range(3):
            piece=source.crop((sx[col],sy[row],sx[col+1],sy[row+1]))
            out.alpha_composite(piece.resize((dx[col+1]-dx[col],dy[row+1]-dy[row]),Image.Resampling.NEAREST),(dx[col],dy[row]))
    text(out,caption,(112,ty),color='#fff0cd')
    return out


def bazar_regions():
    return [('comprar',range(0,4),range(1,3)),('vender',range(5,9),range(1,3)),
            ('subastas',range(0,4),range(3,5)),('ordenes',range(5,9),range(3,5))]


def panel(kind):
    out=frame(kind);d=ImageDraw.Draw(out);ox,oy=OFFSET
    fill,edge=THEMES[kind][4:]
    d.rectangle((ox,oy+16,ox+175,oy+218),fill=fill)
    def box(rect,**kw):d.rectangle(tuple(v+(ox if i%2==0 else oy) for i,v in enumerate(rect)),**kw)
    for row in range(6):
        for col in range(9):
            x,y=7+col*18,17+row*18
            box((x,y,x+17,y+17),fill=fill,outline=edge)
    box((7,128,168,137),fill='#bab7aa')
    for row in range(3):
        for col in range(9):
            x,y=7+col*18,139+row*18
            box((x,y,x+17,y+17),fill=fill,outline=edge)
    for col in range(9):
        x=7+col*18;box((x,197,x+17,214),fill=fill,outline=edge)
    def hole(rect):box(rect,fill=(0,0,0,0))
    for row in range(6):
        for col in range(9):
            x,y=8+col*18,18+row*18;hole((x,y,x+15,y+15))
    for row in range(3):
        for col in range(9):
            x,y=8+col*18,140+row*18;hole((x,y,x+15,y+15))
    for col in range(9):
        x=8+col*18;hole((x,198,x+15,213))
    if kind=='bazar':
        for _,cols,rows in bazar_regions():
            hole((7+min(cols)*18,17+min(rows)*18,6+(max(cols)+1)*18,16+(max(rows)+1)*18))
    elif kind=='herrero':
        box((24,35,79,88),fill='#1d1e20',outline='#aa7947')
        box((42,52,61,71),fill='#090d11',outline='#67c7d2')
        hole((44,54,59,69)) # slot 20: objeto REAL depositado
        text(out,'EQUIPO',(ox+52,oy+39),color='#eac58a')
        text(out,'MATERIALES',(ox+124,oy+39),color='#eac58a')
        hole((25,71,150,88)) # estado / nivel / dinero / probabilidad
        hole((61,89,114,106)) # MEJORAR
    elif kind in ('compra','venta_tienda','venta'):
        box((99,32,150,86),fill='#841a24',outline='#b96d65')
        box((113,51,134,72),fill='#11151b',outline='#d6d3c7')
        hole((116,54,131,69)) # objeto seleccionado (slot 24)
        if kind=='venta':
            hole((25,71,150,88))
            hole((97,89,168,106))
            text(out,'VALOR',(ox+52,oy+39),color='#e1d7bd')
        else:
            for slot,label in [(9,'-1'),(18,'-16'),(27,'-32'),(12,'+1'),(21,'+16'),(30,'+32')]:
                x,y=7+(slot%9)*18,17+(slot//9)*18
                color='#6f2931' if label.startswith('-') else '#28683c'
                box((x,y,x+35,y+17),fill=color,outline='#b7b9b6')
                text(out,label,(ox+x+18,oy+y+5),color='#ffffff')
            b=button('COMPRAR' if kind=='compra' else 'VENDER',72,'#34692e' if kind=='compra' else '#8b2832')
            out.alpha_composite(b,(ox+97,oy+89))
    return out


def button(caption,width=54,color='#366b48'):
    im=Image.new('RGBA',(width,18),color);d=ImageDraw.Draw(im)
    d.rectangle((0,0,width-1,17),outline='#cbb47c');d.rectangle((1,1,width-2,16),outline='#101719')
    d.line((2,2,width-3,2),fill='#d5d3ba');text(im,caption,(width//2,5),color='#ffffff');return im


def banner(caption,color='#ddc699'):
    im=Image.new('RGBA',(126,18),'#24272b');d=ImageDraw.Draw(im)
    d.rectangle((0,0,125,17),outline='#a17e44');text(im,caption,(63,5),color=color);return im


def card(caption,sub,color):
    im=Image.new('RGBA',(72,36),color);d=ImageDraw.Draw(im)
    d.rectangle((0,0,71,35),outline='#c3a25d');d.rectangle((2,2,69,33),outline='#503921')
    text(im,caption,(36,8),color='#fff0ba');text(im,sub,(36,22),color='#c1d3b1');return im


def title(kind):
    first,second=GLYPHS[kind]
    a,b=REWINDS[kind]
    return '&f'+START+first+a+second+b+END


def assets():
    files,providers={},[]
    def model(name,im):
        resource=f'astral:item/servicios/{name}'
        files[f'assets/astral/textures/item/servicios/{name}.png']=png(im)
        files[f'assets/astral/models/servicios/{name}.json']=json.dumps({'parent':'minecraft:item/generated','gui_light':'front',
            'textures':{'layer0':resource},'display':{'gui':{'scale':[im.width/16,im.height/16,1]}}}).encode()
        files[f'assets/astral/items/servicios/{name}.json']=json.dumps({'oversized_in_gui':max(im.size)>16,
            'model':{'type':'minecraft:model','model':f'astral:servicios/{name}'}}).encode()
    def tiles(name,im):
        for row in range(im.height//18):
            for col in range(im.width//18):
                index=row*(im.width//18)+col
                model(f'{name}_{index}',im.crop((col*18,row*18,col*18+18,row*18+18)))
    advances={START:-32,END:32}
    for kind,chars in GLYPHS.items():
        image=panel(kind)
        for n,(part,ascent,char) in enumerate([(image.crop((0,0,224,SPLIT)),53,chars[0]),(image.crop((0,SPLIT,224,image.height)),-3,chars[1])]):
            files[f'assets/astral/textures/font/servicios/{kind}_{n}.png']=png(part)
            providers.append({'type':'bitmap','file':f'astral:font/servicios/{kind}_{n}.png','height':part.height,'ascent':ascent,'chars':[char]})
            advances[REWINDS[kind][n]]=-(part.getbbox()[2]+1)
    providers.append({'type':'space','advances':advances})
    for key,caption,sub,color in [('comprar','COMPRAR','TIENDA','#304e36'),('vender','VENDER','VENTA RAPIDA','#60432b'),
                                  ('subastas','SUBASTAS','JUGADORES','#5d4928'),('ordenes','ORDENES','ENCARGOS','#2b4750')]:
        tiles('bazar_'+key,card(caption,sub,color))
    for name,caption,width,color in [('improve','MEJORAR',54,'#366b48'),('blocked','MEJORAR',54,'#683c36'),
                                     ('sell','VENDER',72,'#93333a'),('sell_blocked','VENDER',72,'#59434a')]:
        tiles(name,button(caption,width,color))
    bars={'empty':('COLOCA TU EQUIPO','#ddc699'),'invalid':('EQUIPO NO MEJORABLE','#ec998b'),'max':('NIVEL MAXIMO +10','#e8d475'),
          'sale_empty':('ELIGE QUE VENDER','#ddc699'),'sale_ready':('REVISA EL IMPORTE','#9ed7b0'),'sold':('VENTA COMPLETADA','#9ed7b0'),
          'not_sold':('NO SE VENDIO EL ITEM','#ec998b')}
    for level,(money,chance,_) in MEJORAS.items():
        bars[f'level{level}']=(f'+{level} / {money}$ / {round(chance*100)}%','#ddc699')
        bars[f'ok{level}']=(f'MEJORA EXITOSA +{level}','#9ed7b0')
        bars[f'fail{level}']=(f'FALLO / EQUIPO INTACTO','#ec998b')
    for name,(caption,color) in bars.items():tiles('bar_'+name,banner(caption,color))
    return files,providers


def previews(folder):
    folder=Path(folder);folder.mkdir(exist_ok=True,parents=True)
    for kind in THEMES:
        im=Image.new('RGBA',SIZE,'#252a28');im.alpha_composite(panel(kind))
        if kind=='bazar':
            for (key,cols,rows),(caption,sub,color) in zip(bazar_regions(),[('COMPRAR','TIENDA','#304e36'),('VENDER','VENTA RAPIDA','#60432b'),('SUBASTAS','JUGADORES','#5d4928'),('ORDENES','ENCARGOS','#2b4750')]):
                im.alpha_composite(card(caption,sub,color),(24+7+min(cols)*18,40+17+min(rows)*18))
        elif kind=='herrero':
            im.alpha_composite(banner('+1 / 300$ / 100%'),(24+25,40+71));im.alpha_composite(button('MEJORAR'),(24+61,40+89))
        elif kind=='venta':
            im.alpha_composite(banner('REVISA EL IMPORTE'),(24+25,40+71));im.alpha_composite(button('VENDER',72,'#93333a'),(24+97,40+89))
        text(im,'Inventario',(24+37,40+129),color='#383c40')
        target=folder/f'{kind}.png';temp=target.with_suffix('.png.tmp');temp.write_bytes(png(im.resize((672,840),Image.Resampling.NEAREST)));temp.replace(target)


if __name__=='__main__':previews(ROOT.parent/'build/Servicios-preview')
