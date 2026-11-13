"""Animaciones con fotogramas clave (pedido del dueno 13/11/2026: jefes y esqueletos menos rigidos).

Convencion de los modelos (ver creatures_tanda3b): el frente es -Z.
- Brazo o pierna colgando: rotacion X POSITIVA lo lleva hacia delante/arriba.
- Cuerpo: rotacion X NEGATIVA lo inclina hacia delante; POSITIVA hacia atras (en cuadrupedos, se para de manos).
Cada canal es una lista [(segundo, (x, y, z)), ...] que bbmodel exporta como fotogramas catmullrom.

Ataques de los jefes (los usan las skills de mobs/jefes_combate.py, sincronizadas con estos tiempos):
- attack: anticipacion -> golpe -> recuperacion (0.9 s).
- slam:   golpe al piso con los dos brazos; el impacto cae en SLAM_IMPACTO segundos.
- throw:  lanzamiento para el ataque de lejos (0.7 s).
"""
import functools

SLAM_LARGO = 1.2
SLAM_IMPACTO = 0.75     # segundos: las skills esperan 15 ticks antes del dano
THROW_LARGO = 0.7


def kf(*pts):
    """kf((t, x, y, z), ...) -> lista de fotogramas."""
    return [(round(t, 3), (x, y, z)) for t, x, y, z in pts]


def wave(amp, speed=1.0, phase=0):
    return f"math.sin(q.anim_time * 360 * {round(speed, 4)} + {phase}) * {amp}"


def bob(amp, speed=1.0):
    """Rebote hacia arriba dos veces por ciclo (un rebote por paso)."""
    return f"(1 - math.cos(q.anim_time * 720 * {round(speed, 4)})) * {amp / 2}"


# ------------------------------------------------------------------ jefes
def biped_boss(base_arm=0, arm_l='arm_l', arm_r='arm_r'):
    b = base_arm
    attack = {
        arm_r: {'rotation': kf((0, b, 0, 0), (.3, 150, 0, -8), (.38, 165, 0, -10), (.5, 35, 0, 6), (.62, 30, 0, 4), (.9, b, 0, 0))},
        arm_l: {'rotation': kf((0, b, 0, 0), (.34, 140, 0, 8), (.42, 155, 0, 10), (.54, 40, 0, -6), (.66, 30, 0, -4), (.9, b, 0, 0))},
        'body': {'rotation': kf((0, 0, 0, 0), (.35, 10, 12, 0), (.5, -18, -10, 0), (.65, -12, -6, 0), (.9, 0, 0, 0)),
                 'position': kf((0, 0, 0, 0), (.35, 0, .6, 0), (.5, 0, -1, -1), (.65, 0, -.8, -.6), (.9, 0, 0, 0))},
        'head': {'rotation': kf((0, 0, 0, 0), (.35, -6, -6, 0), (.5, 12, 4, 0), (.9, 0, 0, 0))},
        'leg_l': {'rotation': kf((0, 0, 0, 0), (.35, -6, 0, 0), (.5, 14, 0, 0), (.9, 0, 0, 0))},
        'leg_r': {'rotation': kf((0, 0, 0, 0), (.35, 4, 0, 0), (.5, 10, 0, 0), (.9, 0, 0, 0))},
    }
    i = SLAM_IMPACTO
    slam = {
        arm_r: {'rotation': kf((0, b, 0, 0), (.45, 170, 0, -6), (.6, 178, 0, -8), (i, 45, 0, 4), (.95, 40, 0, 4), (SLAM_LARGO, b, 0, 0))},
        arm_l: {'rotation': kf((0, b, 0, 0), (.45, 170, 0, 6), (.6, 178, 0, 8), (i, 45, 0, -4), (.95, 40, 0, -4), (SLAM_LARGO, b, 0, 0))},
        'body': {'rotation': kf((0, 0, 0, 0), (.45, 12, 0, 0), (.6, 14, 0, 0), (i, -30, 0, 0), (.95, -26, 0, 0), (SLAM_LARGO, 0, 0, 0)),
                 'position': kf((0, 0, 0, 0), (.45, 0, 1, 0), (.6, 0, 1.2, 0), (i, 0, -3, -1), (.95, 0, -2.6, -.8), (SLAM_LARGO, 0, 0, 0))},
        'head': {'rotation': kf((0, 0, 0, 0), (.45, -10, 0, 0), (i, 20, 0, 0), (.95, 16, 0, 0), (SLAM_LARGO, 0, 0, 0))},
        'leg_l': {'rotation': kf((0, 0, 0, 0), (.45, -12, 0, -4), (i, 30, 0, -8), (.95, 26, 0, -8), (SLAM_LARGO, 0, 0, 0))},
        'leg_r': {'rotation': kf((0, 0, 0, 0), (.45, -12, 0, 4), (i, 30, 0, 8), (.95, 26, 0, 8), (SLAM_LARGO, 0, 0, 0))},
    }
    t = THROW_LARGO
    throw = {
        arm_r: {'rotation': kf((0, b, 0, 0), (.3, 195, 0, -14), (.42, 70, 0, 4), (.52, 55, 0, 4), (t, b, 0, 0))},
        arm_l: {'rotation': kf((0, b, 0, 0), (.3, 40, 0, 20), (.42, -10, 0, 6), (t, b, 0, 0))},
        'body': {'rotation': kf((0, 0, 0, 0), (.3, 8, 18, 0), (.42, -12, -16, 0), (t, 0, 0, 0))},
        'head': {'rotation': kf((0, 0, 0, 0), (.3, -4, -12, 0), (.42, 6, 10, 0), (t, 0, 0, 0))},
    }
    return attack, slam, throw


def quad_boss():
    """Golem de la Forja: se para de manos y aplasta con las patas delanteras."""
    attack = {
        'body': {'rotation': kf((0, 0, 0, 0), (.3, 12, 0, 0), (.45, -10, 0, 0), (.6, -6, 0, 0), (.9, 0, 0, 0)),
                 'position': kf((0, 0, 0, 0), (.3, 0, .8, .6), (.45, 0, -.6, -1.2), (.9, 0, 0, 0))},
        'head': {'rotation': kf((0, 0, 0, 0), (.3, 10, 0, 0), (.45, -22, 0, 0), (.6, -16, 0, 0), (.9, 0, 0, 0))},
        'leg_fl': {'rotation': kf((0, 0, 0, 0), (.3, 35, 0, 0), (.45, -12, 0, 0), (.9, 0, 0, 0))},
        'leg_fr': {'rotation': kf((0, 0, 0, 0), (.33, 30, 0, 0), (.48, -12, 0, 0), (.9, 0, 0, 0))},
        'leg_bl': {'rotation': kf((0, 0, 0, 0), (.3, -12, 0, 0), (.45, 6, 0, 0), (.9, 0, 0, 0))},
        'leg_br': {'rotation': kf((0, 0, 0, 0), (.3, -12, 0, 0), (.45, 6, 0, 0), (.9, 0, 0, 0))},
    }
    i = SLAM_IMPACTO
    slam = {
        'body': {'rotation': kf((0, 0, 0, 0), (.45, 26, 0, 0), (.6, 30, 0, 0), (i, -10, 0, 0), (.95, -6, 0, 0), (SLAM_LARGO, 0, 0, 0)),
                 'position': kf((0, 0, 0, 0), (.45, 0, 2.5, 1), (.6, 0, 3, 1), (i, 0, -1.6, -1), (.95, 0, -1.2, -.8), (SLAM_LARGO, 0, 0, 0))},
        'head': {'rotation': kf((0, 0, 0, 0), (.45, -14, 0, 0), (i, -20, 0, 0), (SLAM_LARGO, 0, 0, 0))},
        'leg_fl': {'rotation': kf((0, 0, 0, 0), (.45, 55, 0, 0), (.6, 60, 0, 0), (i, -14, 0, 0), (SLAM_LARGO, 0, 0, 0))},
        'leg_fr': {'rotation': kf((0, 0, 0, 0), (.45, 55, 0, 0), (.6, 60, 0, 0), (i, -14, 0, 0), (SLAM_LARGO, 0, 0, 0))},
        'leg_bl': {'rotation': kf((0, 0, 0, 0), (.45, -24, 0, 0), (i, 10, 0, 0), (SLAM_LARGO, 0, 0, 0))},
        'leg_br': {'rotation': kf((0, 0, 0, 0), (.45, -24, 0, 0), (i, 10, 0, 0), (SLAM_LARGO, 0, 0, 0))},
    }
    t = THROW_LARGO
    throw = {
        'body': {'rotation': kf((0, 0, 0, 0), (.3, 10, 0, 0), (.42, -8, 0, 0), (t, 0, 0, 0))},
        'head': {'rotation': kf((0, 0, 0, 0), (.3, 18, 0, 0), (.42, -14, 0, 0), (t, 0, 0, 0))},
    }
    return attack, slam, throw


def crab_boss():
    """Cangrejo: pinzas que suben y cierran; en el slam golpea el piso con las dos."""
    attack = {
        'claw_r': {'rotation': kf((0, 0, 0, 0), (.22, 42, -10, 0), (.36, -16, 8, 0), (.6, 0, 0, 0))},
        'claw_l': {'rotation': kf((0, 0, 0, 0), (.3, 42, 10, 0), (.44, -16, -8, 0), (.68, 0, 0, 0))},
        'body': {'rotation': kf((0, 0, 0, 0), (.25, 6, 8, 0), (.4, -6, -8, 0), (.68, 0, 0, 0)),
                 'position': kf((0, 0, 0, 0), (.25, 0, .5, 0), (.4, 0, -.5, -.6), (.68, 0, 0, 0))},
    }
    i = SLAM_IMPACTO
    slam = {
        'claw_r': {'rotation': kf((0, 0, 0, 0), (.45, 65, 0, -10), (.6, 70, 0, -12), (i, -28, 0, 0), (SLAM_LARGO, 0, 0, 0))},
        'claw_l': {'rotation': kf((0, 0, 0, 0), (.45, 65, 0, 10), (.6, 70, 0, 12), (i, -28, 0, 0), (SLAM_LARGO, 0, 0, 0))},
        'body': {'rotation': kf((0, 0, 0, 0), (.45, 12, 0, 0), (i, -10, 0, 0), (SLAM_LARGO, 0, 0, 0)),
                 'position': kf((0, 0, 0, 0), (.45, 0, 1.5, 0), (i, 0, -1, 0), (.95, 0, -.8, 0), (SLAM_LARGO, 0, 0, 0))},
    }
    t = THROW_LARGO
    throw = {
        'claw_r': {'rotation': kf((0, 0, 0, 0), (.3, 50, -20, 0), (.42, 10, 10, 0), (t, 0, 0, 0))},
        'body': {'rotation': kf((0, 0, 0, 0), (.3, 8, 10, 0), (.42, -4, -6, 0), (t, 0, 0, 0))},
    }
    return attack, slam, throw


def chaman_boss():
    """Chaman: el baston esta en arm_r. Golpea con el baston, lo levanta y apunta para el hechizo,
    y lo clava en el piso en el slam."""
    attack = {
        'arm_r': {'rotation': kf((0, 0, 0, 0), (.32, 165, 0, -12), (.4, 175, 0, -14), (.52, 55, 0, 8), (.62, 45, 0, 6), (.9, 0, 0, 0))},
        'arm_l': {'rotation': kf((0, 0, 0, 0), (.32, 40, 0, 18), (.52, -10, 0, 8), (.9, 0, 0, 0))},
        'body': {'rotation': kf((0, 0, 0, 0), (.32, 8, 12, 0), (.52, -16, -14, 0), (.65, -10, -8, 0), (.9, 0, 0, 0)),
                 'position': kf((0, 0, 0, 0), (.32, 0, .4, 0), (.52, 0, -.8, -.8), (.9, 0, 0, 0))},
        'head': {'rotation': kf((0, 0, 0, 0), (.32, -8, -8, 0), (.52, 12, 6, 0), (.9, 0, 0, 0))},
        'leg_l': {'rotation': kf((0, 0, 0, 0), (.32, -6, 0, 0), (.52, 14, 0, 0), (.9, 0, 0, 0))},
        'leg_r': {'rotation': kf((0, 0, 0, 0), (.32, 4, 0, 0), (.52, -8, 0, 0), (.9, 0, 0, 0))},
    }
    t = THROW_LARGO
    throw = {   # baston en alto girando un poco, despues apunta al jugador y la mano libre empuja el hechizo
        'arm_r': {'rotation': kf((0, 0, 0, 0), (.18, 140, 15, -8), (.3, 160, -15, -10), (.42, 88, 0, 4), (.56, 82, 0, 4), (t, 0, 0, 0))},
        'arm_l': {'rotation': kf((0, 0, 0, 0), (.3, 30, 0, 25), (.42, 80, 0, 4), (.56, 75, 0, 4), (t, 0, 0, 0))},
        'body': {'rotation': kf((0, 0, 0, 0), (.3, 8, 6, 0), (.42, -8, -4, 0), (t, 0, 0, 0)),
                 'position': kf((0, 0, 0, 0), (.3, 0, .5, 0), (.42, 0, 0, -.4), (t, 0, 0, 0))},
        'head': {'rotation': kf((0, 0, 0, 0), (.3, -12, 0, 0), (.42, 4, 0, 0), (t, 0, 0, 0))},
    }
    i = SLAM_IMPACTO
    slam = {    # baston con las dos manos, bien arriba, y lo clava en el piso delante
        'arm_r': {'rotation': kf((0, 0, 0, 0), (.45, 170, 0, 10), (.6, 178, 0, 12), (i, 30, 0, 14), (.95, 26, 0, 14), (SLAM_LARGO, 0, 0, 0))},
        'arm_l': {'rotation': kf((0, 0, 0, 0), (.45, 165, 0, -12), (.6, 172, 0, -14), (i, 32, 0, -16), (.95, 28, 0, -16), (SLAM_LARGO, 0, 0, 0))},
        'body': {'rotation': kf((0, 0, 0, 0), (.45, 10, 0, 0), (i, -28, 0, 0), (.95, -24, 0, 0), (SLAM_LARGO, 0, 0, 0)),
                 'position': kf((0, 0, 0, 0), (.45, 0, 1, 0), (i, 0, -2.5, -1), (.95, 0, -2.2, -.8), (SLAM_LARGO, 0, 0, 0))},
        'head': {'rotation': kf((0, 0, 0, 0), (.45, -10, 0, 0), (i, 18, 0, 0), (SLAM_LARGO, 0, 0, 0))},
        'leg_l': {'rotation': kf((0, 0, 0, 0), (.45, -10, 0, -4), (i, 26, 0, -8), (SLAM_LARGO, 0, 0, 0))},
        'leg_r': {'rotation': kf((0, 0, 0, 0), (.45, -10, 0, 4), (i, 26, 0, 8), (SLAM_LARGO, 0, 0, 0))},
    }
    return attack, slam, throw


BOSSES = {
    'astral_momia': lambda: biped_boss(75),        # brazos estirados como en su idle
    'astral_yeti': biped_boss,
    'astral_chaman': chaman_boss,
    'astral_coloso_musgoso': biped_boss,
    'astral_golem_forja': quad_boss,
    'astral_cangrejo': crab_boss,
}
# Paso mas pesado (rebote del cuerpo) para los jefes que caminan en dos patas.
WALK_BOB = {'astral_momia': .8, 'astral_yeti': 1.4, 'astral_chaman': .6, 'astral_coloso_musgoso': 1.2}


def apply_boss(m):
    maker = BOSSES.get(m.name)
    if not maker:
        return m
    attack, slam, throw = maker()
    attack = {b: c for b, c in attack.items() if b in m.bones}
    slam = {b: c for b, c in slam.items() if b in m.bones}
    throw = {b: c for b, c in throw.items() if b in m.bones}
    m.anim('attack', .9 if m.name != 'astral_cangrejo' else .68, attack, loop='once')
    m.anim('slam', SLAM_LARGO, slam, loop='once')
    m.anim('throw', THROW_LARGO, throw, loop='once')
    if m.name in WALK_BOB and 'walk' in m.anims:
        length, loop, ch = m.anims['walk']
        ch = {b: dict(c) for b, c in ch.items()}
        body = ch.setdefault('body', {})
        body['position'] = (0, bob(WALK_BOB[m.name], 1 / length), 0)
        if 'rotation' not in body:
            body['rotation'] = (-4, wave(5, 1 / length), 0)
        ch.setdefault('head', {}).setdefault('rotation', (wave(3, 2 / length), wave(-4, 1 / length), 0))
        m.anim('walk', length, ch, loop)
    return m


def mejorar(fn):
    @functools.wraps(fn)
    def wrapper(*a, **kw):
        return apply_boss(fn(*a, **kw))
    return wrapper


# ------------------------------------------------------------------ esqueletos (creatures_tanda3b.skeleton)
WALK_LARGO = {'escudero': 1.25, 'espadachin': .8}


def skeleton_anims(kind, bones):
    """idle, walk y attack de los 5 esqueletos. El arquero conserva su cuerda/flecha (se agregan en skeleton())."""
    L = WALK_LARGO.get(kind, 1.0)
    s = 1 / L
    legs = 30 if kind != 'escudero' else 24
    arms = 26 if kind == 'espadachin' else 18 if kind == 'escudero' else 22
    walk = {
        'leg_l': {'rotation': (wave(legs, s), 0, 0)},
        'leg_r': {'rotation': (wave(-legs, s), 0, 0)},
        'arm_l': {'rotation': (wave(-arms, s, 20), 0, wave(4, s))},
        'arm_r': {'rotation': (wave(arms * (0.4 if kind == 'arquero' else 1), s, 20), 0, wave(4, s))},
        'body': {'rotation': (-6 if kind == 'espadachin' else -4, wave(7, s), wave(2, s, 90)),
                 'position': (0, bob(.7, s), 0)},
        'head': {'rotation': (wave(3, 2 * s, 60), wave(-6, s), wave(-2, s, 90))},
    }
    if kind == 'nigromante':
        walk['orb'] = {'position': (0, wave(.4, 2 * s), 0)}
    idle = {
        'body': {'position': (0, wave(.25, 1 / 3), 0), 'rotation': (wave(1.5, 1 / 3, 90), 0, wave(2, 1 / 4))},
        'head': {'rotation': (wave(4, 1 / 3, 60), wave(14, 1 / 6), wave(3, 1 / 4, 30))},
        'arm_l': {'rotation': (wave(4, 1 / 3), 0, wave(-3, 1 / 3))},
        'arm_r': {'rotation': (wave(-4, 1 / 3), 0, wave(3, 1 / 3))},
        'leg_l': {'rotation': (0, 0, wave(1.5, 1 / 4))},
        'leg_r': {'rotation': (0, 0, wave(1.5, 1 / 4))},
    }
    if kind == 'nigromante':
        idle['orb'] = {'position': (0, wave(.5, .5), 0), 'scale': ('1+math.sin(q.anim_time*180)*0.12',) * 3}
    if kind == 'arquero':
        attack = {  # tensado: el cuerpo gira de costado y vuelve; los canales de la cuerda se agregan aparte
            'body': {'rotation': kf((0, 0, 0, 0), (.3, -4, -14, 0), (.55, -2, -10, 0), (.65, 0, 0, 0))},
            'head': {'rotation': kf((0, 0, 0, 0), (.3, -4, 12, 0), (.55, -2, 8, 0), (.65, 0, 0, 0))},
        }
        length = .65
    elif kind == 'nigromante':
        attack = {
            'arm_r': {'rotation': kf((0, 0, 0, 0), (.3, 70, 0, -20), (.45, 95, 0, -10), (.7, 50, 0, 0), (.95, 0, 0, 0))},
            'arm_l': {'rotation': kf((0, 0, 0, 0), (.3, 30, 0, 0), (.5, 60, 0, 0), (.95, 0, 0, 0))},
            'body': {'rotation': kf((0, 0, 0, 0), (.3, 8, 0, 0), (.5, -10, 0, 0), (.95, 0, 0, 0)),
                     'position': kf((0, 0, 0, 0), (.3, 0, .5, 0), (.5, 0, -.3, 0), (.95, 0, 0, 0))},
            'head': {'rotation': kf((0, 0, 0, 0), (.3, -12, 0, 0), (.5, 8, 0, 0), (.95, 0, 0, 0))},
            'orb': {'scale': kf((0, 1, 1, 1), (.3, 1.2, 1.2, 1.2), (.5, 1.6, 1.6, 1.6), (.7, .9, .9, .9), (.95, 1, 1, 1))},
        }
        length = .95
    else:
        shield = kind == 'escudero'
        attack = {
            'arm_r': {'rotation': kf((0, 0, 0, 0), (.18, -35, 0, 10), (.3, 95, 0, -14), (.42, 75, 0, -10), (.7, 0, 0, 0))},
            'arm_l': {'rotation': kf((0, 0, 0, 0), (.18, 10, 0, 0), (.3, 40 if shield else 25, 0, 0), (.7, 0, 0, 0))},
            'body': {'rotation': kf((0, 0, 0, 0), (.18, 6, 22, 0), (.3, -12, -22, 0), (.45, -8, -12, 0), (.7, 0, 0, 0)),
                     'position': kf((0, 0, 0, 0), (.18, 0, .3, .4), (.3, 0, -.4, -.8), (.7, 0, 0, 0))},
            'head': {'rotation': kf((0, 0, 0, 0), (.18, -4, -16, 0), (.3, 6, 14, 0), (.7, 0, 0, 0))},
            'leg_l': {'rotation': kf((0, 0, 0, 0), (.18, -10, 0, 0), (.3, 18, 0, 0), (.7, 0, 0, 0))},
            'leg_r': {'rotation': kf((0, 0, 0, 0), (.18, 8, 0, 0), (.3, -10, 0, 0), (.7, 0, 0, 0))},
        }
        if 'weapon' in bones:
            attack['weapon'] = {'rotation': kf((0, 0, 0, 0), (.18, 25, 0, 10), (.3, -50, 0, -25), (.45, -35, 0, -18), (.7, 0, 0, 0))}
        length = .7
    return idle, (L, walk), attack, length
