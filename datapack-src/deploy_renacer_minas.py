"""FINAL privado: Cazador de Bugs e765df5c + insignia Minero Renacido."""
import hashlib
from cosmeticos_ui import assets
from deploy_guia_esc import rewrite
from terceros import privado
BASE = privado() / 'build/entregas/cazador-bugs-24-11/AstralRPG-Textures.zip'
OUT = privado() / 'build/entregas/renacer-minas-25-11'

def change(names, z):
    files, _ = assets()
    out = {n:b for n,b in files.items() if 'cosmeticos/minero_renacido.' in n}
    assert len(out) == 3
    assert not set(out).intersection(names)
    return out

if __name__ == '__main__':
    sha = hashlib.sha1(BASE.read_bytes()).hexdigest()
    assert sha.startswith('e765df5c'), sha
    OUT.mkdir(parents=True, exist_ok=True)
    final = OUT / 'AstralRPG-Textures.zip'
    rewrite(BASE, final, change)
    sha = hashlib.sha1(final.read_bytes()).hexdigest()
    (OUT / 'pack.sha1').write_text(sha+'\n')
    print('FINAL', final, sha)
