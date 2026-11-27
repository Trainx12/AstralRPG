"""Icono Gemini del Nucleo de Venta (Corazon del Astral) sobre el ultimo FINAL privado.

Solo agrega textura, modelo y definicion de item `astral:autoventa`; el resto del FINAL queda igual.
"""
import argparse
import hashlib
from pathlib import Path

from deploy_guia_esc import rewrite
from final_base import select_base
from terceros import privado

HERE = Path(__file__).resolve().parent
OUT = privado() / 'build/entregas/corazon-astral-27-11'
SRC = HERE / 'pack-source/assets/astral'
DELTA = {
    'assets/astral/textures/item/autoventa.png': SRC / 'textures/item/autoventa.png',
    'assets/astral/models/item/autoventa.json': SRC / 'models/item/autoventa.json',
    'assets/astral/items/autoventa.json': SRC / 'items/autoventa.json',
}


def generate(base=None):
    source = select_base(output=OUT, explicit=base)
    OUT.mkdir(parents=True, exist_ok=True)
    final = OUT / 'AstralRPG-Textures.zip'
    rewrite(source, final, lambda names, z: {n: p.read_bytes() for n, p in DELTA.items()})
    sha = hashlib.sha1(final.read_bytes()).hexdigest()
    (OUT / 'pack.sha1').write_text(sha + '\n', encoding='utf8')
    print('base', source, hashlib.sha1(source.read_bytes()).hexdigest())
    print('FINAL', final, sha)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--base')
    generate(p.parse_args().base)
