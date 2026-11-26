"""24/11 (dueno): al picar, la broca del taladro gira (no golpea como pico).
FINAL nuevo = FINAL del server (f6af9faa, iconos-efectos-23-11) + modelos girados de la broca (herramientas3d.giros)
+ items/taladro_*.json que eligen un giro al azar mientras se aprieta picar. El golpe del brazo lo saca el datapack
(minecraft:swing_animation none: build.py para nuevos, gameplay.py upgrade/taladro_sin_golpe para los viejos).

Uso: python deploy_taladro_giro_24_11.py [--base <FINAL.zip>]
"""
import argparse
import hashlib

import herramientas3d as H
from deploy_guia_esc import rewrite
from terceros import privado

OUT = privado() / 'build/entregas/taladro-giro-24-11'
BASE = privado() / 'build/entregas/iconos-efectos-23-11/AstralRPG-Textures.zip'


def change(names, z):
    mine = {n: b for n, b in H.assets().items() if '/taladro_' in n}
    out = {}
    for n, b in mine.items():
        if n.endswith('.png') or n.endswith('.mcmeta'):
            continue                                    # texturas: las mismas del FINAL
        if '_giro' in n:
            assert n not in names, n
            out[n] = b
        elif n.startswith('assets/astral/items/'):
            assert n in names, n
            out[n] = b
        else:
            assert n in names, n                        # modelo quieto: tiene que ser el mismo que ya esta
            assert z.read(n) == b, f'el modelo cambio: {n}'
    return out


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--base', default=str(BASE))
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    final = OUT / 'AstralRPG-Textures.zip'
    rewrite(args.base, final, change)
    sha = hashlib.sha1(final.read_bytes()).hexdigest()
    (OUT / 'pack.sha1').write_text(sha + '\n')
    print('base', args.base, hashlib.sha1(open(args.base, 'rb').read()).hexdigest())
    print('FINAL', final, sha)
