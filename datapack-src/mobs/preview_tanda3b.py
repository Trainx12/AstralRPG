"""Referencias solo locales; exporta una lamina publica con escala compartida."""
from pathlib import Path
from PIL import Image
from bbmodel import save
from build_models import preview3d
from preview_tanda3a import player, text, BG
from creatures_tanda3b import ALL

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'build/previews'


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    source=Image.open(ROOT/'.local/coordination/ref/esqueletos-variantes-referencia.png').convert('RGBA')
    crops=((20,32,225,385),(205,72,390,350),(375,30,555,363),(518,112,671,350),(645,33,828,374))
    figures=[]
    for i,fn in enumerate(ALL):
        m=fn(); tex=save(m,ROOT/'build/models'/f'{m.name}.bbmodel')
        ref=source.crop(crops[i]) if i<5 else Image.open(ROOT/'.local/coordination/ref/creeper-nuclear-referencia.png').convert('RGBA')
        ref.thumbnail((350,410))
        angles=((0,0),(90,0),(35,12),(-24,15),(180,0))
        views=[preview3d(m,tex,yaw,pitch,10,background=BG,translucent=False) for yaw,pitch in angles]
        image=Image.new('RGBA',(365+sum(v.width+20 for v in views),480),BG)
        text(image,(8,10),'Referencia (solo local)',16); image.paste(ref,(8,55),ref)
        x=365
        for title,v in zip(('Frente','Costado','3/4','Angulo foto','Espalda'),views):
            text(image,(x,10),title,16); image.paste(v,(x,55),v); x+=v.width+20
        image.save(OUT/f'{m.name}-comparacion.png')
        v=preview3d(m,tex,0,0,5,background=BG,translucent=False); figures.append((v,m.name.replace('astral_','')))
    p=player(); figures.insert(0,(preview3d(p,p.export()[1],0,0,5,background=BG),'Jugador 1,8 bloques'))
    sheet=Image.new('RGBA',(sum(max(180,v.width)+15 for v,_ in figures),250),BG)
    x=8
    for v,label in figures:
        cell=max(180,v.width); sheet.paste(v,(x+(cell-v.width)//2,195-v.height)); text(sheet,(x,210),label,14); x+=cell+15
    sheet.save(OUT/'tanda3b.png')


if __name__=='__main__': main()
