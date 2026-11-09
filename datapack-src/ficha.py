"""Fichas de items al estilo Hypixel: presentación derivada de los componentes, sin alterar balance.

Armas, bastones, armaduras, arcos, taladros y motosierras. Los encantamientos nativos quedan
visibles para conservar los añadidos por yunque. Los números salen de items.py / escala.py.
"""
import re
from escala import fmt, REGEN_POR_MANA
from items import MEJORA_DANO, MEJORA_VIDA

RAREZA = {1: ('COMÚN', 'white'), 2: ('POCO COMÚN', 'green'),
          3: ('RARA', '#5555FF'), 4: ('ÉPICA', 'dark_purple'), 5: ('LEGENDARIA', 'gold')}
TIPOS = {'sword': 'ESPADA', 'axe': 'HACHA', 'staff': 'BASTÓN', 'scythe': 'GUADAÑA',
         'bow': 'ARCO', 'spear': 'LANZA', 'gloves': 'GUANTES', 'drill': 'TALADRO', 'saw': 'MOTOSIERRA',
         'helmet': 'CASCO', 'chestplate': 'PECHERA', 'leggings': 'GREBAS', 'boots': 'BOTAS'}
ENCHANTS = {'robo_vida': 'Robo de vida', 'furia': 'Furia', 'remate': 'Remate',
            'verdugo': 'Verdugo', 'sangrado': 'Sangrado', 'hendidura': 'Hendidura',
            'maldicion': 'Maldición', 'cono': 'Cono', 'filo_arcano': 'Filo Arcano',
            'ejecucion': 'Ejecución', 'ejecucion_astral': 'Ejecución Astral',
            'igneo': 'Puño Ígneo', 'punteria': 'Puntería', 'empalar': 'Empalar',
            'poder_astral': 'Poder Astral', 'punteria_set': 'Puntería del Set', 'fortune': 'Fortuna',
            'efficiency': 'Eficiencia', 'unbreaking': 'Irrompibilidad'}
# Qué hace cada encantamiento (los números salen de su definición en build.py).
ENCH_DESC = {
    'robo_vida': lambda l: f"{[10, 15, 25, 30, 40][min(l, 5) - 1]}% de curarte al golpear (Regeneración III, 2 s).",
    'furia': lambda l: ("Hasta +15% de daño cuanto menos vida tengas." if l == 1
                        else "+5% de daño por cada 10% de vida perdida (hasta +45%)."),
    'remate': lambda l: "+5% de daño a enemigos con menos del 50% de vida.",
    'verdugo': lambda l: "+10% de daño a enemigos con armadura.",
    'sangrado': lambda l: "10% de causar sangrado: 5 golpes de daño extra.",
    'hendidura': lambda l: "También golpea a los enemigos a 2,5 bloques.",
    'ejecucion': lambda l: "Ejecuta enemigos con menos del 15% de vida.",
    'ejecucion_astral': lambda l: "Ejecuta enemigos con menos del 20% de vida.",
    'cono': lambda l: "Golpea a todos en un cono frente a vos.",
    'maldicion': lambda l: "Aplica Lentitud y Debilidad por 2 a 3 s.",
    'filo_arcano': lambda l: f"+{num([0.5, 1, 1.8, 3, 4.5][min(l, 5) - 1])} de daño por golpe.",
    'igneo': lambda l: "Prende fuego al enemigo por 4 s.",
    'punteria': lambda l: f"Flechas con el daño del tier {l} (+{[0, 8, 15, 22, 30][min(l, 5) - 1]}% extra).",
    'punteria_set': lambda l: f"+{[4, 8, 12, 18, 25][min(l, 5) - 1]}% de daño con arco.",
    'empalar': lambda l: f"+{[1, 2, 3, 4, 6][min(l, 5) - 1]} de daño por golpe.",
    'poder_astral': lambda l: f"Golpes de lanza con el daño del tier {l}.",
    'fortune': lambda l: f"Más minerales por bloque (hasta x{l + 1}).",
}
# Lineas de descripcion de items.py que ya explica un encantamiento (no se repiten).
CUBIERTO = {'Robo de vida', 'Roba vida', '+5% de dano a enemigos con menos del 50% de vida',
            'Mas dano cuanto menos vida tenes (hasta +15%)', '+5% de dano por cada 10% de vida perdida',
            '+10% de dano a enemigos con armadura', '10% de probabilidad de causar sangrado',
            'Golpes en area pequena', 'Ejecuta enemigos con menos del 15% de vida',
            'Aplica lentitud o debilidad', 'Ataques en cono frontal', 'Ejecuta mobs con menos del 20% de vida',
            'Dano en area en cono', 'Tus golpes queman'}


def num(x):
    """2.5 -> '2,5'; 3.0 -> '3'; miles con punto."""
    if abs(x - round(x)) < 1e-9:
        return fmt(x)
    return f"{x:.2f}".rstrip('0').rstrip('.').replace('.', ',')


def rareza(tier, kind):
    # Taladros: 9 tiers repartidos en las 5 rarezas.
    if kind == 'drill':
        tier = min(5, (tier * 5 + 8) // 9)
    return RAREZA[max(1, min(5, tier))]


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

ARMOR_PIECES = ('helmet', 'chestplate', 'leggings', 'boots')
OMITIR = ('Requiere:', 'Dano:', 'Dano del hechizo:', 'Costo del hechizo:', 'Dano de flecha cargada:',
          'Mantene click derecho:', 'Click derecho: proyectil arcano', 'Habilidades: mobs')


def prepare(iid, name, base, lore, data, components, pdc):
    """Captura la fuente una sola vez; los niveles siempre se derivan de ella."""
    kind = data.get('w')
    if data.get('type') == 'armor':
        kind = data['piece']
    elif data.get('type') == 'tool':
        kind = data['tool']
    elif not kind:
        kind = 'axe' if 'axe' in base else 'sword'
        if iid in ('varita_estallido', 'varita_curacion'):
            kind = 'wand'
    return dict(id=iid, name=name, tier=data['tier'], kind=kind, data=data,
                original=lore, components=components.copy(), pdc=pdc or {})


def mejorable(source):
    """El Herrero mejora armas (no bastones) y armaduras; no herramientas."""
    return source['kind'] not in ('staff', 'drill', 'saw')


def enchant_lines(comps):
    ench = [(k.split(':')[-1], v) for k, v in comps.get('minecraft:enchantments', {}).items()
            if not k.split(':')[-1].startswith('mejora_')]
    lines = []
    if len(ench) <= 3:
        # Pocos: nombre en azul y debajo que hace (como el arco de Hypixel).
        for key, lvl in ench:
            lines.append(txt(f"{ENCHANTS.get(key, key.replace('_', ' ').title())} {roman(lvl)}", '#5555FF'))
            if key in ENCH_DESC:
                lines.append(highlighted(ENCH_DESC[key](lvl)))
    else:
        names = [f"{ENCHANTS.get(k, k.replace('_', ' ').title())} {roman(v)}" for k, v in ench]
        for i in range(0, len(names), 3):
            lines.append(txt(', '.join(names[i:i + 3]), '#5555FF'))
    return lines


def extra_lines(source):
    """Descripciones de items.py que no explica un encantamiento ni una stat."""
    out = []
    for line in source['original'][1:]:
        text = line.get('text', '')
        if not text or text.startswith(OMITIR) or text in CUBIERTO:
            continue
        if re.fullmatch(r'[+-]\d+% (de )?dano( magico)?|\+\d+ mana', text):
            continue
        out.append(text)
    return out


def weapon_stats(source, level):
    data, comps = source['data'], source['components']
    lines = []
    mods = comps.get('minecraft:attribute_modifiers', [])
    damage = next((m['amount'] + 1 for m in mods if m['type'] == 'minecraft:attack_damage'), None)
    factor = MEJORA_DANO[level - 1] if level else 1
    if damage is not None:
        lines.append(stat('Daño', '+' + fmt(damage * factor), 'red', damage * (factor - 1) if level else None))
    if source['kind'] == 'bow' and 'arrow' in data:
        arrow = data['arrow']
        lines.append(stat('Daño', '+' + fmt(arrow * factor), 'red', arrow * (factor - 1) if level else None))
    if 'spell' in data:
        lines.append(stat('Daño de hechizo', '+' + fmt(data['spell_display']), 'light_purple'))
    if data.get('mdmg') and source['kind'] == 'staff':
        lines.append(stat('Daño mágico', f"+{num(data['mdmg'] / 100)}%", 'light_purple'))
    for m in mods:
        attr = m['type'].split(':')[-1]
        if attr == 'attack_speed':
            lines.append(stat('Velocidad de ataque', num(m['amount'] + 4), 'white'))
        elif attr == 'movement_speed':
            lines.append(stat('Velocidad', f"+{num(m['amount'] * 100)}%", 'white'))
        elif attr == 'armor':
            lines.append(stat('Defensa', f"+{num(m['amount'])}", 'green'))
        elif attr == 'knockback_resistance':
            lines.append(stat('Resistencia al empuje', f"+{num(m['amount'] * 100)}%", 'green'))
    if source['kind'] == 'bow':
        if data.get('draw'):
            lines.append(stat('Velocidad de carga', f"+{data['draw']}%", 'white'))
        if data.get('auto'):
            lines.append(stat('Disparo automático', f"cada {num(data['auto'])}s", 'green'))
    traits = {'max_mana': ('Maná', 'aqua'), 'mana_regen': ('Regeneración de maná', 'aqua'),
              'crit_chance': ('Prob. crítica', 'blue')}
    for trait in source['pdc'].get('auraskills:item_trait_modifiers', []):
        key = trait['auraskills:trait'].split('/')[-1]
        if key in traits:
            label, col = traits[key]
            value = getattr(trait['auraskills:value'], 'v', trait['auraskills:value'])
            # mana_regen es mana por segundo (AuraSkills), no un porcentaje.
            suffix = {'max_mana': '', 'mana_regen': '/s'}.get(key, '%')
            lines.append(stat(label, f'+{num(value)}{suffix}', col))
    return lines


def armor_stats(source, level):
    from items import ARMOR_SETS, ARMOR_VALUES, TOUGHNESS
    data = source['data']
    tier = ARMOR_SETS[data['set']]['tiers'][data['tier'] - 1]
    st = tier['stats']
    piece = data['piece']
    q = 4  # cada pieza da 1/4 del bonus del set
    lines = []
    vida = []
    if 'hp' in st:
        vida.append(txt(f"{'+' if st['hp'] >= 0 else ''}{num(st['hp'] / q)}%", 'red' if st['hp'] >= 0 else 'dark_red'))
    if level:
        extra = MEJORA_VIDA[level - 1]
        if not vida:
            vida.append(txt(f"+{num(extra)}", 'red'))
        vida.append(txt(f" (+{num(extra)})", 'yellow'))
    if vida:
        line = txt('Vida: ')
        line['extra'] = vida
        lines.append(line)
    lines.append(stat('Defensa', f"+{num(ARMOR_VALUES[tier['mat']][piece] + tier.get('extra_armor', 0))}", 'green'))
    tough = TOUGHNESS[tier['mat']] + tier.get('tough', 0)
    if tough:
        lines.append(stat('Dureza', f"+{num(tough)}", 'green'))

    def pct(label, key, color, sign=1, full=False):
        if key in st:
            v = st[key] * sign / (1 if full else q)
            lines.append(stat(label, f"{'+' if v >= 0 else ''}{num(v)}%", color if v >= 0 else 'red'))

    pct('Bonif. de defensa', 'def', 'green')
    pct('Daño', 'dmg', 'red')
    if 'mana' in st:
        mana = st['mana'] / q
        lines.append(stat('Maná', f"+{num(mana)}", 'aqua'))
        regen = mana * REGEN_POR_MANA * (1 + st.get('mregen', 0) / 100)
        lines.append(stat('Regeneración de maná', f"+{num(round(regen, 2))}/s", 'aqua'))
    pct('Daño mágico', 'mdmg', 'light_purple')
    pct('Enfriamiento de hechizos', 'cdr', 'aqua', sign=-1)
    pct('Daño a distancia', 'rdmg', 'red')
    pct('Prob. crítica', 'crit', 'blue')
    pct('Velocidad', 'spd', 'white')
    if piece == 'chestplate':
        pct('Velocidad de carga', 'draw', 'white', full=True)
    pct('Tiempo en llamas', 'fire', 'gold', sign=-1)
    if 'kb' in st:
        lines.append(stat('Resistencia al empuje', f"+{num(st['kb'] / q)}%", 'green'))
    return lines


def tool_stats(source):
    from tools import DRILLS, CHAINSAWS, AREA_NAMES
    lines = []
    if source['kind'] == 'drill':
        d = next(x for x in DRILLS if x['id'] == source['id'])
        lines.append(stat('Velocidad de minado', f"+{d['speed']}", 'gold'))
        lines.append(stat('Área de minado', AREA_NAMES[d['area']], 'gold'))
    else:
        d = next(x for x in CHAINSAWS if x['id'] == source['id'])
        lines.append(stat('Velocidad de tala', f"+{d['speed']}", 'gold'))
        chain = d['chain']
        lines.append(stat('Tala por corte', 'el árbol entero' if chain >= 100
                          else f"{chain + 1} tronco{'s' if chain else ''}", 'gold'))
    if 'dur' in d:
        lines.append(stat('Durabilidad', fmt(d['dur']), 'white'))
    else:
        lines.append(txt('Indestructible', 'aqua'))
    return lines


def abilities_for(source):
    data, kind = source['data'], source['kind']
    from special_weapons import WEAPONS
    if source['id'] in WEAPONS:
        return WEAPONS[source['id']].get('abilities', [])
    if kind == 'staff':
        return [dict(name='Proyectil arcano', trigger='CLIC DERECHO',
                     description=['Dispara un proyectil arcano.', 'El daño de hechizo sube con la armadura de Mago.'],
                     mana=data.get('mana_display'), cooldown=data['cd_display'])]
    if kind == 'bow' and data.get('auto'):
        return [dict(name='Disparo automático', trigger='MANTENER CLIC DERECHO',
                     description=[f"Dispara solo cada {num(data['auto'])} s mientras lo mantenés."])]
    if kind == 'drill':
        return [dict(name='Precisión', trigger='SHIFT', description=['Rompe solo el bloque apuntado.'])]
    if kind == 'saw':
        return [dict(name='Precisión', trigger='SHIFT', description=['Corta un solo bloque.'])]
    return []


def set_bonus_lines(source):
    from items import SET_BONUS
    out = []
    for npz, (desc, _) in SET_BONUS.get(source['data']['set'], {}).items():
        text = desc[0].upper() + desc[1:]
        out += [txt(f'Bono de set ({npz}/4)', 'gold'), highlighted(text if text.endswith('.') else text + '.')]
    return out


def render(source, level=0):
    kind = source['kind']
    rarity, color = rareza(source['tier'], kind)
    comps = source['components']
    if not mejorable(source):
        level = 0
    name = txt(source['name'], color)
    if level:
        name['extra'] = [txt(' ')] + [txt('✪', 'gold') for _ in range(min(level, 5))]
        name['extra'] += [txt('✪', 'red') for _ in range(max(0, level - 5))]
    original = source['original']
    lore = [txt(original[0]['text'])]
    if kind in ARMOR_PIECES:
        lore += armor_stats(source, level)
    elif kind in ('drill', 'saw'):
        lore += tool_stats(source)
    else:
        lore += weapon_stats(source, level)
    ench = enchant_lines(comps)
    if ench:
        lore += [txt('')] + ench
    extras = [] if kind in ('drill', 'saw') or kind in ARMOR_PIECES else extra_lines(source)
    if extras:
        lore += [txt('')] + [highlighted(e) for e in extras]
    for ability in abilities_for(source):
        lore.append(txt(''))
        header = txt('Habilidad: ' + ability['name'], 'gold')
        header['extra'] = [txt('  ' + ability['trigger'], 'yellow', bold=True)]
        lore.append(header)
        lore.extend(highlighted(s) for s in ability['description'])
        if ability.get('mana'):
            lore.append(stat('Costo de maná', str(ability['mana']), 'aqua'))
        if ability.get('cooldown'):
            lore.append(stat('Recarga', f"{num(ability['cooldown'])}s", 'green'))
        lore.extend(txt(s, 'dark_gray') for s in ability.get('notes', []))
    if kind in ARMOR_PIECES:
        lore += [txt('')] + set_bonus_lines(source)
    lore.append(txt(''))
    lore.extend(txt(s['text'], 'red') for s in original if s.get('text', '').startswith('Requiere:'))
    lore.append(txt(rarity + ' ' + TIPOS.get(kind, 'VARITA'), color, bold=True))
    return {'minecraft:item_name': name, 'minecraft:lore': lore}


def modifier(source, level):
    components = render(source, level)
    return [{'function': 'minecraft:set_name', 'target': 'item_name', 'name': components['minecraft:item_name']},
            {'function': 'minecraft:set_lore', 'mode': 'replace_all', 'lore': components['minecraft:lore']}]
