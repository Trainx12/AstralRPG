"""Balance 16/11: datos compartidos por fichas, generadores y ensayo."""
from escala import DANO, HECHIZO, MANA_HECHIZO

SPECIAL_TIERS = {'espada_destello': 2, 'espada_tormenta': 3, 'espada_sombras': 4,
                 'hacha_terremoto': 3, 'varita_estallido': 4, 'varita_curacion': 3}
TALISMAN_PCT = (.05, .10, .20)
LANZA_DANO = .9
LANZA_VELOCIDAD = 1.1
ASURA_DANO = 1.10
ASURA_GOLPES = 4
ASURA_EXTRA = .50
ASURA_CURA = .05
CARNIVORA_DEF = 5
CARNIVORA_CURA_BAJA = .03  # vida maxima; regeneracion al matar, sin curas enormes por dano escalado
AGUA_HACHA = .25
AGUA_PROYECTIL = round(HECHIZO[3] * (1+__import__('items').STAFFS[2]['mdmg']/100) * .9)
AGUA_MANA = MANA_HECHIZO[3]
AGUA_CD = __import__('items').STAFFS[2]['cd']  # ticks, igual al baston T3 antes del CDR
NADO_FACTOR = 1.5
GOLPES_MAZMORRA = 200  # presupuesto conservador, no medicion con jugadores
ARMOR_MIN = GOLPES_MAZMORRA * 12 + 1
WEAPON_MIN = 600 * 12 + 1


def finalize(items, fichas):
    """Completa el contrato de equipo antes de exportar recetas/migraciones."""
    import re
    from copy import deepcopy
    from ficha import prepare, render, utility_render, txt, num
    for iid, item in items.items():
        c = item['components']
        raw = c.get('minecraft:custom_data', '')
        tier = re.search(r'\btier:(\d+)', raw)
        if not tier:
            continue
        tier = int(tier[1])
        armor = iid in fichas and fichas[iid]['kind'] in ('helmet', 'chestplate', 'leggings', 'boots')
        # Toda armadura usa max_damage explicito; armas vanilla tambien migran al presupuesto.
        if armor:
            c['minecraft:max_damage'] = max(ARMOR_MIN, c.get('minecraft:max_damage', 0))
        elif item['kind'] == 'weapon' and (iid not in fichas or fichas[iid]['kind'] not in ('drill','saw')) and any(k in item['base'] for k in ('sword', 'axe', 'hoe', 'bow', 'spear')):
            if 'minecraft:unbreakable' not in c:
                c['minecraft:max_damage'] = max(WEAPON_MIN, c.get('minecraft:max_damage', 0))
        if 'type:"utility"' in raw and any(k in item['base'] for k in ('pickaxe','shovel','hoe','fishing_rod','shield')):
            c['minecraft:max_damage'] = max(WEAPON_MIN, c.get('minecraft:max_damage',0))
            c['minecraft:lore'].insert(1,txt('Durabilidad: '+num(c['minecraft:max_damage'])))
        if iid in fichas:
            f = fichas[iid]
            f['components'] = deepcopy(c)
            c.update(render(f))
        elif 'type:talisman' in raw or 'type:"talisman"' in raw:
            f = prepare(iid, item['name'], item['base'], c['minecraft:lore'],
                        {'type': 'talisman', 'w': 'talisman', 'tier': tier}, c, {})
            fichas[iid] = f
            c.update(render(f))
            item['ficha'] = True
            item['mejorable'] = False
        # Movilidad no inflige dano: se declara explicitamente.
        elif iid in ('gancho', 'gancho_realista'):
            original=c['minecraft:lore']
            c['minecraft:lore'] = [txt('Movilidad Astral I'), txt('Daño: 0 (movilidad)'),
                txt('Velocidad: sin modificación'), txt(''),
                txt('Habilidad: '+item['name']+'  CLIC DERECHO','gold'), *original,
                txt(f'Tier: {tier}'),txt(''),txt('Requiere: sin nivel'),txt('COMÚN MOVILIDAD','white',bold=True)]
