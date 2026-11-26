"""FINAL privado 25/11: Renacer de Minas (30e8b93f = Cazador de Bugs/Dueno e765df5c + insignia Minero Renacido)
+ ventana "Renacer en las Minas" (ventana_renacer.py, diseno Gemini del dueno).

Solo agrega: fondos font/ventanas2011/renacer_*.png, los 10 numeros del bonus y sus providers en la fuente
default (bitmaps + un space con las vueltas de la ventana). No toca nada mas del pack.
"""
import hashlib
import json

from deploy_guia_esc import rewrite
from terceros import privado

BASE = privado() / 'build/entregas/renacer-minas-25-11/AstralRPG-Textures.zip'
OUT = privado() / 'build/entregas/renacer-ventana-25-11'
FONT = 'assets/minecraft/font/default.json'


def change(names, z):
    import ventanas_19_11 as V
    from ventana_renacer import bonus_providers
    out, prov = {}, []
    for i, (g, v, pieza, alto, ascent, x0, avance) in enumerate(V._tiles_hd('renacer')):
        path = f'font/ventanas2011/renacer_{i}.png'
        out['assets/astral/textures/' + path] = V.png(pieza)
        prov.append(dict(type='bitmap', file='astral:' + path, height=alto, ascent=ascent, chars=[g]))
        prov.append(dict(type='space', advances={v: -(avance + x0)}))
    bf, bp = bonus_providers()
    out.update(bf)
    prov += bp
    assert not set(out) & set(names), 'el pack base ya tiene archivos de la ventana'
    font = json.loads(z.read(FONT))
    usados = {c for p in font['providers'] for row in p.get('chars', []) for c in row} | \
             {c for p in font['providers'] for c in p.get('advances', {})}
    nuevos = {c for p in prov for row in p.get('chars', []) for c in row} | {c for p in prov for c in p.get('advances', {})}
    assert not usados & nuevos, 'caracteres ya usados en la fuente'
    assert V.ADELANTE_112 in usados and V.START in usados
    font['providers'] = font['providers'] + prov
    out[FONT] = json.dumps(font, ensure_ascii=False).encode()
    return out


if __name__ == '__main__':
    sha = hashlib.sha1(BASE.read_bytes()).hexdigest()
    assert sha.startswith('30e8b93f'), sha
    OUT.mkdir(parents=True, exist_ok=True)
    final = OUT / 'AstralRPG-Textures.zip'
    rewrite(BASE, final, change)
    sha = hashlib.sha1(final.read_bytes()).hexdigest()
    (OUT / 'pack.sha1').write_text(sha + '\n')
    print('FINAL', final, sha)
