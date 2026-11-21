"""Paginas 21/11: FINAL nuevo = ultimo FINAL + segundas paginas de Portales y Minas (flechas Gemini)
y el cartel de la Guia Astral abajo al medio en /menu.

Solo cambia: fondos de viajes (font/viajes/*), fondo del Menu Astral (font/menu/principal_*) y sus providers
en la fuente default. Uso: python deploy_paginas_21_11.py [--base <FINAL.zip>]
"""
import argparse
import hashlib
import json

from deploy_guia_esc import rewrite
from final_base import select_base
from terceros import privado

OUT = privado() / 'build/entregas/paginas-21-11'
FONT = 'assets/minecraft/font/default.json'


def chars_of(p):
    return {c for row in p.get('chars', []) for c in row} | set(p.get('advances', {}))


def change(names, z):
    import travel_ui
    import menu_ui
    tfiles, tprov = travel_ui.assets()
    mfiles, mprov = menu_ui.assets()
    out = {n: b for n, b in tfiles.items() if '/font/viajes/' in n}
    out.update({n: b for n, b in mfiles.items() if '/font/menu/principal_' in n})
    nuevos = tprov + mprov
    propios = set().union(*map(chars_of, nuevos))
    font = json.loads(z.read(FONT))
    viejos = [p for p in font['providers'] if chars_of(p) & propios]
    # Solo se reemplazan los providers de viajes y del menu (mismos archivos o mismos caracteres).
    for p in viejos:
        f = p.get('file', '')
        assert p['type'] == 'space' or f.startswith(('astral:font/viajes/', 'astral:font/menu/principal_')), p
    font['providers'] = nuevos + [p for p in font['providers'] if p not in viejos]
    out[FONT] = json.dumps(font, ensure_ascii=False).encode()
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
