"""Tanda 3c: maquinas de Mini juegos (diseno propio, paleta Astral) a 16 px por bloque."""
import random
from bbmodel import Model, hexc, uid, swing

V = '#7b3fe4'; VD = '#4a2296'; VDD = '#2a1458'; B = '#3a5bd9'; BD = '#263c96'
C = '#3ef0ff'; G = '#f2c230'; GD = '#b8860f'; K = '#15121f'; W = '#ffffff'; MG = '#ff4fa3'; R = '#ff3b5c'


def rgba(c, a=255):
    if isinstance(c, str):
        return hexc(c) + (a,)
    return tuple(c) + (a,) if len(c) == 3 else tuple(c)


class Face:
    """Lienzo de una cara: (0,0) arriba a la izquierda, como se ve desde afuera."""
    def __init__(self, px, x0, y0, w, h, cube, face):
        self._px, self.x0, self.y0, self.w, self.h, self.cube, self.face = px, x0, y0, w, h, cube, face

    def get(self, x, y):
        return self._px[self.x0 + x, self.y0 + y]

    def set(self, x, y, c, a=255):
        if 0 <= x < self.w and 0 <= y < self.h:
            self._px[self.x0 + x, self.y0 + y] = rgba(c, a)

    def rect(self, x, y, w, h, c, a=255):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, c, a)

    def fill(self, c, a=255):
        self.rect(0, 0, self.w, self.h, c, a)

    def rows(self, rows, pal, ox=0, oy=0):
        for yy, row in enumerate(rows):
            for xx, ch in enumerate(row):
                if ch in pal:
                    self.set(ox + xx, oy + yy, pal[ch])

    def world(self, x, y):
        """Centro del pixel en coordenadas del modelo (solo caras laterales): (eje horizontal, altura)."""
        a, b = self.cube['from'], self.cube['to']
        yy = b[1] - (y + .5) * (b[1] - a[1]) / self.h
        t = (x + .5) / self.w
        if self.face == 'east':
            return b[2] - t * (b[2] - a[2]), yy
        if self.face == 'west':
            return a[2] + t * (b[2] - a[2]), yy
        if self.face == 'north':
            return b[0] - t * (b[0] - a[0]), yy
        return a[0] + t * (b[0] - a[0]), yy


class PixelModel(Model):
    """Model con pintura por cara (art={cara: funcion(Face)}) y caja de clic de BetterModel."""
    def __init__(self, name, hitbox=None):
        super().__init__(name)
        self.art = {}
        self.hitbox = hitbox
        self.nametag = True

    def cube(self, bone, frm, to, color, art=None, **kw):
        super().cube(bone, frm, to, color, **kw)
        if art:
            self.art[len(self.cubes) - 1] = art

    def _paint(self, size, pos):
        img = super()._paint(size, pos)
        px = img.load()
        for (i, face), (x0, y0, w, h) in pos.items():
            fn = self.art.get(i, {}).get(face) or self.art.get(i, {}).get('*')
            if fn:
                fn(Face(px, x0, y0, w, h, self.cubes[i], face))
        return img

    def export(self):
        if self.nametag and 'mtag_nombre' not in self.bones:
            # Hueso 'mtag_' de BetterModel: ahi dibuja el nombre del mob, arriba de todo el modelo.
            top = max(max(c['from'][1], c['to'][1]) for c in self.cubes)
            self.bone('mtag_nombre', (0, top + 3, 0), self.order[0])
        data, img = super().export()
        if self.hitbox:
            lo, hi = self.hitbox
            cid = uid(self.name + '/hitbox/cube'); gid = uid(self.name + '/hitbox/group')
            data['elements'].append({'name': 'astral_hitbox', 'type': 'cube', 'uuid': cid, 'from': list(lo), 'to': list(hi),
                                     'origin': [0, 0, 0], 'faces': {f: {'uv': [0, 0, 0, 0], 'texture': None}
                                                                    for f in ('north', 'south', 'east', 'west', 'up', 'down')}})
            group = dict(name='b_astral_hitbox', uuid=gid, origin=[0, 0, 0], rotation=[0, 0, 0], children=[cid])
            data['groups'].append(group)
            data['outliner'].append(group)
        return data, img


def shade(c, k):
    return tuple(max(0, min(255, int(v * k))) for v in hexc(c) if True) if isinstance(c, str) else tuple(max(0, min(255, int(v * k))) for v in c[:3])


def star(f, cx, cy, core=W, col=G):
    for dx, dy in ((0, -2), (0, 2), (-2, 0), (2, 0), (-1, 0), (1, 0), (0, -1), (0, 1)):
        f.set(cx + dx, cy + dy, col)
    f.set(cx, cy, core)


# ------------------------------------------------------------------ arcade
def arcade_side(f):
    """Grafica lateral continua entre las piezas: franja azul con filo cian, linea dorada y estrella."""
    rng = random.Random(f'{f.cube["from"]}{f.face}')
    for y in range(f.h):
        for x in range(f.w):
            z, wy = f.world(x, y)
            d = wy + z * 0.9
            if 13 <= d < 18:
                c = B
            elif 12 <= d < 13 or 18 <= d < 19:
                c = C
            elif 21 <= d < 22:
                c = G
            elif wy < 3.2:
                c = VDD
            else:
                c = V
            k = 0.86 + 0.2 * wy / 32 + rng.uniform(-.035, .035)
            if c in (C, G):
                k = 1
            f.set(x, y, shade(c, k))
    # estrella dorada abajo y destellos arriba, en coordenadas del modelo
    for sz, sy, big in ((2.5, 8.5, True), (4.5, 29.5, False), (-3.5, 24.5, False)):
        for y in range(f.h):
            for x in range(f.w):
                z, wy = f.world(x, y)
                dz, dy = abs(z - sz), abs(wy - sy)
                if big and ((dz < .5 and dy < 2.5) or (dy < .5 and dz < 2.5) or (dz < 1.5 and dy < 1.5)):
                    f.set(x, y, W if dz < .5 and dy < .5 else G)
                elif not big and dz < .5 and dy < .5:
                    f.set(x, y, W)


SCREEN = ["kkkkkkkkkkkk",
          "kgg.....w.wk",
          "k.mm.mm.mm.k",
          "k.mm.mm.mm.k",
          "k..........k",
          "k..yy.yy.s.k",
          "k.s...w....k",
          "k..........k",
          "k....cc....k",
          "k...cccc...k",
          "kkkkkkkkkkkk"]
MARQUEE = ["GGGGGGGGGGGG",
           "GvcvvwYvvcvG",
           "GvvcvYwvcvvG",
           "GGGGGGGGGGGG"]
COINDOOR = ["dddddddddddd",
            "vvvvvvvvvvvv",
            "vGGGGvvGGGGv",
            "vGkkGvvGkkGv",
            "vGrrGvvGrrGv",
            "vGYYGvvGYYGv",
            "vGkkGvvGkkGv",
            "vGGGGvvGGGGv",
            "vvvvvvvvvvvv",
            "vkckckckckcv",
            "vvvvvvvvvvvv",
            "dddddddddddd"]
PAL = {'k': K, '.': '#111c55', 'g': G, 'm': MG, 'y': G, 'w': W, 'c': C, 's': '#5f7cff', 'G': G, 'v': V, 'Y': '#fff2a8',
       'd': VDD, 'r': R, 'b': B}


def arcade():
    m = PixelModel('astral_maquina_arcade', hitbox=((-7, 0, -7), (7, 32, 7)))
    m.bone('body', (0, 0, 0))
    m.cube('body', (-7, 0, -5.5), (7, 2, 7), K)
    # laterales con el perfil clasico: base, tablero salido, pantalla hundida y marquesina adelantada
    neon = []
    for x0, x1, f in ((-7, -6, 'west'), (6, 7, 'east')):
        for (z0, y0, y1) in ((-5, 2, 14), (-9, 14, 17), (-3, 17, 27), (-7, 27, 32)):
            m.cube('body', (x0, y0, z0), (x1, y1, 7), V,
                   art={f: arcade_side, 'north': lambda fc: fc.fill(C), 'up': lambda fc: fc.fill(shade(V, .8))})
            neon.append(((x0, y0, z0 - .15), (x1, y1, z0)))
    # cuerpo interior
    m.cube('body', (-6, 2, -4.5), (6, 14, 6.5), VD, art={'north': lambda f: f.rows(COINDOOR, PAL)})

    def deck_top(f):
        f.fill(K)
        f.rect(0, 0, f.w, 1, G)
        f.rect(1, 2, 4, 3, '#221c38'); f.rect(6, 2, 6, 3, '#221c38')

    def deck_front(f):
        f.fill(VD); f.rect(0, 1, f.w, 1, C)
        f.set(2, 2, G); f.set(9, 2, G)
    m.cube('body', (-6, 14, -8.5), (6, 16.5, 6.5), K, art={'up': deck_top, 'north': deck_front})
    m.cube('body', (-6, 16.5, -.8), (6, 27, 6.5), K)
    m.cube('body', (-6, 27, -6.5), (6, 31.5, 6.5), VDD)
    m.cube('body', (-6, 31.5, -6.8), (6, 32, 6.5), K, art={'up': lambda f: f.fill(VDD)})

    def back(f):
        f.fill(shade(VD, .8))
        for y in range(3, f.h - 3, 2):
            f.rect(3, y, f.w - 6, 1, K)
    m.cube('body', (-6, 2, 6.5), (6, 32, 7), VD, art={'south': back})
    # pantalla inclinada hacia atras, con su propio hueso para darle brillo maximo
    m.bone('pantalla', (0, 16.5, -3), 'body', rotation=(12, 0, 0))
    m.cube('pantalla', (-6, 16.5, -3), (6, 26.7, -2), K, art={'north': lambda f: f.rows(SCREEN, PAL)})
    # marquesina iluminada y luz inferior
    m.bone('marquesina', (0, 29, -6.5), 'body')
    m.cube('marquesina', (-6, 27.5, -6.9), (6, 31, -6.5), G, art={'north': lambda f: f.rows(MARQUEE, PAL)})
    m.cube('marquesina', (-5, 26.8, -6), (5, 27, -1.5), '#dffcff', art={'*': lambda f: f.fill('#dffcff')})
    # filos de neon cian al frente de los laterales (hueso propio para el brillo)
    m.bone('neon', (0, 16, -5), 'body')
    for a, b in neon:
        m.cube('neon', a, b, C, art={'*': lambda f: f.fill(C)})
    # palanca y botones
    m.cube('body', (-4.2, 16.5, -7.2), (-1.8, 17, -4.8), '#2b2540')
    m.bone('palanca', (-3, 17, -6), 'body')
    m.cube('palanca', (-3.35, 17, -6.35), (-2.65, 19.2, -5.65), '#c9c9d6')
    m.cube('palanca', (-3.9, 19, -6.9), (-2.1, 20.8, -5.1), R, art={'*': lambda f: (f.fill(R), f.set(0, 0, '#ff9db0'))})
    m.bone('botones', (2.5, 16.5, -6), 'body')
    for x, z, col in ((.3, -7.3, C), (2.3, -6.3, G), (4.3, -7.3, MG), (.3, -5, MG), (4.3, -5, C)):
        m.cube('botones', (x, 16.5, z), (x + 1.4, 17, z + 1.4), col, art={'*': lambda f, col=col: f.fill(col)})
    # luces del techo
    m.bone('luces', (0, 32, -5.5), 'body')
    for x, col in ((-6.5, C), (4.5, G)):
        m.cube('luces', (x, 32, -6.5), (x + 2, 33.5, -4.5), col,
               art={'*': lambda f, col=col: (f.fill(col), f.set(0, 0, W))})
    m.anim('idle', 4, {'palanca': {'rotation': (swing(14, .5), 0, swing(18, .75, 40))},
                       'luces': {'scale': ('1+math.sin(q.anim_time*360)*0.15',) * 3},
                       'botones': {'position': (0, 'math.min(0, math.sin(q.anim_time*720))*0.25', 0)}})
    return m


# ------------------------------------------------------------------ capsulas (gashapon)
CAPS = [V, C, G, MG, B, '#5fe36a', R, '#ff9a3d']


def glass(top=False, ring=None):
    """Vidrio celeste: casi transparente al medio, mas marcado en los bordes, con un reflejo en diagonal."""
    def fn(f):
        rng = random.Random(f'{f.cube["from"]}{f.face}')
        for y in range(f.h):
            for x in range(f.w):
                edge = x in (0, f.w - 1) or y in (0, f.h - 1)
                if f.face in ('up', 'down'):
                    if f.face == 'down' or not top:
                        inside = ring is not None and ring <= x < f.w - ring and ring <= y < f.h - ring
                        if f.face == 'down' or inside:
                            f.set(x, y, (0, 0, 0), 0)
                            continue
                    f.set(x, y, (205, 246, 255), 120 if edge else 50)
                    continue
                a = 125 if edge else 38 + rng.randrange(8)
                col = (232, 252, 255) if edge else (176, 236, 255)
                if not edge and (x + y) % 9 in (2, 3) and y < f.h * .7 and x < f.w * .6:
                    col, a = (255, 255, 255), 120
                f.set(x, y, col, a)
    return {'*': fn}


def capsule(m, bone, x, y, z, col, rot=0, s=3.0):
    def art(f, col=col):
        half = f.h // 2
        if f.face == 'up':
            f.fill(shade(col, 1.12)); f.set(1, 1, W); return
        if f.face == 'down':
            f.fill('#d9d4e6'); return
        f.rect(0, 0, f.w, half, col); f.rect(0, half, f.w, f.h - half, '#f1eefa')
        f.rect(0, half, f.w, 1, shade(col, .6))
        f.set(0, 0, shade(col, 1.35)); f.set(f.w - 1, f.h - 1, '#c6c0d8')
    m.cube(bone, (x - s / 2, y, z - s / 2), (x + s / 2, y + s, z + s / 2), col, art={'*': art},
           rotation=(0, rot, 0) if rot else None)


BODY_FRONT = ["GGGGGGGGGGGG",
              "bllllllllllb",
              "blwwwwwwwwlb",
              "blwwwwwwkGlb",
              "blwwwwwwkGlb",
              "blwwwwwwwwlb",
              "blwwwwwwwwlb",
              "bllllllllllb",
              "bbbbbbbbbbbb",
              "bbvvvvvvvvbb",
              "bbvkkkkkkvbb",
              "bbvkkkkkkvbb"]
BPAL = {'G': G, 'b': B, 'l': '#9db4ff', 'w': '#e9e4ff', 'k': K, 'v': V}


def capsulas():
    m = PixelModel('astral_maquina_capsulas', hitbox=((-6.5, 0, -6.5), (6.5, 30, 6.5)))
    m.bone('body', (0, 0, 0))
    m.cube('body', (-6, 0, -6), (6, 2, 6), K)

    def side(f):
        rng = random.Random(f.face)
        for y in range(f.h):
            for x in range(f.w):
                c = G if y == 0 else V if 7 <= y <= 8 else C if y in (6, 9) else B
                f.set(x, y, shade(c, 1 if c in (G, C) else 1.05 - .16 * y / f.h + rng.uniform(-.03, .03)))
        cx = f.w // 2
        for dy in range(-2, 3):
            for dx in range(-(2 - abs(dy)), 3 - abs(dy)):
                f.set(cx + dx, 3 + dy, W if (dx, dy) == (0, 0) else G)
    m.cube('body', (-6, 2, -6), (6, 14, 6), B, art={'north': lambda f: f.rows(BODY_FRONT, BPAL), 'east': side, 'west': side, 'south': side})
    # columnas violetas en las esquinas
    for x in (-6.5, 5.5):
        for z in (-6.5, 5.5):
            m.cube('body', (x, 0, z), (x + 1, 14, z + 1), V,
                   art={'*': lambda f: [f.set(xx, yy, shade(V, 1.1 - .25 * yy / f.h)) for yy in range(f.h) for xx in range(f.w)]})
    # capsula asomando en la boca de premios
    capsule(m, 'body', 1.2, 2.1, -5.6, C, rot=22.5, s=2.2)
    # aro dorado
    m.cube('body', (-6.5, 14, -6.5), (6.5, 15.5, 6.5), G,
           art={'*': lambda f: (f.fill(G), f.rect(0, f.h - 1, f.w, 1, GD), f.rect(0, 0, f.w, 1, '#ffe27a')) if f.face not in ('up', 'down') else f.fill(GD)})
    # perilla que gira
    m.bone('perilla', (-1, 9.5, -6), 'body')
    m.cube('perilla', (-3, 7.5, -7), (1, 11.5, -6), '#f4f1ff',
           art={'north': lambda f: (f.fill('#f4f1ff'), f.rect(0, 0, 1, 1, B), f.rect(3, 0, 1, 1, B), f.rect(0, 3, 1, 1, B), f.rect(3, 3, 1, 1, B),
                                    f.rect(1, 1, 2, 2, C))})
    m.cube('perilla', (-3.5, 9, -7.8), (1.5, 10, -7), G, art={'*': lambda f: (f.fill(G), f.set(0, 0, '#ffe27a'))})
    # cupula: primero las capsulas (opacas) y despues el vidrio, en el mismo hueso
    m.bone('cupula', (0, 21, 0), 'body')
    m.cube('cupula', (-4.6, 15.5, -4.6), (4.6, 15.7, 4.6), '#ece8f8')
    rng = random.Random(7)
    n = 0
    for x in (-3.1, 0, 3.1):
        for z in (-3.1, 0, 3.1):
            capsule(m, 'cupula', x + rng.uniform(-.15, .15), 15.7, z + rng.uniform(-.15, .15), CAPS[(n * 3) % len(CAPS)],
                    rot=rng.choice((0, 22.5, -22.5, 45)), s=2.9)
            n += 1
    for x, z in ((-3.2, -3.2), (3.2, -3.2), (-3.2, 3.2), (3.2, 3.2), (0, -3.6), (0, 3.6), (-3.6, 0), (3.6, 0), (0, 0)):
        capsule(m, 'cupula', x, 18.5, z, CAPS[(n * 5 + 1) % len(CAPS)], rot=rng.choice((0, 22.5, -22.5, 45)), s=2.9)
        n += 1
    for x, z in ((-1.7, -1.7), (1.7, -1.7), (-1.7, 1.7), (1.7, 1.7)):
        capsule(m, 'cupula', x, 21.3, z, CAPS[(n * 3 + 2) % len(CAPS)], rot=rng.choice((0, 22.5, 45)), s=2.9)
        n += 1
    m.cube('cupula', (-5, 15.5, -5), (5, 17.5, 5), C, art=glass())
    m.cube('cupula', (-6.5, 17.5, -6.5), (6.5, 25, 6.5), C, art=glass(top=True, ring=2))
    m.cube('cupula', (-5, 25, -5), (5, 27, 5), C, art=glass(top=True, ring=2))
    # tapa violeta con pomo dorado
    m.cube('body', (-3.5, 27, -3.5), (3.5, 28.5, 3.5), V,
           art={'*': lambda f: (f.fill(V), f.rect(0, f.h - 1, f.w, 1, VD)) if f.face not in ('up', 'down') else f.fill(shade(V, 1.1))})
    m.bone('pomo', (0, 28.5, 0), 'body')
    m.cube('pomo', (-1.2, 28.5, -1.2), (1.2, 30.5, 1.2), G, art={'*': lambda f: (f.fill(G), f.set(0, 0, W))})
    m.anim('idle', 6, {'perilla': {'rotation': (0, 0, 'math.clamp(math.sin(q.anim_time*60)*4-3,0,1)*360')},
                       'pomo': {'scale': ('1+math.sin(q.anim_time*120)*0.12',) * 3}})
    return m


MAQUINAS = [arcade, capsulas]


def _npcs():
    import npc_tanda3c
    return list(npc_tanda3c.NPCS)


ALL = list(MAQUINAS) + _npcs()
