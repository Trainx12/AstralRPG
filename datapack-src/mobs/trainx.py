# -*- coding: utf-8 -*-
"""Jefe final del Santuario: Trainx (el dueno), con su skin, la Espada del Dios de la Guerra y el Baston Astral.

Uso (desde datapack-src):
    python mobs/trainx.py                 -> modelo privado + vista previa (necesita la skin privada)

La skin es privada (docs/TERCEROS.md): vive en <ASTRAL_PRIVADO>/originales/trainx/skin.png y el modelo
derivado en <ASTRAL_PRIVADO>/build/models/astral_trainx.bbmodel. Nada de esto entra al repo publico.
Se saco de SkinsRestorer del servidor (cuenta premium ByTrainx) el 14/11/2026.

La pelea (MythicMobs) sale de mobs/mythic.py -> trainx_blocks(), con los numeros de abajo.
"""
import json
import os
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
from bbmodel import Model  # noqa: E402

MODEL_ID = 'astral_trainx'
K = 2.5            # unidades de modelo por pixel de skin: 32 px -> 80 unidades = 5 bloques
ARMA = 1.5         # escala de la espada y el baston (de su modelo de item)
ALTO_BLOQUES = 32 * K / 16

# ============================ NUMEROS DE LA PELEA (ajustables) ============================
# Vida: pensada para 4 jugadores tier V. Base = jefe de la Forja; los jefes del Santuario van de x0,6 a x1,0.
# Trainx: 4 jugadores x el Golem del Santuario (x1,0) x 1,3 ("un poco mas dificil").
VIDA_FACTOR = 4 * 1.0 * 1.3
# Dano antes del x tier 5 de astral_gameplay.sk (x400). Un jugador tier V con set completo tiene ~48.000 de vida:
# 36 -> ~30 %, 28 -> ~23 %, 13 -> ~11 % (antes de su defensa). El Golem del Santuario pega 41.
DANO_ESPADA = 36          # golpe cuerpo a cuerpo
DANO_TAJO = 28            # cada tajo del combo y la embestida
DANO_BARRIDO = 30         # barrido circular con aviso
DANO_RAYO = 13            # proyectil del baston
DANO_ESTRELLA = 15        # cada estrella de la lluvia
DISTANCIA_CERCA = 6       # bloques: de cerca espada, de lejos baston
JUGADORES_PENSADOS = 4
VELOCIDAD = 0.31
# ==========================================================================================


def skin_path():
    from terceros import privado
    return privado() / 'originales' / 'trainx' / 'skin.png'


# ------------------------------------------------------------------ skin -> cubos
class SkinModel(Model):
    """Model con caras que toman su textura de una skin 64x64 (pegada arriba a la izquierda del atlas)."""

    def __init__(self, name, skin):
        super().__init__(name)
        self.skin = skin.convert('RGBA')

    def skin_cube(self, bone, frm, to, uv, dims, inflate=0.0):
        """uv = (u, v) de la caja en la skin; dims = (ancho, alto, fondo) en pixeles de skin."""
        frm = [frm[i] - inflate for i in range(3)]
        to = [to[i] + inflate for i in range(3)]
        u, v = uv
        w, h, d = dims
        # Distribucion vanilla de la skin. El frente mira al norte; el costado derecho del personaje es +X (este).
        faces = {
            'east': (u, v + d, d, h),
            'north': (u + d, v + d, w, h),
            'west': (u + d + w, v + d, d, h),
            'south': (u + 2 * d + w, v + d, w, h),
            # arriba / abajo: girados 180 respecto de Blockbench
            'up': (u + d + w, v + d, -w, -d),
            'down': (u + d + 2 * w, v + d, -w, -d),
        }
        self.cubes.append({'bone': bone, 'from': frm, 'to': to, 'color': '#000000', 'decals': {}, 'shade': 0,
                           'rotation': None, 'origin': None, 'pat': None, 'skin': faces})

    def _pack(self):
        rects = []
        for i, c in enumerate(self.cubes):
            if c.get('skin'):
                continue
            for f in ('north', 'east', 'south', 'west', 'up', 'down'):
                w, h = self._face_size(c, f)
                rects.append((h, w, i, f))
        rects.sort(key=lambda r: (-r[0], -r[1]))
        for size in (128, 256, 512, 1024, 2048):
            x, y, shelf = 0, 64, 0
            pos, ok = {}, True
            for (h, w, i, f) in rects:
                if x + w > size:
                    x, y, shelf = 0, y + shelf, 0
                if y + h > size:
                    ok = False
                    break
                pos[(i, f)] = (x, y, w, h)
                x += w
                shelf = max(shelf, h)
            if ok:
                for i, c in enumerate(self.cubes):
                    for f, rect in (c.get('skin') or {}).items():
                        pos[(i, f)] = rect
                return size, pos
        raise ValueError('modelo demasiado grande para la textura')

    def _paint(self, size, pos):
        colored = {k: v for k, v in pos.items() if not self.cubes[k[0]].get('skin')}
        img = super()._paint(size, colored)
        img.paste(self.skin, (0, 0))
        return img


def _px(x, y, z):
    return (x * K, y * K, z * K)


def body(m):
    """Cuerpo de jugador clasico (brazos de 4 px) a escala K, capa interna + capa externa."""
    m.bone('root', (0, 0, 0))
    m.bone('body', _px(0, 12, 0), 'root')
    m.bone('head', _px(0, 24, 0), 'body')
    m.bone('arm_r', _px(5, 22, 0), 'body')
    m.bone('arm_l', _px(-5, 22, 0), 'body')
    m.bone('leg_r', _px(2, 12, 0), 'root')
    m.bone('leg_l', _px(-2, 12, 0), 'root')
    parts = [
        # hueso, desde, hasta (px), uv base, uv capa, dims, inflado de la capa
        ('head', (-4, 24, -4), (4, 32, 4), (0, 0), (32, 0), (8, 8, 8), 0.5),
        ('body', (-4, 12, -2), (4, 24, 2), (16, 16), (16, 32), (8, 12, 4), 0.25),
        ('arm_r', (4, 12, -2), (8, 24, 2), (40, 16), (40, 32), (4, 12, 4), 0.25),
        ('arm_l', (-8, 12, -2), (-4, 24, 2), (32, 48), (48, 48), (4, 12, 4), 0.25),
        ('leg_r', (0, 0, -2), (4, 12, 2), (0, 16), (0, 32), (4, 12, 4), 0.25),
        ('leg_l', (-4, 0, -2), (0, 12, 2), (16, 48), (0, 48), (4, 12, 4), 0.25),
    ]
    for bone, a, b, uv, uv2, dims, inf in parts:
        m.skin_cube(bone, _px(*a), _px(*b), uv, dims)
        m.skin_cube(bone, _px(*a), _px(*b), uv2, dims, inflate=inf * K)


# ------------------------------------------------------------------ armas (modelos de item -> cubos)
def _hex(rgb):
    return '#%02x%02x%02x' % tuple(rgb)


def weapon(m, wand, bone, hand, grip_y, forward):
    """Copia los cubos del modelo de item. forward=True: la hoja apunta al frente (-Z); False: vertical (+Y).

    Mapeo (rotacion propia, no espeja): item x -> X; vertical: y -> Y, z -> Z; al frente: y -> -Z, z -> Y."""
    hx, hy, hz = hand

    def tr(p):
        x, y, z = p
        if forward:
            return (hx + (x - 8) * ARMA, hy + (z - 8) * ARMA, hz - (y - grip_y) * ARMA)
        return (hx + (x - 8) * ARMA, hy + (y - grip_y) * ARMA, hz + (z - 8) * ARMA)

    for e in wand.els:
        a, b = tr(e['from']), tr(e['to'])
        lo = [min(a[i], b[i]) for i in range(3)]
        hi = [max(a[i], b[i]) for i in range(3)]
        rot = org = None
        if e['rot']:
            axis, ang, origin = e['rot']
            org = list(tr(origin))
            if forward:
                axis, ang = {'x': ('x', ang), 'y': ('z', -ang), 'z': ('y', ang)}[axis]
            rot = [ang if axis == 'x' else 0, ang if axis == 'y' else 0, ang if axis == 'z' else 0]
        m.cube(bone, lo, hi, _hex(wand.palette[e['sw']][0]), rotation=rot, origin=org)


def animations(m):
    """Animaciones (rehechas 16/11/2026): cada ataque tiene preparacion, golpe y recuperacion; el cuerpo, las
    piernas y el brazo libre acompanan, y los tiempos del golpe coinciden con el dano de skills_yaml()."""
    from animaciones import kf
    w = 'math.sin(q.anim_time * 360 * {s} + {p}) * {a}'
    R, L = (12, 0, 4), (8, 0, -4)                    # brazos en reposo (espada / baston)
    m.anim('idle', 4.0, {
        'body': {'rotation': (w.format(s=0.25, p=0, a=2), w.format(s=0.25, p=90, a=3), 0),
                 'position': (0, w.format(s=0.5, p=0, a=0.5), 0)},
        'head': {'rotation': (w.format(s=0.5, p=90, a=2.5), w.format(s=0.25, p=0, a=9), 0)},
        'arm_r': {'rotation': (f'14 + {w.format(s=0.5, p=0, a=4)}', w.format(s=0.25, p=0, a=4), f'5 + {w.format(s=0.5, p=90, a=1.5)}')},
        'arm_l': {'rotation': (f'22 + {w.format(s=0.5, p=180, a=5)}', 0, f'-7 + {w.format(s=0.5, p=0, a=2)}')},
        'baston': {'rotation': (w.format(s=0.5, p=0, a=6), w.format(s=0.25, p=0, a=20), 0)},
        'espada': {'rotation': (w.format(s=0.25, p=90, a=4), 0, 0)},
        'leg_r': {'rotation': (0, 0, 3)}, 'leg_l': {'rotation': (0, 0, -3)},
    })
    m.anim('walk', 1.0, {
        'leg_r': {'rotation': (w.format(s=1, p=0, a=34), 0, 0)},
        'leg_l': {'rotation': (w.format(s=1, p=180, a=34), 0, 0)},
        'arm_r': {'rotation': (f'24 + {w.format(s=1, p=180, a=16)}', 0, 6)},
        'arm_l': {'rotation': (f'14 + {w.format(s=1, p=0, a=14)}', 0, -6)},
        'body': {'position': (0, '(1 - math.cos(q.anim_time * 720)) * 0.9', 0),
                 'rotation': (-6, w.format(s=1, p=0, a=7), w.format(s=1, p=90, a=1.5))},
        'head': {'rotation': (5, w.format(s=1, p=180, a=5), 0)},
        'espada': {'rotation': (w.format(s=1, p=0, a=6), 0, 0)},
    })
    # Golpe comun de espada (~onAttack): paso adelante, tajo de arriba hacia abajo y rebote.
    m.anim('attack', 0.8, {
        'arm_r': {'rotation': kf((0, *R), (.12, 60, -20, -6), (.26, 172, -10, -12), (.4, 18, 14, 10), (.5, 30, 8, 8), (.8, *R))},
        'arm_l': {'rotation': kf((0, *L), (.26, -30, 0, -22), (.4, 40, 0, -10), (.8, *L))},
        'body': {'rotation': kf((0, 0, 0, 0), (.26, 10, 18, 0), (.4, -20, -14, 0), (.52, -12, -8, 0), (.8, 0, 0, 0)),
                 'position': kf((0, 0, 0, 0), (.26, 0, 1, 1), (.4, 0, -2, -3), (.8, 0, 0, 0))},
        'head': {'rotation': kf((0, 0, 0, 0), (.26, -10, -10, 0), (.4, 14, 6, 0), (.8, 0, 0, 0))},
        'leg_r': {'rotation': kf((0, 0, 0, 0), (.26, 12, 0, 0), (.4, -28, 0, 0), (.8, 0, 0, 0))},
        'leg_l': {'rotation': kf((0, 0, 0, 0), (.26, -8, 0, 0), (.4, 22, 0, 0), (.8, 0, 0, 0))},
        'espada': {'rotation': kf((0, 0, 0, 0), (.26, -25, 0, 0), (.4, 30, 0, 0), (.8, 0, 0, 0))},
    }, loop='once')
    # Combo: dos tajos cruzados (dano a 0,25 s y 0,6 s) y cierre girando la espada.
    m.anim('combo', 1.2, {
        'arm_r': {'rotation': kf((0, *R), (.13, 150, -50, -25), (.25, 35, 50, 25), (.42, 130, 55, 35),
                                 (.6, 22, -50, -14), (.8, 70, -20, 0), (1.2, *R))},
        'arm_l': {'rotation': kf((0, *L), (.13, 30, 0, -30), (.25, -25, 0, -14), (.42, 35, 0, -28), (.6, -20, 0, -10), (1.2, *L))},
        'body': {'rotation': kf((0, 0, 0, 0), (.13, 4, 26, 0), (.25, -12, -28, 0), (.42, 2, -24, 0), (.6, -14, 30, 0), (.8, -4, 10, 0), (1.2, 0, 0, 0)),
                 'position': kf((0, 0, 0, 0), (.25, 0, -1.5, -2), (.42, 0, 0, -1), (.6, 0, -2, -3.5), (1.2, 0, 0, 0))},
        'head': {'rotation': kf((0, 0, 0, 0), (.13, -4, -14, 0), (.25, 8, 14, 0), (.42, -4, 12, 0), (.6, 10, -14, 0), (1.2, 0, 0, 0))},
        'leg_r': {'rotation': kf((0, 0, 0, 0), (.25, -24, 0, 0), (.42, -10, 0, 0), (.6, 20, 0, 0), (1.2, 0, 0, 0))},
        'leg_l': {'rotation': kf((0, 0, 0, 0), (.25, 18, 0, 0), (.42, 8, 0, 0), (.6, -26, 0, 0), (1.2, 0, 0, 0))},
        'espada': {'rotation': kf((0, 0, 0, 0), (.25, 35, 0, 0), (.42, -20, 0, 0), (.6, 35, 0, 0), (.9, 0, 0, 360), (1.2, 0, 0, 360))},
    }, loop='once')
    # Barrido: se agacha, carga la espada atras y gira entero (el dano cae a los 0,6 s).
    m.anim('barrido', 1.2, {
        'arm_r': {'rotation': kf((0, *R), (.3, 70, 60, -30), (.45, 92, 0, 60), (.6, 92, 0, 85), (.9, 70, 0, 50), (1.2, *R))},
        'arm_l': {'rotation': kf((0, *L), (.3, 30, 0, -40), (.6, 80, 0, -70), (.9, 40, 0, -30), (1.2, *L))},
        'body': {'rotation': kf((0, 0, 0, 0), (.3, -10, 60, 0), (.6, -6, -180, 0), (.9, -4, -340, 0), (1.2, 0, -360, 0)),
                 'position': kf((0, 0, 0, 0), (.3, 0, -3, 0), (.6, 0, -2, 0), (.9, 0, -1, 0), (1.2, 0, 0, 0))},
        'head': {'rotation': kf((0, 0, 0, 0), (.3, 6, -20, 0), (.6, 0, 0, 0), (1.2, 0, 0, 0))},
        'leg_r': {'rotation': kf((0, 0, 0, 0), (.3, -22, 0, 8), (.6, 10, 0, 12), (.9, -10, 0, 6), (1.2, 0, 0, 0))},
        'leg_l': {'rotation': kf((0, 0, 0, 0), (.3, 26, 0, -8), (.6, -10, 0, -12), (.9, 10, 0, -6), (1.2, 0, 0, 0))},
    }, loop='once')
    # Lanzar con el baston: lo gira atras, lo clava hacia adelante (sale a los 0,5 s) y retrocede.
    m.anim('cast', 1.0, {
        'arm_l': {'rotation': kf((0, *L), (.2, 60, 30, -30), (.38, 165, 0, -14), (.5, 88, 0, -2), (.6, 96, 0, -2), (.78, 80, 0, -4), (1.0, *L))},
        'arm_r': {'rotation': kf((0, *R), (.38, -25, 0, 18), (.5, 30, 0, 10), (1.0, *R))},
        'body': {'rotation': kf((0, 0, 0, 0), (.38, 10, -22, 0), (.5, -12, 14, 0), (.62, -6, 8, 0), (1.0, 0, 0, 0)),
                 'position': kf((0, 0, 0, 0), (.38, 0, .8, 1.5), (.5, 0, -1, -2.5), (.62, 0, -.5, -1), (1.0, 0, 0, 0))},
        'head': {'rotation': kf((0, 0, 0, 0), (.38, -14, 10, 0), (.5, 6, -4, 0), (1.0, 0, 0, 0))},
        'leg_r': {'rotation': kf((0, 0, 0, 0), (.38, 10, 0, 0), (.5, 18, 0, 0), (1.0, 0, 0, 0))},
        'leg_l': {'rotation': kf((0, 0, 0, 0), (.38, -6, 0, 0), (.5, -22, 0, 0), (1.0, 0, 0, 0))},
        'baston': {'rotation': kf((0, 0, 0, 0), (.38, 0, 0, -360), (.5, -20, 0, -360), (1.0, 0, 0, -360))},
    }, loop='once')
    # Lluvia de estrellas: se eleva, baston arriba girando y brazos abiertos; baja de golpe.
    m.anim('lluvia', 1.6, {
        'root': {'position': kf((0, 0, 0, 0), (.4, 0, 9, 0), (.8, 0, 11, 0), (1.2, 0, 9.5, 0), (1.45, 0, -1, 0), (1.6, 0, 0, 0))},
        'arm_l': {'rotation': kf((0, *L), (.4, 178, 0, -8), (1.2, 172, 0, -12), (1.45, 60, 0, -20), (1.6, *L))},
        'arm_r': {'rotation': kf((0, *R), (.4, 40, 0, 55), (1.2, 50, 0, 62), (1.45, 30, 0, 20), (1.6, *R))},
        'head': {'rotation': kf((0, 0, 0, 0), (.4, -28, 0, 0), (1.2, -30, 0, 0), (1.45, 12, 0, 0), (1.6, 0, 0, 0))},
        'body': {'rotation': kf((0, 0, 0, 0), (.4, 8, 0, 0), (1.2, 10, 0, 0), (1.45, -12, 0, 0), (1.6, 0, 0, 0))},
        'leg_r': {'rotation': kf((0, 0, 0, 0), (.4, 14, 0, 4), (1.2, 22, 0, 5), (1.45, -30, 0, 6), (1.6, 0, 0, 0))},
        'leg_l': {'rotation': kf((0, 0, 0, 0), (.4, -8, 0, -4), (1.2, -4, 0, -5), (1.45, -30, 0, -6), (1.6, 0, 0, 0))},
        'baston': {'rotation': kf((0, 0, 0, 0), (.4, 0, 180, 0), (.8, 0, 540, 0), (1.2, 0, 900, 0), (1.6, 0, 1080, 0))},
    }, loop='once')
    # Embestida: se agazapa, sale con la espada de punta y remata con un tajo (dano a los 0,65 s).
    m.anim('dash', 0.8, {
        'body': {'rotation': kf((0, 0, 0, 0), (.12, 14, 20, 0), (.2, -32, 0, 0), (.55, -30, 0, 0), (.65, -14, -24, 0), (.8, 0, 0, 0)),
                 'position': kf((0, 0, 0, 0), (.12, 0, -3, 2), (.2, 0, -1, -2), (.65, 0, -1, -2), (.8, 0, 0, 0))},
        'arm_r': {'rotation': kf((0, *R), (.12, 40, 40, -20), (.2, 88, 0, 6), (.55, 92, 0, 6), (.65, 20, 40, 20), (.8, *R))},
        'arm_l': {'rotation': kf((0, *L), (.2, -50, 0, -20), (.55, -55, 0, -22), (.8, *L))},
        'head': {'rotation': kf((0, 0, 0, 0), (.2, 24, 0, 0), (.55, 24, 0, 0), (.8, 0, 0, 0))},
        'leg_r': {'rotation': kf((0, 0, 0, 0), (.12, 20, 0, 0), (.2, -40, 0, 0), (.4, 30, 0, 0), (.55, -40, 0, 0), (.8, 0, 0, 0))},
        'leg_l': {'rotation': kf((0, 0, 0, 0), (.12, -20, 0, 0), (.2, 40, 0, 0), (.4, -30, 0, 0), (.55, 40, 0, 0), (.8, 0, 0, 0))},
    }, loop='once')
    # Aparece: cae del cielo, aterriza de rodillas con la espada clavada y se levanta.
    m.anim('aparece', 2.0, {
        'root': {'position': kf((0, 0, 70, 0), (.55, 0, 0, 0), (.7, 0, -5, 0), (1.3, 0, -5, 0), (2.0, 0, 0, 0))},
        'body': {'rotation': kf((0, 14, 0, 0), (.55, -10, 0, 0), (.7, -34, 0, 0), (1.3, -30, 0, 0), (2.0, 0, 0, 0))},
        'head': {'rotation': kf((0, -20, 0, 0), (.7, 30, 0, 0), (1.3, 26, 0, 0), (1.6, -8, 0, 0), (2.0, 0, 0, 0))},
        'arm_r': {'rotation': kf((0, 170, 0, -10), (.55, 170, 0, -10), (.7, 28, 0, 6), (1.3, 30, 0, 6), (2.0, *R))},
        'arm_l': {'rotation': kf((0, -30, 0, -50), (.55, -30, 0, -50), (.7, 40, 0, -20), (1.3, 40, 0, -20), (2.0, *L))},
        'leg_r': {'rotation': kf((0, 10, 0, 0), (.55, 10, 0, 0), (.7, 70, 0, 0), (1.3, 66, 0, 0), (2.0, 0, 0, 0))},
        'leg_l': {'rotation': kf((0, -10, 0, 0), (.55, -10, 0, 0), (.7, -40, 0, 0), (1.3, -36, 0, 0), (2.0, 0, 0, 0))},
    }, loop='once')
    # Furia (cambio de fase): junta las armas, tiembla y abre los brazos con un grito.
    m.anim('furia', 1.6, {
        'body': {'rotation': kf((0, 0, 0, 0), (.4, -22, 0, 0), (.55, -24, 3, 0), (.7, -22, -3, 0), (.85, 16, 0, 0), (1.3, 14, 0, 0), (1.6, 0, 0, 0)),
                 'position': kf((0, 0, 0, 0), (.4, 0, -3, 0), (.7, 0, -3, 0), (.85, 0, 2, 0), (1.3, 0, 1.5, 0), (1.6, 0, 0, 0))},
        'head': {'rotation': kf((0, 0, 0, 0), (.4, 26, 0, 0), (.7, 26, 0, 0), (.85, -32, 0, 0), (1.3, -30, 0, 0), (1.6, 0, 0, 0))},
        'arm_r': {'rotation': kf((0, *R), (.4, 70, -40, -30), (.7, 72, -42, -30), (.85, 40, 0, 95), (1.3, 44, 0, 90), (1.6, *R))},
        'arm_l': {'rotation': kf((0, *L), (.4, 70, 40, 30), (.7, 72, 42, 30), (.85, 40, 0, -95), (1.3, 44, 0, -90), (1.6, *L))},
        'leg_r': {'rotation': kf((0, 0, 0, 0), (.4, -20, 0, 6), (.85, 0, 0, 10), (1.3, 0, 0, 10), (1.6, 0, 0, 0))},
        'leg_l': {'rotation': kf((0, 0, 0, 0), (.4, 20, 0, -6), (.85, 0, 0, -10), (1.3, 0, 0, -10), (1.6, 0, 0, 0))},
    }, loop='once')
    # Muerte: retrocede tambaleando, suelta los brazos, cae de rodillas y se desploma hacia adelante.
    m.anim('death', 2.0, {
        'root': {'position': kf((0, 0, 0, 0), (.35, 0, 0, 4), (.9, 0, -12, 3), (1.4, 0, -13, 2), (2.0, 0, -22, -6))},
        'leg_r': {'rotation': kf((0, 0, 0, 0), (.35, 14, 0, 0), (.9, -82, 0, 0), (1.4, -85, 0, 0), (2.0, -10, 0, 0))},
        'leg_l': {'rotation': kf((0, 0, 0, 0), (.35, -10, 0, 0), (.9, -80, 0, 0), (1.4, -85, 0, 0), (2.0, -10, 0, 0))},
        'body': {'rotation': kf((0, 0, 0, 0), (.35, 18, 8, 0), (.9, -8, 0, 0), (1.4, -30, 0, 0), (2.0, -86, 0, 0))},
        'head': {'rotation': kf((0, 0, 0, 0), (.35, -24, 0, 0), (.9, 14, 0, 0), (1.4, 34, 0, 0), (2.0, 10, 20, 0))},
        'arm_r': {'rotation': kf((0, *R), (.35, 60, 0, 40), (.9, 30, 0, 14), (1.4, 8, 0, 22), (2.0, 150, 0, 30))},
        'arm_l': {'rotation': kf((0, *L), (.35, 50, 0, -40), (.9, 30, 0, -14), (1.4, 8, 0, -22), (2.0, 140, 0, -30))},
    }, loop='hold')


def build(skin=None):
    import espadas3d
    import varitas3d
    skin = skin or Image.open(skin_path())
    m = SkinModel(MODEL_ID, skin)
    body(m)
    # Manos: centro del puno, un pixel arriba del final del brazo.
    m.bone('espada', _px(6, 13, 0), 'arm_r')
    m.bone('baston', _px(-6, 13, 0), 'arm_l')
    weapon(m, espadas3d.espada_dios_guerra(), 'espada', _px(6, 13, -0.5), grip_y=-3.5, forward=True)
    weapon(m, varitas3d.astral(), 'baston', _px(-6, 13, 0), grip_y=1.0, forward=False)
    m.bone('mtag_nombre', (0, 32 * K + 8, 0), 'root')
    animations(m)
    return m


# ------------------------------------------------------------------ MythicMobs
MOB_ID = 'astral_santuario_trainx'
ESTRELLA_ID = 'astral_trainx_estrella'


def q(s):
    return "'" + s.replace("'", "''") + "'"


def vida():
    from escala import VIDA_JEFE
    return round(VIDA_JEFE['forja'] * VIDA_FACTOR)


def mob_block():
    """Bloque del jefe (oleada 6 del Santuario) + la estrella que cae. Devuelve (id, yaml, ayudantes)."""
    sk = [
        'skill{s=TRAINX_MODELO} @self ~onSpawn', 'skill{s=TRAINX_MODELO} @self ~onLoad',
        'skill{s=TRAINX_APARECE} @self ~onSpawn',
        'command{c="trainxinicio <caster.l.w>"} @self ~onSpawn',
        'state{s=attack} @self ~onAttack',
        # De cerca: espada. De lejos: baston.
        f'skill{{s=TRAINX_COMBO}} @self ~onTimer:60 ?playerwithin{{d={DISTANCIA_CERCA}}}',
        f'skill{{s=TRAINX_BARRIDO}} @self ~onTimer:220 ?playerwithin{{d={DISTANCIA_CERCA + 1}}}',
        f'skill{{s=TRAINX_RAYO}} @PlayersInRing{{min={DISTANCIA_CERCA};max=40}} ~onTimer:40',
        'skill{s=TRAINX_LLUVIA} @self ~onTimer:300 ?playerwithin{d=40}',
        'skill{s=TRAINX_DASH} @PlayersInRing{min=12;max=40;sort=FURTHEST;limit=1} ~onTimer:300',
        # Fases
        'skill{s=TRAINX_FASE2} @self ~onDamaged ?healthpercent{p=<0.6} ?!hastag{tag=trainx.f2}',
        'skill{s=TRAINX_FASE3} @self ~onDamaged ?healthpercent{p=<0.3} ?!hastag{tag=trainx.f3}',
        'skill{s=TRAINX_LLUVIA} @self ~onTimer:180 ?hastag{tag=trainx.f2} ?playerwithin{d=40}',
        f'skill{{s=TRAINX_RAYO}} @PlayersInRing{{min={DISTANCIA_CERCA};max=40}} ~onTimer:25 ?hastag{{tag=trainx.f3}}',
        # Anti trampa: si no queda nadie cerca, se cura entero y vuelve al centro. Si cae al agua, vuelve.
        'skill{s=TRAINX_RESET} @self ~onTimer:600 ?!playerwithin{d=48}',
        'teleport @SpawnLocation ~onTimer:20 ?inblock{m=WATER}',
        'teleport @SpawnLocation ~onTimer:100 ?!playerwithin{d=48}',
        'skill{s=TRAINX_MUERE} @self ~onDeath',
    ]
    lines = [
        f'{MOB_ID}:', '  Type: ZOMBIE', "  Display: '&d&lTrainx'", f'  Health: {vida()}',
        f'  Damage: {DANO_ESPADA}', '  Armor: 12', '  Options:', '    Glowing: true',
        '    PreventOtherDrops: true', '    PreventItemPickup: true', '    PreventSunburn: true', '    Silent: true',
        '    Despawn: false', f'    MovementSpeed: {VELOCIDAD}', '    KnockbackResistance: 1', '    FollowRange: 48',
        '    PreventRandomEquipment: true', '    Baby: false',
        '  AIGoalSelectors:', '  - clear', '  - meleeattack', '  - lookatplayers',
        '  AITargetSelectors:', '  - clear', '  - attacker', '  - players',
        # Nunca YELLOW (BetterHud la vuelve invisible).
        '  BossBar:', '    Enabled: true', "    Title: '&5✦ Tier V+ ✦ &d&lTrainx'", '    Range: 64',
        '    Color: PURPLE', '    Style: SEGMENTED_20',
        '  Drops:', '  - exp 600',
        '  Skills:', *['  - ' + q(s) for s in sk], '',
        f'{ESTRELLA_ID}:', '  Type: ARMOR_STAND', "  Display: 'Estrella'", '  Health: 1', '  Options:',
        '    Invisible: true', '    Marker: true', '    Invincible: true', '    NoGravity: true', '    Silent: true',
        '    Despawn: true', '    PreventOtherDrops: true', '    AlwaysShowName: false',
        '  Skills:', "  - 'skill{s=TRAINX_ESTRELLA} @self ~onSpawn'", '',
    ]
    return MOB_ID, '\n'.join(lines) + '\n', {ESTRELLA_ID}


def skills_yaml():
    from mobs.tamanos import VANILLA
    scale = round(ALTO_BLOQUES / VANILLA['ZOMBIE'][1], 4)
    S = {
        'TRAINX_MODELO': ['addtag{tag=astral.seen} @self', 'addtag{tag=astral.vplus} @self', 'addtag{tag=astral.mt5} @self',
                          f'model{{m={MODEL_ID};s=1}} @self',
                          f'command{{c="attribute <caster.uuid> minecraft:scale base set {scale}"}} @self',
                          'command{c="attribute <caster.uuid> minecraft:step_height base set 1.5"} @self',
                          'delay 2', 'command{c="execute as <caster.uuid> run function astral:mob/nombre_vplus"} @self'],
        'TRAINX_APARECE': ['state{s=aparece} @self', 'delay 11', __import__('efectos').mm_fx('golpe', '#d0306a', 7, 'vacio'),
                           'sound{s=entity.generic.explode;v=1.6;p=0.6} @self',
                           'sound{s=entity.wither.spawn;v=2;p=0.8} @PlayersInRadius{r=64}',
                           'particles{p=end_rod;amount=200;hS=2;vS=6;y=4;speed=0.05} @self',
                           'particles{p=firework;amount=120;hS=3;vS=3;y=3;speed=0.1} @self',
                           'message{m="&5✦ &d&lTrainx &5✦ &7baja del cielo del Santuario, con la espada en una mano y el baston en la otra."} @PlayersInRadius{r=64}',
                           'message{m="&d«Llegaron muy lejos. Veamos si la estrella los eligio bien.»"} @PlayersInRadius{r=64}'],
        'TRAINX_COMBO': ['state{s=combo} @self', 'sound{s=entity.player.attack.sweep;v=1.5;p=0.7} @self', 'delay 5',
                         'particles{p=sweep_attack;amount=6;hS=2;vS=0.6;y=2} @self',
                         f'damage{{a={DANO_TAJO}}} @PlayersInRadius{{r={DISTANCIA_CERCA}}}', 'delay 7',
                         'sound{s=entity.player.attack.strong;v=1.5;p=0.6} @self',
                         'particles{p=sweep_attack;amount=6;hS=2;vS=0.6;y=2} @self',
                         __import__('efectos').mm_fx('golpe', '#ff5fd2', 3.5, 'arcano'),
                         f'damage{{a={DANO_TAJO}}} @PlayersInRadius{{r={DISTANCIA_CERCA}}}',
                         'throw{velocity=4;velocityY=1.5} @PlayersInRadius{r=4}'],
        'TRAINX_BARRIDO': ['state{s=barrido} @self', 'sound{s=block.beacon.power_select;v=2;p=0.6} @self',
                           f'particlering{{p=dust;color=#d0306a;size=2;radius={DISTANCIA_CERCA + 1};points=60;amount=1;y=0.2}} @self',
                           'delay 6',
                           f'particlering{{p=dust;color=#d0306a;size=2;radius={DISTANCIA_CERCA + 1};points=60;amount=1;y=0.2}} @self',
                           'delay 6', 'sound{s=entity.player.attack.sweep;v=2;p=0.5} @self',
                           'particles{p=sweep_attack;amount=20;hS=4;vS=0.4;y=1.5} @self',
                           __import__('efectos').mm_fx('golpe', '#d0306a', DISTANCIA_CERCA + 1, 'vacio'),
                           f'damage{{a={DANO_BARRIDO}}} @PlayersInRadius{{r={DISTANCIA_CERCA + 1}}}',
                           f'throw{{velocity=8;velocityY=3}} @PlayersInRadius{{r={DISTANCIA_CERCA + 1}}}'],
        'TRAINX_RAYO': ['state{s=cast} @self', 'sound{s=block.amethyst_block.chime;v=2;p=0.6} @self', 'delay 10',
                        __import__('efectos').mm_fx('estallido', '#4fd1ff', 0.8, 'luz'),
                        'sound{s=entity.illusioner.cast_spell;v=1.5;p=1.2} @self',
                        'projectile{onTick=TRAINX_RAYO_TICK;onHit=TRAINX_RAYO_HIT;v=18;i=1;hR=1;vR=1;mr=48;'
                        'bulletType=ITEM;material=NETHER_STAR;hnp=true;sy=3}'],
        'TRAINX_RAYO_TICK': ['particles{p=end_rod;amount=2;hS=0.05;vS=0.05;speed=0} @origin',
                             'particles{p=dust;color=#4fd1ff;size=1.3;amount=2;hS=0.1;vS=0.1} @origin',
                             'command{c="astralfx estela <target.l.w> <target.l.x> <target.l.y> <target.l.z> 4fd1ff 1 luz"} @origin'],
        'TRAINX_RAYO_HIT': [f'damage{{a={DANO_RAYO}}}', __import__('efectos').mm_fx('estallido', '#4fd1ff', 1.8, 'luz', 'target'), 'particles{p=firework;amount=25;hS=0.6;vS=0.6;speed=0.08} @origin',
                            'sound{s=entity.firework_rocket.blast;v=1.2;p=1.4} @origin'],
        'TRAINX_LLUVIA': ['state{s=lluvia} @self', 'sound{s=block.beacon.activate;v=2;p=1.4} @PlayersInRadius{r=40}',
                          'message{m="&d«Que caigan las estrellas.»"} @PlayersInRadius{r=40}', 'delay 10',
                          f'summon{{type={ESTRELLA_ID};amount=1;radius=0}} @PlayersInRadius{{r=40}}', 'delay 16',
                          f'summon{{type={ESTRELLA_ID};amount=1;radius=0}} @PlayersInRadius{{r=40}}'],
        'TRAINX_ESTRELLA': ['particlering{p=end_rod;radius=2.5;points=24;amount=1;y=0.15} @self', 'delay 8',
                            'particlering{p=end_rod;radius=2.5;points=24;amount=1;y=0.15} @self', 'delay 8',
                            'particlering{p=dust;color=#ffd84d;size=2;radius=2.5;points=24;amount=1;y=0.15} @self', 'delay 6',
                            'particles{p=firework;amount=50;hS=0.3;vS=4;y=5;speed=0.02} @self',
                            'sound{s=entity.firework_rocket.large_blast;v=1.6;p=0.8} @self',
                            __import__('efectos').mm_fx('golpe', '#ffd84d', 2.5, 'luz'),
                            f'damage{{a={DANO_ESTRELLA}}} @PlayersInRadius{{r=2.5}}',
                            'particles{p=explosion;amount=2} @self', 'delay 2', 'remove @self'],
        'TRAINX_DASH': ['state{s=dash} @self', 'sound{s=entity.ender_dragon.flap;v=2;p=0.8} @self', 'delay 3',
                        'lunge{velocity=3.2;velocityY=0.35} @target', 'delay 10',
                        'particles{p=sweep_attack;amount=8;hS=2;vS=0.5;y=2} @self',
                        __import__('efectos').mm_fx('golpe', '#ff5fd2', 3, 'arcano'),
                        f'damage{{a={DANO_TAJO}}} @PlayersInRadius{{r=4}}'],
        'TRAINX_FASE2': ['addtag{tag=trainx.f2} @self', 'state{s=furia} @self', __import__('efectos').mm_fx('golpe', '#ff5fd2', 6, 'arcano'),
                         'sound{s=entity.ender_dragon.growl;v=2;p=1.2} @PlayersInRadius{r=64}',
                         'message{m="&d«Bien. Entonces peleemos en serio.»"} @PlayersInRadius{r=64}'],
        'TRAINX_FASE3': ['addtag{tag=trainx.f3} @self', 'state{s=furia} @self', __import__('efectos').mm_fx('golpe', '#b03cff', 8, 'vacio'),
                         'potion{type=SPEED;duration=2147483647;level=0;hasParticles=false} @self',
                         'sound{s=entity.wither.ambient;v=2;p=0.6} @PlayersInRadius{r=64}',
                         'particles{p=dragon_breath;amount=150;hS=2;vS=3;y=2;speed=0.05} @self',
                         'message{m="&5&l«¡Muestrenme la luz de la estrella!»"} @PlayersInRadius{r=64}'],
        'TRAINX_RESET': ['heal{a=2000000000} @self', 'removetag{tag=trainx.f2} @self', 'removetag{tag=trainx.f3} @self',
                         'potionclear @self', 'teleport @SpawnLocation'],
        'TRAINX_MUERE': ['state{s=death} @self', __import__('efectos').mm_fx('golpe', '#ffe9a0', 8, 'luz'), 'sound{s=ui.toast.challenge_complete;v=2;p=0.8} @PlayersInRadius{r=64}',
                         'particles{p=end_rod;amount=300;hS=2;vS=4;y=3;speed=0.1} @self',
                         'command{c="trainxfin <caster.l.w>"} @self'],
    }
    out = ['# Generado por datapack-src/mobs/trainx.py: jefe final del Santuario (Trainx).', '']
    for name, skills in S.items():
        out += [f'{name}:']
        if name in ('TRAINX_COMBO', 'TRAINX_RAYO'):
            out += ['  Cooldown: 3']
        if name in ('TRAINX_BARRIDO', 'TRAINX_LLUVIA', 'TRAINX_DASH'):
            out += ['  Cooldown: 8']
        out += ['  Skills:', *['  - ' + q(s) for s in skills], '']
    return '\n'.join(out)


def write_skills(out_dir):
    path = Path(out_dir) / 'mythicmobs' / 'skills' / 'trainx.yml'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(skills_yaml(), encoding='utf-8')
    return path


def export(dest=None, preview=True):
    from bbmodel import save
    from terceros import privado
    m = build()
    dest = Path(dest or privado() / 'build' / 'models' / f'{MODEL_ID}.bbmodel')
    dest.parent.mkdir(parents=True, exist_ok=True)
    img = save(m, dest)
    if preview:
        from build_models import preview3d
        views = [preview3d(m, img, yaw, 15, 3) for yaw in (20, 160, 90)]
        sheet = Image.new('RGBA', (sum(v.width for v in views) + 20, max(v.height for v in views)), (40, 40, 48, 255))
        x = 0
        for v in views:
            sheet.paste(v, (x, 0)); x += v.width + 10
        out = privado() / 'build' / 'previews' / 'trainx.png'
        out.parent.mkdir(parents=True, exist_ok=True)
        sheet.save(out)
        print('Vista previa:', out)
    print('Modelo:', dest, len(m.cubes), 'cubos')
    return dest


if __name__ == '__main__':
    export(sys.argv[1] if len(sys.argv) > 1 else None)
