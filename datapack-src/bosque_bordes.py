"""Parche minimo del radio de Bosque; no reescribe el datapack principal pendiente.

Al regenerar el principal con build.py, estas mismas funciones ya salen con r=108.
El complemento debe habilitarse DESPUES del principal (datapack enable ... last).
"""
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/AstralRPG-Bosque-Bordes.zip'


def contents():
    from mobs.tanda2 import generate
    # build.py ejecuta la generacion al importarse; leer el formato del ZIP existente.
    with zipfile.ZipFile(ROOT / 'build/AstralRPG-Items.zip') as base:
        pack = json.loads(base.read('pack.mcmeta'))['pack']
    files = {'data/astral/function/load.mcfunction': ''}
    generate(files)
    prefix = 'data/astral/function/tanda2/bosque/sala1/wave'
    selected = {name: value for name, value in files.items()
                if name.startswith(prefix) and name.removeprefix(prefix) in
                ('1.mcfunction', '2.mcfunction', '3.mcfunction')}
    if len(selected) != 3:
        raise ValueError('Cambio la estructura del Bosque: revisar el parche')
    selected['pack.mcmeta'] = json.dumps({'pack': {
        'description': 'AstralRPG - Bosque conteo rectangular (18/11/2026)',
        **{key: pack[key] for key in ('min_format', 'max_format') if key in pack}}}, ensure_ascii=False)+'\n'
    return selected


def generate():
    with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as z:
        for name, value in sorted(contents().items()):
            info = zipfile.ZipInfo(name, (2026, 11, 18, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, value)
    return OUT


if __name__ == '__main__':
    print(generate())
