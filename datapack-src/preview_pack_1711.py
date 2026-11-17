"""Comparacion CPU privada: misma camara y transformacion FP sin autoencuadrar.

Referencia: cliente oficial Mojang suministrado por --client; jamas publicar sus assets.
Posicion de reposo, sin balanceo ni animacion del brazo/carga del cliente.
"""
import argparse
import io
import json
import math
import zipfile

import numpy as np
from PIL import Image, ImageDraw

import armas_mod as A
import armaduras_geo as G
from cascos_planos import resolve
from deploy_pack_1711 import BASE, OUT


def readpack(path):
    with zipfile.ZipFile(path) as z:
        return {n: z.read(n) for n in z.namelist()}


def generated(im):
    """Frente/dorso y cantos del contorno: grosor vanilla de 1 unidad."""
    w = im.width
    im = im.crop((0, 0, w, w))
    a = np.asarray(im)[..., 3] > 25
    els = [{'from': [0, 0, 7.5], 'to': [16, 16, 8.5], 'faces': {
        'south': {'texture': '#t', 'uv': [0, 0, 16, 16]},
        'north': {'texture': '#t', 'uv': [16, 0, 0, 16]}}}]
    u = 16 / w
    for y, x in zip(*np.nonzero(a)):
        faces = {}
        for face, dy, dx in [('up', -1, 0), ('down', 1, 0), ('west', 0, -1), ('east', 0, 1)]:
            yy, xx = y + dy, x + dx
            if not (0 <= yy < w and 0 <= xx < w and a[yy, xx]):
                faces[face] = {'texture': '#t', 'uv': [x*u, y*u, (x+1)*u, (y+1)*u]}
        if faces:
            els.append({'from': [x*u, 16-(y+1)*u, 7.5],
                        'to': [(x+1)*u, 16-y*u, 8.5], 'faces': faces})
    return {'elements': els}


def render(files, ref, side='righthand', transparent=False):
    model = resolve(files, ref)
    texref = model.get('textures', {}).get('layer0', model.get('textures', {}).get('t'))
    if not texref:
        raise ValueError(ref)
    ns, path = texref.split(':', 1) if ':' in texref else ('minecraft', texref)
    tex = Image.open(io.BytesIO(files[f'assets/{ns}/textures/{path}.png'])).convert('RGBA')
    frame = tex.crop((0, 0, tex.width, tex.width))
    d = model.get('display', {}).get('firstperson_' + side, {})
    if not model.get('elements'):
        model = dict(model, **generated(frame))
    # UV de un fotograma, no de la tira animada completa (T10 tiene dos).
    quads = A.quads_modelo(model, frame.size)
    r = list(d.get('rotation', [0, 0, 0]))
    if side == 'lefthand':
        r[1],r[2] = -r[1],-r[2]
    R = A._rx(r[0]) @ A._ry(r[1]) @ A._rz(r[2])
    scale = np.array(d.get('scale', [1]*3))
    tr = np.array(d.get('translation', [0]*3)) / 16
    if side == 'lefthand':
        tr[0] *= -1
    transformed = []
    width, height = 400, 225
    focal = height / (2 * math.tan(math.radians(70) / 2))
    for pts, uv in quads:
        p = ((pts-8)*scale) @ R.T / 16 + tr + [(-.56 if side == 'lefthand' else .56), -.52, -.72]
        if np.any(p[:, 2] >= -.03):
            continue
        screen_x = p[:, 0] * focal / -p[:, 2]
        screen_y = -p[:, 1] * focal / -p[:, 2]
        transformed.append((np.column_stack([-screen_x, 20-screen_y, -p[:, 2]]), uv))
    old = G.W, G.H, G.S
    try:
        G.W, G.H, G.S = width, height, 1
        im = G.render([(transformed, np.asarray(frame, dtype=np.float32)/255)], yaw=0, pitch=0)
    finally:
        G.W, G.H, G.S = old
    if transparent:
        return im
    bg = Image.new('RGBA', im.size, '#343b43')
    dr = ImageDraw.Draw(bg)
    dr.line((0, 142, width, 142), fill='#56636a')
    dr.line((width//2-5, height//2, width//2+5, height//2), fill='white')
    dr.line((width//2, height//2-5, width//2, height//2+5), fill='white')
    bg.alpha_composite(im)
    return bg


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--client', required=True)
    args = ap.parse_args()
    vanilla = readpack(args.client)
    before, after = readpack(BASE), readpack(OUT / 'AstralRPG-Textures.zip')
    # Resolver herencia vanilla (generated no declara firstperson: se hereda de generated/handheld).
    for family in ('bow', 'crossbow'):
        key = f'assets/minecraft/models/item/{family}.json'
        m = json.loads(vanilla[key])
        m['display'] = dict(A.VANILLA['item/'+family], **m.get('display', {}))
        vanilla[key] = json.dumps(m).encode()
    metrics=[]
    for family, ids, suffixes in [
        ('ballestas', ['ballesta_3', 'ballesta_4', 'ballesta_5'],
         ['', '_pulling_0', '_pulling_1', '_pulling_2', '_arrow', '_firework']),
        ('arcos', [f'arco_{t}' for t in range(6,11)] + ['agua_arco'],
         ['', '_pulling_0', '_pulling_1', '_pulling_2'])]:
        rows = [(iid+s, s, side) for iid in ids for s in suffixes for side in ('righthand','lefthand')]
        sheet = Image.new('RGBA', (1200, 40 + len(rows)*250), '#20242c')
        summary = Image.new('RGBA', (1200,40+len(ids)*2*250),'#20242c')
        ImageDraw.Draw(summary).text((12,10),'VANILLA / BASE INSTALADA / DESPUES - derecha e izquierda, reposo y carga final',fill='white')
        summary_rows=0
        draw = ImageDraw.Draw(sheet)
        draw.text((12, 10), 'VANILLA / ANTES / DESPUES - CPU, FOV 70, reposo, misma camara (sin autoajuste)', fill='white')
        for i, (name, suffix, side) in enumerate(rows):
            ref = 'astral:item/' + name
            y = 40 + i*250
            vname = ('crossbow' if family == 'ballestas' else 'bow')
            if suffix:
                vname += suffix
            vb=render(vanilla,'minecraft:item/'+vname,side,transparent=True).getbbox()
            ab=render(after,ref+'_primera_persona',side,transparent=True).getbbox()
            area=lambda b:(b[2]-b[0])*(b[3]-b[1])
            ratio=area(ab)/area(vb)
            distance=math.hypot((ab[0]+ab[2]-vb[0]-vb[2])/2,(ab[1]+ab[3]-vb[1]-vb[3])/2)
            metrics.append(dict(model=name,side=side,vanilla=vb,after=ab,area_ratio=ratio,center_distance=distance))
            assert .70 <= ratio <= 1.20 and distance <= 40 and ab[3] == 225, metrics[-1]
            for col, files, model in [(0, vanilla, 'minecraft:item/'+vname), (1, before, ref),
                                      (2, after, ref+'_primera_persona')]:
                # Mareas usa el sufijo _icono_fp para la textura, no cambia el nombre del modelo.
                im = render(files, model, side)
                sheet.alpha_composite(im, (col*400, y))
            draw.text((8, y+229), name+' / '+side, fill='white')
            if suffix in ('','_pulling_2'):
                # Resumen compacto: derecha en reposo, izquierda cargada; todos
                # los otros estados/manos quedan en la lamina completa.
                if (suffix=='' and side=='righthand') or (suffix=='_pulling_2' and side=='lefthand'):
                    summary.alpha_composite(sheet.crop((0,y,1200,y+250)),(0,40+summary_rows*250))
                    summary_rows+=1
        path = OUT / f'previews/{family}_primera_persona.png'
        sheet.convert('RGB').save(path)
        summary.convert('RGB').save(OUT/f'previews/{family}_revision.png')
        print(path)
    (OUT/'previews/primera_persona_medidas.json').write_text(json.dumps(metrics,indent=2),encoding='utf8')
    print('Mediciones:',len(metrics),'area',min(m['area_ratio'] for m in metrics),max(m['area_ratio'] for m in metrics),
          'centro max',max(m['center_distance'] for m in metrics))


if __name__ == '__main__':
    main()
