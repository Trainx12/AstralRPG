"""Galeria ceremonial de titulos: azul petroleo, marfil y oro antiguo."""
import json
from pathlib import Path
from PIL import Image,ImageDraw,ImageOps
from services_ui import png,SIZE,SPLIT
from escape_menu import text
from market_ui import band_color
from lobby import TITLES

ROOT=Path(__file__).resolve().parent
FILL,EDGE,ACCENT='#1a1c2d','#b89a5d','#8bdce2'
START,END='\ue700','\ue701'
GLYPHS=tuple(chr(0xe710+i) for i in range(4))
RARITIES={'common':('Comun','#a8bac1'),'uncommon':('Poco comun','#94bc91'),
          'rare':('Raro','#73cee0'),'epic':('Epico','#94b1f0'),'legendary':('Legendario','#edc36b')}
TITLE_SLOTS=tuple(range(10,17))+tuple(range(28,35))
# /cosmeticos (pantalla principal): dos tarjetas de 4x5 casillas.
HUB_CARDS={'titulos':tuple(r*9+c for r in range(5) for c in range(0,4)),
           'sombreros':tuple(r*9+c for r in range(5) for c in range(5,9))}
HUB_START,HUB_END='',''
HUB_GLYPHS=tuple(chr(0xed40+i) for i in range(4))
CLEAR_SLOTS=tuple(range(47,52))


def title():
    return '&f'+START+''.join(GLYPHS)+END


def hub_title():
    return '&f'+HUB_START+''.join(HUB_GLYPHS)+HUB_END


def hub_card(key):
    """Tarjeta grande 72x90: ilustracion de Gemini y cinta con el nombre."""
    from services_ui import illustration
    from adventure_ui import label
    art=illustration('cosmeticos_'+key)
    side=min(art.size);art=art.crop(((art.width-side)//2,(art.height-side)//2,(art.width+side)//2,(art.height+side)//2))
    im=Image.new('RGBA',(72,90),'#0d222f')
    im.alpha_composite(art.resize((288,288),Image.Resampling.BOX).resize((70,70),Image.Resampling.LANCZOS),(1,1))
    d=ImageDraw.Draw(im)
    d.rectangle((0,71,71,89),fill='#14303c')
    d.line((2,72,69,72),fill=EDGE);d.line((2,88,69,88),fill=EDGE)
    label(im,'TITULOS' if key=='titulos' else 'SOMBREROS',(36,77),56,'#f3e4b8')
    d.rectangle((0,0,71,89),outline=EDGE);d.rectangle((1,1,70,88),outline='#3d2c12')
    for cx,cy in ((0,0),(71,0),(0,89),(71,89)):d.point((cx,cy),fill='#8bdce2')
    return im


def hub_panel():
    im=panel('COSMETICOS');d=ImageDraw.Draw(im)
    d.rectangle((24,56,199,165),fill=FILL)
    for key,slots in HUB_CARDS.items():
        x,y=31+slots[0]%9*18,57+slots[0]//9*18
        d.rectangle((x,y,x+71,y+89),fill=(0,0,0,0))
    for slot in (45,49,53):
        x,y=31+slot%9*18,57+slot//9*18
        d.rectangle((x,y,x+17,y+17),outline=EDGE);d.rectangle((x+1,y+1,x+16,y+16),fill=(0,0,0,0))
    d.rectangle((67,147,156,164),fill=FILL)
    return im


def key_for(name):
    return name.lower().replace(' ','_')


def icon(index,color):
    """Emblemas originales para las catorce profesiones y honores."""
    im=Image.new('RGBA',(18,18));d=ImageDraw.Draw(im)
    dark='#244650';light='#f2e8c9'
    if index==0: # brujula
        d.ellipse((4,4,13,13),outline=color)
        d.polygon(((9,4),(11,9),(8,12),(7,8)),fill=light)
    elif index==1: # mapa
        d.polygon(((3,5),(7,4),(11,5),(14,4),(14,12),(10,13),(7,12),(3,13)),fill=color)
        d.line((7,5,7,11),fill=dark);d.line((10,6,12,8,10,10),fill=dark)
    elif index in (2,3,5):
        if index==5: # yunque
            d.polygon(((3,5),(14,5),(12,8),(10,8),(10,11),(13,13),(4,13),(7,11),(7,8),(4,8)),fill=color)
            d.line((5,6,12,6),fill=light)
        else:
            d.line((5,13,11,5),fill='#c3a579',width=2)
            if index==2:d.polygon(((7,4),(12,4),(14,8),(10,9)),fill=color)
            else:d.line((4,5,10,4,14,7),fill=color,width=2)
    elif index in (4,10): # arco y flecha
        if index==4:
            d.arc((3,3,12,14),270,90,fill=color,width=2)
            d.line((8,3,8,14),fill=light)
        d.line((3,9,14,9),fill=light)
        d.polygon(((14,9),(11,7),(11,11)),fill=color)
    elif index==6: # frasco de alquimia
        d.rectangle((7,3,10,6),fill=light)
        d.polygon(((7,6),(4,11),(5,14),(12,14),(13,11),(10,6)),fill=color)
        d.line((6,10,11,10),fill=light)
    elif index==7: # huella
        d.ellipse((6,8,12,13),fill=color)
        for x,y in ((4,6),(7,4),(11,4),(14,6)):d.ellipse((x-1,y-1,x+1,y+1),fill=light)
    elif index==8: # sigilo arcano
        d.polygon(((9,3),(11,7),(15,9),(11,11),(9,15),(7,11),(3,9),(7,7)),fill=color)
        d.rectangle((8,8,9,9),fill=light)
    elif index==9: # espadas cruzadas
        d.line((4,4,13,13),fill=color,width=2);d.line((13,4,4,13),fill=light,width=2)
        d.line((3,10,7,14),fill='#c3a579');d.line((10,14,14,10),fill='#c3a579')
    elif index==11: # copa
        d.rectangle((6,4,11,9),fill=color);d.arc((3,4,14,10),0,180,fill=color)
        d.line((9,9,9,12),fill=color,width=2);d.rectangle((6,12,11,13),fill=light)
    elif index==12: # ojo del abismo
        d.polygon(((3,9),(7,5),(11,5),(15,9),(11,12),(7,12)),fill=color)
        d.ellipse((7,6,11,11),fill=dark);d.line((9,7,9,10),fill=light)
    else: # corona astral
        d.polygon(((3,6),(6,8),(9,3),(12,8),(15,6),(13,13),(5,13)),fill=color)
        d.line((6,12,12,12),fill=light);d.rectangle((8,8,10,10),fill=ACCENT)
    return im


def medal(index,locked=False):
    rarity,_,_=TITLES[index];color=RARITIES[rarity][1]
    im=Image.new('RGBA',(18,18),FILL);d=ImageDraw.Draw(im)
    d.polygon(((4,1),(13,1),(16,4),(16,13),(13,16),(4,16),(1,13),(1,4)),fill='#163f4c',outline=EDGE)
    d.rectangle((4,3,13,14),outline='#365d69')
    # Emblema pintado por Gemini, dentro del marco con el color de la rareza.
    from services_ui import illustration
    im.alpha_composite(illustration(f'titulo_{index}').resize((14,14),Image.Resampling.LANCZOS),(2,2))
    if rarity in ('epic','legendary'):
        d.point((2,2),fill=color);d.point((15,2),fill=color)
        d.point((2,15),fill=color);d.point((15,15),fill=color)
    if not locked:
        d.polygon(((4,1),(13,1),(16,4),(16,13),(13,16),(4,16),(1,13),(1,4)),outline='#f2d27f')
        d.line((4,2,8,2),fill='#fff3cf');d.point((3,3),fill='#fff3cf')
    if locked:
        alpha=im.getchannel('A');im=ImageOps.grayscale(im).convert('RGBA');im.putalpha(alpha)
        # Barniz oscuro sobre el metal: la silueta aun permite reconocer el titulo.
        im=Image.blend(im,Image.new('RGBA',im.size,'#233039'),.50);d=ImageDraw.Draw(im)
        d.rectangle((11,10,16,16),fill='#17242c',outline='#a3adb2')
        d.arc((12,6,15,13),180,360,fill='#ccd4ce')
        d.point((14,13),fill='#d4c79e')
    return im


def nav_icon(kind):
    """Botones del marco en el mismo metal y terciopelo que la galeria."""
    im=Image.new('RGBA',(18,18),FILL);d=ImageDraw.Draw(im)
    d.rectangle((0,0,17,17),outline=EDGE);d.rectangle((1,1,16,16),fill='#163f4c',outline='#365d69')
    d.line((2,1,15,1),fill='#ebdab1')
    gold,ivory,teal='#d9b766','#f2e8c9',ACCENT
    if kind=='info':      # pergamino con la i
        d.rectangle((5,4,12,13),fill=ivory);d.line((4,4,13,4),fill=gold);d.line((4,13,13,13),fill=gold)
        d.point((8,6),fill='#244650');d.line((8,8,8,11),fill='#244650')
    elif kind=='gacha':   # cofre con gema turquesa
        d.rectangle((3,7,14,13),fill='#7a5230',outline=gold);d.rectangle((3,5,14,7),fill='#946238',outline=gold)
        d.line((3,9,14,9),fill=gold);d.rectangle((7,8,10,11),fill=gold)
        d.point((8,9),fill=teal);d.point((9,10),fill=teal)
        d.point((13,3),fill=teal);d.point((15,5),fill='#edc36b')
    elif kind=='back':    # flecha dorada
        d.polygon(((3,9),(8,4),(8,7),(14,7),(14,11),(8,11),(8,14)),fill=gold)
        d.line((9,8,13,8),fill=ivory)
    else:                 # cerrar: aspa marfil
        d.line((5,5,12,12),fill=ivory,width=2);d.line((12,5,5,12),fill=ivory,width=2)
        d.point((8,8),fill='#e07a5f')
    return im


def clear_button():
    im=Image.new('RGBA',(90,18),'#1c3b47');d=ImageDraw.Draw(im)
    d.rectangle((0,0,89,17),outline=EDGE);d.rectangle((2,2,87,15),outline='#587475')
    d.line((3,1,86,1),fill='#ebdab1')
    text(im,'SIN TITULO',(45,5),color='#f2e6c9')
    return im


def panel(caption='COSMETICOS Y TITULOS'):
    # Marco de Gemini (noviembre 2026): interior medido sobre el original.
    source=Image.open(ROOT/'pack-source/ref/cosmeticos2-frame.png').convert('RGBA')
    sx=[0,108,1690,source.width]
    sy=[0,573,2192,source.height]
    dx,dy=[0,24,200,224],[0,56,258,280]
    im=Image.new('RGBA',SIZE)
    for row in range(3):
        for col in range(3):
            piece=source.crop((sx[col],sy[row],sx[col+1],sy[row+1]))
            im.alpha_composite(piece.resize((dx[col+1]-dx[col],dy[row+1]-dy[row]),Image.Resampling.NEAREST),(dx[col],dy[row]))
    from services_ui import outlined
    outlined(im,caption,(112,34))
    d=ImageDraw.Draw(im);d.rectangle((24,56,199,258),fill=FILL)
    # Dos vitrinas; los emblemas ocupan solo las catorce casillas clicables.
    for y,caption in ((75,'OFICIOS Y AVENTURA'),(111,'HONORES Y LEYENDAS')):
        d.rectangle((47,y-2,176,y+33),fill='#0d222f',outline='#6a7a6d')
        d.line((50,y+19,173,y+19),fill=EDGE)
        for cx,cy in ((47,y-2),(176,y-2),(47,y+33),(176,y+33)):
            d.polygon(((cx,cy-2),(cx+2,cy),(cx,cy+2),(cx-2,cy)),fill='#d9b766')
        text(im,caption,(112,y+23),color='#c2d5cf')
        for col in range(7):
            x=49+col*18
            d.line((x,y+19,x,y+21),fill=EDGE)
    for slot in (*TITLE_SLOTS,4,8,45,53):
        x,y=31+slot%9*18,57+slot//9*18
        d.rectangle((x,y,x+17,y+17),outline=EDGE)
        d.rectangle((x+1,y+1,x+16,y+16),fill=(0,0,0,0))
    d.rectangle((67,147,156,164),fill=(0,0,0,0))
    # Inventario real del jugador con la misma ubicacion que el cofre de seis filas.
    d.rectangle((31,168,192,177),fill=band_color(EDGE));d.line((31,167,192,167),fill=EDGE)
    d.line((31,178,192,178),fill=EDGE);d.line((33,169,190,169),fill='#ffffff60')
    for x,s in ((31,1),(192,-1)):
        d.polygon(((x,172),(x+3*s,169),(x+6*s,172),(x+3*s,175)),fill=EDGE)
    for row in (*range(3),4):
        for col in range(9):
            x,y=31+col*18,179+row*18 if row<3 else 237
            d.rectangle((x,y,x+17,y+17),outline='#597477')
            d.rectangle((x+1,y+1,x+16,y+16),fill=(0,0,0,0))
    return im


def assets():
    files,providers={},[];advances={START:-32,END:32}
    a,b,c,d=GLYPHS;im=panel()
    for n,(part,ascent,char,rewind) in enumerate(((im.crop((0,0,224,SPLIT)),53,a,b),(im.crop((0,SPLIT,224,280)),-3,c,d))):
        path=f'font/cosmeticos/gallery_{n}.png'
        files['assets/astral/textures/'+path]=png(part)
        providers.append({'type':'bitmap','file':'astral:'+path,'height':part.height,'ascent':ascent,'chars':[char]})
        advances[rewind]=-(part.getbbox()[2]+1)
    providers.append({'type':'space','advances':advances})
    def model(name,image):
        files[f'assets/astral/textures/item/cosmeticos/{name}.png']=png(image)
        files[f'assets/astral/models/cosmeticos/{name}.json']=json.dumps({'parent':'minecraft:item/generated','gui_light':'front',
            'textures':{'layer0':f'astral:item/cosmeticos/{name}'},'display':{'gui':{'scale':[1.125,1.125,1]}}}).encode()
        files[f'assets/astral/items/cosmeticos/{name}.json']=json.dumps({'oversized_in_gui':True,
            'model':{'type':'minecraft:model','model':f'astral:cosmeticos/{name}'}}).encode()
    for index,(_,name,_) in enumerate(TITLES):
        for locked in (False,True):model(key_for(name)+('_locked' if locked else ''),medal(index,locked))
    for kind in ('info','gacha','back','close'):model('nav_'+kind,nav_icon(kind))
    button=clear_button()
    for i in range(5):model(f'clear_{i}',button.crop((i*18,0,i*18+18,18)))
    for key,slots in HUB_CARDS.items():
        card=hub_card(key)
        for i,slot in enumerate(slots):
            col,row=i%4,i//4
            model(f'hub_{key}_{i}',card.crop((col*18,row*18,col*18+18,row*18+18)))
    # Glifos de la pantalla principal (mismo START/END que la galeria de titulos).
    a2,b2,c2,d2=HUB_GLYPHS;hub=hub_panel()
    for n,(part,ascent,char,rewind) in enumerate(((hub.crop((0,0,224,SPLIT)),53,a2,b2),(hub.crop((0,SPLIT,224,280)),-3,c2,d2))):
        path=f'font/cosmeticos/hub_{n}.png'
        files['assets/astral/textures/'+path]=png(part)
        providers.insert(-1,{'type':'bitmap','file':'astral:'+path,'height':part.height,'ascent':ascent,'chars':[char]})
        advances[rewind]=-(part.getbbox()[2]+1)
    return files,providers


def previews(folder):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    for sample in ('mixta','completa'):
        im=Image.new('RGBA',SIZE,'#1a2531');im.alpha_composite(panel())
        for index,slot in enumerate(TITLE_SLOTS):
            im.alpha_composite(medal(index,sample=='mixta' and index not in (0,1,4,8,11)),(31+slot%9*18,57+slot//9*18))
        im.alpha_composite(clear_button(),(67,147))
        for slot,kind in ((4,'info'),(8,'gacha'),(45,'back'),(53,'close')):
            im.alpha_composite(nav_icon(kind),(31+slot%9*18,57+slot//9*18))
        from menu_ui import icon as menu_icon
        im.alpha_composite(menu_icon('cosmeticos'),(31,57))
        im.alpha_composite(menu_icon('titulos'),(49,57))
        text(im,'Inventario',(86,169),color='#383c40')
        (folder/f'cosmeticos-{sample}.png').write_bytes(png(im.resize((672,840),Image.Resampling.NEAREST)))


if __name__=='__main__':previews(ROOT.parent/'build/Servicios-preview')
