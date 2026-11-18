"""Preparar arte Gemini propio y fuentes Atlas desde los recursos reales.

Importacion explicita: python guia_atlas_arte.py --importar <carpeta-Gemini>.
No requiere originales en builds posteriores; conserva los PNG reemplazables.
"""
import argparse
import io
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps
from guia_atlas import ART, DECOR


def png(im):
    out = io.BytesIO()
    im.save(out, 'PNG')
    return out.getvalue()


def normalize(im):
    # Las piezas tienen escalones de aproximadamente cuatro pixeles de origen.
    # NEAREST evita inventar subpixeles; paleta de 64 colores, sin dithering.
    im = im.convert('RGB').resize((max(1, im.width // 4), max(1, im.height // 4)), Image.Resampling.NEAREST)
    im = im.quantize(colors=64, dither=Image.Dither.NONE).convert('RGBA')
    # Solo el fondo exterior conectado: nunca borrar interiores azul noche.
    pixels = im.load()
    pending = [(x, y) for x in range(im.width) for y in (0, im.height - 1)]
    pending += [(x, y) for y in range(im.height) for x in (0, im.width - 1)]
    visited = set()
    while pending:
        x, y = pending.pop()
        if (x, y) in visited or not (0 <= x < im.width and 0 <= y < im.height):
            continue
        visited.add((x, y))
        r, g, b, _ = pixels[x, y]
        if (r - 20)**2 + (g - 18)**2 + (b - 31)**2 > 24**2:
            continue
        pixels[x, y] = (r, g, b, 0)
        pending += [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
    return im


def import_art(source):
    ART.mkdir(parents=True, exist_ok=True)
    inputs = {'cabecera': ('atlas_cabecera_botones_finos.png', (32, 0, 896, 312)),
              'indice': ('atlas_ventana_ancha.png', (0, 0, 1376, 128)),
              'catalogo': ('atlas_catalogo.png', (0, 0, 928, 180)),
              'receta': ('atlas_receta.png', (0, 0, 1200, 132)),
              'ficha': ('atlas_ventana_vacia.png', (0, 0, 825, 180))}
    for name, (filename, box) in inputs.items():
        normalize(Image.open(source / filename).crop(box)).save(ART / (name + '.png'))
    for sheet, names in [(1, DECOR[5:11]), (2, DECOR[11:])]:
        im = Image.open(source / f'atlas_ilustraciones_{sheet}.png')
        for n, name in enumerate(names):
            x, y = n % 3 * 459, n // 3 * 368
            normalize(im.crop((x + 70, y + 48, min(x + 390, im.width), y + 352))).save(ART / (name + '.png'))
    for filename in ('atlas_ventana_vacia', 'atlas_ventana_ancha', 'atlas_receta', 'atlas_catalogo', 'atlas_botones', 'atlas_cabecera_botones_finos'):
        normalize(Image.open(source / (filename + '.png'))).save(ART / ('reserva_' + filename + '.png'))


def texture_for_item(files, iid):
    """Sigue item_model, padres y referencias # de la textura GUI vigente."""
    def obj(path):
        return json.loads(files[path]) if path in files else {}
    def resource(ref, folder):
        ns, name = ref.split(':', 1) if ':' in ref else ('minecraft', ref)
        return f'assets/{ns}/{folder}/{name}.json'
    tree = obj(f'assets/astral/items/{iid}.json').get('model', {})
    for _ in range(20):
        if isinstance(tree.get('model'), str):
            break
        tree = tree.get('on_false', tree.get('fallback', {}))
    ref = tree.get('model')
    textures, seen = {}, set()
    while ref and ref not in seen:
        seen.add(ref)
        data = obj(resource(ref, 'models'))
        textures = {**data.get('textures', {}), **textures}
        ref = data.get('parent')
    ref = textures.get('layer0') or textures.get('all') or textures.get('particle') or next(iter(textures.values()), None)
    seen = set()
    while ref and ref.startswith('#') and ref not in seen:
        seen.add(ref)
        ref = textures.get(ref[1:])
    if not ref or ref.startswith('#'):
        return None
    ns, name = ref.split(':', 1) if ':' in ref else ('minecraft', ref)
    data = files.get(f'assets/{ns}/textures/{name}.png')
    return Image.open(io.BytesIO(data)).convert('RGBA') if data else None


def complete_assets(files, iconmap, rows, modelroot, private_models=None):
    """Agrega glifos sin tocar fuente default ni assets ajenos al Atlas."""
    from guia_atlas import assets
    out = assets()
    font = json.loads(out['assets/astral/font/guia_atlas.json'])
    missing = []
    for iid, char in iconmap.items():
        im = texture_for_item(files, iid)
        if im is None:
            missing.append(iid)
            # Reserva explicita: no inventar una ilustracion del objeto.
            im = Image.new('RGBA', (16, 16))
        else:
            im = ImageOps.contain(im, (16, 16), Image.Resampling.NEAREST)
        canvas = Image.new('RGBA', (16, 16))
        canvas.alpha_composite(im, ((16 - im.width) // 2, (16 - im.height) // 2))
        out[f'assets/astral/textures/gui/atlas/iconos/{iid}.png'] = png(canvas)
        font['providers'].append(dict(type='bitmap', file=f'astral:gui/atlas/iconos/{iid}.png', height=12, ascent=10, chars=[char]))

    # Renderer existente: cubos/UV/huesos del .bbmodel real, sin IA generativa.
    # collect permite reutilizar la misma camara 3/4. Su hoja auxiliar permanece privada.
    from build_privado import preview
    models, unavailable = {}, []
    for row in rows:
        mid = row['model']
        if mid is None:
            continue
        path = Path(modelroot) / (mid + '.bbmodel')
        if private_models and mid in private_models:
            models[mid] = private_models[mid]
        elif path.exists():
            models[mid] = json.loads(path.read_text('utf8'))
        else:
            unavailable.append(mid)
    renders = {}
    if models:
        preview(models, name='guia-atlas-modelos-cpu', include_sword=False, collect=renders)
    for n, row in enumerate(rows):
        if row['model'] is None:
            continue
        canvas = Image.new('RGBA', (96, 96))
        im = renders.get(row['model'])
        if im is not None:
            im = ImageOps.contain(im, (92, 92), Image.Resampling.NEAREST)
            canvas.alpha_composite(im, ((96 - im.width) // 2, (96 - im.height) // 2))
        else:
            ImageDraw.Draw(canvas).text((38, 38), '?', fill='#e8b24a')
        mid = row['id']
        out[f'assets/astral/textures/gui/atlas/mobs/{mid}.png'] = png(canvas)
        font['providers'].append(dict(type='bitmap', file=f'astral:gui/atlas/mobs/{mid}.png', height=64, ascent=7, chars=[chr(0xF000 + n)]))
    # Reserva invisible para iconos sin textura propia. El item vanilla sigue
    # mostrandose en el cuerpo nativo con su modelo real y tooltip.
    out['assets/astral/font/guia_atlas.json'] = json.dumps(font).encode()
    out['assets/astral/atlas-audit.json'] = json.dumps(dict(iconos_sin_textura=missing, modelos_sin_retrato=unavailable)).encode()
    return out


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--importar', type=Path, required=True)
    import_art(parser.parse_args().importar)
