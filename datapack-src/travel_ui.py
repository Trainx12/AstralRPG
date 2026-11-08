"""Adaptador de viajes: marcos ImageGen y composicion compartida de servicios."""
import io
import json
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance
from escape_menu import text
from services_ui import ornament, button, banner, card

KINDS=('portales','minas','minas-venta','arenas')
ROWS={'portales':6,'minas':6,'minas-venta':5,'arenas':6}
CAPTIONS={'portales':'PORTALES ASTRALES','minas':'MINAS ASTRALES','minas-venta':'VENTA RAPIDA','arenas':'ARENAS PvP'}
# 4 tarjetas de 40 px sobre las 9 columnas: cada columna va a la tarjeta que tiene su centro.
CARD_COLS=((0,1),(2,3,4),(5,6),(7,8))
CARD_SLOTS={key:[r*9+c for r in (0,1,2,3) for c in CARD_COLS[i]] for i,key in enumerate(('nether','end','parkour','arenas'))}
ARENA_SLOTS=dict(zip(('clasica','tft1','tft2','tft3'),CARD_SLOTS.values()))
SALE_SLOTS=tuple(range(28,35))
# Tira de la venta: items vanilla reales en la fila superior (solo muestran que se vende).
SALE_STRIP={1:'coal',2:'iron_ingot',3:'gold_ingot',4:'emerald',5:'diamond'}
# Icono vanilla de cada mina: I = mineral, II = mena, III = bloque. El cliente ya trae estas texturas.
VANILLA=['item/coal','item/copper_ingot','item/iron_ingot','item/gold_ingot','item/emerald','item/diamond',
         'block/coal_ore','block/copper_ore','block/iron_ore','block/gold_ore','block/emerald_ore','block/diamond_ore','block/ancient_debris_side',
         'block/coal_block','block/copper_block','block/iron_block','block/gold_block','block/emerald_block','block/diamond_block','block/netherite_block']
FRAME_COLORS={'open':'#71e07a','next':'#f2c94c','locked':'#656171'}
USED={'portales':set(sum(CARD_SLOTS.values(),[]))|{45,46,47,51,52,53},'arenas':set(sum(ARENA_SLOTS.values(),[]))|{45,46,47,51,52,53},
      'minas':{4,9,18,27,45,49,53,*range(10,16),*range(19,26),*range(28,35)},'minas-venta':set(SALE_SLOTS)|{35}|set(SALE_STRIP)}
GRID_Y=57


def slices(kind):
    h=280
    return [(y,min(y+128,h)) for y in range(0,h,128)]


def title(kind):
    base=0xe900+KINDS.index(kind)*16
    return '&f'+''.join(chr(base+i) for i in range(2+4*len(slices(kind))))


def bevel(d,box,fill='#353544',edge='#77778b'):
    x,y,x2,y2=box
    d.rectangle(box,fill=fill,outline='#090a10')
    d.line((x+1,y+1,x2-1,y+1,x2-1,y2-1),fill='#171720',width=2)
    d.line((x+1,y2-1,x+1,y+1,x2-1,y+1),fill=edge,width=2)


# Los cortes son coordenadas del centro vacio de cada original ImageGen.
THEMES={
    'portales':('portales',(157,365,963,1300),44,'#170e25','#a782ca'),
    'minas':('minas',(120,405,1000,1270),44,'#25272a','#776345'),
    'arenas':('arenas',(150,375,975,1245),35,'#22252b','#787a80'),
    'minas-venta':('venta_minerales',(100,325,1030,1285),23,'#2a211a','#ac823d'),
}


def illustration(kind,index):
    source=Image.open(Path(__file__).parent/f'pack-source/ref/{kind}-cards.png').convert('RGBA')
    return source.crop((round(index*source.width/4),0,round((index+1)*source.width/4),source.height)).resize((36,56),Image.Resampling.LANCZOS)


def label(im,caption,center,width=32):
    # Solo las etiquetas estrechas se reducen; el titulo usa la fuente comun sin escalar.
    art=Image.new('RGBA',(200,10));text(art,caption,(100,0),color='#fff0cd')
    art=art.crop(art.getbbox())
    if art.width>width:
        # Sin espacio entre letras en vez de estirar: estirar deforma la fuente.
        parts=[]
        for ch in caption:
            g=Image.new('RGBA',(16,10));text(g,ch,(8,0),color='#fff0cd');b=g.getbbox()
            parts.append(g.crop(b) if b else Image.new('RGBA',(3,8)))
        art=Image.new('RGBA',(sum(x.width for x in parts),max(x.height for x in parts)));x=0
        for part in parts:art.alpha_composite(part,(x,art.height-part.height));x+=part.width
    im.alpha_composite(art,(center[0]-art.width//2,center[1]))


def panel(kind):
    art,cuts,ty,fill,edge=THEMES[kind]
    rows=ROWS[kind];im=ornament(art,cuts);d=ImageDraw.Draw(im)
    text(im,CAPTIONS[kind],(112,ty),color='#fff0cd')
    d.rectangle((24,56,199,257),fill=fill)
    if kind in ('portales','arenas'):
        labels=('Nether','End','Parkour','Arenas') if kind=='portales' else ('Coliseo','Ruinas','Vacio','Volcan')
        for i,caption in enumerate(labels):
            x,y=31+round(i*40.5),GRID_Y
            # Tarjeta de 40x72: pintura arriba y nombre abajo, borde dorado como el concepto.
            plaque=Image.new('RGBA',(40,72),'#302738');pd=ImageDraw.Draw(plaque)
            plaque.alpha_composite(illustration(kind,i),(2,2))
            pd.rectangle((1,59,38,70),fill='#1d1726')
            pd.rectangle((0,0,39,71),outline='#c3a25d');pd.line((1,58,38,58),fill='#c3a25d')
            label(plaque,caption,(20,61),37)
            im.alpha_composite(plaque,(x,y))
        label(im,'Elegi tu campo de batalla' if kind=='arenas' else 'Cruza tu proximo umbral',(112,135),160)
        im.alpha_composite(button('',54,'#60432b'),(31,147))
        # La casilla 45 muestra la barrera vanilla (item real); aca solo el texto.
        text(im,'Lobby',(67,152),color='#fff0cd')
        im.alpha_composite(button('',54,'#683c36'),(139,147))
        im.alpha_composite(icon('cerrar'),(158,148))
    elif kind=='minas':
        # Banner de saldo: el importe sigue en el nombre/lore del item real.
        im.alpha_composite(banner('TU ORO ($)'),(49,57))
        for slot in USED[kind]:
            if slot==4:continue
            x,y=31+slot%9*18,GRID_Y+slot//9*18
            d.rectangle((x,y,x+17,y+17),fill=fill,outline=edge)
            d.rectangle((x+1,y+1,x+16,y+16),fill=(0,0,0,0))
        label(im,'Abierta - Siguiente - Bloqueada',(112,134),162)
    else:
        # Los minerales de la tira son items vanilla reales (SALE_STRIP); aca solo sus casilleros.
        for col in SALE_STRIP:
            x=31+col*18;d.rectangle((x,GRID_Y,x+17,GRID_Y+17),fill='#1a2029',outline='#ac823d')
        text(im,'>',(31+6*18+9,GRID_Y+5),color='#e8c55b');im.alpha_composite(icon('coin'),(31+7*18+1,GRID_Y+1))
        im.alpha_composite(banner('RECIBIS'),(49,85))
        im.alpha_composite(button('VENDER TODO',126,'#366b48'),(49,111))
        im.alpha_composite(button('',18,'#683c36'),(175,111))
        im.alpha_composite(icon('cerrar'),(176,112))
        label(im,'Tu equipo Astral no se vende',(112,134),162)
    inventory(im,rows,fill,edge)
    return im.resize((448,560),Image.Resampling.NEAREST)


def inventory(im,rows,fill,edge):
    d=ImageDraw.Draw(im);shift=(6-rows)*18
    # Las mismas coordenadas, franja y cuatro filas de services_ui.panel.
    d.rectangle((31,168-shift,192,177-shift),fill='#bab7aa')
    text(im,'Inventario',(61,169-shift),color='#383c40')
    for row in range(4):
        for col in range(9):
            x=31+col*18;y=(179+row*18 if row<3 else 237)-shift
            d.rectangle((x,y,x+17,y+17),fill=fill,outline=edge)
            d.rectangle((x+1,y+1,x+16,y+16),fill=(0,0,0,0))


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
        for flip in (False,True):
            blade=Image.new('RGBA',(16,16));b=ImageDraw.Draw(blade)
            b.polygon(((4,10),(10,2),(13,1),(13,4),(6,12)),fill='#d0e1e5',outline='#687685')
            b.line((5,10,11,3),fill='#ffffff')
            b.line((3,9,7,13),fill='#e5b85b',width=2);b.line((2,14,4,12),fill='#875c37',width=2)
            im.alpha_composite(blade.transpose(Image.Transpose.FLIP_LEFT_RIGHT) if flip else blade)
    elif name=='lobby':
        d.polygon(((1,7),(8,1),(14,7)),fill='#eaa35b'); d.rectangle((3,7,12,14),fill='#9a592e');d.rectangle((7,9,9,14),fill='#172d39')
    elif name=='cerrar':
        d.line((4,4,11,11),fill='#ed655e',width=2);d.line((4,11,11,4),fill='#ed655e',width=2)
    elif name=='coin':
        d.ellipse((1,1,14,14),fill='#c8962a',outline='#fff1a8',width=2)
        d.ellipse((4,3,11,12),outline='#f2c94c')
        d.line((7,5,7,10),fill='#fff1a8',width=2)
    elif name in ('info','gold'):
        im=button('?' if name=='info' else '$',18).crop((1,1,17,17))
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



def mine_frame(state):
    im=Image.new('RGBA',(16,16));d=ImageDraw.Draw(im)
    bevel(d,(0,0,15,15),'#4a4f5c',FRAME_COLORS[state])
    if state=='open':d.rectangle((1,1,14,14),outline=FRAME_COLORS[state])
    return im


def lock_icon():
    im=Image.new('RGBA',(16,16));d=ImageDraw.Draw(im)
    d.arc((9,6,15,13),180,360,fill='#ffdc73',width=1)
    d.rectangle((8,10,15,15),fill='#c8962a',outline='#5a3d14');d.point((11,12),fill='#3a2614');d.point((12,12),fill='#3a2614')
    return im


def vanilla_texture(path):
    """Solo para las vistas previas: lee la textura del cliente instalado. El pack NO la incluye."""
    import os,zipfile
    jar=Path(os.environ.get('MC_JAR',Path(os.environ.get('APPDATA',''))/'.minecraft/versions/26.1.2/26.1.2.jar'))
    if not jar.exists():return None
    with zipfile.ZipFile(jar) as z:
        im=Image.open(io.BytesIO(z.read(f'assets/minecraft/textures/{path}.png'))).convert('RGBA')
    return im.crop((0,0,16,16))


def mine_model(index,state):
    """Modelo plano: marco astral + textura vanilla del cliente + candado si esta bloqueada."""
    def plane(z,box,tex,tint=False):
        face={'uv':[0,0,16,16],'texture':tex}
        if tint:face['tintindex']=0
        back=dict(face,uv=[16,0,0,16])
        return {'from':[box[0],box[1],z],'to':[box[2],box[3],z],'shade':False,'faces':{'south':face,'north':back}}
    elements=[plane(7.9,(0,0,16,16),'#frame'),plane(8,(2,2,14,14),'#icon',True)]
    textures={'frame':f'astral:item/viajes/frame_{state}','icon':'minecraft:'+VANILLA[index-1],'particle':f'astral:item/viajes/frame_{state}'}
    if state=='locked':
        elements.append(plane(8.1,(0,0,16,16),'#lock'));textures['lock']='astral:item/viajes/lock'
    return {'textures':textures,'gui_light':'front','elements':elements,
            'display':{'gui':{'rotation':[0,0,0],'translation':[0,0,0],'scale':[1,1,1]}}}


def mine_icon(index,state):
    """Vista previa del modelo de mina (en el juego lo arma el cliente con mine_model)."""
    im=mine_frame(state);tex=vanilla_texture(VANILLA[index-1])
    if tex is not None:
        tex=tex.resize((12,12),Image.Resampling.NEAREST)
        if state=='locked':tex=ImageEnhance.Brightness(tex).enhance(.65)
        im.alpha_composite(tex,(2,2))
    if state=='locked':im.alpha_composite(lock_icon())
    return im


def assets():
    files={};providers=[];advances={}
    def put(path,im):
        out=io.BytesIO();im.save(out,'PNG');files[path]=out.getvalue()
    for kind in KINDS:
        im=panel(kind);base=0xe900+KINDS.index(kind)*16;advances[chr(base)]=-32
        for n,(start,end) in enumerate(slices(kind)):
            for col in range(2):
                part=im.crop((col*224,start*2,(col+1)*224,end*2));name=f'font/viajes/{kind}_{n}_{col}'
                put(f'assets/astral/textures/{name}.png',part)
                code=base+1+n*4+col*2
                providers.append({'type':'bitmap','file':f'astral:{name}.png','height':end-start,'ascent':53-start,'chars':[chr(code)]})
                advance=math.ceil(part.getbbox()[2]/2)+1
                # Tras la izquierda avanzar 112; tras la derecha volver al origen.
                advances[chr(code+1)]=(112-advance) if col==0 else -(112+advance)
        advances[chr(base+1+len(slices(kind))*4)]=32
    providers.append({'type':'space','advances':advances})
    icons={n:icon(n) for n in ('nether','end','parkour','arenas','lobby','cerrar','sell','tier1','tier2','tier3','info','gold')}
    icons['blank']=Image.new('RGBA',(16,16))
    for name,im in icons.items():
        put(f'assets/astral/textures/item/viajes/{name}.png',im)
        files[f'assets/astral/models/viajes/{name}.json']=json.dumps({'parent':'minecraft:item/generated','textures':{'layer0':f'astral:item/viajes/{name}'}}).encode()
        files[f'assets/astral/items/viajes/{name}.json']=json.dumps({'model':{'type':'minecraft:model','model':f'astral:viajes/{name}'}}).encode()
    for state in FRAME_COLORS:put(f'assets/astral/textures/item/viajes/frame_{state}.png',mine_frame(state))
    put('assets/astral/textures/item/viajes/lock.png',lock_icon())
    flat={'gui_light':'front','display':{'gui':{'rotation':[0,0,0],'translation':[0,0,0],'scale':[1,1,1]}}}
    def plane_model(tex,z):
        face={'uv':[0,0,16,16],'texture':'#t'}
        return dict(flat,textures={'t':tex,'particle':tex},elements=[{'from':[0,0,z],'to':[16,16,z],'shade':False,
                    'faces':{'south':face,'north':dict(face,uv=[16,0,0,16])}}])
    for state in FRAME_COLORS:
        # Marco detras (z=0) y candado delante (z=16) del cubo vanilla.
        files[f'assets/astral/models/viajes/frame_{state}.json']=json.dumps(plane_model(f'astral:item/viajes/frame_{state}',0)).encode()
    files['assets/astral/models/viajes/lock_front.json']=json.dumps(plane_model('astral:item/viajes/lock',16)).encode()
    for i in range(1,21):
        for state in FRAME_COLORS:
            name=f'mine_{i}_{state}'
            if VANILLA[i-1].startswith('item/'):
                model={'type':'minecraft:model','model':f'astral:viajes/{name}'}
                # Bloqueada: el icono vanilla se oscurece con un tinte fijo.
                if state=='locked':model['tints']=[{'type':'minecraft:constant','value':0xa0a0aa}]
                files[f'assets/astral/models/viajes/{name}.json']=json.dumps(mine_model(i,state)).encode()
            else:
                # Las texturas de bloque no se pueden usar en un modelo de item propio (salen violeta y negro):
                # se combina el modelo vanilla del bloque, que el cliente ya trae.
                block=VANILLA[i-1].split('/')[1].replace('ancient_debris_side','ancient_debris')
                parts=[{'type':'minecraft:model','model':f'astral:viajes/frame_{state}'},
                       {'type':'minecraft:model','model':f'minecraft:block/{block}'}]
                if state=='locked':parts.append({'type':'minecraft:model','model':'astral:viajes/lock_front'})
                model={'type':'minecraft:composite','models':parts}
            files[f'assets/astral/items/viajes/{name}.json']=json.dumps({'model':model}).encode()
    return files,providers


def previews(folder,concept=None):
    from minas import MINES,slot
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    for kind in KINDS:
        im=Image.new('RGBA',(448,560),'#252a28');im.alpha_composite(panel(kind))
        if kind=='minas':
            mapping={9:icon('tier1'),18:icon('tier2'),27:icon('tier3'),45:icon('info'),53:icon('cerrar')}
            barrier=vanilla_texture('item/barrier')
            if barrier is not None:mapping[49]=barrier
            mapping.update({slot(i):mine_icon(i,'open' if i<=5 else 'next' if i==6 else 'locked') for i in range(1,len(MINES)+1)})
            for s,art in mapping.items():im.alpha_composite(art.resize((32,32),Image.Resampling.NEAREST),((32+s%9*18)*2,(GRID_Y+1+s//9*18)*2))
        if kind in ('portales','arenas'):
            art=vanilla_texture('item/barrier')
            if art is not None:im.alpha_composite(art.resize((32,32),Image.Resampling.NEAREST),((32+0*18)*2,(GRID_Y+1+5*18)*2))
        if kind=='minas-venta':
            for s,name in SALE_STRIP.items():
                art=vanilla_texture('item/'+name)
                if art is not None:im.alpha_composite(art.resize((32,32),Image.Resampling.NEAREST),((32+s*18)*2,(GRID_Y+1)*2))
        im.resize((672,840),Image.Resampling.NEAREST).save(folder/f'{kind}.png')
    comparison(folder,concept)


def comparison(folder,concept=None):
    root=Path(__file__).resolve().parents[1]
    # La referencia privada se incorpora solo si se pasa explicitamente. No es dependencia del pack.
    boxes={'portales':(20,76,765,560),'minas':(774,74,1518,562),'arenas':(15,556,768,1018),'minas-venta':(775,563,1520,1018)}
    sheet=Image.new('RGBA',(672*5,880*4),'#252a28')
    original=Image.open(concept).convert('RGBA') if concept else None
    for row,kind in enumerate(KINDS):
        y=row*880
        if original:
            art=original.crop(boxes[kind]);art.thumbnail((672,800),Image.Resampling.NEAREST)
            sheet.alpha_composite(art,((672-art.width)//2,y+40+(800-art.height)//2))
            text(sheet,'CONCEPTO',(336,y+15))
        sheet.alpha_composite(Image.open(folder/f'{kind}.png'),(672,y+40))
        text(sheet,CAPTIONS[kind],(1008,y+15))
        for col,name in enumerate(('herrero','bazar','gacha_rpg'),2):
            sheet.alpha_composite(Image.open(root/f'build/Servicios-preview/{name}.png'),(col*672,y+40))
            text(sheet,name.upper(),(col*672+336,y+15))
    sheet.save(folder/'comparacion.png')


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--concept',type=Path)
    args=parser.parse_args()
    previews(Path(__file__).resolve().parents[1]/'build/Interfaces-preview',args.concept)
