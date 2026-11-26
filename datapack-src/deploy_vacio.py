"""Pack FINAL privado del Vacio Estelar (23/11/2026) sobre el pack instalado (armaduras-t5t6-23-11, 16f0f125).

Suma las texturas/modelos de las vetas y de los items del Vacio (vacio.pack_assets) y parcha el bloque de nota
(la campanilla 0-15 pasa a ser veta). No despliega.

python datapack-src/deploy_vacio.py -> ASTRAL_PRIVADO/build/entregas/vacio-23-11/AstralRPG-Textures.zip
"""
import hashlib
import io
import json
import zipfile

from terceros import privado
import vacio

BASE = 'build/entregas/armaduras-t5t6-23-11/AstralRPG-Textures.zip'
BASE_SHA = '16f0f125c26ff000baa27f3cb7bcefb8357bfddc'
OUT = 'build/entregas/vacio-23-11'
BS = 'assets/minecraft/blockstates/note_block.json'


def main():
    blob = (privado() / BASE).read_bytes()
    if hashlib.sha1(blob).hexdigest() != BASE_SHA:
        raise ValueError('La base no coincide con el pack instalado (armaduras-t5t6-23-11)')
    z = zipfile.ZipFile(io.BytesIO(blob))
    files = {n: z.read(n) for n in z.namelist()}
    files.update(vacio.pack_assets())
    files[BS] = json.dumps(vacio.parchar_note_block(json.loads(files[BS])), ensure_ascii=False, indent=1).encode()
    dest = privado() / OUT / 'AstralRPG-Textures.zip'
    dest.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(dest, 'w', zipfile.ZIP_DEFLATED) as out:
        for n in sorted(files):
            out.writestr(zipfile.ZipInfo(n, (2026, 11, 23, 0, 0, 0)), files[n])
    print(dest, hashlib.sha1(dest.read_bytes()).hexdigest())


if __name__ == '__main__':
    main()
