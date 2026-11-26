# -*- coding: utf-8 -*-
"""Capitan del Vacio: jefe de la Nave del Vacio (nave.py), 22/11/2026. Rehecho a la tarde con el dibujo del dueno:
rey calavera que flota, corona de cristales violetas, seis brazos de mangas violetas con brazaletes dorados y manos de
hueso con puntas que brillan, costillas a la vista con una estrella de luz, cinturon de hebillas y tunica larga rasgada.
Lo acompanan los Ojos Vigias (cubos con un ojo) que lo protegen.

    python mobs/capitan_vacio.py   -> build/models/astral_capitan_vacio.bbmodel, astral_ojo_vigia.bbmodel + vista previa

Fases: 100-70 zarpazos, salto detras de un jugador, cubos de vacio. 70%: aparecen 3 Ojos Vigias; mientras vive
alguno el Capitan recibe 80% menos de dano y los ojos disparan rayos; tambien llama crias. 40%: falla de gravedad
(pulsos de levitacion, zonas del piso que lastiman) y se acelera.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
from bbmodel import Model  # noqa: E402

MODEL_ID = 'astral_capitan_vacio'
OJO_ID = 'astral_ojo_vigia'
MOB_ID = 'astral_nave_capitan'
OJO_MOB = 'astral_nave_ojo'
CRIA_MOB = 'astral_nave_cria'
TIMONEL_MOB = 'astral_nave_timonel'
ZONA_MOB = 'astral_nave_zona'

# ============================ NUMEROS DE LA PELEA (ajustables) ============================
ALTO = 4.5                # bloques de alto en juego (23/11: con 11,7 no se lo veia)
ESCALA = 2.3              # escala de la entidad (ZOMBIE 1,95 x 2,3 = 4,5 de caja para pegarle)
VIDA_FACTOR = 1.5         # x el jefe de la Forja (13.125.000): 19.687.500, como el Santuario (x1,5)
OJOS = 3
OJO_VIDA = 0.03           # cada Ojo Vigia: 3% de la vida del Capitan (590.625)
ESCUDO = 0.2              # con Ojos vivos recibe solo el 20% del dano
DANO_ZARPAZO = 30         # golpe cuerpo a cuerpo (antes del x tier de astral_gameplay.sk, como Trainx)
DANO_CUBO = 36            # cubo de vacio (proyectil)
DANO_ZONA = 5             # cada medio segundo dentro de una zona de vacio
DANO_RAYO_OJO = 8         # rayo de cada Ojo Vigia
DANO_PULSO = 45           # pulso de gravedad (fase 3)
DANO_BARRIDO = 60         # barrido del vacio: gira 360 con las garras (radio 7)
VELOCIDAD = 0.27
TIMONEL_EZ = 12           # minijefe: 12 zombis T5 de vida (x1,5 de la mazmorra)
# ==========================================================================================

NEGRO, NEGRO2, VIOLETA, MAGENTA, ROSA, BLANCO = '#17101f', '#21162c', '#5a1694', '#c43bff', '#f0a0ff', '#fff4ff'
VERDE, VERDE_OSC, TEAL = '#1fd38a', '#06140f', '#123b33'

# Diseno del dueno (22/11 tarde, dibujo de referencia): rey calavera del vacio con corona de cristales, seis brazos de
# mangas violetas con brazaletes dorados y manos de hueso con puntas que brillan, costillas a la vista con una estrella
# de luz, cinturon de hebillas doradas y tunica larga rasgada con tabardos de borde dorado. Flota.
# Lo que brilla va en huesos glow_ (BetterModel los muestra con brillo propio).
TUN, TUN_L, TUN_D, TUN_O = '#5b2c92', '#7a44b8', '#3c1a62', '#24103c'
ORO, ORO_D, ORO_L = '#d9a845', '#8a6420', '#f2d27a'
HUESO, HUESO_D, HUESO_O = '#e6dcec', '#b4a6c6', '#4a3a5e'
LUZ, LUZ2, VACIO = '#e040ff', '#ffb0ff', '#1a0b2a'
CRISTAL, CRISTAL_L = '#9a3ae0', '#d08cff'
AME, AME_L, AME_D, AME_H, AME_O = '#9a5ce6', '#cfa4ff', '#6a35b0', '#f3e2ff', '#432078'
CUENCA = '#170a22'

# Pose de cada brazo (rotacion base del hueso; las animaciones suman sobre esto). s=-1: lado -X.
# X positivo = hacia adelante; Z = s * angulo abre hacia afuera.
BRAZOS = {  # nombre: (pivote, rot brazo, rot antebrazo)
    'u': ((17, 66, 2), (15, 0, 130), (0, 0, 35)),     # par de arriba: alzados, manos arriba
    'm': ((21, 61, -1), (20, 0, 95), (0, 0, 55)),      # par del medio: abiertos, antebrazo hacia arriba
    'l': ((12, 50, -1), (55, 0, 30), (30, 0, 0)),      # par de abajo: hacia adelante
}


def _pose(n, s, which=1):
    r = BRAZOS[n][which]
    return (r[0], r[1] * s, r[2] * s)


def _borde(w, h, col=ORO):
    return [(0, 0, w, 1, col), (0, h - 1, w, 1, col), (0, 0, 1, h, col), (w - 1, 0, 1, h, col)]


def _tela(w, h, seed, col=TUN_L, col2=TUN_D):
    """Motas de la tela violeta (como el dibujo)."""
    import random
    r = random.Random(seed)
    out = []
    for _ in range(max(2, w * h // 9)):
        out.append((r.randrange(max(1, w)), r.randrange(max(1, h)), 1, 1, col if r.random() < .5 else col2))
    return out


def _guarda(w, h, seed):
    """Tabardo: tela oscura con borde dorado y cruces doradas."""
    d = _borde(w, h) + _tela(w, h, seed, TUN, TUN_O)
    cx = w // 2
    for y in range(4, h - 4, 7):
        d += [(cx, y, 1, 3, ORO), (cx - 1, y + 1, 3, 1, ORO)]
    return d


def build():
    m = Model(MODEL_ID)
    B = m.bone
    B('root', (0, 0, 0))
    B('body', (0, 40, 0), 'root')
    B('glow_nucleo', (0, 49.5, -5), 'body')
    # la tunica se abre un poco hacia abajo (vuelo)
    for k, piv, rot in (('f', (0, 40, -6), (7, 0, 0)), ('b', (0, 40, 6), (-9, 0, 0)), ('r', (-9, 40, 0), (0, 0, -9)),
                        ('l', (9, 40, 0), (0, 0, 9))):
        B(f'cola_{k}', piv, 'body', rotation=rot)
        B(f'glow_cola_{k}', piv, f'cola_{k}')
    B('head', (0, 66, 0), 'body')
    B('jaw', (0, 70, -1.5), 'head')
    B('glow_ojos', (0, 76, -8), 'head')
    B('corona', (0, 82, 0), 'head')
    B('glow_corona', (0, 82, 0), 'corona')
    for n, (piv, rot, rot2) in BRAZOS.items():
        for s, lado in ((-1, 'r'), (1, 'l')):
            x, y, z = piv[0] * s, piv[1], piv[2]
            B(f'arm_{n}{lado}', (x, y, z), 'body', rotation=_pose(n, s, 1))
            B(f'ante_{n}{lado}', (x, y - 14, z), f'arm_{n}{lado}', rotation=_pose(n, s, 2))
    B('mtag_nombre', (0, 112, 0), 'root')
    C, R = m.cube, m.rcube

    # ------------------------------------------------------------------ torso: costillas, esternon corto y estrella a la vista
    C('body', (-7, 43, -4), (7, 64, 5), VACIO)
    C('body', (-1.2, 42, 2.5), (1.2, 64, 4.5), HUESO_D)                                    # columna
    for k, y in enumerate((46.5, 49.5, 52.5, 55.5, 58.5)):
        w = 6.4 - abs(k - 2.6) * 0.35
        x_in = 2.2 if k < 2 else 0.9                                                       # las de abajo dejan ver la estrella
        for s in (-1, 1):
            x0, x1 = sorted((s * x_in, s * (0.9 + w)))
            C('body', (x0, y, -5.4), (x1, y + 1.7, -4.0), HUESO, decals={'north': [(0, 0, int(abs(x1 - x0)), 1, '#ffffff')]})
            x0, x1 = sorted((s * (0.9 + w - 1.2), s * (0.9 + w)))
            C('body', (x0, y - 0.6, -4.4), (x1, y + 1.4, 3.2), HUESO_D)
    C('body', (-1.3, 54.2, -5.9), (1.3, 61.5, -4.2), HUESO, decals={'north': [(1, 0, 1, 7, '#ffffff')]})  # esternon (termina arriba)
    C('body', (-1.6, 53.4, -6.0), (1.6, 54.6, -4.4), HUESO_D)
    for s in (-1, 1):                                                                      # claviculas
        C('body', (s * 5.5 - 4.5, 61.2, -5.4), (s * 5.5 + 4.5, 62.8, -3.8), HUESO, rotation=[0, 0, s * 22.5],
          origin=[s * 5.5, 62, -4.6])
    C('glow_nucleo', (-4.2, 44.6, -4.3), (4.2, 54.2, -3.9), '#4a1478')                     # luz adentro del pecho
    C('glow_nucleo', (-0.55, 45.2, -6.9), (0.55, 53.8, -6.1), '#ffffff')
    C('glow_nucleo', (-3.9, 48.95, -6.9), (3.9, 50.05, -6.1), '#ffffff')
    C('glow_nucleo', (-2.0, 47.5, -6.6), (2.0, 51.5, -5.8), LUZ, rotation=[0, 0, 45])
    C('glow_nucleo', (-2.9, 46.6, -6.2), (2.9, 52.4, -5.5), '#a020d0', rotation=[0, 0, 45])

    # ------------------------------------------------------------------ tunica alrededor del pecho (solapas y espalda)
    for s in (-1, 1):
        x0, x1 = sorted((s * 7, s * 12.5))
        C('body', (x0, 40, -6.6), (x1, 64, 6), TUN, pat='cloth',
          decals={'north': [(0 if s > 0 else 4, 0, 1, 24, ORO), (1 if s > 0 else 3, 0, 1, 24, ORO_D)] + _tela(5, 24, f's{s}'),
                  'east': _tela(12, 24, f'e{s}'), 'west': _tela(12, 24, f'w{s}')})
        for y in (44, 50, 56):
            C('body', (s * 7.6 - 0.7, y, -7.2), (s * 7.6 + 0.7, y + 1.4, -6.5), ORO)
    C('body', (-12.5, 40, 5), (12.5, 66, 8), TUN, pat='cloth', decals={'south': _borde(25, 26) + _tela(25, 26, 'esp')})
    C('body', (-2.4, 66.2, 7.6), (2.4, 70.6, 8.6), ORO, rotation=[0, 0, 45], origin=[0, 68.4, 8.1])   # gema de la espalda
    C('body', (-1.2, 67.4, 8.4), (1.2, 69.4, 9.0), LUZ)
    # cuello alto de la tunica
    C('body', (-10.5, 62, 4), (10.5, 76, 7.5), TUN, pat='cloth', decals={'north': [(0, 0, 21, 1, ORO)] + _tela(21, 14, 'c1'),
                                                                        'south': _borde(21, 14) + _tela(21, 14, 'c2')})
    for s in (-1, 1):
        x0, x1 = sorted((s * 9, s * 12))
        C('body', (x0, 62, -4), (x1, 75, 6), TUN, pat='cloth', decals={'up': [(0, 0, 3, 10, ORO)], 'north': _borde(3, 13)},
          rotation=[0, s * -22.5, 0], origin=[s * 10.5, 68, 1])

    # ------------------------------------------------------------------ hombreras en capas con borde dorado
    for s in (-1, 1):
        x0, x1 = sorted((s * 10, s * 25))
        R('body', (x0, 61.5, -8.5), (x1, 66.5, 8.5), TUN, pat='cloth', decals={'up': _borde(15, 17) + _tela(15, 17, f'h{s}'),
                                                                                'north': _borde(15, 5)})
        x0, x1 = sorted((s * 11, s * 22))
        R('body', (x0, 66, -6.5), (x1, 69.5, 6.5), TUN_L, pat='cloth', decals={'up': _borde(11, 13) + _tela(11, 13, f'g{s}', TUN, TUN_D)})
        x0, x1 = sorted((s * 12.5, s * 21.5))
        C('body', (x0, 54.5, -9.6), (x1, 62, -8.4), TUN, pat='cloth', decals={'north': _borde(9, 8) + _tela(9, 8, f'p{s}')})
        C('body', (s * 17 - 2.6, 52.6, -9.5), (s * 17 + 2.6, 57.8, -8.5), TUN, rotation=[0, 0, 45], origin=[s * 17, 55.2, -9])
        C('body', (s * 17 - 1.7, 53.5, -9.8), (s * 17 + 1.7, 56.9, -8.8), ORO, rotation=[0, 0, 45], origin=[s * 17, 55.2, -9])
        C('body', (s * 17 - 0.8, 54.4, -10.1), (s * 17 + 0.8, 56.0, -9.4), LUZ)
        for k in range(4):                                                                 # flecos dorados
            x = s * (12.8 + k * 2.6)
            C('body', (x - 0.4, 57.5 - (k % 2) * 1.5, -10.0), (x + 0.4, 61.6, -9.5), ORO_L if k % 2 else ORO)

    # ------------------------------------------------------------------ cinturon con hebillas
    C('body', (-11, 38, -7), (11, 42, 6.5), TUN_O, decals={'north': [(0, 0, 22, 1, ORO), (0, 3, 22, 1, ORO)]})
    for (x, w) in ((-6.6, 3.6), (0, 4.6), (6.6, 3.6)):
        C('body', (x - w / 2, 40 - w / 2, -7.8), (x + w / 2, 40 + w / 2, -6.8), ORO,
          decals={'north': [(1, 1, int(w) - 2, int(w) - 2, TUN_O)]})
    C('body', (-0.9, 39.1, -8.1), (0.9, 40.9, -7.5), LUZ)
    C('body', (-1.6, 34, -7.6), (1.6, 38, -6.8), ORO, decals={'north': [(1, 1, 1, 2, TUN_O)]})
    C('body', (-1.1, 32.6, -7.6), (1.1, 34.8, -6.8), ORO, rotation=[0, 0, 45], origin=[0, 33.7, -7.2])

    # ------------------------------------------------------------------ tunica en tres capas (4 partes que se mueven)
    import random

    def capa(bone, eje, a0, a1, f0, f1, seed, fondo, colores, cara, oro=True, brilla=False, top=38.2):
        """Una capa: tiras con largos distintos entre f0..f1 de profundidad; borde dorado abajo y/o punta que brilla."""
        r = random.Random(seed)
        a = a0
        while a < a1 - 0.3:
            w = min(a1 - a, r.choice((1.8, 2.2, 2.6, 3.0)))
            bot = fondo + r.choice((0, 1.5, 3, 4.5))
            col = r.choice(colores)
            hh = int(top - bot)
            dec = _tela(int(w) + 1, hh, f'{seed}{a}', TUN_L, TUN_O)
            if oro:
                dec += [(0, hh - 1, int(w) + 1, 1, ORO), (0, hh - 2, int(w) + 1, 1, ORO_D)]
            if eje == 'x':
                frm, to = (a, bot, f0), (a + w, top, f1)
                gfrm, gto = (a + 0.25, bot - 2.0, f0 + 0.1), (a + w - 0.25, bot + 0.4, f1 - 0.1)
            else:
                frm, to = (f0, bot, a), (f1, top, a + w)
                gfrm, gto = (f0 + 0.1, bot - 2.0, a + 0.25), (f1 - 0.1, bot + 0.4, a + w - 0.25)
            C(bone, frm, to, col, pat='cloth', decals={cara: dec})
            if oro and r.random() < .45:                                                   # punta dorada de la capa
                c = ((a + w / 2, bot, (f0 + f1) / 2) if eje == 'x' else ((f0 + f1) / 2, bot, a + w / 2))
                C(bone, (c[0] - 0.7, c[1] - 0.7, c[2] - 0.45), (c[0] + 0.7, c[1] + 0.7, c[2] + 0.45), ORO,
                  rotation=[0, 0, 45] if eje == 'x' else [45, 0, 0])
            if brilla and r.random() < .75:
                C('glow_' + bone, gfrm, gto, LUZ if r.random() < .6 else '#a030e0')
            a += w
    CL = (TUN_L, TUN, TUN)
    CM = (TUN, TUN, TUN_D)
    CB = (TUN_D, TUN_O, TUN)
    # frente (a los costados del tabardo)
    for (a0, a1) in ((-12, -3.9), (3.9, 12)):
        capa('cola_f', 'x', a0, a1, -8.6, -7.6, f'fA{a0}', 27, CL, 'north')
        capa('cola_f', 'x', a0 - 0.4, a1 + 0.4, -7.6, -6.6, f'fB{a0}', 16, CM, 'north')
    capa('cola_f', 'x', -12.6, 12.6, -6.6, -5.6, 'fC', 5, CB, 'north', oro=False, brilla=True)
    # atras
    capa('cola_b', 'x', -12.5, 12.5, 8.2, 9.2, 'bA', 28, CL, 'south')
    capa('cola_b', 'x', -13, 13, 7.2, 8.2, 'bB', 16, CM, 'south')
    capa('cola_b', 'x', -13.4, 13.4, 6.2, 7.2, 'bC', 4, CB, 'south', oro=False, brilla=True)
    # costados
    for bone, sgn, cara in (('cola_r', -1, 'west'), ('cola_l', 1, 'east')):
        for k, (fondo, cols, oro, brilla) in enumerate(((28, CL, True, False), (16, CM, True, False), (6, CB, False, True))):
            f0, f1 = sorted((sgn * (14.0 - k), sgn * (13.0 - k)))
            capa(bone, 'z', -6.8 - k * 0.4, 6.8 + k * 0.4, f0, f1, f'{bone}{k}', fondo, cols, cara, oro=oro, brilla=brilla)
    # tabardo del frente (encima de todo: borde dorado, cruces y punta)
    C('cola_f', (-3.9, 7, -9.5), (3.9, 38.2, -8.5), TUN_O, decals={'north': _guarda(8, 31, 'tab')})
    C('cola_f', (-2.7, 4.3, -9.4), (2.7, 9.7, -8.6), TUN_O, decals={'north': _borde(5, 5)}, rotation=[0, 0, 45], origin=[0, 7, -9.0])
    C('cola_f', (-1.2, 5.8, -9.7), (1.2, 8.2, -9.2), ORO, rotation=[0, 0, 45], origin=[0, 7, -9.45])
    C('glow_cola_f', (-0.6, 2.6, -9.2), (0.6, 4.6, -8.8), LUZ)
    # capa de atras: panel con borde dorado, emblema y punta
    C('cola_b', (-8, 9, 9.2), (8, 38.2, 10.2), TUN, pat='cloth', decals={'south': _borde(16, 29) + _tela(16, 29, 'capa')})
    C('cola_b', (-3.6, 12, 10.1), (3.6, 36, 10.6), TUN_O, decals={'south': _guarda(7, 24, 'capa2')})
    C('cola_b', (-2.8, 9.2, 10.0), (2.8, 14.8, 10.5), ORO, rotation=[0, 0, 45], origin=[0, 12, 10.25])

    # ------------------------------------------------------------------ cabeza: calavera (cuencas hundidas, nariz, pomulos, dientes)
    C('head', (-1.6, 63, -1.6), (1.6, 68, 1.6), HUESO_D)                                    # vertebras
    R('head', (-7.2, 71.5, -6.6), (7.2, 84.5, 7), HUESO, decals={'east': [(5, 3, 6, 1, HUESO_D), (9, 4, 1, 4, HUESO_D)],
                                                                 'west': [(5, 3, 6, 1, HUESO_D)], 'up': [(3, 2, 1, 6, HUESO_D)]})
    C('head', (-6.8, 77.5, -7.3), (6.8, 83.2, -6.2), HUESO, decals={'north': [(9, 0, 1, 2, HUESO_O), (10, 2, 1, 2, HUESO_O), (3, 1, 1, 2, HUESO_D)]})
    for s in (-1, 1):
        sx = s * 4.1
        C('head', (sx - 2.3, 73.2, -7.6), (sx + 2.3, 77.6, -6.7), CUENCA)                   # cuenca hundida
        x0, x1 = sorted((s * 0.9, s * 7.2))
        C('head', (x0, 77.4, -8.4), (x1, 79.0, -6.6), HUESO_D, rotation=[0, 0, s * -22.5], origin=[s * 4.0, 78.2, -7.5])  # ceja
        x0, x1 = sorted((s * 1.6, s * 7.0))
        C('head', (x0, 72.2, -7.9), (x1, 73.4, -5.8), HUESO, decals={'north': [(0, 0, 5, 1, '#ffffff')]})               # borde de abajo
        x0, x1 = sorted((s * 6.4, s * 7.4))
        C('head', (x0, 72.2, -7.7), (x1, 77.6, -5.8), HUESO)                                # borde de afuera
        x0, x1 = sorted((s * 5.2, s * 8.0))
        C('head', (x0, 70.6, -6.4), (x1, 73.0, 3.0), HUESO_D)                               # pomulo
        C('glow_ojos', (sx - 0.8, 74.6, -7.75), (sx + 0.8, 76.2, -7.5), LUZ)                # pupila que brilla
        C('glow_ojos', (sx - 0.3, 75.1, -7.85), (sx + 0.3, 75.7, -7.7), '#ffffff')
    C('head', (-1.2, 71.0, -7.7), (1.2, 73.8, -6.6), CUENCA)                                # nariz
    for s in (-1, 1):
        C('head', (s * 0.6 - 0.6, 72.9, -7.8), (s * 0.6 + 0.6, 74.1, -6.7), CUENCA, rotation=[0, 0, 45], origin=[s * 0.6, 73.5, -7.2])
    C('head', (-5.2, 68.4, -7.3), (5.2, 71.4, -2.0), HUESO, decals={'north': [(0, 0, 10, 1, HUESO_D)]})   # maxilar
    for k in range(8):                                                                      # dientes de arriba
        x = -4.6 + k * 1.3
        largo = 1.9 if k in (1, 6) else 1.4
        C('head', (x, 69.0 - largo, -7.55), (x + 1.05, 69.2, -6.7), '#fbf6ff', decals={'north': [(0, 0, 1, 1, HUESO_D)]})
    # mandibula (se mueve): dientes de abajo, menton y ramas que suben a la cara
    C('jaw', (-5.4, 64.6, -7.2), (5.4, 66.6, -1.8), HUESO, decals={'north': [(0, 1, 11, 1, HUESO_D)]})
    C('jaw', (-2.8, 63.6, -7.5), (2.8, 64.8, -5.6), HUESO_D)
    for k in range(7):
        x = -4.2 + k * 1.3
        C('jaw', (x, 66.4, -7.45), (x + 1.05, 67.9, -6.6), '#fbf6ff')
    for s in (-1, 1):
        x0, x1 = sorted((s * 4.6, s * 6.0))
        C('jaw', (x0, 64.6, -4.6), (x1, 71.0, -0.6), HUESO_D)
    # corona: aro dorado con gema y un racimo de AMATISTAS facetadas (rombo de frente, punta clara que brilla)
    C('corona', (-8.0, 81, -8.0), (8.0, 85, 7.6), ORO, decals={f: [(1, 1, w - 2, 2, AME_O)] for f, w in (('north', 16), ('south', 16), ('east', 15), ('west', 15))})
    C('corona', (-8.6, 84.4, -8.6), (8.6, 85.6, 8.2), ORO_D)
    C('corona', (-8.6, 80.4, -8.6), (8.6, 81.4, 8.2), ORO_D)
    C('corona', (-2.8, 80.6, -9.4), (2.8, 86.2, -8.2), ORO, decals={'north': _borde(6, 6, ORO_D)}, rotation=[0, 0, 45], origin=[0, 83.4, -8.8])
    C('glow_corona', (-1.6, 81.8, -9.8), (1.6, 85.0, -9.1), AME_L, rotation=[0, 0, 45], origin=[0, 83.4, -9.45])

    def amatista(x, z, h, w, base=85.0, rot=None, glow=True):
        """Cristal de amatista: cuerpo violeta con cara clara (faceta), tramo de arriba mas fino y punta brillante."""
        r = rot or [0, 45, 0]
        org = [x, base, z]
        hb = max(1, int(h * .62))
        C('corona', (x - w / 2, base, z - w / 2), (x + w / 2, base + h * 0.62, z + w / 2), AME,
          decals={'north': [(0, 0, 1, hb, AME_L), (max(0, int(w) - 1), 0, 1, hb, AME_D)],
                  'east': [(0, 0, 1, hb, AME_H)], 'west': [(0, 0, 1, hb, AME_D)],
                  'south': [(0, 0, 1, hb, AME_D)]}, rotation=r, origin=org)
        C('corona', (x - w * .34, base + h * 0.6, z - w * .34), (x + w * .34, base + h * 0.88, z + w * .34), AME_L,
          decals={'east': [(0, 0, 1, int(h * .28) + 1, AME_H)]}, rotation=r, origin=org)
        if glow:
            C('glow_corona', (x - w * .17, base + h * 0.86, z - w * .17), (x + w * .17, base + h, z + w * .17), AME_H, rotation=r, origin=org)
    # grandes (parados, rombo) y chicos inclinados alrededor, como un racimo
    for (x, z, h, w) in ((0, -7.2, 15, 3.4), (-4.3, -6.8, 11, 2.8), (4.3, -6.8, 11, 2.8), (-7.0, -2.8, 9, 2.4), (7.0, -2.8, 9, 2.4),
                         (-6.6, 3.2, 8, 2.2), (6.6, 3.2, 8, 2.2), (-2.8, 6.6, 10, 2.6), (2.8, 6.6, 10, 2.6), (0, 0, 7, 2.6)):
        amatista(x, z, h, w)
    for (x, z, h, w, rot) in ((-2.2, -8.2, 6, 1.6, [0, 0, 22.5]), (2.2, -8.2, 6, 1.6, [0, 0, -22.5]), (-8.2, 0, 5, 1.5, [0, 0, 22.5]),
                              (8.2, 0, 5, 1.5, [0, 0, -22.5]), (-5.5, -7.8, 5, 1.4, [-22.5, 0, 0]), (5.5, -7.8, 5, 1.4, [-22.5, 0, 0]),
                              (0, 8.2, 6, 1.6, [22.5, 0, 0])):
        amatista(x, z, h, w, rot=rot, glow=False)
    for s in (-1, 1):                                                                       # cuernitos de hueso a los costados
        C('corona', (s * 9.6 - 1.2, 82, -2), (s * 9.6 + 1.2, 88, 0.4), HUESO_D, rotation=[0, 0, s * -45], origin=[s * 8.5, 83, -0.8])
        C('corona', (s * 11.8 - 0.7, 86, -1.5), (s * 11.8 + 0.7, 89.5, -0.1), HUESO, rotation=[0, 0, s * -22.5], origin=[s * 11.8, 86, -0.8])

    # ------------------------------------------------------------------ seis brazos: manga, brazalete y mano de hueso
    for n, (piv, rot, rot2) in BRAZOS.items():
        for s, lado in ((-1, 'r'), (1, 'l')):
            x, y, z = piv[0] * s, piv[1], piv[2]
            a, f = f'arm_{n}{lado}', f'ante_{n}{lado}'
            R(a, (x - 3, y - 14.5, z - 3), (x + 3, y + 1.5, z + 3), TUN, pat='cloth', decals={'north': _tela(6, 16, a), 'south': _tela(6, 16, a + 's')})
            C(a, (x - 3.4, y - 14.8, z - 3.4), (x + 3.4, y - 12.6, z + 3.4), ORO, decals={'north': [(0, 1, 7, 1, ORO_D)]})
            C(f, (x - 2.8, y - 24, z - 2.8), (x + 2.8, y - 14, z + 2.8), TUN_L, pat='cloth', decals={'north': _tela(6, 10, f)})
            C(f, (x - 3.8, y - 24.6, z - 3.8), (x + 3.8, y - 20.4, z + 3.8), ORO,
              decals={g: [(0, 0, 8, 1, ORO_L), (0, 3, 8, 1, ORO_D), (3, 1, 2, 2, LUZ)] for g in ('north', 'south', 'east', 'west')})
            # mano de hueso: palma con nudillos, cuatro dedos de tres falanges que se curvan y pulgar
            C(f, (x - 2.2, y - 28, z - 1.4), (x + 2.2, y - 24.4, z + 1.4), HUESO, decals={'north': [(0, 0, 4, 1, HUESO_D), (1, 2, 1, 1, HUESO_D)]})
            C(f, (x - 2.4, y - 28.6, z - 1.2), (x + 2.4, y - 27.4, z + 0.6), HUESO_D)
            for k, dx in enumerate((-1.65, -0.55, 0.55, 1.65)):
                l1, l2, l3 = ((2.6, 2.0, 1.8), (3.0, 2.4, 2.0), (2.9, 2.2, 1.9), (2.4, 1.8, 1.6))[k]
                y1 = y - 28.4
                C(f, (x + dx - 0.45, y1 - l1, z - 0.9), (x + dx + 0.45, y1, z), HUESO)
                C(f, (x + dx - 0.55, y1 - l1 - 0.45, z - 1.0), (x + dx + 0.55, y1 - l1 + 0.45, z + 0.1), HUESO_D)   # nudillo
                o2 = [x + dx, y1 - l1, z - 0.45]
                C(f, (x + dx - 0.4, o2[1] - l2, z - 0.85), (x + dx + 0.4, o2[1], z - 0.05), HUESO, rotation=[22.5, 0, 0], origin=o2)
                o3 = [x + dx, o2[1] - l2 * 0.9239, o2[2] - l2 * 0.3827]
                C(f, (x + dx - 0.32, o3[1] - l3, o3[2] - 0.32), (x + dx + 0.32, o3[1], o3[2] + 0.32), '#f6f0fa',
                  decals={'north': [(0, max(0, int(l3) - 1), 1, 1, HUESO_D)]}, rotation=[45, 0, 0], origin=o3)
            C(f, (x - s * 2.6 - 0.45, y - 30.5, z - 2.2), (x - s * 2.6 + 0.45, y - 26, z - 1.2), HUESO_D)
            C(f, (x - s * 2.6 - 0.35, y - 32.4, z - 2.7), (x - s * 2.6 + 0.35, y - 30.4, z - 2.0), HUESO, rotation=[22.5, 0, 0],
              origin=[x - s * 2.6, y - 30.5, z - 1.7])

    animations(m)
    return m


def animations(m):
    from animaciones import kf
    w = 'math.sin(q.anim_time * 360 * {s} + {p}) * {a}'
    ARMS = [(n, s, l) for n in 'uml' for s, l in ((-1, 'r'), (1, 'l'))]

    def colas(base=0, amp=5, s=0.5):
        r = lambda x: round(x, 2)   # BetterModel no lee numeros con muchos decimales
        return {'cola_b': {'rotation': (f'{r(base)} + {w.format(s=s, p=0, a=r(amp))}', 0, 0)},
                'cola_f': {'rotation': (f'{r(-base * .4)} + {w.format(s=s, p=90, a=r(amp * .6))}', 0, 0)},
                'cola_r': {'rotation': (f'{r(base * .3)}', 0, f'{w.format(s=s, p=60, a=r(amp * .7))}')},
                'cola_l': {'rotation': (f'{r(base * .3)}', 0, f'{w.format(s=s, p=240, a=r(amp * .7))}')}}

    def brazos(fn):
        """fn(n, s) -> {bone: channels} sumando sobre la pose base."""
        out = {}
        for n, s, l in ARMS:
            out.update(fn(n, s, l))
        return out

    def hang(n, s, k=1.0):
        """Delta que lleva el brazo de la pose a colgar (k=1) - para aparecer/morir."""
        p = _pose(n, s, 1)
        return (-p[0] * k, 0, -p[2] * k)

    fase = {'ur': 0, 'ul': 180, 'mr': 90, 'ml': 270, 'lr': 45, 'll': 225}
    m.anim('idle', 4.0, {
        'root': {'position': (0, f'3 + {w.format(s=0.5, p=0, a=2)}', 0)},
        'body': {'rotation': (w.format(s=0.25, p=0, a=2), w.format(s=0.25, p=90, a=4), 0)},
        'head': {'rotation': (w.format(s=0.5, p=90, a=4), w.format(s=0.25, p=0, a=12), w.format(s=0.25, p=45, a=3))},
        'jaw': {'rotation': (f'-3 + {w.format(s=0.5, p=0, a=3)}', 0, 0)},
        'glow_nucleo': {'scale': (f'1 + {w.format(s=1, p=0, a=0.15)}', f'1 + {w.format(s=1, p=0, a=0.15)}', 1)},
        **brazos(lambda n, s, l: {
            f'arm_{n}{l}': {'rotation': (w.format(s=0.5, p=fase[n + l], a=6), 0, w.format(s=0.5, p=fase[n + l] + 90, a=7))},
            f'ante_{n}{l}': {'rotation': (w.format(s=0.5, p=fase[n + l] + 45, a=8), 0, w.format(s=0.5, p=fase[n + l], a=6))}}),
        **colas(),
    })
    m.anim('walk', 2.0, {
        'root': {'position': (0, f'3 + {w.format(s=0.5, p=0, a=2)}', 0)},
        'body': {'rotation': (-10, w.format(s=0.5, p=0, a=5), 0)},
        'head': {'rotation': (8, w.format(s=0.5, p=180, a=4), 0)},
        **brazos(lambda n, s, l: {f'arm_{n}{l}': {'rotation': (f'-12 + {w.format(s=0.5, p=fase[n + l], a=8)}', 0, 0)}}),
        **colas(-24, 7, 1),
    })
    # Combo (~onAttack): los de arriba suben y golpean hacia abajo, los de abajo pinchan adelante (dano ~0,45 s).
    m.anim('attack', 1.1, {
        'body': {'rotation': kf((0, 0, 0, 0), (.25, 12, 0, 0), (.45, -16, 0, 0), (.7, -10, 0, 0), (1.1, 0, 0, 0)),
                 'position': kf((0, 0, 0, 0), (.45, 0, -1, -5), (.8, 0, -1, -4), (1.1, 0, 0, 0))},
        'head': {'rotation': kf((0, 0, 0, 0), (.25, 14, 0, 0), (.45, -12, 0, 0), (1.1, 0, 0, 0))},
        'jaw': {'rotation': kf((0, -3, 0, 0), (.3, -35, 0, 0), (.8, -32, 0, 0), (1.1, -3, 0, 0))},
        **brazos(lambda n, s, l: {
            f'arm_{n}{l}': {'rotation': kf((0, 0, 0, 0), (.25, -25, 0, s * 20) if n != 'l' else (.25, -45, 0, 0),
                                            (.45, 70, 0, -s * 70) if n == 'u' else (.45, 55, 0, -s * 45) if n == 'm' else (.45, 45, 0, -s * 10),
                                            (.7, 55, 0, -s * 55) if n == 'u' else (.7, 40, 0, -s * 30) if n == 'm' else (.7, 35, 0, 0),
                                            (1.1, 0, 0, 0))},
            f'ante_{n}{l}': {'rotation': kf((0, 0, 0, 0), (.25, 0, 0, s * 15), (.45, 25, 0, -s * 20), (1.1, 0, 0, 0))}}),
        **colas(10, 4, 1),
    }, loop='once')
    # Barrido del vacio: gira 360 grados con los seis brazos abiertos (dano a los 0,55 s).
    m.anim('barrido', 1.4, {
        'root': {'rotation': kf((0, 0, 0, 0), (.25, 0, -25, 0), (.85, 0, 360, 0), (1.4, 0, 360, 0)),
                 'position': kf((0, 0, 3, 0), (.25, 0, 1, 0), (.55, 0, 6, 0), (.85, 0, 3, 0), (1.4, 0, 3, 0))},
        **brazos(lambda n, s, l: {
            f'arm_{n}{l}': {'rotation': kf((0, 0, 0, 0), (.25, -_pose(n, s)[0], 0, s * 90 - _pose(n, s)[2] + s * (25 if n == 'u' else 0 if n == 'm' else -25)),
                                            (.85, -_pose(n, s)[0], 0, s * 90 - _pose(n, s)[2] + s * (25 if n == 'u' else 0 if n == 'm' else -25)),
                                            (1.4, 0, 0, 0))},
            f'ante_{n}{l}': {'rotation': kf((0, 0, 0, 0), (.25, -_pose(n, s, 2)[0], 0, -_pose(n, s, 2)[2]),
                                             (.85, -_pose(n, s, 2)[0], 0, -_pose(n, s, 2)[2]), (1.4, 0, 0, 0))}}),
        'cola_b': {'rotation': kf((0, 0, 0, 0), (.55, -45, 0, 0), (.85, -35, 0, 0), (1.4, 0, 0, 0))},
        'cola_f': {'rotation': kf((0, 0, 0, 0), (.55, 25, 0, 0), (.85, 20, 0, 0), (1.4, 0, 0, 0))},
        'cola_r': {'rotation': kf((0, 0, 0, 0), (.55, 0, 0, -40), (.85, 0, 0, -30), (1.4, 0, 0, 0))},
        'cola_l': {'rotation': kf((0, 0, 0, 0), (.55, 0, 0, 40), (.85, 0, 0, 30), (1.4, 0, 0, 0))},
        'jaw': {'rotation': kf((0, -3, 0, 0), (.3, -30, 0, 0), (1.0, -30, 0, 0), (1.4, -3, 0, 0))},
    }, loop='once')
    # Lanzamiento: un brazo de abajo va atras y tira (sale a los 0,45 s).
    m.anim('throw', 0.8, {
        'arm_lr': {'rotation': kf((0, 0, 0, 0), (.3, -95, 0, 0), (.45, 40, 0, 0), (.8, 0, 0, 0))},
        'arm_ll': {'rotation': kf((0, 0, 0, 0), (.3, -70, 0, 0), (.5, 30, 0, 0), (.8, 0, 0, 0))},
        'body': {'rotation': kf((0, 0, 0, 0), (.3, 10, 12, 0), (.45, -14, -10, 0), (.8, 0, 0, 0))},
        'head': {'rotation': kf((0, 0, 0, 0), (.3, 10, 0, 0), (.45, -12, 0, 0), (.8, 0, 0, 0))},
    }, loop='once')
    # Salto del vacio: se encoge girando y reaparece (la skill lo lleva detras del jugador a los 0,5 s).
    m.anim('salto', 1.0, {
        'root': {'scale': kf((0, 1, 1, 1), (.45, .15, 1.4, .15), (.5, .05, .05, .05), (.6, .05, .05, .05), (.8, 1.15, 1.15, 1.15), (1.0, 1, 1, 1)),
                 'rotation': kf((0, 0, 0, 0), (.45, 0, 180, 0), (.5, 0, 180, 0), (.8, 0, 360, 0), (1.0, 0, 360, 0))},
    }, loop='once')
    # Furia (cambio de fase): ruge mirando arriba y abre los seis brazos; la estrella del pecho se agranda.
    m.anim('furia', 1.6, {
        'body': {'rotation': kf((0, 0, 0, 0), (.4, -14, 0, 0), (.8, 14, 0, 0), (1.3, 12, 0, 0), (1.6, 0, 0, 0))},
        'head': {'rotation': kf((0, 0, 0, 0), (.4, -15, 0, 0), (.8, 30, 0, 0), (1.3, 26, 0, 0), (1.6, 0, 0, 0))},
        'jaw': {'rotation': kf((0, -3, 0, 0), (.4, -3, 0, 0), (.8, -42, 0, 0), (1.3, -40, 0, 0), (1.6, -3, 0, 0))},
        **brazos(lambda n, s, l: {
            f'arm_{n}{l}': {'rotation': kf((0, 0, 0, 0), (.4, 10, 0, -s * 15), (.8, -20, 0, s * 25), (1.3, -18, 0, s * 22), (1.6, 0, 0, 0))},
            f'ante_{n}{l}': {'rotation': kf((0, 0, 0, 0), (.8, 0, 0, -s * 20), (1.3, 0, 0, -s * 18), (1.6, 0, 0, 0))}}),
        'glow_nucleo': {'scale': kf((0, 1, 1, 1), (.8, 2.0, 2.0, 2.0), (1.3, 1.8, 1.8, 1.8), (1.6, 1, 1, 1))},
        'corona': {'position': kf((0, 0, 0, 0), (.8, 0, 1.5, 0), (1.3, 0, 1.2, 0), (1.6, 0, 0, 0))},
        'cola_b': {'rotation': kf((0, 0, 0, 0), (.8, -30, 0, 0), (1.3, -26, 0, 0), (1.6, 0, 0, 0))},
    }, loop='once')
    # Pulso de gravedad: se eleva con los brazos arriba y baja de golpe (dano a los 1,1 s).
    m.anim('pulso', 1.4, {
        'root': {'position': kf((0, 0, 3, 0), (.6, 0, 22, 0), (.95, 0, 24, 0), (1.1, 0, 0, 0), (1.4, 0, 3, 0))},
        **brazos(lambda n, s, l: {
            f'arm_{n}{l}': {'rotation': kf((0, 0, 0, 0), (.6, -10, 0, s * 25), (1.1, 45, 0, -s * 50), (1.4, 0, 0, 0))}}),
        'cola_b': {'rotation': kf((0, 0, 0, 0), (.6, 20, 0, 0), (1.1, -45, 0, 0), (1.4, 0, 0, 0))},
        'cola_f': {'rotation': kf((0, 0, 0, 0), (.6, -15, 0, 0), (1.1, 30, 0, 0), (1.4, 0, 0, 0))},
        'glow_nucleo': {'scale': kf((0, 1, 1, 1), (.95, 1.8, 1.8, 1.8), (1.1, .8, .8, .8), (1.4, 1, 1, 1))},
    }, loop='once')
    # Aparece: sube desde abajo con los brazos colgando y los va abriendo; la corona se enciende.
    m.anim('aparece', 2.0, {
        'root': {'position': kf((0, 0, -100, 0), (1.2, 0, 0, 0), (1.5, 0, 6, 0), (2.0, 0, 3, 0))},
        'head': {'rotation': kf((0, -30, 0, 0), (1.2, -30, 0, 0), (1.5, 30, 0, 0), (2.0, 0, 0, 0))},
        'jaw': {'rotation': kf((0, -3, 0, 0), (1.3, -3, 0, 0), (1.5, -40, 0, 0), (2.0, -3, 0, 0))},
        **brazos(lambda n, s, l: {
            f'arm_{n}{l}': {'rotation': kf((0, *hang(n, s, 0.9)), (1.2, *hang(n, s, 0.9)), (1.6, 0, 0, s * 15), (2.0, 0, 0, 0))}}),
        'corona': {'scale': kf((0, .1, .1, .1), (1.3, .1, .1, .1), (1.6, 1.3, 1.3, 1.3), (2.0, 1, 1, 1))},
    }, loop='once')
    # Muerte: la estrella estalla, se le cae la corona, los brazos caen y se hunde.
    m.anim('death', 2.2, {
        'root': {'position': kf((0, 0, 3, 0), (.5, 0, 8, 0), (1.4, 0, -10, 0), (2.2, 0, -40, 0))},
        'body': {'rotation': kf((0, 0, 0, 0), (.5, 15, 0, 0), (1.4, -30, 10, 0), (2.2, -70, 20, 0))},
        'head': {'rotation': kf((0, 0, 0, 0), (.5, 35, 0, 0), (1.4, -30, 0, 0), (2.2, -40, 0, 0))},
        'jaw': {'rotation': kf((0, -3, 0, 0), (.5, -45, 0, 0), (2.2, -35, 0, 0))},
        'corona': {'position': kf((0, 0, 0, 0), (.5, 0, 5, 0), (1.4, 0, -20, 6), (2.2, 0, -60, 12)),
                   'rotation': kf((0, 0, 0, 0), (.5, -15, 0, 10), (1.4, 50, 30, 40), (2.2, 90, 60, 80))},
        **brazos(lambda n, s, l: {
            f'arm_{n}{l}': {'rotation': kf((0, 0, 0, 0), (.5, -10, 0, s * 20), (1.4, *hang(n, s, 0.6)), (2.2, *hang(n, s, 0.85)))}}),
        'glow_nucleo': {'scale': kf((0, 1, 1, 1), (.5, 2.4, 2.4, 2.4), (1.4, .4, .4, .4), (2.2, .05, .05, .05))},
    }, loop='hold')


def build_ojo():
    """Ojo Vigia: cubo verde azulado con un ojo en cada cara y cuatro aletas."""
    m = Model(OJO_ID)
    m.bone('root', (0, 0, 0))
    m.bone('body', (0, 10, 0), 'root')
    m.bone('glow_ojo', (0, 10, 0), 'body')
    m.bone('mtag_nombre', (0, 22, 0), 'root')
    for (a, b) in (((-3, 7, -6.4), (3, 13, -6.05)), ((-3, 7, 6.05), (3, 13, 6.4)), ((-6.4, 7, -3), (-6.05, 13, 3)), ((6.05, 7, -3), (6.4, 13, 3))):
        m.cube('glow_ojo', a, b, '#5affc0', decals={f: [(2, 2, 2, 2, VERDE_OSC), (2, 2, 1, 1, '#ffffff')] for f in ('north', 'south', 'east', 'west')})
    ojo = [(1, 1, 10, 10, VERDE), (3, 3, 6, 6, '#9dffd4'), (4, 4, 4, 4, VERDE_OSC), (5, 5, 1, 1, '#ffffff')]
    m.rcube('body', (-6, 4, -6), (6, 16, 6), TEAL, pat='stone', decals={f: ojo for f in ('north', 'south', 'east', 'west')})
    for (a, b) in (((-8, 8, -1), (-6, 12, 1)), ((6, 8, -1), (8, 12, 1)), ((-1, 16, -1), (1, 19, 1)), ((-1, 1, -1), (1, 4, 1))):
        m.cube('body', a, b, '#0c2a24', decals={'north': [(0, 0, 2, 1, VERDE)]})
    w = 'math.sin(q.anim_time * 360 * {s} + {p}) * {a}'
    m.anim('idle', 2.0, {'body': {'rotation': (w.format(s=0.5, p=0, a=10), 'q.anim_time * 45', w.format(s=0.5, p=90, a=10)),
                                  'position': (0, w.format(s=0.5, p=0, a=1.5), 0)}})
    m.anim('walk', 2.0, {'body': {'rotation': (w.format(s=0.5, p=0, a=10), 'q.anim_time * 90', 0)}})
    m.anim('attack', 0.6, {'body': {'scale': [(0, (1, 1, 1)), (.2, (1.3, 1.3, 1.3)), (.35, (.9, .9, .9)), (.6, (1, 1, 1))]}}, loop='once')
    m.anim('death', 0.8, {'body': {'scale': [(0, (1, 1, 1)), (.3, (1.5, 1.5, 1.5)), (.8, (.05, .05, .05))]}}, loop='hold')
    return m


# ------------------------------------------------------------------ MythicMobs
def q(s):
    return "'" + s.replace("'", "''") + "'"


def vida():
    from escala import VIDA_JEFE
    return round(VIDA_JEFE['forja'] * VIDA_FACTOR)


def alto_modelo():
    # 23/11: medir el .bbmodel exportado (lo que dibuja BetterModel). bounds_data(export()) dividia dos veces por 16
    # y el Capitan salia de ~70 bloques.
    from tamanos import bounds
    lo, hi = bounds(MODEL_ID)[1]
    return hi - lo


def modelo_s():
    """BetterModel multiplica la escala del modelo por la de la entidad (oceano_fosa.py, 15/11)."""
    return round(ALTO / (ESCALA * alto_modelo()), 3)


def mobs_yaml():
    from escala import VIDA_REF
    fx = __import__('efectos').mm_fx
    ojo_vida = round(vida() * OJO_VIDA)
    timonel = round(TIMONEL_EZ * VIDA_REF[5] * 1.5)
    sk = [
        'skill{s=NAVE_CAP_MODELO} @self ~onSpawn', 'skill{s=NAVE_CAP_MODELO} @self ~onLoad',
        'skill{s=NAVE_CAP_APARECE} @self ~onSpawn',
        'state{s=attack} @self ~onAttack',
        'skill{s=NAVE_CAP_CUBO} @PlayersInRing{min=5;max=40;sort=RANDOM;limit=1} ~onTimer:120',
        'skill{s=NAVE_CAP_SALTO} @PlayersInRadius{r=40;sort=RANDOM;limit=1} ~onTimer:260',
        'skill{s=NAVE_CAP_BARRIDO} @self ~onTimer:180 ?playerwithin{d=7}',
        # Escudo de los Ojos: con un Ojo Vigia vivo recibe el 20% del dano (lo descuenta AstralNave).
        'skill{s=NAVE_CAP_FASE2} @self ~onDamaged ?healthpercent{p=<0.7} ?!hastag{tag=nave.f2}',
        'skill{s=NAVE_CAP_FASE3} @self ~onDamaged ?healthpercent{p=<0.4} ?!hastag{tag=nave.f3}',
        'skill{s=NAVE_CAP_CRIAS} @self ~onTimer:400 ?hastag{tag=nave.f2}',
        'skill{s=NAVE_CAP_PULSO} @self ~onTimer:220 ?hastag{tag=nave.f3} ?playerwithin{d=40}',
        'skill{s=NAVE_CAP_ZONAS} @PlayersInRadius{r=40} ~onTimer:160 ?hastag{tag=nave.f3}',
        'skill{s=NAVE_CAP_RESET} @self ~onTimer:600 ?!playerwithin{d=48}',
        'teleport @SpawnLocation ~onTimer:100 ?!playerwithin{d=48}',
        'skill{s=NAVE_CAP_MUERE} @self ~onDeath',
    ]
    ojo = [f'model{{m={OJO_ID};s=2}} @self ~onSpawn', f'model{{m={OJO_ID};s=2}} @self ~onLoad',
           'addtag{tag=astral.seen} @self ~onSpawn', 'addtag{tag=nave.ojo} @self ~onSpawn', 'addtag{tag=astral.mt5} @self ~onSpawn',
           'command{c="attribute <caster.uuid> minecraft:scale base set 2"} @self ~onSpawn',
           'skill{s=NAVE_OJO_RAYO} @PlayersInRadius{r=32;sort=RANDOM;limit=1} ~onTimer:70',
           'skill{s=NAVE_OJO_MUERE} @self ~onDeath']
    L = [
        f'{MOB_ID}:', '  Type: ZOMBIE', "  Display: '&5&lCapitan del Vacio'", f'  Health: {vida()}',
        f'  Damage: {DANO_ZARPAZO}', '  Options:', '    Glowing: true',
        '    PreventOtherDrops: true', '    PreventItemPickup: true', '    PreventSunburn: true', '    Silent: true',
        '    Despawn: false', f'    MovementSpeed: {VELOCIDAD}', '    KnockbackResistance: 1', '    FollowRange: 48',
        '    PreventRandomEquipment: true', '    Baby: false',
        '  AIGoalSelectors:', '  - clear', '  - meleeattack', '  - lookatplayers',
        '  AITargetSelectors:', '  - clear', '  - attacker', '  - players',
        '  BossBar:', '    Enabled: true', "    Title: '&5✦ Tier V ✦ &d&lCapitan del Vacio'", '    Range: 64',
        '    Color: PURPLE', '    Style: SEGMENTED_20',
        '  Drops:', '  - exp 500',
        '  Skills:', *['  - ' + q(s) for s in sk], '',
        f'{OJO_MOB}:', '  Type: VEX', "  Display: '&a&lOjo Vigia'", f'  Health: {ojo_vida}', '  Damage: 0',
        '  Options:', '    Glowing: true', '    Silent: true', '    Despawn: false', '    PreventOtherDrops: true',
        '    PreventItemPickup: true', '    MovementSpeed: 0.2', '    KnockbackResistance: 1',
        '  AIGoalSelectors:', '  - clear', '  - lookatplayers',
        '  Skills:', *['  - ' + q(s) for s in ojo], '',
        f'{CRIA_MOB}:', '  Type: ENDERMITE', "  Display: '&dCria del Vacio'", '  Health: 20', '  Damage: 4',
        '  Options:', '    Glowing: true', '    Despawn: false', '    MovementSpeed: 0.32', '    PreventOtherDrops: true',
        '  Skills:', "  - 'command{c=\"attribute <caster.uuid> minecraft:scale base set 2.2\"} @self ~onSpawn'",
        "  - 'particles{p=portal;amount=6;hS=0.4;vS=0.3} @self ~onTimer:20'", '',
        f'{TIMONEL_MOB}:', '  Type: ENDERMAN', "  Display: '&d&lTimonel del Vacio'", f'  Health: {timonel}', '  Damage: 22',
        '  Options:', '    Glowing: true', '    Despawn: false', '    PreventTeleport: true', '    PreventOtherDrops: true',
        '    PreventItemPickup: true', '    PreventBlockPickup: true', '    MovementSpeed: 0.3', '    KnockbackResistance: 1', '    FollowRange: 40',
        '  AIGoalSelectors:', '  - clear', '  - meleeattack', '  - randomstroll',
        '  AITargetSelectors:', '  - clear', '  - attacker', '  - players',
        '  BossBar:', '    Enabled: true', "    Title: '&5✦ Tier V ✦ &d&lTimonel del Vacio'", '    Range: 48',
        '    Color: PINK', '    Style: SEGMENTED_10',
        '  Skills:', "  - 'addtag{tag=astral.seen} @self ~onSpawn'", "  - 'addtag{tag=astral.mt5} @self ~onSpawn'",
        "  - 'command{c=\"attribute <caster.uuid> minecraft:scale base set 1.4\"} @self ~onSpawn'",
        "  - 'skill{s=NAVE_TIM_SALTO} @PlayersInRadius{r=30;sort=RANDOM;limit=1} ~onTimer:200'",
        "  - 'skill{s=NAVE_CAP_CUBO} @PlayersInRing{min=5;max=30;sort=RANDOM;limit=1} ~onTimer:160'",
        '',
        f'{ZONA_MOB}:', '  Type: ARMOR_STAND', "  Display: 'Vacio'", '  Health: 1', '  Options:',
        '    Invisible: true', '    Marker: true', '    Invincible: true', '    NoGravity: true', '    Silent: true',
        '    Despawn: true', '    PreventOtherDrops: true', '    AlwaysShowName: false',
        '  Skills:', "  - 'skill{s=NAVE_ZONA} @self ~onSpawn'", '',
    ]
    return '\n'.join(L) + '\n'


def skills_yaml():
    fx = __import__('efectos').mm_fx
    from tamanos import VANILLA
    S = {
        'NAVE_CAP_MODELO': ['addtag{tag=astral.seen} @self', 'addtag{tag=astral.mt5} @self', 'addtag{tag=nave.jefe} @self',
                            f'model{{m={MODEL_ID};s={modelo_s()}}} @self',
                            f'command{{c="attribute <caster.uuid> minecraft:scale base set {ESCALA}"}} @self',
                            'command{c="attribute <caster.uuid> minecraft:step_height base set 2"} @self'],
        'NAVE_CAP_APARECE': ['state{s=aparece} @self', 'sound{s=entity.wither.spawn;v=2;p=0.6} @PlayersInRadius{r=64}',
                             'particles{p=reverse_portal;amount=300;hS=3;vS=6;y=4;speed=0.2} @self', 'delay 24',
                             fx('golpe', '#c43bff', 8, 'vacio'),
                             'message{m="&5✦ &d&lCapitan del Vacio &5✦ &7se levanta del nucleo de la nave."} @PlayersInRadius{r=64}',
                             'message{m="&d«Esta nave no vuelve a la estrella. Ustedes tampoco.»"} @PlayersInRadius{r=64}'],
        'NAVE_CAP_CUBO': ['state{s=throw} @self', 'sound{s=entity.shulker.shoot;v=2;p=0.6} @self', 'delay 9',
                          'projectile{onTick=NAVE_CUBO_TICK;onHit=NAVE_CUBO_HIT;onEnd=NAVE_CUBO_FIN;v=12;i=1;hR=1.2;vR=1.2;mr=44;'
                          'bulletType=ITEM;material=CRYING_OBSIDIAN;hnp=true;sy=2.5}'],
        'NAVE_CUBO_TICK': ['particles{p=dust;color=#c43bff;size=2;amount=3;hS=0.2;vS=0.2} @origin',
                           'particles{p=reverse_portal;amount=3;hS=0.1;vS=0.1;speed=0.05} @origin'],
        'NAVE_CUBO_HIT': [f'damage{{a={DANO_CUBO}}}', fx('estallido', '#c43bff', 2, 'vacio', 'target'),
                          'sound{s=block.respawn_anchor.deplete;v=1.5;p=0.8} @origin'],
        'NAVE_CUBO_FIN': [f'summon{{type={ZONA_MOB};amount=1;radius=0}} @origin'],
        # Zona de vacio: aviso, despues lastima 4 segundos.
        'NAVE_ZONA': ['particlering{p=dust;color=#c43bff;size=2;radius=3;points=30;amount=1;y=0.2} @self', 'delay 10',
                      'particlering{p=dust;color=#c43bff;size=2;radius=3;points=30;amount=1;y=0.2} @self', 'delay 10',
                      'skill{s=NAVE_ZONA_TICK;repeat=8;repeatInterval=10} @self', 'delay 82', 'remove @self'],
        'NAVE_ZONA_TICK': ['particles{p=dragon_breath;amount=25;hS=2.5;vS=0.2;y=0.3;speed=0.01} @self',
                           f'damage{{a={DANO_ZONA};ignoreArmor=true}} @PlayersInRadius{{r=3}}'],
        # Salto del vacio: se encoge, aparece detras del jugador y pega.
        'NAVE_CAP_SALTO': ['state{s=salto} @self', 'sound{s=entity.enderman.teleport;v=2;p=0.5} @self', 'delay 10',
                           'teleport{spreadh=0} @Forward{f=-4;y=0} ', 'delay 2',
                           'sound{s=entity.enderman.scream;v=2;p=0.6} @self', 'delay 4', 'state{s=attack} @self', 'delay 8',
                           fx('golpe', '#c43bff', 4, 'vacio'), f'damage{{a={DANO_ZARPAZO}}} @PlayersInRadius{{r=5}}',
                           'throw{velocity=6;velocityY=2} @PlayersInRadius{r=5}'],
        # Barrido del vacio: gira 360 grados con las garras abiertas (animacion barrido, golpe a los 0,55 s).
        'NAVE_CAP_BARRIDO': ['state{s=barrido} @self', 'sound{s=entity.player.attack.sweep;v=2;p=0.5} @self', 'delay 11',
                             'particlering{p=sweep_attack;radius=5;points=16;amount=1;y=3} @self',
                             'particlering{p=dust;color=#e25aff;size=2;radius=6;points=40;amount=1;y=2} @self',
                             'sound{s=entity.wither.break_block;v=1.2;p=1.4} @self',
                             f'damage{{a={DANO_BARRIDO}}} @PlayersInRadius{{r=7}}', 'throw{velocity=7;velocityY=1.5} @PlayersInRadius{r=7}'],
        'NAVE_CAP_FASE2': ['addtag{tag=nave.f2} @self', 'state{s=furia} @self', fx('golpe', '#1fd38a', 6, 'arcano'),
                           'sound{s=entity.elder_guardian.curse;v=2;p=0.8} @PlayersInRadius{r=64}',
                           'message{m="&a«Vigias. Abran los ojos.» &7(rompe los Ojos Vigias para danar al Capitan)"} @PlayersInRadius{r=64}',
                           f'summon{{type={OJO_MOB};amount={OJOS};radius=6;yOffset=6}} @self'],
        'NAVE_CAP_FASE3': ['addtag{tag=nave.f3} @self', 'state{s=furia} @self', fx('golpe', '#c43bff', 9, 'vacio'),
                           'potion{type=SPEED;duration=2147483647;level=0;hasParticles=false} @self',
                           'sound{s=entity.ender_dragon.growl;v=2;p=0.7} @PlayersInRadius{r=64}',
                           'particles{p=reverse_portal;amount=250;hS=3;vS=5;y=4;speed=0.3} @self',
                           'message{m="&5&l«¡Falla de gravedad! Que el vacio los trague.»"} @PlayersInRadius{r=64}'],
        'NAVE_CAP_CRIAS': ['sound{s=entity.endermite.ambient;v=2;p=0.5} @self',
                           f'summon{{type={CRIA_MOB};amount=4;radius=6}} @self'],
        'NAVE_CAP_PULSO': ['state{s=pulso} @self', 'sound{s=block.beacon.power_select;v=2;p=0.5} @PlayersInRadius{r=40}',
                           'potion{type=LEVITATION;duration=24;level=1;hasParticles=false} @PlayersInRadius{r=30}', 'delay 22',
                           fx('golpe', '#c43bff', 10, 'vacio'), 'sound{s=entity.generic.explode;v=2;p=0.6} @self',
                           f'damage{{a={DANO_PULSO}}} @PlayersInRadius{{r=10}}', 'throw{velocity=10;velocityY=2} @PlayersInRadius{r=10}'],
        'NAVE_CAP_ZONAS': [f'summon{{type={ZONA_MOB};amount=1;radius=0}} @target'],
        'NAVE_OJO_RAYO': ['state{s=attack} @self', 'sound{s=entity.guardian.attack;v=1.5;p=1.4} @self', 'delay 6',
                          'projectile{onTick=NAVE_OJO_TICK;onHit=NAVE_OJO_HIT;v=20;i=1;hR=0.8;vR=0.8;mr=36;hnp=true}'],
        'NAVE_OJO_TICK': ['particles{p=dust;color=#1fd38a;size=1.4;amount=3;hS=0.05;vS=0.05} @origin'],
        'NAVE_OJO_HIT': [f'damage{{a={DANO_RAYO_OJO}}}', 'particles{p=happy_villager;amount=10;hS=0.4;vS=0.4} @origin'],
        'NAVE_OJO_MUERE': ['state{s=death} @self', fx('estallido', '#1fd38a', 3, 'arcano'),
                           'sound{s=entity.elder_guardian.death;v=1.5;p=1.2} @self',
                           'message{m="&aUn Ojo Vigia se apaga."} @PlayersInRadius{r=48}'],
        'NAVE_TIM_SALTO': ['sound{s=entity.enderman.teleport;v=2;p=0.7} @self', 'teleport @Forward{f=-3;y=0}',
                           'delay 6', f'damage{{a=18}} @PlayersInRadius{{r=4}}', 'particles{p=portal;amount=60;hS=1;vS=2;y=1.5} @self'],
        'NAVE_CAP_RESET': ['heal{a=2000000000} @self', 'removetag{tag=nave.f2} @self', 'removetag{tag=nave.f3} @self',
                           'potionclear @self', 'teleport @SpawnLocation'],
        'NAVE_CAP_MUERE': ['state{s=death} @self', fx('golpe', '#f0a0ff', 10, 'vacio'),
                           'sound{s=ui.toast.challenge_complete;v=2;p=0.8} @PlayersInRadius{r=64}',
                           'particles{p=reverse_portal;amount=400;hS=3;vS=6;y=4;speed=0.3} @self'],
    }
    out = ['# Generado por datapack-src/mobs/capitan_vacio.py: Capitan del Vacio (Nave del Vacio).', '']
    for name, skills in S.items():
        out += [f'{name}:']
        if name in ('NAVE_CAP_CUBO',):
            out += ['  Cooldown: 4']
        if name in ('NAVE_CAP_SALTO', 'NAVE_CAP_PULSO', 'NAVE_CAP_BARRIDO'):
            out += ['  Cooldown: 8']
        out += ['  Skills:', *['  - ' + q(s.strip()) for s in skills], '']
    return '\n'.join(out)


def export(preview=True):
    from bbmodel import save
    from build_models import preview3d
    from PIL import Image
    out = HERE.parent.parent / 'build' / 'models'
    out.mkdir(parents=True, exist_ok=True)
    hojas = []
    for m in (build(), build_ojo()):
        img = save(m, out / f'{m.name}.bbmodel')
        print('Modelo:', out / f'{m.name}.bbmodel', len(m.cubes), 'cubos')
        if preview:
            hojas += [preview3d(m, img, yaw, 15, 3 if m.name == MODEL_ID else 8) for yaw in (20, 160, 90)]
    if preview:
        sheet = Image.new('RGBA', (sum(v.width for v in hojas) + 60, max(v.height for v in hojas)), (40, 40, 48, 255))
        x = 0
        for v in hojas:
            sheet.paste(v, (x, 0)); x += v.width + 10
        dest = HERE.parent.parent / 'build' / 'previews' / 'capitan_vacio.png'
        dest.parent.mkdir(parents=True, exist_ok=True)
        sheet.save(dest)
        print('Vista previa:', dest)


if __name__ == '__main__':
    export()
