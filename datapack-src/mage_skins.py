# -*- coding: utf-8 -*-
"""
Texturas de las armaduras de Mago (niveles 1 a 5) copiadas de las skins de referencia.
Cada letra es un color de la paleta; '.' es transparente.
La armadura usa el formato de 64x32 de Minecraft (cabeza, cuerpo, brazos y piernas).
El nivel 3 se copia directo de la imagen plana de referencia (ref/mago3.png).
"""
import os

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "pack-source", "assets", "astral", "textures", "entity", "equipment")
REF3 = os.path.join(HERE, "pack-source", "ref", "mago3.png")

SKINS = {
    1: {  # pelo blanco, cuello dorado, tunica negra con lineas doradas
        "pal": {"W": (232, 232, 238), "w": (200, 200, 210), "B": (70, 50, 40), "T": (90, 175, 175), "G": (110, 195, 110),
                "Y": (220, 170, 50), "y": (170, 120, 30), "K": (22, 25, 36), "k": (40, 45, 62), "N": (95, 70, 50),
                "n": (150, 120, 80)},
        "head_front": ["WwBTTWNW", "WBTTWWBG", "WNBWWWNW", "WW....wW", "W......W", "W......W", "w......w", "........"],
        "head_side": ["WWwWWBWW", "WWWNWWWW", "WwWWWWwW", "WWWWWWWW", "wWWWWWWw", "WWWWWWWW", "wWWwWWWW", "WWWWWWWW"],
        "head_back": ["WWBWWWWW", "WWWWNWWW", "WwWWWWBW", "WWWWWWWW", "WBWWWwWW", "WWWWWWWW", "wWWWWWWw", "WWwWWWWW"],
        "head_top": ["WWTTWWGW", "WTTWWWWG", "WWWWBWWW", "WWWWWWWW", "WBWWWWWW", "WWWWWNWW", "WWWWWWWW", "WWwWWWWW"],
        "body_front": ["YYyYYyYY", "yYYYYYYy", "KkyYYykK", "KKKYYKKK", "KkKYYKkK", "KKnYYnKK", "KKKyYKKK", "KkKYYKkK",
                       "KKKYyKKK", "NNNYYNNN", "KKKYYKKK", "KKYKKYKK"],
        "body_back": ["YYYYYYYY", "yYYYYYYy", "KKKKKKKK", "KkKKKKkK", "KKKNNKKK", "KKKKKKKK", "KkKKKKkK", "KKKKKKKK",
                      "KKyKKyKK", "NNNNNNNN", "KKKKKKKK", "KYKKKKYK"],
        "body_side": ["YYYY", "yYYy", "KKKK", "KkKK", "KKKK", "KKkK", "KKKK", "KkKK", "KKKK", "NNNN", "KKKK", "KKYK"],
        "arm": ["KkKK", "NnNK", "KKKK", "KkKK", "NNnK", "KKKK", "KKKk", "KkKK", "KKKK", "YYyY", "YyYY", "kKKK"],
        "leg": ["KKKY", "KkKY", "KKKY", "KKYK", "KkKY", "KKKY", "KKYK", "KKKY", "yYKK", "NNNN", "NnNN", "BBBB"],
    },
    2: {  # capucha verde azulada, cara oscura, gema verde
        "pal": {"H": (80, 140, 120), "h": (115, 175, 150), "d": (45, 85, 75), "C": (225, 215, 160), "c": (190, 180, 130),
                "V": (22, 22, 28), "E": (95, 225, 80), "e": (60, 160, 60), "T": (60, 185, 170), "P": (38, 28, 70),
                "p": (60, 45, 100)},
        "head_front": ["HHhHHhHH", "HhHHHHhH", "HCCCCCCH", "HCVVVVCH", "CVVVVVVC", "CVVVVVVC", "CVVVVVVC", "cVVVVVVc"],
        "head_side": ["HHhHHHhH", "HhHHHHHH", "HHHHhHHH", "dHHHHHhH", "HHhHHHHd", "HHHHHHHH", "dHHHhHHH", "HHHHHHHd"],
        "head_back": ["HHhHHhHH", "HhHHHHhH", "HHHHHHHH", "HHhHHHHH", "HHHHHhHH", "HhHHHHHH", "HHHHHHhH", "dHHHHHHd"],
        "head_top": ["HHhHHhHH", "HhHHHHhH", "HHHVVHHH", "HHHHHHHH", "HhHHHHHH", "HHHHHhHH", "HHHHHHHH", "HhHHHHhH"],
        "body_front": ["CdVVVVdC", "CddVVddC", "dddEEddd", "HddEeddH", "dHddddHd", "CdHddHdC", "dCddddCd", "HHHTTHHH",
                       "CHHHHHHC", "dHhHHhHd", "HdHHHHdH", "dHHCCHHd"],
        "body_back": ["HHHHHHHH", "HhHHHHhH", "HHHHHHHH", "dHHhHHHd", "HHHHHHHH", "HhHHHHhH", "HHHHHHHH", "CCCCCCCC",
                      "HHHHHHHH", "HhHHHhHH", "HHHHHHHH", "dHHHHHHd"],
        "body_side": ["HHHH", "HhHH", "HHHH", "CHHC", "HHHH", "HhHH", "HHHH", "CCCC", "HHHH", "HHhH", "HHHH", "dHHd"],
        "arm": ["hHHh", "HHhH", "HHHH", "CHHC", "HhHH", "HHHH", "CCCc", "dHHd", "HddH", "CdCd", "dddd", "CCCC"],
        "leg": ["dHHd", "HHhH", "HdHH", "HHHC", "dHHd", "HCHH", "PdHH", "PPdC", "PPPP", "CCCC", "PPpP", "CCCC"],
    },
    4: {  # capucha negra, ojos rojos, banda roja cruzada
        "pal": {"K": (20, 18, 22), "k": (36, 34, 42), "g": (70, 70, 82), "G": (105, 105, 115), "R": (232, 30, 30),
                "r": (150, 15, 20), "O": (240, 140, 40)},
        "head_front": ["KkKKKKkK", "KKkKKKKK", "gKKKKKKg", "gKKKKKKg", "gRrKKrRg", "gKKKKKKg", "kKKKKKKk", "KKKKKKKK"],
        "head_side": ["KKKkKKKK", "KkKKKKKK", "KKKKKkKK", "KKgKKKKK", "KKKKKKgK", "KkKKKKKK", "KKKKKKKK", "KKKKkKKK"],
        "head_back": ["KKKKKKKK", "KkKKKKkK", "KKKKKKKK", "KKKgKKKK", "KKKKKKKK", "KkKKKKKK", "KKKKKkKK", "KKKKKKKK"],
        "head_top": ["KKkKKKKK", "KKKKKkKK", "KkKKKKKK", "KKKKKKKK", "KKKKKkKK", "KKkKKKKK", "KKKKKKKK", "KkKKKKkK"],
        "body_front": ["KgKKKKgK", "KRKKKKKK", "KKRKKKKK", "KKRRKKKK", "KKKRRKKK", "KKKKRKKK", "KKKKrRKK", "KKKKKrKK",
                       "KKKKKKKK", "kRKKKKRk", "KKKKKKKK", "KRKKKKRK"],
        "body_back": ["KKKKKKKK", "KgKKKKgK", "KKKKKKKK", "KKKRRKKK", "KKKKKKKK", "KkKKKKkK", "KKKKKKKK", "KKKKKKKK",
                      "KKKRRKKK", "KKKKKKKK", "KkKKKKkK", "KKKKKKKK"],
        "body_side": ["KKKK", "KgKK", "KKKK", "KKKK", "KKKK", "KKgK", "KKKK", "KKKK", "KRKK", "KKKK", "KKKK", "KKKK"],
        "arm": ["gGgK", "KKKK", "gKKg", "KKKK", "KRKK", "KKKK", "gGGg", "OOrO", "gGGg", "KKRK", "KKKK", "KRRK"],
        "leg": ["KKKK", "KRKK", "KKKK", "KKRK", "KKKK", "KKKK", "KKKK", "KKKK", "KKKK", "KKKK", "KRRK", "rKKr"],
    },
    5: {  # capucha azul marino, franjas rojas, manos celestes brillantes
        "pal": {"N": (25, 45, 85), "n": (40, 70, 115), "D": (18, 20, 38), "M": (232, 30, 70), "m": (140, 20, 50),
                "C": (20, 215, 235), "c": (0, 140, 195), "W": (235, 245, 250), "B": (40, 100, 170)},
        "head_front": ["NnNNnNNN", "NNNMMNnN", "NDMmDMDN", "NDmDDmDN", "NDDDDDDN", "DcWDDWcD", "NDDDDDDN", "NnDDDDnN"],
        "head_side": ["NnNNNNnN", "NNNNNNNN", "NNnNNNNN", "NNNNNnNN", "nNNNNNNN", "NNNNNNNN", "NnNNNNNn", "NNNNNNNN"],
        "head_back": ["NNNNnNNN", "NnNNNNNN", "NNNMMNNN", "NNNMmNNN", "NNNMMNNN", "NnNNNNnN", "NNNNNNNN", "nNNNNNNn"],
        "head_top": ["NnNNNNnN", "NNNMMNNN", "NNNMmNNN", "NNNNNNNN", "NnNNNNNN", "NNNNNnNN", "NNNNNNNN", "NNnNNNNN"],
        "body_front": ["NDDMmDDN", "NnDMDDnN", "NDDMDDcN", "nDDmDDDN", "NDDMDDcN", "NDDMDDDN", "nDDmmDDn", "NDMDDMDN",
                       "NDMDDcDN", "NmDDDDmN", "NDDDDDDN", "nDDDDDDn"],
        "body_back": ["NnNNnNNN", "NNNNNNNN", "nNNMMNNn", "NNNMMNNN", "NNNNNNNN", "NnNNNNnN", "NNNNNNNN", "NNNMMNNN",
                      "NNNNNNNN", "nNNNNNNn", "NNNNNNNN", "DDDDDDDD"],
        "body_side": ["NnNN", "NNNN", "NNnN", "NNNN", "NnNN", "NNNN", "NNNN", "NNnN", "NNNN", "NNNN", "nNNN", "DDDD"],
        "arm": ["NnNN", "NNWN", "NNNN", "nNNN", "NBNN", "NNcN", "BCcN", "CWCc", "CCWC", "cCCB", "NccN", "NDDN"],
        "leg": ["DDDM", "DnDM", "DDMm", "DDDM", "DcDM", "DDDM", "DDMm", "DDDM", "DDDm", "mDDM", "mmDm", "DmmD"],
    },
}


def grid_img(rows, pal):
    h, w = len(rows), len(rows[0])
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch != ".":
                im.putpixel((x, y), pal[ch] + (255,))
    return im


def from_ref3():
    """Copia el nivel 3 desde la imagen plana (frente y espalda, 8 px por pixel de skin)."""
    ref = Image.open(REF3).convert("RGBA")

    def cut(x0, y0, w, h):
        im = Image.new("RGBA", (w, h))
        for y in range(h):
            for x in range(w):
                im.putpixel((x, y), ref.getpixel((x0 + x * 8 + 4, y0 + y * 8 + 4)))
        return im

    def widen(arm3):  # brazos finos (3 px) -> 4 px repitiendo la columna del medio
        im = Image.new("RGBA", (4, arm3.size[1]))
        for y in range(arm3.size[1]):
            cols = [arm3.getpixel((0, y)), arm3.getpixel((1, y)), arm3.getpixel((1, y)), arm3.getpixel((2, y))]
            for x in range(4):
                im.putpixel((x, y), cols[x])
        return im

    f = {}
    f["head_front"] = cut(24, 0, 8, 8)
    f["head_back"] = cut(200, 0, 8, 8)
    f["body_front"] = cut(24, 64, 8, 12)
    f["body_back"] = cut(200, 64, 8, 12)
    f["arm_front"] = widen(cut(0, 64, 3, 12))
    f["arm_back"] = widen(cut(176, 64, 3, 12))
    f["leg_front"] = cut(24, 160, 4, 12)
    f["leg_back"] = cut(200, 160, 4, 12)
    # lados y techo: se arman con la espalda (la imagen no los muestra)
    f["head_side"] = f["head_back"]
    f["head_top"] = f["head_back"]
    f["body_side"] = f["body_back"].crop((0, 0, 4, 12))
    return f


def faces_for(level):
    if level == 3:
        f = from_ref3()
        f["arm_side"] = f["arm_front"]
        f["leg_side"] = f["leg_front"]
        return f
    s = SKINS[level]
    p = s["pal"]
    f = {k: grid_img(s[k], p) for k in ("head_front", "head_side", "head_back", "head_top",
                                         "body_front", "body_back", "body_side")}
    f["arm_front"] = f["arm_back"] = f["arm_side"] = grid_img(s["arm"], p)
    f["leg_front"] = f["leg_back"] = f["leg_side"] = grid_img(s["leg"], p)
    return f


def paste(dst, img, x, y):
    dst.paste(img, (x, y))


def build_layers(f):
    main = Image.new("RGBA", (64, 32), (0, 0, 0, 0))
    # cabeza (0,0): arriba, abajo, derecha, frente, izquierda, atras
    paste(main, f["head_top"], 8, 0)
    paste(main, f["head_top"], 16, 0)
    paste(main, f["head_side"], 0, 8)
    paste(main, f["head_front"], 8, 8)
    paste(main, f["head_side"].transpose(Image.FLIP_LEFT_RIGHT), 16, 8)
    paste(main, f["head_back"], 24, 8)
    # cuerpo (16,16)
    top = f["body_front"].crop((0, 0, 8, 4))
    paste(main, top, 20, 16)
    paste(main, top, 28, 16)
    paste(main, f["body_side"], 16, 20)
    paste(main, f["body_front"], 20, 20)
    paste(main, f["body_side"], 28, 20)
    paste(main, f["body_back"], 32, 20)
    # brazo (40,16)
    atop = f["arm_front"].crop((0, 0, 4, 4))
    paste(main, atop, 44, 16)
    paste(main, f["arm_front"].crop((0, 8, 4, 12)), 48, 16)
    paste(main, f["arm_side"], 40, 20)
    paste(main, f["arm_front"], 44, 20)
    paste(main, f["arm_side"], 48, 20)
    paste(main, f["arm_back"], 52, 20)
    # botas: solo la parte de abajo de las piernas (las filas de arriba transparentes)
    boots = Image.new("RGBA", (16, 16), (0, 0, 0, 0))

    def leg_block(img, front, side, back, from_row=0):
        def low(i):
            out = Image.new("RGBA", i.size, (0, 0, 0, 0))
            out.paste(i.crop((0, from_row, i.size[0], i.size[1])), (0, from_row))
            return out
        img.paste(low(front).crop((0, 8, 4, 12)), (8, 0))
        img.paste(low(side), (0, 4))
        img.paste(low(front), (4, 4))
        img.paste(low(side), (8, 4))
        img.paste(low(back), (12, 4))
        if from_row == 0:
            img.paste(front.crop((0, 0, 4, 4)), (4, 0))

    leg_block(boots, f["leg_front"], f["leg_side"], f["leg_back"], from_row=8)
    main.paste(boots, (0, 16), boots)

    legs = Image.new("RGBA", (64, 32), (0, 0, 0, 0))
    lb = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    leg_block(lb, f["leg_front"], f["leg_side"], f["leg_back"])
    legs.paste(lb, (0, 16))
    # cintura (cuerpo en la capa de pantalones)
    paste(legs, f["body_front"].crop((0, 0, 8, 4)), 20, 16)
    paste(legs, f["body_side"], 16, 20)
    paste(legs, f["body_front"], 20, 20)
    paste(legs, f["body_side"], 28, 20)
    paste(legs, f["body_back"], 32, 20)
    return main, legs


def main():
    for lvl in range(1, 6):
        m, l = build_layers(faces_for(lvl))
        os.makedirs(os.path.join(OUT, "humanoid"), exist_ok=True)
        os.makedirs(os.path.join(OUT, "humanoid_leggings"), exist_ok=True)
        m.save(os.path.join(OUT, "humanoid", f"mago_{lvl}.png"))
        l.save(os.path.join(OUT, "humanoid_leggings", f"mago_{lvl}.png"))
    print("armaduras de mago listas")


if __name__ == "__main__":
    main()
