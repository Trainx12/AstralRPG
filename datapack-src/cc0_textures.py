# -*- coding: utf-8 -*-
"""
Reemplaza las texturas que eran recolores por texturas nuevas de dominio publico (CC0).
Fuentes y creditos: pack-source/cc0/CREDITOS.txt
Se escribe encima de textures/item/gen/<id>.png, asi el resto del armado no cambia.
"""
import os

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "pack-source", "cc0")
OUT = os.path.join(HERE, "pack-source", "assets", "astral", "textures", "item", "gen")
JETREL_BG = (111, 119, 109)


def cell(sheet, col, row, size=16, key=None):
    im = Image.open(os.path.join(SRC, sheet)).convert("RGBA").crop(
        (col * size, row * size, col * size + size, row * size + size))
    if key:
        px = im.load()
        for y in range(im.size[1]):
            for x in range(im.size[0]):
                if px[x, y][:3] == key:
                    px[x, y] = (0, 0, 0, 0)
    return im


def full(rel):
    return Image.open(os.path.join(SRC, rel)).convert("RGBA")


def jet(col, row):
    return cell("jetrel_items.png", col, row, key=JETREL_BG)


# item -> textura nueva (pensada segun el nombre)
PICKS = {
    # armas
    "hacha_4": lambda: cell("steel-weapons.png", 2, 11),          # Hacha del Coloso: hacha doble de acero
    "hacha_5": lambda: cell("gold-weapons.png", 2, 15),           # Hacha del Apocalipsis: hacha dorada
    "guadana_1": lambda: cell("steel-weapons.png", 14, 10),       # Guadana Umbria Menor
    "guadana_4": lambda: cell("gold-weapons.png", 14, 15),        # Guadana del Archimago: dorada
    "guadana_umbria": lambda: cell("steel-weapons.png", 14, 16),  # Guadana Umbria (especial)
    "taladro_infernal": lambda: cell("steel-weapons.png", 23, 11),  # martillo con cabeza ardiente
    "gancho": lambda: cell("steel-weapons.png", 15, 12),          # gancho curvo
    "guantes_meteoro": lambda: jet(4, 5),                         # guantelete
    # materiales
    "fragmento_cristal": lambda: full("gem/small_purple.png"),
    "cristal_refinado": lambda: full("gem/large_purple.png"),
    "corazon_shulker": lambda: full("gem/heart.png"),
    "esencia_elite": lambda: jet(3, 4),                           # frasco de esencia
    "alma_corrupta": lambda: jet(6, 5),                           # alma verde
    "chispa_astral": lambda: jet(5, 5),                           # esfera con destellos
    # talismanes: cada tipo con su color, y joyas mas elaboradas en cada nivel
    "talisman_vida_1": lambda: full("ring/ring_03_red.png"),
    "talisman_vida_2": lambda: full("amulet/crystal_red.png"),
    "talisman_vida_3": lambda: full("amulet/celtic_red.png"),
    "talisman_furia_1": lambda: full("amulet/cameo_orange.png"),
    "talisman_furia_2": lambda: full("amulet/penta_orange.png"),
    "talisman_furia_3": lambda: full("amulet/face_01_gold.png"),
    "talisman_viento_1": lambda: full("ring/ring_03_light_green.png"),
    "talisman_viento_2": lambda: full("amulet/eye_cyan.png"),
    "talisman_viento_3": lambda: full("amulet/crystal_green.png"),
    "talisman_roca_1": lambda: full("ring/ring_03_gray.png"),
    "talisman_roca_2": lambda: full("amulet/bone_gray.png"),
    "talisman_roca_3": lambda: full("amulet/cylinder_gray.png"),
}


def main():
    os.makedirs(OUT, exist_ok=True)
    for iid, f in PICKS.items():
        f().save(os.path.join(OUT, f"{iid}.png"))
    print(len(PICKS), "texturas CC0 aplicadas")


if __name__ == "__main__":
    main()
