"""Vista previa ilustrativa generada desde los JSON (no captura del cliente)."""
import json
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parent.parent
COLORS={'gray':'#aaaaaa','white':'#ffffff','green':'#55ff55','gold':'#ffaa00',
        'yellow':'#ffff55','red':'#ff5555','aqua':'#55ffff','dark_gray':'#555555',
        'light_purple':'#ff55ff','dark_purple':'#aa00aa','blue':'#5555ff'}

def generate():
    image=Image.new('RGB',(1650,740),'#181423');draw=ImageDraw.Draw(image)
    font=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',17)
    titlefont=ImageFont.truetype('C:/Windows/Fonts/consolab.ttf',18)
    draw.text((24,18),'ASTRALRPG · Fichas generadas · Vista previa ilustrativa',font=titlefont,fill='#d6b4ff')
    for column,(iid,level) in enumerate((('espada_1',0),('espada_5',7),('espada_destello',0))):
        mods=json.loads((ROOT/f'build/AstralRPG-Items/data/astral/item_modifier/ficha/{iid}/{level}.json').read_text(encoding='utf-8'))
        x=24+column*545;y=80
        draw.rounded_rectangle((x-8,y-12,x+520,690),radius=8,fill='#100510',outline='#5000a0',width=3)
        def write(component,x,y):
            value=component.get('text','');color=component.get('color','gray')
            if value=='✪':
                points=[(x+9+8*math.cos(-math.pi/2+i*math.pi/5)*(1 if i%2==0 else .44),
                         y+10+8*math.sin(-math.pi/2+i*math.pi/5)*(1 if i%2==0 else .44)) for i in range(10)]
                draw.polygon(points,fill=COLORS[color])
                return x+19
            draw.text((x,y),value,font=font,fill=COLORS.get(color,color))
            x+=draw.textlength(value,font=font)
            for child in component.get('extra',[]):x=write(child,x,y)
            return x
        for line in [mods[0]['name'],{'text':''}]+mods[1]['lore']:
            write(line,x,y);y+=27
    path=ROOT/'build/previews/fichas-armas.png';path.parent.mkdir(parents=True,exist_ok=True)
    image.save(path)
    return path

if __name__=='__main__':print(generate())
