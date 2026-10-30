"""HUD estilo RPG para el resource pack (dibujado de cero, nada copiado de Minecraft).

Minecraft dibuja cada pieza del HUD en su lugar fijo (no se puede mover sin mods), pero la textura puede tener
mas pixeles que la original: aca todo se dibuja a 4x (cada pixel del juego = 4x4) para tener sombras y brillos.

- Corazones: forma normal, con contorno, degrade, brillo y sombra.
- Comida: barra naranja en pedazos (Minecraft dibuja 10 pegados cada 8 pixeles, juntos forman una barra).
- Armadura: escudos de acero; aire: burbujas.
- Barra de items, mano secundaria, experiencia, salto y jefes: piedra oscura, oro y gemas violetas.
"""
import math
import random

from PIL import Image, ImageDraw

E = 4  # escala

ORO = (217, 164, 58)
ORO_CLARO = (252, 214, 112)
BRONCE = (107, 74, 28)
CONTORNO = (14, 11, 9)
PIEDRA = (46, 50, 52)
PIEDRA_CLARA = (74, 79, 80)
PIEDRA_OSCURA = (24, 26, 28)
JUNTA = (30, 32, 34)
VIOLETA = (154, 82, 214)
VIOLETA_CLARO = (220, 160, 255)
VIOLETA_OSCURO = (52, 30, 74)
ROSA = (246, 160, 255)
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)


# ------------------------------------------------------------------ utilidades
def mezcla(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple(round(x + (y - x) * t) for x, y in zip(a[:3], b[:3]))


def claro(c, t):
    return mezcla(c, BLANCO, t)


def oscuro(c, t):
    return mezcla(c, NEGRO, t)


def lienzo(w, h):
    return Image.new("RGBA", (w * E, h * E), (0, 0, 0, 0))


def pon(px, x, y, col, a=255):
    px[x, y] = tuple(col[:3]) + (a,)


def rect(im, x0, y0, x1, y1, col, a=255):
    """Rectangulo en pixeles reales, x1/y1 incluidos."""
    px = im.load()
    for y in range(max(0, y0), min(im.size[1], y1 + 1)):
        for x in range(max(0, x0), min(im.size[0], x1 + 1)):
            pon(px, x, y, col, a)


def ruido(x, y, semilla=0, amp=6):
    return random.Random(x * 92821 + y * 68917 + semilla * 1013).randint(-amp, amp)


def con_ruido(c, x, y, semilla=0, amp=6):
    n = ruido(x, y, semilla, amp)
    return tuple(max(0, min(255, v + n)) for v in c[:3])


def pintar_forma(im, dentro, color, borde, grosor=2, sombra=2, mascara=None, borde_alpha=255):
    """Pinta una forma definida por dentro(u, v) en unidades del juego (0..ancho). color(u, v, d) da el relleno,
    d = distancia aproximada al borde en pixeles reales. mascara(u, v) recorta el relleno (medio corazon, etc.)."""
    W, H = im.size
    px = im.load()
    ins = [[dentro((x + 0.5) / E, (y + 0.5) / E) for x in range(W)] for y in range(H)]

    def adentro(x, y):
        return 0 <= x < W and 0 <= y < H and ins[y][x]

    if sombra:
        for y in range(H):
            for x in range(W):
                if not ins[y][x] and adentro(x - sombra, y - sombra) and (mascara is None or
                                                                          mascara((x - sombra + 0.5) / E, (y - sombra + 0.5) / E)):
                    pon(px, x, y, NEGRO, 90)
    for y in range(H):
        for x in range(W):
            if not ins[y][x]:
                continue
            u, v = (x + 0.5) / E, (y + 0.5) / E
            if mascara is not None and not mascara(u, v):
                continue
            d = 99
            for r in range(1, 6):
                if any(not adentro(x + dx, y + dy) for dx, dy in ((r, 0), (-r, 0), (0, r), (0, -r))):
                    d = r
                    break
            if d <= grosor:
                if borde is not None:
                    pon(px, x, y, borde, borde_alpha)
            else:
                c = color(u, v, d)
                if c is not None:
                    pon(px, x, y, c[:3], c[3] if len(c) > 3 else 255)


# ------------------------------------------------------------------ corazones
def dentro_corazon(u, v):
    if (u - 2.65) ** 2 + (v - 3.0) ** 2 <= 2.45 ** 2 or (u - 6.35) ** 2 + (v - 3.0) ** 2 <= 2.45 ** 2:
        return True
    return 3.0 <= v <= 8.1 and abs(u - 4.5) <= (8.1 - v) * 0.92


def corazon(base, parte="full", parpadeo=False, hardcore=False):
    """parte: full | half | container."""
    im = lienzo(9, 9)
    if parte == "container":
        borde = (230, 230, 230) if parpadeo else (30, 8, 10)

        def col(u, v, d):
            t = v / 9
            c = mezcla((58, 22, 26), (24, 8, 10), t)
            return c + (235,) if d > 4 else oscuro(c, 0.35) + (235,)
        pintar_forma(im, dentro_corazon, col, borde, grosor=2, sombra=2)
        return im

    luz, sombra_c = claro(base, 0.55), oscuro(base, 0.45)

    def col(u, v, d):
        t = (u * 0.45 + v) / 11.0                               # degrade: arriba-izq claro, abajo-der oscuro
        c = mezcla(claro(base, 0.18), sombra_c, t)
        if d <= 4 and (v > 4.5 or u > 6.8):                     # sombra interna abajo/derecha
            c = oscuro(c, 0.25)
        if d <= 4 and v < 3.0 and u < 4:                        # luz en el borde de arriba
            c = mezcla(c, luz, 0.5)
        if ((u - 2.3) / 1.15) ** 2 + ((v - 2.3) / 0.75) ** 2 <= 1:      # brillo grande
            c = mezcla(c, BLANCO, 0.62)
        if (u - 6.6) ** 2 + (v - 2.2) ** 2 <= 0.32:                      # brillo chico
            c = mezcla(c, BLANCO, 0.5)
        if hardcore and abs(u - 4.5) <= 0.35 and 3.4 <= v <= 6.6:        # vena oscura (hardcore)
            c = oscuro(c, 0.45)
        return c
    borde = (250, 250, 250) if parpadeo else oscuro(base, 0.78)
    mascara = (lambda u, v: u < 4.5) if parte == "half" else None
    pintar_forma(im, dentro_corazon, col, borde, grosor=2, sombra=2, mascara=mascara)
    return im


VIDA = {"": (226, 34, 46), "poisoned_": (126, 178, 38), "withered_": (62, 56, 54), "frozen_": (150, 214, 244),
        "absorbing_": (246, 196, 54)}


# ------------------------------------------------------------------ comida (barra)
def pedazo_barra(color, parte="full", invertido=False, fondo=(44, 28, 16)):
    """Pedazo de 9x9 de una barra de 5 de alto. parte: full | half | empty."""
    im = lienzo(9, 9)
    W = im.size[0]
    y0, y1 = 2 * E, 7 * E - 1
    if parte == "empty":
        rect(im, 0, y0 - 2, W - 1, y1 + 2, CONTORNO)
        for y in range(y0, y1 + 1):
            c = mezcla(oscuro(fondo, 0.4), fondo, (y - y0) / (y1 - y0))
            rect(im, 2, y, W - 3, y, c)
        rect(im, 2, y0, W - 3, y0 + 1, oscuro(fondo, 0.6))          # sombra interna arriba
        rect(im, 0, y1 + 3, W - 1, y1 + 4, NEGRO, 90)                # sombra bajo la barra
        rect(im, 0, y0 - 2, 1, y1 + 2, (8, 6, 4))                    # separadores
        rect(im, W - 2, y0 - 2, W - 1, y1 + 2, (8, 6, 4))
        return im
    a, b = 2, W - 3
    if parte == "half":
        a, b = (W // 2, W - 3) if invertido else (2, W // 2 - 1)
    px = im.load()
    alto = y1 - y0
    for y in range(y0, y1 + 1):
        t = (y - y0) / alto
        if t < 0.18:
            c = claro(color, 0.55)
        elif t < 0.35:
            c = claro(color, 0.22)
        elif t > 0.8:
            c = oscuro(color, 0.4)
        elif t > 0.62:
            c = oscuro(color, 0.18)
        else:
            c = color
        for x in range(a, b + 1):
            cc = con_ruido(c, x, y, 7, 5)
            if (x - y) % 18 in (0, 1, 2) and 0.2 < t < 0.7:          # reflejo en diagonal
                cc = claro(cc, 0.2)
            pon(px, x, y, cc)
    return im


# ------------------------------------------------------------------ armadura
def dentro_escudo(u, v):
    if v < 0.5 or v > 8.5:
        return False
    if v < 4.6:
        w = 3.9 - max(0.0, 1.3 - v) * 0.9
    else:
        w = 3.9 * (8.5 - v) / 3.9
    return abs(u - 4.5) <= w


def escudo(parte):
    im = lienzo(9, 9)

    def vacio(u, v, d):
        return (34, 36, 42, 150)

    def lleno(u, v, d):
        t = (u * 0.5 + v) / 11.0
        c = mezcla((226, 232, 240), (104, 110, 126), t)
        if u > 4.5:
            c = oscuro(c, 0.14)                                      # mitad derecha en sombra
        if abs(u - 4.5) < 0.3:
            c = claro(c, 0.35)                                       # arista del medio
        if d <= 4:
            c = mezcla(c, ORO if v < 5 else BRONCE, 0.55)            # ribete dorado
        if ((u - 4.5) ** 2 + (v - 3.6) ** 2) <= 0.85:                # piedra violeta del centro
            c = VIOLETA_CLARO if (u < 4.4 and v < 3.4) else VIOLETA
        if ((u - 3.0) / 0.6) ** 2 + ((v - 1.9) / 0.5) ** 2 <= 1:
            c = claro(c, 0.6)
        return c
    if parte == "empty":
        pintar_forma(im, dentro_escudo, vacio, (92, 96, 108), grosor=2, sombra=2)
    elif parte == "full":
        pintar_forma(im, dentro_escudo, lleno, (28, 26, 30), grosor=2, sombra=2)
    else:
        pintar_forma(im, dentro_escudo, lambda u, v, d: lleno(u, v, d) if u < 4.5 else vacio(u, v, d),
                     (28, 26, 30), grosor=2, sombra=2)
    return im


# ------------------------------------------------------------------ aire
def burbuja(estado):
    im = lienzo(9, 9)
    px = im.load()
    W = im.size[0]
    cx = cy = 4.5 * E
    R = 3.9 * E
    for y in range(W):
        for x in range(W):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            d = math.hypot(dx, dy)
            if d > R:
                if estado == "full" and d <= R + 2 and dx > -2 and dy > -2:
                    pon(px, x, y, NEGRO, 70)                          # sombrita
                continue
            if estado == "empty":
                if d >= R - 2:
                    pon(px, x, y, (96, 130, 160), 150)
                continue
            if estado == "bursting":
                ang = math.atan2(dy, dx)
                if d >= R - 3 and int((ang + math.pi) / (math.pi / 6)) % 2 == 0:
                    pon(px, x, y, (230, 248, 255))
                continue
            if d >= R - 2:
                pon(px, x, y, (24, 70, 120))                          # contorno
            elif d >= R - 4:
                pon(px, x, y, mezcla((170, 226, 255), (70, 140, 210), (dx + dy + R) / (2 * R)))
            else:
                t = d / R
                pon(px, x, y, mezcla((40, 100, 180), (110, 180, 245), t), 150 + int(80 * t))
            if ((dx + 5) / 5) ** 2 + ((dy + 6) / 3.2) ** 2 <= 1:      # brillo
                pon(px, x, y, (240, 252, 255))
            if (dx - 6) ** 2 + (dy - 6) ** 2 <= 3:
                pon(px, x, y, (220, 245, 255), 220)
    return im


# ------------------------------------------------------------------ barra de items
def piedra_tallada(im, x0, y0, x1, y1, semilla=0):
    """Ladrillos de piedra oscura con juntas y ruido."""
    px = im.load()
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            fila = (y - y0) // (5 * E)
            dx = x - x0 + (6 * E if fila % 2 else 0)
            if (y - y0) % (5 * E) in (0, 1) or dx % (12 * E) in (0, 1):
                c = JUNTA
            else:
                v = random.Random((dx // (12 * E)) * 7919 + fila * 104729 + semilla).randint(-6, 6)
                c = tuple(max(0, min(255, k + v)) for k in PIEDRA)
                if (y - y0) % (5 * E) in (2,):
                    c = claro(c, 0.12)                                # canto de luz del ladrillo
                c = con_ruido(c, x, y, semilla, 4)
            pon(px, x, y, c)


def marco_oro(im, x0, y0, x1, y1, ancho=3):
    """Ribete dorado biselado de 'ancho' pixeles reales, con contorno."""
    rect(im, x0, y0, x1, y0, CONTORNO)
    rect(im, x0, y1, x1, y1, CONTORNO)
    rect(im, x0, y0, x0, y1, CONTORNO)
    rect(im, x1, y0, x1, y1, CONTORNO)
    for k in range(1, ancho + 1):
        t = k / ancho
        arriba = mezcla(ORO_CLARO, ORO, t)
        abajo = mezcla(ORO, BRONCE, 1 - t * 0.3)
        rect(im, x0 + k, y0 + k, x1 - k, y0 + k, arriba)
        rect(im, x0 + k, y0 + k, x0 + k, y1 - k, arriba)
        rect(im, x0 + k, y1 - k, x1 - k, y1 - k, abajo)
        rect(im, x1 - k, y0 + k, x1 - k, y1 - k, abajo)
    rect(im, x0 + ancho + 1, y0 + ancho + 1, x1 - ancho - 1, y0 + ancho + 1, CONTORNO, 160)


def gema(im, cx, cy, r, apagada=True):
    """Gema en rombo con 4 caras, brillo y contorno."""
    px = im.load()
    base = VIOLETA if not apagada else (118, 62, 170)
    caras = {"ai": claro(base, 0.35), "ad": base, "bi": oscuro(base, 0.15), "bd": oscuro(base, 0.4)}
    for y in range(-r, r + 1):
        for x in range(-r, r + 1):
            d = abs(x) + abs(y)
            if d > r:
                continue
            if d >= r - 1:
                c = oscuro(base, 0.65)
            else:
                c = caras[("a" if y < 0 else "b") + ("i" if x < 0 else "d")]
                if abs(x) + abs(y) <= r // 3:
                    c = claro(c, 0.15)
                if x == -r // 3 and y == -r // 3:
                    c = claro(c, 0.7)
            pon(px, cx + x, cy + y, c, 200 if apagada else 255)


def casillero(im, x0, y0, semilla=0, con_gema=True):
    """Hueco de 16x16 (en unidades del juego) hundido en la piedra, con sombra interna."""
    a0, b0 = x0 * E - 2, y0 * E - 2
    a1, b1 = (x0 + 16) * E + 1, (y0 + 16) * E + 1
    rect(im, a0, b0, a1, b1, CONTORNO)
    px = im.load()
    cx, cy = (a0 + a1) / 2, (b0 + b1) / 2
    for y in range(b0 + 1, b1):
        for x in range(a0 + 1, a1):
            dd = max(abs(x - cx), abs(y - cy)) / ((a1 - a0) / 2)
            c = mezcla((44, 30, 60), (20, 14, 28), dd ** 2)           # mas oscuro en los bordes
            c = con_ruido(c, x, y, semilla, 2)
            pon(px, x, y, c)
    rect(im, a0 + 1, b0 + 1, a1 - 1, b0 + 3, NEGRO, 120)             # sombra interna arriba
    rect(im, a0 + 1, b0 + 1, a0 + 3, b1 - 1, NEGRO, 90)              # sombra interna izquierda
    rect(im, a0 + 1, b1 - 1, a1 - 1, b1 - 1, (110, 90, 60))          # luz abajo
    rect(im, a1 - 1, b0 + 1, a1 - 1, b1 - 1, (90, 74, 50))
    if con_gema:
        gema(im, int(cx), int(cy), 2 * E + 1)


def remache(im, cx, cy):
    rect(im, cx - 2, cy - 2, cx + 2, cy + 2, CONTORNO)
    rect(im, cx - 1, cy - 1, cx + 1, cy + 1, ORO)
    pon(im.load(), cx - 1, cy - 1, ORO_CLARO)


def hotbar():
    im = lienzo(182, 22)
    W, H = im.size
    piedra_tallada(im, 0, 0, W - 1, H - 1, semilla=3)
    marco_oro(im, 0, 0, W - 1, H - 1, ancho=3)
    for i in range(9):
        casillero(im, 3 + 20 * i, 3, semilla=i)
        if i < 8:                                                     # columna dorada entre casilleros
            mx = (3 + 20 * i + 18) * E
            rect(im, mx - 2, 2 * E + 2, mx + 1, H - 2 * E - 3, CONTORNO)
            rect(im, mx - 1, 2 * E + 3, mx, H - 2 * E - 4, BRONCE)
            pon(im.load(), mx - 1, 2 * E + 3, ORO_CLARO)
            gema(im, mx, H // 2, 3, apagada=False)
    for cx in (6, W - 7):                                             # remaches de las puntas
        for cy in (6, H - 7):
            remache(im, cx, cy)
    for cx in range(20 * E, W - 10, 40 * E):                          # remaches arriba y abajo
        remache(im, cx + 2 * E, 2)
        remache(im, cx + 2 * E, H - 3)
    # Runas en los pilares: el centro de cada hueco queda libre para leer los items.
    d = ImageDraw.Draw(im)
    for i in range(1, 9):
        x = (2 + 20 * i) * E
        d.line([(x, 5 * E), (x - E, 7 * E), (x, 9 * E),
                (x + E, 7 * E), (x, 5 * E)], fill=VIOLETA + (255,), width=2)
        d.line([(x, 12 * E), (x, 16 * E)], fill=ORO + (255,), width=2)
    return im


def hotbar_seleccion():
    im = lienzo(24, 23)
    W, H = im.size
    for k, (col, a) in enumerate(((VIOLETA, 70), (VIOLETA, 130), (VIOLETA_OSCURO, 255), (VIOLETA_CLARO, 255),
                                  (VIOLETA, 255), (VIOLETA_CLARO, 255), (VIOLETA_OSCURO, 255))):
        rect(im, k, k, W - 1 - k, k, col, a)
        rect(im, k, H - 1 - k, W - 1 - k, H - 1 - k, col, a)
        rect(im, k, k, k, H - 1 - k, col, a)
        rect(im, W - 1 - k, k, W - 1 - k, H - 1 - k, col, a)
    rect(im, 7, 7, W - 8, 9, VIOLETA, 70)                             # brillo hacia adentro
    for cx, cy in ((5, 5), (W - 6, 5), (5, H - 6), (W - 6, H - 6)):    # puntas de oro con gema
        rect(im, cx - 4, cy - 4, cx + 4, cy + 4, CONTORNO)
        rect(im, cx - 3, cy - 3, cx + 3, cy + 3, ORO)
        rect(im, cx - 3, cy - 3, cx + 3, cy - 3, ORO_CLARO)
        rect(im, cx - 1, cy - 1, cx + 1, cy + 1, ROSA)
        pon(im.load(), cx - 1, cy - 1, BLANCO)
    for cx in (W // 2,):                                               # gema arriba y abajo
        gema(im, cx, 3, 3, apagada=False)
        gema(im, cx, H - 4, 3, apagada=False)
    return im


def mano_secundaria(lado):
    im = lienzo(29, 24)
    W, H = im.size
    x0 = 0 if lado == "left" else 7 * E
    x1 = x0 + 22 * E - 1
    piedra_tallada(im, x0, 0, x1, H - 1, semilla=5)
    marco_oro(im, x0, 0, x1, H - 1, ancho=3)
    casillero(im, x0 // E + 3, 4, semilla=9, con_gema=False)
    for cx in (x0 + 6, x1 - 6):
        for cy in (6, H - 7):
            remache(im, cx, cy)
    return im


# ------------------------------------------------------------------ barras largas (experiencia, salto, jefes)
def barra_fondo():
    im = lienzo(182, 5)
    W, H = im.size
    rect(im, 0, 0, W - 1, H - 1, CONTORNO)
    for y in range(2, H - 2):
        rect(im, 2, y, W - 3, y, mezcla((14, 10, 18), (40, 32, 48), (y - 2) / (H - 4)))
    rect(im, 1, 0, W - 2, 1, ORO_CLARO)
    rect(im, 1, 1, W - 2, 1, ORO)
    rect(im, 1, H - 2, W - 2, H - 1, BRONCE)
    rect(im, 0, 1, 1, H - 2, ORO)
    rect(im, W - 2, 1, W - 1, H - 2, BRONCE)
    for x in range(20 * E, W - 4, 20 * E):                            # marcas cada 20
        rect(im, x - 1, 2, x, H - 3, (70, 56, 34))
        rect(im, x - 2, 2, x + 1, 3, ORO)
    for cx, cy in ((0, 0), (W - 1, 0), (0, H - 1), (W - 1, H - 1)):   # puntas redondeadas
        pon(im.load(), cx, cy, NEGRO, 0)
    return im


def barra_progreso(color):
    im = lienzo(182, 5)
    W, H = im.size
    px = im.load()
    for y in range(2, H - 2):
        t = (y - 2) / (H - 5)
        if t < 0.2:
            c = claro(color, 0.6)
        elif t < 0.45:
            c = claro(color, 0.2)
        elif t > 0.8:
            c = oscuro(color, 0.4)
        else:
            c = color
        for x in range(2, W - 2):
            cc = c
            if (x + y) % 24 < 5:                                       # reflejos en diagonal
                cc = claro(cc, 0.18)
            pon(px, x, y, con_ruido(cc, x, y, 11, 3))
    return im


JEFES = {"pink": (236, 110, 190), "blue": (70, 140, 240), "red": (220, 50, 50), "green": (80, 200, 80),
         "yellow": (240, 210, 60), "purple": (160, 80, 220), "white": (230, 230, 230)}


def indicador(progreso=False, cruz=False):
    """Indicador de recarga real del ataque, sin inventar una barra de mana."""
    im = lienzo(16 if cruz else 18, 4 if cruz else 18)
    w, h = im.size
    if cruz:
        rect(im, 0, E, w - 1, h - E - 1, VIOLETA_CLARO if progreso else PIEDRA_OSCURA)
        rect(im, 0, 0, w - 1, 0, ORO)
    else:
        marco_oro(im, 4 * E, E, 14 * E - 1, h - E - 1, ancho=E)
        rect(im, 6 * E, 3 * E, 12 * E - 1, h - 3 * E - 1,
             VIOLETA_CLARO if progreso else PIEDRA_OSCURA)
    return im


def marco_efecto(ambient=False):
    """Marco de los efectos activos: conserva el hueco del icono vanilla."""
    im = lienzo(24, 24)
    rect(im, 0, 0, im.width-1, im.height-1, PIEDRA_OSCURA, 220)
    marco_oro(im, 0, 0, im.width-1, im.height-1, ancho=E)
    for x,y in ((2*E,2*E),(21*E,2*E),(2*E,21*E),(21*E,21*E)):
        gema(im,x,y,E,apagada=not ambient)
    return im


def hud(alta_resolucion=False):
    """Devuelve {ruta relativa a textures/gui: imagen}."""
    S = "sprites/hud/"
    out = {S + "hotbar.png": hotbar(), S + "hotbar_selection.png": hotbar_seleccion(),
           S + "hotbar_offhand_left.png": mano_secundaria("left"), S + "hotbar_offhand_right.png": mano_secundaria("right")}
    for pre, col in VIDA.items():
        for hard in ("", "hardcore_"):
            for blink in ("", "_blinking"):
                for parte in ("full", "half"):
                    out[f"{S}heart/{pre}{hard}{parte}{blink}.png"] = corazon(col, parte, bool(blink), bool(hard))
    for hard in ("", "_hardcore"):
        for blink in ("", "_blinking"):
            out[f"{S}heart/container{hard}{blink}.png"] = corazon(None, "container", bool(blink))
    out[S + "heart/vehicle_container.png"] = corazon(None, "container")
    out[S + "heart/vehicle_full.png"] = corazon((214, 160, 82), "full")
    out[S + "heart/vehicle_half.png"] = corazon((214, 160, 82), "half")
    naranja, hambre = (242, 140, 36), (128, 160, 48)
    out[S + "food_empty.png"] = pedazo_barra(None, "empty")
    out[S + "food_empty_hunger.png"] = pedazo_barra(None, "empty", fondo=(34, 44, 18))
    out[S + "food_full.png"] = pedazo_barra(naranja, "full")
    out[S + "food_half.png"] = pedazo_barra(naranja, "half", invertido=True)
    out[S + "food_full_hunger.png"] = pedazo_barra(hambre, "full")
    out[S + "food_half_hunger.png"] = pedazo_barra(hambre, "half", invertido=True)
    for k in ("full", "half", "empty"):
        out[f"{S}armor_{k}.png"] = escudo(k)
    out[S + "air.png"] = burbuja("full")
    out[S + "air_empty.png"] = burbuja("empty")
    out[S + "air_bursting.png"] = burbuja("bursting")
    out[S + "experience_bar_background.png"] = barra_fondo()
    out[S + "experience_bar_progress.png"] = barra_progreso((176, 110, 240))
    out[S + "jump_bar_background.png"] = barra_fondo()
    out[S + "jump_bar_cooldown.png"] = barra_progreso((90, 80, 70))
    out[S + "jump_bar_progress.png"] = barra_progreso((90, 180, 240))
    out[S + "effect_background.png"] = marco_efecto()
    out[S + "effect_background_ambient.png"] = marco_efecto(True)
    # La barra de localizacion puede sustituir la de XP en 26.1.2.
    # El localizador es un tile de 12x5 con metadatos propios del cliente.
    # Se conserva vanilla hasta tratar tambien su nine-slice, sin romperlo.
    for parte in ("background", "progress"):
        out[S + f"hotbar_attack_indicator_{parte}.png"] = indicador(parte == "progress")
        out[S + f"crosshair_attack_indicator_{parte}.png"] = indicador(parte == "progress", cruz=True)
    for col, rgb in JEFES.items():
        out[f"sprites/boss_bar/{col}_background.png"] = barra_fondo()
        out[f"sprites/boss_bar/{col}_progress.png"] = barra_progreso(rgb)
    # Exportar al tamano nativo. E es solo la resolucion interna del dibujante.
    # No dependemos del escalado del atlas ni dejamos metadatos de otras texturas.
    if alta_resolucion:
        return out
    native = {ruta: im.resize((im.width // E, im.height // E), Image.Resampling.NEAREST)
              for ruta, im in out.items()}
    # Estos detalles se trazan al final para que sean legibles a escala 1x.
    d = ImageDraw.Draw(native[S + "hotbar.png"])
    for i in range(1, 9):
        x = 1 + 20*i
        d.line((x,3,x,18), fill=BRONCE+(255,))
        d.line((x-1,4,x-1,17), fill=PIEDRA_CLARA+(255,))
        d.polygon([(x,7),(x+1,8),(x,9),(x-1,8)],fill=VIOLETA+(255,))
        d.point((x,7),fill=VIOLETA_CLARO+(255,))
        d.point((x,14),fill=ORO_CLARO+(255,))
    d = ImageDraw.Draw(native[S + "hotbar_selection.png"])
    d.rectangle((1,1,22,21),outline=VIOLETA_CLARO+(255,))
    for x,y in ((1,1),(22,1),(1,21),(22,21)):
        d.point((x,y),fill=ORO_CLARO+(255,))
    return native


def preview(path):
    """Muestra los sprites a escala GUI 4x. No simula datos ni una captura real."""
    sprites = hud()
    im = Image.new("RGBA", (1000,420), (24,29,31,255))
    ImageDraw.Draw(im).text((32,24),"ASTRAL RPG / HUD - vista de texturas, no captura del juego",fill=ORO_CLARO)

    def paste(name,x,y):
        s=sprites[name]
        im.alpha_composite(s.resize((s.width*4,s.height*4),Image.Resampling.NEAREST),(x,y))

    h="sprites/hud/"
    paste("sprites/boss_bar/purple_background.png",136,80)
    paste("sprites/boss_bar/purple_progress.png",136,80)
    for i in range(10):
        paste(h+"armor_full.png",136+i*32,180)
        paste(h+"heart/container.png",136+i*32,220)
        if i<7:paste(h+"heart/full.png",136+i*32,220)
        paste(h+"food_empty.png",540+i*32,220)
        if i<8:paste(h+"food_full.png",540+i*32,220)
    paste(h+"experience_bar_background.png",136,264)
    progress=sprites[h+"experience_bar_progress.png"].crop((0,0,120,5)).resize((480,20),Image.Resampling.NEAREST)
    im.alpha_composite(progress,(136,264))
    paste(h+"hotbar.png",136,300)
    paste(h+"hotbar_selection.png",292,296)
    paste(h+"hotbar_offhand_left.png",12,296)
    paste(h+"effect_background.png",880,160)
    im.convert("RGB").save(path)


if __name__=="__main__":
    from pathlib import Path
    path=Path(__file__).resolve().parent.parent/"build/HUD-preview.png"
    path.parent.mkdir(parents=True,exist_ok=True)
    preview(path)
    print(path)
