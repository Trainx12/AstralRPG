# -*- coding: utf-8 -*-
"""
Texturas de las armaduras de Arquero (niveles 1 a 5) copiadas de las skins de referencia
(pack-source/ref/arquero1.png ... arquero5.png).
- Niveles 1 y 2: frente y espalda planos (8 px por pixel de skin).
- Nivel 3: solo frente (10 px por pixel); la espalda se arma a partir del frente.
- Nivel 4: vista de PlanetMinecraft.
- Nivel 5: render en perspectiva, pasado a mano (cuadricula de letras).
La piel del personaje queda transparente (se ve la cara y los brazos de quien la lleva).
"""
import os

from PIL import Image

import berserker_skins as bs
import mage_skins

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, "pack-source", "ref")

LEVEL5 = {
    "pal": {"K": (8, 8, 16), "N": (20, 20, 62), "n": (36, 30, 92), "P": (95, 70, 182), "p": (150, 120, 222),
            "L": (215, 200, 250), "W": (245, 245, 255), "Y": (212, 172, 92), "y": (140, 100, 50)},
    "head_front": ["KKyYYyKK", "KYYPPYYK", "YKNPpNKY", "yWWPpWWy", "KNNPpNNK", "KNnPpnNK", "KNnPpnNK", "KKNPpNKK"],
    "head_side": ["KKyYYyKK", "yYYKKKYy", "KKKKKKKK", "yYYyKKKK", "KKKKKKKK", "KKNKKKKK", "KKKKNKKK", "KKKKKKKK"],
    "head_back": ["KKyYYyKK", "yYYYYYYy", "KKKNNKKK", "yYYYYYYy", "KKKNNKKK", "KKNNNNKK", "KKKNNKKK", "KKKKKKKK"],
    "head_top": ["KKyYYyKK", "KKYPPYKK", "KNNPPNNK", "KNnPPnNK", "KNnPPnNK", "KNNPPNNK", "KKNNNNKK", "KKKKKKKK"],
    "body_front": ["NNnPpnNN", "NnnPLnnN", "nPPLWLPn", "PpLWWWLp", "nPPLWLPn", "NnPLWPnN", "NnnPLnnN", "NNnPLnNN",
                   "NNnPpnNN", "KNnPpnNK", "KNnpPnNK", "KKNPpNKK"],
    "body_back": ["NNnPpnNN", "NnnYYnnN", "nPYLWYPn", "PYYWWYYp", "nPYLWYPn", "NnPYYPnN", "NnnPLnnN", "NNnPLnNN",
                  "NNnPpnNN", "KNnPpnNK", "KNnpPnNK", "KKNPpNKK"],
    "body_side": ["KNNK", "KNnK", "NnPN", "NPpN", "NnPN", "KNnK", "KNNK", "KNNK", "KNNK", "KKNK", "KKNK", "KKKK"],
    "arm": ["KNNK", "NnnN", "KNNK", "YYyY", "KNnK", "yYYy", "KNNK", "YyYY", "KNnK", "KNNK", "yYYy", "KKKK"],
    "leg": ["NnPp", "NnPL", "NNPp", "KNnP", "KNnP", "yKNP", "KKNp", "YKNn", "KKNN", "yYKN", "KKKK", "YyKK"],
}


def flat_faces(path, back_x, px=8):
    """Imagen plana: frente con brazos de 4 px desde x=0, espalda desde back_x."""
    img = Image.open(path).convert("RGBA")

    def g(x0, col, row, w, h):
        return bs.sample_quad(img, bs.box(x0 + col * px, row * px, x0 + (col + w) * px, (row + h) * px), w, h)

    f = {
        "head_front": g(0, 4, 0, 8, 8), "body_front": g(0, 4, 8, 8, 12), "arm_front": g(0, 0, 8, 4, 12),
        "leg_front": g(0, 4, 20, 4, 12),
        "head_back": g(back_x, 4, 0, 8, 8), "body_back": g(back_x, 4, 8, 8, 12), "arm_back": g(back_x, 12, 8, 4, 12),
        "leg_back": g(back_x, 8, 20, 4, 12),
    }
    f["head_side"] = f["head_back"]
    f["head_top"] = f["head_back"]
    f["body_side"] = f["body_back"].crop((0, 0, 4, 12))
    f["arm_side"] = f["arm_front"]
    f["leg_side"] = f["leg_front"]
    return f


def front_only_faces(path):
    """Nivel 3: solo frente (10 px por pixel). La espalda es el frente espejado con la capucha cerrada."""
    img = Image.open(path).convert("RGBA")
    # el fondo es negro puro: lo tratamos como transparente
    px = img.load()
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            r, g, b, a = px[x, y]
            if r < 6 and g < 6 and b < 6:
                px[x, y] = (0, 0, 0, 0)
    f = {
        "head_front": bs.sample_quad(img, bs.box(40, 5, 120, 95), 8, 8),
        "body_front": bs.sample_quad(img, bs.box(40, 95, 120, 205), 8, 12),
        "arm_front": bs.sample_quad(img, bs.box(0, 95, 40, 205), 4, 12),
        "leg_front": bs.sample_quad(img, bs.box(40, 205, 80, 325), 4, 12),
    }
    hood = f["head_front"].getpixel((3, 0))
    hb = Image.new("RGBA", (8, 8), hood)
    hb.paste(f["head_front"].crop((0, 0, 8, 2)), (0, 0))
    f["head_back"] = hb
    f["head_side"] = hb
    f["head_top"] = hb
    f["body_back"] = f["body_front"].transpose(Image.FLIP_LEFT_RIGHT)
    f["body_side"] = f["body_front"].crop((0, 0, 4, 12))
    f["arm_back"] = f["arm_side"] = f["arm_front"]
    f["leg_back"] = f["leg_side"] = f["leg_front"]
    return f


def grid_faces(spec):
    p = spec["pal"]
    f = {k: mage_skins.grid_img(spec[k], p) for k in ("head_front", "head_side", "head_back", "head_top",
                                                      "body_front", "body_back", "body_side")}
    f["arm_front"] = f["arm_back"] = f["arm_side"] = mage_skins.grid_img(spec["arm"], p)
    f["leg_front"] = f["leg_back"] = f["leg_side"] = mage_skins.grid_img(spec["leg"], p)
    return f


def faces_for(level):
    path = os.path.join(REF, f"arquero{level}.png")
    if level == 1:
        f = flat_faces(path, 168)
    elif level == 2:
        f = flat_faces(path, 160)
    elif level == 3:
        f = front_only_faces(path)
    elif level == 4:
        f = bs.pmc_faces(path)
    else:
        return grid_faces(LEVEL5)
    if level in (2, 3):
        for k in ("head_front", "head_side", "arm_front", "arm_back", "arm_side"):
            f[k] = bs.clear_skin(f[k].copy())
    return f


def main():
    out = mage_skins.OUT
    for lvl in range(1, 6):
        m, l = mage_skins.build_layers(faces_for(lvl))
        m.save(os.path.join(out, "humanoid", f"arquero_{lvl}.png"))
        l.save(os.path.join(out, "humanoid_leggings", f"arquero_{lvl}.png"))
    print("armaduras de arquero listas")


if __name__ == "__main__":
    main()
