"""Reforja de gemas (7d, 19/11/2026): entrega sobre lo que ya esta en el server.

- Datapack: el que esta en el server (.local/deploy-economia/AstralRPG-Items.zip = server + economia) MAS solo los
  archivos que cambian por las gemas (diferencia entre el build del ultimo commit y el build actual). Antes comprueba
  que los archivos que se pisan sean iguales en el server y en el commit (si no, frena).
- Pack FINAL: ultimo FINAL privado (economia-e1) + texturas de gemas + ventana Reforja + boton GEMAS del Herrero.
Uso: python deploy_gemas.py [--base-pack <FINAL.zip>] [--base-datapack <zip>] [--commit HEAD]
"""
import argparse
import hashlib
import io
import json
import subprocess
import zipfile
from pathlib import Path

from deploy_guia_esc import rewrite
from final_base import select_base
from terceros import privado

ROOT = Path(__file__).resolve().parents[1]
OUT = privado() / 'build/entregas/reforja-gemas'
LOCAL = ROOT / '.local/deploy-gemas'
DATAPACK_SERVER = ROOT / '.local/deploy-economia/AstralRPG-Items.zip'
REFORJA_CHARS = ('', '', '', '')


# ------------------------------------------------------------------ pack
def pack_files():
    """{ruta: bytes} que agrega o reemplaza la Reforja, y providers de fuente nuevos."""
    import services_ui as S
    from gemas import pack_assets, BOTONES, BARRAS
    files, providers = S.assets()
    nuevos = {n: b for n, b in files.items()
              if n.startswith('assets/astral/textures/font/servicios/reforja_')
              or n.startswith('assets/astral/textures/font/servicios/herrero_')
              or any(f'/servicios/{k}_' in n for k in BOTONES)
              or any(f'/servicios/bar_{k}_' in n for k in BARRAS)
              or '/servicios/gem_socket_' in n}
    nuevos.update(pack_assets())
    mios = [p for p in providers if p.get('type') == 'bitmap' and 'servicios/reforja_' in p['file']]
    adv = next(p for p in providers if p.get('type') == 'space')['advances']
    mios.append({'type': 'space', 'advances': {c: adv[c] for c in REFORJA_CHARS[2:]}})
    assert [c for p in mios[:2] for c in p['chars']] == list(REFORJA_CHARS[:2]), mios
    return nuevos, mios


def herrero_viejo():
    """Fondo del Herrero tal como se genera SIN el boton GEMAS (para comprobar la base antes de pisarlo)."""
    import services_ui as S
    image = S.panel('herrero', used=S.USED['herrero'] - {51, 52})
    return {f'assets/astral/textures/font/servicios/herrero_{n}.png': S.png(part) for n, part in
            enumerate([image.crop((0, 0, 224, S.SPLIT)), image.crop((0, S.SPLIT, 224, image.height))])}


def change(names, z):
    files, providers = pack_files()
    for n, b in herrero_viejo().items():
        assert n in names and z.read(n) == b, f'el Herrero del FINAL no es el esperado: {n} (no se pisa a ciegas)'
    for n in files:
        if n in names and not ('/font/servicios/herrero_' in n or n.startswith('assets/astral/textures/item/gemas/')
                               or n.startswith('assets/astral/models/item/gemas/') or n.startswith('assets/astral/items/gemas/')):
            assert z.read(n) == files[n], f'{n} ya existe distinto en la base'
    font = json.loads(z.read('assets/minecraft/font/default.json'))
    usados = {c for p in font['providers'] for row in p.get('chars', []) for c in row} | \
             {c for p in font['providers'] for c in p.get('advances', {})}
    ya = [c for c in REFORJA_CHARS if c in usados]
    if ya:   # rearmado sobre un FINAL que ya tiene la Reforja: sacar los providers viejos
        font['providers'] = [p for p in font['providers']
                             if not (p.get('type') == 'bitmap' and 'servicios/reforja_' in p.get('file', ''))
                             and not (p.get('type') == 'space' and set(p.get('advances', {})) <= set(REFORJA_CHARS))]
    font['providers'] = providers + font['providers']
    files = dict(files)
    files['assets/minecraft/font/default.json'] = json.dumps(font, ensure_ascii=False).encode()
    return {n: b for n, b in files.items() if n not in names or z.read(n) != b}


# ------------------------------------------------------------------ datapack
def datapack(base, commit):
    viejo = zipfile.ZipFile(io.BytesIO(subprocess.run(['git', 'show', f'{commit}:build/AstralRPG-Items.zip'], cwd=ROOT,
                                                      capture_output=True, check=True).stdout))
    nuevo = zipfile.ZipFile(ROOT / 'build/AstralRPG-Items.zip')
    server = zipfile.ZipFile(base)
    vn, nn, sn = set(viejo.namelist()), set(nuevo.namelist()), set(server.namelist())
    cambios = sorted(n for n in nn if n not in vn or viejo.read(n) != nuevo.read(n))
    borrados = sorted(vn - nn)
    assert not borrados, borrados
    for n in cambios:
        if n in vn:
            assert n in sn and server.read(n) == viejo.read(n), f'el server tiene otra version de {n}: no se pisa'
    LOCAL.mkdir(parents=True, exist_ok=True)
    dest = LOCAL / 'AstralRPG-Items.zip'
    with zipfile.ZipFile(dest, 'w', zipfile.ZIP_DEFLATED) as z:
        for n in server.namelist():
            if n not in cambios:
                z.writestr(server.getinfo(n), server.read(n))
        for n in cambios:
            z.writestr(n, nuevo.read(n))
    (LOCAL / 'datapack-cambios.txt').write_text('\n'.join(cambios) + '\n', encoding='utf-8')
    return dest, cambios


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--base-pack')
    ap.add_argument('--base-datapack', default=str(DATAPACK_SERVER))
    ap.add_argument('--commit', default='HEAD')
    a = ap.parse_args()
    dp, cambios = datapack(Path(a.base_datapack), a.commit)
    print('datapack', dp, len(cambios), 'archivos nuevos o cambiados', hashlib.sha1(dp.read_bytes()).hexdigest())
    base = select_base(output=OUT, explicit=a.base_pack)
    OUT.mkdir(parents=True, exist_ok=True)
    final = OUT / 'AstralRPG-Textures.zip'
    rewrite(base, final, change)
    sha = hashlib.sha1(final.read_bytes()).hexdigest()
    (OUT / 'pack.sha1').write_text(sha + '\n')
    print('base', base)
    print('FINAL', final, sha)
