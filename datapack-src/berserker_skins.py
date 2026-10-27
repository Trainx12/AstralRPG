# -*- coding: utf-8 -*-
"""
Texturas de las armaduras de Berserker (niveles 1 a 5) copiadas de las skins de referencia
(pack-source/ref/berserker1.png ... berserker5.png).
- Niveles 1, 4 y 5: vista de PlanetMinecraft (espalda, costado, frente, costado), 4 px por pixel.
- Niveles 2 y 3: renders de frente y espalda; cada parte se mapea con un cuadrilatero.
"""
import os

from PIL import Image

import mage_skins

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, "pack-source", "ref")


def is_bg(p):
    r, g, b, a = p
    if a < 40:
        return True
    if r > 235 and g > 235 and b > 235:  # fondo blanco
        return True
    # fondo lila de PlanetMinecraft
    return 140 < r < 200 and 160 < g < 210 and b > 205 and b - r > 40


def sample_quad(img, quad, w, h):
    """quad = (arriba-izq, arriba-der, abajo-der, abajo-izq); devuelve una imagen w x h."""
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = quad
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for j in range(h):
        v = (j + 0.5) / h
        for i in range(w):
            u = (i + 0.5) / w
            tx, ty = x0 + (x1 - x0) * u, y0 + (y1 - y0) * u
            bx, by = x3 + (x2 - x3) * u, y3 + (y2 - y3) * u
            x, y = tx + (bx - tx) * v, ty + (by - ty) * v
            p = img.getpixel((int(min(max(x, 0), img.size[0] - 1)), int(min(max(y, 0), img.size[1] - 1))))
            if not is_bg(p):
                out.putpixel((i, j), p[:3] + (255,))
    return fill_holes(out)


def fill_holes(img):
    """Rellena pixeles transparentes sueltos con el vecino (la armadura tiene que ser solida)."""
    w, h = img.size
    px = img.load()
    for _ in range(2):
        for y in range(h):
            for x in range(w):
                if px[x, y][3] == 0:
                    for dx, dy in ((0, -1), (-1, 0), (1, 0), (0, 1)):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < w and 0 <= ny < h and px[nx, ny][3] > 0:
                            px[x, y] = px[nx, ny]
                            break
    return img


def box(x0, y0, x1, y1):
    return ((x0, y0), (x1, y0), (x1, y1), (x0, y1))


def pmc_faces(path):
    """Vista de PlanetMinecraft 256x146: espalda x=8, costado x=88, frente x=136. 4 px por pixel."""
    img = Image.open(path).convert("RGBA")
    S, Y = 4, 6
    f = {}

    def g(x0, col, row, w, h):
        return sample_quad(img, box(x0 + col * S, Y + row * S, x0 + (col + w) * S, Y + (row + h) * S), w, h)

    f["head_front"] = g(136, 4, 0, 8, 8)
    f["body_front"] = g(136, 4, 8, 8, 12)
    f["arm_front"] = g(136, 0, 8, 4, 12)
    f["leg_front"] = g(136, 4, 20, 4, 12)
    f["head_back"] = g(8, 4, 0, 8, 8)
    f["body_back"] = g(8, 4, 8, 8, 12)
    f["arm_back"] = g(8, 12, 8, 4, 12)
    f["leg_back"] = g(8, 8, 20, 4, 12)
    f["head_side"] = g(88, 0, 0, 8, 8)
    f["arm_side"] = g(88, 2, 8, 4, 12)
    f["leg_side"] = g(88, 2, 20, 4, 12)
    f["body_side"] = f["arm_side"]
    f["head_top"] = f["head_back"]
    return f


def render_faces(path, parts):
    img = Image.open(path).convert("RGBA")
    f = {k: sample_quad(img, q, w, h) for k, (q, w, h) in parts.items()}
    f["head_side"] = f["head_back"]
    f["head_top"] = f["head_back"]
    f["body_side"] = f["body_back"].crop((0, 0, 4, 12))
    f["arm_side"] = f["arm_front"]
    f["leg_side"] = f["leg_front"]
    return f


# Nivel 3 (render 538x437). La foto esta girada: se ve el frente y un costado.
# Solo se toma la cara de frente de cada parte (los ojos naranjas quedan en la fila 4).
L3 = {
    "head_front": (box(63, 10, 150, 96), 8, 8),
    "body_front": (box(63, 100, 168, 248), 8, 12),
    "arm_front": (((8, 102), (63, 102), (63, 246), (2, 236)), 4, 12),
    "leg_front": (box(82, 256, 128, 396), 4, 12),
    "head_back": (box(323, 10, 410, 96), 8, 8),
    "body_back": (box(332, 100, 440, 248), 8, 12),
    "arm_back": (((440, 102), (480, 102), (500, 236), (448, 246)), 4, 12),
    "leg_back": (box(346, 256, 394, 396), 4, 12),
}
# Nivel 2 (render 402x288, brazos abiertos y cabeza girada: la cara es la parte izquierda)
L2 = {
    "head_front": (box(48, 8, 112, 72), 8, 8),
    "body_front": (box(60, 66, 130, 170), 8, 12),
    "arm_front": (((38, 66), (60, 66), (45, 156), (10, 146)), 4, 12),
    "leg_front": (box(64, 176, 96, 262), 4, 12),
    "head_back": (box(262, 8, 330, 72), 8, 8),
    "body_back": (box(258, 66, 328, 170), 8, 12),
    "arm_back": (((326, 66), (348, 66), (388, 146), (358, 156)), 4, 12),
    "leg_back": (box(264, 176, 296, 262), 4, 12),
}


def is_skin(p):
    r, g, b, a = p
    return a > 0 and r > 130 and g > 95 and b > 65 and r - b > 22 and r >= g >= b


def clear_skin(img):
    """La piel del personaje queda transparente: asi se ve la cara y los brazos de quien la lleva."""
    px = img.load()
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            if is_skin(px[x, y]):
                px[x, y] = (0, 0, 0, 0)
    return img


def faces_for(level):
    path = os.path.join(REF, f"berserker{level}.png")
    if level in (1, 4, 5):
        f = pmc_faces(path)
    else:
        f = render_faces(path, L3 if level == 3 else L2)
    if level == 1:
        for k in ("head_front", "head_side", "arm_front", "arm_back", "arm_side"):
            f[k] = clear_skin(f[k].copy())
    return f


def main():
    out = mage_skins.OUT
    for lvl in range(1, 6):
        m, l = mage_skins.build_layers(faces_for(lvl))
        m.save(os.path.join(out, "humanoid", f"berserker_{lvl}.png"))
        l.save(os.path.join(out, "humanoid_leggings", f"berserker_{lvl}.png"))
    print("armaduras de berserker listas")


if __name__ == "__main__":
    main()
