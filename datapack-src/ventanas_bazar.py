# -*- coding: utf-8 -*-
"""Ventanas del Bazar (AstralBazar) con los disenos Gemini del dueno (25/11/2026).

Referencias (privadas, no van al repo): .local/gemini/refs-25-11/bazar/concepto_{1,2,3}.webp
  1 = Categorias, Productos, Producto      2 = Cantidad, Precio, Confirmar orden, Orden
  3 = Mis ordenes, Retiros, Vender equipo, Confirmar equipo

Cada ventana se arma sobre la grilla exacta del cofre (como ventanas_20_11.py, K=2, W=224):
bandas del dibujo deformadas a las filas del cofre (titulo, filas de casilleros, fila de botones, borde)
y, donde el concepto no coincide con la grilla, piezas recortadas (tarjetas y botones) puestas encima.
Lo que cambia (nombre, precio, pagina, total) no se dibuja: va en el nombre/lore del item del plugin.
Los botones dibujados se atrapan con items invisibles en los casilleros de BOTONES (abajo).

python ventanas_bazar.py -> pack-source/arte-bazar/<ventana>.png + build/previews/bazar_<ventana>.png
"""
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import ventanas_20_11 as V

HERE = Path(__file__).resolve().parent
REF = HERE.parent / '.local/gemini/refs-25-11/bazar'
OUT = HERE / 'pack-source/arte-bazar'
K, W = V.K, V.W
GX = V._rejilla(31, 9)          # 30.5 .. 192.5
TOP = 56.5                      # linea de arriba de la fila 0
FONDO = {1: (18, 16, 23), 2: (21, 20, 26), 3: (19, 17, 22)}

# Filas de cada ventana (el plugin abre el cofre con estas filas)
FILAS = {'categorias': 6, 'productos': 6, 'producto': 6, 'cantidad': 5, 'precio': 5, 'confirmar_orden': 5,
         'orden': 5, 'mis_ordenes': 6, 'retiros': 6, 'vender_equipo': 6, 'confirmar_equipo': 6}


@lru_cache(None)
def ref(n):
    im = Image.open(REF / f'concepto_{n}.webp').convert('RGBA')
    return im.filter(ImageFilter.GaussianBlur(0.45))


def fila(r):
    return TOP + 18 * r


class Mapa:
    """Lineas de la grilla del concepto (x) -> lineas del juego. Fuera de la grilla, misma escala
    (estirada si hace falta para tapar la textura vanilla de 22 a 201)."""

    def __init__(self, lineas, xl, xr):
        s = 18 / ((lineas[-1] - lineas[0]) / 9)
        self.s = s
        izq = min(30.5 - (lineas[0] - xl) * s, 22)
        der = max(192.5 + (xr - lineas[-1]) * s, 201)
        self.src = [xl] + list(lineas) + [xr]
        self.dst = [izq] + GX + [der]

    def x(self, xs):
        return float(np.interp(xs, self.src, self.dst))

    def par(self):
        return (self.src, self.dst)


def lin(x0, paso):
    return [x0 + paso * k for k in range(10)]


def banda(im, n, m, ysrc, ydst):
    """Pega la banda ysrc del concepto deformada a ydst (px de ventana)."""
    y0, y1 = ydst[0], ydst[-1]
    alto = round((y1 - y0) * K)
    if alto <= 0:
        return
    parte = V._deformar(ref(n), m.par(), (list(ysrc), [y - y0 for y in ydst]), (W * K, alto))
    d = ImageDraw.Draw(parte)
    d.rectangle((0, 0, round(m.dst[0] * K) - 1, alto), fill=(0, 0, 0, 0))
    d.rectangle((round(m.dst[-1] * K), 0, W * K, alto), fill=(0, 0, 0, 0))
    im.alpha_composite(parte, (0, round(y0 * K)))


def titulo(im, n, m, y_top, y_grilla):
    """Cabecera: del borde de arriba del marco a la primera linea de la grilla, a la escala del marco."""
    banda(im, n, m, (y_top, y_grilla), (min(TOP - (y_grilla - y_top) * m.s, 36), TOP))


def borde(im, n, m, filas, y0, y1, tope=11):
    alto = min((y1 - y0) * m.s, tope)
    banda(im, n, m, (y0, y1), (fila(filas), fila(filas) + alto))


def liso(im, n, m, ysrc, r0, r1):
    """Filas r0..r1-1 con una franja lisa del concepto (marco a los costados, fondo adentro)."""
    banda(im, n, m, ysrc, (fila(r0), fila(r1)))


def pieza(n, caja, borrar=(), mover=()):
    """Recorte del concepto. borrar: [(caja, punto_color)] se tapa con ese color;
    mover: [(caja, dy)] se corre esa franja dy px (despues de borrar)."""
    im = ref(n).crop(caja).copy()
    x0, y0 = caja[0], caja[1]
    for (a, b, c, d), (px, py) in borrar:
        col = ref(n).getpixel((px, py))
        ImageDraw.Draw(im).rectangle((a - x0, b - y0, c - x0 - 1, d - y0 - 1), fill=col)
    for (a, b, c, d), dy, *dx in mover:
        dx = dx[0] if dx else 0
        franja = im.crop((a - x0, b - y0, c - x0, d - y0))
        col = ref(n).getpixel(dx and (c + 4, b + 3) or (a - 2, b + 2))
        ImageDraw.Draw(im).rectangle((a - x0, b - y0, c - x0 - 1, d - y0 - 1), fill=col)
        im.alpha_composite(franja, (round(a - x0 + dx), round(b - y0 + dy)))
    return im


def poner(im, p, rect, estirar=1.0):
    """Pega p dentro de rect (px de ventana) sin deformar (o estirando a lo ancho hasta 'estirar')."""
    x0, y0, x1, y1 = rect
    w, h = (x1 - x0) * K, (y1 - y0) * K
    esc = min(w / (p.width * estirar), h / p.height)
    tw, th = min(w, p.width * esc * estirar), p.height * esc
    q = p.resize((round(tw), round(th)), Image.Resampling.LANCZOS)
    im.alpha_composite(q, (round(x0 * K + (w - q.width) / 2), round(y0 * K + (h - q.height) / 2)))
    return ((x0 * K + (w - q.width) / 2) / K, (x0 * K + (w + q.width) / 2) / K)


def celdas(im, n, caja, slots):
    """Casillero vacio recortado del concepto (de linea a linea), repetido en esos casilleros."""
    c = ref(n).crop(caja).resize((18 * K, 18 * K), Image.Resampling.LANCZOS)
    for s in slots:
        im.alpha_composite(c, (round((30.5 + 18 * (s % 9)) * K), round((TOP + 18 * (s // 9)) * K)))


def marco_slot(im, slot, oro=(214, 170, 84, 255), fondo=(26, 24, 32, 255)):
    x, y = 30.5 + 18 * (slot % 9), TOP + 18 * (slot // 9)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle(((x - 2) * K, (y - 2) * K, (x + 20) * K - 1, (y + 20) * K - 1), 3, fill=(40, 30, 18, 255),
                        outline=oro, width=2)
    d.rectangle(((x + 1) * K, (y + 1) * K, (x + 17) * K - 1, (y + 17) * K - 1), fill=fondo)


def texto(im, lineas, cx, cy, color=(236, 226, 205, 255), sombra=(30, 22, 12, 255)):
    """Texto con la fuente del juego a 1x (px de ventana), centrado."""
    from escape_menu import text
    capa = Image.new('RGBA', (W, 400))
    alto = 10 * len(lineas)
    for i, t in enumerate(lineas):
        y = round(cy - alto / 2 + 10 * i + 1)
        text(capa, t, (round(cx), y), color=color)
    capa = capa.crop((0, 0, W, im.height // K)).resize((im.width, im.height), Image.Resampling.NEAREST)
    im.alpha_composite(capa)


def lienzo(kind):
    return Image.new('RGBA', (W * K, V._alto(FILAS[kind]) * K))


def recortar(im, n):
    return V._recorte_fondo(im, FONDO[n], tol=30)


# ================================================================== concepto 1
M_CAT = Mapa(lin(22.9, 51.42), 10, 506)
CAT_TARJETAS = [(31, 275, 120, 395), (126, 275, 210, 395), (216.5, 275, 302.5, 395), (310, 275, 395, 395),
                (401.5, 275, 486, 395)]
CAT_BOTONES = [(34, 589, 140, 664), (149, 589, 254, 664), (264, 589, 371.5, 664), (382.5, 589, 483.5, 664)]


def categorias():
    im, m = lienzo('categorias'), M_CAT
    titulo(im, 1, m, 135, 205.5)
    banda(im, 1, m, (205.5, 256.1), (fila(0), fila(1)))
    liso(im, 1, m, (260, 271), 1, 3)
    banda(im, 1, m, (411.8, 465.3), (fila(3), fila(4)))
    liso(im, 1, m, (260, 271), 4, 6)
    paso = 162 / 5
    for k, c in enumerate(CAT_TARJETAS):
        x = 30.5 + paso * k
        poner(im, pieza(1, c), (x + 1, fila(1) + 1, x + paso - 1, fila(3) - 1))
    paso = 162 / 4
    for k, c in enumerate(CAT_BOTONES):
        x = 30.5 + paso * k
        poner(im, pieza(1, c), (x + 1, fila(4) + 2, x + paso - 1, fila(6) - 2))
    borde(im, 1, m, 6, 670, 698)
    return recortar(im, 1)


M_PROD = Mapa(lin(536.1, 51.42), 519, 1019)


def _caja_pagina(im, n, caja, col, fila_r, borrar):
    p = pieza(n, caja, borrar=borrar)
    x = 30.5 + 18 * col
    poner(im, p, (x - 5, fila(fila_r) - 1, x + 23, fila(fila_r + 1) + 1))


def productos():
    im, m = lienzo('productos'), M_PROD
    titulo(im, 1, m, 135, 203.5)
    for r in range(4):
        banda(im, 1, m, (507.6, 562.4), (fila(r), fila(r + 1)))
    liso(im, 1, m, (568, 584), 4, 6)
    poner(im, pieza(1, (544, 591, 636, 662)), (31, fila(4) + 2, 66, fila(6) - 2))              # Volver
    poner(im, pieza(1, (671, 601, 720, 648)), (84.5, fila(5), 102.5, fila(6)))                  # anterior
    _caja_pagina(im, 1, (728, 601, 812, 648), 4, 5, [((738, 608, 802, 641), (733, 624))])       # pagina
    poner(im, pieza(1, (819, 601, 868, 648)), (120.5, fila(5), 138.5, fila(6)))                 # siguiente
    poner(im, pieza(1, (902, 591, 995, 662)), (157, fila(4) + 2, 192, fila(6) - 2))             # Cerrar
    borde(im, 1, m, 6, 668, 698)
    return recortar(im, 1)


M_PRODUCTO = Mapa(lin(1054.0, 49.67), 1032, 1526)
# precio de los botones al instante: se borra y el texto baja al medio
_INST = {'comprar': ((1054, 487, 1270.5, 535.5), (1110, 510, 1266, 532), (1112, 489, 1266, 511), (1140, 520)),
         'vender': ((1285, 487, 1503, 535.5), (1330, 510, 1499, 532), (1330, 489, 1499, 511), (1480, 520))}


def _instante(k):
    caja, precio, linea, color = _INST[k]
    return pieza(1, caja, borrar=[(precio, color)], mover=[(linea, 10)])


def producto():
    im, m = lienzo('producto'), M_PRODUCTO
    titulo(im, 1, m, 135, 192)
    liso(im, 1, m, (603, 613), 0, 1)
    banda(im, 1, m, (330.5, 379.5), (fila(1), fila(2)))
    banda(im, 1, m, (419.2, 468.8), (fila(2), fila(3)))
    liso(im, 1, m, (603, 613), 3, 6)
    marco_slot(im, 4)
    # iconos de las filas: carrito (compras) y etiqueta (ventas) en la primera casilla
    poner(im, pieza(1, (1060, 490, 1106, 532)), (32.5, fila(1) + 2, 46.5, fila(2) - 2))
    poner(im, pieza(1, (1291, 490, 1335, 532)), (32.5, fila(2) + 2, 46.5, fila(3) - 2))
    poner(im, _instante('comprar'), (30.5, fila(3) + .5, 102.5, fila(4) - .5), estirar=1.15)
    poner(im, _instante('vender'), (120.5, fila(3) + .5, 192.5, fila(4) - .5), estirar=1.15)
    poner(im, pieza(1, (1054, 548, 1270.5, 599.5)), (30.5, fila(4) + .5, 102.5, fila(5) - .5), estirar=1.15)
    poner(im, pieza(1, (1285, 548, 1503, 599.5)), (120.5, fila(4) + .5, 192.5, fila(5) - .5), estirar=1.15)
    poner(im, pieza(1, (1053.5, 617.5, 1216, 662.5)), (30.5, fila(5) + .5, 84.5, fila(6) - .5), estirar=1.1)
    poner(im, pieza(1, (1226.5, 617.5, 1347.5, 662.5)), (84.5, fila(5) + .5, 138.5, fila(6) - .5), estirar=1.1)
    poner(im, pieza(1, (1369, 617.5, 1503.5, 662.5)), (138.5, fila(5) + .5, 192.5, fila(6) - .5), estirar=1.1)
    borde(im, 1, m, 6, 665, 702)
    return recortar(im, 1)


# ================================================================== concepto 2 (4 filas de grilla + botones)
C2 = {'cantidad': (Mapa([44.7, 123.1, 199.0, 276.5, 351.0, 427.0, 502.0, 574.0, 653.1, 733.6], 36, 756),
                   (106, 180.5), [180.5, 253.3, 325.4, 396.9, 455.2], (449, 521), (521, 538)),
      'precio': (Mapa([797.1, 877.9, 953.4, 1028.9, 1104.1, 1183.9, 1259.4, 1334.9, 1411.0, 1492.6], 786, 1506),
                 (106, 179.8), [179.8, 253.8, 325.5, 397.1, 454.7], (449, 521), (521, 538)),
      'confirmar_orden': (Mapa([44.9, 123.1, 199.1, 275.5, 351.0, 427.0, 501.6, 576.4, 654.4, 733.4], 36, 756),
                          (553, 628.3), [628.3, 701.5, 773.2, 845.0, 899.0], (893, 970), (970, 988)),
      'orden': (Mapa([803.3, 879.4, 953.6, 1029.0, 1104.1, 1183.9, 1259.5, 1336.2, 1411.5, 1485.9], 786, 1506),
                (553, 627.7), [627.7, 700.9, 773.1, 844.9, 899.0], (893, 970), (970, 988))}
# contenido de los recuadros de confirmar/orden: se borra y queda un casillero para el item + texto fijo
C2_RECUADRO = {'confirmar_orden': ((134, 668, 650, 860), (128, 760)),
               'orden': ((902, 668, 1418, 860), (896, 760))}
C2_TEXTO = {'confirmar_orden': ['Revisa la orden', 'en el item:', 'cantidad, precio', 'e impuesto.'],
            'orden': ['Pasa el mouse', 'por el item:', 'avance, plata', 'e impuesto.']}


def concepto2(kind):
    m, cab, filas_y, botones, abajo = C2[kind]
    im = lienzo(kind)
    titulo(im, 2, m, *cab)
    banda(im, 2, m, filas_y, [fila(r) for r in range(5)])
    if kind in C2_RECUADRO:
        (a, b, c, d), col = C2_RECUADRO[kind]
        # se tapa el contenido en la imagen deformada: el recuadro cubre filas 0-3, columnas ~1-8
        xa, xc = m.x(a), m.x(c)
        ya = float(np.interp(b, filas_y, [fila(r) for r in range(5)]))
        yc = float(np.interp(d, filas_y, [fila(r) for r in range(5)]))
        colr = ref(2).getpixel(col)
        ImageDraw.Draw(im).rectangle((xa * K, ya * K, xc * K, yc * K), fill=colr)
        marco_slot(im, 20)
        texto(im, C2_TEXTO[kind], (73 + xc) / 2, fila(2))
    banda(im, 2, m, botones, (fila(4), fila(5)))
    borde(im, 2, m, 5, *abajo)
    return recortar(im, 2)


# ================================================================== concepto 3 (6 filas de grilla + botones)
M_MIS = Mapa([80.4, 149.6, 219.9, 289.6, 359.0, 428.0, 497.7, 567.5, 635.4, 704.5], 40, 745)
M_RET = Mapa([828.7, 899.5, 968.9, 1039.1, 1109.5, 1180.4, 1251.5, 1321.5, 1386.6, 1454.3], 790, 1503)
Y3 = [139.9, 199.5, 255.5, 309.4, 362.0, 412.5, 460.5]


def _filas3(im, n, m, ys, src_rows):
    for r, s in enumerate(src_rows):
        banda(im, n, m, (ys[s], ys[s + 1]), (fila(r), fila(r + 1)))


def mis_ordenes():
    im, m = lienzo('mis_ordenes'), M_MIS
    titulo(im, 3, m, 80, 139.9)
    _filas3(im, 3, m, Y3, [2, 3, 4, 5, 2])
    banda(im, 3, m, (466, 531), (fila(5), fila(6)))
    borde(im, 3, m, 6, 531, 548)
    # se borra el "1 / 2" (la pagina va en el nombre de las flechas)
    a, b = m.x(380), m.x(447)
    ImageDraw.Draw(im).rectangle((a * K, (fila(5) + 3) * K, b * K, (fila(6) - 3) * K), fill=ref(3).getpixel((378, 500)))
    return recortar(im, 3)


def retiros():
    im, m = lienzo('retiros'), M_RET
    titulo(im, 3, m, 80, 139.9)
    _filas3(im, 3, m, Y3, [1, 2, 3, 4, 5])
    banda(im, 3, m, (466, 531), (fila(5), fila(6)))
    borde(im, 3, m, 6, 531, 548)
    a, b = m.x(1093), m.x(1196)
    ImageDraw.Draw(im).rectangle((a * K, (fila(5) + 2) * K, b * K, (fila(6) - 2) * K), fill=ref(3).getpixel((1090, 500)))
    celdas(im, 3, (968.9, 255.5, 1039.1, 309.4), [49])
    return recortar(im, 3)


M_VEND = Mapa([93.3, 165.5, 236.6, 307.6, 379.0, 451.1, 520.4, 590.5, 660.1, 729.4], 40, 772)
YV = [616.6, 675.5, 729.5, 783.4, 838.6, 894.5]


def vender_equipo():
    im, m = lienzo('vender_equipo'), M_VEND
    titulo(im, 3, m, 557, 616.6)
    _filas3(im, 3, m, YV, [1, 1, 2, 3, 4])
    banda(im, 3, m, (905, 985), (fila(5), fila(6)))
    borde(im, 3, m, 6, 985, 1002)
    # "Vender por $24.000" -> "Vender" centrado (el monto va en el nombre del boton)
    boton = pieza(3, (228, 922, 594, 978), borrar=[((405, 930, 572, 970), (578, 950))], mover=[((255, 930, 405, 972), 0, 82)])
    poner(im, boton, (m.x(228), fila(5), m.x(594), fila(6)), estirar=1.2)
    return recortar(im, 3)


M_CONF = Mapa([864.6, 930.6, 993.3, 1062.7, 1133.0, 1198.3, 1257.3, 1319.4, 1381.9, 1440.7], 818, 1488)
YC = [619.7, 673.5, 720.4, 763.4]


def confirmar_equipo():
    im, m = lienzo('confirmar_equipo'), M_CONF
    titulo(im, 3, m, 557, 619.7)
    _filas3(im, 3, m, YC, [1, 1, 2])
    liso(im, 3, m, (903, 916), 3, 5)
    poner(im, pieza(3, (976, 812, 1323, 845)), (40, fila(3) + 3, 183, fila(4) - 3))
    poner(im, pieza(3, (953, 853, 1351, 901)), (40, fila(4) + 1, 183, fila(5) - 1))
    banda(im, 3, m, (913, 983), (fila(5), fila(6)))
    borde(im, 3, m, 6, 983, 1002)
    return recortar(im, 3)


VENTANAS = {'categorias': categorias, 'productos': productos, 'producto': producto,
            'cantidad': lambda: concepto2('cantidad'), 'precio': lambda: concepto2('precio'),
            'confirmar_orden': lambda: concepto2('confirmar_orden'), 'orden': lambda: concepto2('orden'),
            'mis_ordenes': mis_ordenes, 'retiros': retiros, 'vender_equipo': vender_equipo,
            'confirmar_equipo': confirmar_equipo}


def preview(kind, im):
    """Sobre una ventana vanilla gris aproximada (para ver como queda)."""
    filas = FILAS[kind]
    prev = Image.new('RGBA', im.size, (40, 40, 40, 255))
    d = ImageDraw.Draw(prev)
    top = 39
    d.rectangle((23 * K, top * K, 199 * K, (fila(filas) + 97) * K), fill=(198, 198, 198, 255))
    for r in range(3):
        for c in range(9):
            x, y = 30.5 + 18 * c, fila(filas) + 14 + 18 * r
            d.rectangle((x * K, y * K, (x + 18) * K - 1, (y + 18) * K - 1), fill=(139, 139, 139, 255), outline=(55, 55, 55, 255))
    for c in range(9):
        x, y = 30.5 + 18 * c, fila(filas) + 72
        d.rectangle((x * K, y * K, (x + 18) * K - 1, (y + 18) * K - 1), fill=(139, 139, 139, 255), outline=(55, 55, 55, 255))
    prev.alpha_composite(im)
    return prev


if __name__ == '__main__':
    import sys
    OUT.mkdir(parents=True, exist_ok=True)
    out = HERE.parent / 'build/previews'
    out.mkdir(parents=True, exist_ok=True)
    for kind in (sys.argv[1:] or VENTANAS):
        im = VENTANAS[kind]()
        im.save(OUT / f'{kind}.png')
        preview(kind, im).save(out / f'bazar_{kind}.png')
        print('ok', kind)


# ================================================================== glifos (titulo de cada ventana)
ORDEN = list(FILAS)
BASE = 0xF600                   # 16 caracteres por ventana: 0xF600 .. 0xF6AF


def tiles(kind):
    """Fondo partido en pedazos de 112x112 de ventana (224 px de imagen, el juego no carga mas de 256).
    [(char_glifo, char_vuelta, imagen, alto_gui, ascent, x_gui, avance)] como ventanas_19_11._tiles_hd."""
    im = Image.open(OUT / f'{kind}.png').convert('RGBA')
    base = BASE + 16 * ORDEN.index(kind)
    alto = im.height // K
    filas = [(0, 56)] + [(y, min(y + 112, alto)) for y in range(56, alto, 112)]
    out, t = [], 0
    for y0, y1 in filas:
        for x0 in (0, 112):
            p = im.crop((x0 * K, y0 * K, (x0 + 112) * K, y1 * K))
            caja = p.getbbox()
            if caja:
                avance = -(-caja[2] // K) + 1
                out.append((chr(base + t), chr(base + 8 + t), p, y1 - y0, 53 - y0, x0, avance))
            t += 1
    assert t <= 8
    return out


def titulo_ventana(kind):
    from ventanas_19_11 import START, END, ADELANTE_112
    s = ''.join((ADELANTE_112 if x0 else '') + g + v for g, v, _, _, _, x0, _ in tiles(kind))
    return '§f' + START + s + END


def assets():
    """Archivos del pack y providers de la fuente default para las 11 ventanas."""
    from services_ui import png
    files, prov = {}, []
    for kind in ORDEN:
        for i, (g, v, p, alto, ascent, x0, avance) in enumerate(tiles(kind)):
            path = f'font/bazar/{kind}_{i}.png'
            files['assets/astral/textures/' + path] = png(p)
            prov.append(dict(type='bitmap', file='astral:' + path, height=alto, ascent=ascent, chars=[g]))
            prov.append(dict(type='space', advances={v: -(avance + x0)}))
    return files, prov
