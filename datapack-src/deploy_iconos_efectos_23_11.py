"""23/11: FINAL nuevo = ultimo FINAL + iconos del Menu Astral a 72x72 (menu_ui.hd_icon) + interruptores de Efectos
con una pieza por fila (ventanas_20_11.E_PILL). La Guia usa modelos que ya estan en el pack (guadana_1, etc.).

Uso: python deploy_iconos_efectos_23_11.py [--base <FINAL.zip>]
"""
import argparse
import hashlib

from deploy_guia_esc import rewrite
from final_base import select_base
from terceros import privado

OUT = privado() / 'build/entregas/iconos-efectos-23-11'


def change(names, z):
    import ventanas_19_11
    import menu_ui
    vfiles, _ = ventanas_19_11.assets()
    out = {n: b for n, b in vfiles.items() if '/ventanas1911/interruptor_' in n}
    mfiles, _ = menu_ui.assets()
    claves = {f'/menu/icon_{k}.' for k in menu_ui.HD_KEYS}
    out.update({n: b for n, b in mfiles.items() if any(c in n for c in claves)})
    out = {n: b for n, b in out.items() if n not in names or z.read(n) != b}
    print(len(out), 'archivos cambiados')
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
