# -*- coding: utf-8 -*-
"""Ventana del /trade (AxTrade) con el diseno del dueno (Gemini, 23/11/2026): "Intercambio Astral".

Referencia (local, no va al repo): .local/gemini/refs-23-11/trade.webp (1448x1086).
- Cofre de 6 filas: fila 1 = estado y oro de cada lado; filas 2-6 = 4 columnas tuyas | divisor | 4 del otro.
- Los textos de la referencia que cambian (nombres, cantidades de oro, LISTO/ESPERANDO) se borran: los pone el
  juego (titulo de AxTrade y los items de confirmar / oro / estado).
- La cinta "Ambos deben confirmar" pasa a la derecha: a la izquierda el juego escribe "Inventario".

python ventana_trade.py -> pack-source/arte-20-11/trade.png (fondo a 2x) + piezas en pack-source/arte-23-11/
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import ventanas_20_11 as V

HERE = Path(__file__).resolve().parent
REF = HERE.parent / '.local/gemini/refs-23-11/trade.webp'
PIEZAS = HERE / 'pack-source/arte-23-11'
K = V.K
FIN = 57 + 6 * 18 - 1      # ultima linea del cofre (164)

# Lineas medidas en la referencia
FX = ([210, 288, 381, 477, 572, 667, 778, 871, 968, 1064, 1159, 1240],
      [16, 30.5, 48.5, 66.5, 84.5, 102.5, 120.5, 138.5, 156.5, 174.5, 192.5, 207.5])
IX = ([210] + [259, 361, 461, 566, 667, 773, 876, 980, 1082, 1184] + [1240],
      [16] + V._rejilla(31, 9) + [207.5])
# Cajas de la referencia
NOMBRE_IZQ = (333, 140, 450, 190)
NOMBRE_DER = (930, 140, 1128, 190)
CINTA = (505, 645, 945, 697)          # "Ambos deben confirmar"
PILL = {'tu_oferta': (390, 215, 531, 262), 'su_oferta': (748, 215, 879, 262)}
ICONOS = {'trade_listo': (252, 217, 301, 261), 'trade_oro': (541, 219, 585, 258), 'trade_esperando': (1055, 218, 1097, 260)}


def _fuente():
    im = Image.open(REF).convert('RGB')
    d = ImageDraw.Draw(im)
    # nombres fuera (los escribe el juego): relleno con el pergamino de al lado
    for caja in (NOMBRE_IZQ, NOMBRE_DER):
        x0, y0, x1, y1 = caja
        muestra = np.asarray(im.crop((x0, y0 + 6, x1, y0 + 12))).reshape(-1, 3)
        d.rectangle(caja, fill=tuple(int(v) for v in np.median(muestra, 0)))
    return im


def _icono(caja, gris=False):
    im = Image.open(REF).convert('RGBA').crop(caja)
    lado = max(im.size)
    sq = Image.new('RGBA', (lado, lado))
    sq.alpha_composite(im, ((lado - im.width) // 2, (lado - im.height) // 2))
    sq = sq.resize((32, 32), Image.Resampling.LANCZOS)
    if gris:
        a = np.asarray(sq).astype(float)
        g = a[..., :3].mean(-1, keepdims=True)
        a[..., :3] = g * 0.8 + 20
        sq = Image.fromarray(a.clip(0, 255).astype(np.uint8), 'RGBA')
    return sq


def piezas():
    out = {k: _icono(c) for k, c in ICONOS.items()}
    out['trade_confirmar'] = _icono(ICONOS['trade_listo'], gris=True)
    return out


GEMINI = HERE.parent / '.local/gemini/refs-23-11/trade_gemini.png'   # version limpia de Gemini (825x1024)
GX = ([8, 52, 130, 208, 288, 366, 458, 533, 611, 690, 768, 817],
      [20, 30.5, 48.5, 66.5, 84.5, 102.5, 120.5, 138.5, 156.5, 174.5, 192.5, 203])
GIX = ([8, 52, 131, 210, 291, 369, 449, 529, 608, 688, 768, 817], [20] + V._rejilla(31, 9) + [203])
G_PILL = {'tu_oferta': (138, 190, 317, 233), 'su_oferta': (511, 190, 688, 233)}
G_CINTA = (255, 605, 569, 646)
G_LINEA = (569, 612, 740, 640)       # linea dorada con la gema, a la derecha de la cinta


def panel():
    """Fondo a 2x desde la version limpia de Gemini (23/11)."""
    ref = Image.open(GEMINI).convert('RGB')
    src = ref.filter(ImageFilter.GaussianBlur(1.1))
    im = Image.new('RGBA', (V.W * K, V._alto(6) * K))
    V._banda(im, src, *GX, [0, 120, 170, 178], [2, 42, 55, 56.5])                 # cinta, escudo y carteles
    V._banda(im, src, *GX, [176, 186], [56.5, 74.5])                              # fila 1 (lisa)
    V._banda(im, src, *GX, [239, 311, 381, 452, 523, 594], [74.5, 92.5, 110.5, 128.5, 146.5, 164.5])
    V._banda(im, src, *GIX, [594, 600, 649, 655], [164.5, 165.5, 177.5, 178.5])
    V._banda(im, src, *GIX, [655, 728, 801, 873, 894, 970, 1024], [FIN + 14.5, FIN + 32.5, FIN + 50.5, FIN + 68.5,
                                                                    FIN + 72.5, FIN + 90.5, FIN + 104])
    im = V._recorte_fondo(im, (0, 0, 0), tol=40)
    d = ImageDraw.Draw(im)
    # fuera del marco (la deformacion repite el borde): transparente
    d.rectangle((0, 0, 19 * K - 1, im.height), fill=(0, 0, 0, 0))
    d.rectangle((205 * K, 0, im.width, im.height), fill=(0, 0, 0, 0))
    rgba = ref.convert('RGBA')
    # fila 1: carteles TU OFERTA / SU OFERTA en sus 2 casillas; marcos dorados donde van los items
    for clave, slot in (('tu_oferta', 1), ('su_oferta', 6)):
        p = rgba.crop(G_PILL[clave]).resize((35 * K, 16 * K), Image.Resampling.LANCZOS)
        im.alpha_composite(p, ((31 + 18 * slot) * K, 57 * K))
    for slot in (0, 3, 5, 8):
        x = (31 + 18 * slot) * K
        d.rounded_rectangle((x - K, 56 * K, x + 17 * K - 1, 74 * K - 1), 3, fill=(38, 37, 40, 255),
                            outline=(201, 161, 79, 255), width=K)
    # banda del inventario: la cinta (vacia) a la izquierda, ahi escribe el juego "Inventario"; a la derecha la linea dorada
    y0, y1 = 165 * K, 178 * K
    fondo = im.crop((24 * K, y0, 25 * K, y1))
    for x in range(26 * K, 198 * K):
        im.paste(fondo, (x, y0))
    cinta = rgba.crop(G_CINTA).resize((74 * K, 11 * K), Image.Resampling.LANCZOS)
    im.alpha_composite(cinta, (28 * K, (FIN + 3) * K))
    linea = rgba.crop(G_LINEA).resize((88 * K, 7 * K), Image.Resampling.LANCZOS)
    im.alpha_composite(linea, (106 * K, (FIN + 5) * K))
    return im


# Titulo: fondo + "Vos" en el cartel izquierdo + el nombre del otro (%player% de AxTrade) en el derecho.
def titulo():
    from ventanas_19_11 import titulo as t
    from guia_cofre import SHIFT, text_width

    def espacio(n):
        s = ''
        for k in sorted(SHIFT, reverse=True):
            while n >= k:
                s += SHIFT[k]
                n -= k
        return s
    izq, der = 35, 139          # x del texto en la ventana; el titulo del juego arranca en x = 31
    return t('trade') + espacio(izq - 31) + '&#3b2412Vos' + espacio(der - izq - text_width('Vos')) + '&#3b2412%player%'


if __name__ == '__main__':
    V.OUT.mkdir(parents=True, exist_ok=True)
    panel().save(V.OUT / 'trade.png')
    PIEZAS.mkdir(parents=True, exist_ok=True)
    for k, im in piezas().items():
        im.save(PIEZAS / f'{k}.png')
    prev = Image.new('RGBA', (V.W * K, V._alto(6) * K), (60, 60, 60, 255))
    prev.alpha_composite(panel())
    prev.save(HERE.parent / 'build/previews/ventana_trade.png')
    print('ok')
