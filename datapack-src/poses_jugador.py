# -*- coding: utf-8 -*-
"""Animaciones del Segador y del Invocador (pedido del dueno 22/11/2026).

1) Cuerpo del jugador (BetterModel 3.6, carpeta plugins/BetterModel/players): por un momento el jugador se ve como
   un modelo con SU skin y su arma. Solo en la Cosecha (guadana_giro: gira 360 agachado con la guadana estirada y
   deja un anillo de almas). El dueno pidio que no pase en cada golpe: mientras dura no se ve la armadura (BetterModel
   solo sabe dibujar armaduras vanilla, no las nuestras).
2) Efectos sueltos (modelo normal astral_fx_clases, plugins/BetterModel/models): no tapan al jugador.
   - tajo: media luna de almas adelante del jugador en el barrido (golpe cargado de guadana).
   - invocar: circulo de invocacion en el piso con runas que suben.
El arma/libro que tiene en la mano se ve en el hueso pri_right_item (lo pone BetterModel).

El esqueleto sigue el modelo de ejemplo de BetterModel (proporciones y UV de la skin estandar de Minecraft):
cada hueso con prefijo p* toma la skin del jugador. La textura '-skin' no se exporta (el '-' la saltea).
Los efectos usan una textura propia chica y van en huesos glow_ (brillan).

Convencion de giros (BetterModel, frente = -Z): X positivo lleva un brazo colgando hacia adelante/arriba;
X negativo inclina el cuerpo hacia adelante; Y positivo gira el frente hacia -X (la izquierda del jugador);
Z positivo abre el brazo derecho (+X) hacia afuera.

Uso: python poses_jugador.py  -> build/players/astral_poses.bbmodel + build/previews/poses_jugador.png
"""
import base64
import io
import json
import math
import uuid
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
MODEL_ID = 'astral_poses'
FX_ID = 'astral_fx_clases'
ANIMS = ('guadana_giro',)
FX_ANIMS = ('tajo', 'invocar')
_ACTUAL = [MODEL_ID]


def uid(s):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f'{_ACTUAL[0]}/{s}'))


# ------------------------------------------------------------------------------------------ esqueleto
# (hueso, origen, padre)
HUESOS = [
    ('player_root', (0, 17, 0), None),
    ('phip_hip', (0, 11.25, 0), 'player_root'),
    ('pw_waist', (0, 15, 0), 'phip_hip'),
    ('pc_chest', (0, 18.75, 0), 'pw_waist'),
    ('cape_cape', (0, 22.75, 2), 'pc_chest'),
    ('h_ph_head', (0, 22.5, 0), 'pc_chest'),
    ('pra_right_arm', (5, 22, 0), 'pc_chest'),
    ('prfa_right_forearm', (5, 16.5, 0), 'pra_right_arm'),
    ('pri_right_item', (5.625, 10.875, 0), 'prfa_right_forearm'),
    ('pla_left_arm', (-5, 22, 0), 'pc_chest'),
    ('plfa_left_forearm', (-5, 16.5, 0), 'pla_left_arm'),
    ('pli_left_item', (-5.625, 10.875, 0), 'plfa_left_forearm'),
    ('prl_right_leg', (1.875, 11.25, 0), 'player_root'),
    ('prfl_right_foreleg', (1.875, 5.625, 0), 'prl_right_leg'),
    ('pll_left_leg', (-1.875, 11.25, 0), 'player_root'),
    ('plfl_left_foreleg', (-1.875, 5.625, 0), 'pll_left_leg'),
    # efectos (textura propia, brillan)
    ('glow_estela', (0, 15, 0), 'player_root'),
    ('tag_name', (0, 36.8, 0), 'player_root'),
]
# Modelo de efectos: el origen queda en los pies del jugador, el frente (-Z) hacia donde mira.
FX_HUESOS = [
    ('fx_root', (0, 0, 0), None),
    ('glow_circulo', (0, 0.15, 0), 'fx_root'),
    ('glow_runas', (0, 2, 0), 'fx_root'),
    ('glow_tajo', (0, 17, 0), 'fx_root'),
]
ROT_HUESO = {'pri_right_item': [-90, 0, 0], 'pli_left_item': [-90, 0, 0]}

# Partes de la skin: (hueso, desde, hasta, pivote, inflado, uv por cara) - layout estandar de skin 64x64.
F = ('north', 'east', 'south', 'west', 'up', 'down')


def _uv(n, e, s, w, u, d):
    return dict(zip(F, (n, e, s, w, u, d)))


SKIN = [
    ('phip_hip', (-3.75, 11.25, -1.875), (3.75, 15, 1.875), (0, 11.25, 0), 0,
     _uv([20, 28, 28, 32], [16, 28, 20, 32], [32, 28, 40, 32], [28, 28, 32, 32], [28, 28, 20, 24], [36, 16, 28, 20])),
    ('phip_hip', (-3.73437, 11.26563, -1.85937), (3.73438, 14.98438, 1.85938), (0, 11.25, 0), 0.25,
     _uv([20, 44, 28, 48], [16, 44, 20, 48], [32, 44, 40, 48], [28, 44, 32, 48], [8, 4, 0, 0], [36, 32, 28, 36])),
    ('pw_waist', (-3.75, 15, -1.875), (3.75, 18.75, 1.875), (0, 15, 0), 0,
     _uv([20, 24, 28, 28], [16, 24, 20, 28], [32, 24, 40, 28], [28, 24, 32, 28], [28, 24, 20, 20], [28, 28, 20, 32])),
    ('pw_waist', (-3.73437, 15.01563, -1.85937), (3.73438, 18.73438, 1.85938), (0, 15, 0), 0.25,
     _uv([20, 40, 28, 44], [16, 40, 20, 44], [32, 40, 40, 44], [28, 40, 32, 44], [8, 4, 0, 0], [8, 0, 0, 4])),
    ('pc_chest', (-3.75, 18.75, -1.875), (3.75, 22.5, 1.875), (0, 18.75, 0), 0,
     _uv([20, 20, 28, 24], [16, 20, 20, 24], [32, 20, 40, 24], [28, 20, 32, 24], [28, 20, 20, 16], [28, 24, 20, 28])),
    ('pc_chest', (-3.73437, 18.76563, -1.85937), (3.73438, 22.48438, 1.85938), (0, 18.75, 0), 0.25,
     _uv([20, 36, 28, 40], [16, 36, 20, 40], [32, 36, 40, 40], [28, 36, 32, 40], [28, 36, 20, 32], [8, 0, 0, 4])),
    ('h_ph_head', (-3.75, 22.5, -3.75), (3.75, 30, 3.75), (0, 22.5, -1.875), 0,
     _uv([8, 8, 16, 16], [0, 8, 8, 16], [24, 8, 32, 16], [16, 8, 24, 16], [16, 8, 8, 0], [24, 0, 16, 8])),
    ('h_ph_head', (-3.73437, 22.51563, -3.73437), (3.73438, 29.98438, 3.73438), (0, 22.5, -1.875), 0.5,
     _uv([40, 8, 48, 16], [32, 8, 40, 16], [56, 8, 64, 16], [48, 8, 56, 16], [48, 8, 40, 0], [56, 0, 48, 8])),
    ('pra_right_arm', (3.75, 16.875, -1.875), (7.5, 22.5, 1.875), (5.15625, 21.5625, 0), 0,
     _uv([44, 20.1, 48, 26.1], [40, 20, 44, 26], [52, 20, 56, 26], [48, 20, 52, 26], [48, 20.1, 44, 16.1], [48, 26.1, 44, 30.1])),
    ('pra_right_arm', (3.76563, 16.89063, -1.85937), (7.48438, 22.48438, 1.85938), (5.15625, 21.5625, 0), 0.25,
     _uv([44, 36, 48, 42], [40, 36, 44, 42], [52, 36, 56, 42], [48, 36, 52, 42], [48, 36, 44, 32], [56, 32, 52, 36])),
    ('prfa_right_forearm', (3.75, 11.25, -1.875), (7.5, 16.875, 1.875), (5.15625, 15.9375, 0), 0,
     _uv([44, 26, 48, 32], [40, 26, 44, 32], [52, 26, 56, 32], [48, 26, 52, 32], [48, 26, 44, 22], [52, 16, 48, 20])),
    ('prfa_right_forearm', (3.76563, 11.26563, -1.85937), (7.48438, 16.85938, 1.85938), (5.15625, 15.9375, 0), 0.25,
     _uv([44, 42, 48, 48], [40, 42, 44, 48], [52, 42, 56, 48], [48, 42, 52, 48], [44, 36, 40, 32], [52, 32, 48, 36])),
    ('pla_left_arm', (-7.5, 16.875, -1.875), (-3.75, 22.5, 1.875), (-5.15625, 21.5625, 0), 0,
     _uv([36, 52, 40, 58], [32, 52, 36, 58], [44, 52, 48, 58], [40, 52, 44, 58], [40, 52, 36, 48], [40, 58, 36, 62])),
    ('pla_left_arm', (-7.48437, 16.89063, -1.85937), (-3.76562, 22.48438, 1.85938), (-5.15625, 21.5625, 0), 0.25,
     _uv([52, 52, 56, 58], [48, 52, 52, 58], [60, 52, 64, 58], [56, 52, 60, 58], [56, 52, 52, 48], [64, 48, 60, 52])),
    ('plfa_left_forearm', (-7.5, 11.25, -1.875), (-3.75, 16.875, 1.875), (-5.15625, 15.9375, 0), 0,
     _uv([36, 58, 40, 64], [32, 58, 36, 64], [44, 58, 48, 64], [40, 58, 44, 64], [40, 58, 36, 54], [44, 48, 40, 52])),
    ('plfa_left_forearm', (-7.48437, 11.26563, -1.85937), (-3.76562, 16.85938, 1.85938), (-5.15625, 15.9375, 0), 0.25,
     _uv([52, 58, 56, 64], [48, 58, 52, 64], [60, 58, 64, 64], [56, 58, 60, 64], [52, 52, 48, 48], [60, 48, 56, 52])),
    ('prl_right_leg', (0, 5.625, -1.875), (3.75, 11.25, 1.875), (1.40625, 10.3125, 0), 0,
     _uv([4, 20, 8, 26], [0, 20, 4, 26], [12, 20, 16, 26], [8, 20, 12, 26], [8, 20, 4, 16], [8, 26, 4, 30])),
    ('prl_right_leg', (0.01563, 5.64063, -1.85937), (3.73438, 11.23438, 1.85938), (1.40625, 10.3125, 0), 0.25,
     _uv([4, 36, 8, 42], [0, 36, 4, 42], [12, 36, 16, 42], [8, 36, 12, 42], [8, 36, 4, 32], [16, 32, 12, 36])),
    ('prfl_right_foreleg', (0, 0, -1.875), (3.75, 5.625, 1.875), (1.40625, 4.6875, 0), 0,
     _uv([4, 26, 8, 32], [0, 26, 4, 32], [12, 26, 16, 32], [8, 26, 12, 32], [8, 26, 4, 22], [12, 16, 8, 20])),
    ('prfl_right_foreleg', (0.01563, 0.01563, -1.85937), (3.73438, 5.60938, 1.85938), (1.40625, 4.6875, 0), 0.25,
     _uv([4, 42, 8, 48], [0, 42, 4, 48], [12, 42, 16, 48], [8, 42, 12, 48], [4, 36, 0, 32], [12, 32, 8, 36])),
    ('pll_left_leg', (-3.75, 5.625, -1.875), (0, 11.25, 1.875), (-1.40625, 10.3125, 0), 0,
     _uv([20, 52, 24, 58], [16, 52, 20, 58], [28, 52, 32, 58], [24, 52, 28, 58], [24, 52, 20, 48], [24, 58, 20, 62])),
    ('pll_left_leg', (-3.73437, 5.64063, -1.85937), (-0.01562, 11.23438, 1.85938), (-1.40625, 10.3125, 0), 0.25,
     _uv([4, 52, 8, 58], [0, 52, 4, 58], [12, 52, 16, 58], [8, 52, 12, 58], [8, 52, 4, 48], [16, 48, 12, 52])),
    ('plfl_left_foreleg', (-3.75, 0, -1.875), (0, 5.625, 1.875), (-1.40625, 4.6875, 0), 0,
     _uv([20, 58, 24, 64], [16, 58, 20, 64], [28, 58, 32, 64], [24, 58, 28, 64], [24, 58, 20, 54], [28, 48, 24, 52])),
    ('plfl_left_foreleg', (-3.73437, 0.01563, -1.85938), (-0.01562, 5.60938, 1.85937), (-1.40625, 4.6875, 0), 0.25,
     _uv([4, 58, 8, 64], [0, 58, 4, 64], [12, 58, 16, 64], [8, 58, 12, 64], [4, 52, 0, 48], [12, 48, 8, 52])),
    ('tag_name', (-1, 35.8, -1), (1, 37.8, 1), (0, 35.8, 0), 0, _uv(*([[0, 0, 2, 2]] * 6))),
]

# ------------------------------------------------------------------------------------------ efectos
FX = 32   # textura de efectos 32x32: muestras de 8x8
FX_COL = {'alma': ('#7ff8ff', '#d8ffff'), 'alma2': ('#3ad0e8', '#a8f4ff'), 'magia': ('#9a6cff', '#e0d0ff'),
          'magia2': ('#d05aff', '#ffd0ff'), 'runa': ('#ffe28a', '#fff6d0'), 'blanco': ('#ffffff', '#ffffff')}
FX_SLOT = {k: i for i, k in enumerate(FX_COL)}


def fx_texture():
    im = Image.new('RGBA', (FX, FX), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for k, i in FX_SLOT.items():
        x, y = i % 4 * 8, i // 4 * 8
        a, b = FX_COL[k]
        d.rectangle((x, y, x + 7, y + 7), fill=a)
        d.rectangle((x + 2, y + 2, x + 5, y + 5), fill=b)
    return im


EFECTOS = []   # (hueso, desde, hasta, pivote, rotacion, muestra)


def fx(bone, c, size, col, rot=None):
    a = [c[i] - size[i] / 2 for i in range(3)]
    b = [c[i] + size[i] / 2 for i in range(3)]
    EFECTOS.append((bone, a, b, list(c), rot, col))


def _efectos():
    EFECTOS.clear()
    # circulo de invocacion: dos anillos, una estrella de 4 puntas y runas
    for k in range(16):
        a = math.radians(k * 22.5)
        for (r, w, col) in ((14, 5.2, 'magia'), (9.5, 3.6, 'magia2')):
            fx('glow_circulo', (math.cos(a) * r, 0.1, math.sin(a) * r), (w, 0.15, 0.6), col, [0, _ang(-k * 22.5 + 90), 0])
    for a in (0, 45):
        fx('glow_circulo', (0, 0.12, 0), (0.5, 0.15, 26), 'magia2', [0, a, 0] if a else None)
        fx('glow_circulo', (0, 0.12, 0), (26, 0.15, 0.5), 'magia2', [0, a, 0] if a else None)
    for k in range(8):
        a = math.radians(k * 45 + 22.5)
        fx('glow_circulo', (math.cos(a) * 11.8, 0.2, math.sin(a) * 11.8), (1.4, 0.2, 1.4), 'runa', [0, 45, 0])
    # runas que suben (giran alrededor)
    for k in range(6):
        a = math.radians(k * 60)
        fx('glow_runas', (math.cos(a) * 11, 4 + (k % 3) * 5, math.sin(a) * 11), (0.4, 2.4, 1.6), 'runa')
        fx('glow_runas', (math.cos(a) * 11, 4 + (k % 3) * 5, math.sin(a) * 11), (0.4, 0.6, 2.6), 'runa')
    # estela de la Cosecha: anillo de almas a la altura de la guadana
    for k in range(16):
        a = math.radians(k * 22.5)
        fx('glow_estela', (math.cos(a) * 22, 15, math.sin(a) * 22), (9.2, 0.5 + (k % 2) * 0.4, 0.8),
           'alma' if k % 2 else 'alma2', [0, _ang(-k * 22.5 + 90), 0])
        fx('glow_estela', (math.cos(a) * 18, 13.5, math.sin(a) * 18), (6.6, 0.4, 0.6), 'blanco' if k % 4 == 0 else 'alma',
           [0, _ang(-k * 22.5 + 90), 0])
    # tajo del golpe: media luna adelante
    for k in range(-3, 4):
        a = math.radians(-90 + k * 22.5)
        fx('glow_tajo', (math.cos(a) * 20, 17 - k * 0.6, math.sin(a) * 20), (8.4, 0.6, 0.8), 'alma' if k % 2 else 'blanco',
           [0, _ang(-(-90 + k * 22.5) + 90), 0])


def _ang(a):
    """Angulo de giro (Y) equivalente en -45..45 para una barra (una barra girada 90 es la misma barra)."""
    a = ((a + 90) % 180) - 90
    if a > 45:
        a -= 90
        return ('swap', a)
    if a < -45:
        a += 90
        return ('swap', a)
    return a


# ------------------------------------------------------------------------------------------ animaciones
def kf(*pts):
    return [(round(t, 3), (x, y, z)) for t, x, y, z in pts]


Z3 = (0, 0, 0)


def anims():
    """Modelo de jugador: solo la Cosecha."""
    A = {}
    A['guadana_giro'] = (1.0, {
        'player_root': {'rotation': kf((0, 0, 0, 0), (.15, 0, -35, 0), (.35, 0, 120, 0), (.55, 0, 240, 0), (.75, 0, 360, 0), (1.0, 0, 360, 0)),
                        'position': kf((0, 0, 0, 0), (.15, 0, -1.5, 0), (.75, 0, -1.5, 0), (.9, 0, .5, 0), (1.0, 0, 0, 0))},
        'pra_right_arm': {'rotation': kf((0, 0, 0, 0), (.15, 60, 0, 80), (.75, 70, 0, 85), (1.0, 0, 0, 0))},
        'prfa_right_forearm': {'rotation': kf((0, 0, 0, 0), (.15, 10, 0, 0), (.75, 5, 0, 0), (1.0, 0, 0, 0))},
        'pla_left_arm': {'rotation': kf((0, 0, 0, 0), (.15, 40, 0, -70), (.75, 30, 0, -75), (1.0, 0, 0, 0))},
        'pc_chest': {'rotation': kf((0, 0, 0, 0), (.15, -18, -20, 0), (.75, -14, 0, 0), (1.0, 0, 0, 0))},
        'h_ph_head': {'rotation': kf((0, 0, 0, 0), (.15, 10, 20, 0), (.75, 8, 0, 0), (1.0, 0, 0, 0))},
        'prl_right_leg': {'rotation': kf((0, 0, 0, 0), (.15, 35, 0, 12), (.75, 35, 0, 12), (1.0, 0, 0, 0))},
        'prfl_right_foreleg': {'rotation': kf((0, 0, 0, 0), (.15, -45, 0, 0), (.75, -45, 0, 0), (1.0, 0, 0, 0))},
        'pll_left_leg': {'rotation': kf((0, 0, 0, 0), (.15, -25, 0, -12), (.75, -25, 0, -12), (1.0, 0, 0, 0))},
        'plfl_left_foreleg': {'rotation': kf((0, 0, 0, 0), (.15, 30, 0, 0), (.75, 30, 0, 0), (1.0, 0, 0, 0))},
        'glow_estela': {'scale': kf((0, .01, .01, .01), (.25, .01, .01, .01), (.35, .7, 1, .7), (.75, 1.1, 1, 1.1), (.9, 1.25, 1, 1.25), (.98, .01, .01, .01), (1.0, .01, .01, .01)),
                        'rotation': kf((0, 0, 0, 0), (1.0, 0, -180, 0))},
    })
    return A


def anims_fx():
    """Modelo de efectos sueltos: el tajo del barrido y el circulo de invocar."""
    A = {}
    A['tajo'] = (0.5, {
        'glow_tajo': {'scale': kf((0, .01, .01, .01), (.06, 1, 1, 1), (.25, 1.15, 1, 1.15), (.38, .01, .01, .01), (.5, .01, .01, .01)),
                      'rotation': kf((0, 0, -70, 0), (.06, 0, -60, 0), (.3, 0, 45, 0), (.5, 0, 45, 0))},
        'glow_circulo': {'scale': kf((0, .01, .01, .01))}, 'glow_runas': {'scale': kf((0, .01, .01, .01))},
    })
    A['invocar'] = (1.3, {
        'glow_circulo': {'scale': kf((0, .01, .01, .01), (.3, 1.1, 1, 1.1), (.4, 1, 1, 1), (1.05, 1, 1, 1), (1.25, .01, .01, .01), (1.3, .01, .01, .01)),
                         'rotation': kf((0, 0, 0, 0), (1.3, 0, 120, 0))},
        'glow_runas': {'scale': kf((0, .01, .01, .01), (.2, .01, .01, .01), (.35, 1, 1, 1), (1.1, 1, 1, 1), (1.25, .01, .01, .01), (1.3, .01, .01, .01)),
                       'position': kf((0, 0, 0, 0), (.2, 0, 0, 0), (1.1, 0, 14, 0), (1.3, 0, 14, 0)),
                       'rotation': kf((0, 0, 0, 0), (1.3, 0, -160, 0))},
        'glow_tajo': {'scale': kf((0, .01, .01, .01))},
    })
    return A


# ------------------------------------------------------------------------------------------ export
def _png64(im):
    b = io.BytesIO()
    im.save(b, 'PNG')
    return 'data:image/png;base64,' + base64.b64encode(b.getvalue()).decode()


def skin_template():
    """Textura de relleno 64x64 (la reemplaza la skin del jugador): gris con la cara marcada."""
    im = Image.new('RGBA', (64, 64), (150, 150, 160, 255))
    d = ImageDraw.Draw(im)
    d.rectangle((8, 8, 15, 15), fill=(200, 160, 130, 255))
    d.rectangle((9, 11, 10, 12), fill=(40, 40, 60, 255))
    d.rectangle((13, 11, 14, 12), fill=(40, 40, 60, 255))
    return im


def export(fx=False):
    _efectos()
    _ACTUAL[0] = FX_ID if fx else MODEL_ID
    huesos = FX_HUESOS if fx else HUESOS
    nombres = {h[0] for h in huesos}
    elements, kids = [], {}
    for i, (bone, a, b, org, inflate, faces) in enumerate(SKIN if not fx else ()):
        e = {'name': 'skin' if not inflate else 'hat', 'box_uv': False, 'render_order': 'default', 'locked': False,
             'allow_mirror_modeling': True, 'from': list(a), 'to': list(b), 'autouv': 0, 'color': 0, 'origin': list(org),
             'faces': {f: {'uv': faces[f] if bone != 'tag_name' else [1, 1, 3, 3], 'texture': 0 if bone != 'tag_name' else 1}
                       for f in F}, 'type': 'cube', 'uuid': uid(f'skin{i}')}
        if inflate:
            e['inflate'] = inflate
        elements.append(e)
        kids.setdefault(bone, []).append(e['uuid'])
    for i, (bone, a, b, org, rot, col) in enumerate(EFECTOS):
        if bone not in nombres:
            continue
        s = FX_SLOT[col]
        u, v = s % 4 * 8 + 1, s // 4 * 8 + 1
        uv = [u, v, u + 6, v + 6]
        if isinstance(rot, list) and isinstance(rot[1], tuple):
            # barra girada 90: se cambian los lados x/z
            ang = rot[1][1]
            cx, cz = (a[0] + b[0]) / 2, (a[2] + b[2]) / 2
            hx, hz = (b[0] - a[0]) / 2, (b[2] - a[2]) / 2
            a = [cx - hz, a[1], cz - hx]
            b = [cx + hz, b[1], cz + hx]
            rot = [0, ang, 0] if ang else None
        e = {'name': 'fx', 'box_uv': False, 'render_order': 'default', 'locked': False, 'allow_mirror_modeling': True,
             'from': [round(x, 4) for x in a], 'to': [round(x, 4) for x in b], 'autouv': 0, 'color': 0,
             'origin': [round(x, 4) for x in org], 'faces': {f: {'uv': uv, 'texture': 1} for f in F}, 'type': 'cube',
             'uuid': uid(f'fx{i}')}
        if rot:
            e['rotation'] = rot
        elements.append(e)
        kids.setdefault(bone, []).append(e['uuid'])
    groups = []
    for (name, org, parent) in huesos:
        groups.append({'uuid': uid(f'b/{name}'), 'export': True, 'locked': False, 'origin': list(org),
                       'rotation': ROT_HUESO.get(name, [0, 0, 0]), 'color': 0, 'name': name, 'children': [], 'reset': False,
                       'shade': True, 'mirror_uv': False, 'selected': False, 'visibility': True, 'autouv': 0,
                       'isOpen': True, 'primary_selected': False})

    def node(name):
        ch = list(kids.get(name, []))
        ch += [node(n) for (n, _, p) in huesos if p == name]
        return {'uuid': uid(f'b/{name}'), 'isOpen': True, 'children': ch}

    outliner = [node(n) for (n, _, p) in huesos if p is None]
    animations = []
    for an, (length, chans) in (anims_fx() if fx else anims()).items():
        animators = {}
        for bone, ch in chans.items():
            kfs = []
            for channel, frames in ch.items():
                for i, (t, val) in enumerate(frames):
                    kfs.append({'channel': channel, 'data_points': [{'x': str(val[0]), 'y': str(val[1]), 'z': str(val[2])}],
                                'uuid': uid(f'{an}/{bone}/{channel}/{i}'), 'time': t, 'color': -1, 'interpolation': 'catmullrom'})
            animators[uid(f'b/{bone}')] = {'name': bone, 'type': 'bone', 'rotation_global': False,
                                           'quaternion_interpolation': False, 'keyframes': kfs}
        animations.append({'uuid': uid(f'anim/{an}'), 'name': an, 'loop': 'once', 'override': False, 'length': length,
                           'snapping': 24, 'selected': False, 'anim_time_update': '', 'blend_weight': '', 'start_delay': '',
                           'loop_delay': '', 'animators': animators})

    def tex(name, im, idx):
        return {'name': name, 'path': '', 'folder': '', 'namespace': '', 'id': str(idx), 'group': '', 'width': im.width,
                'height': im.height, 'uv_width': im.width, 'uv_height': im.height, 'particle': False, 'use_as_default': False,
                'layers_enabled': False, 'sync_to_project': '', 'render_mode': 'default', 'render_sides': 'auto',
                'pbr_channel': 'color', 'frame_time': 1, 'frame_order_type': 'loop', 'frame_order': '',
                'frame_interpolate': False, 'visible': True, 'internal': True, 'saved': False, 'uuid': uid(f'tex/{idx}'),
                'source': _png64(im)}
    return {
        'meta': {'format_version': '5.0', 'model_format': 'free', 'box_uv': False},
        'name': FX_ID if fx else MODEL_ID, 'model_identifier': '', 'visible_box': [1, 1, 0], 'variable_placeholders': '',
        'variable_placeholder_buttons': [], 'timeline_setups': [], 'unhandled_root_fields': {},
        'resolution': {'width': 64, 'height': 64},
        'elements': elements, 'groups': groups, 'outliner': outliner,
        'textures': [tex('-skin.png', skin_template(), 0), tex('astral_poses_fx.png', fx_texture(), 1)],
        'animations': animations,
    }


def save():
    """build/players/astral_poses.bbmodel (jugador) y build/models/astral_fx_clases.bbmodel (efectos)."""
    out = ROOT / 'build' / 'players'
    out.mkdir(parents=True, exist_ok=True)
    p = out / f'{MODEL_ID}.bbmodel'
    p.write_text(json.dumps(export()), encoding='utf-8')
    q = ROOT / 'build' / 'models' / f'{FX_ID}.bbmodel'
    q.write_text(json.dumps(export(fx=True)), encoding='utf-8')
    return p, q


# ------------------------------------------------------------------------------------------ vista previa
def preview():
    """Render simple con la cuenta de BetterModel: cada hueso gira sobre su origen (Rz*Ry*Rx como Blockbench)."""
    datos = {False: export(), True: export(fx=True)}
    P = {n: (o, p) for (n, o, p) in HUESOS + FX_HUESOS}
    owner = {}
    for d in datos.values():
        for b, ids in _kids(d).items():
            for i in ids:
                owner[i] = b
    A = {**anims(), **anims_fx()}

    def val(frames, t):
        if t <= frames[0][0]:
            return frames[0][1]
        for (t0, a), (t1, b) in zip(frames, frames[1:]):
            if t <= t1:
                k = (t - t0) / (t1 - t0) if t1 > t0 else 1
                return tuple(x + (y - x) * k for x, y in zip(a, b))
        return frames[-1][1]

    def rot(v, r):
        x, y, z = v
        rx_, ry_, rz_ = (math.radians(a) for a in r)
        # Blockbench/BetterModel: Z, despues Y, despues X (aplicado al punto: X primero)
        c, s = math.cos(rx_), math.sin(rx_); y, z = y * c - z * s, y * s + z * c
        c, s = math.cos(ry_), math.sin(ry_); x, z = x * c + z * s, -x * s + z * c
        c, s = math.cos(rz_), math.sin(rz_); x, y = x * c - y * s, x * s + y * c
        return (x, y, z)

    def world(bone, pt, an, t):
        chans = A[an][1]
        while bone:
            org, parent = P[bone]
            ch = chans.get(bone, {})
            r = val(ch['rotation'], t) if 'rotation' in ch else (0, 0, 0)
            pos = val(ch['position'], t) if 'position' in ch else (0, 0, 0)
            sc = val(ch['scale'], t) if 'scale' in ch else (1, 1, 1)
            v = [(pt[i] - org[i]) * sc[i] for i in range(3)]
            v = rot(v, r)
            pt = [v[i] + org[i] + pos[i] for i in range(3)]
            bone = parent
        return pt

    shots = [('tajo', .12), ('tajo', .25), ('guadana_giro', .15), ('guadana_giro', .45), ('guadana_giro', .8),
             ('invocar', .3), ('invocar', .7)]
    cell = 200
    out = Image.new('RGB', (cell * len(shots), cell + 24), '#1c2030')
    dr = ImageDraw.Draw(out)
    import itertools
    for k, (an, t) in enumerate(shots):
        polys = []
        for e in datos[an in FX_ANIMS]['elements']:
            b = owner[e['uuid']]
            if e['name'] == 'hat':
                continue
            pts = [[(e['from'], e['to'])[ix][0], (e['from'], e['to'])[iy][1], (e['from'], e['to'])[iz][2]]
                   for ix, iy, iz in itertools.product((0, 1), repeat=3)]
            if e.get('rotation'):
                o = e['origin']
                pts = [[a + bb for a, bb in zip(rot([p[i] - o[i] for i in range(3)], e['rotation']), o)] for p in pts]
            pts = [world(b, p, an, t) for p in pts]
            col = (200, 170, 140) if b.startswith(('h_', 'pra', 'prfa', 'pla', 'plfa')) else (70, 110, 170) if b.startswith('p') else \
                (150, 255, 255) if 'estela' in b or 'tajo' in b else (200, 150, 255)
            if b == 'tag_name':
                continue
            if b.startswith('glow_'):
                sc = [p for p in pts]
                if max(abs(p[1] - pts[0][1]) for p in pts) + max(abs(p[0] - pts[0][0]) for p in pts) < 0.2:
                    continue
            polys.append((pts, col))
        yaw = math.radians(35)
        cx0, cy0, s = k * cell + cell / 2, cell - 20, 3.6

        def proj(p):
            x = p[0] * math.cos(yaw) - p[2] * math.sin(yaw)
            z = p[0] * math.sin(yaw) + p[2] * math.cos(yaw)
            y = p[1] - z * 0.25
            return (cx0 + x * s, cy0 - y * s, z)
        faces = []
        for pts, col in polys:
            pp = [proj(p) for p in pts]
            for f in ((0, 1, 3, 2), (4, 5, 7, 6), (0, 1, 5, 4), (2, 3, 7, 6), (0, 2, 6, 4), (1, 3, 7, 5)):
                q = [pp[i] for i in f]
                faces.append((sum(p[2] for p in q) / 4, q, col))
        faces.sort(key=lambda f: -f[0])
        for _, q, col in faces:
            dr.polygon([(p[0], p[1]) for p in q], fill=col, outline=tuple(int(c * .7) for c in col))
        dr.text((k * cell + 6, cell + 4), f'{an} {t}s', fill='white')
    dest = ROOT / 'build' / 'previews' / 'poses_jugador.png'
    out.save(dest)
    return dest


def _kids(data):
    out = {}

    def walk(n, bone):
        for c in n['children']:
            if isinstance(c, str):
                out.setdefault(bone, []).append(c)
            else:
                name = next(g['name'] for g in data['groups'] if g['uuid'] == c['uuid'])
                walk(c, name)
    for n in data['outliner']:
        name = next(g['name'] for g in data['groups'] if g['uuid'] == n['uuid'])
        walk(n, name)
    return out


if __name__ == '__main__':
    print('Modelo:', save())
    print('Vista previa:', preview())
