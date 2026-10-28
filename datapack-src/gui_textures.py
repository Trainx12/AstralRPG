# -*- coding: utf-8 -*-
"""
Interfaz estilo "piedra y oro" para el resource pack (dibujo propio, inspirado en packs medievales).

Toma las texturas de interfaz de Minecraft (sacadas del client.jar) y les cambia los colores, asi cada ventana
conserva su forma exacta (casilleros, flechas del horno, etc.):
  fondo gris claro  -> ladrillos de piedra oscura        borde blanco     -> dorado
  borde gris oscuro -> bronce                             contorno negro   -> marron casi negro
  casillero gris    -> hueco oscuro                       sombras/luces del casillero -> marrones
Tambien: barra de items, tooltips y botones.

Uso:  python gui_textures.py <carpeta con assets/minecraft/textures/gui de Minecraft 26.1.x>
Salida: pack-source/gui/assets/minecraft/textures/gui/... (lo copia build_pack.py)
"""
import os
import random
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "pack-source", "gui")

# colores
ORO = (217, 164, 58)
ORO_CLARO = (240, 200, 96)
BRONCE = (107, 74, 28)
CONTORNO = (28, 21, 13)
HUECO = (46, 41, 34)
HUECO_SOMBRA = (23, 19, 14)
HUECO_LUZ = (122, 106, 80)
PIEDRA = (94, 87, 76)
JUNTA = (63, 57, 47)

# que archivos se tocan (carpetas y archivos sueltos relativos a textures/gui)
CARPETAS = ["container", "sprites/container", "sprites/widget", "sprites/recipe_book"]
SUELTOS = ["sprites/hud/hotbar.png", "sprites/hud/hotbar_selection.png", "sprites/hud/hotbar_offhand_left.png",
           "sprites/hud/hotbar_offhand_right.png", "sprites/tooltip/background.png", "sprites/tooltip/frame.png"]


def ladrillo(x, y):
    """Color de la piedra de fondo en (x, y): ladrillos de 8x4 desfasados, con juntas y un poco de ruido."""
    fila = y // 4
    dx = (x + (4 if fila % 2 else 0))
    if y % 4 == 3 or dx % 8 == 7:
        base = JUNTA
    else:
        rnd = random.Random((dx // 8) * 7919 + fila * 104729)
        v = rnd.randint(-8, 8)
        base = tuple(max(0, min(255, c + v)) for c in PIEDRA)
    r = random.Random(x * 31337 + y * 7331)
    n = r.randint(-4, 4)
    return tuple(max(0, min(255, c + n)) for c in base)


def mezcla(a, b, t):
    return tuple(int(a[k] + (b[k] - a[k]) * t) for k in range(3))


def gris_a_color(v):
    """Grises que no son los de la paleta base: escala de marron oscuro a dorado claro."""
    t = v / 255
    if t < 0.5:
        return mezcla(CONTORNO, PIEDRA, t * 2)
    return mezcla(PIEDRA, ORO_CLARO, (t - 0.5) * 2)


def recolor(im):
    im = im.convert("RGBA")
    w, h = im.size
    src = im.load()
    out = Image.new("RGBA", (w, h))
    dst = out.load()

    def es(x, y, val):
        if 0 <= x < w and 0 <= y < h:
            r, g, b, a = src[x, y]
            return a > 0 and r == g == b == val
        return False

    for y in range(h):
        for x in range(w):
            r, g, b, a = src[x, y]
            if a == 0:
                dst[x, y] = (0, 0, 0, 0)
                continue
            if not (r == g == b):                       # pixel con color (flechas, iconos): se respeta
                dst[x, y] = (r, g, b, a)
                continue
            v = r
            if v == 198:
                c = ladrillo(x, y)
            elif v == 139:
                c = HUECO
            elif v == 255:
                junto_hueco = any(es(x + dx, y + dy, 139) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                c = HUECO_LUZ if junto_hueco else ORO
            elif v == 85:
                c = BRONCE
            elif v == 55:
                c = HUECO_SOMBRA
            elif v == 0:
                c = CONTORNO
            else:
                c = gris_a_color(v)
            dst[x, y] = c + (a,)
    return out


def tooltip_fondo(im):
    out = Image.new("RGBA", im.size)
    s, d = im.convert("RGBA").load(), out.load()
    for y in range(im.size[1]):
        for x in range(im.size[0]):
            a = s[x, y][3]
            d[x, y] = (24, 18, 12, min(a, 238)) if a else (0, 0, 0, 0)
    return out


def tooltip_marco(im):
    """El marco violeta pasa a dorado (arriba mas claro, abajo bronce)."""
    out = Image.new("RGBA", im.size)
    s, d = im.convert("RGBA").load(), out.load()
    h = im.size[1]
    for y in range(h):
        col = mezcla(ORO_CLARO, BRONCE, y / max(1, h - 1))
        for x in range(im.size[0]):
            a = s[x, y][3]
            d[x, y] = col + (a,) if a else (0, 0, 0, 0)
    return out


# El HUD (barra de items, corazones, comida, etc.) se dibuja de cero en hud_rpg.py
from hud_rpg import hud  # noqa: E402


def main():
    src = os.path.join(sys.argv[1]) if len(sys.argv) > 1 else os.environ.get("VANILLA_GUI")
    if not src or not os.path.isdir(src):
        sys.exit("Falta la carpeta textures/gui de Minecraft (sacala del client.jar)")
    hechos = 0
    lista = []
    for c in CARPETAS:
        for root, _, fs in os.walk(os.path.join(src, c)):
            for f in fs:
                if f.endswith(".png"):
                    lista.append(os.path.relpath(os.path.join(root, f), src))
    lista += SUELTOS
    for rel in lista:
        p = os.path.join(src, rel)
        if not os.path.exists(p):
            continue
        im = Image.open(p)
        if rel.endswith("tooltip/background.png"):
            out = tooltip_fondo(im)
        elif rel.endswith("tooltip/frame.png"):
            out = tooltip_marco(im)
        else:
            out = recolor(im)
        dst = os.path.join(OUT, "assets", "minecraft", "textures", "gui", rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        out.save(dst)
        mc = p + ".mcmeta"                      # sprites que se estiran en 9 partes necesitan su .mcmeta
        if os.path.exists(mc):
            with open(mc, "rb") as fi, open(dst + ".mcmeta", "wb") as fo:
                fo.write(fi.read())
        hechos += 1
    for rel, im in hud().items():
        dst = os.path.join(OUT, "assets", "minecraft", "textures", "gui", rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        im.save(dst)
        hechos += 1
    print(f"interfaz: {hechos} texturas -> {os.path.abspath(OUT)}")


if __name__ == "__main__":
    main()
