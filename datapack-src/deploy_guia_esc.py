"""Guia Astral en ESC (18/11): FINAL nuevo encima del ultimo FINAL desplegado.

Solo cambia la fuente del Atlas (tiras <=240 px, ascent normal) y las etiquetas
de ESC/acciones rapidas del datapack de Crop & Kettle. Todo lo demas se copia tal cual.
Uso: python deploy_guia_esc.py [--base <FINAL.zip>]
"""
import argparse
import hashlib
import json
import zipfile
from final_base import select_base
from guia_atlas import ENTRADA, assets
from terceros import privado

OUT = privado() / 'build/entregas/guia-esc-18-11'


def rewrite(src, dst, change):
    with zipfile.ZipFile(src) as zin, zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as zout:
        names = zin.namelist()
        extra = change(names, zin)
        for n in names:
            if n not in extra:
                zout.writestr(zin.getinfo(n), zin.read(n))
        for n, data in extra.items():
            if data is not None:
                zout.writestr(n, data)


def pack_change(names, z):
    font = json.loads(z.read('assets/astral/font/guia_atlas.json'))
    mine = assets()
    deco = json.loads(mine['assets/astral/font/guia_atlas.json'])['providers']
    keep = [p for p in font['providers'] if not p.get('file', '').startswith('astral:gui/atlas/')
            or '/iconos/' in p['file'] or '/mobs/' in p['file']]
    for p in keep:
        if '/mobs/' in p.get('file', ''):
            p['ascent'] = 7
    keep = [p for p in keep if p.get('type') != 'space']
    out = {n: b for n, b in mine.items() if n.endswith('.png')}
    # Texturas viejas anchas (indice/receta) ya no se usan: se reemplazan por tiras.
    for n in names:
        if n.startswith('assets/astral/textures/gui/atlas/') and n.count('/') == 5 and n not in out:
            out[n] = None
    out['assets/astral/font/guia_atlas.json'] = json.dumps(dict(providers=deco + keep)).encode()
    return out


def cnk_change(names, z):
    out = {}
    for n in names:
        if n.endswith(('tags/dialog/pause_screen_additions.json', 'tags/dialog/quick_actions.json')):
            obj = json.loads(z.read(n))
            obj['values'] = [ENTRADA]  # misma entrada que Astral: el tag la junta en un solo boton
            out[n] = json.dumps(obj).encode()
    return out


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--base')
    args = ap.parse_args()
    base = select_base(output=OUT, explicit=args.base)
    OUT.mkdir(parents=True, exist_ok=True)
    final = OUT / 'AstralRPG-Textures.zip'
    rewrite(base, final, pack_change)
    sha = hashlib.sha1(final.read_bytes()).hexdigest()
    (OUT / 'pack.sha1').write_text(sha + '\n')
    cnk = privado() / 'build/entregas/crop-kettle/CropAndKettle-Astral.zip'
    rewrite(cnk, OUT / 'CropAndKettle-Astral.zip', cnk_change)
    print('base', base)
    print('FINAL', final, sha)
