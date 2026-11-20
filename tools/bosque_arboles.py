"""Detecta los arboles del Bosque Astral armado y guarda sus cajas para que vuelvan a crecer.

python tools/bosque_arboles.py
Lee .local/bosque-mapas/entrega/region (salida de tools/bosque_armar.py) y escribe
datapack-src/bosque_arboles.json: solo coordenadas (ningun bloque del mapa), lo usa bosque_talar.py.

Arbol = troncos unidos (26 vecinos) + las hojas que les quedan mas cerca (camino por hojas).
Punto de control = el tronco mas bajo: si queda vacio, el arbol se talo.
"""
import json
import sys
from collections import deque
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT / 'datapack-src'))
from bosque_mapa_leer import load_box  # noqa: E402
import bosque_talar as B  # noqa: E402

REGION = ROOT / '.local/bosque-mapas/entrega/region'
INFO = ROOT / '.local/bosque-mapas/datos/info.json'
OUT = ROOT / 'datapack-src/bosque_arboles.json'
TOP = 230


def detect(arr, pal, y0):
    names = [p.split('[')[0] for p in pal]
    is_log = np.array([n.endswith(('_log', '_wood', '_stem')) or n.endswith('bee_nest') for n in names])
    is_leaf = np.array(['leaves' in n or n.endswith(('vine', 'vines', 'cocoa', 'pale_moss_carpet', 'pale_hanging_moss'))
                        for n in names])
    logm = is_log[arr]; leafm = is_leaf[arr]
    H, L, W = arr.shape
    lab = np.zeros(arr.shape, np.int32)
    n = 0
    pts = np.argwhere(logm)
    nb26 = [(dy, dz, dx) for dy in (-1, 0, 1) for dz in (-1, 0, 1) for dx in (-1, 0, 1) if (dy, dz, dx) != (0, 0, 0)]
    for y, z, x in pts:
        if lab[y, z, x]:
            continue
        n += 1
        lab[y, z, x] = n
        q = deque([(y, z, x)])
        while q:
            a, b, c = q.popleft()
            for dy, dz, dx in nb26:
                p = (a + dy, b + dz, c + dx)
                if 0 <= p[0] < H and 0 <= p[1] < L and 0 <= p[2] < W and logm[p] and not lab[p]:
                    lab[p] = n; q.append(p)
    # Hojas: BFS desde todos los troncos a la vez (6 vecinos, solo por hojas).
    q = deque(map(tuple, np.argwhere(lab > 0)))
    nb6 = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
    while q:
        a, b, c = q.popleft()
        v = lab[a, b, c]
        for dy, dz, dx in nb6:
            p = (a + dy, b + dz, c + dx)
            if 0 <= p[0] < H and 0 <= p[1] < L and 0 <= p[2] < W and leafm[p] and not lab[p]:
                lab[p] = v; q.append(p)
    trees = []
    flat = lab.ravel()
    order = np.argsort(flat, kind='stable')
    counts = np.bincount(flat, minlength=n + 1)
    starts = np.concatenate([[0], np.cumsum(counts)])
    logflat = logm.ravel()
    for t in range(1, n + 1):
        sel = order[starts[t]:starts[t + 1]]
        ys, zs, xs = np.unravel_index(sel, arr.shape)
        lg = logflat[sel]
        if lg.sum() < 2:
            continue
        ly, lz, lx = ys[lg], zs[lg], xs[lg]
        k = np.lexsort((np.abs(lx - lx.mean()) + np.abs(lz - lz.mean()), ly))[0]
        trees.append({'base': [int(lx[k]), int(ly[k]) + y0, int(lz[k])],
                      'box': [int(xs.min()), int(ys.min()) + y0, int(zs.min()),
                              int(xs.max()), int(ys.max()) + y0, int(zs.max())],
                      'troncos': int(lg.sum()), 'bloques': int(len(sel))})
    return merge_branches(trees)


def merge_branches(trees):
    """Ramas sueltas (pocos troncos, dentro de la caja de un arbol grande) se suman a ese arbol."""
    trees = sorted(trees, key=lambda t: -t['troncos'])
    out = []
    for t in trees:
        host = None
        if t['troncos'] <= 16:
            bx = t['box']
            for h in out:
                hb = h['box']
                if all(hb[i] - 2 <= bx[i] for i in range(3)) and all(bx[i] <= hb[i] + 2 for i in range(3, 6)):
                    host = h; break
        if host:
            hb = host['box']
            host['box'] = [min(hb[i], bx[i]) for i in range(3)] + [max(hb[i], bx[i]) for i in range(3, 6)]
            host['troncos'] += t['troncos']; host['bloques'] += t['bloques']
        else:
            out.append(dict(t))
    return out


def main():
    S = B.SIZE
    arr, pal = load_box(REGION, 0, S - 1, 0, S - 1, B.LIVE_BOTTOM, TOP)
    trees = detect(arr, pal, B.LIVE_BOTTOM)
    trees.sort(key=lambda t: (t['base'][2], t['base'][0]))
    info = json.loads(INFO.read_text(encoding='utf-8'))
    data = {'spawn': info['spawn'], 'arboles': [{'base': t['base'], 'box': t['box']} for t in trees]}
    OUT.write_text(json.dumps(data, separators=(',', ':')) + '\n', encoding='utf-8')
    big = sorted(trees, key=lambda t: -t['bloques'])[:5]
    print('arboles', len(trees), 'troncos totales', sum(t['troncos'] for t in trees))
    print('mas grandes', [(t['box'], t['bloques']) for t in big])
    print('altura max', max(t['box'][4] for t in trees))


if __name__ == '__main__':
    main()
