# -*- coding: utf-8 -*-
"""
Iconos de inventario de las armaduras armados con la misma textura que se ve puesta:
casco = frente de la cabeza, pechera = torso y brazos, pantalones = cintura y piernas,
botas = parte de abajo de las piernas. Se le agrega un borde oscuro para que se lea bien.
"""
import os

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
EQ = os.path.join(HERE, "pack-source", "assets", "astral", "textures", "entity", "equipment")
OUT = os.path.join(HERE, "pack-source", "assets", "astral", "textures", "item", "gen")
# Sets que ya tienen textura propia copiada de una skin (agregar aca cuando haya mas)
SETS = ["mago", "berserker", "arquero"]


def outline(img):
    """Borde oscuro de 1 pixel alrededor de lo que no es transparente."""
    w, h = img.size
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    px = img.load()
    for y in range(h):
        for x in range(w):
            if px[x, y][3] > 0:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and px[nx, ny][3] > 0:
                    out.putpixel((x, y), (20, 18, 24, 255))
                    break
    out.alpha_composite(img)
    return out


def flip(i):
    return i.transpose(Image.FLIP_LEFT_RIGHT)


def icons(main, legs):
    res = {}
    # Casco: frente de la cabeza (8x8) agrandado x2 menos un borde -> 14x14 centrado
    head = main.crop((8, 8, 16, 16))
    hi = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    hi.paste(head.resize((14, 14), Image.NEAREST), (1, 1))
    res["helmet"] = hi
    # Pechera: brazo + torso + brazo (4+8+4 = 16) con 12 de alto, centrado
    body = main.crop((20, 20, 28, 32))
    arm = main.crop((44, 20, 48, 32))
    ci = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    ci.paste(arm, (0, 2))
    ci.paste(body, (4, 2))
    ci.paste(flip(arm), (12, 2))
    # los brazos un poco mas cortos para que se lea como pechera
    for x in list(range(0, 4)) + list(range(12, 16)):
        for y in range(11, 14):
            ci.putpixel((x, y), (0, 0, 0, 0))
    res["chestplate"] = ci
    # Pantalones: cintura (4 filas) + dos piernas (12 filas), 8 de ancho, centrado
    waist = legs.crop((20, 28, 28, 32))
    leg = legs.crop((4, 20, 8, 32))
    li = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    li.paste(waist, (4, 0))
    li.paste(leg, (4, 4))
    li.paste(flip(leg), (8, 4))
    # separacion entre piernas
    for y in range(9, 16):
        for x in (7, 8):
            li.putpixel((x, y), (0, 0, 0, 0))
    res["leggings"] = li
    # Botas: parte de abajo de cada pierna (4x4) agrandada x2, separadas
    boot = main.crop((4, 28, 8, 32)).resize((6, 6), Image.NEAREST)
    bi = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    bi.paste(boot, (1, 7))
    bi.paste(flip(boot), (9, 7))
    res["boots"] = bi
    return {k: outline(v) for k, v in res.items()}


def main():
    n = 0
    for s in SETS:
        for t in range(1, 6):
            mp = os.path.join(EQ, "humanoid", f"{s}_{t}.png")
            lp = os.path.join(EQ, "humanoid_leggings", f"{s}_{t}.png")
            if not (os.path.exists(mp) and os.path.exists(lp)):
                continue
            main_img = Image.open(mp).convert("RGBA")
            legs_img = Image.open(lp).convert("RGBA")
            for piece, img in icons(main_img, legs_img).items():
                img.save(os.path.join(OUT, f"{s}_{t}_{piece}.png"))
                n += 1
    print(n, "iconos de armadura generados desde la textura puesta")


if __name__ == "__main__":
    main()
