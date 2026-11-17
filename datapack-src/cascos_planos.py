"""Cascos: conservar el arbol de cabeza y aplanar cada modelo fuera de ella.

Trabaja sobre el diccionario del pack recibido: nunca importa arte privado.
Si recibe arte privado, sus PNG derivados deben guardarse en ese mismo circuito.
"""
import copy
import io
import json

import numpy as np
from PIL import Image, ImageDraw

import armas_mod as A
import armaduras_geo as G


def js(obj):
    return (json.dumps(obj, ensure_ascii=False, indent=1) + '\n').encode('utf8')


def resolve(files, ref):
    ns, path = ref.split(':', 1)
    key = f'assets/{ns}/models/{path}.json'
    if key not in files:
        if ns == 'minecraft':
            return {'parent': ref}
        raise ValueError('Modelo faltante: ' + ref)
    raw = json.loads(files[key])
    parent = raw.get('parent')
    if parent and not parent.endswith(('generated', 'handheld')):
        base = resolve(files, parent)
        raw = {**base, **raw, 'textures': {**base.get('textures', {}), **raw.get('textures', {})},
               'display': {**base.get('display', {}), **raw.get('display', {})}}
    return raw


def render_model(files, ref, size=128):
    raw = resolve(files, ref)
    layers = []
    textures = raw.get('textures', {})
    groups = {}
    for e in raw.get('elements', []):
        for face, fd in e.get('faces', {}).items():
            tex = fd['texture']
            while tex.startswith('#'):
                tex = textures[tex[1:]]
            groups.setdefault(tex, []).append(dict(e, faces={face: fd}))
    for tex, els in groups.items():
        ns, path = tex.split(':', 1)
        im = Image.open(io.BytesIO(files[f'assets/{ns}/textures/{path}.png'])).convert('RGBA')
        quads = A.quads_modelo(dict(raw, elements=els), im.size)
        layers.append((quads, np.asarray(im, dtype=np.float32) / 255))
    if not layers:
        raise ValueError('Sin elementos para renderizar: ' + ref)
    points = np.concatenate([q for qs, _ in layers for q, _ in qs])
    lo, hi = points.min(0), points.max(0)
    ctr = (lo + hi) / 2
    old = G.W, G.H, G.S
    try:
        G.W = G.H = size
        G.S = size * .70 / max(float(np.linalg.norm(hi - lo)), 1)
        centered = [([(q - ctr + [0, 20, 0], uv) for q, uv in qs], tex) for qs, tex in layers]
        im = G.render(centered, yaw=25, pitch=12)
    finally:
        G.W, G.H, G.S = old
    bbox = im.getbbox()
    if not bbox:
        raise ValueError('Render vacio: ' + ref)
    crop = im.crop(bbox)
    crop.thumbnail((size - 8, size - 8), Image.Resampling.LANCZOS)
    result = Image.new('RGBA', (size, size))
    result.alpha_composite(crop, ((size - crop.width) // 2, (size - crop.height) // 2))
    return result


def context(tree, value):
    """Resuelve solo display_context, conserva condiciones y custom_model_data."""
    if tree.get('property') == 'minecraft:display_context':
        for case in tree['cases']:
            when = case['when']
            if value in (when if isinstance(when, list) else [when]):
                return context(case['model'], value)
        return context(tree['fallback'], value)
    out = copy.deepcopy(tree)
    for k, v in list(out.items()):
        if isinstance(v, dict):
            out[k] = context(v, value)
        elif isinstance(v, list):
            out[k] = [context(x, value) if isinstance(x, dict) else x for x in v]
    return out


def normalize(files, preview=None):
    cache, rows = {}, []

    def flat(tree):
        out = copy.deepcopy(tree)
        if out.get('type') == 'minecraft:model':
            ref = out['model']
            raw = resolve(files, ref)
            if raw.get('elements'):
                if ref not in cache:
                    ns, path = ref.split(':', 1)
                    target = f'item/cascos_planos/{ns}/{path}'
                    image = render_model(files, ref)
                    icon = image.resize((32, 32), Image.Resampling.BOX)
                    # Alfa binario: el extruido vanilla no deja halos semitransparentes.
                    icon.putalpha(icon.getchannel('A').point(lambda a: 255 if a >= 128 else 0))
                    buf = io.BytesIO(); icon.save(buf, 'PNG')
                    files[f'assets/astral/textures/{target}.png'] = buf.getvalue()
                    files[f'assets/astral/models/{target}.json'] = js({
                        'parent': 'minecraft:item/generated', 'textures': {'layer0': 'astral:' + target}})
                    cache[ref] = 'astral:' + target
                    rows.append((ref, image, icon))
                out['model'] = cache[ref]
            return out
        for key, val in list(out.items()):
            if isinstance(val, dict):
                out[key] = flat(val)
            elif isinstance(val, list):
                out[key] = [flat(v) if isinstance(v, dict) else v for v in val]
        return out

    for name, blob in list(files.items()):
        if not (name.startswith('assets/astral/items/') and name.endswith('.json')):
            continue
        iid = name.rsplit('/', 1)[-1][:-5]
        if not (iid.endswith('_helmet') or iid.startswith(('sombrero_', 'casco_'))):
            continue
        data = json.loads(blob)
        tree = data['model']
        data['model'] = {'type': 'minecraft:select', 'property': 'minecraft:display_context',
                         'cases': [{'when': 'head', 'model': context(tree, 'head')}],
                         'fallback': flat(context(tree, 'gui'))}
        files[name] = js(data)
    if preview:
        cols, cw, ch = 4, 290, 170
        sheet = Image.new('RGBA', (cols * cw, max(1, (len(rows) + cols - 1) // cols) * ch), '#242735')
        draw = ImageDraw.Draw(sheet)
        for i, (ref, model, icon) in enumerate(rows):
            x, y = i % cols * cw, i // cols * ch
            sheet.alpha_composite(model, (x, y))
            sheet.alpha_composite(icon.resize((96, 96), Image.Resampling.NEAREST), (x + 160, y + 16))
            label = ref.split(':')[1].replace('item/', '')
            draw.text((x + 4, y + 136), label[:43], fill='white')
        preview.parent.mkdir(parents=True, exist_ok=True)
        sheet.convert('RGB').save(preview)
    return sorted(cache)
