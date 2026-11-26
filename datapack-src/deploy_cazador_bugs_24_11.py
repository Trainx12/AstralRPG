"""24/11: titulo especial Cazador de Bugs (premio a Nicxo28) en la coleccion de /titulos.
FINAL = reinicio-24-11 (f547e206, el pack cargado en el server) + la insignia cazador_de_bugs.
Menu (cosmeticos_titulos.yml) y astral_cosmeticos.sk salen de cosmeticos.py.

Uso: python deploy_cazador_bugs_24_11.py
"""
import hashlib

from cosmeticos_ui import assets, key_for, SPECIAL_TITLES
from deploy_guia_esc import rewrite
from terceros import privado

OUT = privado() / 'build/entregas/cazador-bugs-24-11'
BASE = privado() / 'build/entregas/reinicio-24-11/AstralRPG-Textures.zip'


def change(names, z):
    files, _ = assets()
    keys = [key_for(n) for n, _, _ in SPECIAL_TITLES]
    out = {n: b for n, b in files.items() if any(f'cosmeticos/{k}.' in n for k in keys)}
    assert len(out) == 3 * len(keys), sorted(out)  # Cazador de Bugs + Dueño
    for n in out:
        assert n not in names, f'ya estaba en el pack: {n}'
        print('  +', n)
    return out


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    base_sha = hashlib.sha1(BASE.read_bytes()).hexdigest()
    assert base_sha.startswith('f547e206'), base_sha
    final = OUT / 'AstralRPG-Textures.zip'
    rewrite(BASE, final, change)
    sha = hashlib.sha1(final.read_bytes()).hexdigest()
    (OUT / 'pack.sha1').write_text(sha + '\n')
    print('base', base_sha)
    print('FINAL', final, sha)
