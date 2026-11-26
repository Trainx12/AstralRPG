"""Manzanas de Mazmorra 21/11: FINAL nuevo = ultimo FINAL + texturas/modelos de manzana_t2..t10 (manzanas.py).

Uso: python deploy_manzanas_21_11.py [--base <FINAL.zip>]
"""
import argparse
import hashlib

from deploy_guia_esc import rewrite
from final_base import select_base
from terceros import privado

OUT = privado() / 'build/entregas/manzanas-21-11'


def change(names, z):
    from manzanas import pack_assets
    out = pack_assets()
    print(len(out), 'archivos de manzanas')
    return out


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--base')
    args = ap.parse_args()
    base = select_base(output=OUT, explicit=args.base)
    OUT.mkdir(parents=True, exist_ok=True)
    final = OUT / 'AstralRPG-Textures.zip'
    rewrite(base, final, change)
    sha = hashlib.sha1(final.read_bytes()).hexdigest()
    (OUT / 'pack.sha1').write_text(sha + '\n')
    print('base', base)
    print('FINAL', final, sha)
