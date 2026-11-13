"""Oceano Astral (tanda B): set de agua, armas y herramientas, menas y cofres. Arte propio y provisorio.

Equipo tier 3 (como Carnivora). Recetas en la Forja y en la mesa (RECIPES comun).
- Armadura de agua: cada pieza da mas velocidad nadando, minar mas rapido bajo el agua y mas aire.
  Casco: vision nocturna bajo el agua. Set completo: respiracion infinita (los dos los aplica AstralOceano).
- Arco de agua: clic derecho dispara un chorro (tridente de agua) sin gastar flechas (AstralOceano).
- Espada y hacha de agua (clones tier 3), pico de agua (mina rapido bajo el agua).
- Menas: bloque de nota con estado propio (banjo 22/23), solo en el oceano, con taladro de amatista (tier 3) o mejor.
- Cofres al azar: tabla astral:chests/oceano (los pone el generador del oceano).
"""
from copy import deepcopy
import json

from escala import VIDA_PIEZA, defensa_pieza

COLOR = '#4fd8e8'
TIER = 3
# Menas: (id del material, nota del bloque de nota en banjo, nombre)
ORES = {'perla_abisal': (22, 'Perla Abisal'), 'coral_astral': (23, 'Coral Astral')}
DRILL_TIER = 3           # taladro de amatista o mejor
CLONES = {'agua_espada': ('espada_3', 'Espada de las Mareas', 'sword'),
          'agua_hacha': ('hacha_3', 'Hacha de las Mareas', 'axe'),
          'agua_arco': ('arco_3', 'Arco de Agua', 'bow')}
PIECES = {'helmet': 'Casco', 'chestplate': 'Pechera', 'leggings': 'Grebas', 'boots': 'Botas'}
SLOT = {'helmet': 'head', 'chestplate': 'chest', 'leggings': 'legs', 'boots': 'feet'}
# Por pieza (4 piezas = el maximo vanilla en nado y mineria bajo el agua).
NADO = 0.25              # minecraft:water_movement_efficiency
MINERIA = 0.2            # minecraft:submerged_mining_speed (base 0.2; 4 piezas = 1.0, como Afinidad acuatica)
AIRE = 1.0               # minecraft:oxygen_bonus


def recipe_cost(iid):
    big = iid.endswith(('chestplate', 'leggings'))
    return [('c', 'perla_abisal', 10 if big else 6), ('c', 'coral_astral', 4 if big else 2), ('c', 'netherita_reforzada', 1)]


def register(items, fichas, recipes, add_item, txt, armor_attrs):
    for iid, (name, _) in ((k, v[::-1]) for k, v in ORES.items()):
        add_item(iid, 'minecraft:prismarine_crystals' if iid == 'perla_abisal' else 'minecraft:prismarine_shard', name, COLOR,
                 [txt('Material del Oceano Astral. Se mina con taladro de amatista o mejor.')],
                 {'type': 'material', 'tier': TIER}, model='astral:' + iid, kind='material')
    for iid, (source, name, _) in CLONES.items():
        it = deepcopy(items[source]); c = it['components']
        c['minecraft:custom_data'] = c['minecraft:custom_data'].replace('id:"' + source + '"', 'id:"' + iid + '"')
        c['minecraft:item_name'] = txt(name, COLOR)
        c['minecraft:item_model'] = 'astral:' + iid
        if iid == 'agua_arco':
            c['minecraft:lore'] = c.get('minecraft:lore', []) + [txt('Clic derecho: chorro de agua. No gasta flechas.', 'aqua')]
        it['name'] = name
        if source in fichas:
            from ficha import render
            f = deepcopy(fichas[source]); f.update(id=iid, name=name, components=deepcopy(c))
            c.update(render(f))
            fichas[iid] = f
        items[iid] = it
    for piece, label in PIECES.items():
        iid = 'agua_' + piece
        mods = armor_attrs(iid, piece, 'diamond', {}, vida=VIDA_PIEZA[TIER])
        for attr, amount, suffix in (('water_movement_efficiency', NADO, 'nado'), ('submerged_mining_speed', MINERIA, 'mineria'),
                                     ('oxygen_bonus', AIRE, 'aire')):
            mods.append({'type': f'minecraft:{attr}', 'id': f'astral:{iid}.{suffix}', 'amount': amount, 'operation': 'add_value', 'slot': SLOT[piece]})
        lore = [txt('Armadura de Agua III'), txt('Nadas y minas mas rapido bajo el agua.', 'aqua')]
        if piece == 'helmet':
            lore.append(txt('Vision nocturna bajo el agua.', 'aqua'))
        lore.append(txt('Set completo: respiras sin limite.', 'gold'))
        add_item(iid, 'minecraft:diamond_' + piece, label + ' de Agua', COLOR, lore,
                 {'type': 'armor', 'set': 'agua', 'tier': TIER, 'piece': piece, 'def': defensa_pieza(TIER, piece)},
                 extra={'minecraft:attribute_modifiers': mods,
                        'minecraft:equippable': {'slot': SLOT[piece], **({} if piece == 'helmet' else {'asset_id': 'astral:agua'})}},
                 model='astral:' + iid, kind='armor')
    add_item('agua_pico', 'minecraft:diamond_pickaxe', 'Pico de las Mareas', COLOR,
             [txt('Equipo de Agua III'), txt('Mina rapido bajo el agua.', 'aqua')], {'type': 'utility', 'tier': TIER},
             extra={'minecraft:enchantments': {'minecraft:efficiency': 4, 'minecraft:unbreaking': 3},
                    'minecraft:attribute_modifiers': [{'type': 'minecraft:submerged_mining_speed', 'id': 'astral:agua_pico.mineria',
                                                       'amount': 0.8, 'operation': 'add_value', 'slot': 'mainhand'}]},
             model='astral:agua_pico', kind='item')
    for iid in [*CLONES, *('agua_' + p for p in PIECES), 'agua_pico']:
        recipes.append((iid, 1, recipe_cost(iid), 'Agua'))


# ------------------------------------------------------------------------------------- datapack
def ore_state(note):
    return {'instrument': 'banjo', 'note': str(note), 'powered': 'false'}


def extend_note_block_table(files):
    """Agrega las menas del oceano a la tabla del bloque de nota (la crea tanda4b_world con la del Asura)."""
    path = 'data/minecraft/loot_table/blocks/note_block.json'
    table = json.loads(files[path])
    # Sin location_check (en 26.1 la condicion de dimension no se cumple en tablas de bloques): fuera del
    # oceano las menas falsas no sueltan nada por AstralOceano (rotura a mano) y drill_guard (taladro en area).
    for iid, (note, _) in ORES.items():
        state = {'condition': 'minecraft:block_state_property', 'block': 'minecraft:note_block',
                 'properties': {'instrument': 'banjo', 'note': str(note)}}
        table['pools'].insert(0, {'rolls': 1, 'conditions': [state], 'entries': [
            {'type': 'minecraft:loot_table', 'value': 'astral:item/' + iid,
             'functions': [{'function': 'minecraft:set_count', 'count': {'min': 1, 'max': 2}},
                           {'function': 'minecraft:apply_bonus', 'enchantment': 'minecraft:fortune', 'formula': 'minecraft:ore_drops'}]}]})
    # El bloque de nota comun solo cae si no es una mena (Asura u oceano).
    for pool in table['pools']:
        for cond in pool.get('conditions', []):
            if cond.get('condition') == 'minecraft:inverted' and cond['term'].get('block') == 'minecraft:note_block':
                pool['conditions'] = [c for c in pool['conditions'] if c is not cond] + [
                    {'condition': 'minecraft:inverted', 'term': {'condition': 'minecraft:block_state_property', 'block': 'minecraft:note_block',
                                                                 'properties': {'instrument': 'banjo', 'note': str(n)}}}
                    for n in (*(note for note, _ in ORES.values()), 24)]
                break
    files[path] = json.dumps(table, ensure_ascii=False, indent=1)


def chest_table():
    def it(iid, w, lo=1, hi=1):
        return {'type': 'minecraft:loot_table', 'value': 'astral:item/' + iid, 'weight': w,
                'functions': [{'function': 'minecraft:set_count', 'count': {'min': lo, 'max': hi}}]}

    def van(name, w, lo=1, hi=1):
        return {'type': 'minecraft:item', 'name': 'minecraft:' + name, 'weight': w,
                'functions': [{'function': 'minecraft:set_count', 'count': {'min': lo, 'max': hi}}]}
    return {'type': 'minecraft:chest', 'pools': [
        {'rolls': {'min': 2, 'max': 4}, 'entries': [it('perla_abisal', 30, 1, 3), it('coral_astral', 22, 1, 2),
                                                    van('prismarine_shard', 25, 2, 6), van('prismarine_crystals', 18, 2, 5),
                                                    van('gold_ingot', 15, 1, 4), van('nautilus_shell', 8), van('diamond', 5, 1, 2)]},
        {'rolls': 1, 'entries': [{'type': 'minecraft:empty', 'weight': 60}, it('esencia_elite', 25, 1, 2),
                                 van('heart_of_the_sea', 4), it('netherita_reforzada', 11)]},
        {'rolls': 1, 'entries': [{'type': 'minecraft:empty', 'weight': 70},
                                 {'type': 'minecraft:item', 'name': 'minecraft:potion', 'weight': 30,
                                  'functions': [{'function': 'minecraft:set_potion', 'id': 'minecraft:long_water_breathing'}]}]},
    ]}


def drill_guard():
    """tool/mine: las menas del oceano solo con taladro de tier 3+ (las otras herramientas no pasan)."""
    lines = []
    for note, _ in ORES.values():
        # Fuera del oceano una "mena" armada a mano se borra sin soltar nada.
        lines.append(f'execute unless dimension minecraft:oceano if block ~ ~ ~ minecraft:note_block[instrument=banjo,note={note}] '
                     'run return run setblock ~ ~ ~ minecraft:air')
        ok = ' '.join(f'unless items entity @s weapon.mainhand *[minecraft:custom_data~{{astral:{{tool:"drill",tier:{t}}}}}]'
                      for t in range(DRILL_TIER, 10))
        lines.append(f'execute if block ~ ~ ~ minecraft:note_block[instrument=banjo,note={note}] {ok} run return 0')
    return lines


def generate(files):
    extend_note_block_table(files)
    files['data/astral/loot_table/chests/oceano.json'] = json.dumps(chest_table(), ensure_ascii=False, indent=1)


# ------------------------------------------------------------------------------------- arte propio
def own_textures():
    """Texturas procedurales originales (provisorias hasta que el dueno pase las suyas)."""
    from PIL import Image, ImageDraw
    import io
    import random
    files = {}

    def png(name, im):
        s = io.BytesIO(); im.save(s, 'PNG'); files['assets/astral/textures/' + name + '.png'] = s.getvalue()

    def put(name, obj):
        files['assets/' + name + '.json'] = json.dumps(obj).encode()
    for iid, colors in (('perla_abisal', ('#2a5d7a', '#bff6ff', '#e8fbff')), ('coral_astral', ('#7a2a5d', '#ff8fd0', '#ffe0f4'))):
        rng = random.Random(len(iid) * 31)
        im = Image.new('RGB', (16, 16)); px = im.load()
        for y in range(16):
            for x in range(16):
                c = rng.randrange(70, 110); px[x, y] = (c - 20, c + 5, c + 25)
        d = ImageDraw.Draw(im)
        for x, y in [(4, 4), (11, 5), (7, 11), (12, 12)]:
            d.ellipse((x - 2, y - 2, x + 1, y + 1), fill=colors[1], outline=colors[0]); d.point((x - 1, y - 1), fill=colors[2])
        png('block/' + iid + '_ore', im)
        put('astral/models/block/' + iid + '_ore', {'parent': 'minecraft:block/cube_all', 'textures': {'all': 'astral:block/' + iid + '_ore'}})
        it = Image.new('RGBA', (16, 16)); d = ImageDraw.Draw(it)
        if iid == 'perla_abisal':
            d.ellipse((3, 3, 12, 12), fill=colors[1], outline=colors[0]); d.ellipse((5, 5, 8, 8), fill=colors[2])
        else:
            d.line((8, 14, 8, 6), fill=colors[0], width=2); d.line((8, 9, 4, 4), fill=colors[1], width=2); d.line((8, 8, 12, 3), fill=colors[1], width=2)
        png('item/' + iid, it)
        put('astral/models/item/' + iid, {'parent': 'minecraft:item/generated', 'textures': {'layer0': 'astral:item/' + iid}})
        put('astral/items/' + iid, {'model': {'type': 'minecraft:model', 'model': 'astral:item/' + iid}})
    fall = {'agua_espada': 'diamond_sword', 'agua_hacha': 'diamond_axe', 'agua_arco': 'bow', 'agua_pico': 'diamond_pickaxe',
            **{'agua_' + p: 'diamond_' + p for p in PIECES}}
    for iid, model in fall.items():
        put('astral/items/' + iid, {'model': {'type': 'minecraft:model', 'model': 'minecraft:item/' + model}})
    put('astral/equipment/agua', {'layers': {k: [{'texture': 'minecraft:diamond'}] for k in ('humanoid', 'humanoid_leggings')}})
    return files


def note_block_variants():
    """Partes del bloque de nota para las menas del oceano (se suman al estado del Asura en tanda4b_world)."""
    return [{'when': {'instrument': 'banjo', 'note': str(note)}, 'apply': {'model': 'astral:block/' + iid + '_ore'}}
            for iid, (note, _) in ORES.items()]
