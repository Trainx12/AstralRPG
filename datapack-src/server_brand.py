"""Icono (server-icon.png, 64x64) y descripcion (motd) de la lista de servidores.

Identidad de la portada "AstralRPG foto": letra de piedra con borde dorado, cristal celeste y estrella
astral sobre una noche violeta. Pedido del dueno 14/11/2026: no invasivo, como Hypixel o Universocraft.
python server_brand.py -> build/servidor/server-icon.png, motd.txt y una vista previa de la lista.
"""
import math
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'build/servidor'
S = 256  # se dibuja a 4x y se reduce a 64
GOLD, GOLD_DARK = (240, 198, 92), (150, 98, 26)
CYAN = (110, 236, 255)


def gradient(size, top, bottom):
    im = Image.new('RGBA', size)
    d = ImageDraw.Draw(im)
    for y in range(size[1]):
        t = y / (size[1] - 1)
        d.line((0, y, size[0], y), fill=tuple(round(a + (b - a) * t) for a, b in zip(top, bottom)) + (255,))
    return im


def star(d, cx, cy, r, inner, fill):
    pts = []
    for i in range(8):
        a = math.pi / 4 * i - math.pi / 2
        rr = r if i % 2 == 0 else inner
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=fill)


GEMINI = ROOT / 'datapack-src/pack-source/ref/gemini/icono_servidor.png'


def icon():
    """Arte de Gemini (14/11, pedido del dueno: 'hacela mas linda con gemini'); si falta, el dibujo propio."""
    if GEMINI.exists():
        art = Image.open(GEMINI).convert('RGBA')
        for corner in ((0, 0), (art.width - 1, 0), (0, art.height - 1), (art.width - 1, art.height - 1)):
            ImageDraw.floodfill(art, corner, (0, 0, 0, 0), thresh=40)   # esquinas blancas -> transparentes
        return art.resize((64, 64), Image.Resampling.LANCZOS)
    return drawn_icon()


def drawn_icon():
    rnd = random.Random(7)
    mask = Image.new('L', (S, S)); ImageDraw.Draw(mask).rounded_rectangle((6, 6, S - 7, S - 7), 46, fill=255)
    im = Image.new('RGBA', (S, S))
    bg = gradient((S, S), (14, 16, 48), (62, 28, 104))
    d = ImageDraw.Draw(bg)
    for _ in range(46):  # estrellas chicas
        x, y, r = rnd.randint(14, S - 14), rnd.randint(14, S - 14), rnd.choice((1, 1, 2))
        d.ellipse((x - r, y - r, x + r, y + r), fill=(220, 225, 255, rnd.randint(110, 230)))
    # Halo celeste detras de la letra.
    glow = Image.new('RGBA', (S, S)); ImageDraw.Draw(glow).ellipse((48, 70, 208, 230), fill=CYAN + (90,))
    bg.alpha_composite(glow.filter(ImageFilter.GaussianBlur(26)))
    im.paste(bg, (0, 0), mask)
    # Borde dorado biselado.
    rim = ImageDraw.Draw(im)
    rim.rounded_rectangle((6, 6, S - 7, S - 7), 46, outline=GOLD_DARK, width=12)
    rim.rounded_rectangle((9, 9, S - 10, S - 10), 43, outline=GOLD, width=5)
    # Letra A de piedra con contorno dorado y sombra.
    font = ImageFont.truetype('C:/Windows/Fonts/georgiab.ttf', 196)
    pos = (S // 2, 150)
    shadow = Image.new('RGBA', (S, S)); ImageDraw.Draw(shadow).text((pos[0] + 6, pos[1] + 8), 'A', font=font, anchor='mm', fill=(0, 0, 0, 170))
    im.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(5)))
    letter = Image.new('L', (S, S)); ImageDraw.Draw(letter).text(pos, 'A', font=font, anchor='mm', fill=255,
                                                               stroke_width=9, stroke_fill=255)
    im.paste(Image.new('RGBA', (S, S), GOLD_DARK + (255,)), (0, 0), letter)
    edge = Image.new('L', (S, S)); ImageDraw.Draw(edge).text(pos, 'A', font=font, anchor='mm', fill=255, stroke_width=5, stroke_fill=255)
    im.paste(Image.new('RGBA', (S, S), GOLD + (255,)), (0, 0), edge)
    core = Image.new('L', (S, S)); ImageDraw.Draw(core).text(pos, 'A', font=font, anchor='mm', fill=255)
    stone = gradient((S, S), (236, 238, 245), (128, 134, 150))
    sd = ImageDraw.Draw(stone)
    for _ in range(26):  # grietas de la piedra
        x, y = rnd.randint(40, 216), rnd.randint(60, 230)
        sd.line((x, y, x + rnd.randint(-14, 14), y + rnd.randint(6, 16)), fill=(96, 100, 116), width=2)
    im.paste(stone, (0, 0), core)
    # Cristal celeste en el hueco de la A.
    cd = ImageDraw.Draw(im)
    crystal = [(128, 98), (146, 132), (128, 150), (110, 132)]
    cd.polygon(crystal, fill=(70, 200, 240), outline=(220, 255, 255))
    cd.polygon([(128, 98), (146, 132), (128, 124)], fill=(170, 245, 255))
    # Estrella astral arriba a la derecha con brillo.
    sg = Image.new('RGBA', (S, S)); star(ImageDraw.Draw(sg), 200, 56, 30, 9, CYAN + (200,))
    im.alpha_composite(sg.filter(ImageFilter.GaussianBlur(6)))
    star(cd, 200, 56, 26, 7, (230, 252, 255))
    star(cd, 200, 56, 12, 4, (255, 255, 255))
    return im.resize((64, 64), Image.Resampling.LANCZOS)


def hexcode(rgb):
    return '§x' + ''.join('§' + c for c in '%02x%02x%02x' % rgb)


def blend(text, colors, bold=False):
    out = []
    for i, ch in enumerate(text):
        t = i / max(1, len(text) - 1) * (len(colors) - 1)
        a, b = colors[int(t)], colors[min(len(colors) - 1, int(t) + 1)]
        f = t - int(t)
        out.append(hexcode(tuple(round(x + (y - x) * f) for x, y in zip(a, b))) + ('§l' if bold else '') + ch)
    return ''.join(out)


# Linea 1: nombre con degrade celeste -> violeta -> dorado. Linea 2: lo que hay para hacer.
LINE1 = ('§r      ' + blend('✦ ', [(242, 194, 91)]) + blend('AstralRPG', [(127, 231, 255), (184, 106, 255), (242, 194, 91)], bold=True)
         + '§r' + blend(' ✦', [(242, 194, 91)]) + ' §8│ §7RPG sin mods')
# Minecraft muestra unos 45 caracteres por linea: mas largo se corta.
LINE2 = (' ' + hexcode((242, 194, 91)) + '⚔ §fMazmorras, jefes, mascotas '
         + hexcode((127, 231, 255)) + '✦ ¡Nuevo océano!')
MOTD = LINE1 + '\n' + LINE2


def properties_value():
    """motd escapado para server.properties (Java properties: \\n y unicode \\uXXXX)."""
    text = ''.join('\\n' if c == '\n' else (c if ord(c) < 128 else '\\u%04x' % ord(c)) for c in MOTD)
    # Java y el panel borran los espacios iniciales: LINE1 empieza con §r para que no lo sean.
    lead = len(text) - len(text.lstrip(' '))
    return '\\u0020' * lead + text[lead:]


def preview(ic):
    """Imitacion aproximada de la lista de servidores (sin la fuente real de Minecraft)."""
    W, H = 640, 96
    im = Image.new('RGBA', (W, H), (24, 22, 30, 255))
    im.alpha_composite(ic.resize((72, 72), Image.Resampling.NEAREST), (12, 12))
    font = ImageFont.truetype('C:/Windows/Fonts/seguisym.ttf', 17)
    bold = ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf', 17)
    d = ImageDraw.Draw(im)
    d.text((96, 10), 'AstralRPG', font=font, fill='white')
    for row, line in enumerate((LINE1, LINE2)):
        x, y, color, isbold = 96, 38 + row * 24, (170, 170, 170), False
        i = 0
        while i < len(line):
            if line[i] == '§':
                code = line[i + 1]
                if code == 'x':
                    color = tuple(int(line[i + 3 + k * 4] + line[i + 5 + k * 4], 16) for k in range(3)); i += 14; continue
                isbold = code == 'l' or (isbold and code not in 'r')
                color = {'f': (255, 255, 255), '7': (170, 170, 170), '8': (85, 85, 85), 'r': (170, 170, 170)}.get(code, color)
                i += 2; continue
            f = bold if isbold else font
            d.text((x, y), line[i], font=f, fill=color); x += d.textlength(line[i], font=f) * 0.92; i += 1
    d.text((W - 60, 10), '0/20', font=font, fill=(150, 150, 150))
    return im


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ic = icon()
    ic.save(OUT / 'server-icon.png')
    (OUT / 'motd.txt').write_text('motd=' + properties_value() + '\n', encoding='ascii')
    preview(ic).save(OUT / 'vista-previa-lista.png')
    ic.resize((256, 256), Image.Resampling.NEAREST).save(OUT / 'server-icon-grande.png')
    print(OUT)


if __name__ == '__main__':
    main()
