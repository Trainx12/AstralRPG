# -*- coding: utf-8 -*-
"""Ventanas del 20/11/2026 con disenos de Gemini (refs del dueno): Comisiones (Cavernas) y Subastas y Banco.

El diseno entero se lleva a la grilla del juego a doble resolucion (448 de ancho): cada linea de casilleros del
dibujo cae justo sobre la del juego (deformacion por tramos), las tarjetas de comisiones se vacian (lo de adentro
son items que cambian) y la tira de 'Inventario' queda clara para que se lea el texto del juego.

Fuentes (no van al repo, son locales): .local/gemini/refs-20-11/gemini/*.jpg
Resultado (va al repo): pack-source/arte-20-11/<ventana>.png  ->  `python ventanas_20_11.py` los regenera.
ventanas_19_11.assets() los usa como fondo de 'comisiones' y 'subastas_inicio'.
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / '.local/gemini/refs-20-11/gemini'
OUT = HERE / 'pack-source/arte-20-11'
K = 2            # resolucion: 2 pixeles de imagen por pixel de la ventana
W = 224


def _alto(filas):
    return 57 + filas * 18 + 115


def _rejilla(x0, n):
    """Centros de las lineas de casilleros del juego (en pixeles de ventana): x0 = primera casilla."""
    return [x0 - 0.5 + 18 * i for i in range(n + 1)]


def _mapa(src_pts, dst_pts, tam_dst):
    """Para cada pixel destino (a K), la coordenada fuente por interpolacion lineal por tramos."""
    d = np.arange(tam_dst) + 0.5
    return np.interp(d, np.array(dst_pts) * K, np.array(src_pts, dtype=float))


def _deformar(src, xs, ys, size):
    """src -> imagen size (a K). xs/ys: (puntos_fuente, puntos_destino_en_px_de_ventana)."""
    a = np.asarray(src.convert('RGBA')).astype(np.float32)
    mx = _mapa(*xs, size[0])
    my = _mapa(*ys, size[1])
    # muestreo bilineal
    x0 = np.clip(np.floor(mx - 0.5).astype(int), 0, a.shape[1] - 2); fx = np.clip(mx - 0.5 - x0, 0, 1)
    y0 = np.clip(np.floor(my - 0.5).astype(int), 0, a.shape[0] - 2); fy = np.clip(my - 0.5 - y0, 0, 1)
    # reduccion grande (~4x): se suaviza antes para no perder detalle de forma ruidosa
    ax = a[np.ix_(y0, x0)] * ((1 - fy)[:, None, None] * (1 - fx)[None, :, None])
    ax += a[np.ix_(y0, x0 + 1)] * ((1 - fy)[:, None, None] * fx[None, :, None])
    ax += a[np.ix_(y0 + 1, x0)] * (fy[:, None, None] * (1 - fx)[None, :, None])
    ax += a[np.ix_(y0 + 1, x0 + 1)] * (fy[:, None, None] * fx[None, :, None])
    return Image.fromarray(np.clip(ax, 0, 255).astype(np.uint8), 'RGBA')


def _fuente(nombre, radio=1.6):
    im = Image.open(SRC / f'{nombre}.jpg').convert('RGB')
    return im.filter(ImageFilter.GaussianBlur(radio))   # antialias antes de achicar ~4x


def _banda(dst, src, x_src, x_dst, y_src, y_dst):
    """Pega en dst la banda vertical y_dst (px de ventana) deformada desde src."""
    y0, y1 = y_dst[0], y_dst[-1]
    alto = round((y1 - y0) * K)
    parte = _deformar(src, (x_src, x_dst), (y_src, [y - y0 for y in y_dst]), (W * K, alto))
    dst.alpha_composite(parte, (0, round(y0 * K)))


def _recorte_fondo(im, color_fondo, tol=38):
    """Lo que queda fuera del marco (fondo liso del dibujo) pasa a transparente."""
    a = np.asarray(im).copy()
    dif = np.abs(a[..., :3].astype(int) - np.array(color_fondo)).sum(-1)
    fuera = dif < tol
    # solo el fondo conectado con el borde de la imagen
    m = Image.fromarray((fuera * 255).astype(np.uint8), 'L').copy()
    h, w = fuera.shape
    for x, y in [(x, 0) for x in range(0, w, 4)] + [(x, h - 1) for x in range(0, w, 4)] + \
                [(0, y) for y in range(0, h, 4)] + [(w - 1, y) for y in range(0, h, 4)]:
        if m.getpixel((x, y)) == 255:
            ImageDraw.floodfill(m, (x, y), 128)
    mascara = np.asarray(m) == 128
    a[mascara, 3] = 0
    return Image.fromarray(a, 'RGBA')


def _tira_inventario(im, fin_cofre, relleno, borde):
    """Tira clara bajo el cofre: ahi el juego escribe 'Inventario' en gris oscuro."""
    d = ImageDraw.Draw(im)
    y = (fin_cofre + 4) * K
    d.rounded_rectangle((30 * K, y, 193 * K - 1, y + 10 * K - 1), 3, fill=relleno, outline=borde, width=2)


def _casillas(im, x0, y0, filas, oscuro, linea):
    """Repinta las casillas exactas (16x16 interior) por si la deformacion dejo bordes corridos."""
    d = ImageDraw.Draw(im)
    for r in range(filas):
        for c in range(9):
            x, y = (x0 + 18 * c) * K, (y0 + 18 * r) * K
            d.rectangle((x - K, y - K, x + 17 * K - 1, y + 17 * K - 1), outline=linea, width=K)
            d.rectangle((x, y, x + 16 * K - 1, y + 16 * K - 1), fill=oscuro)


# ------------------------------------------------------------------ Comisiones (6 filas)
# Lineas medidas en el dibujo (px de la imagen de Gemini 1952x2206).
C_INV_X = [346, 487, 627, 769, 912, 1052, 1193, 1338, 1480, 1623]
C_INV_Y = [1345, 1476, 1609, 1740]
C_HOT_Y = [1785, 1916]
C_MARCO_X = (120, 1832)      # borde de roca exterior (sin los cristales que sobresalen)
C_CARTAS_X = [338, 769, 796, 1222, 1249, 1671]
C_CARTAS_Y = (493, 1062)


def comisiones():
    src = _fuente('comisiones_v1')
    alto = _alto(6)
    im = Image.new('RGBA', (W * K, alto * K))
    fin = 57 + 6 * 18 - 1       # 164: linea bajo la ultima fila del cofre
    # X: marco exterior 8..216, tarjetas en columnas 0-2 / 3-5 / 6-8 (30..192)
    gx = _rejilla(31, 9)
    x_cartas = ([0, C_MARCO_X[0]] + C_CARTAS_X + [C_MARCO_X[1], 1952],
                [-4, 8, gx[0], gx[3] - 1, gx[3] + 1, gx[6] - 1, gx[6] + 1, gx[9], 216, 228])
    x_inv = ([0, C_MARCO_X[0]] + C_INV_X + [C_MARCO_X[1], 1952], [-4, 8] + gx + [216, 228])
    # Y por tramos: cabecera, tarjetas (filas 0-4), '3 POR DIA' (fila 5), tira, inventario, barra rapida, pie
    _banda(im, src, *x_cartas, [0, 470, C_CARTAS_Y[0], C_CARTAS_Y[1], 1082, 1211, 1240],
           [0, 50, 55.5, 146.5, 147, 164, 166])
    _banda(im, src, *x_inv, [1240, 1345], [166, fin + 14])
    _banda(im, src, *x_inv, C_INV_Y + C_HOT_Y + [2060, 2206],
           [fin + 14, fin + 32, fin + 50, fin + 68, fin + 72, fin + 90, fin + 104, fin + 116])
    im = _recorte_fondo(im, (24, 17, 33))
    d = ImageDraw.Draw(im)
    # Vaciar las tarjetas: lo de adentro (cartel, cristal, barra, premio) son items del plugin.
    for i in range(3):
        x0, x1 = (gx[3 * i] + 3.5) * K, (gx[3 * i + 3] - 3.5) * K
        d.rounded_rectangle((x0, 60 * K, x1, 142 * K), 4, fill=(33, 24, 44, 255))
        d.rounded_rectangle((x0, 60 * K, x1, 142 * K), 4, outline=(58, 44, 72, 255), width=1)
    # Los 4 botoncitos de arriba a la derecha (no hacen nada en el juego): se tapan con la cabecera espejada.
    caja = (W - 194, 41, W - 151, 52)
    parche = im.crop(tuple(v * K for v in caja)).transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    im.alpha_composite(parche, (151 * K, 41 * K))
    # El '!' rojo de los carteles asoma sobre el borde de cada tarjeta: se tapa con el borde de al lado.
    for i in range(3):
        x = round(gx[3 * i + 3] - 14)
        parche = im.crop(((x - 8) * K, 52 * K, (x - 2) * K, 60 * K))
        im.alpha_composite(parche, ((x - 2) * K, 52 * K))
        im.alpha_composite(parche, (x * K + 2, 52 * K))
    _casillas(im, 31, fin + 15, 3, (30, 27, 36, 255), (110, 96, 126, 255))
    _casillas(im, 31, fin + 73, 1, (30, 27, 36, 255), (110, 96, 126, 255))
    _tira_inventario(im, fin, (168, 158, 186, 255), (92, 78, 108, 255))
    return im


# ------------------------------------------------------------------ Subastas y Banco (3 filas)
S_COFRE_X = [385, 550, 711, 876, 1038, 1198, 1364, 1531, 1689, 1857]
S_COFRE_Y = [385, 522, 678, 829]
S_INV_X = [380, 544, 703, 872, 1032, 1201, 1365, 1530, 1695, 1860]
S_INV_Y = [1051, 1205, 1357, 1511]
S_HOT_Y = [1543, 1708]
S_MARCO_X = (300, 1940)
# carteles 'Subastas' y 'Banco' de la division (se llevan a la fila 3 del cofre)
S_CARTEL = {'subastas': (522, 855, 912, 912), 'banco': (1330, 855, 1720, 912)}


def subastas_inicio():
    src = _fuente('subastas_banco_v1')
    alto = _alto(3)
    im = Image.new('RGBA', (W * K, alto * K))
    fin = 57 + 3 * 18 - 1      # 110
    gx = _rejilla(31, 9)
    x_cofre = ([0, S_MARCO_X[0]] + S_COFRE_X + [S_MARCO_X[1], 2172], [-14, 19] + gx + [204, 238])
    x_inv = ([0, S_MARCO_X[0]] + S_INV_X + [S_MARCO_X[1], 2172], [-14, 19] + gx + [204, 238])
    _banda(im, src, *x_cofre, [0, 120, 196, S_COFRE_Y[0], S_COFRE_Y[1], S_COFRE_Y[2], S_COFRE_Y[3], 849],
           [0, 14, 33, 55.5, 73.5, 91.5, 109.5, 112])
    _banda(im, src, *x_inv, [849, 862, 950, 1051], [112, 113, 113.01, fin + 14])
    _banda(im, src, *x_inv, S_INV_Y + S_HOT_Y + [1796, 1830, 1952],
           [fin + 14, fin + 32, fin + 50, fin + 68, fin + 72, fin + 90, fin + 100, fin + 103, fin + 116])
    im = _recorte_fondo(im, (51, 51, 51), tol=30)
    # Carteles Subastas / Banco en la fila 3 (casillas 19-21 y 23-25), a los lados de la X.
    full = Image.open(SRC / 'subastas_banco_v1.jpg').convert('RGB')
    for nombre, col in (('subastas', 0), ('banco', 5)):
        c = full.crop(S_CARTEL[nombre]).filter(ImageFilter.GaussianBlur(1.2))
        ancho = 3 * 18 * K - 2 * K
        alto_c = round(c.height * ancho / c.width)
        c = c.resize((ancho, alto_c), Image.Resampling.LANCZOS).convert('RGBA')
        x = (31 + 18 * (col + 1) - 1) * K + K
        y = (57 + 36) * K + (18 * K - alto_c) // 2 - K
        im.alpha_composite(c, (x, y))
    _casillas(im, 31, fin + 15, 3, (32, 30, 30, 255), (92, 74, 58, 255))
    _casillas(im, 31, fin + 73, 1, (28, 22, 22, 255), (92, 74, 58, 255))
    _tira_inventario(im, fin, (216, 196, 148, 255), (120, 78, 40, 255))
    return im


# ------------------------------------------------------------------ Banco Astral (6 vistas, 6 filas)
# Hoja de referencia del dueno (19/11): .local/gemini/refs-19-11/banco.png (1536x1024), 6 paneles de 490x403.
BANCO_REF = HERE.parent / '.local/gemini/refs-19-11/banco.png'
BANCO_ORIGEN = {'banco': (15, 82), 'depositar': (522, 82), 'retirar': (1030, 82),
                'mejorar': (15, 505), 'movimiento': (522, 505), 'cuenta': (1030, 505)}
# Alto del panel (relativo a su borde de arriba) -> alto de la ventana. El ultimo tramo es la fila de abajo
# (volver / tira / X) que cae en la fila 6 del cofre (casillas 45-53).
BANCO_Y = {
    'banco': ([0, 75, 222, 320, 377], [50, 108, 146.5, 164.5]),            # boveda+datos, 3 botones (filas 4-5)
    'depositar': ([0, 75, 196, 253, 318, 377], [50, 104, 128.5, 147, 164.5]),   # dibujo, todo/mitad/otra, confirmar
    'retirar': ([0, 75, 196, 253, 318, 377], [50, 104, 128.5, 147, 164.5]),
    'mejorar': ([0, 75, 262, 318, 377], [50, 128.5, 147, 164.5]),          # niveles+boveda, MEJORAR (fila 5)
    'movimiento': ([0, 68, 268, 318, 377], [48, 128.5, 147, 164.5]),       # pergamino, VOLVER AL BANCO
    'cuenta': ([0, 75, 262, 318, 377], [50, 128.5, 147, 164.5]),           # portal+datos, cartel
}
# Lo que cambia en el juego (importes, nombre de la cuenta, el texto del pergamino) se borra: va en el item al pasar
# el mouse. Cajas en px de la hoja.
BANCO_BORRAR = {
    'banco': [(340, 175, 441, 194), (340, 208, 441, 227), (338, 232, 441, 254), (340, 272, 441, 292)],
    'depositar': [(845, 183, 940, 204), (845, 246, 950, 267)],
    'retirar': [(1343, 222, 1456, 244)],
    'mejorar': [(322, 690, 438, 712), (332, 735, 428, 757)],
    'movimiento': [(688, 644, 854, 689), (688, 711, 854, 757)],
    'cuenta': [],
}
BANCO_ESCALA_X = 162 / 385      # del boton volver (x+55) al borde derecho de la X (x+440) = 9 casillas


def _borrar(im, caja):
    """Tapa una caja con el color del borde que la rodea (mediana del anillo)."""
    a = np.asarray(im.convert('RGB')).astype(int)
    x0, y0, x1, y1 = caja
    anillo = np.concatenate([a[y0 - 3:y0, x0:x1].reshape(-1, 3), a[y1:y1 + 3, x0:x1].reshape(-1, 3),
                             a[y0:y1, x0 - 3:x0].reshape(-1, 3), a[y0:y1, x1:x1 + 3].reshape(-1, 3)])
    ImageDraw.Draw(im).rectangle((x0, y0, x1 - 1, y1 - 1), fill=tuple(int(v) for v in np.median(anillo, 0)))


# Fila de niveles de 'Mejorar' redibujada por Gemini (20/11): una hoja sin brillo y otra con brillo, mismos lugares.
NIVELES_HOJA = {k: SRC / f'niveles_{k}.jpg' for k in ('normal', 'brillo')}
NIVELES_CORTE = (60, 380, 2700, 1100)             # fila entera en la hoja (2752x1536)
NIVELES_LIMITES = (60, 576, 1119, 1629, 2168, 2700)   # columnas de cada nivel
NIVELES_DESTINO = (70, 566, 460, 670)               # lugar de la fila en la hoja del Banco (px de la referencia)


def _fila_niveles(ref, nivel=None):
    """Pone la fila de niveles: todos sin brillo y el nivel actual (1..4) con brillo."""
    fila = Image.open(NIVELES_HOJA['normal']).convert('RGB')
    if nivel:
        brillo = Image.open(NIVELES_HOJA['brillo']).convert('RGB')
        x0, x1 = NIVELES_LIMITES[nivel - 1], NIVELES_LIMITES[nivel]
        m = Image.new('L', fila.size, 0)
        ImageDraw.Draw(m).rectangle((x0 + 20, NIVELES_CORTE[1], x1 - 20, NIVELES_CORTE[3]), fill=255)
        fila.paste(brillo, (0, 0), m.filter(ImageFilter.GaussianBlur(14)))
    fila = fila.crop(NIVELES_CORTE)
    dx0, dy0, dx1, dy1 = NIVELES_DESTINO
    fila = fila.resize((dx1 - dx0, dy1 - dy0), Image.Resampling.LANCZOS)
    # se borra la fila vieja (el recuadro dorado de 'Oro')
    a = np.asarray(fila).astype(int)
    fondo = tuple(int(v) for v in np.median(a[:20, :].reshape(-1, 3), 0))   # el azul de la hoja de Gemini
    ImageDraw.Draw(ref).rectangle((dx0 + 4, dy0 + 2, dx1 - 4, 669), fill=fondo)
    # bordes suaves para que el fondo de la hoja de Gemini se funda con el del panel
    m = Image.new('L', fila.size, 0)
    ImageDraw.Draw(m).rectangle((6, 4, fila.width - 7, fila.height - 5), fill=255)
    ref.paste(fila, (dx0, dy0), m.filter(ImageFilter.GaussianBlur(4)))


def banco(vista, nivel=None):
    """nivel (solo 'mejorar'): 1..4 = cuenta actual (Inicial..Esmeralda), se remarca en la fila de niveles."""
    ref = Image.open(BANCO_REF).convert('RGB')
    for caja in BANCO_BORRAR[vista]:
        _borrar(ref, caja)
    if vista == 'mejorar':
        _fila_niveles(ref, nivel)
    src = ref.filter(ImageFilter.GaussianBlur(0.5))
    ox, oy = BANCO_ORIGEN[vista]
    s = BANCO_ESCALA_X
    gx = _rejilla(31, 9)
    xs = ([ox - 40, ox, ox + 55, ox + 440, ox + 490, ox + 530],
          [gx[0] - 95 * s, gx[0] - 55 * s, gx[0], gx[9], gx[9] + 50 * s, gx[9] + 90 * s])
    rel, dst = BANCO_Y[vista]
    y0 = dst[0] - (rel[1] - rel[0]) * 0.4
    fin = 57 + 6 * 18 - 1   # 164
    im = Image.new('RGBA', (W * K, _alto(6) * K))
    # 1) panel de la hoja hasta la fila de abajo (volver / X)
    _banda(im, src, *xs, [oy + r for r in rel], [y0] + dst)
    # 2) costados del marco para el inventario: tira lisa (sin bisagras ni pernos) estirada
    # (de los paneles de abajo de la hoja: en los de arriba esa altura tiene la sombra de un perno)
    _banda(im, src, *xs, [505 + 205, 505 + 230], [fin + 0.5, fin + 96])
    # 3) borde de abajo del panel con los medallones enteros (20/11: cortados se veian mal)
    _banda(im, src, *xs, [oy + 362, oy + 404], [fin + 88, fin + 106])
    im = _recorte_fondo(im, tuple(int(v) for v in np.asarray(ref)[5, 5]), tol=40)
    d = ImageDraw.Draw(im)
    # fuera del panel (a los lados asoma el panel vecino de la hoja): transparente
    d.rectangle((0, 0, round((gx[0] - 55 * s) * K) - 1, im.height), fill=(0, 0, 0, 0))
    d.rectangle((round((gx[9] + 50 * s) * K) + 1, 0, im.width, im.height), fill=(0, 0, 0, 0))
    x_in0, x_in1 = gx[0] + (42 - 55) * s, gx[0] + (447 - 55) * s
    # Union panel / inventario: las esquinas de abajo del panel se tapan con los costados lisos.
    izq, der = round(x_in0 * K) + 2, round(x_in1 * K) - 2
    tira = im.crop((0, (fin + 40) * K, W * K, (fin + 41) * K))
    for y in range((fin - 6) * K, (fin + 2) * K):
        im.paste(tira.crop((0, 0, izq, 1)), (0, y))
        im.paste(tira.crop((der, 0, W * K, 1)), (der, y))
    # interior del inventario liso (entre las lineas doradas), hasta tapar la fila de botones del borde de abajo
    d.rectangle((round(x_in0 * K), (fin + 1) * K, round(x_in1 * K), (fin + 94) * K), fill=(17, 26, 46, 255))
    # restos de las esquinas de adentro del panel (curva dorada) a los lados del volver y la X
    d.rectangle((round(x_in0 * K), (fin - 9) * K, 31 * K + 1, (fin + 1) * K), fill=(17, 26, 46, 255))
    d.rectangle((191 * K + 1, (fin - 9) * K, round(x_in1 * K), (fin + 1) * K), fill=(17, 26, 46, 255))
    _casillas(im, 31, fin + 15, 3, (12, 18, 32, 255), (120, 96, 52, 255))
    _casillas(im, 31, fin + 73, 1, (12, 18, 32, 255), (120, 96, 52, 255))
    _tira_inventario(im, fin, (196, 202, 214, 255), (120, 96, 52, 255))
    return im


BANCO_VISTAS = ('banco', 'depositar', 'retirar', 'mejorar', 'movimiento', 'cuenta')
PANELES = {'comisiones': comisiones, 'subastas_inicio': subastas_inicio,
           **{f'banco_{v}': (lambda v=v: banco(v)) for v in BANCO_VISTAS},
           **{f'banco_mejorar{n}': (lambda n=n: banco('mejorar', n)) for n in (1, 2, 3, 4)}}


def panel(kind):
    """Fondo listo (a K) desde pack-source; se regenera con `python ventanas_20_11.py`."""
    return Image.open(OUT / f'{kind}.png').convert('RGBA')


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    prev = HERE.parent / 'build/previews'
    for k, f in PANELES.items():
        im = f()
        im.save(OUT / f'{k}.png')
        v = Image.new('RGBA', im.size, '#3a4a3a')
        v.alpha_composite(im)
        v.resize((im.width * 3 // 2, im.height * 3 // 2), Image.Resampling.NEAREST).save(prev / f'ventana_{k}_20_11.png')
        print(k, im.size)
