"""Pack FINAL privado de las clases nuevas (Segador, Invocador y Asesino, 22/11/2026).

Base: el ultimo FINAL en vivo (entrega `nave-22-11`, sha1 0a1a1ce6). Encima:
1. Armaduras elegidas por el dueno (arte de terceros ya horneado por `armaduras_t6_10.py`): texturas puestas,
   casco 3D (cabeza e inventario) e iconos de pechera/grebas/botas.
2. Libros del Invocador: por ahora el libro vanilla (los libros 3D los hace el dueno; mismo id de modelo
   `astral:libro_invocador_<tier>`, solo hay que reemplazar `assets/astral/items/libro_invocador_<tier>.json`).

Todo queda en ASTRAL_PRIVADO/build/entregas/clases-22-11/. Nunca en el repo publico.
Uso (desde la raiz): python datapack-src/deploy_clases.py   (antes: armaduras_t6_10.py con los sets de clases)
"""
import hashlib
import os
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import deploy_tiers6_10 as D  # noqa: E402
from clases import SETS, LIBRO_TIERS, SIN_CASCO  # noqa: E402
D.SIN_CASCO.update(SIN_CASCO)
_icono_original = D.icono_sin_casco


def _icono_sin_casco(name, main):
    """Las clases nuevas no tienen casco de reserva en el pack publico: se tine el del Mago III."""
    if not name.startswith(tuple(SETS)):
        return _icono_original(name, main)
    files = _icono_original('mago_3', main)
    return {k.replace('mago_3_helmet', f'{name}_helmet'): (v.replace(b'mago_3_helmet', f'{name}_helmet'.encode())
                                                           if k.endswith('.json') else v) for k, v in files.items()}


D.icono_sin_casco = _icono_sin_casco

ROOT = Path(__file__).resolve().parent.parent
PRIV = D.PRIV
BASE = PRIV / 'build/entregas/nave-22-11/AstralRPG-Textures.zip'
OUT = PRIV / 'build/entregas/clases-22-11'
STAMP = (2026, 11, 22, 0, 0, 0)
BASE_SHA1 = '0a1a1ce639a810f04075d9d168deb6c6194922ca'


def visual():
    return {sid: {t: vid for t, (vid, _) in s['tiers'].items()} for sid, s in SETS.items()}


def libros():
    out = {}
    for t in LIBRO_TIERS:
        out[f'assets/astral/items/libro_invocador_{t}.json'] = D.js(
            {'model': {'type': 'minecraft:model', 'model': 'minecraft:item/book'}})
    return out


def main():
    if not BASE.exists() or not D.ARTE.exists():
        print('Falta el pack base o el arte privado: no se genera nada.')
        return 1
    if hashlib.sha1(BASE.read_bytes()).hexdigest() != BASE_SHA1:
        print('OJO: el pack base no es el 0a1a1ce6 esperado.')
    with zipfile.ZipFile(BASE) as z:
        files = {n: z.read(n) for n in z.namelist()}
    nuevos = D.armaduras(visual())
    nuevos.update(libros())
    # Modelo de la invocacion (BetterModel, propio): assets generados por BetterModel en pack-source/bettermodel.
    bm = ROOT / 'datapack-src/pack-source/bettermodel'
    for f in bm.rglob('astral_invocacion*'):
        nuevos[f.relative_to(bm).as_posix()] = f.read_bytes()
    files.update(nuevos)
    OUT.mkdir(parents=True, exist_ok=True)
    target = OUT / 'AstralRPG-Textures.zip'
    tmp = target.with_suffix('.zip.tmp')
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as out:
        for name, data in sorted(files.items()):
            out.writestr(zipfile.ZipInfo(name, date_time=STAMP), data, compress_type=zipfile.ZIP_DEFLATED)
    tmp.replace(target)
    sha = hashlib.sha1(target.read_bytes()).hexdigest()
    (OUT / 'pack.sha1').write_text(sha + '\n')
    print(len(nuevos), 'archivos nuevos;', target, sha)
    return 0


if __name__ == '__main__':
    sys.exit(main())
