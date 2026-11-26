# -*- coding: utf-8 -*-
"""Ventana "Renacer en las Minas" (Minas Astrales) con el diseno del dueno (Gemini, 25/11/2026).

Referencia del dueno: .local/gemini/refs-25-11/renacer_ref.png; version limpia de Gemini (sin el numero del bonus):
.local/gemini/refs-25-11/renacer_gemini_v1.png (1024x1024). No van al repo; el fondo procesado si
(pack-source/arte-20-11/renacer.png).

- Cofre de 6 filas. Todo el dibujo va en el fondo; los botones RENACER / CANCELAR caen en la fila 6
  (RENACER casillas 45-48, CANCELAR 50-53) y ahi van items invisibles con nombre y lore.
- El "+N% -> +M%" del cuadro BONUS PERMANENTE cambia con los renacimientos: 10 glifos chicos
  (0xF4F0 + n, n = renacimientos actuales 0..9) que se pegan al titulo despues del fondo.

python ventana_renacer.py -> pack-source/arte-20-11/renacer.png + build/previews/ventana_renacer*.png
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

import ventanas_20_11 as V

HERE = Path(__file__).resolve().parent
GEMINI = HERE.parent / '.local/gemini/refs-25-11/renacer_gemini_v1.png'
K = V.K
FIN = 57 + 6 * 18 - 1      # ultima linea del cofre (164)
FONDO_GEMINI = (29, 34, 46)

# Lineas de casilleros medidas en la imagen de Gemini (px) -> lineas del juego (px de ventana)
_GX = [203.5, 270, 338.5, 405.5, 475, 544.5, 614, 683.5, 752.5, 819.5]
_S = (_GX[-1] - _GX[0]) / 162
GX = ([0] + _GX + [1024], [30.5 - _GX[0] / _S] + V._rejilla(31, 9) + [30.5 + (1024 - _GX[0]) / _S])
# Arriba: lineal hasta la primera linea del inventario (los botones caen justo en la fila 6).
GY = ([0, 694.5, 757, 821, 881, 901.5, 956, 1024],
      [0, FIN + 14.5, FIN + 32.5, FIN + 50.5, FIN + 68.5, FIN + 72.5, FIN + 90.5, FIN + 90.5 + 68 / _S])

# Numero del bonus: centro del cuadro vacio (px de ventana) y escala del texto
BONUS_CX, BONUS_CY, ESCALA = 111.5, 118.5, 1
BONUS_BASE = 0xF4F0        # 0xF4F0..0xF4F9 (renacimientos 0..9)
RENACER_MAX = 10
CREMA, ORO, CONTORNO = (255, 240, 205, 255), (240, 190, 70, 255), (26, 18, 8, 255)
SLOTS_RENACER = (45, 46, 47, 48)
SLOTS_CANCELAR = (50, 51, 52, 53)


def panel():
    ref = Image.open(GEMINI).convert('RGB')
    src = ref.filter(ImageFilter.GaussianBlur(0.9))
    im = V._deformar(src, GX, GY, (V.W * K, V._alto(6) * K))
    im = V._recorte_fondo(im, FONDO_GEMINI, tol=36)
    V._casillas(im, 31, FIN + 15, 3, (30, 33, 42, 255), (118, 118, 124, 255))
    V._casillas(im, 31, FIN + 73, 1, (30, 33, 42, 255), (118, 118, 124, 255))
    return im


# ------------------------------------------------------------------ numero del bonus
def _flecha():
    a = Image.new('RGBA', (7, 7))
    d = ImageDraw.Draw(a)
    d.line((0, 3, 5, 3), fill=ORO)
    d.line((3, 0, 6, 3), fill=ORO)
    d.line((3, 6, 6, 3), fill=ORO)
    return a


def _texto(caption, color):
    from escape_menu import text
    from guia_cofre import text_width
    w = text_width(caption)
    im = Image.new('RGBA', (w + 2, 10))
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        text(im, caption, (1 + w / 2 + dx, 1 + dy), color=CONTORNO)
    text(im, caption, (1 + w / 2, 1), color=color)
    return im


def bonus(n):
    """'+N% -> +M%' a 1x (con contorno); el glifo lo agranda ESCALA veces."""
    pct = round(n * 10)
    a, b = _texto(f'+{pct}%', CREMA), _texto(f'+{pct + 10}%', ORO)
    f = _flecha()
    sep = 5
    im = Image.new('RGBA', (a.width + sep + f.width + sep + b.width, 10))
    im.alpha_composite(a, (0, 0))
    im.alpha_composite(f, (a.width + sep, 1))
    im.alpha_composite(b, (a.width + sep + f.width + sep, 0))
    return im.crop(im.getbbox())


def bonus_glifos():
    """[(char, imagen_1x, alto_gui, ascent, x_izq_gui)] para n = 0..RENACER_MAX-1."""
    out = []
    for n in range(RENACER_MAX):
        im = bonus(n)
        alto = im.height * ESCALA
        top = round(BONUS_CY - alto / 2)
        x = round(BONUS_CX - im.width * ESCALA / 2)
        out.append((chr(BONUS_BASE + n), im, alto, 53 - top, x))
    return out


def bonus_providers():
    from services_ui import png
    files, providers = {}, []
    for ch, im, alto, ascent, _ in bonus_glifos():
        path = f'font/ventanas2011/renacer_bonus_{ord(ch) - BONUS_BASE}.png'
        files['assets/astral/textures/' + path] = png(im)
        providers.append(dict(type='bitmap', file='astral:' + path, height=alto, ascent=ascent, chars=[ch]))
    return files, providers


def _espacio(n):
    from guia_cofre import SHIFT
    s = ''
    for k in sorted(SHIFT, reverse=True):
        while n >= k:
            s += SHIFT[k]
            n -= k
    return s


def titulo(n):
    """Fondo + numero del bonus para un jugador con n renacimientos (el texto del titulo arranca en x = 31)."""
    from ventanas_19_11 import titulo as t
    ch, _, _, _, x = bonus_glifos()[min(n, RENACER_MAX - 1)]
    return t('renacer') + _espacio(x - 31) + ch


def preview(n=0):
    prev = Image.new('RGBA', (V.W * K, V._alto(6) * K), (60, 60, 60, 255))
    prev.alpha_composite(panel())
    _, im, alto, _, x = bonus_glifos()[n]
    g = im.resize((im.width * ESCALA * K, alto * K), Image.Resampling.NEAREST)
    prev.alpha_composite(g, (x * K, round(BONUS_CY - alto / 2) * K))
    return prev


if __name__ == '__main__':
    V.OUT.mkdir(parents=True, exist_ok=True)
    panel().save(V.OUT / 'renacer.png')
    out = HERE.parent / 'build/previews'
    out.mkdir(parents=True, exist_ok=True)
    for n in (0, 9):
        preview(n).save(out / f'ventana_renacer_{n}.png')
    print('ok')
