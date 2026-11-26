"""24/11: botones de la tienda (EconomyShopGUI) invisibles. FINAL nuevo = ultimo FINAL + STRUCTURE_VOID sin dibujo
(shop_ui.BOTON_INVISIBLE). En el server, config.yml de EconomyShopGUI pasa los botones de PAPER a STRUCTURE_VOID.

Uso: python deploy_tienda_botones_24_11.py [--base <FINAL.zip>]
"""
import argparse
import hashlib
import json

from deploy_guia_esc import rewrite
from final_base import select_base
from shop_ui import BOTON_INVISIBLE
from terceros import privado

OUT = privado() / 'build/entregas/tienda-botones-24-11'
ITEM = f'assets/minecraft/items/{BOTON_INVISIBLE.lower()}.json'


def change(names, z):
    assert ITEM not in names, ITEM
    return {ITEM: json.dumps({"model": {"type": "minecraft:empty"}}, indent=1).encode()}


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
    print('base', base, hashlib.sha1(base.read_bytes()).hexdigest())
    print('FINAL', final, sha)
