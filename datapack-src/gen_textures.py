# -*- coding: utf-8 -*-
"""
Genera texturas para los items que no tenian una: armaduras (icono + como se ven puestas),
armas nuevas, talismanes y materiales nuevos. Recolorea formas vanilla y tus texturas.
Uso: python gen_textures.py   (escribe en pack-source/assets/astral/textures/...)
"""
import colorsys
import os

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "pack-source")
BASE = os.path.join(SRC, "vanilla-base")
OUT_ITEM = os.path.join(SRC, "assets", "astral", "textures", "item", "gen")
OUT_EQ = os.path.join(SRC, "assets", "astral", "textures", "entity", "equipment")


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def colorize(img, stops):
    """Pinta la imagen segun su luminosidad con un degradado de 3 colores."""
    img = img.convert("RGBA")
    px = img.load()
    w, h = img.size
    lums = [0.299 * r + 0.587 * g + 0.114 * b for y in range(h) for x in range(w)
            for (r, g, b, a) in [px[x, y]] if a > 0]
    if not lums:
        return img
    lo, hi = min(lums), max(lums)
    span = max(hi - lo, 1)
    c = [hexrgb(s) if isinstance(s, str) else s for s in stops]
    out = Image.new("RGBA", img.size)
    op = out.load()
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a == 0:
                op[x, y] = (0, 0, 0, 0)
                continue
            t = (0.299 * r + 0.587 * g + 0.114 * b - lo) / span
            if t < 0.5:
                k = t / 0.5
                a0, a1 = c[0], c[1]
            else:
                k = (t - 0.5) / 0.5
                a0, a1 = c[1], c[2]
            op[x, y] = tuple(int(a0[i] + (a1[i] - a0[i]) * k) for i in range(3)) + (a,)
    return out


def hue_shift(img, target_hue, min_sat=0.2):
    """Cambia el tono de los pixeles con color, deja los grises como estan."""
    img = img.convert("RGBA")
    px = img.load()
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            hh, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            if s >= min_sat:
                r2, g2, b2 = colorsys.hsv_to_rgb(target_hue, s, v)
                px[x, y] = (int(r2 * 255), int(g2 * 255), int(b2 * 255), a)
    return img


def load(rel):
    return Image.open(os.path.join(SRC, rel)).convert("RGBA")


def save(img, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)


# Paletas por set y tier: (sombra, medio, brillo)
PALETTES = {
    "berserker": [("#2a0c0c", "#7a2a1e", "#c46e50"), ("#231e23", "#7a3c3c", "#cbb4aa"),
                  ("#32050a", "#961420", "#e65050"), ("#14141e", "#552030", "#d04848"),
                  ("#321405", "#aa2814", "#ffc850")],
    "mago": [("#1e0f32", "#5a3296", "#aa82e6"), ("#280a46", "#8232c8", "#dcaaff"),
             ("#0f0a3c", "#3c32aa", "#968cff"), ("#190a2d", "#6e1e8c", "#f0c85a"),
             ("#0a1e3c", "#288cd2", "#c8faff")],
    "arquero": [("#281e0f", "#64552d", "#aaa064"), ("#0f280f", "#326e2d", "#8cc86e"),
                ("#0a2828", "#28786e", "#8cdcc8"), ("#1e3c37", "#6ec8aa", "#e6fff5"),
                ("#283250", "#78b4f0", "#ffe68c")],
}
SET_MAT = {"berserker": ["chainmail", "iron", "iron", "diamond", "netherite"],
           "mago": ["leather"] * 5, "arquero": ["leather"] * 5}
PIECES = ["helmet", "chestplate", "leggings", "boots"]


def main():
    made = []
    # Armaduras
    for set_id, pals in PALETTES.items():
        for t, pal in enumerate(pals, start=1):
            mat = SET_MAT[set_id][t - 1]
            for layer in ("humanoid", "humanoid_leggings"):
                img = colorize(Image.open(os.path.join(BASE, layer, f"{mat}.png")), pal)
                save(img, os.path.join(OUT_EQ, layer, f"{set_id}_{t}.png"))
            for p in PIECES:
                img = colorize(Image.open(os.path.join(BASE, "item", f"{mat}_{p}.png")), pal)
                save(img, os.path.join(OUT_ITEM, f"{set_id}_{t}_{p}.png"))
                made.append(f"{set_id}_{t}_{p}")

    A = "assets/astral/textures/item/"
    W = "assets/armasrpg/textures/item/"
    jobs = {
        # armas
        "hacha_4": (W + "hacha_1.png", ("#0a1e3c", "#3c8cd2", "#c8f0ff")),
        "hacha_5": (W + "hacha_2.png", ("#321405", "#c84614", "#ffd264")),
        "guadana_1": (W + "scythe_1.png", ("#1e1e23", "#6e6e78", "#d2d2dc")),
        "guadana_4": (W + "scythe_3.png", ("#1e0a32", "#7832b4", "#f0c85a")),
        "guadana_umbria": (W + "scythe_1.png", ("#0f0519", "#4b1e78", "#b478ff")),
        "taladro_infernal": (A + "martillo_de_reforjado.png", ("#280a05", "#b43c14", "#ffc850")),
        "guantes_meteoro": (A + "nucleo_de_furia.png", ("#3c1405", "#e66e1e", "#ffe68c")),
        # materiales
        "fragmento_cristal": (A + "fragmento_umbrio.png", ("#3c2864", "#a07cf0", "#f0e6ff")),
        "cristal_refinado": (A + "cristal_arcano.png", ("#3c2878", "#b48cff", "#ffffff")),
        "corazon_shulker": (A + "nucleo_astral.png", ("#321446", "#a050c8", "#ffd2ff")),
        "esencia_elite": (A + "esencia_wither.png", ("#0a2814", "#3cc864", "#dcffe6")),
        "alma_corrupta": (A + "gema_umbria_perfecta.png", ("#1e0528", "#a01ec8", "#ff8cff")),
        "chispa_astral": (A + "polvo_astral.png", ("#3c2805", "#ffc81e", "#ffffdc")),
    }
    for iid, (src, pal) in jobs.items():
        save(colorize(load(src), pal), os.path.join(OUT_ITEM, f"{iid}.png"))
        made.append(iid)
    # Gancho: caña de pescar en metal oscuro
    save(colorize(Image.open(os.path.join(BASE, "item", "fishing_rod.png")), ("#1e1e28", "#78788c", "#e6e6f0")),
         os.path.join(OUT_ITEM, "gancho.png"))
    made.append("gancho")
    # Talismanes: forma de gema, color por tipo y mas brillo por nivel
    tal = {"vida": ("#3c0505", "#dc2828", "#ffb4b4"), "furia": ("#3c1405", "#f07814", "#ffdca0"),
           "viento": ("#0a3228", "#50dcb4", "#f0fffa"), "roca": ("#1e1e1e", "#78787d", "#dcdce1")}
    bases = [A + "gema_luminica.png", A + "gema_luminica_perfecta.png", A + "gema_umbria_perfecta.png"]
    for tid, pal in tal.items():
        for lv in range(3):
            save(colorize(load(bases[lv]), pal), os.path.join(OUT_ITEM, f"talisman_{tid}_{lv + 1}.png"))
            made.append(f"talisman_{tid}_{lv + 1}")
    return made


if __name__ == "__main__":
    m = main()
    print(len(m), "texturas generadas")
