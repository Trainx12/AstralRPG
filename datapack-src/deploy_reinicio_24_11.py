"""24/11 (dueno: "reinicia y aplica todo"): un solo FINAL para el reinicio.
FINAL = taladro-giro-24-11 (7b60bacc, sobre f6af9faa del server)
      + boton invisible de la tienda (lo mismo que deploy_tienda_botones_24_11, que se armo sobre f6af9faa)
      + tarjetas del Cronista con la plata nueva (economia.py HISTORIA_PLATA / DIARIA_PLATA).

Uso: python deploy_reinicio_24_11.py
"""
import hashlib
import json

from cronista_ui import assets as cronista_assets
from deploy_guia_esc import rewrite
from shop_ui import BOTON_INVISIBLE
from terceros import privado

OUT = privado() / 'build/entregas/reinicio-24-11'
BASE = privado() / 'build/entregas/taladro-giro-24-11/AstralRPG-Textures.zip'
ITEM = f'assets/minecraft/items/{BOTON_INVISIBLE.lower()}.json'


def change(names, z):
    out = {}
    assert ITEM not in names, ITEM
    out[ITEM] = json.dumps({"model": {"type": "minecraft:empty"}}, indent=1).encode()
    files, _providers = cronista_assets()
    nuevos = [n for n in files if n not in names]
    assert not nuevos, f'el Cronista trae archivos que el FINAL no tiene: {nuevos[:5]}'
    cambiados = [n for n, b in files.items() if z.read(n) != b]
    for n in cambiados:
        out[n] = files[n]
    print('Cronista: archivos cambiados', len(cambiados))
    for n in cambiados[:40]:
        print('  ', n)
    return out


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    final = OUT / 'AstralRPG-Textures.zip'
    rewrite(BASE, final, change)
    sha = hashlib.sha1(final.read_bytes()).hexdigest()
    (OUT / 'pack.sha1').write_text(sha + '\n')
    print('base', BASE, hashlib.sha1(BASE.read_bytes()).hexdigest())
    print('FINAL', final, sha)
