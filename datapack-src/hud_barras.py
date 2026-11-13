"""HUD Astral: hotbar de marco dorado con casilleros azul noche y barras de vida y comida (dibujo propio).

Inspirado en la imagen de referencia del dueno (13/11). Todo es vanilla, sin mods:
- hotbar, seleccion (con gema verde) y mano izquierda: sprites del HUD a doble resolucion.
- Vida: cada corazon es un segmento de barra roja (10 segmentos = una barra). AstralDecor fija la escala
  de vida del cliente en 20 (10 corazones), asi siempre es UNA barra. La vida real no cambia y el texto
  de AuraSkills (vida, defensa, mana) sigue arriba con los numeros reales.
- Comida: segmentos naranjas (se vacia de izquierda a derecha, como vanilla).
- Armadura y burbujas: quedan las de antes.
Lo que no se puede en vanilla: adornos fuera de la barra y casillas extra.

python hud_barras.py [carpeta]  -> sprites en <carpeta>/assets/minecraft/textures/gui/sprites/hud/
El HUD anterior quedo guardado en ASTRAL_PRIVADO/originales/hud-anterior-13-11/.
"""
import os
import sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
PRIV = Path(os.environ.get('ASTRAL_PRIVADO', ROOT / '.local/terceros/AstralRPG-privado'))
OUT = PRIV / 'build/entregas/hud-barras'
S = 2   # texeles por pixel de la interfaz

NEGRO = (10, 10, 14, 255)
ORO_OSC, ORO, ORO_CLARO = (110, 58, 16, 255), (201, 128, 36, 255), (247, 196, 90, 255)
NOCHE, NOCHE_OSC, NOCHE_CLARO = (26, 33, 49, 255), (14, 18, 28, 255), (52, 66, 92, 255)
GEMA = ((20, 90, 50, 255), (60, 190, 100, 255), (190, 255, 200, 255))


class Lienzo:
    def __init__(self, w, h):
        self.im = Image.new('RGBA', (w * S, h * S), (0, 0, 0, 0)); self.px = self.im.load()

    def rect(self, x0, y0, x1, y1, c):
        for y in range(round(y0 * S), round(y1 * S)):
            for x in range(round(x0 * S), round(x1 * S)):
                if 0 <= x < self.im.width and 0 <= y < self.im.height:
                    self.px[x, y] = c

    def marco(self, x0, y0, x1, y1, c, g=0.5):
        self.rect(x0, y0, x1, y0 + g, c); self.rect(x0, y1 - g, x1, y1, c)
        self.rect(x0, y0, x0 + g, y1, c); self.rect(x1 - g, y0, x1, y1, c)

    def casillero(self, x0, y0, x1, y1):
        self.rect(x0, y0, x1, y1, NEGRO)
        self.rect(x0 + 0.5, y0 + 0.5, x1 - 0.5, y1 - 0.5, NOCHE)
        self.rect(x0 + 0.5, y0 + 0.5, x1 - 0.5, y0 + 1, NOCHE_OSC); self.rect(x0 + 0.5, y0 + 0.5, x0 + 1, y1 - 0.5, NOCHE_OSC)
        self.rect(x0 + 0.5, y1 - 1, x1 - 0.5, y1 - 0.5, NOCHE_CLARO); self.rect(x1 - 1, y0 + 0.5, x1 - 0.5, y1 - 0.5, NOCHE_CLARO)

    def gema(self, cx, y):
        o, m, b = GEMA
        self.rect(cx - 1.5, y + 0.5, cx + 1.5, y + 1.5, o); self.rect(cx - 1, y, cx + 1, y + 2, o)
        self.rect(cx - 1, y + 0.5, cx + 1, y + 1.5, m); self.rect(cx - 0.5, y, cx + 0.5, y + 2, m)
        self.rect(cx - 0.5, y + 0.5, cx, y + 1, b)


def marco_oro(l, x0, y0, x1, y1):
    l.rect(x0, y0, x1, y1, NEGRO)
    l.rect(x0 + 0.5, y0 + 0.5, x1 - 0.5, y1 - 0.5, ORO_OSC)
    l.rect(x0 + 1, y0 + 1, x1 - 1, y1 - 1, ORO)
    l.rect(x0 + 1, y0 + 1, x1 - 1, y0 + 1.5, ORO_CLARO); l.rect(x0 + 1, y0 + 1, x0 + 1.5, y1 - 1, ORO_CLARO)


def hotbar():
    l = Lienzo(182, 22)
    marco_oro(l, 0, 0, 182, 22)
    for i in range(9):
        l.casillero(2 + 20 * i, 2, 20 + 20 * i, 20)
        if i:   # remache en cada division
            l.rect(20 * i, 0.5, 20 * i + 2, 1.5, ORO_CLARO); l.rect(20 * i + 0.5, 20.5, 20 * i + 1.5, 21.5, ORO_CLARO)
    for x in (0, 181):   # puntas
        l.rect(x, 9, x + 1, 13, ORO_CLARO)
    return l.im


def seleccion():
    l = Lienzo(24, 23)
    l.marco(0, 0, 24, 23, NEGRO); l.marco(0.5, 0.5, 23.5, 22.5, ORO_CLARO, 1); l.marco(1.5, 1.5, 22.5, 21.5, ORO, 1)
    l.marco(2.5, 2.5, 21.5, 20.5, ORO_OSC)
    for x, y in ((0, 0), (21, 0), (0, 20), (21, 20)):   # esquinas brillantes
        l.rect(x + 0.5, y + 0.5, x + 2.5, y + 2.5, (255, 236, 160, 255))
    o, m, b = GEMA   # gema verde arriba al centro
    l.rect(9.5, 0, 14.5, 3, NEGRO); l.rect(10, 0.5, 14, 2.5, o); l.rect(10.5, 0.5, 13.5, 2, m); l.rect(11, 0.5, 12, 1, b)
    return l.im


def mano_izquierda(derecha=False):
    l = Lienzo(29, 24)
    dx = 7 if derecha else 0
    marco_oro(l, dx, 0, dx + 22, 24)
    l.casillero(dx + 2, 3, dx + 20, 21)
    return l.im


# ---------------------------------------------------------------- barras (corazones y comida como segmentos)
def _seg(colores, desde=1, hasta=8, fondo=None):
    """Segmento 9x9: filas 0 y 8 marco dorado, columnas 0 y 8 divisiones negras, relleno en desde..hasta."""
    l = Lienzo(9, 9)
    if fondo:
        l.rect(0, 0, 9, 1, ORO); l.rect(0, 8, 9, 9, ORO_OSC)
        l.rect(0, 1, 1, 8, NEGRO); l.rect(8, 1, 9, 8, NEGRO)
        l.rect(1, 1, 8, 8, fondo); l.rect(1, 1, 8, 1.5, tuple(max(0, v - 12) for v in fondo[:3]) + (255,))
        return l.im
    alto, medio, bajo = colores
    l.rect(desde, 1, hasta, 8, medio)
    l.rect(desde, 1, hasta, 2.5, alto)
    l.rect(desde, 6, hasta, 8, bajo)
    return l.im


def _tono(rgb, f):
    return tuple(max(0, min(255, round(v * f))) for v in rgb) + (255,)


def _brillo(im, n=40):
    im = im.copy(); px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a:
                px[x, y] = (min(255, r + n), min(255, g + n), min(255, b + n), a)
    return im


VIDA = {'': (225, 40, 40), 'poisoned_': (90, 170, 40), 'withered_': (70, 64, 64), 'frozen_': (150, 210, 245),
        'absorbing_': (240, 195, 60)}
COMIDA = {'': (235, 130, 35), '_hunger': (125, 150, 55)}


def barras():
    out = {}
    for var, rgb in VIDA.items():
        col = (_tono(rgb, 1.35), _tono(rgb, 1.0), _tono(rgb, 0.6))
        for hc in ('', 'hardcore_'):
            for parte, hasta in (('full', 8), ('half', 4.5)):
                im = _seg(col, 1, hasta)
                out[f'heart/{var}{hc}{parte}.png'] = im
                out[f'heart/{var}{hc}{parte}_blinking.png'] = _brillo(im)
    fondo_vida = (48, 12, 16, 255)
    for hc in ('', '_hardcore'):
        out[f'heart/container{hc}.png'] = _seg(None, fondo=fondo_vida)
        out[f'heart/container{hc}_blinking.png'] = _brillo(_seg(None, fondo=fondo_vida), 60)
    montura = (_tono((200, 90, 60), 1.3), _tono((200, 90, 60), 1.0), _tono((200, 90, 60), 0.6))
    out['heart/vehicle_container.png'] = _seg(None, fondo=fondo_vida)
    out['heart/vehicle_full.png'] = _seg(montura)
    out['heart/vehicle_half.png'] = _seg(montura, 1, 4.5)
    for var, rgb in COMIDA.items():
        col = (_tono(rgb, 1.3), _tono(rgb, 1.0), _tono(rgb, 0.62))
        out[f'food_full{var}.png'] = _seg(col)
        out[f'food_half{var}.png'] = _seg(col, 4.5, 8)       # se vacia por la izquierda
        out[f'food_empty{var}.png'] = _seg(None, fondo=(44, 26, 12, 255))
    return out


def sprites():
    out = {'hotbar.png': hotbar(), 'hotbar_selection.png': seleccion(),
           'hotbar_offhand_left.png': mano_izquierda(), 'hotbar_offhand_right.png': mano_izquierda(True)}
    out.update(barras())
    return out


def generate(base=OUT):
    for rel, im in sprites().items():
        d = Path(base) / 'assets/minecraft/textures/gui/sprites/hud' / rel
        d.parent.mkdir(parents=True, exist_ok=True); im.save(d)
    return base


def preview(path):
    """Simulacion del HUD a 4x: hotbar, mano izquierda, vida 7.5/10 y comida 6.5/10."""
    sp = sprites(); E = 4
    W, H = 182 + 60, 50
    can = Image.new('RGBA', (W * S, H * S), (78, 110, 70, 255))
    def put(im, x, y):
        can.alpha_composite(im, (round(x * S), round(y * S)))
    hx, hy = 40, 26
    put(sp['hotbar.png'], hx, hy); put(sp['hotbar_selection.png'], hx - 1 + 20 * 2, hy - 1)
    put(sp['hotbar_offhand_left.png'], hx - 29, hy - 1)
    for i in range(10):
        put(sp['heart/container.png'], hx + i * 8, hy - 13)
        if i < 7: put(sp['heart/full.png'], hx + i * 8, hy - 13)
        elif i == 7: put(sp['heart/half.png'], hx + i * 8, hy - 13)
    for i in range(10):
        x = hx + 182 - i * 8 - 9
        put(sp['food_empty.png'], x, hy - 13)
        if i < 6: put(sp['food_full.png'], x, hy - 13)
        elif i == 6: put(sp['food_half.png'], x, hy - 13)
    can.resize((can.width * E // S, can.height * E // S), Image.NEAREST).save(path)


if __name__ == '__main__':
    base = Path(sys.argv[1]) if len(sys.argv) > 1 else OUT
    print(generate(base))
