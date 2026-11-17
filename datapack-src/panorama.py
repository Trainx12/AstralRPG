"""Cubemap Astral desde arte equirectangular propio; sin dependencias de servicios."""
import io
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'datapack-src/pack-source/panorama/astral_panorama_equirect.png'
PREFIX = 'assets/minecraft/textures/gui/title/background/'


def direction(face, u, v):
    """Orden vanilla: frente, derecha, atras, izquierda, arriba, abajo.

    U hacia la derecha, V hacia abajo. Cada arista comparte la misma direccion.
    """
    one = np.ones_like(u)
    return ((u, -v, one), (one, -v, -u), (-u, -v, -one),
            (-one, -v, u), (u, one, v), (u, -one, -v))[face]


def face_image(source, face, size=1024):
    # Sobremuestreo 2x y reduccion Lanczos: bordes y cristales sin dientes.
    pixels = np.asarray(source.convert('RGB'), dtype=np.float32)
    h, w = pixels.shape[:2]
    axis = (np.arange(size * 2, dtype=np.float32) + .5) / size - 1
    u, v = np.meshgrid(axis, axis)
    x, y, z = direction(face, u, v)
    longitude = np.arctan2(x, z)
    latitude = np.arctan2(y, np.sqrt(x*x + z*z))
    px = (longitude / (2*np.pi) + .5) * w - .5
    py = np.clip((.5 - latitude / np.pi) * h - .5, 0, h - 1)
    ix, iy = np.floor(px).astype(int), np.floor(py).astype(int)
    fx, fy = (px-ix)[..., None], (py-iy)[..., None]
    a = pixels[iy, ix % w] * (1-fx) + pixels[iy, (ix+1) % w] * fx
    b = pixels[np.minimum(iy+1,h-1), ix % w] * (1-fx) + pixels[np.minimum(iy+1,h-1), (ix+1) % w] * fx
    rgb = a*(1-fy) + b*fy
    # El polo equirectangular no debe convertirse en una estrella estirada.
    pole = np.clip((np.abs(latitude) - np.pi*.475) / (np.pi*.025), 0, 1)[..., None]
    mean = np.where((latitude > 0)[...,None], pixels[:4].mean(axis=(0,1)), pixels[-4:].mean(axis=(0,1)))
    rgb = rgb*(1-pole) + mean*pole
    # El original termina en islas estiradas: cerrar el nadir con nubes azules,
    # usando direcciones 3D para no introducir costuras en las caras laterales.
    south = np.clip((-latitude-np.deg2rad(25))/np.deg2rad(35),0,1)[...,None]
    south = south*south*(3-2*south)
    radius=np.sqrt(x*x+y*y+z*z)
    nx,nz=x/radius,z/radius
    cloud=(np.sin(nx*17+nz*9)+np.sin(nx*8-nz*14)+np.cos(nx*24+nz*21))/3
    clouds=pixels[-20:].mean(axis=(0,1)) + cloud[...,None]*np.array([7,9,14])
    rgb=rgb*(1-south)+clouds*south
    return Image.fromarray(np.uint8(np.clip(rgb,0,255))).resize((size,size), Image.Resampling.LANCZOS)


def assets(size=1024, preview=True):
    with Image.open(SOURCE) as source:
        faces = [face_image(source, n, size) for n in range(6)]
        if preview:
            sheet = Image.new('RGB',(1200,1100),'#0e0b22')
            draw = ImageDraw.Draw(sheet)
            for n, face in enumerate(faces):
                x,y=(n%3)*400,(n//3)*330
                sheet.paste(face.resize((300,300)),(x,y+22))
                draw.text((x+4,y+4),f'{n}: '+['frente','derecha','atras','izquierda','arriba','abajo'][n],fill='white')
            # Cruz continua de las caras (la vista no pretende sustituir un cliente).
            for n,(x,y) in enumerate(((1,1),(2,1),(3,1),(0,1),(1,0),(1,2))):
                sheet.paste(faces[n].resize((140,140)),(320+x*140,670+y*140))
            target = ROOT/'build/previews/panorama_astral.png'
            target.parent.mkdir(parents=True,exist_ok=True);sheet.save(target)
    result = {}
    for n, face in enumerate(faces):
        stream=io.BytesIO();face.save(stream,format='PNG')
        result[PREFIX+f'panorama_{n}.png']=stream.getvalue()
    return result


if __name__ == '__main__':
    print('Caras:', len(assets()))
