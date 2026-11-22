"""Pack FINAL privado de los modelos del 22/11 sobre el pack instalado (clases-22-11). No despliega.

- Taladros I-IX y motosierras 3D (herramientas3d.py), gomera 3D (gomera3d.py), libros del Invocador 3D (libros3d.py).
- BetterModel: Capitan del Vacio rehecho, Ojo Vigia y el modelo de jugador astral_poses (animaciones de guadana e
  invocacion). Los assets los genera BetterModel en el Paper local (tools/probar_modelos_22_11.py); antes se borran
  los del Capitan viejo (tenia huesos que ya no existen).

python datapack-src/deploy_modelos_22_11.py [--assets <Paper>/plugins/BetterModel/build]
-> ASTRAL_PRIVADO/build/entregas/modelos-22-11/AstralRPG-Textures.zip + pack.sha1 + procedencia.json
"""
import argparse
import hashlib
import io
import json
import zipfile
from pathlib import Path

from terceros import ROOT, privado

BASE = 'build/entregas/clases-22-11/AstralRPG-Textures.zip'
BASE_SHA = '76fc66d9c8d9ca2ead14e197cfbc7f6595ef73a1'
MODELOS_BM = ('astral_capitan_vacio', 'astral_ojo_vigia', 'astral_poses', 'astral_fx_clases')


def main(assets):
    base = privado() / BASE
    blob = base.read_bytes()
    if hashlib.sha1(blob).hexdigest() != BASE_SHA:
        raise ValueError('La base no coincide con el pack instalado (clases-22-11)')
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        files = {n: z.read(n) for n in z.namelist()}
    original = dict(files)
    import herramientas3d
    import gomera3d
    import libros3d
    for mod in (herramientas3d, gomera3d, libros3d):
        files.update(mod.assets())
    # BetterModel: fuera lo viejo de estos modelos, adentro lo que genero el Paper local
    viejos = [n for n in files if n.startswith('assets/bettermodel/') and any(f'/{m}_' in n or n.endswith(f'/{m}.json') for m in MODELOS_BM)]
    for n in viejos:
        del files[n]
    nuevos = []
    for p in sorted(assets.rglob('*')):
        if not p.is_file():
            continue
        rel = p.relative_to(assets).as_posix()
        if not rel.startswith('assets/'):
            continue
        # los modelos propios + las piezas del cuerpo del jugador que arma BetterModel (player_limb y mesh_triangle)
        if any(m in p.name for m in MODELOS_BM) or '/player_limb' in rel or '/mesh_triangle' in rel:
            files[rel] = p.read_bytes()
            nuevos.append(rel)
    for m in MODELOS_BM:
        if not any(m in n for n in nuevos):
            raise ValueError(f'BetterModel no exporto {m}: correr tools/probar_modelos_22_11.py')
    out = privado() / 'build/entregas/modelos-22-11'
    out.mkdir(parents=True, exist_ok=True)
    target = out / 'AstralRPG-Textures.zip'
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as z:
        for name, data in sorted(files.items()):
            z.writestr(zipfile.ZipInfo(name, (2026, 11, 22, 0, 0, 0)), data, compress_type=zipfile.ZIP_DEFLATED)
    sha = hashlib.sha1(target.read_bytes()).hexdigest()
    (out / 'pack.sha1').write_text(sha + '\n')
    changed = sorted(n for n, d in files.items() if original.get(n) != d)
    (out / 'procedencia.json').write_text(json.dumps({'base': BASE, 'base_sha1': BASE_SHA, 'final_sha1': sha,
                                                      'changed': changed, 'removed': sorted(set(original) - set(files)),
                                                      'bettermodel': nuevos}, indent=2), encoding='utf8')
    print('FINAL', target, sha, 'cambiados', len(changed), 'borrados', len(set(original) - set(files)), 'bettermodel', len(nuevos))
    return target, sha


if __name__ == '__main__':
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument('--assets', type=Path, default=ROOT / '.local/modelos-2211-probe/srv/plugins/BetterModel/build')
    main(a.parse_args().assets.resolve())
