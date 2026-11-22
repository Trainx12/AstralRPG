# -*- coding: utf-8 -*-
"""Capitan del Vacio: jefe de la Nave del Vacio (nave.py), diseno propio del 22/11/2026.

Figura de obsidiana viva que flota (de la cintura para abajo se deshace en jirones), cabeza con tres ojos y corona
de fuego magenta, nucleo de cristal en el pecho con grietas, cuatro brazos (dos con garras arriba, dos abajo con
cubos de vacio) y alas de fragmentos. Lo acompanan los Ojos Vigias (cubos con un ojo) que lo protegen.

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
ALTO = 11.7               # bloques de alto en juego
ESCALA = 6.0              # escala de la entidad (ZOMBIE 1,95 x 6 = 11,7 de caja para pegarle)
VIDA_FACTOR = 1.5         # x el jefe de la Forja (13.125.000): 19.687.500, como el Santuario (x1,5)
OJOS = 3
OJO_VIDA = 0.03           # cada Ojo Vigia: 3% de la vida del Capitan (590.625)
ESCUDO = 0.2              # con Ojos vivos recibe solo el 20% del dano
DANO_ZARPAZO = 30         # golpe cuerpo a cuerpo (antes del x tier de astral_gameplay.sk, como Trainx)
DANO_CUBO = 14            # cubo de vacio (proyectil)
DANO_ZONA = 5             # cada medio segundo dentro de una zona de vacio
DANO_RAYO_OJO = 8         # rayo de cada Ojo Vigia
DANO_PULSO = 18           # pulso de gravedad (fase 3)
VELOCIDAD = 0.27
TIMONEL_EZ = 12           # minijefe: 12 zombis T5 de vida (x1,5 de la mazmorra)
# ==========================================================================================

NEGRO, NEGRO2, VIOLETA, MAGENTA, ROSA, BLANCO = '#17101f', '#21162c', '#5a1694', '#c43bff', '#f0a0ff', '#fff4ff'
VERDE, VERDE_OSC, TEAL = '#1fd38a', '#06140f', '#123b33'


def _grietas(w, h, seed):
    """Grietas magenta en una cara de w x h pixeles."""
    import random
    r = random.Random(seed)
    out, x = [], r.randint(1, max(1, w - 2))
    for y in range(0, h, 2):
        x = max(0, min(w - 1, x + r.choice((-1, 0, 1))))
        out.append((x, y, 1, 2, MAGENTA))
        if r.random() < .25:
            out.append((max(0, x - 1), y, 1, 1, ROSA))
    return out


def build():
    m = Model(MODEL_ID)
    m.bone('root', (0, 0, 0))
    m.bone('jirones', (0, 34, 0), 'root')
    m.bone('body', (0, 34, 0), 'root')
    m.bone('head', (0, 70, 0), 'body')
    m.bone('corona', (0, 88, 0), 'head')
    m.bone('arm_ur', (-20, 68, 0), 'body')
    m.bone('arm_ul', (20, 68, 0), 'body')
    m.bone('arm_lr', (-15, 56, 0), 'body')
    m.bone('arm_ll', (15, 56, 0), 'body')
    m.bone('cubo_r', (-15, 36, -3), 'arm_lr')
    m.bone('cubo_l', (15, 36, -3), 'arm_ll')
    m.bone('ala_r', (-8, 62, 8), 'body')
    m.bone('ala_l', (8, 62, 8), 'body')
    m.bone('nucleo', (0, 51, -8), 'body')
    m.bone('mtag_nombre', (0, 108, 0), 'root')

    # Jirones: la parte de abajo se deshace (cada vez mas finos y violetas).
    for (w, y0, y1, d, col) in ((22, 26, 36, 14, NEGRO), (16, 17, 26, 11, NEGRO2), (10, 9, 17, 8, VIOLETA), (5, 2, 9, 5, MAGENTA)):
        m.cube('jirones', (-w / 2, y0, -d / 2), (w / 2, y1, d / 2), col, pat='stone',
               decals={'north': _grietas(w, y1 - y0, f'j{y0}'), 'south': _grietas(w, y1 - y0, f'js{y0}')})
    for sx in (-1, 1):   # tiras sueltas a los costados
        m.cube('jirones', (sx * 9 - 2, 12, -2), (sx * 9 + 2, 26, 2), NEGRO2, decals={'north': [(1, 2, 1, 8, VIOLETA)]})
        m.cube('jirones', (sx * 6 - 1.5, 4, 3), (sx * 6 + 1.5, 14, 6), VIOLETA)

    # Torso: pelvis, pecho ancho con grietas y el nucleo de cristal.
    m.rcube('body', (-11, 34, -7), (11, 42, 7), NEGRO, pat='stone')
    pecho = _grietas(28, 26, 'pecho') + _grietas(28, 26, 'pecho2') + [(12, 0, 4, 26, MAGENTA), (13, 0, 2, 26, ROSA)]
    m.rcube('body', (-14, 42, -8), (14, 68, 8), NEGRO, pat='stone',
            decals={'north': pecho, 'south': _grietas(28, 26, 'espalda'), 'east': _grietas(16, 26, 'ce'), 'west': _grietas(16, 26, 'cw')})
    m.cube('nucleo', (-5, 46, -9.5), (5, 56, -7.5), ROSA, decals={'north': [(2, 2, 6, 6, BLANCO), (3, 3, 4, 4, '#ffffff')]})
    m.cube('nucleo', (-7, 48, -9), (7, 54, -8), MAGENTA)
    m.cube('nucleo', (-3, 44, -9), (3, 58, -8), MAGENTA)
    # Hombreras con puntas.
    for sx in (-1, 1):
        x0, x1 = sorted((sx * 12, sx * 26))
        m.rcube('body', (x0, 60, -8), (x1, 71, 8), NEGRO2, pat='stone', decals={'up': [(2, 4, 10, 2, VIOLETA)]})
        px0, px1 = sorted((sx * 20, sx * 25))
        m.cube('body', (px0, 71, -2), (px1, 80, 3), NEGRO, decals={'north': [(1, 0, 3, 3, MAGENTA)]})
        m.cube('body', (px0 + 1, 80, -1), (px1 - 1, 84, 2), MAGENTA)

    # Cabeza: tres ojos (uno vertical en la frente) y boca con colmillos de luz.
    ojos = [(2, 7, 5, 3, MAGENTA), (11, 7, 5, 3, MAGENTA), (3, 8, 2, 1, BLANCO), (13, 8, 2, 1, BLANCO),
            (8, 1, 2, 5, MAGENTA), (8, 2, 2, 2, BLANCO),
            (4, 13, 10, 2, '#0a0410'), (5, 13, 1, 1, MAGENTA), (8, 13, 1, 1, MAGENTA), (11, 13, 1, 1, MAGENTA)]
    m.rcube('head', (-9, 70, -9), (9, 88, 9), NEGRO, pat='stone', decals={'north': ojos, 'east': _grietas(18, 18, 'he'), 'west': _grietas(18, 18, 'hw')})
    for sx in (-1, 1):   # cuernos
        x0, x1 = sorted((sx * 8, sx * 12))
        m.cube('head', (x0, 84, -2), (x1, 90, 2), NEGRO2)
        x0, x1 = sorted((sx * 11, sx * 14))
        m.cube('head', (x0, 89, -1.5), (x1, 96, 1.5), NEGRO2, decals={'north': [(0, 0, 3, 2, MAGENTA)]})
    # Corona de fuego magenta.
    for (x, h, col) in ((-7, 7, MAGENTA), (-3.5, 11, MAGENTA), (0, 15, ROSA), (3.5, 10, MAGENTA), (7, 6, MAGENTA)):
        m.cube('corona', (x - 1.75, 88, -3), (x + 1.75, 88 + h, 3), col, decals={'north': [(1, int(h * .4), 1, int(h * .6), ROSA)]})
    m.cube('corona', (-8.5, 88, -4), (8.5, 90, 4), VIOLETA)

    # Brazos de arriba: largos, con garras de tres dedos.
    for bone, sx in (('arm_ur', -1), ('arm_ul', 1)):
        x = sx * 20
        m.rcube(bone, (x - 4, 48, -4), (x + 4, 70, 4), NEGRO2, pat='stone', decals={'north': _grietas(8, 22, bone)})
        m.rcube(bone, (x - 3.5, 30, -3.5), (x + 3.5, 49, 3.5), NEGRO, pat='stone', decals={'north': [(3, 2, 1, 14, MAGENTA)]})
        m.cube(bone, (x - 4.5, 26, -4.5), (x + 4.5, 31, 4.5), NEGRO2)
        for dx in (-3, 0, 3):
            m.cube(bone, (x + dx - 1, 14, -4.5), (x + dx + 1, 26, -2.5), NEGRO, decals={'north': [(0, 9, 2, 3, MAGENTA)]})
        m.cube(bone, (x - sx * 4.5 - 1, 18, -1), (x - sx * 4.5 + 1, 27, 1), NEGRO)   # pulgar
    # Brazos de abajo: mas cortos, cada mano sostiene un cubo de vacio.
    for bone, cubo, sx in (('arm_lr', 'cubo_r', -1), ('arm_ll', 'cubo_l', 1)):
        x = sx * 15
        m.rcube(bone, (x - 3, 40, -3), (x + 3, 58, 3), NEGRO2, pat='stone')
        m.cube(bone, (x - 3.5, 36, -3.5), (x + 3.5, 41, 3.5), NEGRO)
        m.cube(cubo, (x - 5, 26, -8), (x + 5, 36, 2), '#0a0410',
               decals={f: [(1, 1, 8, 8, VIOLETA), (3, 3, 4, 4, MAGENTA), (4, 4, 2, 2, BLANCO)] for f in ('north', 'south', 'east', 'west', 'up', 'down')})

    # Alas de fragmentos: escalones de placas finas que se abren hacia afuera y arriba.
    for bone, sx in (('ala_r', -1), ('ala_l', 1)):
        for i, (dx, y0, y1, w) in enumerate(((8, 52, 74, 10), (17, 60, 86, 10), (26, 66, 96, 9), (34, 70, 100, 7), (40, 76, 98, 5))):
            x0, x1 = sorted((sx * dx, sx * (dx + w)))
            m.cube(bone, (x0, y0, 9 + i), (x1, y1, 11 + i), NEGRO2 if i % 2 else NEGRO,
                   decals={'south': [(1, 2, 1, y1 - y0 - 4, MAGENTA)], 'north': [(w // 2, 3, 1, y1 - y0 - 8, VIOLETA)]})
        for (dx, y0, y1) in ((14, 44, 54), (25, 52, 62), (36, 62, 70)):   # puntas que cuelgan
            x0, x1 = sorted((sx * dx, sx * (dx + 4)))
            m.cube(bone, (x0, y0, 11), (x1, y1, 13), MAGENTA)

    animations(m)
    return m


def animations(m):
    from animaciones import kf
    w = 'math.sin(q.anim_time * 360 * {s} + {p}) * {a}'
    UR, UL, LR, LL = (-30, 0, 18), (-30, 0, -18), (24, 0, 6), (24, 0, -6)      # brazos de arriba levantados con garras
    m.anim('idle', 4.0, {
        'root': {'position': (0, f'3 + {w.format(s=0.5, p=0, a=2)}', 0)},
        'jirones': {'rotation': (w.format(s=0.5, p=90, a=6), w.format(s=0.25, p=0, a=10), w.format(s=0.5, p=0, a=4))},
        'body': {'rotation': (w.format(s=0.25, p=0, a=2), w.format(s=0.25, p=90, a=3), 0)},
        'head': {'rotation': (w.format(s=0.5, p=90, a=3), w.format(s=0.25, p=0, a=10), 0)},
        'corona': {'position': (0, w.format(s=2, p=0, a=0.8), 0)},
        'arm_ur': {'rotation': (f'{UR[0]} + {w.format(s=0.5, p=0, a=6)}', 0, f'{UR[2]} + {w.format(s=0.5, p=90, a=4)}')},
        'arm_ul': {'rotation': (f'{UL[0]} + {w.format(s=0.5, p=180, a=6)}', 0, f'{UL[2]} + {w.format(s=0.5, p=270, a=4)}')},
        'arm_lr': {'rotation': (f'{LR[0]} + {w.format(s=0.5, p=90, a=4)}', 0, LR[2])},
        'arm_ll': {'rotation': (f'{LL[0]} + {w.format(s=0.5, p=270, a=4)}', 0, LL[2])},
        'cubo_r': {'rotation': (0, 'q.anim_time * 90', 0)}, 'cubo_l': {'rotation': (0, 'q.anim_time * -90', 0)},
        'ala_r': {'rotation': (0, f'-10 + {w.format(s=0.5, p=0, a=6)}', 0)},
        'ala_l': {'rotation': (0, f'10 + {w.format(s=0.5, p=180, a=6)}', 0)},
        'nucleo': {'position': (0, 0, w.format(s=1, p=0, a=0.4))},
    })
    m.anim('walk', 2.0, {
        'root': {'position': (0, f'3 + {w.format(s=0.5, p=0, a=2)}', 0)},
        'jirones': {'rotation': (f'22 + {w.format(s=1, p=0, a=6)}', 0, w.format(s=0.5, p=0, a=6))},
        'body': {'rotation': (-8, w.format(s=0.5, p=0, a=4), 0)},
        'arm_ur': {'rotation': (f'{UR[0] - 10} + {w.format(s=0.5, p=0, a=8)}', 0, UR[2])},
        'arm_ul': {'rotation': (f'{UL[0] - 10} + {w.format(s=0.5, p=180, a=8)}', 0, UL[2])},
        'arm_lr': {'rotation': (LR[0], 0, LR[2])}, 'arm_ll': {'rotation': (LL[0], 0, LL[2])},
        'cubo_r': {'rotation': (0, 'q.anim_time * 90', 0)}, 'cubo_l': {'rotation': (0, 'q.anim_time * -90', 0)},
        'ala_r': {'rotation': (0, f'-18 + {w.format(s=1, p=0, a=8)}', 0)},
        'ala_l': {'rotation': (0, f'18 + {w.format(s=1, p=180, a=8)}', 0)},
    })
    # Zarpazo (~onAttack): levanta las dos garras y las cruza hacia abajo (dano a los 0,4 s).
    m.anim('attack', 0.9, {
        'arm_ur': {'rotation': kf((0, *UR), (.25, -150, 0, 30), (.4, 30, 0, -10), (.55, 20, 0, -6), (.9, *UR))},
        'arm_ul': {'rotation': kf((0, *UL), (.25, -150, 0, -30), (.4, 30, 0, 10), (.55, 20, 0, 6), (.9, *UL))},
        'body': {'rotation': kf((0, 0, 0, 0), (.25, 12, 0, 0), (.4, -20, 0, 0), (.9, 0, 0, 0)),
                 'position': kf((0, 0, 0, 0), (.25, 0, 2, 2), (.4, 0, -2, -4), (.9, 0, 0, 0))},
        'head': {'rotation': kf((0, 0, 0, 0), (.25, -14, 0, 0), (.4, 16, 0, 0), (.9, 0, 0, 0))},
    }, loop='once')
    # Cubo de vacio: echa un brazo de abajo atras y lo lanza (sale a los 0,45 s).
    m.anim('throw', 0.8, {
        'arm_lr': {'rotation': kf((0, *LR), (.3, -70, 0, 20), (.45, 80, 0, 0), (.8, *LR))},
        'arm_ll': {'rotation': kf((0, *LL), (.3, -70, 0, -20), (.45, 80, 0, 0), (.8, *LL))},
        'body': {'rotation': kf((0, 0, 0, 0), (.3, 8, 0, 0), (.45, -12, 0, 0), (.8, 0, 0, 0))},
        'cubo_r': {'position': kf((0, 0, 0, 0), (.44, 0, 0, 0), (.46, 0, -200, 0), (.79, 0, -200, 0), (.8, 0, 0, 0))},
        'cubo_l': {'position': kf((0, 0, 0, 0), (.44, 0, 0, 0), (.46, 0, -200, 0), (.79, 0, -200, 0), (.8, 0, 0, 0))},
    }, loop='once')
    # Salto del vacio: se encoge en el nucleo y desaparece (la skill lo lleva detras del jugador a los 0,5 s).
    m.anim('salto', 1.0, {
        'root': {'scale': kf((0, 1, 1, 1), (.45, .15, 1.4, .15), (.5, .05, .05, .05), (.6, .05, .05, .05), (.8, 1.15, 1.15, 1.15), (1.0, 1, 1, 1))},
    }, loop='once')
    # Furia (fases): abre las alas y los cuatro brazos y grita.
    m.anim('furia', 1.6, {
        'body': {'rotation': kf((0, 0, 0, 0), (.4, -16, 0, 0), (.8, 14, 0, 0), (1.3, 12, 0, 0), (1.6, 0, 0, 0))},
        'head': {'rotation': kf((0, 0, 0, 0), (.4, 20, 0, 0), (.8, -34, 0, 0), (1.3, -30, 0, 0), (1.6, 0, 0, 0))},
        'arm_ur': {'rotation': kf((0, *UR), (.8, -160, 0, 60), (1.3, -158, 0, 58), (1.6, *UR))},
        'arm_ul': {'rotation': kf((0, *UL), (.8, -160, 0, -60), (1.3, -158, 0, -58), (1.6, *UL))},
        'arm_lr': {'rotation': kf((0, *LR), (.8, 20, 0, 70), (1.3, 20, 0, 66), (1.6, *LR))},
        'arm_ll': {'rotation': kf((0, *LL), (.8, 20, 0, -70), (1.3, 20, 0, -66), (1.6, *LL))},
        'ala_r': {'rotation': kf((0, 0, -10, 0), (.8, 0, -55, -15), (1.3, 0, -52, -14), (1.6, 0, -10, 0))},
        'ala_l': {'rotation': kf((0, 0, 10, 0), (.8, 0, 55, 15), (1.3, 0, 52, 14), (1.6, 0, 10, 0))},
        'nucleo': {'scale': kf((0, 1, 1, 1), (.8, 1.6, 1.6, 1.6), (1.3, 1.5, 1.5, 1.5), (1.6, 1, 1, 1))},
    }, loop='once')
    # Pulso de gravedad: se eleva con los brazos abiertos y baja de golpe (dano a los 1,1 s).
    m.anim('pulso', 1.4, {
        'root': {'position': kf((0, 0, 3, 0), (.6, 0, 22, 0), (.95, 0, 24, 0), (1.1, 0, 0, 0), (1.4, 0, 3, 0))},
        'arm_ur': {'rotation': kf((0, *UR), (.6, -175, 0, 20), (1.1, 40, 0, 10), (1.4, *UR))},
        'arm_ul': {'rotation': kf((0, *UL), (.6, -175, 0, -20), (1.1, 40, 0, -10), (1.4, *UL))},
        'jirones': {'rotation': kf((0, 0, 0, 0), (.6, 30, 0, 0), (1.1, -10, 0, 0), (1.4, 0, 0, 0))},
    }, loop='once')
    # Aparece: sale del suelo desde el nucleo.
    m.anim('aparece', 2.0, {
        'root': {'position': kf((0, 0, -100, 0), (1.2, 0, 0, 0), (1.5, 0, 6, 0), (2.0, 0, 3, 0))},
        'head': {'rotation': kf((0, 30, 0, 0), (1.2, 30, 0, 0), (1.5, -30, 0, 0), (2.0, 0, 0, 0))},
        'arm_ur': {'rotation': kf((0, 0, 0, 0), (1.2, 0, 0, 0), (1.5, -170, 0, 40), (2.0, *UR))},
        'arm_ul': {'rotation': kf((0, 0, 0, 0), (1.2, 0, 0, 0), (1.5, -170, 0, -40), (2.0, *UL))},
    }, loop='once')
    # Muerte: el nucleo se apaga, se desarma hacia abajo y queda flotando quieto.
    m.anim('death', 2.2, {
        'root': {'position': kf((0, 0, 3, 0), (.5, 0, 8, 0), (1.4, 0, -10, 0), (2.2, 0, -40, 0))},
        'body': {'rotation': kf((0, 0, 0, 0), (.5, -20, 0, 0), (1.4, 30, 10, 0), (2.2, 70, 20, 0))},
        'head': {'rotation': kf((0, 0, 0, 0), (.5, -40, 0, 0), (1.4, 30, 0, 0), (2.2, 40, 0, 0))},
        'arm_ur': {'rotation': kf((0, *UR), (.5, -170, 0, 50), (1.4, 10, 0, 30), (2.2, 20, 0, 40))},
        'arm_ul': {'rotation': kf((0, *UL), (.5, -170, 0, -50), (1.4, 10, 0, -30), (2.2, 20, 0, -40))},
        'nucleo': {'scale': kf((0, 1, 1, 1), (.5, 1.8, 1.8, 1.8), (1.4, .4, .4, .4), (2.2, .1, .1, .1))},
    }, loop='hold')


def build_ojo():
    """Ojo Vigia: cubo verde azulado con un ojo en cada cara y cuatro aletas."""
    m = Model(OJO_ID)
    m.bone('root', (0, 0, 0))
    m.bone('body', (0, 10, 0), 'root')
    m.bone('mtag_nombre', (0, 22, 0), 'root')
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
    from tamanos import bounds_data
    return bounds_data(build().export()[0])[1][1] / 16


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
        "  - 'command{c=\"attribute <caster.uuid> minecraft:scale base set 2.5\"} @self ~onSpawn'",
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
                          'bulletType=ITEM;material=CRYING_OBSIDIAN;hnp=true;sy=6}'],
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
        if name in ('NAVE_CAP_SALTO', 'NAVE_CAP_PULSO'):
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
