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
import argparse
import io
import random
import sys
import zipfile

from PIL import Image, ImageDraw
from pathlib import Path


def save_png(image, path):
    buffer = io.BytesIO()
    image.save(buffer, 'PNG')
    target = Path(path)
    data = buffer.getvalue()
    if target.exists() and target.read_bytes() == data:
        return
    temporary = target.with_suffix('.png.tmp')
    temporary.write_bytes(data)
    temporary.replace(target)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "pack-source", "gui")

# colores
ORO = (230, 165, 42)
ORO_CLARO = (255, 232, 150)
BRONCE = (125, 66, 23)
CONTORNO = (28, 21, 13)
HUECO = (189, 143, 83)
HUECO_SOMBRA = (104, 65, 32)
HUECO_LUZ = (255, 222, 154)
PIEDRA = (239, 203, 139)
JUNTA = (218, 175, 107)

# que archivos se tocan (carpetas y archivos sueltos relativos a textures/gui)
CARPETAS = ["container", "sprites/container", "sprites/widget", "sprites/recipe_book"]
SUELTOS = ["sprites/tooltip/background.png", "sprites/tooltip/frame.png"]

# Las ventanas y el HUD se pueden regenerar por separado.
HUD_RPG = True


def ladrillo(x, y):
    """Pergamino calido: sin juntas de piedra ni acentos morados."""
    base = PIEDRA
    r = random.Random(x * 31337 + y * 7331)
    n = r.randint(-4, 4)
    return tuple(max(0, min(255, c + n)) for c in base)


def ornate_button(im, highlighted=False, disabled=False):
    """Boton propio de pergamino y oro con hojas verdes en las esquinas."""
    out = Image.new('RGBA', im.size)
    d = ImageDraw.Draw(out)
    w, h = out.size
    d.rectangle((0, 0, w - 1, h - 1), fill=CONTORNO)
    d.rectangle((1, 1, w - 2, h - 2), fill=ORO_CLARO if highlighted else ORO)
    d.rectangle((2, 2, w - 3, h - 3), outline=BRONCE)
    for y in range(3, h - 3):
        t = (y - 3) / max(1, h - 7)
        col = mezcla((255, 230, 169), (215, 155, 77), t)
        if disabled:
            col = mezcla(col, (107, 97, 76), 0.55)
        d.line((3, y, w - 4, y), fill=col)
    d.line((4, 3, w - 5, 3), fill=(255, 248, 198))
    d.line((4, h - 4, w - 5, h - 4), fill=(150, 75, 26))
    d.line((9, h - 3, w - 10, h - 3), fill=(164, 47, 22))
    for x, direction in ((4, 1), (w - 5, -1)):
        d.line((x, 3, x, h - 4), fill=(29, 70, 23))
        for y in (4, 8, 12, h - 5):
            center = x + direction * (2 if y % 8 else 0)
            d.polygon([(center - 2, y), (center, y - 2), (center + 2, y), (center, y + 2)], fill=(35, 89, 26))
            d.line((center - 1, y, center + 1, y - 1), fill=(111, 184, 42))
            d.point((center, y - 1), fill=(185, 224, 79))
        d.rectangle((x - 1, h // 2 - 1, x + 1, h // 2 + 1), fill=ORO_CLARO)
        d.point((x, h // 2), fill=(199, 66, 26))
    return out


def mezcla(a, b, t):
    return tuple(int(a[k] + (b[k] - a[k]) * t) for k in range(3))


def gris_a_color(v, piedra=PIEDRA, oro_claro=ORO_CLARO):
    """Grises que no son los de la paleta base: escala de marron oscuro a dorado claro."""
    t = v / 255
    if t < 0.5:
        return mezcla(CONTORNO, piedra, t * 2)
    return mezcla(piedra, oro_claro, (t - 0.5) * 2)


def ladrillo_oscuro(x, y):
    fila = y // 4
    dx = x + (4 if fila % 2 else 0)
    if y % 4 == 3 or dx % 8 == 7:
        base = (63, 57, 47)
    else:
        v = random.Random((dx // 8) * 7919 + fila * 104729).randint(-8, 8)
        base = tuple(max(0, min(255, c + v)) for c in (94, 87, 76))
    n = random.Random(x * 31337 + y * 7331).randint(-4, 4)
    return tuple(max(0, min(255, c + n)) for c in base)


def recolor(im, dark_container=False):
    oro, brillo, bronce, hueco, sombra, luz, piedra = (
        ((217, 164, 58), (240, 200, 96), (107, 74, 28), (46, 41, 34),
         (23, 19, 14), (122, 106, 80), (94, 87, 76)) if dark_container else
        (ORO, ORO_CLARO, BRONCE, HUECO, HUECO_SOMBRA, HUECO_LUZ, PIEDRA))
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
                c = ladrillo_oscuro(x, y) if dark_container else ladrillo(x, y)
            elif v == 139:
                c = hueco
            elif v == 255:
                junto_hueco = any(es(x + dx, y + dy, 139) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                c = luz if junto_hueco else oro
            elif v == 85:
                c = bronce
            elif v == 55:
                c = sombra
            elif v == 0:
                c = CONTORNO
            else:
                c = gris_a_color(v, piedra, brillo)
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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("src", nargs="?", default=os.environ.get("VANILLA_GUI"))
    parser.add_argument("--hud-only", action="store_true", help="Conservar todas las ventanas existentes")
    parser.add_argument("--client-jar", help="Validar sprites y dimensiones contra el cliente de la version usada")
    args = parser.parse_args()
    src = args.src
    if not args.hud_only and (not src or not os.path.isdir(src)):
        sys.exit("Falta la carpeta textures/gui de Minecraft (sacala del client.jar)")
    hechos = 0
    lista = []
    for c in (CARPETAS if not args.hud_only else []):
        for root, _, fs in os.walk(os.path.join(src, c)):
            for f in fs:
                if f.endswith(".png"):
                    lista.append(os.path.relpath(os.path.join(root, f), src).replace(os.sep, '/'))
    if not args.hud_only:
        lista += SUELTOS
    for rel in lista:
        p = os.path.join(src, rel)
        if not os.path.exists(p):
            continue
        im = Image.open(p)
        if rel.startswith('sprites/widget/button') and im.width >= 20:
            out = ornate_button(im, 'highlighted' in rel, 'disabled' in rel)
        elif rel.endswith("tooltip/background.png"):
            out = tooltip_fondo(im)
        elif rel.endswith("tooltip/frame.png"):
            out = tooltip_marco(im)
        else:
            out = recolor(im, dark_container=rel.startswith(('container/', 'sprites/container/', 'sprites/recipe_book/')))
        dst = os.path.normpath(os.path.join(OUT, "assets", "minecraft", "textures", "gui", rel))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        save_png(out, dst)
        mc = p + ".mcmeta"                      # sprites que se estiran en 9 partes necesitan su .mcmeta
        if os.path.exists(mc):
            with open(mc, "rb") as fi, open(dst + ".mcmeta", "wb") as fo:
                fo.write(fi.read())
        if rel.startswith('sprites/widget/button'):
            import json
            Path(dst + '.mcmeta').write_text(json.dumps({'gui': {'scaling': {
                'type': 'nine_slice', 'width': im.width, 'height': im.height,
                'border': {'left': 9, 'right': 9, 'top': 3, 'bottom': 3}}}}, indent=2), encoding='utf-8')
        hechos += 1
    sprites = hud() if HUD_RPG else {}
    if args.client_jar:
        # Validar todo antes de escribir: un nombre inexistente o una medida distinta
        # abortan la generacion en vez de publicar un pack aparentemente correcto.
        with zipfile.ZipFile(args.client_jar) as client:
            for rel, im in sprites.items():
                path = "assets/minecraft/textures/gui/" + rel
                if path not in client.namelist():
                    sys.exit(f"Sprite inexistente en el cliente: {rel}")
                with Image.open(io.BytesIO(client.read(path))) as vanilla:
                    if im.size != vanilla.size:
                        sys.exit(f"Dimensiones incorrectas: {rel}: {im.size}, esperadas {vanilla.size}")
    for rel, im in sprites.items():
        dst = os.path.normpath(os.path.join(OUT, "assets", "minecraft", "textures", "gui", rel))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        save_png(im, dst)
        # Son sprites estaticos con escala stretch por defecto. No heredar un
        # .mcmeta antiguo (animacion, tile o nine_slice) al sobrescribir su PNG.
        if os.path.exists(dst + ".mcmeta"):
            os.remove(dst + ".mcmeta")
        hechos += 1
    print(f"interfaz: {hechos} texturas -> {os.path.abspath(OUT)}")


if __name__ == "__main__":
    main()
