"""Entrega privada: arte de Gemini (tanda 2) sobre el FINAL d7310b3 instalado. Sin red ni despliegue.

- Retratos pintados de las 17 mascotas nuevas (pantalla Mi companero y tarjetas de las paginas 2-4).
- Gorros agrandados en la vitrina de sombreros (copias de vista con escala de inventario mayor).
- Todo lo demas sale del pack publico regenerado (solo las entradas que cambiaron desde HEAD).
"""
import hashlib
import io
import json
import subprocess
import zipfile
from PIL import Image
from terceros import ROOT, privado
from pack_audit import audit

BASE_SHA = 'd7310b324b82bf0c060e70f9febeb152c446a1a2'
BASE = 'build/entregas/disenos-pendientes/AstralRPG-Textures.zip'
DELIVERY = 'build/entregas/disenos-gemini'


def read_zip(src):
    with zipfile.ZipFile(src) as z:
        return {n: z.read(n) for n in z.namelist()}


def prepare():
    import companero_ui
    import mascotas_ui
    import gorros_ui
    base = privado()/BASE
    if hashlib.sha1(base.read_bytes()).hexdigest() != BASE_SHA:
        raise ValueError('La base instalada no coincide: no combinar')
    original = read_zip(base); files = dict(original)
    public = read_zip(ROOT/'build/AstralRPG-Textures.zip')
    previous = read_zip(io.BytesIO(subprocess.check_output(['git', 'show', 'HEAD:build/AstralRPG-Textures.zip'], cwd=ROOT)))
    for name, blob in public.items():
        if blob != previous.get(name) and name != 'assets/minecraft/font/default.json':
            files[name] = blob
    # Fuente: la publica nueva + proveedores que solo existian en el FINAL instalado.
    font = json.loads(public['assets/minecraft/font/default.json'])
    oldfont = json.loads(original['assets/minecraft/font/default.json'])
    def chars(p): return set(p.get('advances', {})) | set(''.join(p.get('chars', [])))
    used = set()
    for p in font['providers']: used |= chars(p)
    for p in oldfont['providers']:
        if chars(p) and not chars(p) & used: font['providers'].append(p)
    files['assets/minecraft/font/default.json'] = json.dumps(font, ensure_ascii=False).encode()
    # Arte privado: retratos pintados de las mascotas de terceros.
    art = privado()/'arte/gemini'
    for pid in mascotas_ui.EXTRA:
        image = Image.open(art/f'retrato_{pid}.png').convert('RGBA')
        companero_ui.PORTRAITS[pid] = image
        mascotas_ui.CARD_ART[pid] = image
    detail, _ = companero_ui.assets()
    pages, _ = mascotas_ui.assets()
    for name, blob in {**detail, **pages}.items():
        if name.endswith('.png'):
            files[name] = blob
    files.update(gorros_ui.private_menu_models(files))
    dest = privado()/DELIVERY; dest.mkdir(parents=True, exist_ok=True)
    target = dest/'AstralRPG-Textures.zip'
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as z:
        for name, blob in sorted(files.items()):
            z.writestr(zipfile.ZipInfo(name, (2026, 11, 12, 0, 0, 0)), blob, compress_type=zipfile.ZIP_DEFLATED)
    refs = audit(target); sha = hashlib.sha1(target.read_bytes()).hexdigest()
    (dest/'pack.sha1').write_text(sha+'\n')
    changed = sorted(n for n in files if files[n] != original.get(n)); removed = sorted(set(original)-set(files))
    (dest/'procedencia.json').write_text(json.dumps(dict(base_sha1=BASE_SHA, final_sha1=sha, changed=changed,
        removed=removed, references=refs), indent=2), encoding='utf8')
    print('FINAL', target, 'SHA1', sha, 'referencias', refs, 'cambiadas', len(changed), 'retiradas', len(removed))
    return target, sha


if __name__ == '__main__':
    prepare()
