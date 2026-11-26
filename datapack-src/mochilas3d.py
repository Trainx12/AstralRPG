"""Mochilas 3D por material (pedido del dueno 16/11/2026).

La FORMA sale de la mochila `explorer` del mod Wet Backpacks (Lean, Geremilho; LGPL-2.1 / CC0), modificada:
se conservan cuerpo, bolsillos laterales y bolsillo frontal; se quitan hacha, farol y rollo de dormir; se agregan
tapa que cae sobre el frente, dos correas con hebilla, asa y correas de hombro curvas. Por derivar del mod, TODO
sale al circuito privado (ASTRAL_PRIVADO/build/entregas/modelos-3d-efectos); el pack publico conserva la mochila
provisoria de tanda_xp.py. Las texturas (una por material, 128x128) se pintan por codigo: arte propio.

  python datapack-src/mochilas3d.py     modelos + vistas previas privadas
"""
import io
import json
import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from terceros import privado  # noqa: E402

MOD = Path(os.environ.get('ASTRAL_MOD_MOCHILAS', 'C:/Users/Trainx/Desktop/mods/mochilas'))
BASE = MOD / 'assets/leans_extra_backpacks/models/backpacked/explorer.json'
OUT = privado() / 'build/entregas/modelos-3d-efectos'
PX = 2            # pixeles de textura por unidad del modelo
ATLAS = 128
FACES = ('north', 'south', 'east', 'west', 'up', 'down')
MATERIALES = ('leather', 'copper', 'iron', 'gold', 'diamond', 'netherite', 'ender')
NOMBRE = {'leather': 'Cuero', 'copper': 'Cobre', 'iron': 'Hierro', 'gold': 'Oro', 'diamond': 'Diamante',
          'netherite': 'Netherite', 'ender': 'Ender'}
# Indices de la mochila del mod que se conservan: (indice, zona propia)
DEL_MOD = ((0, 'cuerpo'), (1, 'lateral'), (2, 'lateral'), (3, 'bolsillo'))

PALETA = {
    'ender': dict(base='#164c46', luz='#329d88', sombra='#092d30', borde='#071c24', tapa='#1f6f62',
                  correa='#382449', hebilla='#af82dc', detalle='#8bf2c5', asa='#432b59'),
    'leather': dict(base='#7d4c2b', luz='#9a6238', sombra='#5c3720', borde='#38200f', tapa='#8a5630',
                    correa='#4b2d1a', hebilla='#d9b25c', detalle='#e0bd82', asa='#6b3f22'),
    'copper': dict(base='#c4633a', luz='#e88c55', sombra='#994527', borde='#5c2916', tapa='#d2703f',
                   correa='#7b3a21', hebilla='#f0a878', detalle='#f6c29a', asa='#a34e2b', extra='#4da57e'),
    'iron': dict(base='#9399a6', luz='#c8cdd8', sombra='#6a6f7c', borde='#3a3d47', tapa='#a9aebb',
                 correa='#2d2f38', hebilla='#dfe3ea', detalle='#eceff4', asa='#4b4e5a'),
    'gold': dict(base='#e6b422', luz='#ffe263', sombra='#b47c16', borde='#6c480e', tapa='#f2c633',
                 correa='#4c3120', hebilla='#fff3a6', detalle='#fff6bd', asa='#c98a1a'),
    'diamond': dict(base='#36c9cc', luz='#a9f5ee', sombra='#1d97a5', borde='#0e4c63', tapa='#52dcd9',
                    correa='#1b3b6b', hebilla='#cdf8f5', detalle='#e4fffb', asa='#1f5f9c'),
    'netherite': dict(base='#49414f', luz='#6b5d79', sombra='#2e2935', borde='#19151e', tapa='#554a60',
                      correa='#231e2a', hebilla='#b99a69', detalle='#8c6c4b', asa='#35303d', extra='#7459a0'),
}


def _rgb(h):
    h = h.lstrip('#')
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32)


# ------------------------------------------------------------------------------------------- forma
def piezas():
    """[(zona, from, to)] en el espacio del mod (frente = +z). Las 4 primeras son del mod, sin tocar."""
    src = json.loads(BASE.read_text(encoding='utf-8'))['elements']
    out = [(zona, list(src[i]['from']), list(src[i]['to'])) for i, zona in DEL_MOD]
    # Tapa: techo que sobresale y solapa que cae sobre el frente (reemplaza el bolsillo alto y el rollo del mod).
    out += [('tapa', [3.5, 9.5, 7.5], [12.5, 11, 13.6]),
            ('tapa', [3.5, 5.5, 13], [12.5, 10.5, 14.2])]
    for x in (5.3, 9.5):                                  # dos correas con hebilla cuadrada
        out += [('correa', [x, 11, 8], [x + 1.2, 11.25, 14.6]),
                ('correa', [x, 4.2, 14.2], [x + 1.2, 11.25, 14.6]),
                ('hebilla', [x - .3, 4.6, 14.6], [x + 1.5, 6.4, 15.15])]
    out += [('asa', [6.2, 11, 9.6], [7, 12.8, 10.6]), ('asa', [9, 11, 9.6], [9.8, 12.8, 10.6]),
            ('asa', [6.2, 12.8, 9.6], [9.8, 13.6, 10.6])]
    for s in (-1, 1):                                     # correas de hombro: un arco a cada costado
        def box(a, b):
            xs = sorted((8 + s * a[0], 8 + s * b[0]))
            return ('asa', [xs[0], a[1], a[2]], [xs[1], b[1], b[2]])
        out += [box((4, 9, 6.9), (6.4, 10.1, 8)), box((6, 8.2, 6.9), (7, 9.6, 8)),
                box((6.6, 1.2, 6.9), (7.6, 8.6, 8)), box((6, .2, 6.9), (7, 1.6, 8)),
                box((4, -.9, 6.9), (6.4, .6, 8))]
    return out


def _tam(frm, to, face):
    dx, dy, dz = (abs(to[k] - frm[k]) for k in range(3))
    w, h = {'north': (dx, dy), 'south': (dx, dy), 'east': (dz, dy), 'west': (dz, dy),
            'up': (dx, dz), 'down': (dx, dz)}[face]
    return max(1, round(w * PX)), max(1, round(h * PX))


def empaquetar(ps):
    """Estanteria simple: {(pieza, cara): (x, y, w, h)} en pixeles del atlas."""
    rects = sorted(((*_tam(f, t, face), i, face) for i, (_, f, t) in enumerate(ps) for face in FACES),
                   key=lambda r: (-r[1], -r[0]))
    pos, x, y, alto = {}, 0, 0, 0
    for w, h, i, face in rects:
        if x + w > ATLAS:
            x, y, alto = 0, y + alto + 1, 0
        if y + h > ATLAS:
            raise ValueError('La textura de la mochila no entra en el atlas')
        pos[(i, face)] = (x, y, w, h)
        x, alto = x + w + 1, max(alto, h)
    return pos


def modelo(ps, pos, tex):
    els = []
    for i, (_, f, t) in enumerate(ps):
        faces = {}
        for face in FACES:
            x, y, w, h = pos[(i, face)]
            q = 16 / ATLAS
            faces[face] = {'uv': [round(v * q, 4) for v in (x, y, x + w, y + h)], 'texture': '#t'}
        els.append({'from': f, 'to': t, 'faces': faces})
    mano = {'rotation': [75, -45, 0], 'translation': [.75, 5.75, 3.25], 'scale': [.8] * 3}
    fp = {'rotation': [0, -45, 0], 'translation': [-.5, 4.5, .5], 'scale': [.5] * 3}
    display = {'thirdperson_righthand': mano, 'thirdperson_lefthand': dict(mano, rotation=[75, 45, 0]),
               'firstperson_righthand': fp, 'firstperson_lefthand': dict(fp, rotation=[0, 45, 0]),
               'ground': {'translation': [0, 4.75, -2], 'scale': [.6] * 3},
               'gui': {'rotation': [24, -32, 0], 'translation': [.4, 3.1, 0], 'scale': [.95] * 3},
               'head': {'rotation': [0, -180, 0], 'translation': [0, 14.5, 2.5]},
               'fixed': {'rotation': [0, -180, 0], 'translation': [0, 3.5, 1]}}
    return {'texture_size': [ATLAS, ATLAS], 'textures': {'t': tex, 'particle': tex}, 'elements': els,
            'display': display}


# ------------------------------------------------------------------------------------------- pintura
def _ruido(x, y, seed):
    return ((x * 73856093) ^ (y * 19349663) ^ (seed * 83492791)) % 997 / 997


def pintar_cara(mat, zona, face, w, h, seed):
    P = {k: _rgb(v) for k, v in PALETA[mat].items()}
    base = {'cuerpo': P['base'], 'lateral': P['base'], 'bolsillo': P['tapa'], 'tapa': P['tapa'],
            'correa': P['correa'], 'hebilla': P['hebilla'], 'asa': P['asa']}[zona]
    if mat == 'netherite' and zona == 'bolsillo':
        base = P['extra'] * .75 + P['base'] * .25
    luz, sombra = P['luz'], P['sombra']
    if zona in ('correa', 'asa'):
        luz, sombra = base * 1.25, base * .7
    if zona == 'hebilla':
        luz, sombra = P['detalle'], base * .62
    a = np.zeros((h, w, 4), np.float32)
    a[..., 3] = 255
    grande = zona in ('cuerpo', 'lateral', 'bolsillo', 'tapa') and w >= 6 and h >= 5
    for y in range(h):
        for x in range(w):
            n = _ruido(x // 2, y // 2, seed)
            c = base * (.93 + .14 * n)
            if mat == 'diamond' and grande:            # facetas: triangulos claros y oscuros
                cx, cy = x % 8, y % 8
                c = luz * .55 + base * .45 if cx + cy < 7 else (base if cx > cy else sombra * .5 + base * .5)
                if cx + cy == 7 or cx == cy:
                    c = P['detalle'] * .5 + luz * .5
            elif mat == 'gold' and grande and (x + y) % 9 in (0, 1):
                c = luz * .6 + base * .4               # brillo diagonal del oro
            elif mat == 'iron' and grande and (x % 12 == 0 or y % 10 == 9):
                c = sombra                             # juntas de las placas
            elif mat == 'netherite' and grande and n > .82:
                c = luz * .6 + base * .4
            elif mat == 'copper' and grande and _ruido(x, y, seed + 7) > .93 and (x < 3 or y > h - 4 or x > w - 4):
                c = P['extra']                         # verdin en los bordes
            a[y, x, :3] = c
    if face == 'down':
        a[..., :3] *= .78
    if face == 'up' and zona in ('tapa', 'cuerpo'):
        a[..., :3] = a[..., :3] * .8 + luz * .2
    if w >= 3 and h >= 3:                                # canto claro arriba, oscuro abajo y contorno
        a[0, :, :3] = a[0, :, :3] * .5 + luz * .5
        a[-1, :, :3] = a[-1, :, :3] * .5 + sombra * .5
        if zona not in ('correa',):
            a[:, 0, :3] = a[:, 0, :3] * .6 + sombra * .4
            a[:, -1, :3] = a[:, -1, :3] * .6 + sombra * .4
    if zona == 'correa':
        a[:, 0, :3] = sombra
        a[:, -1, :3] = sombra
    lado = face in ('north', 'south', 'east', 'west')
    if zona in ('tapa', 'bolsillo') and grande:
        if lado:                                         # ribete de la solapa / boca del bolsillo
            fila = h - 3 if zona == 'tapa' else 2
            a[fila, 1:-1, :3] = sombra
        if mat == 'leather':                             # costura punteada
            for x in range(2, w - 2):
                if x % 3 != 2:
                    a[1 if zona == 'bolsillo' or not lado else h - 5, x, :3] = P['detalle']
                    if not lado or zona == 'bolsillo':
                        a[h - 2, x, :3] = P['detalle']
            for y in range(2, h - 2):
                if y % 3 != 2:
                    a[y, 1, :3] = P['detalle']
                    a[y, w - 2, :3] = P['detalle']
        elif mat != 'diamond':                           # remaches en las esquinas
            for x, y in ((2, 2), (w - 3, 2), (2, h - 4), (w - 3, h - 4)):
                if 0 <= y < h - 1 and 0 <= x < w:
                    a[y, x, :3] = P['detalle']
                    a[y + 1, x, :3] = P['borde']
        if mat == 'netherite' and lado:
            a[h - 3 if zona == 'tapa' else 2, 1:-1, :3] = P['detalle']
    if zona == 'lateral' and face in ('east', 'west', 'south') and h >= 8:
        a[3, 1:-1, :3] = sombra                          # tapita del bolsillo lateral
        a[2, 1:-1, :3] = a[2, 1:-1, :3] * .4 + luz * .6
    if zona == 'hebilla' and face in ('south', 'north') and w >= 3 and h >= 3:
        a[1:-1, 1:-1, :3] = P['correa']                  # marco con hueco
        a[0, :, :3] = luz
        a[-1, :, :3] = sombra
    if zona == 'cuerpo' and face == 'north':             # espalda: panel acolchado
        a[2:-2, 2:-2, :3] = a[2:-2, 2:-2, :3] * .8 + sombra * .2
    if mat == 'ender' and zona == 'bolsillo' and face == 'south' and w >= 6 and h >= 5:
        # Ojo de ender en el bolsillo frontal; misma geometria de las otras mochilas.
        for yy in range(h):
            for xx in range(w):
                dx, dy = (xx-(w-1)/2)/(w*.38), (yy-(h-1)/2)/(h*.3)
                if abs(dx)+abs(dy) <= 1:
                    a[yy,xx,:3] = P['detalle'] if abs(dx) > .23 else P['borde']
    a[..., :3] = np.clip(a[..., :3], 0, 255)
    return a.astype(np.uint8)


def textura(mat, ps, pos):
    im = np.zeros((ATLAS, ATLAS, 4), np.uint8)
    for (i, face), (x, y, w, h) in pos.items():
        im[y:y + h, x:x + w] = pintar_cara(mat, ps[i][0], face, w, h, i * 6 + FACES.index(face))
    return Image.fromarray(im, 'RGBA')


def plantilla_uv(ps, pos, tex):
    """Guia para repintar: la textura de cuero ampliada con cada zona marcada."""
    k = 8
    im = tex.resize((ATLAS * k, ATLAS * k), Image.NEAREST).convert('RGBA')
    d = ImageDraw.Draw(im)
    color = {'cuerpo': '#ff5050', 'lateral': '#ffa040', 'bolsillo': '#ffe040', 'tapa': '#50ff70',
             'correa': '#50d0ff', 'hebilla': '#ffffff', 'asa': '#d070ff'}
    for (i, face), (x, y, w, h) in pos.items():
        zona = ps[i][0]
        d.rectangle([x * k, y * k, (x + w) * k - 1, (y + h) * k - 1], outline=color[zona])
        if w * k > 52 and h * k > 12:
            d.text((x * k + 3, y * k + 2), f'{zona} {face}'[:w * k // 6], fill=color[zona])
    return im


# ------------------------------------------------------------------------------------------- salida
def _png(im):
    b = io.BytesIO()
    im.save(b, 'PNG')
    return b.getvalue()


def archivos():
    """{ruta en el pack: bytes} + datos para las vistas."""
    ps = piezas()
    pos = empaquetar(ps)
    files, vista = {}, {}
    for mat in MATERIALES:
        tex = f'astral:item/mochilas/mochila_{mat}'
        im = textura(mat, ps, pos)
        m = modelo(ps, pos, tex)
        files[f'assets/astral/textures/item/mochilas/mochila_{mat}.png'] = _png(im)
        files[f'assets/astral/models/item/mochila_{mat}.json'] = (json.dumps(m, separators=(',', ':')) + '\n').encode()
        files[f'assets/astral/items/mochila_{mat}.json'] = (json.dumps(
            {'model': {'type': 'minecraft:model', 'model': f'astral:item/mochila_{mat}'}}) + '\n').encode()
        vista[mat] = (m, im)
    return files, vista, ps, pos


def _vista(model, tex, modo, lado=230):
    import armas_mod as A
    G = A.G
    t = np.asarray(tex, np.float32) / 255
    quads = A.quads_modelo(model, tex.size)
    if modo == 'gui':                                    # lo que hace el juego en el inventario
        d = model['display']['gui']
        R = A._rx(d['rotation'][0]) @ A._ry(d['rotation'][1]) @ A._rz(d['rotation'][2])
        quads = [(((p - 8) * np.array(d['scale'])) @ R.T + np.array(d['translation']) + np.array([0, 16, 0]), uv)
                 for p, uv in quads]
        G.S, G.W, G.H = lado / 16, lado, lado * 2
        im = G.render([(quads, t)], yaw=180, pitch=0)
        top = int(lado + 4 * G.S - lado / 2)
        return im.crop((0, top, lado, top + lado))
    man_q, man_t = G.mannequin()
    G.S, G.W, G.H = 6, lado, 300
    return G.render([(man_q, man_t), (A.en_mano(quads, model['display']), t)], yaw=-68, pitch=8)


def vistas(vista, ps, pos, destino=None):
    destino = destino or OUT / 'previews'
    destino.mkdir(parents=True, exist_ok=True)
    sheet = Image.new('RGBA', (len(MATERIALES) * 240, 580), (24, 26, 36, 255))
    d = ImageDraw.Draw(sheet)
    for i, mat in enumerate(MATERIALES):
        m, tex = vista[mat]
        sheet.alpha_composite(_vista(m, tex, 'gui'), (i * 240 + 5, 20))
        sheet.alpha_composite(_vista(m, tex, 'mano'), (i * 240 + 5, 270))
        d.text((i * 240 + 90, 6), NOMBRE[mat], fill=(240, 232, 200, 255))
    sheet.save(destino / 'mochilas-3d.png')
    plantilla_uv(ps, pos, vista['leather'][1]).save(destino / 'mochilas-uv.png')
    return destino / 'mochilas-3d.png'


def main():
    if not BASE.exists() or not privado().exists():
        print('Falta el mod de mochilas o el circuito privado: no se genera nada.')
        return
    files, vista, ps, pos = archivos()
    for rel, data in files.items():
        p = OUT / 'pack' / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
    print(len(files), 'archivos ->', OUT / 'pack')
    print(vistas(vista, ps, pos))


if __name__ == '__main__':
    main()
