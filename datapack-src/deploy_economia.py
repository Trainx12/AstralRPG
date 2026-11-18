"""Economia E1 (18/11): FINAL nuevo = ultimo FINAL + precios dibujados del Herrero y de las gachas.

Solo reemplaza las barras +N del Herrero (servicios/bar_level*) y las tarjetas de tirada de las gachas
(servicios/gacha_*_x*), que muestran la plata. Todo lo demas queda como en la base.
Uso: python deploy_economia.py [--base <FINAL.zip>]
"""
import argparse
import hashlib
import re
from deploy_guia_esc import rewrite
from final_base import select_base
from terceros import privado

OUT = privado() / 'build/entregas/economia-e1'
PRECIOS = re.compile(r'^assets/astral/textures/item/servicios/(bar_level\d+_\d+|gacha_[a-z]+_x\d+_\d+)\.png$')


def precios():
    from services_ui import assets as servicios
    from market_ui import assets as gachas
    out = {}
    for f in (servicios, gachas):
        files, _ = f()
        out.update({n: b for n, b in files.items() if PRECIOS.match(n)})
    return out


def change(names, z):
    files = precios()
    faltan = [n for n in files if n not in names]
    assert not faltan, f'la base no tiene {faltan[:3]}'
    return {n: b for n, b in files.items() if z.read(n) != b}


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
