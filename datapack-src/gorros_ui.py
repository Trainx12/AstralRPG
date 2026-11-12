"""Vitrina de gorros con el marco ilustrado propio y grilla de 20 piezas."""
import json
from PIL import ImageDraw
from cosmeticos_ui import panel as gallery, FILL, EDGE
from services_ui import png, SPLIT, outlined

START, END = '\ued00', '\ued01'
GLYPHS = tuple(chr(0xed10+i) for i in range(4))


def title():
    return '&f'+START+''.join(GLYPHS)+END


def panel():
    im=gallery('GORROS Y SOMBREROS'); d=ImageDraw.Draw(im)
    d.rectangle((24,56,199,165),fill=FILL)
    for slot in (*range(9,29),45,49,53):
        x,y=31+slot%9*18,57+slot//9*18
        d.rectangle((x,y,x+17,y+17),fill='#102331',outline=EDGE)
        d.rectangle((x+1,y+1,x+16,y+16),fill=(0,0,0,0))
    return im


def assets():
    im=panel(); files={}; providers=[]; advances={START:-32,END:32}
    for i,(box,ascent) in enumerate((((0,0,224,SPLIT),53),((0,SPLIT,224,280),-3))):
        part=im.crop(box); path=f'font/cosmeticos/gorros_{i}.png'
        files['assets/astral/textures/'+path]=png(part)
        providers.append(dict(type='bitmap',file='astral:'+path,height=part.height,ascent=ascent,chars=[GLYPHS[i*2]]))
        advances[GLYPHS[i*2+1]]=-(part.getbbox()[2]+1)
    providers.append(dict(type='space',advances=advances))
    return files,providers
