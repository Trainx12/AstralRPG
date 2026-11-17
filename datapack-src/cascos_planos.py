"""Cascos: conservar el arbol de cabeza y aplanar cada modelo fuera de ella.

Trabaja sobre el diccionario del pack recibido: nunca importa arte privado.
Si recibe arte privado, sus PNG derivados deben guardarse en ese mismo circuito.
"""
import copy
import io
import json

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

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


def render_model(files, ref, size=192, gui=False):
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
        # Compensar el origen y desplazamiento del renderer en espacio de camara.
        R = G.rot_matrix(12, 0, 0) @ G.rot_matrix(0, 25, 0)
        offset = np.array([0, 16, 0]) + R.T @ np.array([0, 4, 0])
        centered = [([(q - ctr + offset, uv) for q, uv in qs], tex) for qs, tex in layers]
        if gui:
            display = raw.get('display', {}).get('gui', {})
            rotation = G.rot_matrix(*display.get('rotation', [30, 225, 0]))
            scale = np.array(display.get('scale', [.625]*3))
            translation = np.array(display.get('translation', [0]*3))
            G.S = size / 16
            centered = [([(((q-8)*scale) @ rotation.T + translation + [0,20,0], uv)
                          for q,uv in qs], tex) for qs,tex in layers]
        im = G.render(centered, yaw=0 if gui else 25, pitch=0 if gui else 12)
    finally:
        G.W, G.H, G.S = old
    if gui:
        return im
    bbox = im.getbbox()
    if not bbox:
        raise ValueError('Render vacio: ' + ref)
    crop = im.crop(bbox)
    crop.thumbnail((size - 8, size - 8), Image.Resampling.LANCZOS)
    result = Image.new('RGBA', (size, size))
    result.alpha_composite(crop, ((size - crop.width) // 2, (size - crop.height) // 2))
    return result


def pixel_icon(image):
    """28 px de arte + contorno de 1 px + margen de 1 px, sin dithering/halos."""
    crop = image.crop(image.getbbox())
    crop.thumbnail((28, 28), Image.Resampling.BOX)
    a = np.array(crop)
    mask = a[..., 3] >= 96
    rgb = a[..., :3].astype(float) / 255
    # Levantar sombras conservando los matices originales; refuerzo en cascos oscuros.
    luma = rgb @ np.array([.2126, .7152, .0722])
    gamma = .64 if np.median(luma[mask]) < .22 else .85
    rgb = np.clip((rgb ** gamma - .45) * 1.08 + .47, 0, 1)
    if gamma < .8:
        median = np.median((rgb @ np.array([.2126,.7152,.0722]))[mask])
        rgb = np.clip(rgb * min(2.8, .30/max(median,.01)),0,1)
    a[..., :3] = (rgb * 255).astype('uint8')
    a[..., 3] = mask.astype('uint8') * 255
    # Paleta local al casco: 24 colores de su render iluminado, sin colores ajenos.
    opaque = Image.fromarray(a).convert('RGB')
    samples = Image.fromarray(a[..., :3][mask].reshape(1, -1, 3))
    palette = samples.quantize(colors=24, method=Image.Quantize.MEDIANCUT)
    clean = opaque.quantize(palette=palette, dither=Image.Dither.NONE).convert('RGBA')
    clean.putalpha(Image.fromarray(a[..., 3]))
    result = Image.new('RGBA', (32, 32))
    result.alpha_composite(clean, ((32-clean.width)//2, (32-clean.height)//2))
    alpha = result.getchannel('A')
    # Solo pixeles aislados, sin quitar detalles finos conectados al casco.
    pixels = np.array(alpha) > 0
    neighbors = sum(np.roll(np.roll(pixels, dy, 0), dx, 1).astype(int)
                    for dx, dy in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,1),(1,-1),(-1,-1)))
    pixels &= neighbors > 0
    alpha = Image.fromarray(pixels.astype('uint8')*255)
    result.putalpha(alpha)
    outline = Image.new('RGBA', result.size, (31, 25, 30, 255))
    outline.putalpha(alpha.filter(ImageFilter.MaxFilter(3)))
    outline.alpha_composite(result)
    return outline


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
            if ref.startswith('astral:item/cascos_planos/'):
                # Regenerar desde la geometria original, nunca desde un PNG anterior.
                source = ref.removeprefix('astral:item/cascos_planos/')
                ns, path = source.split('/', 1)
                ref = ns + ':' + path
            raw = resolve(files, ref)
            if raw.get('elements'):
                if ref not in cache:
                    ns, path = ref.split(':', 1)
                    target = f'item/cascos_planos/{ns}/{path}'
                    image = render_model(files, ref)
                    icon = pixel_icon(image)
                    buf = io.BytesIO(); icon.save(buf, 'PNG')
                    files[f'assets/astral/textures/{target}.png'] = buf.getvalue()
                    files[f'assets/astral/models/{target}.json'] = js({
                        'parent': 'minecraft:item/generated', 'gui_light': 'front',
                        'textures': {'layer0': 'astral:' + target}})
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
