"""FINAL privado 25/11: ventanas del Bazar (ventanas_bazar.py, disenos Gemini del dueno)
encima de 6d57177d (Renacer de Minas + su ventana + insignias Dueno/Cazador).

Solo agrega: fondos font/bazar/*.png y sus providers en la fuente default (bitmaps + vueltas). No toca nada mas.
"""
import hashlib
import json

from deploy_guia_esc import rewrite
from terceros import privado

BASE = privado() / 'build/entregas/renacer-ventana-25-11/AstralRPG-Textures.zip'
OUT = privado() / 'build/entregas/bazar-ventanas-25-11'
FONT = 'assets/minecraft/font/default.json'


def change(names, z):
    import ventanas_19_11 as V
    from ventanas_bazar import assets
    out, prov = assets()
    assert not set(out) & set(names), 'el pack base ya tiene archivos del bazar'
    font = json.loads(z.read(FONT))
    usados = {c for p in font['providers'] for row in p.get('chars', []) for c in row} | \
             {c for p in font['providers'] for c in p.get('advances', {})}
    nuevos = {c for p in prov for row in p.get('chars', []) for c in row} | {c for p in prov for c in p.get('advances', {})}
    assert not usados & nuevos, 'caracteres ya usados en la fuente'
    assert V.ADELANTE_112 in usados and V.START in usados and V.END in usados
    font['providers'] = font['providers'] + prov
    out[FONT] = json.dumps(font, ensure_ascii=False).encode()
    return out


if __name__ == '__main__':
    sha = hashlib.sha1(BASE.read_bytes()).hexdigest()
    assert sha.startswith('6d57177d'), sha
    OUT.mkdir(parents=True, exist_ok=True)
    final = OUT / 'AstralRPG-Textures.zip'
    rewrite(BASE, final, change)
    sha = hashlib.sha1(final.read_bytes()).hexdigest()
    (OUT / 'pack.sha1').write_text(sha + '\n')
    print('FINAL', final, sha)
