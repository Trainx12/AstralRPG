"""Arte final propio: importacion explicita; compilar solo lee fuentes versionadas."""
import argparse
import json
from pathlib import Path
from PIL import Image, ImageDraw
from ventanas_1611 import unmagenta

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT/'datapack-src/pack-source'
ART = PACK/'ref/arte-1611'
ITEMS = ('frasco_xp_pequeno', 'frasco_xp_grande', 'frasco_xp_gigante', 'barril_xp',
         'manzana_esmeralda', 'fragmento_ocaso', 'esquirla_eclipse', 'nucleo_supernova',
         'esencia_vacio', 'corazon_fin', 'saltador')
BUTTONS = ('configuraciones', 'tema', 'infinita', 'oceano', 'garantia', 'probabilidades', 'premio', 'proximamente')


def tile(sheet, index, size):
    """Recorta el cuadro central de la celda, sin calles magenta ni deformacion."""
    x, y = index % 4, index // 4
    im = unmagenta(sheet.crop((round(x*sheet.width/4), round(y*sheet.height/2),
                              round((x+1)*sheet.width/4), round((y+1)*sheet.height/2))))
    im = im.crop(im.getbbox())
    side = min(im.size); left = (im.width-side)//2; top = (im.height-side)//2
    return unmagenta(im.crop((left, top, left+side, top+side)).resize((size,size), Image.Resampling.LANCZOS))


def import_art():
    source = ROOT/'.local/gemini/imagenes'
    ART.mkdir(parents=True, exist_ok=True)
    for iid in ITEMS:
        folder = '37-items' if iid in ITEMS[:5] else '38-items'
        name = 'gancho' if iid == 'saltador' else iid
        (ART/f'{iid}.png').write_bytes((source/folder/f'{name}.png').read_bytes())
    (ART/'experience_bottle.png').write_bytes((source/'37-items/experience_bottle.png').read_bytes())
    sheet = Image.open(source/'38-botones-d.png')
    for i,key in enumerate(BUTTONS):tile(sheet,i,32).save(PACK/f'provisorias/boton_{key}.png')
    sheet = Image.open(source/'38-botones-e.png')
    nav = PACK/'provisorias/navegacion'
    tile(sheet,6,18).save(nav/'mascotas_nav_next.png')
    for family in ('mascotas','cosmeticos'):
        tile(sheet,7,18).save(nav/f'{family}_nav_gacha.png')
        for key,original in (('back','volver'),('close','cerrar'),('info','ayuda')):
            Image.open(PACK/f'provisorias/boton_{original}.png').resize((18,18),Image.Resampling.LANCZOS).save(nav/f'{family}_nav_{key}.png')


def assets():
    files = {}
    for iid in ITEMS:
        files[f'assets/astral/textures/item/arte1611/{iid}.png'] = (ART/f'{iid}.png').read_bytes()
        files[f'assets/astral/models/arte1611/{iid}.json'] = json.dumps({
            'parent':'minecraft:item/generated', 'textures':{'layer0':f'astral:item/arte1611/{iid}'}}).encode()
        files[f'assets/astral/items/{iid}.json'] = json.dumps({'model':{
            'type':'minecraft:model','model':f'astral:arte1611/{iid}'}}).encode()
    files['assets/minecraft/textures/item/experience_bottle.png'] = (ART/'experience_bottle.png').read_bytes()
    return files


def preview():
    paths = [(iid,ART/f'{iid}.png') for iid in (*ITEMS,'experience_bottle')]
    paths += [('boton_'+key,PACK/f'provisorias/boton_{key}.png') for key in BUTTONS]
    paths += [(p.stem,p) for p in sorted((PACK/'provisorias/navegacion').glob('*nav*.png')) if p.stem!='cosmeticos_nav_next']
    out = Image.new('RGB',(1000,((len(paths)+4)//5)*144),'#252832');d=ImageDraw.Draw(out)
    for i,(name,path) in enumerate(paths):
        x,y=i%5*200,i//5*144
        im=Image.open(path).convert('RGBA');im.thumbnail((88,88),Image.Resampling.NEAREST)
        im=im.resize((88,88),Image.Resampling.NEAREST)
        out.paste(im,(x+56,y+8),im);d.text((x+5,y+104),name,fill='white')
    out.save(ROOT/'build/Servicios-preview/arte-16-11.png')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--import-art',action='store_true');args=p.parse_args()
    if args.import_art:import_art()
    preview()
