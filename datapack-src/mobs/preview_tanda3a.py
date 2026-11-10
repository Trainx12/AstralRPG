"""Comparaciones locales con referencias privadas y lamina publica de modelos propios."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import creatures
from build_models import preview3d
from bbmodel import Model
from creatures_tanda3a import coloso, planta

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'build/previews'
BG=(26,32,39,255)


def text(im,xy,value,size=18):
    ImageDraw.Draw(im).text(xy,value,font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',size),fill='white')


def player():
    m=Model('jugador_1_8_bloques'); m.bone('body',(0,0,0))
    for a,b,c in (((-4,21,-4),(4,28.8,4),'#C99C77'),((-4,9,-2),(4,21,2),'#449AA8'),
                  ((-7,9,-2),(-4,21,2),'#C99C77'),((4,9,-2),(7,21,2),'#C99C77'),
                  ((-4,0,-2),(-.3,9,2),'#506B9B'),((.3,0,-2),(4,9,2),'#506B9B')):
        m.cube('body',a,b,c)
    return m


def comparison(model,reference,name):
    data,tex=model.export()
    renders=[preview3d(model,tex,yaw,12,8,background=BG) for yaw in (0,90,35)]
    ref=Image.open(reference).convert('RGBA'); ref.thumbnail((400,600))
    h=max(650,max(im.height for im in renders)+80)
    im=Image.new('RGBA',(430+sum(v.width+15 for v in renders),h),BG)
    im.paste(ref,((420-ref.width)//2,50),ref)
    text(im,(12,12),'Referencia de tercero (solo revision local)',16)
    x=430
    for label,v in zip(('Frente propio','Costado propio','Tres cuartos propio'),renders):
        text(im,(x,15),label,16); im.paste(v,(x,65),v); x+=v.width+15
    im.save(OUT/f'{name}-comparacion.png')


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    for fn,ref,name in ((coloso,'jefe-mina-referencia.webp','coloso-musgoso'),
                         (planta,'planta-carnivora-referencia.png','planta-carnivora')):
        comparison(fn(),ROOT/'.local/coordination/ref'/ref,name)
    models=[(coloso(),2,'Coloso Musgoso'),(planta(),1,'Planta carnivora')]
    for name in ('cangrejo','chaman','momia','yeti','golem_forja'):
        m=getattr(creatures,name)(); models.append((m,2,'Estatua '+name))
        tex=m.export()[1]; a=preview3d(m,tex,0,12,4); b=preview3d(m,tex,35,12,4)
        im=Image.new('RGBA',(a.width+b.width+40,max(a.height,b.height)+70),BG)
        text(im,(10,8),'Jefe original propio / estatua (mismo modelo)',15)
        im.paste(a,(10,55)); im.paste(b,(a.width+25,55)); im.save(OUT/f'estatua-{name}-comparacion.png')
    # Escala comun 32px/bloque: scale del raster = s * 32 / 16.
    figures=[]
    for m,s,label in [(player(),1,'Jugador 1,8 b')]+models:
        raster=preview3d(m,m.export()[1],0,0,2*s,background=BG)
        figures.append((raster,label))
    width=sum(max(im.width,165)+16 for im,_ in figures)
    height=max(im.height for im,_ in figures)+115
    sheet=Image.new('RGBA',(width,height),BG); text(sheet,(15,10),'Tanda 3a - frente, escala comun: 32 px = 1 bloque',22)
    x=8; baseline=height-55
    ImageDraw.Draw(sheet).line((5,baseline,width-5,baseline),fill='#81919A',width=2)
    for im,label in figures:
        cell=max(im.width,165); sheet.paste(im,(x+(cell-im.width)//2,baseline-im.height+4))
        text(sheet,(x,baseline+12),label,15); x+=cell+16
    sheet.save(OUT/'tanda3a.png')


if __name__=='__main__': main()
