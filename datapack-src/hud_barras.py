"""HUD Astral: hotbar azul noche con herrajes dorados biselados y gema, barras de vida y comida (dibujo propio).

Sigue la imagen de referencia del dueno (13/11, segunda version). Todo es vanilla, sin mods:
- hotbar: casilleros de acero azulado con separadores oscuros, liston dorado arriba al centro con gema verde,
  escuadras doradas en las puntas (brazo arriba cortado en diagonal y canto que termina en punta) y filete abajo.
  El dorado es metal biselado: cara naranja arriba, linea amarilla en el canto, caras terracota y sombra roja.
- seleccion: marco dorado biselado sin gema, con muesca para que se vea la gema del centro de la barra.
- mano izquierda: casillero con marco dorado biselado en inglete.
- Vida y comida: cada corazon o muslo es un tramo de un tubo de acero con el relleno fino rojo o naranja
  (10 tramos = una barra continua). AstralDecor fija la escala de vida del cliente en 20: siempre UNA barra.
- Armadura: petos plateados. Burbujas: aros celestes.
Lo que no se puede en vanilla: adornos fuera de cada sprite (volutas, puntas de las barras, casilla del
cofre) ni mover armadura y burbujas al centro.

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
S = 2   # texeles por pixel de la interfaz; todo se dibuja en texeles


def c(h):
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255)


NADA = (0, 0, 0, 0)
BORDE = c('171926')                                    # contorno casi negro
NOCHE_OSC, NOCHE_SOMBRA, NOCHE = c('1c2030'), c('242b3c'), c('2b3447')
ACERO_OSC, ACERO, ACERO_CLARO = c('46576f'), c('5f7289'), c('7d92ab')
# dorado biselado: cara de arriba, canto brillante, caras laterales, cara de abajo y sombra
ORO, ORO_CLARO, TERRA, ORO_BAJO, ORO_SOMBRA = c('e0903a'), c('f2d264'), c('c0623a'), c('c87830'), c('8f3430')
GEMA_OSC, GEMA_MED, GEMA, GEMA_CLARA, GEMA_BORDE = c('2a8040'), c('3fa048'), c('4fb050'), c('86d874'), c('1f5a40')


class Lienzo:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.im = Image.new('RGBA', (w, h), NADA); self.px = self.im.load()

    def p(self, x, y, col):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.px[x, y] = col

    def rect(self, x0, y0, x1, y1, col):
        """Rectangulo con extremos incluidos."""
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.p(x, y, col)

    def anillo(self, x0, y0, x1, y1, col):
        self.rect(x0, y0, x1, y0, col); self.rect(x0, y1, x1, y1, col)
        self.rect(x0, y0, x0, y1, col); self.rect(x1, y0, x1, y1, col)

    def espejo(self):
        """Copia la mitad izquierda sobre la derecha."""
        for y in range(self.h):
            for x in range(self.w // 2):
                self.px[self.w - 1 - x, y] = self.px[x, y]


def casillero(l, ox, oy, w=36, h=36):
    """Casillero: aro de acero oscuro, canto claro arriba y a los lados, fondo azul noche con sombra."""
    x1, y1 = ox + w - 1, oy + h - 1
    l.rect(ox, oy, x1, y1, ACERO_OSC)
    l.rect(ox + 1, oy + 1, x1 - 1, y1 - 1, ACERO_CLARO)
    l.rect(ox + 1, y1 - 1, x1 - 1, y1 - 1, ACERO)                                  # canto de abajo, mas apagado
    l.rect(ox + 2, oy + 2, x1 - 2, y1 - 2, NOCHE)
    l.rect(ox + 2, oy + 2, x1 - 2, oy + 3, NOCHE_SOMBRA); l.rect(ox + 2, oy + 2, ox + 3, y1 - 2, NOCHE_SOMBRA)
    for x, y in ((ox, oy), (x1, oy), (ox, y1), (x1, y1)):                          # esquinas redondeadas
        l.p(x, y, BORDE)


def marco_oro(l, x0, y0, x1, y1, g=3):
    """Marco dorado biselado en inglete: g texeles de cara y un canto amarillo por dentro."""
    l.anillo(x0, y0, x1, y1, BORDE)
    for i in range(1, g + 1):
        l.rect(x0 + i, y0 + i, x1 - i, y0 + i, ORO)                                # cara de arriba
        l.rect(x0 + i, y1 - i, x1 - i, y1 - i, ORO_BAJO)                           # cara de abajo
        l.rect(x0 + i, y0 + i, x0 + i, y1 - i, TERRA)                              # caras laterales
        l.rect(x1 - i, y0 + i, x1 - i, y1 - i, TERRA)
    i = g + 1
    l.anillo(x0 + i, y0 + i, x1 - i, y1 - i, ORO_CLARO)                            # canto brillante
    for k in range(1, g + 1):                                                      # ingletes
        l.p(x0 + k, y0 + k, ORO_CLARO); l.p(x1 - k, y0 + k, ORO_CLARO)
        l.p(x0 + k, y1 - k, ORO_SOMBRA); l.p(x1 - k, y1 - k, ORO_SOMBRA)
    l.anillo(x0 + i + 1, y0 + i + 1, x1 - i - 1, y1 - i - 1, BORDE)


def gema(l, cx, y, n=7):
    """Rombo verde facetado, engarce oscuro con puntas doradas: 2n de ancho, 2n-1 de alto; cx = texel izquierdo del centro."""
    filas = list(range(1, n + 1)) + list(range(n - 1, 0, -1))
    for i, medio in enumerate(filas):
        x0, x1 = cx - medio + 1, cx + medio
        l.rect(x0 - 1, y + i, x1 + 1, y + i, BORDE)
        l.rect(x0, y + i, x1, y + i, (ORO if i < n else ORO_BAJO) if medio <= 2 else GEMA_BORDE)
        if medio == n:
            l.rect(x0, y + i, x0 + 1, y + i, ORO); l.rect(x1 - 1, y + i, x1, y + i, ORO)
        for x in range(x0 + 1, x1):
            if medio > 2:
                arriba, izq = i < n - 1, x <= cx
                l.p(x, y + i, GEMA_CLARA if arriba and izq else GEMA if arriba else GEMA_MED if izq else GEMA_OSC)
    l.rect(cx - 1, y + n - 3, cx, y + n - 3, c('d8ffc8'))                          # destello
    l.rect(cx, y + len(filas), cx + 1, y + len(filas), BORDE)


def hotbar():
    l = Lienzo(364, 44)
    l.rect(0, 0, 363, 43, BORDE)
    l.rect(1, 1, 362, 3, NOCHE_OSC)                       # franja de arriba
    l.rect(1, 40, 362, 40, NOCHE_OSC)                     # repisa
    for i in range(9):
        casillero(l, 4 + 40 * i, 4)
    for i in range(1, 9):                                 # tope de acero bajo cada separador
        l.rect(40 * i + 1, 40, 40 * i + 2, 40, ACERO_OSC)
    d = Lienzo(364, 44)                                   # herrajes en capa aparte: se espejan sin tocar los casilleros
    d.rect(1, 41, 181, 41, ORO_BAJO); d.rect(1, 42, 181, 42, ORO_SOMBRA); d.rect(110, 41, 181, 41, ORO_CLARO)   # filete
    d.rect(100, 41, 103, 41, ORO_CLARO); d.rect(106, 41, 107, 41, ORO_CLARO)
    # escuadra de la punta: canto vertical que termina en punta abajo
    for y in range(1, 43):
        ancho = 6 if y <= 30 else max(1, 6 - (y - 30) // 2)
        cols = (TERRA, TERRA, TERRA, ORO_CLARO, ORO_SOMBRA, ORO_SOMBRA)[:ancho]
        for k, col in enumerate(cols):
            d.p(1 + k, y, col)
        if ancho < 6:
            d.p(ancho, y, ORO_CLARO); d.p(1 + ancho, y, BORDE); d.p(2 + ancho, y, BORDE)
    # brazo de arriba, cortado en diagonal (mas largo arriba)
    for k, col in enumerate((ORO, ORO, ORO, ORO_CLARO, ORO_SOMBRA, ORO_SOMBRA)):
        x0, x1 = (1 if k < 3 else 4 if k == 3 else 5), 34 - 2 * k
        d.rect(x0, 1 + k, x1, 1 + k, col); d.rect(x1 + 1, 1 + k, x1 + 2, 1 + k, BORDE)
    d.rect(7, 7, 22, 7, BORDE)
    d.p(1, 1, ORO_CLARO); d.p(2, 2, ORO_CLARO); d.p(3, 3, ORO_CLARO); d.p(33, 1, ORO_CLARO); d.p(34, 1, ORO_CLARO)
    # liston del centro: cara naranja, canto amarillo y sombra roja; punta en diagonal (mas largo abajo)
    for k, col in enumerate((ORO, ORO, ORO_CLARO, ORO_CLARO, ORO_SOMBRA, ORO_SOMBRA)):
        x0 = 88 - 2 * k
        d.rect(x0, 1 + k, 181, 1 + k, col); d.rect(x0 - 2, 1 + k, x0 - 1, 1 + k, BORDE)
    d.rect(88, 1, 91, 1, ORO_CLARO); d.rect(86, 2, 87, 2, ORO_CLARO)             # brillo en la punta
    d.rect(76, 7, 181, 7, BORDE)
    for i in range(2, 5):                                 # el casillero asoma su canto claro bajo el liston
        x = 4 + 40 * i
        d.rect(x + 1, 8, x + 34, 8, ACERO_CLARO)
    d.espejo()
    l.im.alpha_composite(d.im)
    gema(l, 181, 0)
    return l.im


def seleccion():
    """48x46; se dibuja 2 texeles arriba y a la izquierda de la barra. El casillero queda en 6..41."""
    l = Lienzo(48, 46)
    marco_oro(l, 1, 1, 46, 44, 3)
    l.rect(7, 7, 40, 38, NADA)
    l.rect(15, 0, 32, 6, NADA)                            # muesca: en el casillero del medio deja ver la gema
    l.rect(14, 1, 14, 6, BORDE); l.rect(33, 1, 33, 6, BORDE)
    return l.im


def mano_izquierda(derecha=False):
    """58x48; casillero con marco dorado biselado y un eslabon hacia la barra."""
    l = Lienzo(58, 48)
    marco_oro(l, 0, 2, 43, 45, 3)
    casillero(l, 5, 7, 34, 34)
    l.rect(44, 21, 57, 26, BORDE)                         # eslabon
    l.rect(44, 22, 57, 22, ORO); l.rect(44, 23, 57, 23, ORO_CLARO); l.rect(44, 24, 57, 25, TERRA)
    l.rect(48, 19, 53, 28, BORDE); l.rect(49, 20, 52, 27, TERRA); l.rect(49, 20, 52, 21, ORO)
    l.rect(50, 22, 50, 26, ORO_CLARO); l.rect(49, 27, 52, 27, ORO_SOMBRA)
    return l.im.transpose(Image.FLIP_LEFT_RIGHT) if derecha else l.im


# ---------------------------------------------------------------- barras (corazones y comida como tramos de tubo)
TUBO_ARRIBA, TUBO_LUZ, TUBO_MED, TUBO_CANAL, TUBO_ABAJO = c('3f4f66'), c('8ca0b8'), c('3a485e'), c('1a1f2e'), c('4a5c74')
FILAS_TUBO = (BORDE, TUBO_ARRIBA, TUBO_ARRIBA, TUBO_LUZ, TUBO_MED, TUBO_CANAL,
              None, None, None, None, None, TUBO_CANAL,    # canal del relleno: filas 6 a 10
              TUBO_ABAJO, TUBO_ABAJO, NOCHE_SOMBRA, NOCHE_SOMBRA, NOCHE_OSC, BORDE)


def _tubo(canal):
    """Tramo vacio de 18x18: tubo de acero con brillo arriba y el canal del color dado."""
    l = Lienzo(18, 18)
    for y, col in enumerate(FILAS_TUBO):
        l.rect(0, y, 17, y, col or canal)
    return l.im


def _relleno(colores, desde=0, hasta=17):
    """Relleno fino del canal (filas 6 a 10), de lado a lado para que la barra se vea continua."""
    claro, medio, oscuro = colores
    l = Lienzo(18, 18)
    for y, col in zip(range(6, 11), (oscuro, medio, claro, medio, oscuro)):
        l.rect(desde, y, hasta, y, col)
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


VIDA = {'': (196, 16, 20), 'poisoned_': (90, 170, 40), 'withered_': (70, 64, 64), 'frozen_': (150, 210, 245),
        'absorbing_': (240, 195, 60)}
COMIDA = {'': (216, 100, 32), '_hunger': (125, 150, 55)}


def _tres(rgb):
    return (_tono(rgb, 1.25), _tono(rgb, 1.0), _tono(rgb, 0.62))


def barras():
    out = {}
    for var, rgb in VIDA.items():
        for hc in ('', 'hardcore_'):
            for parte, hasta in (('full', 17), ('half', 8)):
                im = _relleno(_tres(rgb), 0, hasta)
                out[f'heart/{var}{hc}{parte}.png'] = im
                out[f'heart/{var}{hc}{parte}_blinking.png'] = _brillo(im)
    for hc in ('', '_hardcore'):
        out[f'heart/container{hc}.png'] = _tubo(TUBO_CANAL)
        out[f'heart/container{hc}_blinking.png'] = _brillo(_tubo(TUBO_CANAL), 60)
    out['heart/vehicle_container.png'] = _tubo(TUBO_CANAL)
    out['heart/vehicle_full.png'] = _relleno(_tres((200, 90, 60)))
    out['heart/vehicle_half.png'] = _relleno(_tres((200, 90, 60)), 0, 8)
    for var, rgb in COMIDA.items():
        out[f'food_full{var}.png'] = _relleno(_tres(rgb))
        out[f'food_half{var}.png'] = _relleno(_tres(rgb), 9, 17)     # se vacia por la izquierda
        out[f'food_empty{var}.png'] = _tubo(TUBO_CANAL)
    return out


# ---------------------------------------------------------------- armadura (petos) y burbujas (aros)
PETO = ('..................',
        '..................',
        '..###......###....',
        '.#aaa#....#aaa#...',
        '.#aaaa####aaaa#...',
        '.#aaaaaaaaaaaa#...',
        '.#abbbbbbbbbba#...',
        '.#abbbbbbbbbbb#...',
        '.#bbbbbbbbbbbb#...',
        '.#bbbbbbbbbbbb#...',
        '.#bbbbbbbbbbcc#...',
        '..#bbbbbbbbcc#....',
        '..#bbbbbbbccc#....',
        '...#bbbbbccc#.....',
        '....#cccccc#......',
        '.....######.......',
        '..................',
        '..................')


def _peto(izq, der):
    """izq y der: paletas (a, b, c) de cada mitad."""
    l = Lienzo(18, 18)
    for y, fila in enumerate(PETO):
        for x, ch in enumerate(fila):
            if ch == '#':
                l.p(x + 1, y, BORDE)
            elif ch != '.':
                l.p(x + 1, y, (izq if x < 8 else der)['abc'.index(ch)])
    return l.im


def armadura():
    plata = (c('dfe6ee'), c('a4b0c2'), c('6b778c'))
    vacio = (NOCHE, NOCHE_SOMBRA, NOCHE_OSC)
    return {'armor_full.png': _peto(plata, plata), 'armor_half.png': _peto(plata, vacio),
            'armor_empty.png': _peto(vacio, vacio)}


def _aro(aro, luz, centro, roto=False):
    l = Lienzo(18, 18)
    for y in range(18):
        for x in range(18):
            dx, dy = x - 8.5, y - 8.5
            r2 = dx * dx + dy * dy
            if r2 > 7.2 ** 2:
                continue
            if roto and (abs(dx) < 1.6 or abs(dy) < 1.6):
                continue
            if r2 > 6.1 ** 2:
                l.p(x, y, BORDE)
            elif r2 > 3.4 ** 2:
                l.p(x, y, luz if dx + dy < -4 else aro)
            elif not roto:
                l.p(x, y, BORDE if r2 > 2.4 ** 2 else centro)
    return l.im


def burbujas():
    return {'air.png': _aro(c('86bcd6'), c('d2f0fa'), NOCHE),
            'air_bursting.png': _aro(c('86bcd6'), c('d2f0fa'), NOCHE, roto=True),
            'air_empty.png': _aro(ACERO_OSC, ACERO_OSC, NOCHE_OSC)}


def sprites():
    out = {'hotbar.png': hotbar(), 'hotbar_selection.png': seleccion(),
           'hotbar_offhand_left.png': mano_izquierda(), 'hotbar_offhand_right.png': mano_izquierda(True)}
    out.update(barras()); out.update(armadura()); out.update(burbujas())
    return out


def generate(base=OUT):
    for rel, im in sprites().items():
        d = Path(base) / 'assets/minecraft/textures/gui/sprites/hud' / rel
        d.parent.mkdir(parents=True, exist_ok=True); im.save(d)
    return base


def preview(path, elegido=2):
    """Simulacion del HUD a 4x: hotbar, mano izquierda, vida 7.5/10, comida 6.5/10, armadura y burbujas."""
    sp = sprites(); E = 4
    W, H = 182 + 60, 62
    can = Image.new('RGBA', (W * S, H * S), (30, 30, 34, 255))
    def put(im, x, y):
        can.alpha_composite(im, (round(x * S), round(y * S)))
    hx, hy = 40, 38
    put(sp['hotbar.png'], hx, hy); put(sp['hotbar_selection.png'], hx - 1 + 20 * elegido, hy - 1)
    put(sp['hotbar_offhand_left.png'], hx - 29, hy - 1)
    for i in reversed(range(10)):
        put(sp['heart/container.png'], hx + i * 8, hy - 17)
        if i < 7: put(sp['heart/full.png'], hx + i * 8, hy - 17)
        elif i == 7: put(sp['heart/half.png'], hx + i * 8, hy - 17)
        put(sp['armor_full.png' if i < 6 else 'armor_half.png' if i == 6 else 'armor_empty.png'], hx + i * 8, hy - 27)
    for i in range(10):
        x = hx + 182 - i * 8 - 9
        put(sp['food_empty.png'], x, hy - 17)
        if i < 6: put(sp['food_full.png'], x, hy - 17)
        elif i == 6: put(sp['food_half.png'], x, hy - 17)
        put(sp['air.png' if i < 7 else 'air_bursting.png' if i == 7 else 'air_empty.png'], x, hy - 27)
    can.resize((can.width * E // S, can.height * E // S), Image.NEAREST).save(path)


if __name__ == '__main__':
    base = Path(sys.argv[1]) if len(sys.argv) > 1 else OUT
    print(generate(base))
