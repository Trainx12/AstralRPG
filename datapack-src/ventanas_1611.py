"""Ventanas Gemini del 16/11. Arte propio final, casillas reales y vistas desde los YAML."""
import argparse
import io
import json
from pathlib import Path
from PIL import Image, ImageDraw
from services_ui import png, outlined

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT/'datapack-src/pack-source/ref/ventanas-1611'
BUTTONS = ROOT/'datapack-src/pack-source/provisorias'
# Fracciones medidas en los seis originales: abertura, inventario y su borde inferior.
WINDOWS = {
 'configuraciones': ('efectos', 3, 'EFECTOS', (.10,.19,.90,.63,.94)),
 'renacer': ('renacer', 6, 'RENACER', (.12,.19,.88,.60,.94)),
 'deseo': ('deseo', 6, 'UN DESEO', (.12,.26,.88,.63,.94)),
 'deseo_lite': ('deseo_lite', 6, 'DESEO DEL CRONISTA', (.15,.25,.85,.64,.88)),
 'oficios': ('oficios', 4, 'OFICIOS', (.14,.20,.88,.66,.90)),
 'oceano_aviso': ('oceano', 3, 'OCEANO ASTRAL', (.12,.37,.88,.79,.89)),
}
SHEETS = {
 'a': ('efectos_bajo','efectos_medio','efectos_alto','pierdes','conservas','renacer','plata','tier'),
 'b': ('arma','personalizada','otro','reglas','tier_lite','tiradas','cosmetico','minero_info'),
 'c': ('talador_info','minero_set','saldo','entrar','volver','cerrar','info','ayuda'),
}
START, END = '\uf100', '\uf101'
CHARS = {k: tuple(chr(0xf110+i*4+j) for j in range(4)) for i,k in enumerate(WINDOWS)}


def unmagenta(im):
    """Chroma key conectado al fondo: limpia bordes sin borrar violetas interiores."""
    from collections import deque
    im=im.convert('RGBA');px=list(im.getdata());w,h=im.size
    def key(c):
        r,g,b,a=c
        return r>150 and b>150 and g<110 and abs(r-b)<65
    seeds=[i for i,c in enumerate(px) if (c[0]>250 and c[1]<5 and c[2]>250) or
           (key(c) and (i<w or i>=w*(h-1) or i%w in (0,w-1)))]
    seen=set(seeds);queue=deque(seeds)
    while queue:
        i=queue.popleft();x,y=i%w,i//w;px[i]=(0,0,0,0)
        for dx,dy in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,-1),(-1,1),(1,1)):
            nx,ny=x+dx,y+dy
            if 0<=nx<w and 0<=ny<h:
                j=ny*w+nx
                if j not in seen and key(px[j]):seen.add(j);queue.append(j)
    im.putdata(px)
    return im


def import_art():
    """Importacion explicita una sola vez; las compilaciones usan los PNG publicos."""
    source=ROOT/'.local/gemini/imagenes'
    ART.mkdir(parents=True,exist_ok=True);BUTTONS.mkdir(parents=True,exist_ok=True)
    for art,*_ in WINDOWS.values():
        unmagenta(Image.open(source/f'36-{art}-marco.png')).save(ART/f'{art}.png')
    for sheet, keys in SHEETS.items():
        im=Image.open(source/f'36-botones-{sheet}.png')
        # Grilla 4x2; recorte por alpha elimina las calles magenta sin cortar el dibujo.
        for i,key in enumerate(keys):
            x,y=i%4,i//4
            tile=unmagenta(im.crop((round(x*im.width/4),round(y*im.height/2),round((x+1)*im.width/4),round((y+1)*im.height/2))))
            tile=tile.crop(tile.getbbox()).resize((32,32),Image.Resampling.LANCZOS)
            unmagenta(tile).save(BUTTONS/f'boton_{key}.png')
    (BUTTONS/'boton_talador_set.png').write_bytes((BUTTONS/'boton_minero_set.png').read_bytes())
    # Se conserva el item_model. Variantes activas con borde dorado.
    for key in ('efectos_bajo','efectos_medio','efectos_alto'):
        im=Image.open(BUTTONS/f'boton_{key}.png').convert('RGBA')
        ImageDraw.Draw(im).rectangle((0,0,31,31),outline='#ffe480',width=2)
        im.save(BUTTONS/f'boton_{key}_activo.png')


def title(kind):
    return '&f'+START+''.join(CHARS[kind])+END


def apply(kind, data):
    # Configuraciones usa ahora 45 slots y fondo generico sin cambiar el pack.
    if kind == 'configuraciones' or kind not in WINDOWS:return data
    data['menu_title']=title(kind)
    data['size']=WINDOWS[kind][1]*9
    items=data['items']
    for key in list(items):
        if key.startswith('vidrio_'):del items[key]
    if kind=='renacer':
        for key in list(items):
            if key.startswith('confirmar_') and key!='confirmar_0':del items[key]
        items['confirmar_0'].update(slot=40,material='PAPER',item_model='astral:boton_renacer')
        items['pierdes']['slot']=11;items['conservas']['slot']=15
    if kind in ('deseo','deseo_lite'):
        cats=('plata','tier','arma','personalizada','otro') if kind=='deseo' else ('plata','tier','tiradas','arma','cosmetico')
        for key,slot in zip(cats,(18,20,22,24,26)):
            items[key]['slot']=slot
        items['reglas']['slot']=42
    for key,item in items.items():
        alias={'confirmar_0':'renacer','volver':'volver','cerrar':'cerrar','titulo':'info'}.get(key,key)
        if kind=='deseo_lite' and key=='tier':alias='tier_lite'
        if (BUTTONS/f'boton_{alias}.png').exists():item['item_model']='astral:boton_'+alias
    return data


def panel(kind):
    art,rows,caption,(left,top,right,inv,bottom)=WINDOWS[kind]
    source=Image.open(ART/f'{art}.png').convert('RGBA')
    sx=[0,round(left*source.width),round(right*source.width),source.width]
    sy=[0,round(top*source.height),round(inv*source.height),round(bottom*source.height),source.height]
    end=57+rows*18
    dx=[0,24,200,224];dy=[0,57,end+14,end+90,end+115]
    im=Image.new('RGBA',(224,dy[-1]))
    for y in range(4):
        for x in range(3):
            tile=source.crop((sx[x],sy[y],sx[x+1],sy[y+1]))
            im.alpha_composite(tile.resize((dx[x+1]-dx[x],dy[y+1]-dy[y]),Image.Resampling.LANCZOS),(dx[x],dy[y]))
    outlined(im,caption,(112,17 if kind=='deseo_lite' else 25),color='#f5df9b')
    d=ImageDraw.Draw(im)
    # Rejilla del jugador en su posicion vanilla, independiente del hueco original.
    for row in (*range(3),4):
        for col in range(9):
            x=31+18*col;y=end+14+(18*row if row<3 else 58)
            d.rectangle((x-1,y-1,x+16,y+16),outline='#776b75')
            d.rectangle((x,y,x+15,y+15),fill=(0,0,0,0))
    labels={
      'configuraciones':((11,'BAJO'),(13,'MEDIO'),(15,'ALTO')),
      'deseo':tuple(zip((18,20,22,24,26),('PLATA','TIER','EQUIPO','ARMA','OTRO'))),
      'deseo_lite':tuple(zip((18,20,22,24,26),('PLATA','2 PZS','TIRADAS','EQUIPO','COSM.'))),
      'renacer':((11,'PERDES'),(15,'CONSERVAS'),(40,'RENACER')),
      'oceano_aviso':((11,'ENTRAR'),(15,'VOLVER')),
    }
    from adventure_ui import label
    for slot,caption in labels.get(kind,()):
        x,y=31+18*(slot%9),57+18*(slot//9)
        d.rectangle((x-1,y-1,x+17,y+17),outline='#c9a14f')
        label(im,caption,(x+9,y+19),28,'#30251b' if kind=='deseo_lite' else '#f3e4b8')
    return im


def assets():
    files={};providers=[];advances={START:-32,END:32}
    for kind in WINDOWS:
        im=panel(kind);chars=CHARS[kind]
        for n,(part,ascent) in enumerate(((im.crop((0,0,224,56)),53),(im.crop((0,56,224,im.height)),-3))):
            path=f'font/ventanas1611/{kind}_{n}.png'
            files['assets/astral/textures/'+path]=png(part)
            providers.append(dict(type='bitmap',file='astral:'+path,height=part.height,ascent=ascent,chars=[chars[n*2]]))
            advances[chars[n*2+1]]=-(part.getbbox()[2]+1)
    providers.append(dict(type='space',advances=advances))
    return files,providers


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--import-art',action='store_true');args=p.parse_args()
    if args.import_art:import_art()
