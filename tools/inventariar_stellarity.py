"""Lee los originales locales; exporta hechos del recetario, nunca arte ni funciones ajenas."""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def walk(obj):
    if isinstance(obj, dict):
        yield obj
        for v in obj.values():
            yield from walk(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from walk(v)


def inventory(datapack, resource):
    with zipfile.ZipFile(datapack) as z:
        files = {n: z.read(n) for n in z.namelist() if not n.endswith('/')}
    with zipfile.ZipFile(resource) as z:
        lang = json.loads(z.read('assets/stellarity/lang/es_es.json'))
        english = json.loads(z.read('assets/stellarity/lang/en_us.json'))

    def translate(value):
        if isinstance(value, str):
            return value
        if isinstance(value, list):
            return ''.join(map(translate, value))
        if not isinstance(value, dict):
            return str(value)
        k = value.get('translate', '')
        return value.get('text', lang.get(k, english.get(k, k))) + ''.join(map(translate, value.get('extra', [])))

    items, by_loot = {}, {}
    for path, raw in files.items():
        if '/loot_table/' not in path or not path.endswith('.json'):
            continue
        obj = json.loads(raw)
        for entry in walk(obj):
            if entry.get('type') not in ('minecraft:item', 'item'):
                continue
            comps, lore, stats = {}, [], []
            for f in list(obj.get('functions', [])) + entry.get('functions', []):
                if f.get('function') == 'minecraft:set_components':
                    comps.update({k if ':' in k else 'minecraft:' + k: v for k, v in f['components'].items()})
                if f.get('function') == 'minecraft:set_lore':
                    lore += [translate(x) for x in f['lore']]
                if f.get('function') == 'minecraft:set_attributes':
                    stats += f['modifiers']
            model = comps.get('minecraft:item_model')
            custom_id = comps.get('minecraft:custom_data', {}).get('stellarity:item')
            lore += [translate(x) for x in comps.get('minecraft:lore', [])]
            canonical = path.startswith('data/stellarity/loot_table/item/')
            if not canonical and not custom_id and (not model or not model.startswith('stellarity:')):
                continue
            key = custom_id or (model.split(':')[1] if model else Path(path).stem)
            loot = path.removeprefix('data/stellarity/loot_table/').removesuffix('.json')
            row = dict(id=key, material=entry['name'] if ':' in entry['name'] else 'minecraft:' + entry['name'], model=model,
                       name=translate(comps.get('minecraft:item_name', comps.get('minecraft:custom_name', key.replace('_', ' ').title()))),
                       lore=[s for s in lore if s and s != 'Stellarity'],
                       food=comps.get('minecraft:food'), consumable=comps.get('minecraft:consumable'),
                       potion=comps.get('minecraft:potion_contents'), cooldown=comps.get('minecraft:use_cooldown'), stats=stats, source=path)
            by_loot['stellarity:' + loot] = key
            # Las tablas item son la definicion canonica, no los cofres.
            if key not in items or loot.startswith('item/'):
                items[key] = row

    recipes = []
    for path, raw in files.items():
        if '/recipe/' not in path or not path.endswith('.json') or '/events/' in path:
            continue
        obj = json.loads(raw)
        kind = obj['type'].split(':')[1]
        grid = [None] * 9
        if 'pattern' in obj:
            for y, line in enumerate(obj['pattern']):
                for x, c in enumerate(line):
                    if c != ' ':
                        grid[y * 3 + x] = obj['key'][c]
        else:
            ings = obj.get('ingredients', [obj.get('ingredient')])
            grid[:len(ings)] = ings
        recipes.append(dict(id=path.split('/recipe/')[0].split('/')[1] + '_' + path.split('/recipe/')[1][:-5].replace('/', '_'),
                            station={'crafting_shaped': 'Mesa de crafteo', 'crafting_shapeless': 'Mesa sin forma',
                                     'smelting': 'Horno', 'blasting': 'Alto horno', 'campfire_cooking': 'Fogata'}[kind],
                            grid=[dict(item=x, count=1) if x else None for x in grid],
                            result=obj['result'], source=path,
                            seconds=obj.get('cookingtime', 0) / 20, experience=obj.get('experience', 0)))

    prefix = 'data/stellarity/function/mechanic/'
    for path, raw in files.items():
        if not path.startswith(prefix + 'altar_of_the_accursed/crafting/items/') or '/special/' in path or not path.endswith('.mcfunction'):
            continue
        text = raw.decode().replace('\\\n', ' ')
        for line in text.splitlines():
            if 'run function' not in line:
                continue
            ings = re.findall(r'tag=stellarity\.altar_of_the_accursed\.(minecraft|stellarity)\.([a-z_]+),scores=\{stellarity\.altar_of_the_accursed\.count=(\d+)\}', line)
            if not ings:
                raise ValueError('Receta de altar sin ingredientes: ' + path)
            loot = re.search(r'loot:"([^"]+)"', line)
            if loot:
                output, count = by_loot[loot[1]], 1
            elif line.rstrip().endswith('/special/endonomicon'):
                output, count = by_loot['stellarity:item/endonomicon/book'], 1
            elif line.rstrip().endswith('/special/smithing_template'):
                output, count = 'enderite_smithing_template', 2
            else:
                raise ValueError('Salida de altar desconocida: ' + line)
            recipes.append(dict(id='altar_' + output, station='Altar Maldito',
                                grid=[dict(item=ns + ':' + key, count=int(n)) for ns, key, n in ings],
                                result=dict(item=output, count=count), source=path))

    path = prefix + 'cauldron_crafting/crafting/checks.mcfunction'
    for line in files[path].decode().splitlines():
        if 'ingredients:[' not in line:
            continue
        ingredients = json.loads('[' + re.search(r'ingredients:\[(.*?)\]', line)[1] + ']')
        count = int(re.search(r'amount:(\d+)', line)[1])
        loot = re.search(r'loot:"([^"]+)"', line)
        output = dict(item=by_loot[loot[1]], count=1) if loot else dict(id=re.search(r'item:"([^"]+)"', line)[1], count=1)
        ings = []
        for ing in ingredients:
            ing = re.sub(r'_\d+$', '', ing)
            ings.append(dict(item=ing if ':' in ing else 'stellarity:' + ing, count=1))
        key = output.get('item', output.get('id')).replace(':', '_')
        recipes.append(dict(id='caldero_' + key + '_' + str(len(recipes)), station='Caldero de dragon', grid=ings,
                            result=output, breath=int(re.search(r'breath:(\d+)', line)[1]), source=path,
                            warning='La fuente exige 6 objetos pero enumera 5; no se confirma una combinacion funcional.' if count != len(ingredients) else ''))

    for color in ['white', 'light_gray', 'gray', 'black', 'brown', 'red', 'orange', 'yellow', 'lime', 'green', 'cyan', 'light_blue', 'blue', 'purple', 'magenta', 'pink', 'water']:
        recipes.append(dict(id='elytra_' + color, station='Altar Maldito',
                            grid=[dict(item='minecraft:elytra', count=1), dict(item='minecraft:' + ('water_bucket' if color == 'water' else color + '_dye'), count=1)],
                            result=dict(id='minecraft:elytra', count=1), source=prefix + 'altar_of_the_accursed/crafting/dye_elytra/checks.mcfunction',
                            note='Quita el color.' if color == 'water' else 'Aplica el color ' + color + '. Conserva el ala.'))
    world = {kind: [n.split('/worldgen/' + kind + '/')[1][:-5] for n in files if n.startswith('data/stellarity/worldgen/' + kind + '/') and n.endswith('.json')]
             for kind in ['biome', 'structure']}
    evidence = {n: raw.decode() for n, raw in files.items() if n.startswith('data/stellarity/') and
                (('/function/entity/' in n and any(x in n for x in ['/death', '/loot', '/summon', '/spawn'])) or
                 '/function/mechanic/altar_of_the_sacred/' in n or '/function/mechanic/fishing/' in n)}
    return dict(version='5.4.2', sha256=hashlib.sha256(Path(datapack).read_bytes()).hexdigest(), items=items,
                recipes=recipes, world=world), evidence


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--datapack', type=Path, default=ROOT / '.local/dp-server/Stellarity-5.4.2.zip')
    ap.add_argument('--resource', type=Path, default=ROOT / 'datapack-src/pack-source/terceros/Stellarity-6.0.1-RP.zip')
    args = ap.parse_args()
    data, evidence = inventory(args.datapack, args.resource)
    target = ROOT / '.local/coordination/stellarity-inventario.json'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf8')
    target.with_name('stellarity-evidencias.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding='utf8')
    print(len(data['items']), 'objetos;', len(data['recipes']), 'recetas;', data['sha256'])
