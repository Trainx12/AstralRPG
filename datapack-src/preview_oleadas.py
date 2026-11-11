"""Esquema de los estados del panel y barra; no es una captura de Minecraft."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


def main():
    from mobs.mazmorras_data import catalog
    room=next(d for d in catalog() if d['key']=='cumbre')['rooms'][0]
    image=Image.new('RGB',(1200,720),'#16101e'); draw=ImageDraw.Draw(image)
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',19)
    small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',15)
    for i,(phase,left,total) in enumerate(((1,17,17),(1,9,17),(2,15,15),(0,0,0))):
        x=i%2*600;y=i//2*360
        draw.text((x+24,y+16),'Esquema de progreso - '+('Jefe' if phase==0 else f'Oleada {phase}'),font=font,fill='#d6b4ff')
        if phase:
            draw.text((x+55,y+60),f'Oleada {phase}/{len(room["oleadas"])} - {left} restantes',font=font,fill='white')
            draw.rectangle((x+55,y+90,x+545,y+105),fill='#392645',outline='#846397')
            draw.rectangle((x+56,y+91,x+56+int(488*left/total),y+104),fill='#a64bd5')
        else:
            draw.text((x+55,y+72),'Se usa la barra propia del jefe',font=font,fill='#baa5ca')
        lines=('Cumbre Helada',room['name'] if phase else 'Trono del Yeti',
               f'Oleada {phase}/{len(room["oleadas"])}' if phase else 'Jefe',f'Restantes {left}',
               'Sin diarias en esta mazmorra')
        draw.rectangle((x+245,y+135,x+565,y+300),fill='#22182d',outline='#6c507f')
        for n,line in enumerate(lines):draw.text((x+260,y+150+n*27),line,font=small,fill='#f0e6ff')
        draw.text((x+24,y+320),'Al terminar o salir: se oculta la barra de oleada.',font=small,fill='#bca8cc')
    image.save(Path(__file__).resolve().parents[1]/'build/previews/oleadas-tab-barra.png')


if __name__=='__main__':main()
