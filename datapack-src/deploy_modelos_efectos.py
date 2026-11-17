"""Entrega "modelos 3D y efectos" (16/11/2026): pack FINAL privado por delta y lista de instalacion.

FINAL = ultimo FINAL entregado (cargar-arte-16-11) + lo que cambio en el pack publico respecto de HEAD (dibujos de
efectos y Fenix) + los modelos privados de esta tarea (mochilas, cuchillos y armas de las Mareas en 3D).
No sube nada: ni servidor, ni R2, ni push.

  python datapack-src/deploy_modelos_efectos.py [--base <FINAL.zip>]
Antes: efectos.py, mobs/build_models.py, build_pack.py pack-source (con los assets de BetterModel del Fenix).
"""
import hashlib
import io
import json
import subprocess
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import armas_planas3d  # noqa: E402
import mochilas3d  # noqa: E402
from terceros import privado  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = privado() / 'build/entregas/modelos-3d-efectos'
BASE = armas_planas3d.BASE_FINAL
STAMP = (2026, 11, 16, 0, 0, 0)
PROPIOS = ('assets/astral/textures/item/fx/', 'assets/astral/models/item/fx/', 'assets/astral/items/fx/',
           'assets/bettermodel/items/model/astral_pet_fenix', 'assets/bettermodel/models/model/astral_pet_fenix',
           'assets/bettermodel/textures/item/astral_pet_fenix')


def cambios_publicos():
    """Entradas del pack publico nuevo que no estan o son distintas en el de HEAD."""
    new = zipfile.ZipFile(ROOT / 'build/AstralRPG-Textures.zip')
    old = zipfile.ZipFile(io.BytesIO(subprocess.check_output(
        ['git', 'show', 'HEAD:build/AstralRPG-Textures.zip'], cwd=ROOT)))
    viejos = set(old.namelist())
    cambia = {n: new.read(n) for n in new.namelist() if n not in viejos or new.read(n) != old.read(n)}
    sobran = sorted(n for n in viejos - set(new.namelist()))
    return cambia, sobran


def final(base=None):
    base = Path(base or BASE)
    if not base.exists():
        raise FileNotFoundError(f'Falta el FINAL base: {base}')
    with zipfile.ZipFile(base) as z:
        files = {n: z.read(n) for n in z.namelist()}
    pub, sobran = cambios_publicos()
    # Solo lo de esta tarea (dibujos de efectos y Fenix). El resto del pack publico puede diferir de HEAD por
    # otras tandas (ventanas, iconos de reserva) y pisaria arte privado del FINAL: no se toca.
    pub = {n: d for n, d in pub.items() if n.startswith(PROPIOS)}
    S = armas_planas3d.generar(base)
    moch, vista, ps, pos = mochilas3d.archivos()
    priv = dict(S.files)
    priv.update(moch)
    files.update(pub)
    files.update(priv)
    for n in sobran:                                  # piezas viejas de efectos o del Fenix que ya no existen
        if n.startswith(PROPIOS):
            files.pop(n, None)
    for n in [n for n in files if n.startswith(PROPIOS[3:]) and n not in pub]:
        files.pop(n, None)                            # huesos viejos del Fenix (head_2, etc.)
    OUT.mkdir(parents=True, exist_ok=True)
    target = OUT / 'AstralRPG-Textures.zip'
    tmp = target.with_suffix('.zip.tmp')
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as z:
        for name, data in sorted(files.items()):
            z.writestr(zipfile.ZipInfo(name, STAMP), data, compress_type=zipfile.ZIP_DEFLATED)
    from pack_audit import audit
    audit(tmp)
    tmp.replace(target)
    digest = hashlib.sha1(target.read_bytes()).hexdigest()
    (OUT / 'pack.sha1').write_text(digest + '\n')
    base_sha = hashlib.sha1(base.read_bytes()).hexdigest()
    (OUT / 'delta.json').write_text(json.dumps({'base': base.parent.name, 'base_sha1': base_sha,
                                                'publicos': sorted(pub), 'privados': sorted(priv)}, indent=1))
    mochilas3d.vistas(vista, ps, pos)
    armas_planas3d.vista_previa(S, OUT / 'previews/armas-3d.png')
    return target, digest, base_sha, len(pub), len(priv)


def configs_privadas():
    """Skills de MythicMobs en su version privada (el server usa estas): misma receta que build_privado,
    sin tocar medidas.json. Copia a la entrega astral.yml (jefes) y trainx.yml."""
    import shutil
    import build_privado as B
    # private_configs escribe en el build privado compartido (otras tandas lo usan): se guarda y se restaura.
    comunes = [privado() / 'build/mythicmobs' / r for r in ('skills/astral.yml', 'skills/mascotas.yml', 'mobs/astral.yml')]
    antes = {p: p.read_bytes() for p in comunes if p.exists()}
    guardar = B.write_json
    B.write_json = lambda *a, **k: None
    dest = OUT / 'mythicmobs/skills'
    dest.mkdir(parents=True, exist_ok=True)
    try:
        B.private_configs({})
        shutil.copy2(comunes[0], dest / 'astral.yml')
    finally:
        B.write_json = guardar
        for p in comunes:
            if p in antes:
                p.write_bytes(antes[p])
    shutil.copy2(ROOT / 'build/mythicmobs/skills/trainx.yml', dest / 'trainx.yml')
    return dest


if __name__ == '__main__':
    explicit = sys.argv[sys.argv.index('--base') + 1] if '--base' in sys.argv else None
    target, digest, base_sha, n_pub, n_priv = final(explicit)
    print(f'{n_pub} cambios publicos + {n_priv} privados sobre {base_sha}')
    print(target, digest)
    print(configs_privadas())
