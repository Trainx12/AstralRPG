"""Lee la nave (spaceship.schem, mapa de terceros: solo en .local/nave) y calcula las salas de la Nave del Vacio.

python tools/nave_salas.py [--schem .local/nave/spaceship.schem]

La nave es una mano HUECA: casco cerrado con un gran espacio adentro (y capsulas flotando). Todo pasa dentro del
casco, caminando sobre su piso. Cada sala es una zona de la mano (muneca, dedos, palma; el pulgar queda cerrado):
cada celda de aire de adentro va a la zona cuya semilla le queda mas cerca caminando por el aire de adentro, y donde
dos zonas se tocan se pone una pared de BARRERA (no se puede pasar a otra sala ni volver; solo las compuertas llevan).

Salida (coordenadas del mundo = schematic + nave.ORIGEN, sin bloques del mapa):
- datapack-src/nave_salas.json: llegada, compuerta (centro) y apariciones de cada sala (solo sobre el piso de adentro).
- datapack-src/nave_barreras.txt: tiras "x0 x1 y z" de aire que se vuelve barrera.
- datapack-src/nave_zonas.txt: por columna (x, z), que zonas hay adentro (para devolver a quien/lo que se salga).
Imagen de control: .local/nave/salas.png.
"""
import argparse
import collections
import gzip
import json
import math
import struct
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'datapack-src'))
from nave import ORIGEN, SALAS  # noqa: E402

PASO = 4          # una aparicion por celda de 4x4
LEJOS = 5         # apariciones a 5+ bloques de la llegada
MARGEN = 1         # apariciones a 1+ bloque de una barrera


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


VEC6 = ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))


def crecer(m, dentro=None, pasos=1):
    """Dilata la mascara 1 bloque por paso (6 vecinos), opcionalmente sin salir de 'dentro'."""
    for _ in range(pasos):
        g = m.copy()
        g[1:] |= m[:-1]
        g[:-1] |= m[1:]
        g[:, 1:] |= m[:, :-1]
        g[:, :-1] |= m[:, 1:]
        g[:, :, 1:] |= m[:, :, :-1]
        g[:, :, :-1] |= m[:, :, 1:]
        m = g if dentro is None else (g & dentro)
    return m


def inundar(semilla, dentro):
    """Todo lo de 'dentro' conectado (6 vecinos) con la semilla."""
    m = semilla & dentro
    while True:
        g = crecer(m, dentro)
        if g.sum() == m.sum():
            return m
        m = g


def capsulas(bloques):
    """Aire de las capsulas: el aire de afuera (conectado al borde) que esta encerrado entre paredes cercanas.
    El hueco del casco queda sellado (no es afuera) y el espacio abierto se reconoce por estar lejos de todo."""
    aire = ~bloques
    borde = np.zeros(aire.shape, bool)
    borde[[0, -1]] = borde[:, [0, -1]] = borde[:, :, [0, -1]] = True
    afuera = inundar(borde & aire, aire)
    # Distancia (en cubos) a lo que no es aire de afuera, hasta 8.
    dist = np.zeros(aire.shape, np.int8)
    otro = ~afuera
    for d in range(1, 9):
        dist[afuera & ~otro] = d
        otro = crecer(otro)
    # Espacio abierto: desde lo lejano (>= 7) por pasos anchos (>= 3); una puerta de 3 no deja pasar.
    abierto = inundar(afuera & (dist >= 7), afuera & (dist >= 3))
    nucleo = afuera & (dist >= 3) & ~abierto
    return crecer(nucleo, afuera & ~abierto, 3) | nucleo


def salas(path):
    W, H, L, b = leer_schem(path)
    bloques = np.array([v != 'minecraft:air' for v in b], bool).reshape(H, L, W)
    caps = capsulas(bloques)
    zona = np.full(bloques.shape, -1, np.int8)
    for i, s in enumerate(SALAS):
        x, y, z = s['capsula']
        cerca = [(abs(dy) + abs(dz) + abs(dx), y + dy, z + dz, x + dx) for dy in range(-5, 6) for dz in range(-5, 6)
                 for dx in range(-5, 6) if caps[y + dy, z + dz, x + dx]]
        if not cerca:
            raise SystemExit(f'{s["id"]}: {s["capsula"]} no esta adentro de una capsula (cambiar en nave.py)')
        _, y, z, x = min(cerca)
        sem = np.zeros(bloques.shape, bool)
        sem[y, z, x] = True
        m = inundar(sem, caps)
        if (zona[m] >= 0).any():
            raise SystemExit(f'{s["id"]}: comparte capsula con otra sala')
        zona[m] = i
    usadas = zona >= 0
    # Barreras: el aire que toca una capsula usada y no es parte de ella (puertas, ventanas y huecos al vacio).
    barrera = crecer(usadas) & ~usadas & ~bloques
    libre = usadas
    # Piso caminable: aire de la sala con bloque abajo y 3 de alto (endermans).
    piso = np.zeros(bloques.shape, bool)
    piso[1:H - 2] = libre[1:H - 2] & libre[2:H - 1] & libre[3:H] & bloques[0:H - 3]
    cerca_barrera = crecer(barrera, None, MARGEN)
    mundo = lambda c: [int(c[0]) + ORIGEN[0], int(c[1]) + ORIGEN[1], int(c[2]) + ORIGEN[2]]
    out = []
    for i, s in enumerate(SALAS):
        celdas = {(int(x), int(y), int(z)) for y, z, x in zip(*np.nonzero(piso & (zona == i)))}
        # Solo la parte caminable conectada con el punto de la capsula (pasos de 1 bloque).
        sx, sy, sz = s['capsula']
        inicio = min(celdas, key=lambda c: (c[0] - sx) ** 2 + (c[2] - sz) ** 2 + (c[1] - sy) ** 2)
        visto, cola = {inicio}, [inicio]
        while cola:
            x, y, z = cola.pop()
            for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                for dy in (-1, 0, 1):
                    n = (x + dx, y + dy, z + dz)
                    if n in celdas and n not in visto:
                        visto.add(n)
                        cola.append(n)
        ancho = lambda c: all(any((c[0] + dx, c[1] + dy, c[2] + dz) in visto for dy in (-1, 0, 1))
                              for dx in (-1, 0, 1) for dz in (-1, 0, 1))
        anchas = [c for c in visto if ancho(c) and not cerca_barrera[c[1], c[2], c[0]]]
        cerca = lambda p: min(anchas, key=lambda c: (c[0] - p[0]) ** 2 + (c[2] - p[1]) ** 2 + (c[1] - sy) ** 2 / 4)
        llegada, centro = cerca(s['llegada']), cerca(s['centro'])
        techo = lambda c: next((k for k in range(1, H - c[1]) if bloques[c[1] + k, c[2], c[0]]), 99)
        puntos, usadas_c = [], set()
        for c in sorted(anchas, key=lambda c: (c[0], c[2], c[1])):
            celda = (c[0] // PASO, c[2] // PASO)
            if celda in usadas_c or math.dist((c[0], c[2]), (llegada[0], llegada[2])) < LEJOS:
                continue
            usadas_c.add(celda)
            puntos.append(c)
        out.append(dict(id=s['id'], celdas=len(visto), llegada=mundo(llegada), centro=mundo(centro),
                        puntos=[mundo(p) for p in puntos]))
        print(s['id'], len(visto), 'celdas de piso,', len(puntos), 'apariciones, llegada', out[-1]['llegada'],
              'compuerta', out[-1]['centro'], 'techo sobre la compuerta', techo(centro))
    # Tiras de barrera (x0..x1 seguidas en la misma fila y, z).
    tiras = []
    for y in range(H):
        for z in range(L):
            fila = np.nonzero(barrera[y, z])[0]
            if not len(fila):
                continue
            x0 = prev = int(fila[0])
            for x in list(map(int, fila[1:])) + [None]:
                if x is not None and x == prev + 1:
                    prev = x
                    continue
                tiras.append((x0 + ORIGEN[0], prev + ORIGEN[0], y + ORIGEN[1], z + ORIGEN[2]))
                if x is not None:
                    x0 = prev = x
    print(int(barrera.sum()), 'barreras en', len(tiras), 'tiras')
    # Zonas por columna: bit i = la sala i tiene aire en esa columna; y minima y maxima de ese aire.
    mascara = np.zeros((L, W), np.int32)
    for i in range(len(SALAS)):
        mascara |= np.any(zona == i, axis=0).astype(np.int32) << i
    dobles = sum(bin(int(m)).count('1') > 1 for m in mascara.flat)
    if dobles:   # donde dos capsulas se tocan (separadas por barrera): la altura es la de las dos juntas
        print(dobles, 'columnas con dos salas')
    ymin = np.where(usadas.any(axis=0), usadas.argmax(axis=0), 0)
    ymax = np.where(usadas.any(axis=0), H - 1 - usadas[::-1].argmax(axis=0), 0)
    return out, tiras, (mascara, ymin, ymax), (W, H, L, bloques, zona, usadas)


def imagen(datos, mapa, path):
    from PIL import Image, ImageDraw
    W, H, L, bloques, zona, dentro = mapa
    S = 3
    colores = [(90, 60, 160), (60, 130, 170), (60, 160, 100), (160, 140, 50), (170, 80, 60), (150, 60, 150), (50, 50, 50)]
    im = Image.new('RGB', (W * S, L * S), (8, 8, 12))
    dr = ImageDraw.Draw(im)
    for z in range(L):
        for x in range(W):
            ys = np.nonzero(dentro[:, z, x])[0]
            if len(ys):
                c = colores[min(zona[ys[0], z, x], len(colores) - 1)]
                dr.rectangle([x * S, z * S, x * S + S - 1, z * S + S - 1], fill=c)
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
    datos, tiras, mascara, mapa = salas(args.schem)
    src = ROOT / 'datapack-src'
    (src / 'nave_salas.json').write_text(json.dumps(datos, indent=1) + '\n', encoding='utf-8')
    (src / 'nave_barreras.txt').write_text(
        '# x0 x1 y z (mundo): aire de adentro de la nave que se vuelve barrera (tools/nave_salas.py)\n'
        + ''.join(f'{t[0]} {t[1]} {t[2]} {t[3]}\n' for t in tiras), encoding='utf-8')
    mascara, ymin, ymax = mascara
    (src / 'nave_zonas.txt').write_text(
        f'# zonas por columna (tools/nave_salas.py): fila = z desde {ORIGEN[2]}, 6 hex por x desde {ORIGEN[0]}, '
        f'y desde {ORIGEN[1]}: bits de salas (bit i = sala i), y minima y maxima del aire de adentro\n'
        + ''.join(''.join(f'{int(m):02x}{int(a):02x}{int(b):02x}' for m, a, b in zip(*filas)) + '\n'
                  for filas in zip(mascara, ymin, ymax)), encoding='utf-8')
    imagen(datos, mapa, ROOT / '.local/nave/salas.png')
    print('ok')
