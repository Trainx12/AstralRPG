"""Balance propio para Stellarity 5.4.2; no modifica el datapack del autor."""
import json
from pathlib import Path
from escala import DANO, FACTOR_ARMA, VIDA_PIEZA, defensa_pieza, fmt
from items import SWORDS, AXES, SCYTHES, SPEARS, BOWS, STAFFS, SKILLS, ARMOR_LEVEL_SIN_CLASE
from items_t6_10 import PUNTERIA, BALLESTAS
from tools import DRILLS
from balance_equipo import LANZA_DANO

VERSION = 1
CATALOG = json.loads(Path(__file__).with_name('guia_stellarity.json').read_text(encoding='utf8'))['items']
# id de catalogo -> (tier, familia); los ids reales se resuelven por custom_data, nunca por nombre traducido.
WEAPONS = {
    'sharanga': (3, 'bow'), 'shulker_sword': (4, 'sword'), 'shulker_axe': (4, 'axe'),
    'shulker_spear': (4, 'spear'), 'sandstorm_trident': (4, 'spear'),
    'dragonblade': (5, 'sword'), 'tamaris': (5, 'sword'), 'spectral_fury': (5, 'bow'),
    'call_of_the_void': (5, 'bow'), 'slayer_crossbow': (5, 'crossbow'),
    'kaleidoscope': (6, 'sword'), 'prismember': (6, 'sword'), 'prismatic_punch': (6, 'crossbow'),
    'starless_scythe': (6, 'scythe'), 'stellar_striker': (6, 'sword'), 'harvester': (6, 'scythe'),
    'fluffy_hammer': (7, 'axe'), 'spirit_dagger': (7, 'sword'), 'alpha_wooden_sword': (7, 'sword'),
}
ARMOR = {f'{s}_{p}': (t, p) for s, t in [('floral', 4), ('champion', 4), ('shulker', 5), ('hallowed', 6)]
         for p in ('helmet', 'chestplate', 'leggings', 'boots')}
WINGS = {'phantom_wings': 4, 'dragon_wings': 6, 'empress_wings': 6}
UTILITY = {'shulker_pickaxe': 4, 'shulker_shovel': 4, 'shulker_hoe': 4,
    'copper_elektra_shield': 4, 'crest_of_the_end': 5, 'starstruck_shield': 6, 'prismatic_pearl': 6,
    'life_crystal': 5, 'soaring_insignia': 6, 'endermans_hand': 4, 'decayed_clover': 4,
    'fisher_of_voids': 4, 'satchel_of_voids': 5, 'void_locket': 5, 'bell_flower': 4, 'duskberry': 4}
BOOKS = {'book_of_conveyance': 4, 'book_of_obstruct': 4, 'book_of_return': 4, 'book_of_updraft': 4,
         'book_of_jinx': 5, 'book_of_light': 6}
FIXED = {k: {'food': 2000, 'potions': 20000, 'materials': 5000}.get(v['group'], 5000)
         for k, v in CATALOG.items() if v['group'] in ('food', 'potions', 'materials')}
FIXED.update(dict(starlight_soot=100000, hallowed_ingot=1000000, enderite_shard=250000,
    enderite_smithing_template=500000, chorus_plating=50000, sand_rune=50000,
    pho=30000, prismatic_sushi=50000, shepherds_pie=30000, sushi=10000,
    frozen_carpaccio=20000, chorus_pie=10000, chorus_stew=10000, loaf_of_plenty=50000))


def weapon(family, tier):
    table = {'sword': SWORDS, 'axe': AXES, 'scythe': SCYTHES, 'spear': SPEARS,
             'bow': BOWS, 'crossbow': BOWS}[family]
    row = table[tier - 1]
    if family in ('bow', 'crossbow'):
        damage = round(9 * PUNTERIA[tier - 1] * FACTOR_ARMA[tier])
    elif family == 'spear':
        damage = DANO[tier] * LANZA_DANO
    else:
        damage = row['dmg'] * (1 + row.get('bonus', 0) / 100) * FACTOR_ARMA[tier]
    level = BALLESTAS.get(tier, row)['lvl'] if family == 'crossbow' else row['lvl']
    return round(damage, 3), 'archery' if family in ('bow', 'crossbow') else 'fighting', level


def rows():
    out = {}
    for key, (tier, family) in WEAPONS.items():
        damage, skill, level = weapon(family, tier)
        out[key] = dict(tier=tier, kind='weapon', family=family, damage=damage, skill=skill, level=level)
    for key, (tier, piece) in ARMOR.items():
        out[key] = dict(tier=tier, kind='armor', piece=piece, defense=defensa_pieza(tier, piece),
                        health=VIDA_PIEZA[tier], skill='fighting', level=ARMOR_LEVEL_SIN_CLASE[tier])
    for key, tier in WINGS.items():
        out[key] = dict(tier=tier, kind='armor', piece='chestplate', defense=round(defensa_pieza(tier, 'chestplate') * .6),
                        health=VIDA_PIEZA[tier] * .6, skill='fighting', level=ARMOR_LEVEL_SIN_CLASE[tier])
    for key, tier in UTILITY.items():
        mining = key in ('shulker_pickaxe', 'shulker_shovel')
        out[key] = dict(tier=tier, kind='utility', skill='mining' if mining else 'fighting',
                        level=DRILLS[tier - 1]['lvl'] if mining else ARMOR_LEVEL_SIN_CLASE[tier])
    for key, tier in BOOKS.items():
        out[key] = dict(tier=tier, kind='utility', skill='sorcery', level=STAFFS[tier - 1]['lvl'])
    out['reinforced_horse_armor'] = dict(tier=5, kind='horse')  # precio solamente
    for key, price in FIXED.items():
        out[key] = dict(tier=0, kind='fixed', price=price)
    for key, row in out.items():
        row['factor'] = FACTOR_ARMA.get(row['tier'], 1)
        row['version'] = VERSION
        row['lore'] = lore(row)
    return out


def lore(row):
    if not row['tier']:
        return []
    lines = [f"Tier: {row['tier']}"]
    if row.get('damage'): lines.append('Dano: ' + fmt(row['damage']))
    if row.get('defense'): lines += ['Defensa: ' + fmt(row['defense']), 'Vida: +' + fmt(row['health'])]
    if row.get('skill'): lines.append(f"Requiere: {SKILLS[row['skill']]} {row['level']}")
    return lines


def suggested(row, weapon_prices, armor_prices):
    if row['kind'] == 'fixed': return row['price']
    tier = row['tier']
    if row['kind'] in ('armor', 'horse'): return armor_prices[tier]
    return weapon_prices[tier] * (1 if row['kind'] == 'weapon' else .5)
