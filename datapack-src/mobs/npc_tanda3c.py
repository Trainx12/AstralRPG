"""Tanda 3c: personajes 3D propios para los NPC (chibi, 16 px por bloque).

Frente al norte (-Z). La mano derecha del personaje queda en +X (a la izquierda de quien lo mira).
"""
import random
from bbmodel import swing
from creatures_tanda3c import PixelModel, shade, W

SIDES = ('north', 'south', 'east', 'west')
FK = {'up': 1.08, 'down': .72, 'north': 1.0, 'south': .93, 'east': .9, 'west': .9}
SKIN = '#e9b89a'; SKIN_D = '#cf9578'; SKIN_H = '#f6cdb0'
GOLD = '#f2b53a'; GOLD_H = '#ffd76a'; GOLD_D = '#c4862a'
BLACK = '#17151c'; WOOD = '#8a5540'; WOOD_D = '#6b3f30'; WOOD_H = '#a56a4c'
LEATHER = '#7a4a30'; LEATHER_D = '#5e3826'; LEATHER_H = '#93603e'
SILVER = '#c9ccd4'; IRON = '#a3a5ad'; IRON_D = '#74767f'


# ------------------------------------------------------------------ pintura
def cloth(base, hi=None, lo=None, seed=0, grad=.13, blobs=13):
    """Tela con degradado suave y manchas de 2 a 4 pixeles (como las referencias), sin ruido fino."""
    def fn(f):
        rng = random.Random(f'{seed}/{f.cube["from"]}/{f.cube["to"]}/{f.face}')
        k0 = FK[f.face]
        for y in range(f.h):
            for x in range(f.w):
                g = 1.05 - grad * y / max(1, f.h - 1) if f.face in SIDES else 1
                f.set(x, y, shade(base, k0 * g + rng.uniform(-.02, .02)))
        tones = [t for t in (hi, lo) if t]
        if not tones:
            return
        for _ in range(max(1, f.w * f.h // blobs)):
            tone = rng.choice(tones)
            x, y = rng.randrange(f.w), rng.randrange(f.h)
            for _ in range(rng.randint(2, 4)):
                f.set(x, y, shade(tone, k0 + rng.uniform(-.02, .02)))
                x = max(0, min(f.w - 1, x + rng.choice((-1, 0, 1, 1))))
                y = max(0, min(f.h - 1, y + rng.choice((-1, 0, 0, 1))))
    return fn


def flat(col):
    return lambda f: [f.set(x, y, shade(col, FK[f.face])) for y in range(f.h) for x in range(f.w)]


def glow(col, core=None):
    def fn(f):
        f.fill(col)
        if core and f.w >= 3 and f.h >= 3:
            f.rect(1, 1, f.w - 2, f.h - 2, core)
    return fn


def seq(*fns):
    def fn(f):
        for g in fns:
            g(f)
    return fn


def on(faces, fn):
    faces = (faces,) if isinstance(faces, str) else faces
    return lambda f: fn(f) if f.face in faces else None


def row(y, col, x0=0, x1=None, faces=SIDES):
    """Fila completa (y<0 cuenta desde abajo) en las caras laterales."""
    def fn(f):
        if f.face in faces:
            yy = y if y >= 0 else f.h + y
            f.rect(x0, yy, (f.w if x1 is None else x1) - x0, 1, shade(col, FK[f.face]))
    return fn


def col_(x, colr, y0=0, y1=None, faces=('north',)):
    def fn(f):
        if f.face in faces:
            xx = x if x >= 0 else f.w + x
            f.rect(xx, y0, 1, (f.h if y1 is None else y1) - y0, shade(colr, FK[f.face]))
    return fn


def px(face, pts, colr):
    return lambda f: [f.set(x, y, colr) for x, y in pts] if f.face == face else None


def rows(face, data, pal, ox=0, oy=0):
    return lambda f: f.rows(data, pal, ox, oy) if f.face == face else None


def buckle(y, colr=GOLD, w=2, face='north'):
    """Hebilla centrada: marco de color con centro oscuro."""
    def fn(f):
        if f.face != face:
            return
        x0 = (f.w - w - 2) // 2
        f.rect(x0, y - 2, w + 2, 4, colr)
        f.rect(x0 + 1, y - 1, w, 2, BLACK)
        f.set(x0, y - 2, shade(colr, 1.25))
    return fn


def box(m, bone, a, b, paint, rotation=None, origin=None, **faces):
    art = {'*': paint}
    art.update(faces)
    m.cube(bone, a, b, '#808080', art=art, rotation=rotation, origin=origin)


# ------------------------------------------------------------------ esqueleto comun
def rig(name, arm_r=(0, 0, -5), arm_l=(0, 0, 5), body_y=5, head_y=15, shoulder=6.75):
    m = PixelModel(name, hitbox=((-4.8, 0, -4.8), (4.8, 28.8, 4.8)))
    m.bone('root', (0, 0, 0))
    m.bone('body', (0, body_y, 0), 'root')
    m.bone('head', (0, head_y, 0), 'body')
    m.bone('arm_r', (shoulder, head_y - 1, 0), 'body', rotation=arm_r)
    m.bone('arm_l', (-shoulder, head_y - 1, 0), 'body', rotation=arm_l)
    m.bone('leg_r', (2.5, body_y, 0), 'root')
    m.bone('leg_l', (-2.5, body_y, 0), 'root')
    m.anim('idle', 4, {'body': {'scale': (1, '1+math.sin(q.anim_time*90)*0.015', 1)},
                       'head': {'rotation': (swing(1.5, .25), swing(5, .25, 30), 0)},
                       'arm_l': {'rotation': (swing(3, .25, 90), 0, 0)}})
    m.anim('saludo', 1.5, {'arm_l': {'rotation': (0, 0, '-110+math.sin(q.anim_time*960)*18')},
                           'head': {'rotation': (0, 0, -6)}}, loop='once')
    return m


def legs(m, leg, boot, boot_h=2, y1=5, strap=None):
    for b, x in (('leg_r', .5), ('leg_l', -4.5)):
        box(m, b, (x, boot_h, -2), (x + 4, y1, 2), leg)
        box(m, b, (x - .3, 0, -3), (x + 4.3, boot_h, 2.3), seq(boot, strap) if strap else boot)


def arms(m, sleeve, hand, cuff=None, y0=7, w=3.5, hw=5, top=15, cuff_h=2, cap=None, cap_h=3.4):
    """Brazos colgando; cuff = boca de manga que sobresale; cap = manga corta/hombro que sobresale arriba."""
    for b, s in (('arm_r', 1), ('arm_l', -1)):
        x0, x1 = (hw, hw + w) if s > 0 else (-hw - w, -hw)
        box(m, b, (x0, y0, -2), (x1, top, 2), sleeve)
        if cuff:
            box(m, b, (x0 - .8, y0 - .6, -2.8), (x1 + .8, y0 + cuff_h, 2.8), cuff)
        if cap:
            box(m, b, (x0 - .6, top - cap_h, -2.6), (x1 + .6, top + .4, 2.6), cap)
        box(m, b, (x0 + .5, y0 - 1.5, -1.5), (x1 - .5, y0, 1.5), hand)


def belt3d(m, y, colr, buckle_col, hw=5, hd=3, h=1.8):
    """Cinturon con volumen y hebilla que sobresale."""
    box(m, 'body', (-hw - .35, y, -hd - .35), (hw + .35, y + h, hd + .35), seq(flat(colr), row(0, shade(colr, 1.25))))
    bk = lambda f: (f.fill(buckle_col), f.rect(1, 1, max(1, f.w - 2), max(1, f.h - 2), BLACK), f.set(0, 0, shade(buckle_col, 1.3))) \
        if f.face == 'north' else f.fill(shade(buckle_col, FK[f.face]))
    box(m, 'body', (-1.7, y - .7, -hd - .9), (1.7, y + h + .7, -hd - .3), bk)


def nose(m, y=17.6, z=-5, colr='#dc9a80', w=2, h=1.8):
    box(m, 'head', (-w / 2, y, z - .9), (w / 2, y + h, z), seq(flat(colr), row(0, shade(colr, 1.08), faces=('north',))))


def brows(m, colr, y=22, z=-5, w=3, gap=1.6):
    for x in (gap, -gap - w):
        box(m, 'head', (x, y, z - .45), (x + w, y + .8, z), flat(colr))


FACE = ["SSSSSSSSSS",
        "SSSSSSSSSS",
        "SSSSSSSSSS",
        "SddSSSSddS",
        "SwpSSSSpwS",
        "SSSSSSSSSS",
        "SSSSnnSSSS",
        "SSSSSSSSSS",
        "SSSmmmmSSS",
        "ssssssssss"]


def face_pal(pupil='#2b3a6b', brow='#6b3f2a', hair='#6b3f2a'):
    return {'S': SKIN, 's': SKIN_D, 'w': W, 'p': pupil, 'd': brow, 'n': '#dc9a80', 'm': '#b8705c', 'h': hair,
            'H': shade(hair, 1.2), 'k': BLACK, 'g': GOLD, 'c': '#7fe9f2', 'C': '#c9fbff', 'e': '#3fae7a', 'E': '#8fe0b0',
            'W': '#eeeeea', 'G': '#cfcfcc', 'r': '#d83a3a', 'T': '#c9a070', 't': '#9a7650', 'x': '#0d0d12',
            'u': '#6fe6d6', 'U': '#d2fff6', 'o': '#f2b06a', 'i': shade(pupil, 1.35), 'L': SKIN_H}


def head(m, front, pal, hair=None, size=(10, 10, 10), y0=15, skin=SKIN):
    hx, hy, hz = size[0] / 2, size[1], size[2] / 2
    pal = dict(pal, S=skin)
    base = cloth(skin, SKIN_H, SKIN_D, blobs=30)
    art = {'north': seq(base, rows('north', front, pal))}
    if hair:
        art.update(south=hair, east=hair, west=hair, up=hair)
    box(m, 'head', (-hx, y0, -hz), (hx, y0 + hy, hz), base, **art)


def ears(m, y=18.5, colr=SKIN, big=False):
    for x in (5, -6.2 if not big else -6.7):
        w = 1.7 if big else 1.2
        box(m, 'head', (x, y, -1.2), (x + w, y + (3.2 if big else 2.4), .8), cloth(colr, SKIN_H, SKIN_D, blobs=40))


def staff(m, bone, x, z, y0, y1, paint, w=1.2):
    box(m, bone, (x - w / 2, y0, z - w / 2), (x + w / 2, y1, z + w / 2), paint)


def wraps(colr, every=5, off=2):
    return lambda f: [f.rect(0, y, f.w, 1, shade(colr, FK[f.face])) for y in range(off, f.h, every)] if f.face in SIDES else None


# ------------------------------------------------------------------ 1. mago azul (Expediciones)
def mago():
    m = rig('astral_npc_mago', arm_r=(42, 0, -4))
    belt3d(m, 7, WOOD, SILVER)
    BL, BH, BLo = '#5661b6', '#5f95c6', '#454d9a'
    WT, WTd = '#e8e8f0', '#b4b6c6'
    robe = cloth(BL, BH, BLo, seed=1)
    boot = seq(cloth(WOOD, WOOD_H, WOOD_D), row(0, WT))
    legs(m, flat('#2a1c1c'), boot, boot_h=2.5)
    # falda de la tunica: abierta al frente, con borde blanco
    opening = lambda f: (f.rect(4, 0, 3, f.h, WT), f.rect(5, 0, 1, f.h, '#2a1c1c'), f.rect(3, f.h - 3, 5, 3, WT),
                         f.rect(4, f.h - 3, 3, 3, '#3a2622'), f.rect(4, f.h - 1, 3, 1, WOOD)) if f.face == 'north' else None
    box(m, 'body', (-5.5, 1.5, -3.5), (5.5, 7, 3.5), seq(robe, row(-1, WT), opening))
    torso = seq(robe, col_(4, WT), col_(5, WTd), row(-2, WOOD), row(-1, WOOD_D), buckle(6, SILVER))
    box(m, 'body', (-5, 7, -3), (5, 15, 3), torso)
    # cuello alto abierto adelante
    collar = seq(robe, row(0, WT), row(1, WTd, faces=('north',)))
    for a, b in (((-5.8, 14, -4.6), (-4.6, 18.6, 4.6)), ((4.6, 14, -4.6), (5.8, 18.6, 4.6)), ((-5.8, 14, 3.6), (5.8, 18.6, 4.8)),
                 ((-5.8, 14, -5.2), (-1.6, 18, -4.2)), ((1.6, 14, -5.2), (5.8, 18, -4.2))):
        box(m, 'body', a, b, collar)
    arms(m, robe, flat('#0d0d12'), cuff=seq(robe, row(-1, WT), row(-2, WTd)), cuff_h=3)
    # cabeza negra, sin rasgos
    box(m, 'head', (-4.5, 15, -4.5), (4.5, 23.5, 4.5), flat('#0d0d12'))
    # sombrero de ala ancha, banda marron con hebilla plateada y punta con rulo
    m.bone('hat', (0, 20, 0), 'head', rotation=(-5, 0, 4))
    hat = cloth(BL, BH, BLo, seed=2)
    box(m, 'hat', (-9, 20.0, -9), (9, 21.0, 9), hat)
    band = seq(hat, row(-1, WOOD), row(-2, WOOD_H), row(-3, WOOD),
               lambda f: (f.rect(3, f.h - 4, 5, 4, SILVER), f.rect(4, f.h - 3, 3, 2, WOOD), f.set(6, f.h - 2, SILVER)) if f.face == 'north' else None)
    box(m, 'hat', (-5.5, 21.0, -5.5), (5.5, 25.0, 5.5), band)
    box(m, 'hat', (-4.5, 25.0, -4.2), (4.2, 27.5, 4.8), hat)
    box(m, 'hat', (-4, 27.5, -2.5), (2.6, 29.7, 4.8), hat)
    box(m, 'hat', (-4.2, 29.7, 0), (.8, 31.5, 5), hat)
    box(m, 'hat', (-5.4, 30.7, 2.4), (-2.4, 32.5, 5.2), hat)
    curl = flat(BH)
    for a, b in (((-7, 31.5, 3.2), (-5.2, 32.5, 4.4)), ((-7.8, 29.1, 3.2), (-6.8, 32.5, 4.4)), ((-7.8, 28.3, 3.2), (-5.6, 29.3, 4.4)),
                 ((-6.2, 29.1, 3.2), (-5.4, 30.5, 4.4))):
        box(m, 'hat', a, b, curl)
    for x, z in ((-1, 3), (1.6, 1)):   # mechones arriba
        box(m, 'hat', (x, 32.2, z), (x + .8, 33.6, z + .8), curl)
    # baston en zigzag con cristal brillante y cintas celestes
    m.bone('baston', (6.8, 9, -5.8), 'body')
    wood = seq(cloth(WOOD, WOOD_H, WOOD_D, blobs=8), wraps(BH, 6, 9), wraps(BL, 6, 10))
    woodp = cloth(WOOD, WOOD_H, WOOD_D, blobs=8)
    staff(m, 'baston', 6.8, -5.8, 0, 23, wood)
    for a, b in (((6, 23, -6.6), (10.6, 24.6, -5)), ((9, 24.6, -6.6), (10.6, 26.6, -5)), ((6, 26.6, -6.6), (10.6, 28.2, -5)),
                 ((6, 28.2, -6.6), (7.6, 35.4, -5)), ((6, 35.4, -6.6), (14.6, 37, -5)), ((13, 29.6, -6.6), (14.6, 35.4, -5)),
                 ((10.6, 28.6, -6.6), (14.6, 30.2, -5))):
        box(m, 'baston', a, b, woodp)
    m.bone('cristal', (10.3, 32.6, -5.8), 'baston')
    box(m, 'cristal', (8, 30.4, -7), (12.6, 35, -4.6), glow('#c79bf5', W))
    rib = flat(BH)
    for a, b in (((7.4, 9.5, -6.2), (8.2, 14, -5.4)), ((8.2, 7.5, -6.2), (9, 10.5, -5.4)), ((5.6, 12, -6.2), (6.2, 16, -5.4))):
        box(m, 'baston', a, b, rib)
    m.lit = ('cristal',)
    return m


# ------------------------------------------------------------------ 2. herrero enano
def herrero():
    m = rig('astral_npc_herrero', arm_r=(24, 0, -14), arm_l=(0, 0, 8), head_y=14, shoulder=7.5)
    belt3d(m, 6.6, '#35595c', SILVER, hw=6, hd=3.5, h=2)
    TE, TEh, TEd = '#3f6c70', '#56888a', '#2f5559'
    lea = cloth(LEATHER, LEATHER_H, LEATHER_D, seed=3)
    legs(m, cloth(LEATHER, LEATHER_H, LEATHER_D), cloth(LEATHER_D, LEATHER, '#4a2c1e'), boot_h=2.5)
    BELT = '#35595c'
    torso = seq(lea, col_(3, LEATHER_D, 0, 5), col_(8, LEATHER_D, 0, 5), row(-4, BELT), row(-3, shade(BELT, .8)), row(-2, TE), row(-1, TEd),
                lambda f: (f.rect(4, f.h - 5, 4, 4, SILVER), f.rect(5, f.h - 4, 2, 2, '#3b4648'), f.set(4, f.h - 5, W)) if f.face == 'north' else None)
    box(m, 'body', (-6, 5, -3.5), (6, 14, 3.5), torso)
    # falda de cuero en tiras
    strips = lambda f: [f.rect(x, 0, 1, f.h, shade(LEATHER_D, FK[f.face])) for x in range(2, f.w, 3)] if f.face in SIDES else None
    box(m, 'body', (-6.2, 2.4, -3.7), (6.2, 6, 3.7), seq(lea, strips, row(-1, LEATHER_D)))
    for x in (5.2, -9.2):   # hombreras de cuero con tira
        box(m, 'body', (x, 11.5, -3.2), (x + 4, 14.6, 3.2), seq(cloth(LEATHER_D, LEATHER, '#4a2c1e'), row(-1, LEATHER_H), row(1, '#4a2c1e')))
    skin = cloth('#e9a58c', SKIN_H, '#cf8a74', blobs=20)
    glove = seq(cloth(TE, TEh, TEd), row(0, TEh))
    for b, s_ in (('arm_r', 1), ('arm_l', -1)):
        x0, x1 = (6, 9.5) if s_ > 0 else (-9.5, -6)
        box(m, b, (x0 - .6, 9.6, -2.6), (x1 + .6, 13.4, 2.6), seq(lea, row(-1, LEATHER_D)))   # manga corta que sobresale
        box(m, b, (x0, 6.4, -2), (x1, 10, 2), skin)
        box(m, b, (x0 - .7, 4, -2.7), (x1 + .7, 7, 2.7), glove)   # guantes verde azulados
    pal = face_pal()
    F = ["SSSSSSSSSS",
         "SSSSSSSSSS",
         "SSSSSSSSSS",
         "SSSSSSSSSS",
         "SSSLLLLSSS",
         "SSSSSSSSSS",
         "WWSSSSSSWW",
         "WWWWWWWWWW",
         "WWWWWWWWWW"]
    head(m, F, pal, y0=14, size=(10, 9, 10), skin='#e9a58c')
    ears(m, y=17.5, colr='#e9a58c', big=True)
    for x in (6.2, -7.2):   # punta de la oreja
        box(m, 'head', (x, 19.5, -.8), (x + 1.4, 21.4, .4), skin)
    box(m, 'head', (-1.8, 16.4, -6.9), (1.8, 19.2, -5), cloth('#e8937c', '#f6b49c', '#cf7a68', blobs=7))   # nariz grande
    # antiparras: marco grueso gris tostado, cristal celeste con reflejo y correa alrededor de la cabeza
    m.bone('gafas', (0, 19.5, -5.3), 'head')
    gp = {'f': '#7d7566', 'F': '#a89e8a', 'q': '#c4ebe6', 'Q': '#f6fffd', 'e': '#9fd6d0'}
    lens = ["fFFFf", "FqQQF", "FqqQF", "FeqqF", "fFFFf"]
    for x in (.3, -5.3):
        box(m, 'gafas', (x, 17.8, -6.3), (x + 5, 22.6, -5), flat('#a89e8a'), north=lambda f: f.rows(lens, gp))
    box(m, 'gafas', (-.5, 19.8, -5.9), (.5, 21, -5.1), flat('#7d7566'))
    box(m, 'head', (-5.25, 19.6, -5.2), (5.25, 21, 5.25), flat('#6b4a35'))
    # barba blanca enorme en capas, con mechones
    beard = cloth('#eeeeea', W, '#cfcfcc', seed=4, blobs=9)
    box(m, 'head', (-6.2, 12.5, -6.2), (6.2, 17.6, -4.4), beard)
    box(m, 'head', (-5.2, 10.6, -6.4), (5.2, 13, -4.6), beard)
    box(m, 'head', (-3.4, 9.4, -6.2), (3.4, 10.8, -4.8), beard)
    for x in (-6.6, 5.2, -4.6, 3.4):   # puntas
        box(m, 'head', (x, 11.4, -6), (x + 1.4, 13, -4.8), beard)
    for x in (1.6, -5.4):   # bigote
        box(m, 'head', (x, 16.2, -6.7), (x + 3.8, 18, -5.6), beard)
    for x in (5, -6):
        box(m, 'head', (x, 13, -5), (x + 1, 18, -1), beard)
    box(m, 'head', (-5.3, 14.5, 4.6), (5.3, 21.4, 5.4), beard)   # pelo blanco atras
    # casco verde azulado en dos niveles
    HE, HEh, HEd = '#35595c', '#4a7477', '#274447'
    helm = seq(cloth(HE, HEh, HEd, seed=5, blobs=22), row(1, HEd), row(0, HEh))
    box(m, 'head', (-6, 21.4, -6), (6, 24.6, 6), seq(cloth(HE, HEh, HEd, seed=6, blobs=22), row(0, HEh), row(-1, HEd)))
    box(m, 'head', (-5.2, 24.6, -5.2), (5.2, 28, 5.2), helm)
    # martillo de herrero en la mano derecha, parado como el pico del minero
    m.bone('martillo', (9.6, 8, -4.6), 'body', rotation=(0, 0, -6))
    wood = seq(cloth(WOOD, WOOD_H, WOOD_D, blobs=8), wraps(LEATHER_D, 4, 2))
    staff(m, 'martillo', 9.6, -4.6, 1, 15, wood, w=1.9)
    plate = lambda f: (f.fill('#7f7a70'), f.rect(1, 1, f.w - 2, f.h - 2, '#aaa594'), f.rect(2, 2, max(1, f.w - 4), max(1, f.h - 4), '#c9c5b0'),
                       f.set(2, 2, '#eeebdc'), f.rect(3, f.h - 3, max(1, f.w - 6), 1, '#b4b09c'))
    box(m, 'martillo', (5, 14.4, -7.6), (14.2, 21, -1.6), plate)
    box(m, 'martillo', (8.4, 13.6, -5.8), (10.8, 14.6, -3.4), flat('#6f6a60'))
    return m


# ------------------------------------------------------------------ 3. subastas (galera verde)
def subastas():
    m = rig('astral_npc_subastas')
    belt3d(m, 6, BLACK, GOLD)
    GR, GRh, GRd = '#1f5a48', '#2c7560', '#16443a'
    PA, PAh, PAd = '#8a4f33', '#a26342', '#6e3d28'
    WH = '#f1ede6'
    zig = lambda f: [f.set(x, 1 - x % 2, PAh) for x in range(f.w)] if f.face in SIDES else None
    legs(m, seq(cloth(PA, PAh, PAd, seed=6), zig), cloth(PAd, PA, '#57301f'))
    shirt = seq(cloth(WH, W, '#d9d2c8', seed=7, blobs=18), row(2, '#ddd6cc'), row(5, '#ddd6cc'))
    vest = lambda f: (f.rect(0, 0, 3, f.h, GR), f.rect(f.w - 3, 0, 3, f.h, GR), f.set(3, 0, GR), f.set(f.w - 4, 0, GR),
                      f.rect(2, 1, 1, f.h - 1, GRh), f.rect(f.w - 3, 1, 1, f.h - 1, GRh), f.set(1, 6, GRd), f.set(f.w - 2, 4, GRd),
                      f.set(4, 2, '#d9d2c8'), f.set(4, 4, '#d9d2c8'), f.set(4, 6, '#d9d2c8')) if f.face == 'north' else None
    back = on(('south', 'east', 'west'), cloth(GR, GRh, GRd, seed=8))
    torso = seq(shirt, back, vest, row(-3, BLACK), row(-2, '#2a2730'), buckle(8, GOLD, 2),
                row(-1, PA, 3, 7, faces=('north',)))
    box(m, 'body', (-5, 5, -3), (5, 15, 3), torso)
    # faldones del chaleco por debajo del cinturon
    for x in (2.2, -5.2):
        box(m, 'body', (x, 3.4, -3.2), (x + 3, 6, 3.2), cloth(GR, GRh, GRd, seed=9))
    box(m, 'body', (-5.2, 3.4, 2.2), (5.2, 6, 3.2), cloth(GR, GRh, GRd, seed=9))
    # mangas blancas infladas
    arms(m, shirt, cloth(SKIN, SKIN_H, SKIN_D, blobs=30), cuff=seq(shirt, row(-1, '#cfc8bd')), w=3.8, cuff_h=2.2)
    for b, x in (('arm_r', 4.8), ('arm_l', -9)):
        box(m, b, (x, 10, -2.4), (x + 4.2, 14.6, 2.4), shirt)
    pal = face_pal(pupil='#0f2a20', brow='#1d1b22', hair='#1d1b22')
    pal.update(e='#3fae7a')
    F = ["SSSSSSSSSS",
         "SSSSSSSSSS",
         "SSSSSSSSSS",
         "kkkSSSSkkk",
         "wepSSSSpew",
         "wepSSSSpew",
         "SSSSnnSSSS",
         "SSSSSSSSSS",
         "SSSSSSSSSS",
         "ssssssssss"]
    head(m, F, pal)   # pelado: sin pelo debajo de la galera
    ears(m, big=True)
    nose(m, 18, w=2.2, h=2)
    brows(m, '#1d1b22', y=23, w=3.4, gap=1.2)
    for x in (2, -5.2):   # solapas del chaleco con volumen
        box(m, 'body', (x, 7.8, -3.5), (x + 3.2, 15.2, -2.9), seq(cloth(GR, GRh, GRd, seed=8), col_(0 if x > 0 else -1, GRh)))
    # bigote negro grande, con las puntas caidas
    mus = cloth('#1d1b22', '#34313c', '#0f0e13', blobs=10)
    box(m, 'head', (-1.2, 16.2, -6.4), (1.2, 17.8, -5.2), mus)
    for s in (1, -1):
        x = 1 if s > 0 else -4.8
        box(m, 'head', (x, 15.8, -6.3), (x + 3.8, 18, -5), mus)
        x = 4.2 if s > 0 else -6.2
        box(m, 'head', (x, 16.8, -6.1), (x + 2, 19, -4.8), mus)
        x = 5.6 if s > 0 else -6.8
        box(m, 'head', (x, 18.4, -5.9), (x + 1.2, 20, -4.8), mus)
    # galera verde oscura con banda
    m.bone('hat', (0, 24.5, 0), 'head', rotation=(-4, 0, 0))
    hat = cloth('#1d4f42', '#2a6a58', '#143a32', seed=10, blobs=20)
    box(m, 'hat', (-8.6, 24.2, -8.6), (8.6, 25.2, 8.6), hat)
    box(m, 'hat', (-5, 25.2, -5), (5, 31.5, 5), seq(hat, row(-1, '#8a4a30'), row(-2, '#a85e3a'), row(-3, '#8a4a30')))
    box(m, 'hat', (-5.4, 30.6, -5.4), (5.4, 31.8, 5.4), hat)
    return m


# ------------------------------------------------------------------ 4. bazar (explorador)
def bazar():
    m = rig('astral_npc_bazar', arm_r=(42, 0, -4))
    belt3d(m, 6, '#2c2a2e', GOLD)
    GN, GNh, GNd = '#4f8a50', '#66a55e', '#3b6e44'
    BR, BRh, BRd = '#8a5a35', '#a47245', '#6b4428'
    RED = '#c9402f'
    legs(m, cloth(BR, BRh, BRd, seed=11), cloth(BRd, BR, '#523320'), boot_h=2.5)
    tunic = cloth(GN, GNh, GNd, seed=12, blobs=9)
    picos = lambda f: [f.set(x, f.h - 1, (0, 0, 0), 0) for x in range(1, f.w, 2)] if f.face in SIDES else None
    box(m, 'body', (-5.2, 3, -3.2), (5.2, 6, 3.2), seq(tunic, row(-2, GNd), picos))
    torso = seq(tunic, col_(2, LEATHER), col_(7, LEATHER), col_(2, LEATHER, faces=('south',)), col_(7, LEATHER, faces=('south',)),
                row(-3, '#2c2a2e'), row(-2, '#3a373d'), buckle(8, GOLD, 2))
    box(m, 'body', (-5, 5, -3), (5, 15, 3), torso)
    box(m, 'body', (-4.8, 5.4, -4.2), (-2, 8.2, -3), seq(cloth(LEATHER, LEATHER_H, LEATHER_D), px('north', [(1, 1)], GOLD)))   # bolsita
    # panuelo rojo
    scarf = cloth(RED, '#e05a3f', '#a33026', blobs=10)
    box(m, 'body', (-5.4, 13.4, -3.6), (5.4, 15.6, 3.6), scarf)
    box(m, 'body', (-3.4, 12, -3.9), (3.4, 13.6, -3), scarf)
    box(m, 'body', (-2, 10.6, -3.9), (2, 12.2, -3), scarf)
    box(m, 'body', (-.8, 9.4, -3.9), (.8, 10.8, -3), scarf)
    arms(m, cloth(SKIN, SKIN_H, SKIN_D, blobs=30), cloth(SKIN, SKIN_H, SKIN_D, blobs=30), cap=seq(tunic, row(-1, GNd)), cap_h=5)
    pal = face_pal(pupil='#27304f', brow='#6b3f2a', hair='#7a4a2c')
    F = ["hhhhhhhhhh",
         "hhHhhhhHhh",
         "hSSSSSSSSh",
         "wipSSSSpiw",
         "wppSSSSppw",
         "SSSLLLLSSS",
         "SSSSLLSSSS",
         "SSSSSSSSSS",
         "SSSSnnSSSS",
         "ssssssssss"]
    hair = cloth('#7a4a2c', '#93603a', '#5e3820', seed=13, blobs=10)
    head(m, F, pal, hair=seq(hair, lambda f: f.rect(0 if f.face == 'east' else 4, 5, f.w - 4, f.h - 5, SKIN) if f.face in ('east', 'west') else None))
    ears(m)
    nose(m)
    brows(m, '#5e3820', y=22)
    box(m, 'head', (-5.3, 22.8, -5.5), (5.3, 24.2, -4.4), hair)   # flequillo
    for x in (4.6, -5.8):
        box(m, 'head', (x, 16, -4.8), (x + 1.2, 21, 3), hair)
    # sombrero marron con banda verde y pluma roja
    m.bone('hat', (0, 24.5, 0), 'head', rotation=(-6, 0, -3))
    hat = cloth(BR, BRh, BRd, seed=14, blobs=12)
    box(m, 'hat', (-8, 24, -8), (8, 25.2, 8), hat)
    box(m, 'hat', (-5, 25.2, -5), (5, 28.4, 5), seq(hat, row(-1, '#5f9a55'), row(-2, '#76b266')))
    box(m, 'hat', (-4, 28.4, -4), (4, 30, 4), hat)
    box(m, 'hat', (-2.6, 30, -2.6), (2.6, 31, 2.6), hat)
    feather = cloth(RED, '#ee6a4a', '#a02a22', blobs=6)
    box(m, 'hat', (-6.6, 25.2, 0), (-5, 30, 3), feather)
    box(m, 'hat', (-6.6, 28.6, 2.2), (-5, 32.6, 5.4), feather)
    box(m, 'hat', (-6.4, 31.6, 4.6), (-5.2, 34, 7), feather)
    # mochila grande con rollo y sacos
    pack = seq(cloth(LEATHER, LEATHER_H, LEATHER_D, seed=15), row(3, LEATHER_D), px('south', [(4, 4), (5, 4)], GOLD))
    box(m, 'body', (-4.6, 6.5, 3), (4.6, 15, 7.4), pack)
    box(m, 'body', (-6.2, 14.6, 3.4), (6.2, 21, 8), seq(cloth('#4f8f7a', '#66a892', '#3a7262', blobs=10), col_(2, LEATHER_D, faces=SIDES + ('up',)),
                                                          col_(-3, LEATHER_D, faces=SIDES + ('up',))))
    sack = cloth('#b89468', '#d0ae80', '#96764f', blobs=8)
    box(m, 'body', (-7.6, 5.5, 3.4), (-4.6, 10, 6.6), seq(sack, row(0, LEATHER_D)))
    box(m, 'body', (4.6, 8, 3.6), (7, 11.5, 6.2), seq(sack, row(0, LEATHER_D)))
    straw = cloth('#e8d29a', '#f6e6b8', '#c9b07a', blobs=5)
    for y, z in ((7.2, 5.4), (8.4, 4.2), (6.2, 4.6)):
        box(m, 'body', (-10.4, y, z), (-7.6, y + .8, z + .8), straw)
    # baston con gancho y farol encendido colgando
    m.bone('baston', (6.8, 9, -5.8), 'body')
    wood = seq(cloth('#a0483a', '#bb5e48', '#7f3530', blobs=8), wraps('#e0603a', 6, 8))
    staff(m, 'baston', 6.8, -5.8, 0, 26, wood)
    box(m, 'baston', (6.2, 26, -6.4), (11.8, 27.2, -5.2), wood)
    box(m, 'baston', (10.6, 24.6, -6.4), (11.8, 26, -5.2), wood)
    box(m, 'baston', (11, 22.6, -6), (11.4, 24.6, -5.6), flat('#3a3d4a'))
    m.bone('farol', (11.2, 22.6, -5.8), 'baston')
    frame = flat('#3a3d4a')
    box(m, 'farol', (8.8, 21.6, -8.2), (13.6, 22.6, -3.4), frame)
    box(m, 'farol', (8.8, 15.2, -8.2), (13.6, 16.2, -3.4), frame)
    light = lambda f: (f.fill('#ffd866'), [f.rect(0, y, f.w, 1, '#fff3b8') for y in (1, 3)], f.rect(0, 0, 1, f.h, '#3a3d4a'),
                       f.rect(f.w - 1, 0, 1, f.h, '#3a3d4a'))
    box(m, 'farol', (9.1, 16.2, -7.9), (13.3, 21.6, -3.7), light)
    m.lit = ('farol',)
    m.anims['idle'][2]['farol'] = {'rotation': (0, 0, swing(5, .5))}
    return m


# ------------------------------------------------------------------ 5. cronista (anciano)
def cronista():
    m = rig('astral_npc_cronista', arm_r=(14, 0, -6))
    belt3d(m, 7, BLACK, GOLD)
    BL, BH, BLo = '#2f6f9f', '#3f93b8', '#245682'
    robe = cloth(BL, BH, BLo, seed=16)
    legs(m, flat('#5a2f26'), cloth(WOOD, WOOD_H, WOOD_D), boot_h=2.5, strap=row(0, WOOD_H))
    opening = lambda f: (f.rect(4, 0, 3, f.h, '#1c3f5e'), f.rect(5, 0, 1, f.h - 1, GOLD), f.rect(4, f.h - 2, 3, 2, '#5a2f26'),
                         f.rect(3, 0, 1, f.h, GOLD), f.rect(7, 0, 1, f.h, GOLD), f.set(2, f.h - 2, GOLD), f.set(8, f.h - 2, GOLD)) if f.face == 'north' else None
    box(m, 'body', (-5.5, 1.5, -3.5), (5.5, 7, 3.5), seq(robe, row(-1, GOLD), row(-2, GOLD_D, faces=('north',)), opening))
    torso = seq(robe, row(-2, BLACK), row(-1, '#2a2730'), buckle(7, GOLD, 2), col_(4, BLo, 0, 5), col_(5, BLo, 0, 5))
    box(m, 'body', (-5, 7, -3), (5, 15, 3), torso)
    collar = seq(flat(GOLD), row(0, GOLD_H), row(-1, GOLD_D))
    for a, b in (((-5.6, 14, -3.6), (-4.4, 17.6, 3.6)), ((4.4, 14, -3.6), (5.6, 17.6, 3.6)), ((-5.6, 14, 2.4), (5.6, 17.6, 3.6))):
        box(m, 'body', a, b, collar)
    arms(m, robe, cloth(SKIN, SKIN_H, SKIN_D, blobs=30), cuff=seq(flat(GOLD), row(0, GOLD_H), row(-1, GOLD_D)), cuff_h=2.6)
    # libro rojo bajo el brazo derecho: tapas con marco dorado, lomo con nervios y hojas a la vista
    BK, BKd = '#b03a2a', '#8f2a20'
    cover = lambda f: (f.fill(shade(BK, FK[f.face])), f.rect(0, 0, f.w, 1, GOLD), f.rect(0, f.h - 1, f.w, 1, GOLD), f.rect(0, 0, 1, f.h, GOLD),
                       f.rect(f.w - 1, 0, 1, f.h, GOLD), f.rect(1, 1, f.w - 2, f.h - 2, shade(BK, FK[f.face])), f.set(2, 3, GOLD_H),
                       f.set(2, 4, GOLD)) if f.face in ('north', 'south') else f.fill(shade(BK, FK[f.face]))
    pages = lambda f: (f.fill('#efe2bd'), [f.rect(0, y, f.w, 1, '#cdbb8e') for y in range(1, f.h, 2)] if f.face in ('east', 'west') else
                       [f.rect(x, 0, 1, f.h, '#cdbb8e') for x in range(1, f.w, 2)])
    spine = lambda f: (f.fill(shade(BKd, FK[f.face])), [f.rect(0, y, f.w, 1, GOLD) for y in (1, 3, f.h - 2)])
    box(m, 'body', (5.2, 3.4, -6.2), (10, 11, -5.6), cover)
    box(m, 'body', (5.6, 3.8, -5.6), (9.7, 10.6, -3.6), pages)
    box(m, 'body', (5.2, 3.4, -3.6), (10, 11, -3), cover)
    box(m, 'body', (4.8, 3.4, -6.2), (5.6, 11, -3), spine)
    pal = face_pal(pupil='#3a4a6a', brow='#eeeeea')
    F = ["WWWWWWWWWW",
         "WWWWWWWWWW",
         "WSSSSSSSSW",
         "WWWSSSSWWW",
         "SSSSSSSSSS",
         "ScCSSSScCS",
         "SSSSnnSSSS",
         "WSSSnnSSSW",
         "WWWWWWWWWW",
         "WWWWWWWWWW"]
    white = cloth('#eeeeea', W, '#cfcfcc', seed=17, blobs=9)
    head(m, F, pal, hair=white)
    ears(m)
    box(m, 'head', (-1.2, 16.6, -6.4), (1.2, 19, -5), cloth('#e39a80', SKIN, '#cf8068', blobs=9))
    for x in (.8, -4.2):   # cejas blancas tupidas
        box(m, 'head', (x, 21, -5.6), (x + 3.4, 22, -5), white)
    m.bone('gafas', (0, 19.5, -5.3), 'head')
    lens = ["cCc", "ccc"]
    for x in (1, -4):   # cristales chicos con marco fino dorado
        box(m, 'gafas', (x, 18.9, -5.5), (x + 3, 20.7, -5), flat(GOLD), north=lambda f: f.rows(lens, pal))
        box(m, 'gafas', (x - .25, 18.65, -5.45), (x + 3.25, 20.95, -5.2), flat(GOLD))
    box(m, 'gafas', (-1, 19.7, -5.45), (1, 20.1, -5.15), flat(GOLD))
    # barba blanca larga en punta
    box(m, 'head', (-4.6, 14, -6), (4.6, 17.4, -4.4), white)
    box(m, 'head', (-3.4, 11, -6.2), (3.4, 14.2, -4.6), white)
    box(m, 'head', (-2.2, 8.6, -6), (2.2, 11.2, -4.8), white)
    box(m, 'head', (-1, 7.4, -5.8), (1, 8.8, -4.9), white)
    for x in (.8, -4.4):
        box(m, 'head', (x, 16.2, -6.4), (x + 3.6, 17.8, -5.4), white)
    # pelo blanco hacia arriba como llamas, con puntas en rulo
    box(m, 'head', (-5.6, 22.4, -5.6), (5.6, 25.6, 5.6), white)
    for x in (5, -6):
        box(m, 'head', (x, 17, -3), (x + 1, 22.4, 4.6), white)
    for a, b in (((-5.6, 25.6, -3), (-3, 27.6, 0)), ((-2, 25.6, -5), (1, 28, -2.4)), ((3, 25.6, -2.6), (5.6, 27.4, .4)),
                 ((-4, 25.6, 1.4), (-1.4, 28.2, 4.2)), ((1, 25.6, 1.6), (4, 29, 4.4)),
                 ((-1, 28, -4.4), (.2, 29.6, -3.2)), ((-.2, 29.2, -3.8), (1, 30.2, -2.6)),
                 ((2, 29, 2.4), (3.2, 30.8, 3.6)), ((1.2, 30.4, 2.8), (2.4, 31.6, 4))):
        box(m, 'head', a, b, white)
    return m


# ------------------------------------------------------------------ 6. minero (Minas Astrales)
def minero():
    m = rig('astral_npc_minero', arm_r=(24, 0, -14))
    belt3d(m, 6, '#2c2a2e', SILVER)
    RD, RDh, RDd = '#a8483f', '#c05c4c', '#873530'
    lea = cloth(LEATHER, LEATHER_H, LEATHER_D, seed=18)
    legs(m, cloth(LEATHER_D, LEATHER, '#4a2c1e'), cloth(LEATHER, LEATHER_H, LEATHER_D), boot_h=2.5)
    shirt = cloth(RD, RDh, RDd, seed=19, blobs=10)
    box(m, 'body', (-5.2, 2.4, -3.2), (5.2, 6, 3.2), seq(shirt, row(-1, RDd), col_(4, RDh), col_(5, RDh)))
    vest = lambda f: (f.rect(0, 0, 3, f.h, LEATHER), f.rect(f.w - 3, 0, 3, f.h, LEATHER), f.rect(2, 0, 1, f.h, LEATHER_D),
                      f.rect(f.w - 3, 0, 1, f.h, LEATHER_D), f.set(1, 3, LEATHER_H), f.set(f.w - 2, 4, LEATHER_H)) if f.face == 'north' else None
    torso = seq(shirt, col_(4, RDh, 0, 6), on(('south', 'east', 'west'), lea), vest, row(-3, '#2c2a2e'), row(-2, '#3a373d'), buckle(8, SILVER, 2))
    box(m, 'body', (-5, 5, -3), (5, 15, 3), torso)
    for x in (2.4, -5):   # bolsillos del cinturon
        box(m, 'body', (x, 4.6, -3.9), (x + 2.6, 7, -3), seq(lea, row(0, LEATHER_D), px('north', [(1, 1)], SILVER)))
    arms(m, lea, cloth(SKIN, SKIN_H, SKIN_D, blobs=30), cuff=seq(cloth(LEATHER_D, LEATHER), row(0, LEATHER_H)), cuff_h=2.4,
         cap=seq(lea, row(-1, LEATHER_D)), cap_h=2.4)
    for x in (2, -5.2):   # chaleco con volumen
        box(m, 'body', (x, 7.8, -3.5), (x + 3.2, 15.2, -2.9), seq(lea, col_(0 if x > 0 else -1, LEATHER_D)))
    for b, x in (('arm_r', 5), ('arm_l', -8.5)):   # brazo arremangado
        box(m, b, (x - .1, 10.4, -2.1), (x + 3.6, 13.4, 2.1), cloth(SKIN, SKIN_H, SKIN_D, blobs=30))
    pal = face_pal(pupil='#27304f', brow='#5e3820', hair='#6b3f2a')
    F = ["hhhhhhhhhh",
         "hhhhhhhhhh",
         "hSSSSSSSSh",
         "wipSSSSpiw",
         "wppSSSSppw",
         "hSSLLLLSSh",
         "hSSSLLSSSh",
         "SSSSSSSSSS",
         "SSSSnnSSSS",
         "ssssssssss"]
    hair = cloth('#6b3f2a', '#84502f', '#52301f', seed=20, blobs=10)
    head(m, F, pal, hair=seq(hair, lambda f: f.rect(0 if f.face == 'east' else 4, 6, f.w - 4, f.h - 6, SKIN) if f.face in ('east', 'west') else None))
    ears(m)
    nose(m)
    brows(m, '#52301f', y=21.9)
    for x in (4.6, -5.8):   # pelo largo a los costados
        box(m, 'head', (x, 14.4, -4.6), (x + 1.2, 19, 2), hair)
    # casco de cuero con aro de metal y lampara dorada brillante
    rivets = lambda f: [f.set(x, f.h - 1, '#e6e8ee') for x in range(1, f.w, 3)] if f.face in SIDES else None
    cap = seq(cloth(LEATHER, LEATHER_H, LEATHER_D, seed=21, blobs=12), row(-1, IRON), row(-2, IRON_D), rivets)
    box(m, 'head', (-5.6, 22, -5.6), (5.6, 26, 5.6), cap)
    box(m, 'head', (-4.4, 26, -4.4), (4.4, 27, 4.4), cloth(LEATHER, LEATHER_H, LEATHER_D))
    box(m, 'head', (-5.8, 20, 3.6), (5.8, 22.2, 5.8), cloth(LEATHER_D, LEATHER))
    m.bone('lampara', (0, 24, -6), 'head')
    lamp = lambda f: f.rows(["ggYgg", "gYwYg", "YwwwY", "gYwYg", "ggYgg"], {'g': GOLD_D, 'Y': '#ffe27a', 'w': W}) if f.face == 'north' else f.fill(GOLD)
    box(m, 'lampara', (-2.5, 21.6, -6.8), (2.5, 26.6, -5.6), lamp)
    # pico de hierro en la mano derecha
    m.bone('pico', (9.4, 8, -4.6), 'body', rotation=(0, 0, -6))
    staff(m, 'pico', 9.4, -4.6, 1, 16, seq(cloth('#6b4a35', '#84603f', '#523726', blobs=8), wraps('#523726', 4, 2)), w=1.9)
    iron = cloth(IRON, '#c9cbd1', IRON_D, blobs=7)
    box(m, 'pico', (5.6, 14.6, -6), (13.2, 17.4, -3.2), iron)
    box(m, 'pico', (8, 14.2, -6.3), (10.8, 17.8, -2.9), cloth(IRON_D, IRON))
    box(m, 'pico', (3.6, 12.6, -5.8), (6.4, 16.2, -3.4), iron)
    box(m, 'pico', (12.4, 12.6, -5.8), (15.2, 16.2, -3.4), iron)
    box(m, 'pico', (2.2, 9.6, -5.6), (4.4, 13.6, -3.6), iron)
    box(m, 'pico', (14.4, 9.6, -5.6), (16.6, 13.6, -3.6), iron)
    box(m, 'pico', (1.6, 7.6, -5.4), (3, 10, -3.8), cloth('#c9cbd1', W, IRON))
    box(m, 'pico', (15.8, 7.6, -5.4), (17.2, 10, -3.8), cloth('#c9cbd1', W, IRON))
    # mochila con mineral de oro y farol
    box(m, 'body', (-6.4, 6.5, 3), (4.8, 15, 7.8), seq(lea, row(3, LEATHER_D), row(0, LEATHER_H)))
    m.bone('oro', (0, 15, 5), 'body')
    for a, b in (((-7, 15, 3.4), (-3.6, 20, 6.6)), ((-4, 15, 4), (-.4, 23, 7.2)), ((-.8, 15, 3.4), (3, 19, 6.4)), ((-6.4, 19.4, 4.4), (-4, 22.6, 6.6)),
                 ((2.6, 15, 4), (4.6, 17, 6.4))):
        box(m, 'oro', a, b, cloth('#ffcf3a', '#fff0a0', '#e0a020', blobs=5))
    m.bone('farol', (-6, 9, 5.4), 'body')
    box(m, 'farol', (-7.4, 8.4, 4), (-4.6, 9.2, 6.8), flat('#3a3d4a'))
    box(m, 'farol', (-7.2, 5.2, 4.2), (-4.8, 8.4, 6.6), lambda f: (f.fill('#ffb03a'), f.rect(0, 1, f.w, 1, '#ffe08a'), f.rect(0, 0, 1, f.h, '#3a3d4a')))
    box(m, 'farol', (-7.4, 4.6, 4), (-4.6, 5.2, 6.8), flat('#3a3d4a'))
    m.lit = ('lampara', 'farol', 'oro')
    return m


# ------------------------------------------------------------------ 7. caballero (Arenas PvP)
def caballero():
    m = rig('astral_npc_caballero', arm_r=(40, 0, -4))
    belt3d(m, 6, BLACK, GOLD)
    CY, CYh, CYd = '#8fd3d6', '#bdeeee', '#5fa6b0'
    BR, BRh, BRd = '#8a5a3a', '#a4724a', '#6b442c'
    armor = cloth(CY, CYh, CYd, seed=22, blobs=10)
    lea = cloth(BR, BRh, BRd, seed=23)
    legs(m, lea, cloth(BRd, BR, '#523320'), boot_h=2.5)
    box(m, 'body', (-5.3, 3.6, -3.3), (5.3, 7, 3.3), seq(armor, row(-1, CYd), col_(3, CYd), col_(6, CYd)))
    torso = seq(armor, row(0, CYh), row(2, CYd, 1, 9, faces=('north',)), row(4, CYd, 1, 9, faces=('north',)), col_(4, CYh, 0, 6), col_(5, CYd, 0, 6),
                row(-3, BLACK), row(-2, '#2a2730'), buckle(8, GOLD, 2))
    box(m, 'body', (-5, 5, -3), (5, 15, 3), torso)
    for x in (4.8, -9.6):   # hombreras celestes
        box(m, 'body', (x, 12, -3.6), (x + 4.8, 15.8, 3.6), seq(armor, row(-1, CYd), row(0, CYh)))
        box(m, 'body', (x + (1.2 if x < 0 else -.4), 15.8, -2.8), (x + (5.2 if x < 0 else 3.6), 16.8, 2.8), seq(armor, row(0, CYh)))
    arms(m, lea, cloth(BRd, BR), cuff=seq(cloth(BRd, BR), row(0, BRh)), cuff_h=2.6)
    # yelmo con visera: ranura para los ojos y rejilla
    pal = face_pal(pupil='#3a2a22')
    pal.update(A=CY, a=CYd, L=CYh)
    pal.update(x='#2f5a66', s=SKIN_D)
    F = ["LLLLLLLLLLL",
         "AxAxAxAxAxA",
         "AAAAAAAAAAA",
         "aaaaaaaaaaa",
         "asSSSSSSSsa",
         "aSwpSSSpwSa",
         "LLLLLLLLLLL",
         "AAAAAAAAAAA",
         "AAAAAAAAAAA",
         "AAAAAAAAAAA",
         "aaaaaaaaaaa"]
    box(m, 'head', (-5.5, 15, -5.5), (5.5, 25.5, 5.5), seq(armor, row(-1, CYd)), north=lambda f: f.rows(F, pal))
    box(m, 'head', (-5.9, 21.6, -6.3), (5.9, 22.8, -5.5), seq(flat(CYh), row(-1, CY)))                 # ceja de la visera
    box(m, 'body', (-2.2, 2.4, -3.8), (2.2, 6.4, -3.3), seq(armor, row(-1, CYd), col_(2, CYd)))        # faldon central
    box(m, 'body', (-6, 6.2, 2.4), (-3.4, 9.4, 3.8), cloth(BRd, BR))                                    # bolsa del cinturon
    box(m, 'head', (-5.7, 15, -6.4), (5.7, 19.2, -5.5), seq(armor, row(0, CYh), lambda f: [f.rect(x, 1, 1, f.h - 2, '#3d6f7a') for x in (2, 4, 7, 9)] if f.face == 'north' else None))
    box(m, 'head', (-1, 25.5, -5), (1, 26.6, 5.4), flat(CYd))
    # penacho rojo
    plume = cloth('#c23a2e', '#e0553f', '#952822', blobs=7)
    box(m, 'head', (-1.6, 26.4, -2), (1.6, 30, 2.4), plume)
    box(m, 'head', (-1.6, 29, .4), (1.6, 33, 4.6), plume)
    box(m, 'head', (-1.2, 31.6, 3.4), (1.2, 34.6, 6.2), plume)
    # lanza larga roja con cintas
    m.bone('lanza', (6.8, 9, -5.8), 'body')
    shaft = seq(cloth('#a8463a', '#c45c48', '#7f3030', blobs=8), wraps('#7f3030', 7, 3))
    staff(m, 'lanza', 6.8, -5.8, 0, 36, shaft, w=1.1)
    box(m, 'lanza', (5.9, 36, -6.7), (7.7, 37.6, -4.9), flat(CYd))
    box(m, 'lanza', (6.1, 37.6, -6.5), (7.5, 40, -5.1), cloth(CY, CYh, CYd, blobs=5))
    box(m, 'lanza', (6.45, 40, -6.15), (7.15, 42.4, -5.45), flat(CYh))
    rib = cloth('#c23a2e', '#e0553f', '#952822', blobs=6)
    for a, b in (((7.4, 28.5, -6.1), (8.4, 35.6, -5.5)), ((5.2, 30.5, -6.1), (6.2, 35.6, -5.5)), ((8.2, 31, -6.1), (9, 34, -5.5))):
        box(m, 'lanza', a, b, rib)
    return m


# ------------------------------------------------------------------ 8. hechicero rojo (Portales)
def hechicero():
    m = rig('astral_npc_hechicero', arm_r=(42, 0, -4))
    belt3d(m, 6, BLACK, GOLD)
    nose(m, 17.9, z=-5.5, colr='#e6b8a4', w=1.4, h=1.4)
    brows(m, '#3a1820', y=21.2, z=-5.5, w=2.2, gap=.9)
    RD, RDh, RDd = '#b0323a', '#cf4c45', '#8a2434'
    robe = cloth(RD, RDh, RDd, seed=24)
    legs(m, flat('#3a3038'), cloth('#3a3038', '#4c4048', '#2a2228'), boot_h=2)
    box(m, 'body', (-5.6, 3.4, -3.6), (5.6, 6.4, 3.6), seq(robe, col_(5, GOLD)))
    box(m, 'body', (-6.6, .6, -4.6), (6.6, 3.6, 4.6), seq(robe, row(-1, GOLD), row(-2, GOLD_H, faces=('north',)), col_(6, GOLD)))
    torso = seq(robe, col_(3, GOLD, 0, 7), col_(6, GOLD, 0, 7), row(-3, BLACK), row(-2, '#2a2730'), buckle(8, GOLD, 2),
                px('north', [(4, 1), (5, 1), (4, 3), (5, 3), (4, 5), (5, 5)], GOLD_H))
    box(m, 'body', (-5, 5, -3), (5, 15, 3), torso)
    box(m, 'body', (-6.6, 11.6, -4), (6.6, 15.4, 4), seq(robe, row(-1, GOLD)))   # capita con borde dorado
    arms(m, robe, cloth(SKIN, SKIN_H, SKIN_D, blobs=30), cuff=seq(robe, row(-1, GOLD), row(-2, GOLD_D)), cuff_h=3, hw=5.2)
    pal = face_pal()
    pal.update(R=RD, D=RDd, q='#7a2030', P='#f0cdb8', z='#3a1820', p='#3a2a22', m='#c98a78')
    F = ["RRRRRRRRRRR",
         "RRgggggggRR",
         "RgzzzzzzzgR",
         "RgzzzzzzzgR",
         "RgPPPPPPPgR",
         "RgPwpPpwPgR",
         "RgPPPnPPPgR",
         "RggPPmPPggR",
         "RRgggggggRR",
         "DDDDDDDDDDD"]
    hood = cloth(RD, RDh, RDd, seed=25)
    box(m, 'head', (-5.5, 15, -5.5), (5.5, 25.5, 5.5), hood, north=seq(hood, lambda f: f.rows(F, pal)))
    box(m, 'head', (-4.2, 25.5, -3.4), (4.2, 27.4, 5), hood)
    box(m, 'head', (-2.8, 27.4, -1), (2.8, 29.2, 5.6), hood)
    box(m, 'head', (-1.6, 29.2, 1.6), (1.6, 30.8, 6.4), hood)
    box(m, 'head', (-1, 30, 4.6), (1, 31.4, 7.6), hood)
    # baston curvo de madera con gema roja brillante y cinta
    m.bone('baston', (6.8, 9, -5.8), 'body')
    wood = seq(cloth('#9a5a3a', '#b4704a', '#7a4530', blobs=8), wraps(RD, 7, 11), wraps(RDd, 7, 12))
    woodp = cloth('#9a5a3a', '#b4704a', '#7a4530', blobs=8)
    staff(m, 'baston', 6.8, -5.8, 0, 24, wood)
    for a, b in (((6.2, 24, -6.4), (7.4, 31, -5.2)), ((6.2, 31, -6.4), (12.6, 32.2, -5.2)), ((11.4, 26.6, -6.4), (12.6, 31, -5.2)),
                 ((9.4, 25.6, -6.4), (12.6, 26.8, -5.2))):
        box(m, 'baston', a, b, woodp)
    m.bone('gema', (9.4, 29, -5.8), 'baston')
    box(m, 'gema', (7.8, 27, -7), (11.2, 30.6, -4.6), glow('#ff4a4a', W))
    for a, b in (((7.4, 12, -6.1), (8.2, 16.5, -5.5)), ((5.6, 14.5, -6.1), (6.2, 18, -5.5))):
        box(m, 'baston', a, b, flat(RD))
    m.lit = ('gema',)
    return m


# ------------------------------------------------------------------ 9. bruja violeta (Guia de mazmorras)
def bruja():
    m = rig('astral_npc_bruja')
    belt3d(m, 6, BLACK, GOLD)
    nose(m, 16.4, colr='#e8b4a0', w=1.6, h=1.4)
    PU, PUh, PUd = '#6a2a7c', '#8a409c', '#4f1f62'
    TR, TRh = '#f2b06a', '#ffd9a0'
    TQ = '#4fe0c4'
    robe = cloth(PU, PUh, PUd, seed=26)
    strap = seq(row(1, '#e9a85e'), row(3, '#e9a85e'))
    legs(m, flat('#4a2c26'), cloth(WOOD_D, WOOD, '#523024'), boot_h=4.6, strap=strap)
    box(m, 'body', (-6, 3.4, -4), (6, 7, 4), seq(robe, row(-1, TR), col_(5, TR), col_(6, TR)))
    torso = seq(robe, col_(4, TR, 0, 7), col_(5, TR, 0, 7), row(-3, BLACK), row(-2, '#2a2730'), buckle(8, GOLD, 2),
                px('north', [(4, 2), (4, 5)], TRh))
    box(m, 'body', (-5, 5, -3), (5, 15, 3), torso)
    box(m, 'body', (-6.4, 11.4, -3.8), (6.4, 15.4, 3.8), seq(robe, row(-1, TR), col_(4, TR, faces=('north',)), col_(8, TR, faces=('north',))))
    arms(m, robe, cloth(SKIN, SKIN_H, SKIN_D, blobs=30), cuff=seq(robe, row(-1, TR)), cuff_h=3, hw=5.2)
    box(m, 'body', (-5.6, 4, 3), (5.6, 13, 4.2), seq(robe, row(-1, TR)))   # capa
    box(m, 'body', (-1, 13.2, -4.2), (1, 15, -3.7), glow(TR, TRh))        # broche
    pal = face_pal(pupil='#3a2a4a', hair='#2a2430')
    F = ["hhhhhhhhhh",
         "hhSSSSSShh",
         "hSSSSSSSSh",
         "SSSSSSSSSS",
         "SSSSSSSSSS",
         "SSSSSSSSSS",
         "SSSSnnSSSS",
         "SSSSSSSSSS",
         "SSSmmmmSSS",
         "ssssssssss"]
    hair = cloth('#2a2430', '#3d3546', '#1b171f', seed=27, blobs=9)
    head(m, F, pal, hair=hair, skin='#f4c9b4')
    for x in (4.6, -5.8):   # mechones a los costados
        box(m, 'head', (x, 14, -5.4), (x + 1.2, 21, -3.2), hair)
    # lentes redondos turquesa: cristal claro con reflejo y marco fino (las esquinas quedan vacias)
    m.bone('lentes', (0, 19.5, -5.3), 'head')
    lp = {'o': '#e9a85e', 'u': '#7ff2dc', 'U': '#e6fffa', 'v': '#4fd9c2'}

    def lente(f):
        f.fill((0, 0, 0), 0)
        if f.face == 'north':
            f.rows([".ooo.", "ouUUo", "ouuUo", "ovuuo", ".ooo."], lp)
    for x in (.2, -5.2):
        box(m, 'lentes', (x, 17, -5.6), (x + 5, 22, -5.05), lente)
    box(m, 'lentes', (-.8, 19.6, -5.5), (.8, 20.2, -5.1), flat('#e9a85e'))
    # sombrero violeta enorme: ala con borde dorado, banda con gema y punta en rulo
    m.bone('hat', (0, 23.5, 0), 'head', rotation=(-7, 0, 3))
    hat = cloth(PU, PUh, PUd, seed=28, blobs=11)
    brim = lambda f: f.fill(TR) if f.face in SIDES else (hat(f), [f.rect(0, y, f.w, 1, TR) for y in (0, f.h - 1)], [f.rect(x, 0, 1, f.h, TR) for x in (0, f.w - 1)])
    box(m, 'hat', (-10, 23.4, -10), (10, 24.4, 10), brim)
    box(m, 'hat', (-6, 24.4, -6), (6, 27.6, 6), seq(hat, row(-1, TR), row(-2, TRh)))
    box(m, 'hat', (-5, 27.6, -5), (5, 30.6, 5), hat)
    box(m, 'hat', (-4.4, 30.6, -3.4), (3.6, 33.4, 4.6), hat)
    box(m, 'hat', (-4.4, 33.4, -1.2), (1.8, 35.8, 5), hat)
    box(m, 'hat', (-6.4, 35, 1.6), (-1.4, 37.2, 5), hat)
    for a, b in (((-8.6, 36.2, 2.4), (-6, 37.6, 4.2)), ((-9.6, 37, 2.4), (-8.4, 40.4, 4.2)), ((-8.6, 39.6, 2.4), (-5.6, 40.8, 4.2)),
                 ((-6.4, 38.4, 2.4), (-5.4, 40, 4.2)), ((-7.6, 38.2, 2.4), (-6.2, 39, 4.2))):
        box(m, 'hat', a, b, hat)
    m.bone('gema', (0, 26, -6.5), 'hat')
    gem = lambda f: f.rows([".oo.", "oUuo", "ouuo", "ouuo", ".oo."], {'o': TR, 'u': TQ, 'U': '#d2fff6', '.': PU}) if f.face == 'north' else f.fill(TR)
    box(m, 'gema', (-2, 24, -7), (2, 29, -6), gem)
    m.lit = ('gema',)
    return m


NPCS = [mago, herrero, subastas, bazar, cronista, minero, caballero, hechicero, bruja]
REFS = {'astral_npc_mago': 'expediciones', 'astral_npc_herrero': 'herrero', 'astral_npc_subastas': 'subastas',
        'astral_npc_bazar': 'bazar', 'astral_npc_cronista': 'cronista', 'astral_npc_minero': 'minas_astrales',
        'astral_npc_caballero': 'arenas_pvp', 'astral_npc_hechicero': 'portales', 'astral_npc_bruja': 'guia_mazmorras'}
