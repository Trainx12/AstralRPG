"""Catalogo y balance propios; el arte se superpone solamente en build_privado."""
from copy import deepcopy
import json
from pathlib import Path
from escala import VIDA_PIEZA, defensa_pieza

ROOT = Path(__file__).resolve().parents[1]
PLUSHIES = {'alex': 'Alex', 'creaking': 'Creaking', 'ocelot': 'Ocelote', 'steve': 'Steve',
            'tropical_fish': 'Pez tropical', 'zombie_horse': 'Caballo zombi'}
COINS = {'emerald': 'Esmeralda', 'card': 'Carta', 'circle': 'Circulo', 'square': 'Cuadrado', 'triangle': 'Triangulo'}
CLONES = {'carnivora_espada': ('espada_3', 'Espada Carnivora', 'sword'),
          'carnivora_hacha': ('hacha_3', 'Hacha Carnivora', 'axe'),
          'carnivora_guadana': ('guadana_3', 'Guadana Carnivora', 'scythe'),
          'carnivora_baston': ('baston_3', 'Baston Carnivoro', 'staff'),
          'carnivora_arco': ('arco_3', 'Arco Carnivoro', 'bow'),
          'carnivora_lanza': ('lanza_3', 'Lanza Carnivora', 'spear'),
          'carnivora_martillo': ('hacha_3', 'Martillo Carnivoro', 'hammer'),
          'asura_espada': ('espada_4', 'Espada Asura', 'asura_sword')}
SIMPLE = {
    'colmillo_carnivoro': ('Colmillo Carnivoro', 'paper', 'minecraft:flint'),
    'carnivora_pico': ('Pico Carnivoro', 'diamond_pickaxe', 'minecraft:diamond_pickaxe'),
    'carnivora_pala': ('Pala Carnivora', 'diamond_shovel', 'minecraft:diamond_shovel'),
    'carnivora_azada': ('Azada Carnivora', 'diamond_hoe', 'minecraft:diamond_hoe'),
    'carnivora_cana': ('Cana Carnivora', 'fishing_rod', 'minecraft:fishing_rod'),
    'carnivora_escudo': ('Escudo Carnivoro', 'shield', 'minecraft:shield'),
    'carnivora_alas': ('Alas Carnivoras', 'paper', 'minecraft:elytra'),
    'asura_alas': ('Alas Asura', 'paper', 'minecraft:elytra'),
    **{'asura_moneda_' + k: ('Moneda Asura ' + v, 'paper', 'minecraft:emerald') for k, v in COINS.items()},
    **{'peluche_' + k: ('Peluche ' + v, 'paper', 'minecraft:rabbit_hide') for k, v in PLUSHIES.items()},
}


def register(items, fichas, recipes, add_item, txt, armor_attrs):
    """Reutilizar componentes reales de cada clase, incluidos mana y encantamientos."""
    for iid, (source, name, _) in CLONES.items():
        it = deepcopy(items[source]); c = it['components']
        c['minecraft:custom_data'] = c['minecraft:custom_data'].replace('id:"' + source + '"', 'id:"' + iid + '"')
        c['minecraft:item_name'] = txt(name, '#bff05a' if iid.startswith('carnivora') else 'gold')
        c['minecraft:item_model'] = 'astral:' + iid
        if iid == 'carnivora_hacha':
            c.setdefault('minecraft:enchantments', {}).update({'minecraft:efficiency':3, 'minecraft:unbreaking':2})
        it['name'] = name
        if source in fichas:
            from ficha import render
            f = deepcopy(fichas[source]); f.update(id=iid, name=name, components=deepcopy(c))
            c.update(render(f))
            fichas[iid] = f
        items[iid] = it
    for piece, label in [('helmet', 'Casco'), ('chestplate', 'Pechera'), ('leggings', 'Grebas'), ('boots', 'Botas')]:
        iid = 'carnivora_' + piece
        add_item(iid, 'minecraft:diamond_' + piece, label + ' Carnivora', '#bff05a', [txt('Armadura Carnivora III')],
                 {'type': 'armor', 'set': 'carnivora', 'tier': 3, 'piece': piece, 'def': defensa_pieza(3, piece)},
                 extra={'minecraft:attribute_modifiers': armor_attrs(iid, piece, 'diamond', {}, vida=VIDA_PIEZA[3]),
                        # Sin asset_id en cabeza: usa el modelo Java y su display.head.
                        'minecraft:equippable': {'slot': {'helmet':'head','chestplate':'chest','leggings':'legs','boots':'feet'}[piece],
                                                **({} if piece == 'helmet' else {'asset_id':'astral:carnivora'})}},
                 model='astral:' + iid, kind='armor')
    for iid, (name, base, fallback) in SIMPLE.items():
        material = iid == 'colmillo_carnivoro' or iid.startswith('asura_moneda_')
        data = {'type': 'material' if material else 'cosmetic' if iid.endswith('_alas') else 'furniture' if iid.startswith('peluche_') else 'utility'}
        if iid.startswith('carnivora_') and not iid.endswith('_alas'):
            data['tier'] = 3
        if iid.endswith('_alas') or iid.startswith('asura_moneda_'):
            data['tier'] = 4 if iid.startswith('asura_') else 3
        extra = {}
        if iid.endswith('_alas'):
            extra['minecraft:max_stack_size'] = 1
        if iid in ('carnivora_pico', 'carnivora_pala', 'carnivora_azada'):
            extra['minecraft:enchantments'] = {'minecraft:efficiency': 3, 'minecraft:unbreaking': 2}
        add_item(iid, 'minecraft:' + base, name, '#bff05a' if 'carnivor' in iid else 'gold',
                 [txt('Segunda mano: alas cosmeticas; compatible con pechera.' if iid.endswith('_alas') else
                      'Clic derecho en bloque: colocar. Clic izquierdo: recoger.' if iid.startswith('peluche_') else 'Material de forja.' if material else 'Equipo Carnivoro III')],
                 data, extra=extra, model='astral:' + iid, kind='material' if material else 'item')
    for iid in list(CLONES) + ['carnivora_' + p for p in ('helmet','chestplate','leggings','boots')] + [i for i in SIMPLE if i.startswith('carnivora_')]:
        if iid == 'asura_espada':
            continue
        recipes.append((iid, 1, [('c','colmillo_carnivoro', 12 if iid.endswith('chestplate') else 8), ('c','shadowsteel',4), ('c','netherita_reforzada',1)], 'Carnivora'))
    for iid in ('asura_espada', 'asura_alas'):
        recipes.append((iid, 1, [('c','asura_moneda_emerald',32), *[('c','asura_moneda_' + k,2) for k in COINS if k != 'emerald'], ('c','netherita_reforzada',3), ('c','gema_umbria',2)], 'Asura'))


def public_assets():
    """Fallbacks propios; jamas lee x/ ni copia texturas de terceros."""
    files = {}
    def put(name, value):
        files['assets/' + name + '.json'] = json.dumps(value).encode()
    for iid, (source, _, _) in CLONES.items():
        put('astral/items/' + iid, {'model': {'type':'minecraft:model','model':'minecraft:item/' + ('diamond_sword' if 'espada' in iid else 'bow' if 'arco' in iid else 'trident' if 'lanza' in iid else 'diamond_axe')}})
    for iid, (_, _, fallback) in SIMPLE.items():
        put('astral/items/' + iid, {'model': {'type':'minecraft:model', 'model': fallback.replace('minecraft:', 'minecraft:item/')}})
    for piece in ('helmet','chestplate','leggings','boots'):
        put('astral/items/carnivora_' + piece, {'model':{'type':'minecraft:model','model':'minecraft:item/diamond_' + piece}})
    put('astral/equipment/carnivora', {'layers': {k:[{'texture':'minecraft:diamond'}] for k in ('humanoid','humanoid_leggings')}})
    for iid in ('carnivora_alas','asura_alas'):
        # Sin texturas privadas, cosmetic sin geometria: evita usar alas vanilla como falsa elytra.
        put('astral/equipment/' + iid, {'layers':{'humanoid':[]}})
    return files
