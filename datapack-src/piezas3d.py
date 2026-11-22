# -*- coding: utf-8 -*-
"""Motor de modelos 3D de items (22/11/2026): taladros, motosierras, gomera y libros del Invocador.

Es el mismo sistema que los bastones y guadanas (varitas3d.py): cubos + una textura de "muestras" de 8x8 con
vetas, bisel y brillos animados. Cambios:
- hasta 64 muestras por modelo (textura de 64x64 por cuadro), asi cada pieza tiene sus propios tonos;
- cajas redondeadas y discos/octogonos para armar volumenes de verdad (no un dibujo plano ensanchado);
- el agarre se calcula: cada modelo dice donde esta el mango y en que direccion apunta, y la posicion en la mano
  (3ra y 1ra persona) sale de la cuenta de ItemInHandLayer / ItemInHandRenderer de Minecraft;
- vista previa con el inventario, la mano en 3ra persona y la vista en 1ra persona.

Medidas: 16 unidades = 1 bloque. Coordenadas validas -16..32. Giros de 22,5 grados en un solo eje.
"""
import io
import json
import math
import os
import random

from PIL import Image, ImageDraw

import varitas3d as v

FRAMES = v.FRAMES
FRAMETIME = v.FRAMETIME
TS = 8                # pixeles por muestra
GRID = 8              # muestras por fila
TEX = TS * GRID       # 64 px por cuadro
UVS = 16 / GRID       # unidades de UV por muestra
TEX_DIR = 'item/piezas3d'


def hx(h):
    return v.hx(h)


def mezclar(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def aclarar(c, t):
    return mezclar(c, (255, 255, 255), t)


def oscurecer(c, t):
    return mezclar(c, (0, 0, 0), t)


# ------------------------------------------------------------------------------------------- rotaciones
def rx(a):
    return v._rx(math.radians(a))


def ry(a):
    return v._ry(math.radians(a))


def rz(a):
    return v._rz(math.radians(a))


mul = v._mul
app = v._app


def rot_xyz(deg):
    """Matriz de un display de Minecraft: rotationXYZ = Rx * Ry * Rz."""
    return mul(mul(rx(deg[0]), ry(deg[1])), rz(deg[2]))


# ------------------------------------------------------------------------------------------- pieza
class Pieza:
    """Un modelo de item hecho de cubos.

    agarre: punto del modelo donde va el centro del puno.
    frente: direccion del modelo que apunta "hacia adelante" (canon, punta, hoja). arriba: lo que mira arriba.
    """

    def __init__(self, iid, name, palette, tex_dir=TEX_DIR, tex_name=None):
        self.iid = iid
        self.name = name
        self.palette = dict(palette)
        self.slots = {k: i for i, k in enumerate(self.palette)}
        assert len(self.slots) <= GRID * GRID, (iid, len(self.slots))
        self.tex_dir = tex_dir
        self.tex_name = tex_name or iid
        self.els = []
        self.agarre = (8, 8, 8)
        self.poses = {}        # contexto -> dict de display (lo arma cada familia)
        self.gui_rot = [20, 115, 0]

    # -------------------------------------------------------------- primitivas
    def box(self, a, b, sw, rot=None, glow=0):
        assert sw in self.slots, (self.iid, sw)
        a, b = [min(p, q) for p, q in zip(a, b)], [max(p, q) for p, q in zip(a, b)]
        if rot is not None and rot[1] == 0:
            rot = None
        self.els.append({'from': a, 'to': b, 'sw': sw, 'rot': rot, 'glow': glow})

    def cen(self, c, size, sw, rot=None, glow=0):
        """Caja centrada en c. rot=(eje, angulo) gira sobre su centro; (eje, angulo, origen) sobre otro punto."""
        a = [c[i] - size[i] / 2 for i in range(3)]
        b = [c[i] + size[i] / 2 for i in range(3)]
        if rot and len(rot) == 2:
            rot = (rot[0], rot[1], tuple(c))
        self.box(a, b, sw, rot, glow)

    def rbox(self, c, size, sw, r=None, glow=0, eje=None):
        """Caja con bordes redondeados (cajas encimadas que achaflanan las aristas).
        eje: solo redondea las aristas paralelas a ese eje ('x', 'y', 'z'); None las redondea todas."""
        if r is None:
            r = round(min(min(size) / 4, 1.5) * 4) / 4
        ax = {'x': 0, 'y': 1, 'z': 2}
        if eje is None:
            r = min(r, min(size) / 2 - 0.05)
        else:
            r = min(r, min(size[j] for j in range(3) if j != ax[eje]) / 2 - 0.05)
        if r < 0.2:
            self.cen(c, size, sw, glow=glow)
            return
        if eje is None:
            for k in range(3):
                self.cen(c, [size[j] if j == k else size[j] - 2 * r for j in range(3)], sw, glow=glow)
            return
        a = ax[eje]
        o = [j for j in range(3) if j != a]
        for k in o:
            self.cen(c, [size[j] if j in (a, k) else size[j] - 2 * r for j in range(3)], sw, glow=glow)

    def octo(self, c, r, largo, eje, sw, glow=0, lados=16):
        """Cilindro a lo largo de eje, radio r. lados=16: cruz recta + cruz girada 45 (4 cajas, casi redondo);
        lados=8: cruz recta + cuadrado girado (3 cajas)."""
        ax = {'x': 0, 'y': 1, 'z': 2}[eje]
        o = [j for j in range(3) if j != ax]
        ancho = 2 * r * 0.42
        for rot in ((0,), (0, 45))[lados == 16]:
            for k in o:
                s = [0, 0, 0]
                s[ax] = largo
                s[k] = 2 * r
                s[3 - ax - k] = ancho
                self.cen(c, s, sw, (eje, rot) if rot else None, glow)
        if lados != 16:
            s = [0, 0, 0]
            s[ax] = largo
            s[o[0]] = s[o[1]] = 2 * r * 0.75
            self.cen(c, s, sw, (eje, 45), glow)

    def disco(self, c, r, grosor, eje, sw, glow=0):
        """Disco plano (normal = eje) de radio r."""
        self.octo(c, r, grosor, eje, sw, glow)

    def gema(self, c, s, sw, eje='x', glow=15, largo=None):
        """Rombo: una caja girada 45 grados sobre eje (se ve como diamante desde ese costado)."""
        size = [s, s, s]
        size[{'x': 0, 'y': 1, 'z': 2}[eje]] = largo if largo is not None else s * 0.6
        self.cen(c, size, sw, (eje, 45), glow)

    def barra(self, p, q, w, sw, plano='yz', glow=0):
        """Barra de p a q en un plano (yz: gira sobre x; xy: gira sobre z; xz: gira sobre y). El angulo se
        redondea a 22,5 grados. Devuelve el punto final real."""
        i, j = {'yz': (1, 2), 'xy': (0, 1), 'xz': (0, 2)}[plano]
        k = 3 - i - j
        di, dj = q[i] - p[i], q[j] - p[j]
        ln = math.hypot(di, dj)
        ang = math.degrees(math.atan2(dj, di))
        ang = round(ang / 22.5) * 22.5
        r = ((ang + 90) % 180) - 90
        if abs(r) > 45:
            r = r - 90 if r > 0 else r + 90
            along = j
        else:
            along = i
        c = [(p[t] + q[t]) / 2 for t in range(3)]
        size = [w, w, w]
        size[along] = ln + w * 0.4
        eje = {'yz': 'x', 'xy': 'z', 'xz': 'y'}[plano]
        # Minecraft: giro positivo sobre x lleva +y hacia +z; sobre z lleva +x hacia +y; sobre y lleva +z hacia +x.
        sign = {'x': 1, 'z': 1, 'y': -1}[eje]
        self.cen(c, size, sw, (eje, sign * r) if r else None, glow)
        return q

    # -------------------------------------------------------------- limites
    def corners(self):
        return [c for e in self.els for c in v._corners(e)]

    def check(self):
        prob = []
        for e in self.els:
            for c in e['from'] + e['to']:
                if not -16 <= c <= 32:
                    prob.append(f'{self.iid}: coordenada fuera de rango {c}')
            if e['rot'] and e['rot'][1] not in (-45, -22.5, 22.5, 45):
                prob.append(f"{self.iid}: angulo {e['rot'][1]}")
            for i in range(3):
                if e['to'][i] - e['from'][i] <= 0:
                    prob.append(f'{self.iid}: caja vacia {e}')
        for ctx, d in self.display().items():
            for k in d.get('translation', []):
                if abs(k) > 80:
                    prob.append(f'{self.iid}: {ctx} traslacion {k}')
            for k in d.get('scale', []):
                if not 0 < k <= 4:
                    prob.append(f'{self.iid}: {ctx} escala {k}')
        return sorted(set(prob))

    # -------------------------------------------------------------- display
    def fit(self, M, room=15.4):
        pts = [app(M, [c[i] - 8 for i in range(3)]) for c in self.corners()]
        x0, x1 = min(p[0] for p in pts), max(p[0] for p in pts)
        y0, y1 = min(p[1] for p in pts), max(p[1] for p in pts)
        s = round(min(1.6, room / max(x1 - x0, y1 - y0)), 3)
        return s, [round(-(x0 + x1) / 2 * s, 2), round(-(y0 + y1) / 2 * s, 2), 0]

    def pose(self, rot, destino, escala):
        """Display que deja el agarre del modelo en 'destino' (pixeles del espacio de la mano)."""
        R = rot_xyz(rot)
        g = [(self.agarre[i] - 8) * escala for i in range(3)]
        p = app(R, g)
        t = [round(destino[i] - p[i], 2) for i in range(3)]
        return {'rotation': [round(a, 2) for a in rot], 'translation': t, 'scale': [escala] * 3}

    def display(self):
        out = {}
        for ctx, d in self.poses.items():
            out[ctx] = d
            if ctx.endswith('righthand'):
                izq = ctx.replace('righthand', 'lefthand')
                if izq not in self.poses:
                    r = d['rotation']
                    # ItemTransform.apply espeja la mano izquierda (niega rot Y/Z y traslacion X): se guarda igual.
                    out[izq] = {'rotation': [r[0], -r[1], -r[2]], 'translation': list(d['translation']),
                                'scale': list(d['scale'])}
        gm = rot_xyz(self.gui_rot)
        s, t = self.fit(gm)
        out['gui'] = {'rotation': self.gui_rot, 'translation': t, 'scale': [s] * 3}
        fm = mul(ry(180), gm)
        s2, t2 = self.fit(fm)
        out['fixed'] = {'rotation': v._euler_xyz(fm), 'translation': t2, 'scale': [s2] * 3}
        sg = round(s * 0.42, 3)
        out['ground'] = {'rotation': self.gui_rot, 'translation': [0, 3, 0], 'scale': [sg] * 3}
        out['head'] = {'rotation': [0, 180, 0], 'translation': [0, 13, 7], 'scale': [0.6] * 3}
        return out

    # -------------------------------------------------------------- export
    def model_json(self):
        tex = f'astral:{self.tex_dir}/{self.tex_name}'
        els = []
        inset = 0.12
        for e in self.els:
            slot = self.slots[e['sw']]
            u, vv = slot % GRID * UVS, slot // GRID * UVS
            uv = [round(u + inset, 4), round(vv + inset, 4), round(u + UVS - inset, 4), round(vv + UVS - inset, 4)]
            el = {'from': [round(c, 3) for c in e['from']], 'to': [round(c, 3) for c in e['to']],
                  'faces': {f: {'uv': uv, 'texture': '#t'} for f in ('north', 'south', 'east', 'west', 'up', 'down')}}
            if e['rot']:
                axis, ang, org = e['rot']
                el['rotation'] = {'origin': [round(c, 3) for c in org], 'axis': axis, 'angle': ang}
            if e['glow']:
                el['light_emission'] = e['glow']
                el['shade'] = False
            els.append(el)
        return {'textures': {'t': tex, 'particle': tex}, 'elements': els, 'display': self.display()}

    def texture(self):
        animated = any(kind != 's' for _, kind in self.palette.values())
        n = FRAMES if animated else 1
        im = Image.new('RGBA', (TEX, TEX * n), (0, 0, 0, 0))
        px = im.load()
        rnd = random.Random(self.iid)
        noise = [[rnd.uniform(-1, 1) for _ in range(TEX)] for _ in range(TEX)]
        for name, slot in self.slots.items():
            base, kind = self.palette[name]
            sx, sy = slot % GRID * TS, slot // GRID * TS
            for yy in range(TS):
                for xx in range(TS):
                    x, y = sx + xx, sy + yy
                    pat = patron(name, xx, yy, noise[y][x], slot)
                    for f in range(n):
                        px[x, f * TEX + y] = v._frame_color(base, kind, f, noise[y][x], xx, yy, pat)
        return im, n


def patron(name, x, y, n, seed):
    """Material de cada muestra segun el prefijo del nombre (los de varitas3d mas metal cepillado, cadena,
    tela cosida, escamas y pagina)."""
    if name.startswith(('steel', 'metal', 'iron')):
        k = (1.12, 1.06, 1.02, 0.99, 0.98, 0.96, 0.93, 0.86)[y] + 0.03 * n
        if x == 0:
            k += 0.06
        return k
    if name.startswith('plate'):            # placa pintada con bisel
        k = 1 + 0.04 * n
        if y == 0 or x == 0:
            k += 0.18
        if y == TS - 1 or x == TS - 1:
            k -= 0.2
        return k
    if name.startswith('teeth'):            # dientes de cadena
        return 1.15 if x % 4 < 2 else 0.78
    if name.startswith('scale'):
        return 0.82 if (x + y) % 4 == 0 or (x - y) % 4 == 0 else 1.06
    if name.startswith('stitch'):
        return 0.7 if (x % 4 == 1 and y % 3 != 2) else 1 + 0.05 * n
    if name.startswith('cloth'):
        return 0.92 if (x + y) % 2 else 1.02 + 0.04 * n
    if name.startswith('page'):
        return 1.04 if y % 2 else 0.9
    if name.startswith('leather'):
        k = 1 + 0.07 * n
        if (x * 7 + y * 3) % 11 == 0:
            k -= 0.12
        return k
    if name.startswith('rubber'):
        return 0.95 + 0.05 * n + (0.12 if y == 1 else 0)
    return v._pattern(name, x, y, n, seed)


# ------------------------------------------------------------------------------------------- assets
def _png(im):
    b = io.BytesIO()
    im.save(b, 'PNG')
    return b.getvalue()


def assets(piezas, items_json=True):
    """{ruta del pack: bytes}. Si items_json, tambien assets/astral/items/<id>.json simple."""
    out = {}
    hechas = set()
    for p in piezas:
        if p.tex_name not in hechas:
            im, n = p.texture()
            out[f'assets/astral/textures/{p.tex_dir}/{p.tex_name}.png'] = _png(im)
            if n > 1:
                out[f'assets/astral/textures/{p.tex_dir}/{p.tex_name}.png.mcmeta'] = json.dumps(
                    {'animation': {'frametime': FRAMETIME, 'interpolate': True}}, indent=1).encode()
            hechas.add(p.tex_name)
        out[f'assets/astral/models/item/{p.iid}.json'] = json.dumps(p.model_json(), indent=1).encode()
        if items_json:
            out[f'assets/astral/items/{p.iid}.json'] = json.dumps(
                {'model': {'type': 'minecraft:model', 'model': f'astral:item/{p.iid}'}}, indent=1).encode()
    return out


# ------------------------------------------------------------------------------------------- vista previa
CARAS = {
    'north': ((0, 0, -1), [(1, 1, 0), (0, 1, 0), (0, 0, 0), (1, 0, 0)]),
    'south': ((0, 0, 1), [(0, 1, 1), (1, 1, 1), (1, 0, 1), (0, 0, 1)]),
    'east': ((1, 0, 0), [(1, 1, 1), (1, 1, 0), (1, 0, 0), (1, 0, 1)]),
    'west': ((-1, 0, 0), [(0, 1, 0), (0, 1, 1), (0, 0, 1), (0, 0, 0)]),
    'up': ((0, 1, 0), [(0, 1, 0), (1, 1, 0), (1, 1, 1), (0, 1, 1)]),
    'down': ((0, -1, 0), [(0, 0, 1), (1, 0, 1), (1, 0, 0), (0, 0, 0)]),
}


def poligonos(p, tex, M, T=(0, 0, 0), S=1.0, extra=()):
    """Caras visibles del modelo transformadas: punto -> M * S * (punto - 8) + T. Vista desde +Z."""
    px = tex.load()
    out = []
    luz = [0.35, 0.75, 0.55]
    ln = math.sqrt(sum(c * c for c in luz))
    luz = [c / ln for c in luz]
    for e in p.els:
        m, org = v._elrot(e)
        slot = p.slots[e['sw']]
        su, sv = slot % GRID * TS, slot // GRID * TS
        col = px[su + 3, sv + 3]
        col2 = px[su + 1, sv + 1]
        for fname, (nrm, cs) in CARAS.items():
            pts = []
            for c in cs:
                q = [(e['from'], e['to'])[c[i]][i] for i in range(3)]
                if m:
                    q = [a + b for a, b in zip(app(m, [q[i] - org[i] for i in range(3)]), org)]
                q = app(M, [(q[i] - 8) * S for i in range(3)])
                pts.append([q[i] + T[i] for i in range(3)])
            n = list(nrm)
            if m:
                n = app(m, n)
            n = app(M, n)
            out.append((pts, n, col, col2, e['glow']))
    out += list(extra)
    return out


def dibujar(polys, proj, size, fondo=(0, 0, 0, 0), ss=3, luz=(0.35, 0.75, 0.55)):
    """polys: [(pts, normal, color, color2, glow)]. proj(p3) -> (x, y, depth). Pinta del fondo al frente."""
    W, H = size
    img = Image.new('RGBA', (W * ss, H * ss), fondo)
    dr = ImageDraw.Draw(img)
    ln = math.sqrt(sum(c * c for c in luz))
    luz = [c / ln for c in luz]
    caras = []
    for pts, n, col, col2, glow in polys:
        pp = [proj(q) for q in pts]
        if None in pp:
            continue
        # cara de frente si el giro de los puntos proyectados es antihorario
        area = sum(pp[i][0] * pp[(i + 1) % 4][1] - pp[(i + 1) % 4][0] * pp[i][1] for i in range(4))
        if area <= 0:
            continue
        depth = sum(q[2] for q in pp) / 4
        ln2 = math.sqrt(sum(c * c for c in n)) or 1
        k = 1.0 if glow else 0.72 + 0.42 * max(0, sum(n[i] * luz[i] for i in range(3)) / ln2)
        caras.append((depth, pp, col, col2, k))
    caras.sort(key=lambda t: t[0])
    for _, pp, col, col2, k in caras:
        poly = [(q[0] * ss, q[1] * ss) for q in pp]
        c = tuple(int(min(255, col[i] * k)) for i in range(3)) + (255,)
        dr.polygon(poly, fill=c)
        borde = tuple(int(min(255, col[i] * k * 0.84)) for i in range(3)) + (255,)
        dr.line(poly + [poly[0]], fill=borde, width=1)
    return img.resize((W, H), Image.LANCZOS)


def orto(escala, centro, rot=None):
    """Proyeccion ortogonal: x a la derecha, y arriba, mirando desde +Z."""
    R = rot or [[1, 0, 0], [0, 1, 0], [0, 0, 1]]

    def f(q):
        r = app(R, q)
        return (centro[0] + r[0] * escala, centro[1] - r[1] * escala, r[2])
    return f


def vista_inventario(p, tex, cell=96):
    d = p.display()['gui']
    M = rot_xyz(d['rotation'])
    S = d['scale'][0]
    T = d['translation']
    k = cell / 16
    img = dibujar(poligonos(p, tex, M, T, S), orto(k, (cell / 2, cell / 2)), (cell, cell))
    return img


def vista_giro(p, tex, yaw, pitch=-15, size=(150, 150)):
    M = mul(rx(-pitch), ry(yaw))
    pts = [app(M, [c[i] - 8 for i in range(3)]) for c in p.corners()]
    x0, x1 = min(q[0] for q in pts), max(q[0] for q in pts)
    y0, y1 = min(q[1] for q in pts), max(q[1] for q in pts)
    k = min((size[0] - 16) / (x1 - x0), (size[1] - 16) / (y1 - y0))
    T = [-(x0 + x1) / 2, -(y0 + y1) / 2, 0]
    return dibujar(poligonos(p, tex, M, T), orto(k, (size[0] / 2, size[1] / 2)), size)


def _caja_polys(a, b, col, M=None):
    """Caja suelta (brazo del jugador) en coordenadas ya del espacio final."""
    out = []
    for fname, (nrm, cs) in CARAS.items():
        pts = [[(a, b)[c[i]][i] for i in range(3)] for c in cs]
        n = list(nrm)
        if M:
            pts = [app(M, q) for q in pts]
            n = app(M, n)
        out.append((pts, n, col, col, 0))
    return out


# Espacio de la mano en 3ra persona (ItemInHandLayer): +X derecha del jugador, +Y adelante, +Z arriba.
# El origen queda al frente del puno, en la punta del brazo (brazo colgando).
def _mano3(p, tex, ctx='thirdperson_righthand', size=(170, 170), yaw=50, pitch=12, brazo='abajo'):
    d = p.display()[ctx]
    R = rot_xyz(d['rotation'])
    S = d['scale'][0]
    T = d['translation']
    item = poligonos(p, tex, R, T, S)
    arm = _caja_polys((-2, -4, 0), (2, 0, 12), (205, 160, 130))
    polys = item + arm
    # brazo levantado (arco/gomera apuntando): el brazo apunta adelante; +Z de la mano queda hacia atras
    if brazo == 'arriba':
        Rb = [[1, 0, 0], [0, 0, -1], [0, 1, 0]]   # +Z_mano -> -Y (atras), +Y_mano -> +Z (arriba)
        polys = [([app(Rb, q) for q in pts], app(Rb, n), c1, c2, g) for pts, n, c1, c2, g in polys]
    # a mundo de la vista: x = derecha (X), y = arriba (Z), z = hacia la camara (-Y): se mira de costado-frente
    # se mira de frente-costado: adelante (+Y) viene hacia la camara, la derecha del jugador queda a la izquierda
    W = mul(rx(-pitch), mul(ry(yaw), [[-1, 0, 0], [0, 0, 1], [0, 1, 0]]))
    polys = [([app(W, q) for q in pts], app(W, n), c1, c2, g) for pts, n, c1, c2, g in polys]
    return dibujar(polys, orto(4.2, (size[0] / 2, size[1] * 0.42)), size)


def _mano1(p, tex, size=(240, 135), ctx='firstperson_righthand', uso=None):
    """Primera persona: camara en el origen mirando a -Z, FOV vertical 70, pantalla 16:9.
    uso='bow': transformacion extra de Minecraft mientras se tensa un arco."""
    d = p.display()[ctx]
    R = rot_xyz(d['rotation'])
    S = d['scale'][0]
    T = d['translation']
    base = [0.56 * 16, -0.52 * 16, -0.72 * 16]
    pre = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    if uso == 'bow':
        base = [base[0] - 0.2785682 * 16, base[1] + 0.18344387 * 16, base[2] + 0.15731531 * 16]
        # ItemInHandRenderer (arco tensado a fondo): giros fijos, estirado en Z y Y -45 al final
        pre = mul(mul(mul(rx(-13.935), ry(35.3)), rz(-9.785)), mul([[1, 0, 0], [0, 1, 0], [0, 0, 1.2]], ry(-45)))
    polys = poligonos(p, tex, mul(pre, R), [0, 0, 0], S)
    Tp = app(pre, T)
    polys = [([[q[i] + Tp[i] + base[i] for i in range(3)] for q in pts], n, c1, c2, g) for pts, n, c1, c2, g in polys]
    f = size[1] / 2 / math.tan(math.radians(35))

    def proj(q):
        if q[2] > -1:
            return None
        return (size[0] / 2 + q[0] / -q[2] * f, size[1] / 2 - q[1] / -q[2] * f, -(-q[2]))
    img = dibujar(polys, proj, size, fondo=(96, 128, 160, 255))
    dr = ImageDraw.Draw(img)
    dr.line((size[0] / 2 - 4, size[1] / 2, size[0] / 2 + 4, size[1] / 2), fill=(255, 255, 255))
    dr.line((size[0] / 2, size[1] / 2 - 4, size[0] / 2, size[1] / 2 + 4), fill=(255, 255, 255))
    return img


def hoja(piezas, path, titulo, uso=None, brazo='abajo', extra_ctx=None):
    """Lamina de revision: giro 3/4, costado, inventario, mano 3ra persona y 1ra persona."""
    cols = [('3/4', 175), ('costado', 175), ('inventario', 110), ('3ra persona', 175), ('1ra persona', 250)]
    H = 190
    W = sum(c[1] for c in cols) + 20
    out = Image.new('RGBA', (W, 34 + H * len(piezas)), (24, 26, 38, 255))
    d = ImageDraw.Draw(out)
    d.text((10, 8), titulo, fill=(240, 210, 140, 255))
    for r, p in enumerate(piezas):
        tex, _ = p.texture()
        tex = tex.crop((0, 0, TEX, TEX))
        y = 34 + r * H
        x = 10
        ctx3 = (extra_ctx or {}).get(p.iid, 'thirdperson_righthand')
        ims = [vista_giro(p, tex, 35, -18, (170, 160)), vista_giro(p, tex, 90, -5, (170, 160))]
        inv = Image.new('RGBA', (96, 96), (139, 139, 139, 255))
        inv.alpha_composite(vista_inventario(p, tex, 96))
        ims.append(inv)
        ims.append(_mano3(p, tex, ctx3, (170, 160), brazo=brazo))
        ims.append(_mano1(p, tex, (240, 135), uso=uso).convert('RGBA'))
        for (lab, w), im in zip(cols, ims):
            out.alpha_composite(im, (x, y + 18))
            d.text((x, y + 2), lab, fill=(200, 200, 220, 255))
            x += w
        d.text((10, y + H - 14), p.name, fill=(255, 255, 255, 255))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    out.convert('RGB').save(path)
    return path
