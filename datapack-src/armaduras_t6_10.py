"""Armaduras tier 6-10 (solo la parte visual): casco 3D + cuerpo "aplastado" sobre la armadura vanilla.

Sin mods, Minecraft solo deja forma propia en el casco (item en la cabeza SIN asset_id, se dibuja su
item_model). Pecho, brazos, piernas y botas usan las cajas fijas de armadura vanilla, asi que aca se
"hornea" el modelo 3D completo sobre esas cajas: para cada cara de cada caja se mira el modelo desde
afuera (proyeccion ortografica) y se pinta lo que se ve de esa parte, incluidas hombreras, tunicas y
faldas. Lo que sobresale se comprime contra el borde de la cara; lo que sobresale demasiado se recorta.

Los modelos son de terceros (mods de Forge en ASTRAL_MODS). TODO lo que sale de aca va al circuito
privado (ASTRAL_PRIVADO/build/entregas/armaduras-t6-10). Nunca a pack-source ni a commits publicos.

Uso (desde la raiz o datapack-src):  python datapack-src/armaduras_t6_10.py [id ...]
Para sumar un set: agregar una linea en SETS.
"""
import json
import os
import shutil
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import armaduras_geo as G  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
MODS = Path(os.environ.get('ASTRAL_MODS', 'C:/Users/Trainx/Desktop/mods'))
PRIV = Path(os.environ.get('ASTRAL_PRIVADO', ROOT / '.local/terceros/AstralRPG-privado'))
OUT = PRIV / 'build/entregas/armaduras-t6-10'
PREVIEW_COPY = ROOT / '.local/armaduras_preview/server_v2'

ARMORY = MODS / 'armory_forge/assets/armory_rpgs'
TERRARIA = MODS / 'armor_terraria/assets/armor_series__terraria'


def armory(tex_id, geo):
    glow = ARMORY / f'textures/armor/{tex_id}_glowmask.png'
    return dict(geo=ARMORY / f'geo/{geo}.geo.json', tex=ARMORY / f'textures/armor/{tex_id}.png',
                glow=glow if glow.exists() else None)


def terraria(geo, tex):
    return dict(geo=TERRARIA / f'geo/{geo}.geo.json', tex=TERRARIA / f'textures/item/{tex}.png', glow=None)


# Mods de la carpeta Revisar (pedido del 14-15/11/2026: T1-T5 y huecos de T6-T10)
REVISAR = Path(os.environ.get('ASTRAL_MODS_REVISAR', MODS / 'Revisar'))


def geckolib(root, geo, tex, overlay=None):
    """Modelo GeckoLib generico: root = carpeta assets/<ns>, tex relativo a textures/."""
    r = REVISAR / root
    glow = r / f'textures/{tex}_glowmask.png'
    return dict(geo=r / f'geo/{geo}.geo.json', tex=r / f'textures/{tex}.png',
                glow=glow if glow.exists() else None,
                overlay=(r / f'textures/{overlay}.png') if overlay else None)


def fantasy(n):
    return geckolib('fantasy armor/assets/fantasy_armor', f'{n}_armor', f'armor/{n}_armor', f'armor/{n}_armor_overlay')


# RPG Style More Weapons (22/11): modelos MCreator compilados, se leen con javap (armaduras_java.py).
MOREWEAPONS = MODS / 'rpg-more-weapons'


def mcreator(clase, letra, mat):
    cm = MOREWEAPONS / 'net/mcreator/rpgstylemoreweaponsr/client/model'
    piezas = [cm / f'ModelN{letra}A{p}.class' for p in ('H', 'B', 'L', 'Boo')]
    return dict(geo=('java', piezas), glow=None, overlay=None,
                tex=MOREWEAPONS / f'assets/rpg_style_more_weapons_r/textures/entities/new{clase}armor{mat}.png')


def paladins(geo, tex):
    return geckolib('paladins-forge-3.1.3+1.20.1/assets/paladins', geo, f'armor/{tex}')


def rogues(geo, tex):
    return geckolib('rogues-forge-3.1.3+1.20.1/assets/rogues', geo, f'armor/{tex}')


def irons(geo, tex, ar=False):
    root = ("new iron spell/Iron's Spells AR v0.1" if ar else 'ireon spell viejo') + '/assets/irons_spellbooks'
    return geckolib(root, geo, f'models/armor/{tex}')


# (id, nombre, clase, tier, origen, ajustes)   <- una linea por set
SETS = [
    ('glacier_robe', 'Glaciar', 'Mago', 6, armory('glacier_robe', 'tirisfal_robe'), {}),
    ('scarlet_robe', 'Escarlata', 'Mago', 7, armory('scarlet_robe', 'tirisfal_robe'), {}),
    ('rimeweave_robe', 'Escarcha', 'Mago', 8, armory('rimeweave_robe', 'tempest_robe'), {}),
    ('nebula', 'Nebulosa', 'Mago', 9, terraria('nebulaarmor', 'nebulaarmor'), {'casco_plano': True}),
    ('absolution_robe', 'Absolucion', 'Mago', 10, armory('absolution_robe', 'absolution_robe'), {}),
    ('lightbringer_armor', 'Portador de Luz', 'Berserker', 7, armory('lightbringer_armor', 'lightbringer_armor'), {}),
    ('onslaught_armor', 'Embestida', 'Berserker', 8, armory('onslaught_armor', 'onslaught_armor'), {}),
    ('justicar_armor', 'Justiciero', 'Berserker', 9, armory('justicar_armor', 'justicar_armor'), {}),
    ('destroyer_armor', 'Destructor', 'Berserker', 10, armory('destroyer_armor', 'destroyer_armor'), {}),
    ('strider_armor', 'Andariego', 'Arquero', 6, armory('strider_armor', 'strider_armor'), {'leg': 'lleg'}),
    ('riftstalker_armor', 'Acechador', 'Arquero', 7, armory('riftstalker_armor', 'riftstalker_armor'), {}),
    ('deathmantle_armor', 'Manto Mortal', 'Arquero', 10, armory('deathmantle_armor', 'deathmantle_armor'), {}),
    # --- 15/11: T1-T5 de las tres clases y huecos (Berserker T6, Arquero T8/T9)
    ('wandering_magician', 'Mago Errante', 'Mago', 1, irons('wandering_magician_armor', 'wandering_magician', ar=True), {}),
    ('netherite_fire_robe', 'Fuego', 'Mago', 2,
     geckolib('wizards-forge-3.1.3+1.20.1/assets/wizards', 'wizard_robes', 'armor/netherite_fire_robe'), {}),
    ('sanguine_purple', 'Sanguina', 'Mago', 3,
     geckolib('anarchyrpg/assets/anarchy_rpg', 'sanguine', 'armor/sanguine_purple'), {'sin_casco': True, 'botas': True}),
    ('pyromancer', 'Piromante', 'Mago', 4, irons('pyromancer_armor', 'pyromancer'), {}),
    ('dark_cover', 'Manto Oscuro', 'Mago', 5, fantasy('dark_cover'), {}),
    ('rogues_berserker', 'Berserker', 'Berserker', 1,
     geckolib('rogues-forge-3.1.3+1.20.1/assets/rogues', 'warrior_armor', 'armor/berserker_armor'), {}),
    ('dead_gladiator', 'Gladiador', 'Berserker', 2, fantasy('dead_gladiator'), {}),
    ('sunset_wings', 'Alas del Atardecer', 'Berserker', 3, fantasy('sunset_wings'), {}),
    ('flesh_of_the_feaster', 'Festin', 'Berserker', 4, fantasy('flesh_of_the_feaster'), {}),
    ('dark_lord', 'Senor Oscuro', 'Berserker', 5, fantasy('dark_lord'), {}),   # A52 con sus colores originales (15/11)
    ('spark_of_dawn', 'Chispa del Alba', 'Berserker', 6, fantasy('spark_of_dawn'), {}),
    ('ranger', 'Explorador', 'Arquero', 1,
     geckolib('archers-forge-3.1.4+1.20.1/assets/archers', 'ranger_armor', 'armor/ranger_armor'), {}),
    ('netherite_ranger', 'Explorador de Netherita', 'Arquero', 2,
     geckolib('archers-forge-3.1.4+1.20.1/assets/archers', 'ranger_armor', 'armor/netherite_ranger_armor'), {}),
    ('anarchy_thief', 'Ladron', 'Arquero', 3,
     geckolib('anarchyrpg/assets/anarchy_rpg', 'thiefmodel', 'armor/thieftexture'), {}),
    ('fantasy_thief', 'Ladron de las Sombras', 'Arquero', 4, fantasy('thief'), {}),
    ('shadowwalker', 'Caminante de Sombras', 'Arquero', 5, irons('shadowwalker_armor', 'shadowwalker'), {}),
    ('forgotten_trace', 'Rastro Olvidado', 'Arquero', 8, fantasy('forgotten_trace'), {}),
    ('cultist', 'Cultista', 'Arquero', 9, irons('cultist_armor', 'cultist'), {'casco_sin_mascara': True}),
    # --- 22/11: clases nuevas (Segador T1/3/5/7/10, Invocador T1/3/5/7/9/10, Asesino T1-T10), elegidas por el dueno
    ('picaro', 'Picaro', 'Segador', 1, rogues('rogue_armor', 'rogue_armor'), {}),
    ('guardia_niebla', 'Guardia de la Niebla', 'Segador', 3, fantasy('fog_guard'), {}),
    ('centinela_tumba', 'Centinela de la Tumba', 'Segador', 5, fantasy('grave_sentinel'), {}),
    ('verdugo_dorado', 'Verdugo Dorado', 'Segador', 7, fantasy('golden_execution'), {'sin_caras': {'armorHead': {0: ['north'], 1: ['north']}}}),
    ('redentor', 'Redentor', 'Segador', 10, fantasy('redeemer'), {}),
    ('prior_oscuro', 'Prior Oscuro', 'Invocador', 1, paladins('priest_robes', 'netherite_prior_robe'), {}),
    ('medico_peste', 'Medico de la Peste', 'Invocador', 3, irons('plagued_armor', 'plagued'), {}),
    ('kintsugi', 'Kintsugi', 'Invocador', 5, geckolib('anarchyrpg/assets/anarchy_rpg', 'kintsugi', 'armor/kintsugi'), {}),
    ('brujo_errante', 'Brujo Errante', 'Invocador', 7, fantasy('wandering_wizard'), {}),
    ('archievocador', 'Archievocador', 'Invocador', 9, irons('archevoker_armor', 'archevoker'), {}),
    ('prior_dorado', 'Prior Dorado', 'Invocador', 10, paladins('priest_robes', 'prior_robe'), {}),
    ('asesino', 'Asesino', 'Asesino', 1, rogues('rogue_armor', 'assassin_armor'), {}),
    ('encapuchado_verde', 'Encapuchado Verde', 'Asesino', 2, mcreator('assassin', 'A', 'iron'), {}),
    ('asesino_netherita', 'Asesino de Netherita', 'Asesino', 3, rogues('rogue_armor', 'netherite_assassin_armor'), {}),
    ('dama_cazadora', 'Dama Cazadora', 'Asesino', 4, fantasy('lady_maria'), {}),
    ('encapuchado_turquesa', 'Encapuchado Turquesa', 'Asesino', 5, mcreator('assassin', 'A', 'diamond'), {}),
    ('encapuchado_dorado', 'Encapuchado Dorado', 'Asesino', 6, mcreator('assassin', 'A', 'netherite'), {}),
    ('fantasma_ocaso', 'Fantasma del Ocaso', 'Asesino', 7, fantasy('evening_ghost'), {}),
    ('ronin', 'Ronin', 'Asesino', 8, fantasy('ronin'), {}),
    ('valquiria', 'Valquiria', 'Asesino', 9, fantasy('malenia'), {'sin_huesos': ['armorBraid']}),
    ('caceria_dorada', 'Caceria Dorada', 'Asesino', 10, fantasy('gilded_hunt'), {}),
]

K = 4                      # resolucion: textura de equipment 64x32 * K
CAP = 4.5                  # lo que sobresale mas que esto de la caja vanilla se recorta
SQUEEZE = 0.4              # fraccion del sobrante que entra en el borde de la cara
GRAZE = 0.3                # caras casi de canto: solo rellenan huecos (si no, salen rayas)
SHRINK = 0.8               # si el modelo es mas angosto que la caja, se estira hasta esto
FILL = 0.9                 # huecos de hasta esto contra el borde de la cara se rellenan
MAX_MARGIN = 1.6           # borde maximo (unidades) para lo que sobresale

# Cajas vanilla en espacio bb (+x derecha del personaje, -z frente). Capa externa (1.0) y leggings (0.5).
def _box(x0, y0, z0, x1, y1, z1, inf):
    return (x0 - inf, y0 - inf, z0 - inf, x1 + inf, y1 + inf, z1 + inf)


BODY_O = _box(-4, 12, -2, 4, 24, 2, 1.0)
ARM_O = _box(4, 12, -2, 8, 24, 2, 1.0)       # brazo derecho (el izquierdo usa la misma textura espejada)
LEG_O = _box(0, 0, -2, 4, 12, 2, 1.0)        # pierna derecha
HEAD_O = _box(-4, 24, -4, 4, 32, 4, 1.0)     # cabeza (solo para cascos planos)
BODY_I = _box(-4, 12, -2, 4, 24, 2, 0.5)
LEG_I = _box(0, 0, -2, 4, 12, 2, 0.5)

# (u, v, ancho, alto, prof) en la textura 64x32 de armadura
UV_BODY, UV_ARM, UV_LEG = (16, 16, 8, 12, 4), (40, 16, 4, 12, 4), (0, 16, 4, 12, 4)
UV_HEAD = (0, 0, 8, 8, 8)

# cara: (eje a, a desde el max?, eje b, b desde el max?, eje profundidad, camara del lado +?)
FACE_SPEC = {
    'front': (0, True, 1, True, 2, False),
    'back': (0, False, 1, True, 2, True),
    'right': (2, True, 1, True, 0, True),
    'left': (2, False, 1, True, 0, False),
    'up': (0, True, 2, True, 1, True),
    'down': (0, True, 2, False, 1, False),
}


def face_rects(u, v, w, h, d):
    return {'right': (u, v + d, d, h), 'front': (u + d, v + d, w, h), 'left': (u + d + w, v + d, d, h),
            'back': (u + 2 * d + w, v + d, w, h), 'up': (u + d, v, w, d), 'down': (u + d + w, v, w, d)}


# ------------------------------------------------------------------------------------- bake plano
class AxisMap:
    """Mapa por eje: coordenada fisica en la caja vanilla -> coordenada del modelo.

    glo/ghi = lo que ocupa el modelo en ese eje. Si el modelo es un poco mas angosto que la caja, se estira
    (hasta SHRINK) para que no queden bordes vacios; si sobresale, el sobrante (hasta CAP) se comprime en un
    borde de la cara y lo demas se recorta.
    """

    def __init__(self, blo, bhi, glo, ghi):
        self.blo, self.bhi = blo, bhi
        self.clo = min(max(glo, blo), blo + SHRINK)        # nucleo del modelo que va al nucleo de la cara
        self.chi = max(min(ghi, bhi), bhi - SHRINK)
        self.wlo = max(min(glo, blo), blo - CAP)
        self.whi = min(max(ghi, bhi), bhi + CAP)
        self.mlo = min(SQUEEZE * (self.clo - self.wlo), MAX_MARGIN)
        self.mhi = min(SQUEEZE * (self.whi - self.chi), MAX_MARGIN)

    def __call__(self, f):
        blo, bhi, mlo, mhi = self.blo, self.bhi, self.mlo, self.mhi
        core0, core1 = blo + mlo, bhi - mhi
        out = self.clo + (f - core0) / (core1 - core0) * (self.chi - self.clo)
        if mlo > 1e-6:
            out = np.where(f < core0, self.wlo + (f - blo) / mlo * (self.clo - self.wlo), out)
        if mhi > 1e-6:
            out = np.where(f > core1, self.chi + (f - core1) / mhi * (self.whi - self.chi), out)
        return out


def part_window(quads, box):
    """Lo que ocupa el modelo de la parte (x0,y0,z0,x1,y1,z1)."""
    if not quads:
        return box
    P = np.concatenate([q[0] for q in quads])
    return tuple(P.min(0)) + tuple(P.max(0))


def raycast_face(quads, tex, face, box, win, wpx, hpx, eff=None):
    """Proyecta los quads sobre una cara. Devuelve (rgba HxWx4, profundidad, etiqueta del quad)."""
    ai, amax, bi, bmax, di, dpos = FACE_SPEC[face]
    eff = eff or box
    amap = AxisMap(eff[ai], eff[3 + ai], win[ai], win[3 + ai])
    bmap = AxisMap(eff[bi], eff[3 + bi], win[bi], win[3 + bi])
    # caras de arriba/abajo: solo lo que esta cerca de esa cara (si no, la hombrera aparece pintada en la mano)
    dl, dh = eff[di], eff[3 + di]
    slab = None
    if face == 'down':
        slab = (-1e9, dl + 0.35 * (dh - dl))
    elif face == 'up':
        slab = (dh - 0.5 * (dh - dl), 1e9)
    fa = (np.arange(wpx) + 0.5) / wpx
    fb = (np.arange(hpx) + 0.5) / hpx
    pa = box[3 + ai] - fa * (box[3 + ai] - box[ai]) if amax else box[ai] + fa * (box[3 + ai] - box[ai])
    pb = box[3 + bi] - fb * (box[3 + bi] - box[bi]) if bmax else box[bi] + fb * (box[3 + bi] - box[bi])
    A, B = np.meshgrid(amap(pa), bmap(pb))           # coordenadas del modelo de cada texel (hpx, wpx)
    th, tw = tex.shape[:2]
    best = np.full((hpx, wpx), -np.inf)               # "cercania" (mayor = mas cerca de la camara)
    rgba = np.zeros((hpx, wpx, 4), np.float32)
    tag = np.full((hpx, wpx), -1, int)
    sign = 1 if dpos else -1
    order = []
    for qi, (pts, uvs, _t) in enumerate(quads):
        n = np.cross(pts[1] - pts[0], pts[3] - pts[0])
        nn = np.linalg.norm(n)
        if nn > 1e-9:
            order.append((abs(n[di]) / nn >= GRAZE, qi))
    filled = np.zeros((hpx, wpx), bool)
    for pas in (True, False):
      for face_on, qi in order:
        if face_on != pas:
            continue
        pts, uvs, _t = quads[qi]
        P0, e1, e2 = pts[0], pts[1] - pts[0], pts[3] - pts[0]
        det = e1[ai] * e2[bi] - e2[ai] * e1[bi]
        if abs(det) < 1e-9:
            continue
        ra, rb = A - P0[ai], B - P0[bi]
        if not pas:
            ra = np.where(filled, np.nan, ra)
        s = (ra * e2[bi] - rb * e2[ai]) / det
        t = (e1[ai] * rb - e1[bi] * ra) / det
        m = (s >= -1e-6) & (s <= 1 + 1e-6) & (t >= -1e-6) & (t <= 1 + 1e-6)
        if not m.any():
            continue
        s, t = np.where(m, s, 0), np.where(m, t, 0)
        depth = sign * (P0[di] + s * e1[di] + t * e2[di])
        if slab:
            m &= (sign * depth >= slab[0]) & (sign * depth <= slab[1])
        m &= depth > best
        if not m.any():
            continue
        u = uvs[0, 0] + s * (uvs[1, 0] - uvs[0, 0]) + t * (uvs[3, 0] - uvs[0, 0])
        v = uvs[0, 1] + s * (uvs[1, 1] - uvs[0, 1]) + t * (uvs[3, 1] - uvs[0, 1])
        tu = np.clip(np.floor(u * tw - 1e-5 * np.sign(uvs[1, 0] - uvs[0, 0] + 1e-12)), 0, tw - 1).astype(int)
        tv = np.clip(np.floor(v * th - 1e-5 * np.sign(uvs[3, 1] - uvs[0, 1] + 1e-12)), 0, th - 1).astype(int)
        tx = tex[tv, tu]
        m &= tx[..., 3] > 0.5
        if not m.any():
            continue
        n = np.cross(e1, e2)
        n /= np.linalg.norm(n)
        shade = 0.72 + 0.28 * abs(n[di])
        best[m] = depth[m]
        rgba[m, :3] = tx[m, :3] * shade
        rgba[m, 3] = 1
        tag[m] = qi
      filled = rgba[..., 3] > 0
    # sombra en los escalones de profundidad: lo que queda "abajo" de una pieza se oscurece un poco
    d = np.where(np.isfinite(best), best, -1e9)
    occl = np.zeros_like(d, bool)
    for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
        nb = np.roll(np.roll(d, dy, 0), dx, 1)
        occl |= (nb - d > 0.8) & (nb > -1e8)
    rgba[occl & (rgba[..., 3] > 0), :3] *= 0.85
    return rgba, best, tag


def dilate_margin(rgba, face, box, win, eff):
    """Rellena con el color vecino los texels transparentes del borde comprimido (evita huecos)."""
    ai, amax, bi, bmax, di, dpos = FACE_SPEC[face]
    out = rgba.copy()
    h, w = out.shape[:2]
    for axis, idx, mx, n in ((1, ai, amax, w), (0, bi, bmax, h)):
        am = AxisMap(eff[idx], eff[3 + idx], win[idx], win[3 + idx])
        size = box[3 + idx] - box[idx]
        lo_px = int(round((am.mlo + eff[idx] - box[idx]) / size * n))
        hi_px = int(round((am.mhi + box[3 + idx] - eff[3 + idx]) / size * n))
        extra = int(round(FILL / size * n))               # el modelo suele ser algo mas chico que la caja
        lo_px, hi_px = lo_px + extra, hi_px + extra
        first, last = (hi_px, lo_px) if mx else (lo_px, hi_px)   # borde al principio / al final del eje
        for _ in range(max(first, last)):
            a = out[..., 3] > 0
            for limit, shift, sl in ((first, -1, slice(0, first)), (last, 1, slice(n - last, n))):
                if limit <= 0:
                    continue
                src, sa = np.roll(out, shift, axis), np.roll(a, shift, axis)
                band = np.zeros_like(a)
                if axis == 1:
                    band[:, sl] = True
                else:
                    band[sl, :] = True
                f = band & ~a & sa
                out[f] = src[f]
    return out


def bake_part(quads, tex, box, uvbox, img, win=None, keep_tags=None, rows=None, dilate=True, eff=None):
    """Pinta las 6 caras de una caja en img (array). keep_tags: funcion(tag_quad) -> bool por texel."""
    win = win or part_window(quads, box)
    eff = eff or box
    clip = [(i, -1e9, eff[i]) for i in range(3) if eff[i] > box[i]] +            [(i, eff[3 + i], 1e9) for i in range(3) if eff[3 + i] < box[3 + i]]
    rects = face_rects(*uvbox)
    done = {}
    for face, (u, v, w, h) in rects.items():
        wpx, hpx = w * K, h * K
        rgba, best, tag = raycast_face(quads, tex, face, box, win, wpx, hpx, eff)
        if keep_tags is not None:
            ok = np.vectorize(lambda t: t >= 0 and keep_tags(quads[t][2]), otypes=[bool])(tag)
            rgba[~ok] = 0
        if dilate:
            rgba = dilate_margin(rgba, face, box, win, eff)
        if rows is not None and face not in ('up', 'down'):
            ylo, yhi = rows                       # solo una franja de alturas (cintura del pantalon)
            ys = box[4] - (np.arange(hpx) + 0.5) / hpx * (box[4] - box[1])
            rgba[~((ys >= ylo) & (ys <= yhi))] = 0
        if rows is not None and face == 'up':
            rgba[:] = 0
        # zonas donde otra caja vanilla queda en el mismo plano: se reparte a la mitad para que no parpadee
        ai, amax, bi, bmax, _d, _p = FACE_SPEC[face]
        for axis, lo, hi in clip:
            if axis == ai:
                fa = (np.arange(wpx) + 0.5) / wpx
                pa = box[3 + ai] - fa * (box[3 + ai] - box[ai]) if amax else box[ai] + fa * (box[3 + ai] - box[ai])
                ha = 0.5 * (box[3 + ai] - box[ai]) / wpx      # el texel que pisa la linea se conserva
                rgba[:, (pa > lo + ha - 1e-6) & (pa < hi - ha + 1e-6)] = 0
            elif axis == bi:
                fb = (np.arange(hpx) + 0.5) / hpx
                pb = box[3 + bi] - fb * (box[3 + bi] - box[bi]) if bmax else box[bi] + fb * (box[3 + bi] - box[bi])
                hb = 0.5 * (box[3 + bi] - box[bi]) / hpx
                rgba[(pb > lo + hb - 1e-6) & (pb < hi - hb + 1e-6)] = 0
        done[face] = rgba
    # tapa de arriba/abajo: si los costados no llegan hasta ese borde (manga corta), no se pinta: quedaria flotando
    sides = ('front', 'back', 'right', 'left')
    if np.mean([done[f][-K // 2:, :, 3].mean() for f in sides]) < 0.5:
        done['down'][:] = 0
    if np.mean([done[f][:K // 2, :, 3].mean() for f in sides]) < 0.5:
        done['up'][:] = 0
    for face, (u, v, w, h) in rects.items():
        img[v * K:(v + h) * K, u * K:(u + w) * K] = done[face]
    return win


def bake(cubes, tex, tex_size, opts):
    """Devuelve (humanoid, humanoid_leggings) como arrays (32K x 64K x 4)."""
    def quads_of(pred):
        out = []
        for c in cubes:
            if pred(c):
                for pts, uvs in G.cube_quads(c, tex_size):
                    out.append((pts, uvs, c['bone']))
        return out

    hum = np.zeros((32 * K, 64 * K, 4), np.float32)
    leg = np.zeros((32 * K, 64 * K, 4), np.float32)
    body = quads_of(lambda c: c['root'] == 'body')
    arm = quads_of(lambda c: c['root'] == opts.get('arm', 'rarm'))
    legq = quads_of(lambda c: c['root'] == opts.get('leg', 'rleg'))
    waist = quads_of(lambda c: c['root'] == 'waist')   # faldones/sacos colgados de la cintura (Sanguina)
    if waist:
        body = body + waist
        legq = legq + waist
    if opts.get('arm', 'rarm') == 'larm':           # usar el brazo izquierdo espejado
        arm = [(p * np.array([-1, 1, 1]), u, t) for p, u, t in arm]
    if opts.get('leg', 'rleg') == 'lleg':
        legq = [(p * np.array([-1, 1, 1]), u, t) for p, u, t in legq]
    is_boot = lambda bone: 'boot' in bone.lower() or bone.lower() in opts.get('boot_bones', ())
    # caja "efectiva": donde dos cajas vanilla se pisan en el mismo plano, cada una pinta su mitad
    e_body, e_arm, e_leg = _eff(BODY_O, x0=-4, x1=4, y0=12), _eff(ARM_O, x0=4), _eff(LEG_O, x0=0, y1=12)
    bake_part(body, tex, BODY_O, UV_BODY, hum, eff=e_body)
    bake_part(arm, tex, ARM_O, UV_ARM, hum, eff=e_arm)
    win = bake_part(legq, tex, LEG_O, UV_LEG, hum, keep_tags=is_boot, eff=e_leg)
    # pantalon: todo lo de la pierna que no es bota (falda incluida)
    leg_noboot = [q for q in legq if not is_boot(q[2])]
    bake_part(leg_noboot, tex, LEG_I, UV_LEG, leg, win=win, eff=_eff(LEG_I, x0=0, y1=12))
    bake_part(body, tex, BODY_I, UV_BODY, leg, rows=(12, 15.5), dilate=False, eff=_eff(BODY_I, y0=12))
    if opts.get('casco_plano'):   # la capucha/casco se pega a la cabeza (textura plana, sin modelo 3D aparte)
        head = quads_of(lambda c: c['root'] == 'head')
        bake_part(head, tex, HEAD_O, UV_HEAD, hum, eff=_eff(HEAD_O, y0=24))
    return hum, leg


def _eff(box, x0=None, x1=None, y0=None, y1=None):
    b = list(box)
    for i, v in ((0, x0), (3, x1), (1, y0), (4, y1)):
        if v is not None:
            b[i] = v
    return tuple(b)


def to_img(a):
    a = a.copy()
    a[a[..., 3] < 0.5] = 0
    a[..., 3] = (a[..., 3] >= 0.5)
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8), 'RGBA')


# ------------------------------------------------------------------------------------- casco 3D
HEAD_C = np.array([0, 28, 0])
PX = 1.6   # unidades de modelo de item por pixel de cabeza


def helmet_model(cubes, tex_name, tex_size):
    """Modelo de item Java (26.1: rotacion libre x/y/z) con los huesos de la cabeza."""
    elems = []
    tw, th = tex_size
    for c in cubes:
        if c['root'] != 'head':
            continue
        x0, y0, z0, x1, y1, z1 = c['box']
        lo, hi = np.array([x0, y0, z0]), np.array([x1, y1, z1])
        ctr = (lo + hi) / 2
        R, t = c['R'], c['t']
        wc = R @ ctr + t                              # centro final
        half = (hi - lo) / 2
        faces = {}
        for k, (u, v, w, h) in c['faces'].items():
            if w == 0 or h == 0:
                continue
            q = 16 / tw, 16 / th
            if k in ('up', 'down'):
                uv = [(u + w) * q[0], (v + h) * q[1], u * q[0], v * q[1]]
            else:
                uv = [u * q[0], v * q[1], (u + w) * q[0], (v + h) * q[1]]
            faces[k] = {'uv': [round(x, 4) for x in uv], 'texture': '#t'}
        if not faces:
            continue
        e = {'from': list(wc - half), 'to': list(wc + half), 'faces': faces, '_R': R, '_c': wc}
        elems.append(e)
    # a coordenadas de item: centro de la cabeza = (8, 8, 8), 1 pixel = 1.6
    pts = []
    for e in elems:
        pts += [e['from'], e['to']]
    pts = (np.array(pts) - HEAD_C) * PX + 8 if pts else np.zeros((1, 3))
    span = max(pts.max() - 8, 8 - pts.min(), 1e-9)
    scale = min(1.0, 23.9 / span)                     # elementos dentro de -16..32
    out = []
    for e in elems:
        f = (np.array(e['from']) - HEAD_C) * PX * scale + 8
        to = (np.array(e['to']) - HEAD_C) * PX * scale + 8
        o = (e['_c'] - HEAD_C) * PX * scale + 8
        el = {'from': [round(x, 4) for x in f], 'to': [round(x, 4) for x in to], 'faces': e['faces']}
        rx, ry, rz = G.euler_zyx(e['_R'])
        if max(abs(rx), abs(ry), abs(rz)) > 1e-3:
            el['rotation'] = {'origin': [round(x, 4) for x in o], 'x': round(rx, 3), 'y': round(ry, 3), 'z': round(rz, 3)}
        out.append(el)
    disp = {'head': {'rotation': [0, 0, 0], 'translation': [0, 0, 0], 'scale': [round(1 / scale, 4)] * 3}}
    return {'textures': {'t': tex_name, 'particle': tex_name}, 'elements': out, 'display': disp}


def helmet_quads(model, tex_size_px):
    """Decodifica el modelo Java a quads en espacio bb (para la vista previa del server)."""
    q = []
    sc = model['display']['head']['scale'][0]
    tr = np.array(model['display']['head']['translation'])
    for el in model['elements']:
        f, t = np.array(el['from']), np.array(el['to'])
        fc = G.face_corners(*f, *t)
        if 'rotation' in el:
            r = el['rotation']
            R = G.rot_matrix(r['x'], r['y'], r['z'])
            o = np.array(r['origin'])
        else:
            R, o = np.eye(3), np.zeros(3)
        for k, fd in el['faces'].items():
            U0, V0, U1, V1 = [x / 16 for x in fd['uv']]
            if k in ('up', 'down'):
                U0, V0, U1, V1 = U1, V1, U0, V0
            pts = (np.array(fc[k], float) - o) @ R.T + o
            pts = ((pts - 8) * sc + tr) / PX + HEAD_C
            q.append((pts, np.array([(U0, V0), (U1, V0), (U1, V1), (U0, V1)])))
    return q


# ------------------------------------------------------------------------------------- vista previa
def vanilla_geo():
    """Cajas de armadura vanilla como geo (para renderizar el resultado real)."""
    def cube(o, s, uv, inf, mirror=False):
        return {'origin': o, 'size': s, 'uv': uv, 'inflate': inf, 'mirror': mirror}
    hum = {'description': {'texture_width': 64, 'texture_height': 32}, 'bones': [
        {'name': 'h', 'cubes': [cube([-4, 24, -4], [8, 8, 8], [0, 0], 1.0)]},
        {'name': 'b', 'cubes': [cube([-4, 12, -2], [8, 12, 4], [16, 16], 1.0)]},
        {'name': 'ra', 'cubes': [cube([-8, 12, -2], [4, 12, 4], [40, 16], 1.0)]},
        {'name': 'la', 'cubes': [cube([4, 12, -2], [4, 12, 4], [40, 16], 1.0, True)]},
        {'name': 'rl', 'cubes': [cube([-4, 0, -2], [4, 12, 4], [0, 16], 1.0)]},
        {'name': 'll', 'cubes': [cube([0, 0, -2], [4, 12, 4], [0, 16], 1.0, True)]},
    ]}
    leg = {'description': {'texture_width': 64, 'texture_height': 32}, 'bones': [
        {'name': 'b', 'cubes': [cube([-4, 12, -2], [8, 12, 4], [16, 16], 0.5)]},
        {'name': 'rl', 'cubes': [cube([-4, 0, -2], [4, 12, 4], [0, 16], 0.5)]},
        {'name': 'll', 'cubes': [cube([0, 0, -2], [4, 12, 4], [0, 16], 0.5, True)]},
    ]}
    return G.geo_quads(hum), G.geo_quads(leg)


def preview(sid, name, geo, tex, hum_img, leg_img, helm, helm_tex):
    mq, mt = G.mannequin()
    mod_q = G.geo_quads(geo)
    hq, lq = vanilla_geo()
    ht = np.asarray(hum_img, np.float32) / 255
    lt = np.asarray(leg_img, np.float32) / 255
    hm = helmet_quads(helm, None)
    mod_layers = [(mq, mt), (mod_q, tex)]
    srv_layers = [(mq, mt), (lq, lt), (hq, ht), (hm, helm_tex)]
    ims = [G.render(mod_layers, 25), G.render(srv_layers, 25), G.render(mod_layers, 205), G.render(srv_layers, 205)]
    w, h = ims[0].size
    sheet = Image.new('RGBA', (w * 4, h), (0, 0, 0, 0))
    for i, im in enumerate(ims):
        sheet.paste(im, (i * w, 0), im)
    bb = sheet.getbbox()
    sheet = sheet.crop((0, max(0, bb[1] - 10), w * 4, min(h, bb[3] + 10)))
    bg = Image.new('RGBA', (sheet.width, sheet.height + 40), (236, 238, 242, 255))
    bg.paste(sheet, (0, 40), sheet)
    d = ImageDraw.Draw(bg)
    try:
        font = ImageFont.truetype('arial.ttf', 22)
    except OSError:
        font = ImageFont.load_default()
    for i, lab in enumerate(('Mod - frente', 'Server - frente', 'Mod - espalda', 'Server - espalda')):
        d.text((i * w + 20, 8), f'{name}: {lab}' if i == 0 else lab, fill=(30, 30, 40), font=font)
    for i in range(1, 4):
        d.line([(i * w, 0), (i * w, bg.height)], fill=(200, 200, 210), width=2)
    return bg


def tinte_rojo(tex):
    """Lleva la armadura a tonos rojos (pedido del dueno para el Berserker T5): conserva la luz de cada pixel."""
    rgb = tex[..., :3]
    lum = rgb @ np.array([0.299, 0.587, 0.114])
    sat = rgb.max(-1) - rgb.min(-1)
    # rampa roja: negro -> rojo sangre -> rojo vivo -> rosado claro
    ramp = np.array([[0.05, 0.01, 0.01], [0.42, 0.04, 0.05], [0.80, 0.12, 0.10], [1.0, 0.62, 0.55]])
    x = np.clip(lum * 1.15, 0, 1) * (len(ramp) - 1)
    i = np.clip(np.floor(x).astype(int), 0, len(ramp) - 2)
    f = (x - i)[..., None]
    red = ramp[i] * (1 - f) + ramp[i + 1] * f
    # los metales claros y dorados quedan algo mas cerca del original para no perder el detalle
    keep = np.clip((lum - 0.75) * 2, 0, 0.5)[..., None] * (sat[..., None] < 0.15)
    out = tex.copy()
    out[..., :3] = red * (1 - keep) + rgb * keep
    return out


# Botas pintadas (15/11/2026): modelos sin pies (Sanguina) dejaban la zona de las botas vacia y se veian invisibles.
BOTAS_COLORES = ((42, 24, 56), (59, 33, 80), (184, 134, 46))   # violeta oscuro, violeta, dorado (de la tunica)


def pintar_botas(img, k=None, colores=BOTAS_COLORES):
    """Pinta botas en la zona de las piernas de la capa `humanoid` (textura 64x32 * k) si esta vacia:
    4 pixeles de abajo de cada cara de la pierna, una linea dorada arriba y la suela."""
    k = k or img.width // 64
    img = img.copy()
    px = img.load()
    oscuro, medio, oro = colores

    def rect(u0, v0, u1, v1, color_fn):
        for v in range(v0 * k, v1 * k):
            for u in range(u0 * k, u1 * k):
                if px[u, v][3] == 0:
                    c = color_fn(u // k, v // k)
                    px[u, v] = (*c, 255)
    tono = lambda u, v: medio if (u + v) % 3 == 0 else oscuro
    for u0 in (0, 4, 8, 12):                         # derecha, frente, izquierda, atras
        rect(u0, 28, u0 + 4, 32, tono)
        rect(u0, 27, u0 + 4, 28, lambda u, v: oro)
    rect(8, 16, 12, 20, lambda u, v: oscuro)          # suela
    return img


# ------------------------------------------------------------------------------------- main
def cargar_geo(ref):
    if isinstance(ref, tuple) and ref[0] == 'java':
        import armaduras_java
        return armaduras_java.to_geo([str(p) for p in ref[1]])
    return G.load_geo(ref)


def quitar(geo, opts):
    """Saca huesos enteros (con sus hijos) y cubos sueltos que el dueno no quiere (pelo, mascaras)."""
    fuera = set(opts.get('sin_huesos', ()))
    cambio = True
    while cambio:
        cambio = False
        for b in geo['bones']:
            if b['name'] not in fuera and b.get('parent') in fuera:
                fuera.add(b['name'])
                cambio = True
    bones = []
    for b in geo['bones']:
        b = dict(b)
        if b['name'] in fuera:
            b['cubes'] = []
        caras = opts.get('sin_caras', {}).get(b['name'], {})
        if caras:   # caras sueltas de un cubo (ej. el frente de la capucha): se pasa la UV a una por cara
            cs = []
            for i, c in enumerate(b.get('cubes', [])):
                if i in caras and not isinstance(c.get('uv'), dict):
                    s = c['size']
                    f = G.box_uv(c['uv'][0], c['uv'][1], s[0], s[1], s[2], c.get('mirror', False))
                    c = dict(c, uv={k: {'uv': [u, v], 'uv_size': [w, h]} for k, (u, v, w, h) in f.items()
                                    if k not in caras[i]})
                cs.append(c)
            b['cubes'] = cs
        idx = opts.get('sin_cubos', {}).get(b['name'])
        if idx:
            b['cubes'] = [c for i, c in enumerate(b.get('cubes', [])) if i not in idx]
        bones.append(b)
    return dict(geo, bones=bones)


def build(sid, name, cls, tier, src, opts):
    geo = quitar(cargar_geo(src['geo']), opts)
    d = geo['description']
    tex_size = (d.get('texture_width', 64), d.get('texture_height', 64))
    tex = G.load_tex(src['tex'], src['glow'])
    if src.get('overlay') and src['overlay'].exists():
        ov = G.load_tex(src['overlay'])
        if ov.shape == tex.shape:
            a = ov[..., 3:4]
            tex = tex.copy()
            tex[..., :3] = ov[..., :3] * a + tex[..., :3] * (1 - a)
            tex[..., 3] = np.maximum(tex[..., 3], ov[..., 3])
    if opts.get('tint') == 'rojo':
        tex = tinte_rojo(tex)
    cubes = G.collect_cubes(geo)
    if opts.get('sin_casco'):
        cubes = [c for c in cubes if c['root'] != 'head']
    casco_sin = set(opts.get('casco_sin', ()))
    helm_cubes = [c for c in cubes if not (c['root'] == 'head' and c['bone'] in casco_sin)]
    if opts.get('casco_sin_mascara'):   # Cultista: sin la mascara de calavera (cubo con una sola cara), se ve la cara
        helm_cubes = [c for c in helm_cubes if not (c['root'] == 'head' and len(c['faces']) == 1)]
    hum, leg = bake(cubes, tex, tex_size, opts)
    hum_img, leg_img = to_img(hum), to_img(leg)
    if opts.get('botas'):
        hum_img = pintar_botas(hum_img, K)
    key = f'armadura_{sid}'
    tex_name = f'astral:item/{key}_casco'
    helm = helmet_model(helm_cubes, tex_name, tex_size)
    pack = OUT / 'pack/assets/astral'
    for sub in ('textures/entity/equipment/humanoid', 'textures/entity/equipment/humanoid_leggings',
                'textures/item', 'models/item', 'equipment'):
        (pack / sub).mkdir(parents=True, exist_ok=True)
    hum_img.save(pack / f'textures/entity/equipment/humanoid/{key}.png')
    leg_img.save(pack / f'textures/entity/equipment/humanoid_leggings/{key}.png')
    Image.fromarray((tex * 255).astype(np.uint8), 'RGBA').save(pack / f'textures/item/{key}_casco.png')
    json.dump(helm, open(pack / f'models/item/{key}_casco_3d.json', 'w'), indent=1)
    json.dump({'layers': {'humanoid': [{'texture': f'astral:{key}'}],
                          'humanoid_leggings': [{'texture': f'astral:{key}'}]}},
              open(pack / f'equipment/{key}.json', 'w'), indent=1)
    pv = preview(sid, name, geo, tex, hum_img, leg_img, helm, tex)
    (OUT / 'previews').mkdir(parents=True, exist_ok=True)
    pv.save(OUT / f'previews/{sid}.png')
    return pv


def main(argv):
    if not MODS.exists():
        print('No encuentro los mods originales en', MODS, '(ASTRAL_MODS)')
        return 1
    if not PRIV.exists():
        print('Sin circuito privado (ASTRAL_PRIVADO): no se genera nada.')
        return 1
    only = set(argv)
    sheets = []
    for sid, name, cls, tier, src, opts in SETS:
        if only and sid not in only:
            continue
        pv = build(sid, name, cls, tier, src, opts)
        sheets.append(pv)
        print('ok', sid)
    if not only:
        sc = 0.5
        ims = [s.resize((int(s.width * sc), int(s.height * sc)), Image.LANCZOS) for s in sheets]
        wmax = max(i.width for i in ims)
        cols = 2
        rows = (len(ims) + cols - 1) // cols
        hrow = max(i.height for i in ims)
        hoja = Image.new('RGBA', (wmax * cols, hrow * rows), (236, 238, 242, 255))
        for i, im in enumerate(ims):
            hoja.paste(im, ((i % cols) * wmax, (i // cols) * hrow), im)
        hoja.save(OUT / 'previews/hoja.png')
    PREVIEW_COPY.mkdir(parents=True, exist_ok=True)
    for f in (OUT / 'previews').glob('*.png'):
        shutil.copy(f, PREVIEW_COPY / f.name)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
