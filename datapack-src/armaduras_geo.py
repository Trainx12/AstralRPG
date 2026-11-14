"""Lectura de modelos GeckoLib (.geo.json) y renderizador CPU simple (sin GPU).

Espacio de trabajo "bb" (como Blockbench): +x = derecha del personaje, +y = arriba, -z = frente.
El codigo es propio; los modelos y texturas que se lean con esto son de terceros y sus salidas
van solo al circuito privado (ver docs/TERCEROS.md).
"""
import json
import math

import numpy as np
from PIL import Image

FACES = ('north', 'south', 'east', 'west', 'up', 'down')
ROOTS = {'bipedhead': 'head', 'bipedbody': 'body', 'bipedrightarm': 'rarm', 'bipedleftarm': 'larm',
         'bipedrightleg': 'rleg', 'bipedleftleg': 'lleg'}


def rot_matrix(rx, ry, rz):
    """Rz @ Ry @ Rx (grados, mano derecha)."""
    rx, ry, rz = map(math.radians, (rx, ry, rz))
    cx, sx, cy, sy, cz, sz = math.cos(rx), math.sin(rx), math.cos(ry), math.sin(ry), math.cos(rz), math.sin(rz)
    X = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    Y = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Z = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return Z @ Y @ X


def euler_zyx(R):
    """Inversa de rot_matrix: devuelve (rx, ry, rz) en grados con R = Rz Ry Rx."""
    sy = -R[2, 0]
    sy = max(-1.0, min(1.0, sy))
    ry = math.asin(sy)
    if abs(sy) < 0.99999:
        rx = math.atan2(R[2, 1], R[2, 2])
        rz = math.atan2(R[1, 0], R[0, 0])
    else:  # bloqueo de cardan
        rx = math.atan2(-R[1, 2], R[1, 1])
        rz = 0.0
    return tuple(math.degrees(a) for a in (rx, ry, rz))


def face_corners(x0, y0, z0, x1, y1, z1):
    """Esquinas (arriba-izq, arriba-der, abajo-der, abajo-izq) de cada cara vista desde afuera."""
    return {
        'north': [(x1, y1, z0), (x0, y1, z0), (x0, y0, z0), (x1, y0, z0)],
        'south': [(x0, y1, z1), (x1, y1, z1), (x1, y0, z1), (x0, y0, z1)],
        'east': [(x1, y1, z1), (x1, y1, z0), (x1, y0, z0), (x1, y0, z1)],
        'west': [(x0, y1, z0), (x0, y1, z1), (x0, y0, z1), (x0, y0, z0)],
        'up': [(x1, y1, z1), (x0, y1, z1), (x0, y1, z0), (x1, y1, z0)],
        'down': [(x1, y0, z0), (x0, y0, z0), (x0, y0, z1), (x1, y0, z1)],
    }


def box_uv(u, v, w, h, d, mirror):
    w, h, d = math.floor(w + 1e-6), math.floor(h + 1e-6), math.floor(d + 1e-6)
    f = {
        'east': (u, v + d, d, h), 'north': (u + d, v + d, w, h),
        'west': (u + d + w, v + d, d, h), 'south': (u + 2 * d + w, v + d, w, h),
        'up': (u + d, v, w, d), 'down': (u + d + w, v + d, w, -d),
    }
    if mirror:
        f['east'], f['west'] = f['west'], f['east']
        f = {k: (a + c, b, -c, e) for k, (a, b, c, e) in f.items()}
    return f


def _rot_of(r):
    return rot_matrix(-r[0], -r[1], r[2])


def _to_bb(p):
    return np.array([-p[0], p[1], p[2]], float)


def load_geo(path):
    return json.load(open(path, encoding='utf-8'))['minecraft:geometry'][0]


def collect_cubes(geo):
    """Lista de cubos con su transformacion final.

    Cada cubo: dict(bone, root, box=(x0,y0,z0,x1,y1,z1) en bb sin rotar, R (3x3), t (3,), faces={cara: (u,v,w,h)}).
    El punto final es R @ p + t.
    """
    bones = {b['name']: b for b in geo['bones']}

    def chain(name):
        out = []
        while name:
            b = bones[name]
            out.append(b)
            name = b.get('parent')
        return out

    cubes = []
    for b in geo['bones']:
        ch = chain(b['name'])
        root = ROOTS.get(ch[-1]['name'].lower())
        mirror_b = b.get('mirror', False)
        # transformacion de la cadena de huesos (hijo -> raiz)
        Rb, tb = np.eye(3), np.zeros(3)
        for bb in ch:
            if 'rotation' in bb and any(bb['rotation']):
                pv = _to_bb(bb.get('pivot', [0, 0, 0]))
                Rr = _rot_of(bb['rotation'])
                # x -> Rr (x - pv) + pv, aplicado despues de lo acumulado
                Rb, tb = Rr @ Rb, Rr @ (tb - pv) + pv
        for c in b.get('cubes', []):
            o, s = c['origin'], c['size']
            inf = c.get('inflate', 0)
            box = (-(o[0] + s[0]) - inf, o[1] - inf, o[2] - inf, -o[0] + inf, o[1] + s[1] + inf, o[2] + s[2] + inf)
            R, t = Rb, tb
            if 'rotation' in c and any(c['rotation']):
                pv = _to_bb(c.get('pivot', [0, 0, 0]))
                Rc = _rot_of(c['rotation'])
                # primero el cubo, despues los huesos
                R, t = Rb @ Rc, Rb @ (pv - Rc @ pv) + tb
            uv = c.get('uv', [0, 0])
            if isinstance(uv, dict):
                faces = {}
                for k, fd in uv.items():
                    u, v = fd['uv']
                    w, h = fd.get('uv_size', [0, 0])
                    faces[k] = (u, v, w, h)
            else:
                faces = box_uv(uv[0], uv[1], s[0], s[1], s[2], c.get('mirror', mirror_b))
            cubes.append(dict(bone=b['name'], root=root, box=box, R=R, t=t, faces=faces))
    return cubes


def cube_quads(cube, tex_size):
    """[(pts 4x3, uv 4x2 normalizado)] de un cubo."""
    fc = face_corners(*cube['box'])
    out = []
    for k, (u, v, w, h) in cube['faces'].items():
        if w == 0 or h == 0 or k not in fc:
            continue
        pts = np.array(fc[k], float) @ cube['R'].T + cube['t']
        uvs = np.array([(u, v), (u + w, v), (u + w, v + h), (u, v + h)], float) / np.array(tex_size, float)
        out.append((pts, uvs))
    return out


def geo_quads(geo, tex_size=None, keep=None):
    d = geo['description']
    ts = tex_size or (d.get('texture_width', 64), d.get('texture_height', 64))
    q = []
    for c in collect_cubes(geo):
        if keep is None or keep(c):
            q += cube_quads(c, ts)
    return q


def load_tex(path, glow=None):
    tex = np.asarray(Image.open(path).convert('RGBA'), np.float32) / 255
    if glow:
        g = np.asarray(Image.open(glow).convert('RGBA'), np.float32) / 255
        if g.shape == tex.shape:
            m = g[..., 3] > 0.5
            tex = tex.copy()
            tex[m] = g[m]
            tex[m, 3] = 1
    return tex


# ------------------------------------------------------------------------------------------ render
S = 14  # pixeles por unidad
W, H = 40 * S, 60 * S


def mannequin():
    """Cuerpo base del jugador con textura plana."""
    tex = Image.new('RGBA', (64, 64))
    px = tex.load()

    def fill(x0, y0, x1, y1, col):
        for x in range(x0, x1):
            for y in range(y0, y1):
                px[x, y] = col
    fill(0, 0, 32, 16, (205, 160, 125, 255))
    fill(16, 16, 40, 32, (70, 80, 95, 255))
    fill(40, 16, 56, 32, (205, 160, 125, 255))
    fill(0, 16, 16, 32, (45, 50, 62, 255))
    for x in (9, 10, 13, 14):
        px[x, 12] = (40, 40, 60, 255)
    geo = {'description': {'texture_width': 64, 'texture_height': 64}, 'bones': [
        {'name': 'h', 'cubes': [{'origin': [-4, 24, -4], 'size': [8, 8, 8], 'uv': [0, 0]}]},
        {'name': 'b', 'cubes': [{'origin': [-4, 12, -2], 'size': [8, 12, 4], 'uv': [16, 16]}]},
        {'name': 'ra', 'cubes': [{'origin': [-8, 12, -2], 'size': [4, 12, 4], 'uv': [40, 16]}]},
        {'name': 'la', 'cubes': [{'origin': [4, 12, -2], 'size': [4, 12, 4], 'uv': [40, 16], 'mirror': True}]},
        {'name': 'rl', 'cubes': [{'origin': [-4, 0, -2], 'size': [4, 12, 4], 'uv': [0, 16]}]},
        {'name': 'll', 'cubes': [{'origin': [0, 0, -2], 'size': [4, 12, 4], 'uv': [0, 16], 'mirror': True}]},
    ]}
    return geo_quads(geo), np.asarray(tex, np.float32) / 255


LIGHT = np.array([0.35, 0.8, -0.5])
LIGHT /= np.linalg.norm(LIGHT)


def render(layers, yaw, pitch=12):
    """layers: [(quads, tex)]. yaw 0 = de frente."""
    color = np.zeros((H, W, 3), np.float32)
    alpha = np.zeros((H, W), np.float32)
    zbuf = np.full((H, W), np.inf, np.float32)
    R = rot_matrix(pitch, 0, 0) @ rot_matrix(0, yaw, 0)
    for li, (quads, tex) in enumerate(layers):
        th, tw = tex.shape[:2]
        bias = -0.02 * li
        for pts, uvs in quads:
            P = (pts - np.array([0, 16, 0])) @ R.T
            n = np.cross(P[1] - P[0], P[3] - P[0])
            nn = np.linalg.norm(n)
            if nn < 1e-9:
                continue
            n /= nn
            shade = 0.55 + 0.45 * abs(float(n @ (R @ LIGHT)))
            sx = W / 2 - P[:, 0] * S
            sy = H / 2 - P[:, 1] * S + 4 * S
            sz = P[:, 2] + bias
            for tri in ((0, 1, 2), (0, 2, 3)):
                xs, ys = sx[list(tri)], sy[list(tri)]
                x_min, x_max = int(max(0, math.floor(xs.min()))), int(min(W - 1, math.ceil(xs.max())))
                y_min, y_max = int(max(0, math.floor(ys.min()))), int(min(H - 1, math.ceil(ys.max())))
                if x_min > x_max or y_min > y_max:
                    continue
                gx, gy = np.meshgrid(np.arange(x_min, x_max + 1) + 0.5, np.arange(y_min, y_max + 1) + 0.5)
                (x0, x1, x2), (y0, y1, y2) = xs, ys
                den = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
                if abs(den) < 1e-9:
                    continue
                a = ((y1 - y2) * (gx - x2) + (x2 - x1) * (gy - y2)) / den
                b = ((y2 - y0) * (gx - x2) + (x0 - x2) * (gy - y2)) / den
                c = 1 - a - b
                m = (a >= -1e-4) & (b >= -1e-4) & (c >= -1e-4)
                if not m.any():
                    continue
                z = a * sz[tri[0]] + b * sz[tri[1]] + c * sz[tri[2]]
                uv = uvs[list(tri)]
                u = a * uv[0, 0] + b * uv[1, 0] + c * uv[2, 0]
                v = a * uv[0, 1] + b * uv[1, 1] + c * uv[2, 1]
                tu = np.clip(np.floor(u * tw - 1e-4 * np.sign(uv[1, 0] - uv[0, 0] + 1e-9)), 0, tw - 1).astype(int)
                tv = np.clip(np.floor(v * th - 1e-4), 0, th - 1).astype(int)
                texel = tex[tv, tu]
                m &= texel[..., 3] > 0.5
                sub_z = zbuf[y_min:y_max + 1, x_min:x_max + 1]
                m &= z < sub_z
                if not m.any():
                    continue
                sub_z[m] = z[m]
                color[y_min:y_max + 1, x_min:x_max + 1][m] = texel[..., :3][m] * shade
                alpha[y_min:y_max + 1, x_min:x_max + 1][m] = 1
    img = np.dstack([color, alpha])
    return Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8), 'RGBA')
