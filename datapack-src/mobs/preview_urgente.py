"""Vistas CPU propias; no son capturas de Minecraft."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageOps
from mobs import build_models
from mobs.muerte import ensure
from mobs.preview_arreglos import posed

ROOT=Path(__file__).resolve().parents[2]


def main():
    out=ROOT/'build/previews';out.mkdir(exist_ok=True)
    for fn in build_models.creatures.ALL:
        m=ensure(fn())
        if 'death' not in m.anims:continue
        sheet=Image.new('RGB',(1000,300),'#18232b');draw=ImageDraw.Draw(sheet)
        for i,t in enumerate((0,.2,.4,.6,.79)):
            pose=posed(m,'death',t);texture=pose.export()[1]
            im=build_models.preview3d(pose,texture,yaw=0,pitch=0,scale=4)
            im=ImageOps.contain(im,(195,250))
            sheet.paste(im,(i*200+(200-im.width)//2,280-im.height),im)
            draw.text((i*200+5,8),f'CPU death {t}s',fill='white')
        sheet.save(out/('muerte-'+m.name.removeprefix('astral_')+'.png'))
    m=build_models.creatures.yeti();tex=m.export()[1]
    base=build_models.preview3d(m,tex,yaw=0,pitch=0,scale=1)
    canvas=Image.new('RGB',(900,550),'#18232b');draw=ImageDraw.Draw(canvas)
    unit=30;ground=500
    for x,factor,title in ((70,2,'Yeti Ancestral'),(380,4,'Yeti Cumbre = 2 Ancestrales')):
        im=base.resize((round(base.width*factor*unit/16),round(base.height*factor*unit/16)),Image.Resampling.NEAREST)
        canvas.paste(im,(x,ground-im.height),im);draw.text((x,515),title,fill='white')
    draw.rectangle((820,ground-1.8*unit,838,ground),fill='#b6ddf5');draw.text((785,515),'Jugador 1,8 b',fill='white')
    draw.line((0,ground,900,ground),fill='#a8acb5');draw.text((10,8),'Comparacion CPU a escala comun (30 px/bloque)',fill='white')
    canvas.save(out/'yeti-tamano.png')


if __name__=='__main__':main()
