"""Entrega de prueba Atlas por delta sobre el ultimo FINAL. No publica ni despliega."""
import argparse
import hashlib
import json
import zipfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
from terceros import ROOT, privado
from final_base import select_base
from guia_atlas_arte import complete_assets

NAME = 'guia-atlas-fase1'


def readzip(path):
    with zipfile.ZipFile(path) as z:
        return {n: z.read(n) for n in z.namelist() if not n.endswith('/')}


def writezip(path, files):
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        for name, blob in sorted(files.items()):
            z.writestr(zipfile.ZipInfo(name, (2026, 11, 17, 0, 0, 0)), blob, compress_type=zipfile.ZIP_DEFLATED)


def datapack_delta(base, task):
    """Preserva CNK y trabajo acumulado; solo agrega namespace Atlas y sus tags."""
    result = dict(base)
    result.update({n: b for n, b in task.items() if n.startswith(('data/astral/dialog/atlas/', 'data/astral/function/atlas/', 'data/astral/atlas/'))})
    for tag in ('load', 'tick'):
        name = f'data/minecraft/tags/function/{tag}.json'
        obj = json.loads(result[name])
        value = 'astral:atlas/' + tag
        if value not in obj['values']:
            obj['values'].append(value)
        result[name] = json.dumps(obj).encode()
    return result


def previews(pack, datapack, destination, public=True):
    """Laminas CPU del contenido real; no son capturas ni prometen fondo custom."""
    from guia_atlas_arte import texture_for_item
    font_path = Path('C:/Windows/Fonts/arial.ttf')
    font = ImageFont.truetype(str(font_path), 17) if font_path.exists() else ImageFont.load_default()
    def label(obj):
        if isinstance(obj, str):
            return obj
        if isinstance(obj, list):
            return ''.join(label(x) for x in obj)
        return obj.get('text', '') if isinstance(obj, dict) else ''
    choices = {'indice': 'atlas/indice', 'berserker': 'atlas/catalogo/armadura_1/1',
               'xp': 'atlas/seccion/consumibles', 'bestiario': 'atlas/criatura/astral_mapache'}
    recipe = next(n for n in datapack if n.startswith('data/astral/dialog/atlas/receta/'))
    choices['receta'] = recipe.removeprefix('data/astral/dialog/').removesuffix('.json')
    for name, path in choices.items():
        data = json.loads(datapack['data/astral/dialog/' + path + '.json'])
        canvas = Image.new('RGB', (900, 1100), '#151b30')
        draw = ImageDraw.Draw(canvas)
        draw.text((24, 16), 'RENDER CPU · prototipo de contenido; validar layout en cliente', font=font, fill='#e8b24a')
        draw.text((24, 45), label(data['title']), font=font, fill='white')
        y = 85
        for body in data['body']:
            if body['type'] == 'minecraft:item':
                item = body['item']
                model = item.get('components', {}).get('minecraft:item_model', '')
                iid = model.split(':')[-1]
                icon = texture_for_item(pack, iid)
                if icon:
                    icon = ImageOps.contain(icon, (52, 52), Image.Resampling.NEAREST)
                    canvas.paste(icon, (24, y), icon)
                desc = label(body.get('description', {}).get('contents', {}))
                for line in desc.splitlines():
                    draw.text((92, y), line[:92], font=font, fill='#e5d9bb'); y += 23
                y += 30
            else:
                contents = body.get('contents', {})
                value = label(contents)
                char = next((c for c in value if 0xE900 <= ord(c) < 0xF100), None)
                if char:
                    font_data = json.loads(pack['assets/astral/font/guia_atlas.json'])
                    provider = next((p for p in font_data['providers'] if char in ''.join(p.get('chars', []))), None)
                    if provider:
                        ns, rel = provider['file'].split(':')
                        im = Image.open(__import__('io').BytesIO(pack[f'assets/{ns}/textures/{rel}'])).convert('RGBA')
                        im = ImageOps.contain(im, (600, 125), Image.Resampling.NEAREST)
                        canvas.paste(im, (24, y), im); y += im.height + 16
                else:
                    import textwrap
                    for line in textwrap.wrap(value, 92):
                        draw.text((24, y), line, font=font, fill='#e5d9bb'); y += 23
                if y > 850:
                    break
        for n, button in enumerate(data.get('actions', [])):
            columns = data.get('columns', 2)
            x = 24 + (n % columns) * 430
            by = y + n // columns * 35
            draw.rectangle((x, by, x + 412, by + 30), fill='#222e4e', outline='#39d4ff')
            value = ''.join(c for c in label(button['label']) if ord(c) < 0xE000)
            draw.text((x + 8, by + 3), value[:48], font=font, fill='white')
        destination.mkdir(parents=True, exist_ok=True)
        canvas.save(destination / f'guia_atlas_fase1_{name}.png')


def prepare(public_root, base=None, data_base=None):
    out = privado() / 'build/entregas' / NAME
    out.mkdir(parents=True, exist_ok=True)
    base = select_base(output=out, explicit=base)
    original = readzip(base)
    task = readzip(public_root / 'build/AstralRPG-Items.zip')
    iconmap = json.loads(task['data/astral/atlas/iconos.json'])
    rows = json.loads(task['data/astral/atlas/bestiario.json'])
    # Modelos privados adaptados mas recientes; nunca salen del circuito privado.
    models = {}
    paths = list((privado() / 'build/models').glob('*.bbmodel'))
    paths += list((privado() / 'build/entregas').glob('*/models/*.bbmodel'))
    for path in sorted(paths, key=lambda p: p.stat().st_mtime_ns):
        models[path.stem] = json.loads(path.read_text('utf8'))
    patch = complete_assets(original, iconmap, rows, ROOT / 'build/models', models)
    result = {**original, **patch}
    assert all(result[n] == b for n, b in original.items() if n not in patch)
    writezip(out / 'AstralRPG-Textures.zip', result)
    if data_base is None:
        candidates = [p for p in (privado() / 'build/entregas').rglob('AstralRPG-Items*.zip') if out not in p.parents]
        if not candidates:
            raise FileNotFoundError('Falta datapack privado acumulado; indicar --datapack-base')
        data_base = max(candidates, key=lambda p: p.stat().st_mtime_ns)
    combined = datapack_delta(readzip(data_base), task)
    writezip(out / 'AstralRPG-Items-PRUEBA.zip', combined)
    # Copia acumulada local sin mezclarla con el artefacto publicado de tarea.
    cumulative = ROOT / 'build/AstralRPG-Items.zip'
    writezip(out / 'AstralRPG-Items-ACUMULADO-PRUEBA.zip', datapack_delta(readzip(cumulative), task))
    manifest = dict(base=str(base.relative_to(ROOT)), base_sha1=hashlib.sha1(base.read_bytes()).hexdigest(),
                    datapack_base=str(data_base.relative_to(ROOT)),
                    datapack_base_sha256=hashlib.sha256(data_base.read_bytes()).hexdigest(),
                    files={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in out.glob('*.zip')},
                    pack_sha1=hashlib.sha1((out / 'AstralRPG-Textures.zip').read_bytes()).hexdigest(),
                    changed=sorted(patch))
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2), 'utf8')
    (out / 'pack.sha1').write_text(manifest['pack_sha1'] + '\n', 'utf8')
    previews(result, task, out / 'previews', public=False)
    public_pack = readzip(public_root / 'build/AstralRPG-Textures.zip')
    previews(public_pack, task, ROOT / 'build/previews')
    print('FINAL de prueba:', out, '\nSHA-1:', manifest['pack_sha1'])
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--public-root', type=Path, default=ROOT)
    parser.add_argument('--base', type=Path)
    parser.add_argument('--datapack-base', type=Path)
    args = parser.parse_args()
    prepare(args.public_root.resolve(), args.base, args.datapack_base)
