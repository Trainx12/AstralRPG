"""Caminos del lobby (19/11): plaza -> estacion del tren y plaza -> castillo.

Usa la misma mezcla que los caminos de la plaza (tierra gruesa + granito, medida del
mapa). El resto del pasto con manchas de tierra (zonas que no se pisan) pasa a pasto y
musgo. Solo cambia el bloque de arriba del suelo; nunca piedra, caminos ni edificios.
Salida: cubos Sponge v3 (como lobby_terreno.py) que se pegan SIN -a.

  python datapack-src/lobby_caminos.py --hoy .local/lobby/actual-19-11b/region \
      --config .local/lobby/caminos.json --out .local/lobby/caminos-v1
"""
import argparse, json
from collections import Counter
from pathlib import Path
import numpy as np
import lobby_terreno as lt

BROWN = {'coarse_dirt', 'rooted_dirt', 'packed_mud', 'dirt', 'granite'}
GREEN = {'grass_block', 'moss_block'}
SOFT = BROWN | GREEN
PLANTS = {'short_grass', 'tall_grass', 'fern', 'large_fern', 'bush', 'short_dry_grass', 'tall_dry_grass'}


def segment_distance(xx, zz, points):
    d = np.full(xx.shape, np.inf)
    for a, b in zip(points, points[1:]):
        a, b = np.array(a, float), np.array(b, float)
        delta = b-a
        f = np.clip(((xx-a[0])*delta[0]+(zz-a[1])*delta[1])/float(delta@delta), 0, 1)
        d = np.minimum(d, np.hypot(xx-a[0]-f*delta[0], zz-a[1]-f*delta[1]))
    return d


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--hoy', type=Path, required=True)
    p.add_argument('--config', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    out = lt.private(args.out)
    if out.exists():
        raise ValueError('Usar salida nueva')
    cfg = json.loads(args.config.read_text(encoding='utf-8-sig'))
    bounds = cfg['bounds']
    x0, z0, x1, z1 = bounds
    world = lt.World.load(args.hoy, bounds)
    h, t = world.surface(bounds, ground=True)
    name = lambda v: lt.base(world.names[int(v)])
    zz, xx = np.indices(h.shape)
    xx = xx+x0
    zz = zz+z0
    low, high = cfg['y']
    soft = np.vectorize(lambda v: name(v) in SOFT)(t) & (h >= low) & (h <= high)
    keep = np.zeros(h.shape, bool)
    for ax, az, bx, bz in cfg['conservar']:
        keep |= (xx >= ax) & (xx <= bx) & (zz >= az) & (zz <= bz)
    for cx, cz, r0, r1 in cfg.get('anillos', []):
        r = np.hypot(xx-cx, zz-cz)
        keep |= (r >= r0) & (r <= r1)
    # Mezcla del camino medida en la plaza (zona conservada).
    mix = Counter(world.names[int(v)] for v, k in zip(t.flat, keep.flat) if k and name(v) in BROWN)
    if not mix:
        raise ValueError('La plaza no tiene camino medido')
    green = Counter(world.names[int(v)] for v, k, s in zip(t.flat, keep.flat, soft.flat) if s and not k and name(v) in GREEN)
    seed = cfg['seed']
    path = np.zeros(h.shape, bool)
    for camino in cfg['caminos']:
        d = segment_distance(xx, zz, camino['puntos'])
        edge = camino['ancho']/2+np.vectorize(lambda x, z: (lt.noise(x, z, 5, seed+1)-.5)*2.2)(xx, zz)
        path |= d <= edge
    changes = {}
    counts = Counter()
    for z, x in zip(*np.nonzero(soft & ~keep)):
        wx, wz, y = int(x+x0), int(z+z0), int(h[z, x])
        before = world.get(wx, y, wz)
        if path[z, x]:
            # Mismo orden que la plaza: manchas grandes de granito sobre tierra gruesa.
            state = lt.choose(mix, lt.noise(wx, wz, 6, seed+2))
            kind = 'camino'
        elif lt.base(before) in BROWN:
            state = lt.choose(green, lt.noise(wx, wz, 6, seed+3))
            kind = 'verde'
        else:
            continue
        if (wx, y, wz) in world.tiles or before == state:
            continue
        changes[wx, y, wz] = state
        counts[kind] += 1
        above = world.get(wx, y+1, wz)
        if kind == 'camino' and lt.base(above) in PLANTS:
            changes[wx, y+1, wz] = 'minecraft:air'
            top = world.get(wx, y+2, wz)
            if lt.base(top) in PLANTS:
                changes[wx, y+2, wz] = 'minecraft:air'
    out.mkdir(parents=True)
    sectors = lt.export(world, changes, out)
    f = out/'pegar.txt'
    f.write_text(f.read_text(encoding='utf8').replace('//paste -a', '//paste'), encoding='utf8')
    lt.previews(world, changes, bounds, out/'previews')
    info = {'cambios': len(changes), 'por_tipo': dict(counts), 'sectores': len(sectors),
            'mezcla_camino': dict(mix), 'mezcla_verde': dict(green), 'sectors': sectors}
    (out/'cambios.json').write_text(json.dumps([[*k, v] for k, v in changes.items()]), encoding='utf8')
    (out/'manifest.json').write_text(json.dumps(info, indent=1)+'\n', encoding='utf8')
    print(json.dumps({k: v for k, v in info.items() if k != 'sectors'}))


if __name__ == '__main__':
    main()
