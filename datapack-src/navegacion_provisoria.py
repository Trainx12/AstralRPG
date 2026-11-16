"""Reservas con trama y marca P; PNG reemplazables por el dueno."""
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent/'pack-source/provisorias/navegacion'

def icon(family,kind):
    ROOT.mkdir(parents=True,exist_ok=True);path=ROOT/f'{family}_nav_{kind}.png'
    if path.exists():return Image.open(path).convert('RGBA')
    im=Image.new('RGBA',(18,18),'#26344c');d=ImageDraw.Draw(im)
    for x in range(-16,18,4):d.line((x,1,x+16,16),fill='#394968')
    d.rectangle((0,0,17,17),outline='#e5ba66')
    if kind=='gacha':
        d.rectangle((3,5,14,13),fill='#87582e',outline='#ffe299');d.rectangle((3,5,14,8),fill='#c98b3e');d.rectangle((8,7,10,10),fill='#70ffef')
        d.line((12,2,12,4),fill='#fff4b5');d.line((11,3,13,3),fill='#fff4b5')
    elif kind in ('back','next'):
        d.polygon(((3,9),(9,4),(9,7),(14,7),(14,11),(9,11),(9,14)),fill='#ffdd7c')
        if kind=='next':im=im.transpose(Image.Transpose.FLIP_LEFT_RIGHT);d=ImageDraw.Draw(im)
    elif kind=='info':
        d.ellipse((4,3,13,13),fill='#62dce3');d.line((9,7,9,11),fill='#20324a',width=2);d.point((9,5),fill='#20324a')
    else:
        d.line((5,5,12,12),fill='#ff9e9e',width=3);d.line((12,5,5,12),fill='#ff9e9e',width=3)
    d.rectangle((0,12,4,17),fill='#683f78');d.line((1,16,1,13,3,13,3,14,1,14),fill='#ffbaff')
    im.save(path);return im

def rest(rebuild=False):
    ROOT.mkdir(parents=True,exist_ok=True)
    paths=[ROOT/f'mascotas_rest_{i}.png' for i in range(5)]
    if rebuild or not all(p.exists() for p in paths):
        image=Image.new('RGBA',(90,18),'#294438');d=ImageDraw.Draw(image)
        for x in range(-16,90,4):d.line((x,0,x+17,17),fill='#345544')
        d.rectangle((0,0,89,17),outline='#e5ba66')
        from escape_menu import text
        text(image,'DESCANSAR',(45,5),color='#eee3be');d.text((1,3),'P',fill='#ffbaff')
        for i,path in enumerate(paths):image.crop((i*18,0,i*18+18,18)).save(path)
    image=Image.new('RGBA',(90,18))
    for i,path in enumerate(paths):image.alpha_composite(Image.open(path).convert('RGBA'),(18*i,0))
    return image
