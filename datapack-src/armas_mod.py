"""Armas elegidas por el dueno (15/11/2026): T6-T10 de cada familia, guante nuevo y tres ballestas.

El arte es de mods de terceros (ASTRAL_MODS_REVISAR). TODO lo que sale de aca va al circuito privado
(ASTRAL_PRIVADO/build/entregas/armas-mod). Nunca a pack-source ni a commits publicos (docs/TERCEROS.md).

Tres caminos segun lo que trae el mod:
- "plano": el mod solo tiene un icono. Se esculpe en 3D como las armas propias: el arma queda derecha
  (parada en x=8, z=8), los mangos salen redondos, los orbes y cristales con volumen real y las hojas con
  lomo grueso y filo fino. El dibujo del mod se usa como textura. Lo que brilla en el mod (textura _e) queda
  con luz propia y las texturas animadas (.mcmeta) siguen animadas.
- "java": el mod ya trae un modelo 3D de bloques (json con elements). Se copia tal cual.
- "geo": el mod trae un modelo 3D de GeckoLib / Bedrock (.geo.json). Se convierte a modelo de item 26.1
  (rotacion libre x/y/z), sin tocar las piezas.
En el inventario siempre se ve el icono plano del mod.

Uso (desde la raiz):
  python datapack-src/armas_mod.py            modelos + vista previa + pack FINAL
  python datapack-src/armas_mod.py --sin-pack solo modelos y vista previa
Requiere antes `python build_pack.py pack-source` (para el FINAL).
"""
import hashlib
import io
import json
import math
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import armaduras_geo as G  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
MODS = Path(os.environ.get('ASTRAL_MODS_REVISAR', 'C:/Users/Trainx/Desktop/mods/Revisar'))
PRIV = Path(os.environ.get('ASTRAL_PRIVADO', ROOT / '.local/terceros/AstralRPG-privado'))
OUT = PRIV / 'build/entregas/armas-mod'
PACK = OUT / 'pack'
BASE = PRIV / 'build/entregas/tiers6-10/AstralRPG-Textures.zip'
STAMP = (2026, 11, 15, 0, 0, 0)
TEX = 'item/armas_mod'

NS_DIR = {
    'wizards': 'wizards-forge-3.1.3+1.20.1', 'mcdw': 'mcdw-9.0.4', 'rogues': 'rogues-forge-3.1.3+1.20.1',
    'archers': 'archers-forge-3.1.4+1.20.1', 'born_in_chaos_v1': 'born in chaos',
    'irons_spellbooks': 'ireon spell viejo', 'forcemaster_rpg': 'forcemaster_rpg-forge-3.1.2+1.20.1',
}
BIC = 'born_in_chaos_v1'

# ------------------------------------------------------------------------------------- que arma es cual
# plano: (camino, modelo del mod)                      -> se recrea con volumen
# java:  (camino, modelo 3D, textura, icono)           -> se copia
# geo:   (camino, geo, textura, icono, display)        -> se convierte
ARMAS = {
    'baston_6': ('plano', 'wizards:item/staff_arcane'),
    'baston_7': ('plano', 'wizards:item/staff_fire'),
    'baston_8': ('plano', 'wizards:item/aether_wizard_staff'),
    'baston_9': ('geo', f'{BIC}:geo/staffmagicarrows', f'{BIC}:item/staffmagicarrows',
                 f'{BIC}:item/staff_of_magic_arrows_item', f'{BIC}:displaysettings/staffmagicarrows.item'),
    'baston_10': ('geo', f'{BIC}:geo/bonescallerstaff', f'{BIC}:item/bonescallerstaff',
                 f'{BIC}:item/bonescaller_staff_item', f'{BIC}:displaysettings/bonescallerstaff.item'),
    'espada_6': ('plano', 'mcdw:item/sword_sinister'),
    'espada_7': ('plano', f'{BIC}:item/dark_ritual_dagger'),
    'espada_8': ('plano', None, f'{BIC}:item/spiritsword'),
    'espada_9': ('plano', 'mcdw:item/sword_obsidian_claymore'),
    'espada_10': ('plano', 'mcdw:item/sword_the_starless_night'),
    'hacha_6': ('plano', 'rogues:item/aeternium_double_axe'),
    'hacha_7': ('plano', 'mcdw:item/double_axe_whirlwind'),
    'hacha_8': ('plano', 'rogues:item/aether_double_axe'),
    'hacha_9': ('plano', 'mcdw:item/axe_firebrand'),
    'hacha_10': ('java', f'{BIC}:custom/executionersgreatax', f'{BIC}:block/executionersgreatax',
                 f'{BIC}:item/great_reaper_axe'),
    'guadana_6': ('plano', 'mcdw:item/scythe_jailors_scythe'),
    'guadana_7': ('plano', 'mcdw:item/scythe_skull_scythe'),
    'guadana_8': ('plano', 'irons_spellbooks:item/stone_scythe'),
    'guadana_9': ('plano', 'mcdw:item/scythe_frost_scythe'),
    'guadana_10': ('java', f'{BIC}:custom/nightmarescythe', f'{BIC}:block/nightmarescythe',
                   f'{BIC}:item/nightmare_scythe'),
    'arco_6': ('arco', 'mcdw:item/bow_lost_souls'),
    'arco_7': ('arco', 'mcdw:item/bow_burst_gale_bow'),
    'arco_8': ('arco', 'mcdw:item/bow_echo_of_the_valley'),
    'arco_9': ('arco', 'mcdw:item/bow_bubble_burster'),
    'arco_10': ('arco', 'mcdw:item/bow_haunted_bow'),
    'lanza_6': ('plano', 'mcdw:item/spear_fortune'),
    'lanza_7': ('varatha', 'hades_aspect'),
    'lanza_8': ('varatha', 'zagreus_aspect'),
    'lanza_9': ('varatha', 'achilles_aspect'),
    'lanza_10': ('varatha', 'guanyu_aspect'),
    'guantes_meteoro': ('java', 'forcemaster_rpg:item/ruby_knuckle_model', 'forcemaster_rpg:item/ruby_knuckle_texture',
                        'forcemaster_rpg:item/ruby_knuckle_inventory'),
    'ballesta_3': ('ballesta', 'archers:item/aether_heavy_crossbow'),
    'ballesta_4': ('ballesta', 'archers:item/netherite_rapid_crossbow'),
    'ballesta_5': ('ballesta', 'archers:item/aether_rapid_crossbow'),
}
# Reservado: completar solo cuando el dueno elija los modelos. None conserva el PNG provisorio.
PENDIENTES = {f'cuchillo_{t}': None for t in range(1,11)}
ARMAS.update({iid: spec for iid,spec in PENDIENTES.items() if spec is not None})
# Ajuste de tamano en la mano respecto del mod (la guadana de piedra venia gigante).
ESCALA = {'guadana_8': 0.67, 'lanza_6': 1.25}
NOMBRES = {'cuchillo': 'Cuchillo', 'baston': 'Baston', 'espada': 'Espada', 'hacha': 'Hacha', 'guadana': 'Guadana', 'arco': 'Arco',
           'lanza': 'Lanza', 'ballesta': 'Ballesta', 'guantes': 'Guantes'}

# Como agarra vanilla cada tipo de item (lo que heredan los modelos de los mods).
_FP = {'firstperson_righthand': {'rotation': [0, -90, 25], 'translation': [1.13, 3.2, 1.13], 'scale': [0.68] * 3},
       'firstperson_lefthand': {'rotation': [0, 90, -25], 'translation': [1.13, 3.2, 1.13], 'scale': [0.68] * 3}}
VANILLA = {
    'item/generated': dict(_FP, **{
        'ground': {'rotation': [0, 0, 0], 'translation': [0, 2, 0], 'scale': [0.5] * 3},
        'head': {'rotation': [0, 180, 0], 'translation': [0, 13, 7], 'scale': [1] * 3},
        'thirdperson_righthand': {'rotation': [0, 0, 0], 'translation': [0, 3, 1], 'scale': [0.55] * 3},
        'thirdperson_lefthand': {'rotation': [0, 0, 0], 'translation': [0, 3, 1], 'scale': [0.55] * 3},
        'fixed': {'rotation': [0, 180, 0], 'scale': [1] * 3}}),
}
VANILLA['item/handheld'] = dict(VANILLA['item/generated'], **{
    'thirdperson_righthand': {'rotation': [0, -90, 55], 'translation': [0, 4, 0.5], 'scale': [0.85] * 3},
    'thirdperson_lefthand': {'rotation': [0, 90, -55], 'translation': [0, 4, 0.5], 'scale': [0.85] * 3}})
VANILLA['item/bow'] = dict(VANILLA['item/generated'], **{
    'thirdperson_righthand': {'rotation': [-80, 260, -40], 'translation': [-1, -2, 2.5], 'scale': [0.9] * 3},
    'thirdperson_lefthand': {'rotation': [-80, -280, 40], 'translation': [-1, -2, 2.5], 'scale': [0.9] * 3}})
VANILLA['item/crossbow'] = dict(VANILLA['item/generated'], **{
    'thirdperson_righthand': {'rotation': [-90, 0, -60], 'translation': [2, 0.1, -3], 'scale': [0.9] * 3},
    'thirdperson_lefthand': {'rotation': [-90, 0, 30], 'translation': [2, 0.1, -3], 'scale': [0.9] * 3},
    'firstperson_righthand': {'rotation': [-90, 0, -55], 'translation': [1.13, 3.2, 1.13], 'scale': [0.68] * 3},
    'firstperson_lefthand': {'rotation': [-90, 0, 35], 'translation': [1.13, 3.2, 1.13], 'scale': [0.68] * 3}})
# Modelo parado (x=8, z=8): mismo agarre que las armas 3D propias (varitas3d.display).
PARADO = {
    'thirdperson_righthand': {'rotation': [0, -90, 10], 'translation': [0, 4, 0.5], 'scale': [0.85] * 3},
    'thirdperson_lefthand': {'rotation': [0, 90, -10], 'translation': [0, 4, 0.5], 'scale': [0.85] * 3},
    'firstperson_righthand': {'rotation': [0, -90, -20], 'translation': [1.13, 3.2, 1.13], 'scale': [0.68] * 3},
    'firstperson_lefthand': {'rotation': [0, 90, 20], 'translation': [1.13, 3.2, 1.13], 'scale': [0.68] * 3},
    'head': {'rotation': [0, 0, -45], 'translation': [0, 10, 0], 'scale': [0.8] * 3},
}

ALFA = 40                     # menos que esto es transparente


# ------------------------------------------------------------------------------------- lectura de mods
def ruta(ref, kind, ext):
    ns, _, path = ref.partition(':')
    return MODS / NS_DIR[ns] / 'assets' / ns / kind / (path + ext)


def cargar_modelo(ref):
    if ':' not in ref:
        ref = 'minecraft:' + ref
    ns, _, path = ref.partition(':')
    if ns == 'minecraft':
        if path in VANILLA:
            return {'display': VANILLA[path]}
        if path.startswith('builtin/'):
            return {}
        raise SystemExit(f'modelo vanilla sin datos: {ref}')
    return json.loads(ruta(ref, 'models', '.json').read_text(encoding='utf-8'))


def resolver(ref):
    """Sigue la cadena de parents: devuelve (display final, texturas finales)."""
    chain = []
    while ref:
        m = cargar_modelo(ref)
        chain.append(m)
        ref = m.get('parent')
    disp, tex = {}, {}
    for m in reversed(chain):
        for k, v in m.get('display', {}).items():
            disp[k] = dict(v)
        tex.update(m.get('textures', {}))
    return disp, tex


def _png(im):
    b = io.BytesIO()
    im.save(b, 'PNG')
    return b.getvalue()


def js(d):
    return (json.dumps(d, ensure_ascii=False, separators=(',', ':')) + '\n').encode('utf-8')


def leer_textura(ref):
    """Textura del mod con su brillo (_e) encima. Devuelve (imagen, mascara de brillo o None, mcmeta o None)."""
    p = ruta(ref, 'textures', '.png')
    im = Image.open(p).convert('RGBA')
    glow = None
    e = ruta(ref + '_e', 'textures', '.png')
    if e.exists():
        ge = Image.open(e).convert('RGBA')
        if ge.size == im.size:
            im.alpha_composite(ge)
            glow = np.asarray(ge)[..., 3] > ALFA
    meta = Path(str(p) + '.mcmeta')
    mc = None
    if meta.exists():
        anim = json.loads(meta.read_text(encoding='utf-8')).get('animation', {})
        mc = {'animation': {k: anim[k] for k in ('frametime', 'interpolate', 'frames') if k in anim}}
    return im, glow, mc


# ------------------------------------------------------------------------------------- icono -> escultura
SS = 4                        # muestras por pixel del icono al enderezarlo
CELDA = 2                     # muestras por celda de la escultura (2 = medio pixel del icono)
NIVELES = [0.5, 0.8, 1.15, 1.5, 2.0, 2.6, 3.3, 4.1, 5.0]   # medio grosor de cada capa, en pixeles del icono
ROD = 1.5                     # hasta este radio la pieza es redonda (mangos, astas, cuerdas)


def _familia(name):
    return name.split('_')[0]


def _grosor_max(R, fam):
    """Medio grosor en el centro de una pieza de radio R (pixeles del icono)."""
    if fam == 'baston':                     # orbes, cristales y adornos: casi esfericos
        return np.where(R <= ROD, R, np.minimum(ROD + (R - ROD) * 0.85, NIVELES[-1]))
    if fam in ('arco', 'ballesta'):         # palas y cuerpo: tablas gruesas
        return np.where(R <= ROD, R, np.minimum(ROD + (R - ROD) * 0.25, 2.2))
    # hojas (espada, hacha, guadana, lanza): cuanto mas ancha, mas fina; nunca menos que 0.75
    return np.where(R <= ROD, R, np.maximum(0.75, ROD - (R - ROD) * 0.45))


def _distancia(a):
    """Distancia de cada muestra opaca al borde (en muestras)."""
    p = np.pad(a, 1)
    borde = ~p & (np.roll(p, 1, 0) | np.roll(p, -1, 0) | np.roll(p, 1, 1) | np.roll(p, -1, 1))
    by, bx = np.nonzero(borde)
    ys, xs = np.nonzero(a)
    d = np.zeros(a.shape, np.float32)
    for i in range(0, len(ys), 2000):
        yy, xx = ys[i:i + 2000, None] + 1, xs[i:i + 2000, None] + 1
        d[ys[i:i + 2000], xs[i:i + 2000]] = np.sqrt(((yy - by) ** 2 + (xx - bx) ** 2).min(1)) - 0.5
    return d


def _radio(d):
    """Radio de la pieza a la que pertenece cada muestra (discos maximos del eje medio)."""
    R = d.copy()
    p = np.pad(d, 1)
    cresta = (d > 0) & np.all([d >= p[1 + dy:p.shape[0] - 1 + dy, 1 + dx:p.shape[1] - 1 + dx] - 1e-4
                               for dy in (-1, 0, 1) for dx in (-1, 0, 1)], axis=0)
    h, w = d.shape
    for y, x in zip(*np.nonzero(cresta)):
        r = float(d[y, x]) + 0.5
        k = int(math.ceil(r))
        y0, y1, x0, x1 = max(0, y - k), min(h, y + k + 1), max(0, x - k), min(w, x + k + 1)
        gy, gx = np.ogrid[y0 - y:y1 - y, x0 - x:x1 - x]
        m = gy * gy + gx * gx <= r * r
        sub = R[y0:y1, x0:x1]
        sub[m] = np.maximum(sub[m], d[y, x])
    return R


def _relleno(rgba):
    """Pinta lo transparente con el color opaco mas cercano (asi cualquier cara tiene color)."""
    a = rgba[..., 3] > ALFA
    out = rgba.copy()
    cur = a.copy()
    while not cur.all():
        nxt = cur.copy()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            src = np.roll(cur, (dy, dx), (0, 1))
            col = np.roll(out, (dy, dx), (0, 1))
            m = src & ~nxt
            if dy == 1:
                m[0] = False
            if dy == -1:
                m[-1] = False
            if dx == 1:
                m[:, 0] = False
            if dx == -1:
                m[:, -1] = False
            out[m] = col[m]
            nxt |= m
        if (nxt == cur).all():
            break
        cur = nxt
    out[..., 3] = 255
    return out


def enderezar(im, glow):
    """Gira el icono 45 grados (el arma queda parada). Devuelve (textura girada con todos sus cuadros,
    mascara del primer cuadro, mascara de brillo), todo a SS muestras por pixel."""
    w = im.size[0]
    n = im.size[1] // w if im.size[1] % w == 0 else 1
    frames = []
    for i in range(n):
        f = im.crop((0, i * w, w, (i + 1) * w)).resize((w * SS, w * SS), Image.NEAREST)
        frames.append(f.rotate(45, resample=Image.NEAREST, expand=True))
    size = frames[0].size[0]
    a = np.asarray(frames[0])[..., 3] > ALFA
    g = np.zeros_like(a)
    if glow is not None:
        gi = Image.fromarray((glow[:w] * 255).astype(np.uint8)).resize((w * SS, w * SS), Image.NEAREST)
        g = np.asarray(gi.rotate(45, resample=Image.NEAREST, expand=True)) > 127
    strip = Image.new('RGBA', (size, size * n))
    for i, f in enumerate(frames):
        strip.paste(Image.fromarray(_relleno(np.asarray(f))), (0, i * size))
    return strip, a, g & a


def _cajas(m):
    """Rectangulos que cubren la mascara: tramos por fila unidos con los iguales de las filas siguientes."""
    runs = {}
    h, w = m.shape
    for y in range(h):
        row = m[y]
        x = 0
        while x < w:
            if not row[x]:
                x += 1
                continue
            x0 = x
            while x < w and row[x]:
                x += 1
            runs[(y, x0)] = [x0, x, y, y + 1]
    out = []
    for (y, x0), r in sorted(runs.items()):
        if r is None:
            continue
        yy = y + 1
        while runs.get((yy, x0)) and runs[(yy, x0)][1] == r[1]:
            r[3] = yy + 1
            runs[(yy, x0)] = None
            yy += 1
        out.append(r)
    return out


def _suavizar(m):
    """Saca dientes de una celda en los bordes (el giro de 45 grados deja serrucho)."""
    p = np.pad(m, 1).astype(np.int8)
    vecinos = sum(p[1 + dy:p.shape[0] - 1 + dy, 1 + dx:p.shape[1] - 1 + dx]
                  for dy in (-1, 0, 1) for dx in (-1, 0, 1)) - m
    return (m & (vecinos >= 3)) | (~m & (vecinos >= 6))


def esculpir(a, g, fam, w):
    """Elementos del arma parada. a/g: mascaras a SS muestras por pixel; w: ancho del icono en pixeles."""
    d = _distancia(a) / SS + 0.25                  # pixeles del icono
    R = np.maximum(_radio(d), 1e-3)
    tope = _grosor_max(R, fam)
    hh = tope * np.sqrt(np.clip(1 - ((R - np.minimum(d, R)) / R) ** 2, 0, 1))
    hh = np.where(a, np.maximum(hh, NIVELES[0]), 0)
    # a celdas
    n = a.shape[0] // CELDA * CELDA
    def celdas(v, f):
        return f(f(v[:n, :n].reshape(n // CELDA, CELDA, n // CELDA, CELDA), 3), 1)
    cm = _suavizar(celdas(a.astype(np.float32), np.mean) >= 0.5)
    ch = np.where(cm, np.maximum(celdas(hh, np.max), NIVELES[0]), 0)
    # la suavizada puede sumar celdas sin altura: toman la del vecino
    cg = (celdas(g.astype(np.float32), np.mean) >= 0.5) & cm
    size = a.shape[0]
    u = 16 / w                                     # unidades por pixel del icono
    paso = CELDA / SS                              # pixeles del icono por celda
    c = size / SS / 2                              # centro del lienzo girado, en pixeles
    q = 16 / size * CELDA                          # uv por celda
    els = []
    for ni, t in enumerate(NIVELES):
        capa = cm if ni == 0 else ch >= t - 0.12
        if not capa.any():
            break
        for gl in (False, True):
            for x0, x1, y0, y1 in _cajas(capa & (cg == gl)):
                fx0, fx1 = 8 + (x0 * paso - c) * u, 8 + (x1 * paso - c) * u
                fy0, fy1 = 8 - (y1 * paso - c) * u, 8 - (y0 * paso - c) * u
                half = t * u
                U0, U1, V0, V1 = x0 * q, x1 * q, y0 * q, y1 * q
                faces = {'south': [U0, V0, U1, V1], 'north': [U1, V0, U0, V1],
                         'up': [U0, V0, U1, V0 + q], 'down': [U0, V1 - q, U1, V1],
                         'west': [U0, V0, U0 + q, V1], 'east': [U1 - q, V0, U1, V1]}
                el = {'from': [round(fx0, 4), round(fy0, 4), round(8 - half, 4)],
                      'to': [round(fx1, 4), round(fy1, 4), round(8 + half, 4)],
                      'faces': {k: {'uv': [round(v, 4) for v in uv], 'texture': '#t'} for k, uv in faces.items()}}
                if gl:
                    el['light_emission'] = 15
                    el['shade'] = False
                els.append(el)
    return els


def display_parado(disp, f=1):
    """El display del mod es para el icono en diagonal; el arma esculpida esta parada (45 grados menos)
    y tiene volumen propio (escala pareja en z)."""
    out = {}
    for k in ('thirdperson_righthand', 'thirdperson_lefthand', 'firstperson_righthand', 'firstperson_lefthand',
              'head', 'ground', 'fixed'):
        if k in disp:
            v = dict(disp[k])
            s = v.get('scale', [1, 1, 1])
            v['scale'] = [round(s[0] * f, 4), round(s[1] * f, 4), round(s[0] * f, 4)]
            r = list(v.get('rotation', [0, 0, 0]))
            r[2] += 45 if k.endswith('lefthand') else -45
            v['rotation'] = r
            if f != 1 and 'translation' in v and k.startswith('third'):
                v['translation'] = [round(x * f, 3) for x in v['translation']]
            out[k] = v
    return out


class Salida:
    def __init__(self):
        self.files = {}
        self.vista = {}                 # iid -> (modelo 3D, textura, icono)

    def tex(self, name, im, mc=None):
        self.files[f'assets/astral/textures/{TEX}/{name}.png'] = _png(im)
        if mc:
            self.files[f'assets/astral/textures/{TEX}/{name}.png.mcmeta'] = js(mc)
        return f'astral:{TEX}/{name}'

    def modelo(self, name, data):
        self.files[f'assets/astral/models/item/{name}.json'] = js(data)
        return {'type': 'minecraft:model', 'model': f'astral:item/{name}'}

    def item(self, iid, model):
        self.files[f'assets/astral/items/{iid}.json'] = js({'model': model})

    def plano_gui(self, name, tex, disp=None):
        d = {'parent': 'minecraft:item/generated', 'textures': {'layer0': tex}, 'gui_light': 'front'}
        if disp and 'gui' in disp:
            d['display'] = {'gui': disp['gui']}
        return self.modelo(name + '_gui', d)


def por_contexto(plano, solido, cuando=('gui',)):
    return {'type': 'minecraft:select', 'property': 'minecraft:display_context',
            'cases': [{'when': list(cuando), 'model': plano}], 'fallback': solido}


def primera_persona(S, name, textura, solido, familia):
    """Extrusion fina continua del motor vanilla, sin capas de voxeles superpuestas.

    El icono sigue en diagonal: aplica el display vanilla sin display_parado.
    Solo cambia las dos vistas en primera persona; conserva el resto del modelo.
    """
    base = VANILLA['item/crossbow' if familia == 'ballesta' else 'item/bow']
    disp = {}
    for side in ('righthand', 'lefthand'):
        key = 'firstperson_' + side
        disp[key] = dict(base[key], scale=[0.50] * 3, translation=[-0.5, 5.5, -1.0])
    plano = S.modelo(name + '_primera_persona', {
        'parent': 'minecraft:item/generated', 'textures': {'layer0': textura}, 'display': disp})
    return por_contexto(plano, solido, ('firstperson_righthand', 'firstperson_lefthand'))


def hacer_plano(S, name, ref, tex_ref=None, base='item/handheld'):
    """Devuelve (modelo plano para el inventario, modelo esculpido)."""
    disp, tex = resolver(ref) if ref else resolver(base)
    im, glow, mc = leer_textura(tex_ref or tex['layer0'])
    ti = S.tex(name + '_icono', im, mc)
    girada, a, g = enderezar(im, glow)
    t = S.tex(name, girada, mc)
    arma = name.split('_pulling')[0].replace('_arrow', '').replace('_firework', '')
    els = esculpir(a, g, _familia(name), im.size[0])
    model = {'textures': {'t': t, 'particle': t}, 'elements': els,
             'display': display_parado(disp, ESCALA.get(arma, 1))}
    S.vista.setdefault(name, (model, girada, im))
    solido = S.modelo(name, model)
    if _familia(name) in ('arco', 'ballesta'):
        solido = primera_persona(S, name, ti, solido, _familia(name))
    return S.plano_gui(name, ti, disp), solido


# ------------------------------------------------------------------------------------- geo -> modelo de item
def _rotacion(R, origin):
    """Rotacion de un elemento: un solo eje si alcanza, si no x/y/z (26.1)."""
    ang = math.degrees(math.acos(max(-1.0, min(1.0, (np.trace(R) - 1) / 2))))
    if ang < 1e-3:
        return None
    o = [round(float(x), 4) for x in origin]
    for i, ax in enumerate('xyz'):
        e = np.zeros(3)
        e[i] = 1
        if np.allclose(R @ e, e, atol=1e-5):
            j, k = (i + 1) % 3, (i + 2) % 3
            return {'origin': o, 'axis': ax, 'angle': round(math.degrees(math.atan2(R[k, j], R[j, j])), 3)}
    rx, ry, rz = G.euler_zyx(R)
    return {'origin': o, 'x': round(rx, 3), 'y': round(ry, 3), 'z': round(rz, 3)}


def geo_elementos(geo_path, tex_size=None):
    """Cubos del geo como elementos en espacio bb (sin acomodar): [(centro, mitad, R, caras)]."""
    geo = G.load_geo(geo_path)
    d = geo['description']
    tw, th = tex_size or (d.get('texture_width', 64), d.get('texture_height', 64))
    out = []
    for c in G.collect_cubes(geo):
        x0, y0, z0, x1, y1, z1 = c['box']
        lo, hi = np.array([x0, y0, z0]), np.array([x1, y1, z1])
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
        if faces:
            out.append((c['R'] @ ((lo + hi) / 2) + c['t'], (hi - lo) / 2, c['R'], faces))
    return out


def geo_modelo(cubos, k, mover):
    """Elementos Java: p -> p * k + mover."""
    els = []
    for ctr, half, R, faces in cubos:
        c = ctr * k + mover
        el = {'from': [round(float(x), 4) for x in c - half * k], 'to': [round(float(x), 4) for x in c + half * k],
              'faces': faces}
        r = _rotacion(R, c)
        if r:
            el['rotation'] = r
        els.append(el)
    return els


def _esquinas(cubos):
    pts = []
    for ctr, half, R, _ in cubos:
        for sx in (-1, 1):
            for sy in (-1, 1):
                for sz in (-1, 1):
                    pts.append(ctr + R @ (half * np.array([sx, sy, sz])))
    return np.array(pts)


def hacer_geo(S, name, geo_ref, tex_ref, icon_ref, disp_ref):
    """GeckoLib dibuja el geo con su origen en (0.5, 0.51, 0.5) del bloque y despues aplica el display del item."""
    cubos = geo_elementos(ruta(geo_ref, '', '.json').parent / (geo_ref.split('/')[-1] + '.geo.json'))
    centro = np.array([8, 0.51 * 16, 8])
    pts = _esquinas(cubos) + centro
    k = min(1.0, 23.9 / float(np.abs(pts - 8).max()))          # achicar hacia (8,8,8) para entrar en -16..32
    els = geo_modelo(cubos, k, (centro - 8) * k + 8)
    disp, _ = resolver(disp_ref)
    display = {}
    for ctx, v in disp.items():
        if ctx in ('gui', 'ground', 'fixed'):
            continue
        v = dict(v)
        v['scale'] = [round(s / k, 4) for s in v.get('scale', [1, 1, 1])]
        display[ctx] = v
    im, _, mc = leer_textura(tex_ref)
    t = S.tex(name, im, mc)
    icon, _, imc = leer_textura(icon_ref)
    ti = S.tex(name + '_icono', icon, imc)
    model = {'textures': {'t': t, 'particle': t}, 'elements': els, 'display': display}
    S.vista[name] = (model, im, icon)
    S.item(name, por_contexto(S.plano_gui(name, ti), S.modelo(name, model), ('gui', 'ground', 'fixed')))


def hacer_varatha(S, name, aspecto):
    """Lanza de Bedrock (geo de entidad): se para en x=8, z=8 como las lanzas propias (de y=-11.5 a 31.3)."""
    base = MODS / 'varatha/subpacks' / aspecto
    tex = Image.open(base / 'textures/entity/trident.png').convert('RGBA')
    cubos = geo_elementos(base / 'models/entity/trident.geo.json')
    pts = _esquinas(cubos)
    lo, hi = pts.min(0), pts.max(0)
    k = 42.8 / (hi[1] - lo[1])
    lado = max(hi[0] - lo[0], hi[2] - lo[2]) / 2
    k = min(k, 23.9 / lado)
    mid = (lo + hi) / 2
    mover = np.array([8 - mid[0] * k, -11.5 - lo[1] * k, 8 - mid[2] * k])
    els = geo_modelo(cubos, k, mover)
    t = S.tex(name, tex)
    icon = Image.open(base / 'textures/items/trident.png').convert('RGBA')
    ti = S.tex(name + '_icono', icon)
    model = {'textures': {'t': t, 'particle': t}, 'elements': els, 'display': PARADO}
    S.vista[name] = (model, tex, icon)
    S.item(name, por_contexto(S.plano_gui(name, ti), S.modelo(name, model), ('gui', 'ground', 'fixed')))


def hacer_java(S, name, model_ref, tex_ref, icon_ref):
    src = json.loads(ruta(model_ref, 'models', '.json').read_text(encoding='utf-8'))
    im, _, mc = leer_textura(tex_ref)
    t = S.tex(name, im, mc)
    icon, _, imc = leer_textura(icon_ref)
    ti = S.tex(name + '_icono', icon, imc)
    keys = {f['texture'].lstrip('#') for e in src['elements'] for f in e['faces'].values()}
    model = {'textures': dict({k: t for k in keys}, particle=t), 'elements': src['elements'],
             'display': {k: v for k, v in src.get('display', {}).items() if k not in ('gui', 'ground', 'fixed')}}
    if 'texture_size' in src:
        model['texture_size'] = src['texture_size']
    S.vista[name] = (model, im, icon)
    S.item(name, por_contexto(S.plano_gui(name, ti), S.modelo(name, model), ('gui', 'ground', 'fixed')))


# ------------------------------------------------------------------------------------- arcos y ballestas
def hacer_arco(S, name, ref):
    sufs = ('', '_pulling_0', '_pulling_1', '_pulling_2')
    pares = {s: hacer_plano(S, name + s, ref + s) for s in sufs}

    def arbol(i):
        return {'type': 'minecraft:condition', 'property': 'minecraft:using_item', 'on_false': pares[''][i],
                'on_true': {'type': 'minecraft:range_dispatch', 'property': 'minecraft:use_duration', 'scale': 0.05,
                            'entries': [{'threshold': 0.65, 'model': pares['_pulling_1'][i]},
                                        {'threshold': 0.9, 'model': pares['_pulling_2'][i]}],
                            'fallback': pares['_pulling_0'][i]}}
    S.item(name, por_contexto(arbol(0), arbol(1)))


def hacer_ballesta(S, name, ref):
    sufs = ('', '_pulling_0', '_pulling_1', '_pulling_2', '_arrow', '_firework')
    pares = {s: hacer_plano(S, name + s, ref + s) for s in sufs}

    def arbol(i):
        return {'type': 'minecraft:select', 'property': 'minecraft:charge_type',
                'cases': [{'when': 'arrow', 'model': pares['_arrow'][i]},
                          {'when': 'rocket', 'model': pares['_firework'][i]}],
                'fallback': {'type': 'minecraft:condition', 'property': 'minecraft:using_item', 'on_false': pares[''][i],
                             'on_true': {'type': 'minecraft:range_dispatch', 'property': 'minecraft:crossbow/pull',
                                         'entries': [{'threshold': 0.58, 'model': pares['_pulling_1'][i]},
                                                     {'threshold': 1.0, 'model': pares['_pulling_2'][i]}],
                                         'fallback': pares['_pulling_0'][i]}}}
    S.item(name, por_contexto(arbol(0), arbol(1)))


def generar():
    S = Salida()
    for iid, spec in ARMAS.items():
        kind = spec[0]
        if kind == 'plano':
            plano, solido = hacer_plano(S, iid, spec[1], *spec[2:])
            S.item(iid, por_contexto(plano, solido))
        elif kind == 'arco':
            hacer_arco(S, iid, spec[1])
        elif kind == 'ballesta':
            hacer_ballesta(S, iid, spec[1])
        elif kind == 'geo':
            hacer_geo(S, iid, *spec[1:])
        elif kind == 'varatha':
            hacer_varatha(S, iid, spec[1])
        elif kind == 'java':
            hacer_java(S, iid, *spec[1:])
    return S


def revisar(S):
    """Limites de Minecraft: coordenadas de -16 a 32."""
    malos = []
    for path, data in S.files.items():
        if '/models/' not in path:
            continue
        for e in json.loads(data).get('elements', []):
            if min(e['from'] + e['to']) < -16 or max(e['from'] + e['to']) > 32:
                malos.append(path)
                break
    return malos


# ------------------------------------------------------------------------------------- vista previa
def _rx(a):
    c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def _ry(a):
    c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def _rz(a):
    c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def quads_modelo(model, tex_px):
    """Quads del modelo en sus unidades (0..16), con el uv normalizado al primer cuadro de la textura."""
    q = []
    tw, th = tex_px
    vs = tw / th if th > tw and th % tw == 0 else 1.0          # textura animada: solo el primer cuadro
    ts = model.get('texture_size', [16, 16])
    for el in model['elements']:
        fc = G.face_corners(*el['from'], *el['to'])
        R, o = np.eye(3), np.zeros(3)
        r = el.get('rotation')
        if r:
            o = np.array(r['origin'], float)
            if 'axis' in r:
                R = {'x': _rx, 'y': _ry, 'z': _rz}[r['axis']](r['angle'])
            else:
                R = G.rot_matrix(r['x'], r['y'], r['z'])
        for k, fd in el['faces'].items():
            U0, V0, U1, V1 = [x / 16 for x in fd.get('uv', [0, 0, 16, 16])]
            if k in ('up', 'down'):
                U0, V0, U1, V1 = U1, V1, U0, V0
            pts = (np.array(fc[k], float) - o) @ R.T + o
            q.append((pts, np.array([(U0, V0 * vs), (U1, V0 * vs), (U1, V1 * vs), (U0, V1 * vs)])))
    return q


def en_mano(quads, disp):
    """Lleva el item a la mano derecha de un jugador quieto (misma cuenta que hace el juego). Espacio bb."""
    d = disp.get('thirdperson_righthand', {})
    rot = d.get('rotation', [0, 0, 0])
    R = _rx(rot[0]) @ _ry(rot[1]) @ _rz(rot[2])
    sc = np.array(d.get('scale', [1, 1, 1]), float)
    tr = np.array(d.get('translation', [0, 0, 0]), float)
    A = _rx(-90) @ _ry(180)
    out = []
    for pts, uv in quads:
        p = ((pts - 8) * sc) @ R.T + tr                       # display del item
        p = (p + np.array([1, 2, -10])) @ A.T + np.array([-5, 2, 0])   # mano -> brazo -> cuerpo (y hacia abajo)
        out.append((np.column_stack([-p[:, 0], 24 - p[:, 1], p[:, 2]]), uv))
    return out


def vista_previa(S, path):
    """Por arma: icono del inventario, el modelo solo (de 3/4) y en la mano de un jugador quieto."""
    cw, ch, cols = 600, 440, 5
    base = list(ARMAS)
    rows = (len(base) + cols - 1) // cols
    sheet = Image.new('RGBA', (cols * cw, rows * (ch + 22)), (38, 40, 50, 255))
    dr = ImageDraw.Draw(sheet)
    man_q, man_t = G.mannequin()
    for i, iid in enumerate(base):
        model, tex, icon = S.vista[iid]
        w = tex.size[0]
        frame = tex.crop((0, 0, w, w)) if tex.size[1] > w and tex.size[1] % w == 0 else tex
        t = np.asarray(frame, np.float32) / 255
        quads = quads_modelo(model, frame.size)
        x, y = (i % cols) * cw, (i // cols) * (ch + 22)
        # solo: centrado y a escala para que entre
        pts = np.concatenate([q[0] for q in quads])
        lo, hi = pts.min(0), pts.max(0)
        G.S = min(13, 400 / max(hi[1] - lo[1], 1), 200 / max(hi[0] - lo[0], hi[2] - lo[2], 1))
        G.W, G.H = 230, ch
        solo = [(q - (lo + hi) / 2 + np.array([0, 20, 0]), uv) for q, uv in quads]
        sheet.alpha_composite(G.render([(solo, t)], yaw=38, pitch=10), (x + 40, y))
        # en la mano
        G.S = 6
        G.W, G.H = 330, ch
        im = G.render([(man_q, man_t), (en_mano(quads, model['display']), t)], yaw=-68, pitch=8)
        sheet.alpha_composite(im, (x + 270, y))
        iw = icon.size[0]
        ic = icon.crop((0, 0, iw, iw)).resize((64, 64), Image.NEAREST)
        dr.rectangle([x + 4, y + 4, x + 71, y + 71], fill=(20, 20, 28, 255), outline=(120, 120, 140, 255))
        sheet.alpha_composite(ic, (x + 6, y + 6))
        dr.text((x + 6, y + ch + 4), f'{iid}  ({ARMAS[iid][0]}, {len(model["elements"])} piezas)', fill=(235, 235, 235, 255))
    sheet.save(path)


# ------------------------------------------------------------------------------------- pack FINAL
def cambios_publicos():
    """Archivos del pack publico nuevo que no estan (o son distintos) en el de HEAD."""
    new = zipfile.ZipFile(ROOT / 'build/AstralRPG-Textures.zip')
    old = zipfile.ZipFile(io.BytesIO(subprocess.check_output(
        ['git', 'show', 'HEAD:build/AstralRPG-Textures.zip'], cwd=ROOT)))
    old_names = set(old.namelist())
    return {n: new.read(n) for n in new.namelist() if n not in old_names or new.read(n) != old.read(n)}


def pack_final(S):
    from final_base import select_base
    explicit=Path(sys.argv[sys.argv.index('--base')+1]) if '--base' in sys.argv else None
    base=select_base(BASE,OUT,explicit)
    with zipfile.ZipFile(base) as z:
        files = {n: z.read(n) for n in z.namelist()}
    pub = cambios_publicos()
    files.update(pub)
    files.update(S.files)
    target = OUT / 'AstralRPG-Textures.zip'
    tmp = target.with_suffix('.zip.tmp')
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as out:
        for name, data in sorted(files.items()):
            out.writestr(zipfile.ZipInfo(name, date_time=STAMP), data, compress_type=zipfile.ZIP_DEFLATED)
    from pack_audit import audit
    audit(tmp)
    tmp.replace(target)
    digest = hashlib.sha1(target.read_bytes()).hexdigest()
    (OUT / 'pack.sha1').write_text(digest + '\n')
    print(f'{len(pub)} cambios publicos, {len(S.files)} archivos de armas -> {target} ({digest})')


def main():
    if not MODS.exists() or not PRIV.exists():
        print('Faltan los mods o el circuito privado: no se genera nada.')
        return
    S = generar()
    malos = revisar(S)
    if malos:
        raise SystemExit('Modelos fuera de -16..32: ' + ', '.join(malos))
    if PACK.exists():
        shutil.rmtree(PACK)
    for path, data in S.files.items():
        p = PACK / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
    piezas = {i: len(S.vista[i][0]['elements']) for i in ARMAS}
    print(f'{len(S.files)} archivos -> {PACK}')
    print('piezas:', piezas)
    vista_previa(S, OUT / 'vista_previa.png')
    print('vista previa ->', OUT / 'vista_previa.png')
    if '--sin-pack' not in sys.argv:
        if not BASE.exists():
            print('Falta el pack base (tiers6-10): no se arma el FINAL.')
            return
        pack_final(S)


if __name__ == '__main__':
    main()
