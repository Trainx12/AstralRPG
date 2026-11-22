"""Lee la nave (spaceship.schem, mapa de terceros: solo en .local/nave) y calcula las salas de la Nave del Vacio.

python tools/nave_salas.py [--schem .local/nave/spaceship.schem]
Salida: datapack-src/nave_salas.json (solo coordenadas: llegada, compuerta, apariciones y limites de cada sala,
en coordenadas del mundo = schematic + nave.ORIGEN). La imagen de control queda en .local/nave/salas.png.
"""
import argparse
import collections
import gzip
import json
import math
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'datapack-src'))
from nave import ORIGEN, SALAS  # noqa: E402

PASO = 4          # una aparicion por celda de 4x4
LEJOS = 8         # apariciones a 8+ bloques de la llegada


def leer_schem(path):
    d = gzip.open(path).read()
    p = 0

    def rd(n):
        nonlocal p
        b = d[p:p + n]
        p += n
        return b

    def tag(t):
        fmt = {1: '>b', 2: '>h', 3: '>i', 4: '>q', 5: '>f', 6: '>d'}
        if t in fmt:
            return struct.unpack(fmt[t], rd(struct.calcsize(fmt[t])))[0]
        if t == 7:
            return rd(struct.unpack('>i', rd(4))[0])
        if t == 8:
            return rd(struct.unpack('>H', rd(2))[0]).decode()
        if t == 9:
            et = rd(1)[0]
            return [tag(et) for _ in range(struct.unpack('>i', rd(4))[0])]
        if t == 10:
            o = {}
            while (et := rd(1)[0]) != 0:
                k = rd(struct.unpack('>H', rd(2))[0]).decode()
                o[k] = tag(et)
            return o
        if t == 11:
            n = struct.unpack('>i', rd(4))[0]
            return list(struct.unpack('>%di' % n, rd(4 * n)))
        if t == 12:
            n = struct.unpack('>i', rd(4))[0]
            return list(struct.unpack('>%dq' % n, rd(8 * n)))
        raise ValueError(t)

    rd(1)
    rd(struct.unpack('>H', rd(2))[0])
    root = tag(10)
    root = root.get('Schematic', root)
    W, H, L = root['Width'], root['Height'], root['Length']
    inv = {v: k.split('[')[0] for k, v in root['Palette'].items()}
    vals, i, data = [], 0, root['BlockData']
    while i < len(data):
        v = s = 0
        while True:
            b = data[i]
            i += 1
            v |= (b & 127) << s
            s += 7
            if not b & 128:
                break
        vals.append(inv[v])
    return W, H, L, vals


def salas(path):
    W, H, L, b = leer_schem(path)
    aire = lambda x, y, z: 0 <= x < W and 0 <= y < H and 0 <= z < L and b[(y * L + z) * W + x] == 'minecraft:air'
    piso = lambda x, y, z: 0 <= y - 1 and not aire(x, y - 1, z) and aire(x, y, z) and aire(x, y + 1, z) and aire(x, y + 2, z)
    out = []
    for sala in SALAS:
        x0, y0, z0, x1, y1, z1 = sala['caja']           # caja del schematic donde buscar el piso
        celdas = {(x, y, z) for x in range(x0, x1 + 1) for z in range(z0, z1 + 1) for y in range(y0, y1 + 1) if piso(x, y, z)}
        # Quedarse con la parte conectada mas grande (pasos de 1 bloque).
        visto, mejor = set(), []
        for s in celdas:
            if s in visto:
                continue
            q, comp = [s], []
            visto.add(s)
            while q:
                x, y, z = q.pop()
                comp.append((x, y, z))
                for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    for dy in (-1, 0, 1):
                        n = (x + dx, y + dy, z + dz)
                        if n in celdas and n not in visto:
                            visto.add(n)
                            q.append(n)
            if len(comp) > len(mejor):
                mejor = comp
        piso_ok = set(mejor)
        libre = lambda c: all((c[0] + dx, c[1], c[2] + dz) in piso_ok for dx in (-1, 0, 1) for dz in (-1, 0, 1))
        anchas = [c for c in mejor if libre(c)]
        cx, cz = sala['centro']
        centro = min(anchas, key=lambda c: (c[0] - cx) ** 2 + (c[2] - cz) ** 2)
        lx, lz = sala['llegada']
        llegada = min(anchas, key=lambda c: (c[0] - lx) ** 2 + (c[2] - lz) ** 2)
        puntos, usadas = [], set()
        for c in sorted(anchas, key=lambda c: (c[0], c[2], c[1])):
            celda = (c[0] // PASO, c[2] // PASO)
            if celda in usadas or math.dist((c[0], c[2]), (llegada[0], llegada[2])) < LEJOS:
                continue
            usadas.add(celda)
            puntos.append(c)
        xs, ys, zs = [c[0] for c in mejor], [c[1] for c in mejor], [c[2] for c in mejor]
        mundo = lambda c: [c[0] + ORIGEN[0], c[1] + ORIGEN[1], c[2] + ORIGEN[2]]
        out.append(dict(id=sala['id'], celdas=len(mejor), llegada=mundo(llegada), centro=mundo(centro),
                        puntos=[mundo(p) for p in puntos],
                        # limites: si un jugador sale de esta caja (cae al casco hueco), vuelve a la llegada
                        limites=[min(xs) + ORIGEN[0] - 3, min(ys) + ORIGEN[1] - 4, min(zs) + ORIGEN[2] - 3,
                                 max(xs) + ORIGEN[0] + 3, max(ys) + ORIGEN[1] + 25, max(zs) + ORIGEN[2] + 3]))
        print(sala['id'], len(mejor), 'celdas,', len(puntos), 'apariciones, llegada', out[-1]['llegada'], 'centro', out[-1]['centro'])
    return out, (W, H, L, b)


def imagen(datos, mapa, path):
    from PIL import Image, ImageDraw
    W, H, L, b = mapa
    S = 3
    im = Image.new('RGB', (W * S, L * S), (12, 10, 20))
    dr = ImageDraw.Draw(im)
    for z in range(L):
        for x in range(W):
            for y in range(H - 1, -1, -1):
                if b[(y * L + z) * W + x] != 'minecraft:air':
                    g = 40 + y
                    dr.rectangle([x * S, z * S, x * S + S - 1, z * S + S - 1], fill=(g // 2, g // 3, g))
                    break
    loc = lambda c: ((c[0] - ORIGEN[0]) * S, (c[2] - ORIGEN[2]) * S)
    for s in datos:
        for p in s['puntos']:
            x, z = loc(p)
            dr.rectangle([x, z, x + S, z + S], fill=(240, 80, 80))
        x, z = loc(s['llegada'])
        dr.ellipse([x - 5, z - 5, x + 5, z + 5], fill=(80, 240, 120))
        x, z = loc(s['centro'])
        dr.ellipse([x - 5, z - 5, x + 5, z + 5], fill=(80, 160, 255))
        dr.text((x + 8, z - 6), s['id'], fill=(255, 255, 0))
    im.save(path)


if __name__ == '__main__':
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument('--schem', default=str(ROOT / '.local/nave/spaceship.schem'))
    args = a.parse_args()
    datos, mapa = salas(args.schem)
    (ROOT / 'datapack-src/nave_salas.json').write_text(json.dumps(datos, indent=1) + '\n', encoding='utf-8')
    imagen(datos, mapa, ROOT / '.local/nave/salas.png')
    print('ok')
