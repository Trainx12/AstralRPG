"""Pack FINAL privado de los tiers 6-10 (14/11/2026).

Base: el ultimo pack en vivo (entrega `oficios`, sha1 bfb2b1e3). Encima:
1. Lo que cambio en el pack PUBLICO respecto de HEAD (equipment/items de T6-T10 de reserva y tarjeta VI-X de la Infinita).
2. Las armaduras elegidas por el dueno (arte de terceros, `armaduras_t6_10.py`): texturas puestas, casco 3D en la
   cabeza, casco 3D tambien como icono del inventario y los iconos de pechera/grebas/botas sacados de la textura.

Todo lo que sale de aca queda en ASTRAL_PRIVADO/build/entregas/tiers6-10/. Nunca en el repo publico.

Uso (desde la raiz):  python datapack-src/deploy_tiers6_10.py
Requiere antes: python build_pack.py pack-source y python armaduras_t6_10.py.
"""
import hashlib
import io
import json
import os
import subprocess
import sys
import zipfile
from pathlib import Path

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from items_t6_10 import VISUAL  # noqa: E402
from armor_icons import icons, outline  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
PRIV = Path(os.environ.get('ASTRAL_PRIVADO', ROOT / '.local/terceros/AstralRPG-privado'))
BASE = PRIV / 'build/entregas/oficios/AstralRPG-Textures.zip'
ARTE = PRIV / 'build/entregas/armaduras-t6-10/pack'
OUT = PRIV / 'build/entregas/tiers6-10'
PIECES = ('helmet', 'chestplate', 'leggings', 'boots')
STAMP = (2026, 11, 14, 0, 0, 0)


def cambios_publicos():
    """Archivos del pack publico nuevo que no estan (o son distintos) en el de HEAD."""
    new = zipfile.ZipFile(ROOT / 'build/AstralRPG-Textures.zip')
    old = zipfile.ZipFile(io.BytesIO(subprocess.check_output(
        ['git', 'show', 'HEAD:build/AstralRPG-Textures.zip'], cwd=ROOT)))
    old_names = set(old.namelist())
    return {n: new.read(n) for n in new.namelist()
            if n not in old_names or new.read(n) != old.read(n)}


def js(data):
    return (json.dumps(data, ensure_ascii=False, indent=1) + '\n').encode('utf-8')


def png(img):
    buf = io.BytesIO()
    img.save(buf, 'PNG')
    return buf.getvalue()


def icono_gui(model):
    """El casco 3D tambien se ve en el inventario: vista 3/4 escalada para entrar en la casilla."""
    pts = [p for e in model['elements'] for p in (e['from'], e['to'])]
    lo = [min(p[i] for p in pts) for i in range(3)]
    hi = [max(p[i] for p in pts) for i in range(3)]
    ext = max(h - l for l, h in zip(lo, hi))
    s = round(min(0.625, 16 / ext * 0.85), 4)
    c = [(l + h) / 2 for l, h in zip(lo, hi)]
    tr = [round(-(c[0] - 8) * s, 3), round(-(c[1] - 8) * s, 3), 0]
    m = dict(model)
    m['display'] = dict(model.get('display', {}))
    m['display']['gui'] = {'rotation': [30, 225, 0], 'translation': tr, 'scale': [s, s, s]}
    m['display']['ground'] = {'rotation': [0, 0, 0], 'translation': [0, 2, 0], 'scale': [s * 0.6] * 3}
    m['display']['fixed'] = {'rotation': [0, 180, 0], 'translation': tr, 'scale': [s] * 3}
    return m


def armaduras():
    files = {}
    for set_id, tiers in VISUAL.items():
        for t, vid in tiers.items():
            if not vid:
                continue  # sin modelo elegido: queda la reserva del pack publico (T5 de la clase)
            name = f'{set_id}_{t}'
            tex = f'armadura_{vid}'
            for layer in ('humanoid', 'humanoid_leggings'):
                src = ARTE / f'assets/astral/textures/entity/equipment/{layer}/{tex}.png'
                files[f'assets/astral/textures/entity/equipment/{layer}/{tex}.png'] = src.read_bytes()
            files[f'assets/astral/equipment/{name}.json'] = js({'layers': {
                'humanoid': [{'texture': f'astral:{tex}'}], 'humanoid_leggings': [{'texture': f'astral:{tex}'}]}})
            # Casco 3D: en la cabeza (display_context head) y en el inventario.
            casco = json.loads((ARTE / f'assets/astral/models/item/{tex}_casco_3d.json').read_text(encoding='utf-8'))
            files[f'assets/astral/models/item/{tex}_casco_3d.json'] = js(casco)
            files[f'assets/astral/models/item/{tex}_casco_gui.json'] = js(icono_gui(casco))
            files[f'assets/astral/textures/item/{tex}_casco.png'] = (ARTE / f'assets/astral/textures/item/{tex}_casco.png').read_bytes()
            files[f'assets/astral/items/{name}_helmet.json'] = js({'model': {
                'type': 'minecraft:select', 'property': 'minecraft:display_context',
                'cases': [{'when': 'head', 'model': {'type': 'minecraft:model', 'model': f'astral:item/{tex}_casco_3d'}}],
                'fallback': {'type': 'minecraft:model', 'model': f'astral:item/{tex}_casco_gui'}}})
            # Pechera, grebas y botas: icono plano sacado de la textura puesta (como los T1-T5).
            main = Image.open(ARTE / f'assets/astral/textures/entity/equipment/humanoid/{tex}.png').convert('RGBA')
            legs = Image.open(ARTE / f'assets/astral/textures/entity/equipment/humanoid_leggings/{tex}.png').convert('RGBA')
            small = [i.resize((64, 32), Image.Resampling.BOX) for i in (main, legs)]
            for piece, img in icons(*small).items():
                if piece == 'helmet':
                    continue
                iid = f'{name}_{piece}'
                files[f'assets/astral/textures/item/t6_10/{iid}.png'] = png(img)
                files[f'assets/astral/models/item/{iid}.json'] = js(
                    {'parent': 'minecraft:item/generated', 'textures': {'layer0': f'astral:item/t6_10/{iid}'}})
                files[f'assets/astral/items/{iid}.json'] = js({'model': {'type': 'minecraft:model', 'model': f'astral:item/{iid}'}})
    return files


def main():
    if not BASE.exists() or not ARTE.exists():
        print('Falta el pack base o el arte privado: no se genera nada.')
        return
    with zipfile.ZipFile(BASE) as z:
        files = {n: z.read(n) for n in z.namelist()}
    pub = cambios_publicos()
    files.update(pub)
    priv = armaduras()
    files.update(priv)
    OUT.mkdir(parents=True, exist_ok=True)
    target = OUT / 'AstralRPG-Textures.zip'
    tmp = target.with_suffix('.zip.tmp')
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as out:
        for name, data in sorted(files.items()):
            out.writestr(zipfile.ZipInfo(name, date_time=STAMP), data, compress_type=zipfile.ZIP_DEFLATED)
    from pack_audit import audit
    audit(tmp)
    tmp.replace(target)
    digest = hashlib.sha1(target.read_bytes()).hexdigest()
    (OUT / 'pack.sha1').write_text(digest + '\n')
    print(f'{len(pub)} cambios publicos, {len(priv)} archivos de armaduras -> {target} ({digest})')


if __name__ == '__main__':
    main()
