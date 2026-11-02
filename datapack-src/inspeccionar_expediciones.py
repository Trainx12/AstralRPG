"""Inspeccion de los mapas de expediciones; nunca modifica los originales."""
import gzip
import pickle
from pathlib import Path
from PIL import Image, ImageDraw
from mapas import block, color

BASE=Path(__file__).resolve().parent.parent/'.local/mapas/astral-nuevos'
LEGACY={0:'air',1:'stone',2:'grass_block',3:'dirt',4:'cobblestone',5:'oak_planks',7:'bedrock',
        8:'water',9:'water',10:'lava',11:'lava',12:'sand',17:'oak_log',18:'oak_leaves',
        20:'glass',24:'sandstone',31:'short_grass',35:'white_wool',38:'poppy',43:'smooth_stone',
        44:'stone_slab',95:'white_stained_glass',98:'stone_bricks',126:'oak_slab',
        137:'command_block',159:'terracotta',169:'sea_lantern',172:'terracotta',252:'concrete_powder'}

def get(chunks,x,y,z):
    c=chunks.get((x//16,z//16),{})
    for s in c.get('Sections',[]):
        if s['Y']==y//16 and 'Blocks' in s:
            i=(y%16)*256+(z%16)*16+x%16
            ident=s['Blocks'][i]
            if 'Add' in s:ident+=((s['Add'][i//2]>>(4*(i%2)))&15)*256
            metadata=(s.get('Data',bytes(2048))[i//2]>>(4*(i%2)))&15
            if ident==5 and metadata<6:
                return 'minecraft:'+('oak','spruce','birch','jungle','acacia','dark_oak')[metadata]+'_planks'
            if ident==24 and metadata<3:
                return 'minecraft:'+('sandstone','chiseled_sandstone','cut_sandstone')[metadata]
            return 'minecraft:'+LEGACY.get(ident,'legacy_'+str(ident))
    return block(c,x%16,y,z%16)

def load(key):
    with gzip.open(BASE/(key+'-inspeccion.pkl.gz'),'rb') as f:return pickle.load(f)

def render(key,bounds,ymax=255):
    chunks=load(key);x0,z0,x1,z1=bounds
    step=2
    im=Image.new('RGB',((x1-x0)//step+1,(z1-z0)//step+1),(20,24,32))
    for z in range(z0,z1+1,step):
        for x in range(x0,x1+1,step):
            c=chunks.get((x//16,z//16),{})
            for s in sorted(c.get('sections',c.get('Sections',[])),key=lambda s:s['Y'],reverse=True):
                if s['Y']*16>ymax:continue
                for y in range(min(ymax,s['Y']*16+15),s['Y']*16-1,-1):
                    name=get(chunks,x,y,z)
                    if name not in ('minecraft:air','minecraft:cave_air','minecraft:void_air','minecraft:barrier'):
                        im.putpixel(((x-x0)//step,(z-z0)//step),color(name,y));break
                else:continue
                break
    im=im.resize((800,800),Image.Resampling.NEAREST);d=ImageDraw.Draw(im)
    for x in range(x0,x1+1,32):
        px=(x-x0)*800/(x1-x0+1);d.line((px,0,px,800),fill='#777777');d.text((px+2,3),str(x),fill='white')
    for z in range(z0,z1+1,32):
        pz=(z-z0)*800/(z1-z0+1);d.line((0,pz,800,pz),fill='#777777');d.text((3,pz+12),str(z),fill='white')
    path=BASE/(key+'-superficie.png');im.save(path);print(path,flush=True)

if __name__=='__main__':
    render('hielo',(-256,-256,287,287),120)
    render('desierto',(0,0,319,319))
    render('santuario_exploracion',(-64,-128,63,63))
