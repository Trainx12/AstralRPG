"""Fichas de armas: presentación derivada de los componentes, sin alterar balance.

Los encantamientos nativos quedan visibles para conservar los añadidos por yunque.
El daño es el atributo base del arma; los efectos condicionales se describen aparte.
"""
import re
from escala import fmt
from items import MEJORA_DANO

RAREZA = {1: ('COMÚN', 'white'), 2: ('POCO COMÚN', 'green'),
          3: ('RARA', '#5555FF'), 4: ('ÉPICA', 'dark_purple'), 5: ('LEGENDARIA', 'gold')}
TIPOS = {'sword': 'ESPADA', 'axe': 'HACHA', 'staff': 'BASTÓN', 'scythe': 'GUADAÑA',
         'bow': 'ARCO', 'spear': 'LANZA', 'gloves': 'GUANTES'}
ENCHANTS = {'robo_vida': 'Robo de vida', 'furia': 'Furia', 'remate': 'Remate',
            'verdugo': 'Verdugo', 'sangrado': 'Sangrado', 'hendidura': 'Hendidura',
            'maldicion': 'Maldición', 'cono': 'Cono', 'filo_arcano': 'Filo Arcano',
            'ejecucion': 'Ejecución', 'ejecucion_astral': 'Ejecución Astral',
            'igneo': 'Puño Ígneo', 'punteria': 'Puntería', 'empalar': 'Empalar',
            'poder_astral': 'Poder Astral'}

def txt(text, color='gray', **kw):
    return dict(text=text, color=color, italic=False, **kw)

def roman(n):
    out = ''
    for value, symbol in ((10,'X'),(9,'IX'),(5,'V'),(4,'IV'),(1,'I')):
        while n >= value:
            out += symbol
            n -= value
    return out

def highlighted(text):
    line = txt('')
    line['extra'] = [txt(part, 'green' if re.search(r'\d', part) else 'gray')
                     for part in re.split(r'([+]?\d+(?:[.,]\d+)?%?)', text) if part]
    return line

def stat(label, value, color, delta=None):
    line = txt(label + ': ')
    line['extra'] = [txt(value, color)]
    if delta is not None:
        line['extra'].append(txt(f' (+{fmt(delta)})', 'yellow'))
    return line

def prepare(iid, name, base, lore, data, components, pdc):
    """Captura la fuente una sola vez; los niveles siempre se derivan de ella."""
    kind = data.get('w')
    if not kind:
        kind = 'axe' if 'axe' in base else 'sword'
        if iid == 'varita_estallido':
            kind = 'wand'
    return dict(id=iid, name=name, tier=data['tier'], kind=kind, data=data,
                original=lore, components=components.copy(), pdc=pdc or {})

def render(source, level=0):
    rarity, color = RAREZA[source['tier']]
    data, comps = source['data'], source['components']
    # Los bastones no admiten mejoras del Herrero.
    if source['kind'] == 'staff':
        level = 0
    name = txt(source['name'], color)
    if level:
        name['extra'] = [txt(' ')] + [txt('✪', 'gold') for _ in range(min(level,5))]
        name['extra'] += [txt('✪', 'red') for _ in range(max(0,level-5))]
    original = source['original']
    lore = [txt(original[0]['text'])]
    mods = comps.get('minecraft:attribute_modifiers', [])
    damage = next((m['amount']+1 for m in mods if m['type']=='minecraft:attack_damage'), None)
    if damage is not None:
        factor = MEJORA_DANO[level-1] if level else 1
        lore.append(stat('Daño', '+'+fmt(damage*factor), 'red', damage*(factor-1) if level else None))
    if 'spell' in data:
        lore.append(stat('Daño de hechizo', '+'+fmt(data['spell_display']), 'light_purple'))
    for m in mods:
        attr = m['type'].split(':')[-1]
        if attr == 'attack_speed':
            lore.append(stat('Velocidad de ataque', f"{m['amount']+4:g}", 'white'))
        elif attr == 'movement_speed':
            lore.append(stat('Velocidad', f"+{m['amount']*100:g}%", 'white'))
        elif attr == 'armor':
            lore.append(stat('Defensa', f"+{m['amount']:g}", 'green'))
        elif attr == 'knockback_resistance':
            lore.append(stat('Resistencia al empuje', f"+{m['amount']*100:g}%", 'green'))
    traits = {'max_mana': ('Maná','aqua'), 'mana_regen': ('Regeneración de maná','aqua'),
              'crit_chance': ('Prob. crítica','blue')}
    for trait in source['pdc'].get('auraskills:item_trait_modifiers', []):
        key = trait['auraskills:trait'].split('/')[-1]
        if key in traits:
            label, col = traits[key]
            value = trait['auraskills:value']
            value = getattr(value,'v',value)
            suffix = '%' if key != 'max_mana' else ''
            lore.append(stat(label, f'+{value:g}{suffix}', col))
    lore.append(txt(''))
    ench = [f"{ENCHANTS.get(k.split(':')[-1], k.split(':')[-1].replace('_',' ').title())} {roman(v)}"
            for k,v in comps.get('minecraft:enchantments',{}).items() if k != 'astral:mejora_arma']
    for i in range(0,len(ench),3):
        lore.append(txt(', '.join(ench[i:i+3]), '#5555FF'))
    lore.append(txt(''))
    from special_weapons import WEAPONS
    abilities = WEAPONS.get(source['id'],{}).get('abilities',[])
    if source['kind']=='staff':
        abilities = [dict(name='Proyectil arcano', trigger='CLIC DERECHO',
                          description=['Dispara un proyectil arcano.', 'Daño base sin bonus de armadura.'], cooldown=data['cd_display'])]
    elif source['id'] not in WEAPONS:
        descriptions = [s['text'] for s in original[1:] if not s['text'].startswith(('Requiere:', 'Dano:'))]
        if damage is not None:
            descriptions = [s for s in descriptions if not re.fullmatch(r'\+\d+% de dano',s)]
        enchants = comps.get('minecraft:enchantments',{})
        if source['kind']=='bow':
            abilities = [dict(name='Disparo astral', trigger='CLIC DERECHO', description=descriptions)]
        elif enchants and descriptions:
            key = next(iter(enchants)).split(':')[-1]
            abilities = [dict(name=ENCHANTS.get(key,key.title()), trigger='AL GOLPEAR', description=descriptions)]
    if abilities:
        for ability in abilities:
            header = txt('Habilidad: '+ability['name'], 'gold')
            header['extra']=[txt('  '+ability['trigger'], 'yellow', bold=True)]
            lore.append(header)
            lore.extend(highlighted(s) for s in ability['description'])
            if ability.get('mana'):
                lore.append(stat('Costo de maná', str(ability['mana']), 'aqua'))
            if ability.get('cooldown'):
                lore.append(stat('Recarga', f"{ability['cooldown']:g}s", 'green'))
            lore.extend(txt(s,'dark_gray') for s in ability.get('notes',[]))
    else:
        # El daño incorporado al atributo ya se muestra arriba; no duplicar ese bonus.
        for line in original[1:]:
            text = line.get('text','')
            if text.startswith(('Requiere:', 'Dano:', 'Dano del hechizo:')):
                continue
            if damage is not None and re.fullmatch(r'\+\d+% de dano', text):
                continue
            lore.append(txt(text))
    lore.extend(txt(s['text'],'red') for s in original if s.get('text','').startswith('Requiere:'))
    lore.append(txt(rarity+' '+TIPOS.get(source['kind'],'VARITA'), color, bold=True))
    return {'minecraft:item_name': name, 'minecraft:lore': lore}

def modifier(source, level):
    components = render(source,level)
    return [{'function':'minecraft:set_name','target':'item_name','name':components['minecraft:item_name']},
            {'function':'minecraft:set_lore','mode':'replace_all','lore':components['minecraft:lore']}]
