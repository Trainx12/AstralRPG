"""Impide publicar arte privado, tambien dentro de ZIP, JSON y PNG reexportados."""
import base64
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'datapack-src'))
from terceros import privado


def sha(data):
    return hashlib.sha256(data).hexdigest()


def png_signature(data):
    from PIL import Image
    im = Image.open(io.BytesIO(data)).convert('RGBA')
    return sha(str(im.size).encode() + im.tobytes())


def fingerprints():
    base = privado() / 'x'
    if os.name == 'nt' and not str(base).startswith('\\\\?\\'):
        base = Path('\\\\?\\' + str(base))
    if not base.is_dir():
        raise FileNotFoundError('Se necesita ASTRAL_PRIVADO/x para auditar los assets privados.')
    hashes, pixels, names = set(), set(), set()
    for path in base.rglob('*'):
        if path.suffix.lower() not in ('.png', '.bbmodel'):
            continue
        data = path.read_bytes()
        hashes.add(sha(data))
        if path.suffix.lower() == '.bbmodel':
            names.add(path.name.casefold())
        if path.suffix.lower() == '.png':
            pixels.add(png_signature(data))
        else:
            for t in json.loads(data).get('textures', []):
                if t.get('source', '').startswith('data:image/png;base64,'):
                    raw = base64.b64decode(t['source'].split(',', 1)[1])
                    hashes.add(sha(raw)); pixels.add(png_signature(raw))
    # Originales nuevos conservados como ZIP; incluir tambien sus PNG en la auditoria.
    for archive in (privado()/'originales/cosmeticos').glob('*.zip'):
        hashes.add(sha(archive.read_bytes()))
        with zipfile.ZipFile(archive) as z:
            for name in z.namelist():
                if name.endswith(('.png','.json')):
                    blob=z.read(name);hashes.add(sha(blob))
                    if name.endswith('.png'):pixels.add(png_signature(blob))
    return hashes, pixels, names


def inspect(name, data, prints):
    hashes, pixels, names = prints
    suffix = Path(name).suffix.lower()
    if sha(data) in hashes:
        return [name + ': bytes privados']
    if suffix in ('.png', '.bbmodel') and Path(name).name.casefold() in names:
        return [name + ': nombre de asset privado']
    if suffix == '.png' and png_signature(data) in pixels:
        return [name + ': textura privada (pixeles)']
    if suffix == '.bbmodel':
        for t in json.loads(data).get('textures', []):
            if t.get('source', '').startswith('data:image/png;base64,'):
                if png_signature(base64.b64decode(t['source'].split(',', 1)[1])) in pixels:
                    return [name + ': textura privada embebida']
    if suffix == '.zip':
        found = []
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            for member in z.namelist():
                if not member.endswith('/'):
                    found.extend(inspect(name + '!/' + member, z.read(member), prints))
        return found
    return []


def audit():
    prints = fingerprints()
    paths = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
    found = []
    for name in filter(None, paths):
        path = ROOT / name
        if name.startswith(('.local/', 'logs/', 'output/')) or name.endswith('.local.md'):
            found.append(name + ': ruta privada versionada')
        if path.is_file():
            found.extend(inspect(name, path.read_bytes(), prints))
    return found


if __name__ == '__main__':
    errors = audit()
    if errors:
        print('\n'.join(errors)); sys.exit(1)
    print('Repo publico: sin arte privado en archivos versionados ni ZIP.')
