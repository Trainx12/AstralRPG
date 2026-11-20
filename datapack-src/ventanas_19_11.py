# -*- coding: utf-8 -*-
"""Ventanas del 19/11/2026 armadas con las referencias del dueno (.local/gemini/refs-19-11, ver arte_19_11.py).

Cada ventana = fondo en la fuente (dos glifos, como services_ui) + piezas como items con modelo (botones,
carteles, barras). Los recortes ya procesados viven en pack-source/arte-19-11/ventanas/ (van al repo).
Glifos: 0xF300 (inicio, -32), 0xF301 (fin, +32), 0xF310 + 4*i por ventana.

  cavernas_aviso   entrada a las Cavernas (DeluxeMenus, 4 filas)
  comisiones       tablero del campamento (AstralCavernas, 6 filas)
"""
import io
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance

from escape_menu import text
from services_ui import png, outlined

HERE = Path(__file__).resolve().parent
ART = HERE / 'pack-source/arte-19-11/ventanas'
START, END = '', ''
W = 224
BANCO_VISTAS = ('banco', 'depositar', 'retirar', 'mejorar', 'movimiento', 'cuenta')
VENTANAS = {'cavernas_aviso': 4, 'comisiones': 6, 'efectos': 6, **{f'banco_{v}': 6 for v in BANCO_VISTAS},
            'subastas_inicio': 3, **{f'banco_mejorar{n}': 6 for n in (1, 2, 3, 4)}}
# Fondos nuevos a doble resolucion (disenos Gemini 20/11, ventanas_20_11.py): reemplazan al armado de aca.
NUEVAS_2011 = ('comisiones', 'subastas_inicio', *(f'banco_{v}' for v in BANCO_VISTAS),
               *(f'banco_mejorar{n}' for n in (1, 2, 3, 4)))   # Mejorar con el nivel actual remarcado
# Piezas del Banco que ahora estan dibujadas en el fondo (20/11): el item queda invisible (solo nombre y lore).
BANCO_INVISIBLES = ('b_depositar', 'b_retirar', 'b_mejorar_cuenta', 'b_todo', 'b_mitad', 'b_otra', 'b_atras', 'b_cerrar',
                    'b_confirmar_dep', 'b_confirmar_ret', 'b_mejorar', 'b_volver_banco', 'i_saldo', 'i_encima', 'i_cuenta', 'i_limite')
CHARS = {k: tuple(chr(0xF310 + i * 4 + j) for j in range(4)) for i, k in enumerate(VENTANAS)}
FONDO = (36, 22, 49, 255)
ORO = '#c9a14f'


def _tiles_hd(kind):
    """Fondo a 2x partido en pedazos de hasta 224x224 px (el juego no carga glifos de mas de 256 px).
    Devuelve [(char_glifo, char_vuelta, imagen, alto_gui, ascent, x_gui, avance)]."""
    im = panel_hd(kind)
    j = NUEVAS_2011.index(kind)
    base = 0xF3E0 + 16 * j if j < 2 else 0xF410 + 16 * (j - 2)   # 0xF400 es el espacio de +112
    alto = im.height // 2
    filas = [(0, 56)] + [(y, min(y + 112, alto)) for y in range(56, alto, 112)]
    out, t = [], 0
    for y0, y1 in filas:
        for x0 in (0, 112):
            pieza = im.crop((x0 * 2, y0 * 2, (x0 + 112) * 2, y1 * 2))
            caja = pieza.getbbox()
            if caja:
                avance = -(-caja[2] // 2) + 1
                out.append((chr(base + t), chr(base + 8 + t), pieza, y1 - y0, 53 - y0, x0, avance))
            t += 1
    assert t <= 8
    return out


ADELANTE_112 = chr(0xF3E0 + 16 * 2)   # espacio de +112 para los pedazos de la derecha


def titulo(kind):
    if kind in NUEVAS_2011:
        s = ''.join((ADELANTE_112 if x0 else '') + g + v for g, v, _, _, _, x0, _ in _tiles_hd(kind))
        return '&f' + START + s + END
    c = CHARS[kind]
    return '&f' + START + c[0] + c[1] + c[2] + c[3] + END


def _slot(slot):
    return 31 + 18 * (slot % 9), 57 + 18 * (slot // 9)


# ------------------------------------------------------------------ recortes (desde la referencia, una vez)
def importar():
    """Recorta de las referencias las piezas de estas ventanas y las guarda en ART."""
    from arte_19_11 import ref, sin_fondo
    ART.mkdir(parents=True, exist_ok=True)
    cav = ref('cavernas').convert('RGBA')
    # Marco del panel de comisiones (para todas las ventanas de las Cavernas) y su cartel de titulo.
    cav.crop((35, 368, 685, 668)).save(ART / 'marco_cavernas.png')
    for n, b in {'cartel_comisiones': (262, 368, 500, 406), 'cartel_cavernas': (930, 368, 1278, 406)}.items():
        cav.crop(b).save(ART / f'{n}.png')
    piezas = {'badge_pendiente': (113, 423, 260, 455), 'badge_lista': (313, 413, 449, 459),
              'badge_cobrada': (485, 423, 645, 455), 'cobrar': (312, 582, 451, 613),
              'cristal_rojo': (150, 455, 220, 510), 'cristal_violeta': (348, 455, 412, 503),
              'cristal_azul': (538, 455, 604, 510), 'entrar': (1278, 557, 1471, 594), 'volver': (1296, 603, 1452, 637),
              'ilustracion': (716, 403, 1258, 662)}
    for n, b in piezas.items():
        im = cav.crop(b)
        if n.startswith('cristal'):
            im = sin_fondo(cav, b)
        im.save(ART / f'{n}.png')
    # Forja (Herrero y Reforja): botones con icono.
    forja = ref('forja')
    for n, b in FORJA_CAJAS.items():
        sin_fondo(forja, b, tol=22).save(ART / f'forja_{n}.png')
    # Efectos: marco, cartel, dibujos de intensidad, iconos de categoria e interruptores.
    ef = ref('efectos').convert('RGBA')
    ef.save(ART / 'marco_efectos.png')
    for n, b in EFECTOS_CAJAS.items():
        (sin_fondo(ef, b, tol=18) if n.startswith(('icono', 'nivel')) else ef.crop(b)).save(ART / f'efectos_{n}.png')
    # Banco Astral: marco de boveda, carteles, dibujos, botones e iconos.
    bn = ref('banco').convert('RGBA')
    bn.crop((20, 85, 500, 500)).save(ART / 'marco_banco.png')
    for n, b in BANCO_CAJAS.items():
        if n in BANCO_SIN_FONDO:   # botones: sin el azul del panel alrededor (20/11 se veian esquinas cortadas)
            solo_pieza(sin_fondo(bn, b, tol=24)).save(ART / f'banco_{n}.png')
            continue
        im = bn.crop(b)
        if n == 'ilu_movimiento':   # el pergamino trae importes de ejemplo: se tapan (el real va en el item)
            d = ImageDraw.Draw(im)
            d.rectangle((62, 52, im.width - 62, 178), fill=(236, 214, 162, 255))
        im.save(ART / f'banco_{n}.png')
    return sorted(p.name for p in ART.iterdir())


BANCO_CAJAS = {'cartel_banco': (95, 100, 430, 147), 'cartel_depositar': (605, 100, 910, 147), 'cartel_retirar': (1110, 100, 1440, 147),
               'cartel_mejorar': (95, 525, 430, 572), 'cartel_movimiento': (590, 525, 940, 572), 'cartel_cuenta': (1100, 525, 1445, 572),
               'ilu_banco': (80, 157, 285, 290), 'ilu_depositar': (580, 150, 785, 272), 'ilu_retirar': (1095, 152, 1278, 275),
               'ilu_mejorar': (75, 670, 232, 822), 'ilu_movimiento': (597, 583, 935, 775), 'ilu_cuenta': (1085, 580, 1285, 765),
               'b_depositar': (72, 284, 204, 402), 'b_retirar': (206, 284, 329, 402), 'b_mejorar_cuenta': (332, 278, 454, 402),
               'b_todo': (577, 280, 690, 328), 'b_mitad': (700, 280, 818, 328), 'b_otra': (828, 280, 957, 328),
               'b_confirmar_dep': (640, 338, 890, 397), 'b_confirmar_ret': (1150, 338, 1405, 397), 'b_mejorar': (238, 765, 455, 818),
               'b_volver_banco': (618, 776, 918, 822), 'b_atras': (67, 412, 115, 458), 'b_cerrar': (413, 414, 453, 453),
               'banner_cuenta': (1105, 768, 1445, 822), 'i_saldo': (300, 163, 332, 190), 'i_encima': (300, 198, 332, 226),
               'i_cuenta': (300, 232, 332, 258), 'i_limite': (300, 264, 332, 292)}


def solo_pieza(im):
    """Deja solo lo opaco conectado con el centro (saca restos del marco que entraron en el recorte)."""
    import numpy as np
    from collections import deque
    a = np.asarray(im.convert('RGBA')).copy()
    op = a[..., 3] > 0
    h, w = op.shape
    seen = np.zeros_like(op)
    q = deque([(h // 2, w // 2)])
    while q:
        y, x = q.popleft()
        if 0 <= y < h and 0 <= x < w and op[y, x] and not seen[y, x]:
            seen[y, x] = True
            q += [(y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)]
    a[~seen, 3] = 0
    o = Image.fromarray(a)
    return o.crop(o.getbbox())


BANCO_SIN_FONDO = ('b_depositar', 'b_retirar', 'b_mejorar_cuenta', 'b_atras', 'b_cerrar')


EFECTOS_CAJAS = {'cartel': (330, 85, 800, 165), 'nivel_bajo': (270, 280, 340, 335), 'nivel_medio': (480, 270, 640, 340),
                 'nivel_alto': (735, 260, 915, 345), 'check': (636, 258, 678, 298),
                 'icono_armaduras': (185, 455, 295, 508), 'icono_armas': (185, 515, 295, 568), 'icono_bastones': (185, 575, 295, 628),
                 'icono_mascotas': (185, 633, 295, 688), 'icono_jefes': (185, 693, 295, 750),
                 'on': (766, 465, 948, 501), 'off': (761, 642, 951, 680)}
EFECTOS_CATEGORIAS = ('armaduras', 'armas', 'bastones', 'mascotas', 'jefes')


FORJA_CAJAS = {'mejorar': (258, 428, 556, 503), 'atras': (136, 515, 209, 583), 'reparar': (225, 508, 438, 582),
               'gemas': (436, 508, 611, 582), 'cerrar': (614, 515, 681, 583), 'engarzar': (994, 452, 1281, 520),
               'extraer': (935, 518, 1152, 583), 'forja': (1148, 518, 1347, 583)}


def boton_forja(nombre, casillas, estado='listo'):
    """Boton de la Forja (x2 de resolucion) al ancho de sus casillas. estado: listo, apagado (gris), falta (rojo),
    confirma (naranja)."""
    b = _art(f'forja_{nombre}')
    ancho = casillas * 36
    esc = min(ancho / b.width, 34 / b.height)
    ex = min(ancho / b.width, esc * 1.3)          # a lo ancho puede estirarse un poco para llenar sus casillas
    b = b.resize((round(b.width * ex), round(b.height * esc)), Image.Resampling.LANCZOS)
    a = b.getchannel('A')
    if estado == 'apagado':
        b = ImageEnhance.Brightness(ImageEnhance.Color(b).enhance(0.1)).enhance(0.6)
    elif estado in ('falta', 'confirma'):
        capa = Image.new('RGBA', b.size, (200, 50, 50, 255) if estado == 'falta' else (230, 120, 30, 255))
        b = Image.blend(b, capa, 0.35)
    b.putalpha(a)
    out = Image.new('RGBA', (ancho, 36))
    out.alpha_composite(b, ((ancho - b.width) // 2, (36 - b.height) // 2))
    return out


def _art(n):
    return Image.open(ART / f'{n}.png').convert('RGBA')


# ------------------------------------------------------------------ marco por nueve cortes
def marco(alto, esquina=40, fuente='marco_cavernas', tiras=((70, 110), (140, 180), (120, 160)), k=21, fondo=FONDO):
    """Marco 224 x alto desde el panel de la referencia: esquinas con cristales, bordes estirados, interior liso."""
    src = _art(fuente)
    sw, sh = src.size
    out = Image.new('RGBA', (W, alto), fondo)
    e = esquina
    (tx0, tx1), (bx0, bx1), (ly0, ly1) = tiras
    # bordes: tiras sin decoracion (lejos del cartel y del cartel de abajo)
    top = src.crop((tx0, 0, tx1, e)).resize((W - 2 * k, k), Image.Resampling.LANCZOS)
    bot = src.crop((bx0, sh - e, bx1, sh)).resize((W - 2 * k, k), Image.Resampling.LANCZOS)
    izq = src.crop((0, ly0, e, ly1)).resize((k, alto - 2 * k), Image.Resampling.LANCZOS)
    # El lado derecho del panel original toca una tarjeta: se usa el izquierdo espejado (limpio).
    der = izq.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    out.alpha_composite(top, (k, 0)); out.alpha_composite(bot, (k, alto - k))
    out.alpha_composite(izq, (0, k)); out.alpha_composite(der, (W - k, k))
    tl = src.crop((0, 0, e, e)).resize((k, k), Image.Resampling.LANCZOS)
    bl = src.crop((0, sh - e, e, sh)).resize((k, k), Image.Resampling.LANCZOS)
    for im, (dx, dy) in ((tl, (0, 0)), (tl.transpose(Image.Transpose.FLIP_LEFT_RIGHT), (W - k, 0)),
                         (bl, (0, alto - k)), (bl.transpose(Image.Transpose.FLIP_LEFT_RIGHT), (W - k, alto - k))):
        out.alpha_composite(im, (dx, dy))
    ImageDraw.Draw(out).rectangle((k, k, W - k - 1, alto - k - 1), fill=fondo)
    return out


def _cartel(im, nombre, y=4, ancho=150, alto=44):
    c = _art(nombre)
    esc = min(ancho / c.width, alto / c.height)       # que no baje de la cabecera (las casillas empiezan en y 57)
    c = c.resize((round(c.width * esc), round(c.height * esc)), Image.Resampling.LANCZOS)
    im.alpha_composite(c, ((W - c.width) // 2, y))


def _inventario(im, filas):
    d = ImageDraw.Draw(im)
    end = 57 + filas * 18
    d.rectangle((31, end + 4, 192, end + 13), fill='#bab7aa')
    for row in range(4):
        for col in range(9):
            x, y = 31 + 18 * col, end + 14 + (18 * row if row < 3 else 58)
            d.rectangle((x - 1, y - 1, x + 16, y + 16), fill='#1d1426', outline='#7a6290')
            d.rectangle((x, y, x + 15, y + 15), fill=(0, 0, 0, 0))


def _alto(filas):
    return 57 + filas * 18 + 115


def _tarjeta(d, x0, y0, x1, y1):
    d.rectangle((x0, y0, x1, y1), fill='#2b1a38', outline=ORO)
    d.rectangle((x0 + 1, y0 + 1, x1 - 1, y1 - 1), outline='#5a3d1c')


EFECTOS_FONDO = (16, 22, 30, 255)
BANCO_FONDO = (21, 30, 46, 255)
# Dibujo y etiquetas de cada vista del banco (los botones e importes son items: economia.py).
BANCO_PANEL = {'banco': ('ilu_banco', 'Saldo|Encima|Cuenta'), 'depositar': ('ilu_depositar', 'Encima|Capacidad'),
               'retirar': ('ilu_retirar', 'Saldo|Encima'), 'mejorar': ('ilu_mejorar', 'Limite|Costo|Cuenta'),
               'movimiento': ('ilu_movimiento', ''), 'cuenta': ('ilu_cuenta', 'Limite|Interes|Tope')}


def _banco(im, d, vista):
    _cartel(im, f'banco_cartel_{vista}', 6, 140)
    ilu, etiquetas = BANCO_PANEL[vista]
    x0, y0 = _slot(0)
    il = _art('banco_' + ilu)
    if vista == 'movimiento':   # pergamino grande al centro
        il.thumbnail((126, 72))
        im.alpha_composite(il, (x0 + (162 - il.width) // 2, y0 + (72 - il.height) // 2))
        return
    alto = 72 if vista == 'cuenta' else 54
    il.thumbnail((88, alto))
    im.alpha_composite(il, (x0 + (90 - il.width) // 2, y0 + (alto - il.height) // 2))
    for i, et in enumerate(e for e in etiquetas.split('|') if e):
        sx, sy = _slot(i * 9 + 5)
        d.rectangle((sx - 1, sy - 1, sx + 72, sy + 16), fill='#0e1626', outline=ORO)
        text(im, et, (sx + 44, sy + 4), color='#f3e4b8')
    if vista == 'cuenta':
        b = _art('banco_banner_cuenta')
        b.thumbnail((150, 18))
        bx, by = _slot(37)
        im.alpha_composite(b, (bx + (126 - b.width) // 2, by))




def panel(kind):
    filas = VENTANAS[kind]
    if kind in NUEVAS_2011:   # a 1x solo para las vistas previas; el pack usa panel_hd
        im = panel_hd(kind)
        return im.resize((im.width // 2, im.height // 2), Image.Resampling.LANCZOS)
    if kind == 'efectos':
        im = marco(_alto(filas), 230, 'marco_efectos', ((300, 330), (330, 360), (880, 920)), 34, EFECTOS_FONDO)
    elif kind.startswith('banco_'):
        # tiras lisas del marco (20/11: las de antes tomaban el medallon y una bisagra y se veian cortadas)
        im = marco(_alto(filas), 60, 'marco_banco', ((412, 416), (240, 244), (205, 209)), 22, BANCO_FONDO)
    else:
        im = marco(_alto(filas))
    d = ImageDraw.Draw(im)
    if kind.startswith('banco_'):
        _banco(im, d, kind[6:])
    elif kind == 'efectos':
        _cartel(im, 'efectos_cartel', 6, 104)
        nombres = ('Armaduras', 'Armas', 'Bastones', 'Mascotas', 'Jefes')
        for i, nombre in enumerate(nombres):
            x0, y0 = _slot(9 * (i + 1))
            d.rectangle((x0 - 1, y0 - 1, x0 + 162, y0 + 16), fill='#18222c', outline='#3d5466')
            text(im, nombre, (x0 + 21 + len(nombre) * 3, y0 + 4), color='#f1e6c8')
    elif kind == 'comisiones':
        _cartel(im, 'cartel_comisiones', 8, 96)
        for i in range(3):   # tres tarjetas de 3 columnas x 5 filas
            x0, y0 = _slot(i * 3)
            _tarjeta(d, x0, y0 - 2, x0 + 52, y0 + 90 + 1)
        x0, y0 = _slot(47)
        d.rectangle((x0 - 1, y0 - 1, x0 + 90, y0 + 16), fill='#2b1a38', outline=ORO)
        outlined(im, '3 POR DIA', (x0 + 45, y0 + 5), color='#f3e4b8', outline='#1a1208')
    else:   # cavernas_aviso: ilustracion a la izquierda (6 col x 4 filas), botones a la derecha
        _cartel(im, 'cartel_cavernas', 8, 128)
        x0, y0 = _slot(0)
        il = _art('ilustracion')
        il = il.crop(((il.width - il.height * 108 // 72) // 2, 0, (il.width + il.height * 108 // 72) // 2, il.height))
        im.alpha_composite(il.resize((108, 72), Image.Resampling.LANCZOS), (x0, y0))
        d.rectangle((x0 - 1, y0 - 1, x0 + 108, y0 + 72), outline=ORO)
        tx, ty = _slot(6)
        d.rectangle((tx - 1, ty - 1, tx + 54, ty + 72), fill='#2b1a38', outline=ORO)
        outlined(im, 'GEMAS', (tx + 27, ty + 5), color='#f3e4b8', outline='#1a1208')
        outlined(im, 'TIER 4+', (tx + 27, ty + 59), color='#cfb9ff', outline='#1a1208')
    _inventario(im, filas)
    return im


# ------------------------------------------------------------------ piezas (items con modelo)
def _boton(nombre, ancho=54, gris=False):
    """Pieza recortada al ancho de sus casillas (x2 de resolucion), centrada y sin deformar."""
    b = _art(nombre)
    esc = min(ancho * 2 / b.width, 36 / b.height)
    b = b.resize((round(b.width * esc), round(b.height * esc)), Image.Resampling.LANCZOS)
    if gris:
        a = b.getchannel('A'); b = ImageEnhance.Brightness(ImageEnhance.Color(b).enhance(0.1)).enhance(0.6); b.putalpha(a)
    out = Image.new('RGBA', (ancho * 2, 36))
    out.alpha_composite(b, ((out.width - b.width) // 2, (36 - b.height) // 2))
    return out


def _boton_grande(nombre):
    """Boton de 3x2 casillas (x2): 108x72."""
    b = _art(nombre)
    b.thumbnail((108, 72))
    out = Image.new('RGBA', (108, 72))
    out.alpha_composite(b, ((108 - b.width) // 2, (72 - b.height) // 2))
    return out


def barra(nivel, cobrada=False):
    """Barra de avance 54x18 (x2): 0..10."""
    im = Image.new('RGBA', (108, 36))
    d = ImageDraw.Draw(im)
    d.rectangle((2, 10, 105, 25), fill='#140c1c', outline='#c9a14f', width=2)
    if nivel:
        d.rectangle((5, 13, 5 + round(97 * nivel / 10), 22), fill='#7d7f86' if cobrada else '#3fc24a')
        d.line((5, 13, 5 + round(97 * nivel / 10), 13), fill='#b8bac0' if cobrada else '#9cf08c', width=2)
    return im


def _tarjeta_nivel(nivel, activo):
    """Tarjeta de intensidad 54x18 (x2): dibujo de la referencia + nombre; la elegida con borde dorado y tilde."""
    im = Image.new('RGBA', (108, 36))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((1, 1, 106, 34), 5, fill='#121a22', outline='#ffb347' if activo else '#59687a', width=2)
    ic = _art(f'efectos_nivel_{nivel}')
    ic.thumbnail((40, 28))
    im.alpha_composite(ic, (6 + (40 - ic.width) // 2, (36 - ic.height) // 2))
    capa = Image.new('RGBA', (54, 18))
    outlined(capa, nivel.upper(), (33, 5), color='#fff0cd' if activo else '#c7d0d8', outline='#0a0d12')
    im.alpha_composite(capa.resize((108, 36), Image.Resampling.NEAREST))
    if activo:
        ch = _art('efectos_check').resize((10, 10), Image.Resampling.LANCZOS)
        im.alpha_composite(ch, (96, 0))
    return im


def piezas():
    """{modelo: imagen (x2)} de las piezas de estas ventanas."""
    out = {'badge_pendiente': _boton('badge_pendiente'), 'badge_lista': _boton('badge_lista'),
           'badge_cobrada': _boton('badge_cobrada'), 'cobrar': _boton('cobrar'), 'cobrar_off': _boton('cobrar', gris=True),
           'entrar': _boton('entrar'), 'volver': _boton('volver')}
    for n in range(11):
        out[f'barra_{n}'] = barra(n)
    out['barra_cobrada'] = barra(10, True)
    for nivel in ('bajo', 'medio', 'alto'):
        out[f'nivel_{nivel}'] = _tarjeta_nivel(nivel, False)
        out[f'nivel_{nivel}_activo'] = _tarjeta_nivel(nivel, True)
    out['interruptor_on'] = _boton('efectos_on')
    out['interruptor_off'] = _boton('efectos_off')
    for cat in EFECTOS_CATEGORIAS:
        ic = _art(f'efectos_icono_{cat}')
        sq = Image.new('RGBA', (max(ic.size),) * 2)
        sq.alpha_composite(ic, ((sq.width - ic.width) // 2, (sq.height - ic.height) // 2))
        out[f'efecto_{cat}'] = sq.resize((32, 32), Image.Resampling.LANCZOS)
    for n in ('b_depositar', 'b_retirar', 'b_mejorar_cuenta'):   # botones grandes 3x2 casillas
        out[n] = _boton_grande('banco_' + n)
    for n in ('b_todo', 'b_mitad', 'b_otra', 'b_atras', 'b_cerrar'):
        out[n] = _boton('banco_' + n, 54 if n in ('b_todo', 'b_mitad', 'b_otra') else 18)
    for n in ('b_confirmar_dep', 'b_confirmar_ret', 'b_mejorar', 'b_volver_banco'):
        out[n] = _boton('banco_' + n, 90)
    out['blank'] = Image.new('RGBA', (32, 32))
    for n in ('i_saldo', 'i_encima', 'i_cuenta', 'i_limite'):
        out[n] = _art('banco_' + n).resize((32, 32), Image.Resampling.LANCZOS)
    for c in ('rojo', 'violeta', 'azul'):
        ic = _art(f'cristal_{c}')
        sq = Image.new('RGBA', (max(ic.size),) * 2)
        sq.alpha_composite(ic, ((sq.width - ic.width) // 2, (sq.height - ic.height) // 2))
        out[f'cristal_{c}'] = sq.resize((32, 32), Image.Resampling.LANCZOS)
    for n in BANCO_INVISIBLES:
        out[n] = Image.new('RGBA', out[n].size)
    return out


def panel_hd(kind):
    from ventanas_20_11 import panel as p2011
    return p2011(kind)


def assets():
    files, providers, advances = {}, [], {START: -32, END: 32}
    advances[ADELANTE_112] = 112
    for kind in VENTANAS:
        if kind in NUEVAS_2011:
            for i, (g, v, pieza, alto, ascent, x0, avance) in enumerate(_tiles_hd(kind)):
                path = f'font/ventanas2011/{kind}_{i}.png'
                files['assets/astral/textures/' + path] = png(pieza)
                providers.append(dict(type='bitmap', file='astral:' + path, height=alto, ascent=ascent, chars=[g]))
                advances[v] = -(avance + x0)
            continue
        im = panel(kind)
        ch = CHARS[kind]
        for n, (part, ascent) in enumerate(((im.crop((0, 0, W, 56)), 53), (im.crop((0, 56, W, im.height)), -3))):
            path = f'font/ventanas1911/{kind}_{n}.png'
            files['assets/astral/textures/' + path] = png(part)
            providers.append(dict(type='bitmap', file='astral:' + path, height=part.height, ascent=ascent, chars=[ch[n * 2]]))
            advances[ch[n * 2 + 1]] = -(part.getbbox()[2] + 1)
    providers.append(dict(type='space', advances=advances))
    for nombre, im in piezas().items():
        ancho = im.width // 2
        tiles = max(1, ancho // 18) if im.height == 36 else 1
        if im.height == 72:   # botones grandes 3x2: indices 0-2 arriba, 3-5 abajo
            for i in range(6):
                t = im.crop(((i % 3) * 36, (i // 3) * 36, (i % 3) * 36 + 36, (i // 3) * 36 + 36))
                _modelo(files, f'{nombre}_{i}', t, 18)
        elif im.height == 36:   # piezas de 1-5 casillas a doble resolucion
            for i in range(tiles):
                t = im.crop((i * 36, 0, i * 36 + 36, 36))
                _modelo(files, f'{nombre}_{i}', t, 18)
        else:
            _modelo(files, nombre, im, 16)
    return files, providers


def _modelo(files, nombre, im, gui):
    files[f'assets/astral/textures/item/ventanas1911/{nombre}.png'] = png(im)
    files[f'assets/astral/models/ventanas1911/{nombre}.json'] = json.dumps({
        'parent': 'minecraft:item/generated', 'gui_light': 'front', 'textures': {'layer0': f'astral:item/ventanas1911/{nombre}'},
        'display': {'gui': {'scale': [gui / 16, gui / 16, 1]}}}).encode()
    files[f'assets/astral/items/ventanas1911/{nombre}.json'] = json.dumps({
        'oversized_in_gui': gui > 16, 'model': {'type': 'minecraft:model', 'model': f'astral:ventanas1911/{nombre}'}}).encode()


BANCO_EJEMPLO = {
    'banco': [(5, 'i_saldo', 1), (14, 'i_encima', 1), (23, 'i_cuenta', 1), (27, 'b_depositar', 6), (30, 'b_retirar', 6),
              (33, 'b_mejorar_cuenta', 6), (45, 'b_atras', 1), (53, 'b_cerrar', 1)],
    'depositar': [(5, 'i_encima', 1), (14, 'i_limite', 1), (27, 'b_todo', 3), (30, 'b_mitad', 3), (33, 'b_otra', 3),
                  (38, 'b_confirmar_dep', 5), (45, 'b_atras', 1), (53, 'b_cerrar', 1)],
    'retirar': [(5, 'i_saldo', 1), (14, 'i_encima', 1), (27, 'b_todo', 3), (30, 'b_mitad', 3), (33, 'b_otra', 3),
                (38, 'b_confirmar_ret', 5), (45, 'b_atras', 1), (53, 'b_cerrar', 1)],
    'mejorar': [(5, 'i_limite', 1), (14, 'i_saldo', 1), (23, 'i_cuenta', 1), (38, 'b_mejorar', 5), (45, 'b_atras', 1), (53, 'b_cerrar', 1)],
    'movimiento': [(38, 'b_volver_banco', 5), (53, 'b_cerrar', 1)],
    'cuenta': [(5, 'i_limite', 1), (14, 'i_saldo', 1), (23, 'i_encima', 1), (45, 'b_atras', 1), (53, 'b_cerrar', 1)]}


def preview(kind, colocar=()):
    """Vista previa a 3x con piezas puestas: colocar = [(slot, modelo_sin_indice, casillas)]."""
    im = Image.new('RGBA', (W, _alto(VENTANAS[kind])), '#252a28')
    im.alpha_composite(panel(kind))
    pz = piezas()
    for slot, nombre, n in colocar:
        p = pz[nombre]
        p = p.resize((p.width // 2, p.height // 2), Image.Resampling.LANCZOS) if p.height in (36, 72) else p.resize((16, 16), Image.Resampling.LANCZOS)
        x, y = _slot(slot)
        im.alpha_composite(p, (x - (1 if p.height == 18 else 0), y - (1 if p.height == 18 else 0)))
    return im.resize((im.width * 3, im.height * 3), Image.Resampling.NEAREST)


if __name__ == '__main__':
    import sys
    if '--importar' in sys.argv:
        print(importar())
    out = HERE.parent / 'build/previews'
    preview('comisiones', [(0, 'badge_pendiente', 3), (10, 'cristal_rojo', 1), (27, 'barra_3', 3),
                           (3, 'badge_lista', 3), (13, 'cristal_violeta', 1), (30, 'barra_10', 3), (39, 'cobrar', 3),
                           (6, 'badge_cobrada', 3), (16, 'cristal_azul', 1), (33, 'barra_cobrada', 3)]).save(out / 'ventana_comisiones.png')
    preview('cavernas_aviso', [(15, 'entrar', 3), (24, 'volver', 3)]).save(out / 'ventana_cavernas_aviso.png')
    preview('efectos', [(0, 'nivel_bajo', 3), (3, 'nivel_medio_activo', 3), (6, 'nivel_alto', 3)]
            + [(9 * (i + 1), f'efecto_{c}', 1) for i, c in enumerate(EFECTOS_CATEGORIAS)]
            + [(9 * (i + 1) + 6, 'interruptor_off' if c == 'mascotas' else 'interruptor_on', 3) for i, c in enumerate(EFECTOS_CATEGORIAS)]
            ).save(out / 'ventana_efectos.png')
    hoja = Image.new('RGBA', (672 * 3, 1018 * 2))
    for i, v in enumerate(BANCO_VISTAS):
        hoja.alpha_composite(preview(f'banco_{v}', BANCO_EJEMPLO.get(v, [])), ((i % 3) * 672, (i // 3) * 1018))
    hoja.resize((hoja.width // 2, hoja.height // 2)).save(out / 'ventana_banco.png')
    print('vistas en', out)
