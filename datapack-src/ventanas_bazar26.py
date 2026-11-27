# -*- coding: utf-8 -*-
"""Ventanas del Bazar 1.2.0 con el arte Gemini del dueno (26/11/2026).

Referencias (privadas, no van al repo): .local/gemini/refs-26-11/bazar/g_<ventana>.jpg (2400x1792), una por
ventana, pedidas a Gemini con la grilla del cofre. Cada imagen se deforma por tramos (lineas del dibujo ->
lineas de la grilla del juego, K=2, W=224 como ventanas_bazar.py) y lo que no coincide (botones de un
casillero, tarjetas de cantidad) se pega como pieza recortada.

python ventanas_bazar26.py [ventana...] -> pack-source/arte-bazar/<ventana>.png + build/previews/bazar_<ventana>.png
Los casilleros de cada boton estan en runtime/AstralBazar.java (hit(...)).
"""
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import ventanas_bazar as VB

HERE = Path(__file__).resolve().parent
REF = HERE.parent / '.local/gemini/refs-26-11/bazar'
K, W, TOP = VB.K, VB.W, VB.TOP
PRE = 0.2                       # la imagen se achica a esta escala antes de deformar (unos 2x lo final)

FILAS = {'productos': 6, 'producto': 6, 'cantidad_ic': 5, 'cantidad_iv': 5, 'cantidad_oc': 5, 'cantidad_ov': 5,
         'precio': 5, 'mis_ordenes': 6, 'inventario': 6}


def fila(r):
    return TOP + 18 * r


def col(c):
    return 30.5 + 18 * c


@lru_cache(None)
def ref(nombre):
    return Image.open(REF / f'g_{nombre}.jpg').convert('RGBA')


@lru_cache(None)
def chica(nombre):
    im = ref(nombre)
    return np.asarray(im.resize((round(im.width * PRE), round(im.height * PRE)), Image.Resampling.LANCZOS))


def lienzo(filas):
    return Image.new('RGBA', (W * K, VB.V._alto(filas) * K))


def deformar(im, nombre, xs, xd, ys, yd):
    """Pega la imagen deformada por tramos: xs/ys px del dibujo -> xd/yd px de ventana (crecientes)."""
    a = chica(nombre)
    u = (np.arange(W * K) + .5) / K
    v = (np.arange(im.height) + .5) / K
    sx = np.interp(u, xd, xs) * PRE
    sy = np.interp(v, yd, ys) * PRE
    okx = (u >= xd[0]) & (u <= xd[-1])
    oky = (v >= yd[0]) & (v <= yd[-1])
    ix = np.clip(sx.astype(int), 0, a.shape[1] - 1)
    iy = np.clip(sy.astype(int), 0, a.shape[0] - 1)
    out = a[iy][:, ix].copy()
    out[~(oky[:, None] & okx[None, :])] = 0
    im.alpha_composite(Image.fromarray(out, 'RGBA'))


def parejo(im, nombre, xs, xd, ys, yd, hasta):
    """Arriba de y=hasta (px de ventana) con escala pareja en x: carteles sin cortes por los tramos."""
    t = Image.new('RGBA', im.size)
    deformar(t, nombre, xs, xd, ys, yd)
    h = round(hasta * K)
    ImageDraw.Draw(im).rectangle((0, 0, W * K, h - 1), fill=(0, 0, 0, 0))
    im.alpha_composite(t.crop((0, 0, W * K, h)))


def pieza(nombre, caja):
    return ref(nombre).crop(tuple(round(c) for c in caja))


def poner(im, p, rect):
    """Pieza estirada justo a rect (px de ventana)."""
    x0, y0, x1, y1 = rect
    q = p.resize((round((x1 - x0) * K), round((y1 - y0) * K)), Image.Resampling.LANCZOS)
    im.alpha_composite(q, (round(x0 * K), round(y0 * K)))


def llenar(im, nombre, punto, rect):
    color = ref(nombre).getpixel(punto)
    x0, y0, x1, y1 = rect
    ImageDraw.Draw(im).rectangle((round(x0 * K), round(y0 * K), round(x1 * K) - 1, round(y1 * K) - 1), fill=color)


def casillero(im, nombre, caja, slot, margen=0):
    c, r = slot % 9, slot // 9
    poner(im, pieza(nombre, caja), (col(c) - margen, fila(r) - margen, col(c) + 18 + margen, fila(r) + 18 + margen))


# ================================================================== Inicio (lista de productos)
def productos():
    n = 'inicio'
    im = lienzo(6)
    deformar(im, n, [20, 75, 770, 890, 1098, 1301, 1500, 1708, 1912, 2117, 2320, 2385],
             [0, 2, 64, 66.5, 84.5, 102.5, 120.5, 138.5, 156.5, 174.5, 192.5, 198.5],
             [0, 336, 558, 779, 1015, 1255, 1481, 1530, 1740, 1792],
             [fila(0) - 336 * 18 / 225, fila(0), fila(1), fila(2), fila(3), fila(4), fila(5), fila(5) + .5,
              fila(6) - .5, fila(6) + 4])
    # Cabecera sin los tramos de la grilla (si no, el cartel queda cortado): escala pareja.
    cab = lienzo(6)
    deformar(cab, n, [20, 2385], [0, 198.5], [0, 336], [fila(0) - 336 * 18 / 225, fila(0)])
    ImageDraw.Draw(im).rectangle((0, 0, W * K, round(fila(0) * K) - 1), fill=(0, 0, 0, 0))
    im.alpha_composite(cab.crop((0, 0, W * K, round(fila(0) * K))))
    # Fila de botones: Gemini dibujo 11; van 9, uno por casillero.
    llenar(im, n, (270, 1600), (2, fila(5), 198, fila(6) - .5))
    poner(im, pieza(n, (780, 1290, 880, 1470)), (2, fila(5), col(0), fila(6) - .5))
    botones = [(78, 258), (284, 464), (492, 672), (696, 876), (902, 1086), (1110, 1290), (1314, 1494),
               (1522, 1702), (1728, 1908), (1934, 2114), (2142, 2322)]
    for slot, b in zip(range(45, 54), [0, 2, 3, 4, 6, 7, 8, 9, 10]):
        x0, x1 = botones[b]
        casillero(im, n, (x0, 1548, x1, 1718), slot)
    categorias_131(im)
    return im


def categorias_131(im):
    """Conserva marco, espadas, cana y los dos botones inferiores del Gemini original."""
    original = im.copy()
    def banda(r):
        return (4 * K, round(fila(r) * K), 64 * K, round(fila(r + 1) * K))
    im.paste(original.crop(banda(1)), (4 * K, round(fila(0) * K)))
    for r, nombre in ((1, 'Bosque'), (2, 'Oceano')):
        boton = original.crop(banda(2))
        d = ImageDraw.Draw(boton)
        # El interior azul se toma del propio boton, sin tocar sus bordes dorados.
        fondo = boton.getpixel((53 * K, 5 * K))
        d.rectangle((3 * K, 2 * K, 57 * K, 15 * K), fill=fondo)
        if r == 2:
            # Cana de Bosque y pesca, a su misma escala y posicion.
            boton.alpha_composite(original.crop((7*K, round((fila(2)+2)*K), 23*K, round((fila(2)+16)*K))), (3*K, 2*K))
        else:
            # Arbol pixel: paleta azul/verde del icono original, sin alterar el marco.
            arbol = ['....aa....', '...abba...', '..abbcca..', '.abbbccca.', 'aabbbcccaa', '..abccca..', '.abbbccca.', 'aaabccaaaa', '....tt....', '....tt....', '...tttt...']
            pal = {'a':'#173f37', 'b':'#41936c', 'c':'#76bf83', 't':'#a77946'}
            for y,line in enumerate(arbol):
                for x,p in enumerate(line):
                    if p in pal:d.rectangle(((6+x)*K,(3+y)*K,(7+x)*K-1,(4+y)*K-1),fill=pal[p])
        # Letras recortadas del propio Gemini, sin cambiar fuente ni escala.
        if r == 1:
            label = original.crop((55, 192, 100, 205))
        else:
            # C cerrada por su reflejo para O; las minusculas ya existen en las etiquetas.
            from PIL import ImageOps
            cap = original.crop((55, 159, 62, 176))
            arr = np.asarray(cap).copy()
            mirror = np.asarray(ImageOps.mirror(cap))
            take = mirror[:, :, :3].sum(2) > arr[:, :, :3].sum(2)
            arr[take] = mirror[take]
            chars = [Image.fromarray(arr), original.crop((79, 268, 85, 285)),
                     original.crop((100, 159, 107, 176)), original.crop((88, 159, 94, 176)),
                     original.crop((68, 124, 75, 141)), original.crop((62, 159, 69, 176))]
            label = Image.new('RGBA', (sum(c.width for c in chars), 17), fondo)
            x = 0
            for c in chars:
                label.paste(c, (x, 0)); x += c.width
        boton.alpha_composite(label, (round(39*K-label.width/2), round(9*K-label.height/2)))
        im.paste(boton, (4*K, round(fila(r)*K)))


# ================================================================== Producto
def producto():
    n = 'producto'
    im = lienzo(6)
    deformar(im, n, [20, 75, 1095, 1305, 2325, 2385], [26, 30.5, 102.5, 120.5, 192.5, 197],
             [0, 330, 570, 612, 1020, 1068, 1488, 1542, 1722, 1792],
             [fila(0) - 26, fila(0), fila(1), fila(1) + 1, fila(3) - 1, fila(3) + 1, fila(5) - 1, fila(5),
              fila(6), fila(6) + 4])
    return im


# ================================================================== Cantidad (4 casos)
# Tarjetas de g_tarjetas.jpg (2 filas de 4): fila 1 = 1, Un stack, Llenar inventario, Todo lo que tengo;
# fila 2 = 64, 160, 1024, Todo lo que tengo. Caso -> tarjetas (fila, columna) en los casilleros 9-11/12-14/15-17.
CASOS = {'cantidad_ic': [(0, 0), (0, 1), (0, 2)], 'cantidad_iv': [(0, 0), (0, 1), (1, 3)],
         'cantidad_oc': [(1, 0), (1, 1), (1, 2)], 'cantidad_ov': [(1, 0), (1, 1), (1, 3)]}
_TX = [(74, 562), (658, 1152), (1248, 1740), (1838, 2326)]
# por fila: (y icono, y texto) en px del dibujo
_TY = [((150, 462), (470, 760)), ((990, 1340), (1350, 1660))]


def contenido(nombre, caja, umbral=70):
    """Recorte justo a lo que se ve (icono o texto) dentro de caja; el fondo oscuro queda afuera."""
    p = pieza(nombre, caja)
    a = np.asarray(p.convert('L')) > umbral
    ys, xs = np.nonzero(a)
    return p.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))


def encajar(im, p, rect, tope=None):
    """Pieza a escala pareja, centrada dentro de rect (tope: escala maxima, px de ventana por px del dibujo)."""
    x0, y0, x1, y1 = rect
    e = min((x1 - x0) * K / p.width, (y1 - y0) * K / p.height, (tope or 99) * K)
    q = p.resize((max(1, round(p.width * e)), max(1, round(p.height * e))), Image.Resampling.LANCZOS)
    im.alpha_composite(q, (round(x0 * K + ((x1 - x0) * K - q.width) / 2), round(y0 * K + ((y1 - y0) * K - q.height) / 2)))


def cantidad(kind):
    n = 'cantidad'
    im = lienzo(5)
    deformar(im, n, [20, 96, 829, 1590, 2322, 2385], [25, 30.5, 84.5, 138.5, 192.5, 197],
             [0, 330, 570, 1150, 1170, 1470, 1520, 1740, 1792],
             [fila(0) - 26, fila(0), fila(1), fila(3), fila(3), fila(4), fila(4), fila(5), fila(5) + 4])
    for k, (r, c) in enumerate(CASOS[kind]):
        x, (x0, x1), (iy, ty) = col(3 * k), _TX[c], _TY[r]
        # Icono a la izquierda y texto a la derecha (las tarjetas de Gemini son verticales).
        encajar(im, contenido('tarjetas', (x0 + 40, iy[0], x1 - 40, iy[1])), (x + 4, fila(1) + 5, x + 21, fila(3) - 5), .055)
        encajar(im, contenido('tarjetas', (x0 + 25, ty[0], x1 - 25, ty[1]), 110), (x + 22, fila(1) + 4, x + 51, fila(3) - 4), .06)
    return im


# ================================================================== Precio
def precio():
    n = 'precio'
    im = lienzo(5)
    deformar(im, n, [20, 78, 549, 1002, 1416, 1851, 2322, 2385], [25, 30.5, 66.5, 102.5, 120.5, 156.5, 192.5, 197],
             [0, 330, 570, 1500, 1520, 1740, 1792],
             [fila(0) - 26, fila(0), fila(1), fila(4), fila(4), fila(5), fila(5) + 4])
    parejo(im, n, [20, 2385], [25, 197], [0, 330, 570], [fila(0) - 26, fila(0), fila(1)], fila(1))
    return im


# ================================================================== Mis ordenes / Vender inventario
# Gemini dibujo 11 columnas: se usan las 9 primeras y el borde derecho.
_LX = [79, 283, 488, 688, 891, 1098, 1303, 1503, 1708, 1913]
_LY = [333, 560, 778, 1019, 1260, 1482]


def grilla45(n, botones, ladrillo=None):
    im = lienzo(6)
    xs, xd = [20] + _LX + [2319, 2385], [25] + [col(c) for c in range(10)] + [193, 198]
    ys = [0] + _LY + [1530, 1740, 1792]
    yd = [fila(0) - 26] + [fila(r) for r in range(6)] + [fila(5) + .5, fila(6) - .5, fila(6) + 4]
    deformar(im, n, xs, xd, ys, yd)
    parejo(im, n, [20, 2385], [25, 198], ys[:2], yd[:2], fila(0))
    llenar(im, n, (40, 1500), (col(0) - 2, fila(5), col(9) + 2, fila(6) - .5))
    if ladrillo:
        poner(im, pieza(n, ladrillo), (col(0), fila(5), col(9), fila(6)))
    for (x0, x1, *y), (c0, c1) in botones:
        y0, y1 = y or (1542, 1722)
        poner(im, pieza(n, (x0, y0, x1, y1)), (col(c0), fila(5), col(c1 + 1), fila(6)))
    return im


def mis_ordenes():
    return grilla45('mis_ordenes', [((78, 672), (0, 1)), ((696, 876), (2, 2)), ((902, 1086), (3, 3)),
                                    ((1110, 1290), (4, 4)), ((1314, 1794), (5, 6)), ((1818, 2322), (7, 8))])


def inventario():
    return grilla45('inventario', [((78, 618), (0, 1)), ((816, 1584, 1524, 1722), (3, 5)), ((1818, 2322), (7, 8))],
                     ladrillo=(630, 1550, 800, 1710))


VENTANAS = {'productos': productos, 'producto': producto, 'precio': precio, 'mis_ordenes': mis_ordenes,
            'inventario': inventario,
            **{k: (lambda k=k: cantidad(k)) for k in CASOS}}


def preview(kind, im):
    filas = FILAS[kind]
    prev = Image.new('RGBA', im.size, (40, 40, 40, 255))
    d = ImageDraw.Draw(prev)
    d.rectangle((23 * K, 39 * K, 199 * K, (fila(filas) + 97) * K), fill=(198, 198, 198, 255))
    for r in range(filas):
        for c in range(9):
            x, y = col(c), fila(r)
            d.rectangle((x * K, y * K, (x + 18) * K - 1, (y + 18) * K - 1), outline=(255, 0, 255, 255))
    for r in range(4):
        for c in range(9):
            x, y = col(c), fila(filas) + 14 + 18 * r + (4 if r == 3 else 0)
            d.rectangle((x * K, y * K, (x + 18) * K - 1, (y + 18) * K - 1), fill=(139, 139, 139, 255), outline=(55, 55, 55, 255))
    prev.alpha_composite(im)
    guia = Image.new('RGBA', im.size)
    g = ImageDraw.Draw(guia)
    for r in range(filas):
        for c in range(9):
            x, y = col(c), fila(r)
            g.rectangle((x * K, y * K, (x + 18) * K - 1, (y + 18) * K - 1), outline=(255, 0, 255, 90))
    prev.alpha_composite(guia)
    return prev


if __name__ == '__main__':
    import sys
    VB.OUT.mkdir(parents=True, exist_ok=True)
    out = HERE.parent / 'build/previews'
    out.mkdir(parents=True, exist_ok=True)
    for kind in (sys.argv[1:] or VENTANAS):
        im = VENTANAS[kind]()
        im.save(VB.OUT / f'{kind}.png')
        preview(kind, im).save(out / f'bazar_{kind}.png')
        print('ok', kind)
