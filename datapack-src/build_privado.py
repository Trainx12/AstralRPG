"""Circuito privado: --prepare; convertir con BetterModel; --assets <build/assets>.

El pack publico no se modifica. Sin ASTRAL_PRIVADO disponible, termina sin cambios.
"""
import argparse
import base64
from copy import deepcopy
import hashlib
import io
import json
from pathlib import Path
import uuid
import zipfile

from terceros import ROOT, PETS, privado, sources


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding='utf-8')


def adapted(data, mid):
    """Copias portables: texturas embebidas, sin rutas locales y nombres unicos."""
    data = deepcopy(data)
    data['name'] = mid
    if mid.startswith('astral_pet_'):
        # ModelEngine usa estas cajas como metadatos, no como geometria visible.
        # Quitar solo sus descendientes: los planos de ojos/hojas son arte valido.
        groups = {g['uuid']: g for g in data.get('groups', [])}
        removed = set()
        def prune(node, inherited=False):
            if isinstance(node, str):
                if inherited:
                    removed.add(node)
                return not inherited
            group = groups.get(node['uuid'], node)
            hidden = inherited or group.get('visibility') is False or group.get('name') in ('hitbox', 'tag_status', 'tag_nickname')
            children = [child for child in node.get('children', []) if prune(child, hidden)]
            node['children'] = children
            if hidden:
                removed.add(node['uuid'])
            return not hidden
        data['outliner'] = [node for node in data['outliner'] if prune(node)]
        # Contornos de casco invertidos: BetterModel no conserva su culling de
        # ModelEngine y los exporta como caras sueltas. Mantener el cuerpo normal.
        removed.update(e['uuid'] for e in data['elements']
                       if e.get('name') == 'cube_outline' and any(a > b for a,b in zip(e['from'],e['to'])))
        data['elements'] = [e for e in data['elements'] if e['uuid'] not in removed]
        def clean(node):
            if isinstance(node, dict):
                node['children'] = [c for c in node.get('children', []) if (c if isinstance(c,str) else c['uuid']) not in removed]
                for child in node['children']: clean(child)
        for node in data['outliner']: clean(node)
        if 'groups' in data:
            data['groups'] = [g for g in data['groups'] if g['uuid'] not in removed]
        for animation in data.get('animations', []):
            animation['animators'] = {k: v for k, v in animation.get('animators', {}).items() if k not in removed}
    for i, texture in enumerate(data['textures']):
        if not texture.get('source', '').startswith('data:image/png;base64,'):
            raise ValueError('Textura sin PNG embebido: ' + mid)
        texture['name'] = mid + ('_e' if texture.get('name', '').endswith('_e.png') else '_' + str(i)) + '.png'
        for key in ('path', 'relative_path', 'folder'):
            texture.pop(key, None)
    if mid == 'astral_goblin':
        idle = deepcopy(next(a for a in data['animations'] if a['name'] == 'pose'))
        idle.update(name='idle', loop='loop', uuid=str(uuid.uuid5(uuid.NAMESPACE_URL, mid + '/idle')))
        data['animations'].append(idle)
    if mid in ('astral_goblin', 'astral_abejorro', 'astral_vendedor'):
        from mobs.tamanos import bounds_data
        box = bounds_data(data)
        lo, hi = [v[0] * 16 for v in box], [v[1] * 16 for v in box]
        if mid == 'astral_vendedor':
            lo, hi = [-4.8, 0, -4.8], [4.8, 28.8, 4.8]
        cube_id = str(uuid.uuid5(uuid.NAMESPACE_URL, mid + '/hitbox/cube'))
        group_id = str(uuid.uuid5(uuid.NAMESPACE_URL, mid + '/hitbox/group'))
        data['elements'].append({'name': 'astral_hitbox', 'type': 'cube', 'uuid': cube_id,
                                 'from': lo, 'to': hi, 'origin': [0, 0, 0],
                                 'faces': {side: {'uv': [0, 0, 0, 0], 'texture': None}
                                           for side in ('north', 'south', 'east', 'west', 'up', 'down')}})
        group = dict(name='b_astral_hitbox', uuid=group_id, origin=[0, 0, 0], rotation=[0, 0, 0], children=[cube_id])
        if 'groups' in data:
            data['groups'].append(group)
        data['outliner'].append(group)
    if mid == 'astral_vendedor':
        # Hueso 'mtag_' de BetterModel 3.6.0: dibuja el nombre del mob encima del modelo.
        tag = dict(name='mtag_nombre', uuid=str(uuid.uuid5(uuid.NAMESPACE_URL, mid + '/mtag/group')),
                   origin=[0, 33, 0], rotation=[0, 0, 0], children=[])
        if 'groups' in data:
            data['groups'].append(tag)
        data['outliner'].append(tag)
    # El resto conserva las animaciones originales, incluida idle del Grub.
    return data


def item_assets(data):
    """Blockbench java_block -> item model moderno; conserva UV, display y rotaciones."""
    mid = 'espada_heroe_errante'
    result, textures = {}, {}
    for i, texture in enumerate(data['textures']):
        path = f'privado:item/{mid}_{i}'
        textures[str(i)] = path
        result[f'assets/privado/textures/item/{mid}_{i}.png'] = base64.b64decode(texture['source'].split(',', 1)[1])
    # Blockbench guarda las UV en pixeles de la textura (64x64); Minecraft las lee siempre en 0..16.
    res = data.get('resolution', {})
    su, sv = 16 / res.get('width', 16), 16 / res.get('height', 16)
    elements = []
    for cube in data['elements']:
        if cube.get('type', 'cube') != 'cube':
            continue
        e = {k: deepcopy(cube[k]) for k in ('from', 'to', 'shade') if k in cube}
        if any(cube.get('rotation', [])):
            axes = [(axis, angle) for axis, angle in zip('xyz', cube['rotation']) if angle]
            if len(axes) != 1 or axes[0][1] not in (-45, -22.5, 22.5, 45):
                raise ValueError('Rotacion de item no compatible con Java')
            e['rotation'] = dict(origin=cube.get('origin', [8, 8, 8]), axis=axes[0][0], angle=axes[0][1], rescale=cube.get('rescale', False))
        e['faces'] = {side: {**{k: v for k, v in face.items() if k in ('rotation', 'tintindex')},
                             **({'uv': [round(u * s, 4) for u, s in zip(face['uv'], (su, sv, su, sv))]} if 'uv' in face else {}),
                             'texture': '#' + str(face['texture'])}
                      for side, face in cube['faces'].items() if face.get('texture') is not None}
        elements.append(e)
    model = dict(parent='minecraft:item/handheld', textures=textures, elements=elements,
                 display=data.get('display', {}), gui_light=data.get('front_gui_light', False) and 'front' or 'side')
    lo = [min(e['from'][i] for e in elements) for i in range(3)]
    hi = [max(e['to'][i] for e in elements) for i in range(3)]
    fit = min(1, 16 / max(b - a for a, b in zip(lo, hi)))
    model['display'].setdefault('gui', dict(rotation=[0, 0, 0], scale=[fit] * 3,
                                         translation=[(8 - (a + b) / 2) * fit for a, b in zip(lo, hi)]))
    result[f'assets/privado/models/item/{mid}.json'] = json.dumps(model).encode()
    result[f'assets/astral/items/{mid}.json'] = json.dumps({'model': {'type': 'minecraft:model', 'model': f'privado:item/{mid}'}}).encode()
    return result


def prepare():
    base = privado() / 'build'
    models = {}
    for mid, source in sources().items():
        data = adapted(json.loads(source.read_text(encoding='utf-8')), mid)
        if mid == 'espada_heroe_errante':
            for name, content in item_assets(data).items():
                path = base / 'item-pack' / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(content)
        else:
            write_json(base / 'models' / (mid + '.bbmodel'), data)
            models[mid] = data
    private_configs(models)
    from tanda4b_privado import prepare as prepare_tanda4b
    prepare_tanda4b(base)
    preview(models)
    print('Preparados 20 modelos y espada en build privado.')


def private_configs(models):
    import yaml
    # Copias de configuracion propias, ajustadas a los modelos privados.
    from mobs.tamanos import bounds
    from mobs import tamanos
    original_root = tamanos.ROOT
    try:
        tamanos.ROOT = privado()
        bounds.cache_clear()
        skill_path = ROOT / 'build/mythicmobs/skills/astral.yml'
        skills = yaml.safe_load(skill_path.read_text(encoding='utf-8'))
        for mid, entity, factors in [('astral_goblin', 'ZOMBIE', [('', 1)]), ('astral_abejorro', 'VEX', [('', 1), ('_elite', 1.35)])]:
            for suffix, factor in factors:
                # Atributos vanilla como en tanda3a: alto del modelo y step_height.
                # El ancho vanilla depende de la especie; las medidas se registran para revision.
                skills[f'AST_MODEL_{mid}{suffix}']['Skills'] = [
                    'addtag{tag=astral.seen} @self', f'model{{m={mid};s={factor}}} @self',
                    *tamanos.skills(mid, factor, entity)]
        pet_skills = yaml.safe_load((ROOT / 'build/mythicmobs/skills/mascotas.yml').read_text(encoding='utf-8'))
        for pid, *_ in PETS:
            for skill in (f'PET_MODELO_{pid}', f'PET_{pid}_EVOLUCION'):
                pet_skills[skill]['Skills'] = [s.replace('m=astral_pet_lobo', 'm=astral_pet_' + pid) for s in pet_skills[skill]['Skills']]
        mobs = yaml.safe_load((ROOT / 'build/mythicmobs/mobs/astral.yml').read_text(encoding='utf-8'))
        for mid in ('astral_abejorro', 'astral_abejorro_elite'):
            mobs[mid]['Skills'] = [s for s in mobs[mid]['Skills'] if not s.startswith('state{s=attack}')]
        for mid in ('venta', 'mina_venta', 'bosque_venta'):  # la Tienda conserva su aldeano
            mob = mobs['astral_npc_' + mid]
            # VILLAGER adulto: 0,6 x 1,95, aproximadamente jugador. No se escala la entidad.
            mob['Skills'] += ['model{m=astral_vendedor} @self ~onSpawn', 'model{m=astral_vendedor} @self ~onLoad']
        for relative, data in [('skills/astral.yml', skills), ('skills/mascotas.yml', pet_skills), ('mobs/astral.yml', mobs)]:
            dest = privado() / 'build/mythicmobs' / relative
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=150), encoding='utf-8')
        metrics = {mid: {'bounds_blocks': bounds(mid), 'animations': [a['name'] for a in data.get('animations', [])]}
                   for mid, data in models.items()}
        write_json(privado() / 'build/medidas.json', metrics)
    finally:
        tamanos.ROOT = original_root
        bounds.cache_clear()


def preview(models, name='tanda4a', include_sword=True):
    """Render CPU local con texturas originales, exclusivamente en el repo privado."""
    from PIL import Image, ImageDraw, ImageOps
    from mobs.build_models import preview3d
    from types import SimpleNamespace
    tiles = []
    all_models = dict(models)
    if include_sword:
        all_models['espada_heroe_errante'] = adapted(json.loads(sources()['espada_heroe_errante'].read_text(encoding='utf-8')), 'espada_heroe_errante')
    for mid, data in all_models.items():
        data = deepcopy(data)
        images = [Image.open(io.BytesIO(base64.b64decode(t['source'].split(',', 1)[1]))).convert('RGBA') for t in data['textures']]
        atlas = Image.new('RGBA', (sum(im.width for im in images) + 1, max(im.height for im in images)))
        offsets, x = [], 0
        for im in images:
            offsets.append(x); atlas.paste(im, (x, 0)); x += im.width
        bones, parents, hidden = {}, {}, set()
        idle = next((a for a in data.get('animations', []) if a['name'] == 'idle'), {})
        for key, animator in idle.get('animators', {}).items():
            scales = sorted((k for k in animator.get('keyframes', []) if k['channel'] == 'scale'), key=lambda k: k['time'])
            if scales:
                try:
                    if all(float(scales[0]['data_points'][0].get(axis, 1)) == 0 for axis in 'xyz'):
                        hidden.add(key)
                except ValueError:
                    pass
        groups = {g['uuid']: g for g in data.get('groups', [])}
        def visit(node, parent=None):
            if isinstance(node, str):
                parents[node] = parent
                return
            g = groups.get(node['uuid'], node)
            key = node['uuid']
            if key in hidden or not g.get('export', True):
                return
            bones[key] = dict(parent=parent, origin=g.get('origin', [0, 0, 0]), rotation=g.get('rotation', [0, 0, 0]))
            for child in node.get('children', []):
                visit(child, key)
        for node in data.get('outliner', []):
            visit(node)
        elements = []
        for e in data['elements']:
            if (e.get('type', 'cube') != 'cube' or e.get('visibility') is False or not e.get('export', True)
                    or e.get('name') == 'astral_hitbox' or e['uuid'] not in parents
                    or not any(f.get('texture') is not None for f in e.get('faces', {}).values())):
                continue
            e.setdefault('origin', [0, 0, 0])
            for face in ('north', 'south', 'east', 'west', 'up', 'down'):
                f = e.setdefault('faces', {}).setdefault(face, {'uv': [0, 0, 0, 0]})
                if f.get('texture') is None:
                    f['uv'] = [atlas.width - 1, 0, atlas.width, 1]
                    continue
                ti = int(f.get('texture') or 0)
                u0, v0, u1, v1 = f['uv']
                rw = data['textures'][ti].get('uv_width', data.get('resolution', {}).get('width', images[ti].width))
                rh = data['textures'][ti].get('uv_height', data.get('resolution', {}).get('height', images[ti].height))
                us = sorted(min(images[ti].width, max(0, u * images[ti].width / rw)) for u in (u0, u1))
                vs = sorted(min(images[ti].height, max(0, v * images[ti].height / rh)) for v in (v0, v1))
                f['uv'] = [int(us[0]) + offsets[ti], int(vs[0]), max(1, int(us[1])) + offsets[ti], max(1, int(vs[1]))]
            elements.append(e)
        data['elements'] = elements
        model = SimpleNamespace(export=lambda: (data, atlas), bones=bones,
                                cubes=[dict(bone=parents.get(e['uuid'])) for e in elements])
        im = preview3d(model, atlas, scale=3, background=(0, 0, 0, 0))
        if mid.startswith('astral_pet_'):
            pid=mid.removeprefix('astral_pet_')
            icon=ImageOps.contain(im.crop(im.getbbox()),(16,16),Image.Resampling.LANCZOS)
            canvas=Image.new('RGBA',(18,18))
            canvas.alpha_composite(icon,((18-icon.width)//2,(18-icon.height)//2))
            import io as _io
            blob=_io.BytesIO();canvas.save(blob,format='PNG')
            name='catalogo_'+pid
            entries={f'assets/astral/textures/item/mascotas/{name}.png':blob.getvalue(),
                f'assets/astral/models/mascotas/{name}.json':json.dumps({'parent':'minecraft:item/generated',
                    'textures':{'layer0':f'astral:item/mascotas/{name}'},'gui_light':'front'}).encode(),
                f'assets/astral/items/mascotas/{name}.json':json.dumps({'model':{
                    'type':'minecraft:model','model':f'astral:mascotas/{name}'}}).encode()}
            for relative,content in entries.items():
                dest=privado()/'build/item-pack'/relative
                dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(content)
        im = ImageOps.contain(im.crop(im.getbbox()), (225, 190), Image.Resampling.NEAREST)
        tile = Image.new('RGBA', (270, 235), '#18232b')
        tile.alpha_composite(im, ((270 - im.width) // 2, 20))
        ImageDraw.Draw(tile).text((6, 212), mid.removeprefix('astral_'), fill='white')
        tiles.append(tile)
    sheet = Image.new('RGBA', (270 * 5, 235 * ((len(tiles) + 4) // 5)), '#101820')
    for i, tile in enumerate(tiles):
        sheet.paste(tile, (i % 5 * 270, i // 5 * 235))
    dest = privado() / ('build/previews/' + name + '.png')
    dest.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(dest)


def finish(assets):
    """El build de BetterModel debe incluir TODOS los modelos publicos y privados."""
    import shutil
    base = privado() / 'build'
    assets = assets.resolve()
    if assets.name != 'assets' or not (assets / 'bettermodel').is_dir():
        raise ValueError('Se requiere la carpeta assets completa de BetterModel')
    # Fallar si BetterModel no produjo cada modelo requerido.
    names = '\n'.join(p.as_posix() for p in assets.rglob('*.json'))
    for mid in set(sources()) | {p.stem for p in (ROOT / 'build/models').glob('*.bbmodel')}:
        if mid.startswith('espada_'):
            continue
        if mid not in names:
            raise ValueError('BetterModel no exporto ' + mid)
    shutil.copytree(assets, base / 'bettermodel/assets', dirs_exist_ok=True)
    with zipfile.ZipFile(ROOT / 'build/AstralRPG-Textures.zip') as public:
        files = {name: public.read(name) for name in public.namelist()}
    for folder in (assets, base / 'item-pack'):
        for path in folder.rglob('*'):
            if path.is_file():
                name = path.relative_to(folder).as_posix()
                files[('assets/' + name) if folder == assets else name] = path.read_bytes()
    target = base / 'AstralRPG-Textures.zip'
    temporary = target.with_suffix('.zip.tmp')
    with zipfile.ZipFile(temporary, 'w', zipfile.ZIP_DEFLATED) as out:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo(name, date_time=(2026, 11, 10, 0, 0, 0))
            out.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED)
    temporary.replace(target)
    digest = hashlib.sha1(target.read_bytes()).hexdigest()
    (base / 'pack.sha1').write_text(digest + '\n')
    print('Pack FINAL privado:', digest, target.stat().st_size, 'bytes')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare', action='store_true')
    parser.add_argument('--assets', type=Path)
    args = parser.parse_args()
    if not (privado() / 'x').is_dir():
        print('Sin repositorio privado: se conservan los contenidos publicos.')
        return
    if args.prepare:
        prepare()
    if args.assets:
        finish(args.assets)


if __name__ == '__main__':
    main()
