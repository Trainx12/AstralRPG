"""Ventanas 20/11 (disenos Gemini): FINAL nuevo = ultimo FINAL + fondos de Comisiones y Subastas y Banco.

Solo cambia: los dos fondos (font/ventanas2011/*, en pedazos) y los providers de ventanas1911 en
la fuente default. Uso: python deploy_ventanas_20_11.py [--base <FINAL.zip>]
"""
import argparse
import hashlib
import json

from deploy_guia_esc import rewrite
from final_base import select_base
from terceros import privado

OUT = privado() / 'build/entregas/ventanas-20-11-niveles'
FONT = 'assets/minecraft/font/default.json'


def change(names, z):
    import ventanas_19_11
    vfiles, vprov = ventanas_19_11.assets()
    # Los fondos van partidos en pedazos de hasta 224 px: el juego no carga glifos de mas de 256 px (20/11 se vio
    # un cuadradito vacio con el fondo entero de 448 px).
    # + lo de ventanas1911 que cambio (20/11: botones y marco del Banco recortados de nuevo)
    out = {n: b for n, b in vfiles.items() if '/font/ventanas2011/' in n or n not in names or z.read(n) != b}
    assert sum('/font/ventanas2011/' in n for n in out) == 6 * len(ventanas_19_11.NUEVAS_2011), sorted(out)
    font = json.loads(z.read(FONT))
    propios = {c for p in vprov for row in p.get('chars', []) for c in row} | {c for p in vprov for c in p.get('advances', {})}
    font['providers'] = vprov + [p for p in font['providers']
                                 if not ({c for row in p.get('chars', []) for c in row} | set(p.get('advances', {}))) & propios]
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
