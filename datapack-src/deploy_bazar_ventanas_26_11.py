"""FINAL privado 26/11: ventanas del Bazar 1.2.0 con el arte Gemini nuevo (ventanas_bazar26.py) encima de
0fc13619 (el pack en vivo: Renacer + ventanas del Bazar 1.1.0).

Saca los fondos font/bazar/* viejos y sus providers de la fuente default y pone los nuevos (12 ventanas,
0xF600..0xF6BF). No toca nada mas.
"""
import hashlib
import json

from deploy_guia_esc import rewrite
from terceros import privado

BASE = privado() / 'build/entregas/bazar-ventanas-25-11/AstralRPG-Textures.zip'
OUT = privado() / 'build/entregas/bazar-ventanas-26-11'
FONT = 'assets/minecraft/font/default.json'
TEX = 'assets/astral/textures/font/bazar/'
RANGO = range(0xF600, 0xF700)


def change(names, z):
    import ventanas_19_11 as V
    from ventanas_bazar import assets
    out, prov = assets()
    font = json.loads(z.read(FONT))

    def viejo(p):
        if p.get('file', '').startswith('astral:font/bazar/'):
            return True
        return p.get('type') == 'space' and p['advances'] and all(ord(c) in RANGO for c in p['advances'])
    quedan = [p for p in font['providers'] if not viejo(p)]
    usados = {c for p in quedan for row in p.get('chars', []) for c in row} | \
             {c for p in quedan for c in p.get('advances', {})}
    nuevos = {c for p in prov for row in p.get('chars', []) for c in row} | {c for p in prov for c in p.get('advances', {})}
    assert not usados & nuevos, 'caracteres ya usados en la fuente: %r' % sorted(usados & nuevos)
    assert V.ADELANTE_112 in usados and V.START in usados and V.END in usados
    print('providers viejos fuera:', len(font['providers']) - len(quedan), '| nuevos:', len(prov))
    font['providers'] = quedan + prov
    for n in names:
        if n.startswith(TEX) and n not in out:
            out[n] = None
    out[FONT] = json.dumps(font, ensure_ascii=False).encode()
    return out


if __name__ == '__main__':
    sha = hashlib.sha1(BASE.read_bytes()).hexdigest()
    assert sha.startswith('0fc13619'), sha
    OUT.mkdir(parents=True, exist_ok=True)
    final = OUT / 'AstralRPG-Textures.zip'
    rewrite(BASE, final, change)
    sha = hashlib.sha1(final.read_bytes()).hexdigest()
    (OUT / 'pack.sha1').write_text(sha + '\n')
    print('FINAL', final, sha)
