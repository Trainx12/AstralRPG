"""Audita copias de datapacks habilitados para 26.1.2, sin extraer ni modificar ZIP.

Pasar cada ZIP/carpeta habilitada, incluida Astral y CNK. No inferir el estado remoto.
"""
import argparse
import json
from pathlib import Path
import zipfile

TAGS = ('pause_screen_additions', 'quick_actions')


def read_pack(path):
    if path.is_dir():
        files = {p.relative_to(path).as_posix(): p.read_bytes() for p in path.rglob('*.json')}
        files['pack.mcmeta'] = (path / 'pack.mcmeta').read_bytes()
    else:
        with zipfile.ZipFile(path) as z:
            if len(z.namelist()) != len(set(z.namelist())): raise ValueError('ZIP duplicado: '+str(path))
            files = {n: z.read(n) for n in z.namelist() if n.endswith(('.json', 'pack.mcmeta'))}
    data = {n: b for n, b in files.items() if n.startswith('data/')}
    for entry in json.loads(files['pack.mcmeta']).get('overlays', {}).get('entries', []):
        if 'min_format' in entry:
            lo, hi = entry['min_format'], entry['max_format']
            lo = (lo, 0) if isinstance(lo, int) else tuple(lo)
            hi = (hi, 999) if isinstance(hi, int) else tuple(hi)
            enabled = lo <= (101, 1) <= hi
        else:
            fmt = entry['formats']
            enabled = fmt == 101 if isinstance(fmt, int) else fmt['min_inclusive'] <= 101 <= fmt['max_inclusive']
        if enabled:
            prefix = entry['directory'] + '/'
            data.update({n[len(prefix):]: b for n, b in files.items() if n.startswith(prefix+'data/')})
    return data


def audit(paths):
    union = {tag: set() for tag in TAGS}
    for path in paths:
        data = read_pack(path)
        for tag in TAGS:
            obj = json.loads(data.get(f'data/minecraft/tags/dialog/{tag}.json', b'{}'))
            if obj.get('replace', False): raise ValueError(f'{path}: {tag} usa replace; revisar orden de carga')
            values = [v['id'] if isinstance(v, dict) else v for v in obj.get('values', [])]
            union[tag].update(values)
            print(f'{path.name}: {tag} = {values}')
    for tag, values in union.items():
        if values != {'astral:guia'}: raise ValueError(f'Union {tag}: {sorted(values)}; se esperaba solo astral:guia')
    print('OK: pausa y acciones rapidas contienen solo astral:guia en las copias auditadas')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('packs', nargs='+', type=Path)
    args = parser.parse_args()
    audit(args.packs)
