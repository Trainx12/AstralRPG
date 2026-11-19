"""Cavernas de Cristal (7e, 19/11/2026): entrega sobre lo que ya esta en el server.

- Datapack: el del server (.local/deploy-gemas/AstralRPG-Items.zip = desplegado con la Reforja) MAS solo los archivos
  que cambian respecto del build del ultimo commit (comprueba que los que pisa sean iguales en el server y el commit).
- Pack FINAL: ultimo FINAL privado del server (guia-cofre-hd, 93230c21) + vetas e items de las Cavernas + bloque de nota
  parchado + ventanas del 19/11 (Cavernas) + tarjetas de Portales + texturas propias de perla y coral.
Uso: python deploy_cavernas.py [--base-pack <FINAL.zip>] [--base-datapack <zip>] [--commit HEAD]
"""
import argparse
import hashlib
import json
from pathlib import Path

import deploy_gemas as D
from deploy_guia_esc import rewrite
from final_base import select_base
from terceros import privado

ROOT = Path(__file__).resolve().parents[1]
OUT = privado() / 'build/entregas/cavernas-cristal'
LOCAL = ROOT / '.local/deploy-cavernas'
DATAPACK_SERVER = ROOT / '.local/deploy-cavernas/server/AstralRPG-Items.zip'   # bajado del server el 19/11
BS = 'assets/minecraft/blockstates/note_block.json'
FONT = 'assets/minecraft/font/default.json'


REEMPLAZA = ('assets/astral/textures/font/viajes/portales_',                      # Portales con tarjetas nuevas
             'assets/astral/textures/block/coral_astral_ore.png', 'assets/astral/textures/block/perla_abisal_ore.png',
             'assets/astral/textures/item/coral_astral.png', 'assets/astral/textures/item/perla_abisal.png')


def change(names, z):
    import cavernas
    import oceano_items
    import travel_ui
    import ventanas_19_11
    files = cavernas.pack_assets()
    vfiles, vprov = ventanas_19_11.assets()
    files.update(vfiles)
    for n in files:
        assert n not in names or '/cavernas/' in n or '/ventanas1911/' in n, f'{n} ya existe en la base'
    # Reemplazos: tarjetas de Portales (fuente) y texturas propias de las Mareas.
    tfiles, _ = travel_ui.assets()
    files.update({n: b for n, b in tfiles.items() if n.startswith(REEMPLAZA[0])})
    files.update({n: b for n, b in oceano_items.own_textures().items() if n in REEMPLAZA[1:]})
    for n in REEMPLAZA[1:]:
        assert n in names and n in files, n
    # Forja nueva (19/11): fondos de Herrero y Reforja y sus botones (reemplazan a los de la base).
    import services_ui
    sfiles, _ = services_ui.assets()
    forja = ('font/servicios/herrero_', 'font/servicios/reforja_', '/servicios/improve_', '/servicios/blocked_', '/servicios/repair_',
             '/servicios/forja_', '/servicios/gems_', '/servicios/forge_back_', '/servicios/gem_set_', '/servicios/gem_out_')
    files.update({n: b for n, b in sfiles.items() if any(k in n for k in forja)})
    bs = cavernas.parchar_note_block(json.loads(z.read(BS)))
    files[BS] = json.dumps(bs).encode()
    font = json.loads(z.read(FONT))
    propios = {c for p in vprov for c in (p.get('chars', [''])[0] if p.get('chars') else '')} |               {c for p in vprov for c in p.get('advances', {})}
    font['providers'] = vprov + [p for p in font['providers']
                                 if not ({c for row in p.get('chars', []) for c in row} | set(p.get('advances', {}))) & propios]
    files[FONT] = json.dumps(font, ensure_ascii=False).encode()
    return {n: b for n, b in files.items() if n not in names or z.read(n) != b}


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--base-pack')
    ap.add_argument('--base-datapack', default=str(DATAPACK_SERVER))
    ap.add_argument('--commit', default='HEAD')
    a = ap.parse_args()
    D.LOCAL = LOCAL
    dp, cambios = D.datapack(Path(a.base_datapack), a.commit)
    print('datapack', dp, len(cambios), 'archivos nuevos o cambiados', hashlib.sha1(dp.read_bytes()).hexdigest())
    base = select_base(output=OUT, explicit=a.base_pack)
    OUT.mkdir(parents=True, exist_ok=True)
    final = OUT / 'AstralRPG-Textures.zip'
    rewrite(base, final, change)
    sha = hashlib.sha1(final.read_bytes()).hexdigest()
    (OUT / 'pack.sha1').write_text(sha + '\n')
    print('base', base)
    print('FINAL', final, sha)
