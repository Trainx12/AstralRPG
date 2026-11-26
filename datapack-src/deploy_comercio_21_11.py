"""Comercio 21/11: FINAL nuevo = ultimo FINAL + Casa de Comercio (subastas_inicio 6 filas), Efectos con el diseno
nuevo del dueno (fondo + pestanas/interruptores) e icono de Party del Menu Astral (Gemini).

Solo cambia: fondos font/ventanas2011/*, piezas item/ventanas1911/* que cambiaron, providers de ventanas en la
fuente default y el icono astral:menu/icon_party. Uso: python deploy_comercio_21_11.py [--base <FINAL.zip>]
"""
import argparse
import hashlib
import json

from deploy_guia_esc import rewrite
from final_base import select_base
from terceros import privado

OUT = privado() / 'build/entregas/comercio-21-11'
FONT = 'assets/minecraft/font/default.json'


def change(names, z):
    import ventanas_19_11
    import menu_ui
    vfiles, vprov = ventanas_19_11.assets()
    out = {n: b for n, b in vfiles.items() if n not in names or z.read(n) != b}
    mfiles, _ = menu_ui.assets()
    out.update({n: b for n, b in mfiles.items() if '/menu/icon_party' in n})
    font = json.loads(z.read(FONT))
    propios = {c for p in vprov for row in p.get('chars', []) for c in row} | {c for p in vprov for c in p.get('advances', {})}
    font['providers'] = vprov + [p for p in font['providers']
                                 if not ({c for row in p.get('chars', []) for c in row} | set(p.get('advances', {}))) & propios]
    out[FONT] = json.dumps(font, ensure_ascii=False).encode()
    print(len(out), 'archivos cambiados:', *sorted(n for n in out if 'efectos' in n or 'subastas' in n or 'party' in n)[:40], sep='\n  ')
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
