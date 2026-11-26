"""Fichas de items al estilo Hypixel: presentación derivada de los componentes, sin alterar balance.

Armas, bastones, armaduras, arcos, taladros y motosierras. Los encantamientos nativos quedan
visibles para conservar los añadidos por yunque. Los números salen de items.py / escala.py.
"""
import re
from escala import fmt, REGEN_POR_MANA, HECHIZO_PERFORA
from items import MEJORA_DANO, MEJORA_VIDA, MEJORA_MINADO

RAREZA = {1: ('COMÚN', 'white'), 2: ('POCO COMÚN', 'green'),
          3: ('RARA', '#5555FF'), 4: ('ÉPICA', 'dark_purple'), 5: ('LEGENDARIA', 'gold'),
          # Tiers 6-10 (14/11/2026)
          6: ('MÍTICA', '#ff5fd2'), 7: ('MÍTICA', '#ff5fd2'), 8: ('DIVINA', 'aqua'), 9: ('DIVINA', 'aqua'),
          10: ('ASTRAL', '#b388ff')}
TIPOS = {'knife': 'CUCHILLO', 'sword': 'ESPADA', 'axe': 'HACHA', 'staff': 'BASTÓN', 'scythe': 'GUADAÑA',
         'talisman': 'TALISMÁN', 'bow': 'ARCO', 'crossbow': 'BALLESTA', 'spear': 'LANZA', 'gloves': 'GUANTES', 'drill': 'TALADRO', 'saw': 'MOTOSIERRA',
         'pickaxe': 'PICO', 'shovel': 'PALA', 'hoe': 'AZADA', 'fishing_rod': 'CAÑA', 'shield': 'ESCUDO',
         'helmet': 'CASCO', 'chestplate': 'PECHERA', 'leggings': 'GREBAS', 'boots': 'BOTAS'}
ENCHANTS = {'robo_vida': 'Robo de vida', 'furia': 'Furia', 'remate': 'Remate',
            'verdugo': 'Verdugo', 'sangrado': 'Sangrado', 'hendidura': 'Hendidura',
            'maldicion': 'Maldición', 'cono': 'Cono', 'filo_arcano': 'Filo Arcano',
            'ejecucion': 'Ejecución', 'ejecucion_astral': 'Ejecución Astral',
            'igneo': 'Puño Ígneo', 'punteria': 'Puntería', 'empalar': 'Empalar',
            'poder_astral': 'Poder Astral', 'punteria_set': 'Puntería del Set', 'fortune': 'Fortuna',
            'efficiency': 'Eficiencia', 'unbreaking': 'Irrompibilidad',
            'carga_rapida': 'Carga Rápida', 'piercing': 'Perforación', 'multishot': 'Multidisparo'}
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
    'filo_arcano': lambda l: f"+{num([0.5, 1, 1.8, 3, 4.5, 6, 7.5, 9, 11, 13][min(l, 10) - 1])} de daño por golpe.",
    'igneo': lambda l: "Prende fuego al enemigo por 4 s.",
    'punteria': lambda l: f"Flechas con el daño del tier {l} (+{[0, 8, 15, 22, 30, 38, 46, 54, 62, 70][min(l, 10) - 1]}% extra).",
    'punteria_set': lambda l: f"+{[4, 8, 12, 18, 25, 30, 35, 40, 45, 50][min(l, 10) - 1]}% de daño con arco.",
    'empalar': lambda l: f"+{[1, 2, 3, 4, 6, 7, 8, 9, 10, 12][min(l, 10) - 1]} de daño por golpe.",
    'poder_astral': lambda l: f"Golpes de lanza con el daño del tier {l}.",
    'fortune': lambda l: f"Más minerales por bloque (hasta x{l + 1}).",
    'carga_rapida': lambda l: f"Carga la ballesta en {['0,9', '0,65', '0,2'][min(l, 3) - 1]} s.",
    'piercing': lambda l: f"La flecha atraviesa {l} enemigo{'s' if l > 1 else ''}.",
    'multishot': lambda l: "Dispara 3 flechas por tiro.",
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
    return RAREZA[max(1, min(max(RAREZA), tier))]


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
    """El Herrero mejora armas (bastones incluidos) y armaduras; taladros incluidos; no motosierras."""
    return source['kind'] not in ('saw', 'talisman')


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
    if source['kind']=='talisman':
        labels={'max_health':'Vida máxima','attack_damage':'Daño','movement_speed':'Velocidad','armor':'Defensa'}
        return [stat(labels[m['type'].split(':')[-1]], '+'+num(m['amount']*100)+'%', 'green') for m in comps['minecraft:attribute_modifiers']]
    mods = comps.get('minecraft:attribute_modifiers', [])
    damage = next((m['amount'] + 1 for m in mods if m['type'] == 'minecraft:attack_damage'), None)
    factor = MEJORA_DANO[level - 1] if level else 1
    if damage is not None:
        lines.append(stat('Daño', '+' + fmt(damage * factor), 'red', damage * (factor - 1) if level else None))
    if source['kind'] in ('bow', 'crossbow') and 'arrow' in data:
        arrow = data['arrow']
        lines.append(stat('Daño', '+' + fmt(arrow * factor), 'red', arrow * (factor - 1) if level else None))
    if 'spell' in data:
        spell = data['spell_display']
        lines.append(stat('Daño de hechizo', '+' + fmt(spell * factor), 'light_purple', spell * (factor - 1) if level else None))
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
    from clases import SETS as CL_SETS, stats as cl_stats
    if data['set'] in CL_SETS:   # clases nuevas (22/11): solo stats comunes; las propias van como texto
        tier = {'stats': {k: v for k, v in cl_stats(data['set'], data['tier']).items()
                          if k in ('hp', 'mana', 'mregen', 'cdr', 'crit', 'spd')}}
    else:
        tier = ({'stats': {}} if data['set'] in ('carnivora', 'agua', 'minero', 'talador') else ARMOR_SETS[data['set']]['tiers'][data['tier'] - 1])
    st = tier['stats']
    piece = data['piece']
    q = 4  # cada pieza da 1/4 del bonus del set
    lines = []
    from escala import VIDA_PIEZA
    # Vida fija de la pieza; el (+N%) amarillo es la mejora del Herrero.
    line = txt('Vida: ')
    line['extra'] = [txt(f"+{num(VIDA_PIEZA[data['tier']])}", 'red')]
    if level:
        line['extra'].append(txt(f" (+{num(MEJORA_VIDA[level - 1])}%)", 'yellow'))
    lines.append(line)
    if 'hp' in st:
        v = st['hp'] / q
        lines.append(stat('Bonif. de vida', f"{'+' if v >= 0 else ''}{num(v)}%", 'red'))
    lines.append(stat('Defensa', f"+{num(data['def'])}", 'green'))
    lines += attr_extra_lines(source['components'])

    def pct(label, key, color, sign=1, full=False):
        if key in st:
            v = st[key] * sign / (1 if full else q)
            lines.append(stat(label, f"{'+' if v >= 0 else ''}{num(v)}%", color if v >= 0 else 'red'))

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


# Atributos de oficio/agua que no son vida ni defensa (los numeros salen de los attribute_modifiers reales).
ATTR_EXTRA = {'water_movement_efficiency': ('Eficiencia acuática', 'aqua', 100, '%'),
              'submerged_mining_speed': ('Minado bajo el agua', 'aqua', 100, '%'),
              'oxygen_bonus': ('Aire extra', 'aqua', 1, ''),
              'block_break_speed': ('Velocidad de rotura', 'gold', 100, '%'),
              'mining_efficiency': ('Eficiencia de minado', 'gold', 1, '')}


def attr_extra_lines(comps):
    lines = []
    for m in comps.get('minecraft:attribute_modifiers', []):
        attr = m['type'].split(':')[-1]
        if attr in ATTR_EXTRA:
            label, color, mult, suf = ATTR_EXTRA[attr]
            lines.append(stat(label, f"+{num(round(m['amount'] * mult, 2))}{suf}", color))
    return lines


# Sets con descripcion propia (no estan en SET_BONUS): sus lineas de items van como texto y el "Set completo" como bono.
SETS_PROPIOS = ('carnivora', 'agua', 'minero', 'talador', 'segador', 'invocador', 'asesino')


def set_propio_lines(source):
    """(ayudas, bono) desde la lore original de las armaduras de sets propios."""
    ayudas, bono = [], []
    for line in source['original'][1:]:
        text = line.get('text', '')
        if not text or text.startswith(OMITIR) or text.startswith('Se fabrica'):
            continue
        if text.startswith('Set completo'):
            rest = text.split(':', 1)[1].strip()
            bono += [txt('Bono de set (4/4)', 'gold'), highlighted(rest[0].upper() + rest[1:])]
        else:
            ayudas.append(text)
    return ayudas, bono


def utility_render(iid, name, color, base, lore, data, comps):
    """Ficha simple para herramientas de set (picos, palas, cana, escudo): misma presentacion que las armas."""
    kind = next((k for k in ('pickaxe', 'shovel', 'hoe', 'fishing_rod', 'shield') if k in base), 'pickaxe')
    rarity, rcolor = rareza(data.get('tier', 1), kind)
    out = [txt(lore[0]['text'])] if lore else []
    out += attr_extra_lines(comps)
    ench = enchant_lines(comps)
    if ench:
        out += [txt('')] + ench
    extras = [l.get('text', '') for l in lore[1:] if l.get('text') and not l['text'].startswith(('Requiere:', 'Se fabrica'))]
    if extras:
        out += [txt('')] + [highlighted(e) for e in extras]
    if not any('Velocidad' in l.get('text','') for l in out):out.append(txt('Velocidad: sin modificación'))
    out.append(txt(f"Tier: {data.get('tier', 1)}"))
    out.append(txt(''))
    if not any(l.get('text','').startswith('Requiere:') for l in lore):out.append(txt('Requiere: sin nivel','red'))
    out.extend(txt(l['text'], 'red') for l in lore if l.get('text', '').startswith('Requiere:'))
    out.append(txt(rarity + ' ' + TIPOS[kind], rcolor, bold=True))
    return {'minecraft:item_name': txt(name, color), 'minecraft:lore': out}


def tool_stats(source, level=0):
    from tools import DRILLS, CHAINSAWS, AREA_NAMES
    lines = []
    if source['kind'] == 'drill':
        d = next(x for x in DRILLS if x['id'] == source['id'])
        line = stat('Velocidad de minado', f"+{d['speed']}", 'gold')
        if level:
            line.setdefault('extra', []).append(txt(f" (+{round(MEJORA_MINADO[level - 1] * 100)}%)", 'yellow'))
        lines.append(line)
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


def abilities_for(source, level=0):
    data, kind = source['data'], source['kind']
    from special_weapons import WEAPONS
    from balance_equipo import AGUA_PROYECTIL, AGUA_MANA, AGUA_CD, AGUA_HACHA, ASURA_GOLPES, ASURA_EXTRA, ASURA_CURA
    if source['id']=='espada_heroe_errante':
        return [dict(name='Giro del Heroe',trigger='CLIC DERECHO',mana=30,cooldown=8,description=['Golpe de 360 grados, radio 3: 150% de tu golpe.']), dict(name='Valor del Heroe',trigger='PASIVA',description=['+10% de dano directo con la vida llena.'])]
    if source['id']=='asura_espada':
        return [dict(name='Furia de Asura', trigger='PASIVA', description=[f'Cada {ASURA_GOLPES} golpes directos al mismo enemigo en 5 s: +{num(ASURA_EXTRA*100)}% de daño y cura {num(ASURA_CURA*100)}% de vida máxima.'])]
    if source['id']=='agua_espada':
        return [dict(name='Proyectil de agua', trigger='CLIC DERECHO', mana=AGUA_MANA, cooldown=AGUA_CD/20,
                     description=[f'Proyectil de {fmt(AGUA_PROYECTIL)} de daño (bastón T3 -10%).'])]
    if source['id']=='agua_hacha':
        return [dict(name='Fuerza de las Mareas', trigger='BAJO EL AGUA', description=[f'+{num(AGUA_HACHA*100)}% de daño con golpes directos.'])]
    if source['id']=='agua_arco':
        return [dict(name='Flecha de las Mareas', trigger='AL DISPARAR', description=['Flechas con el mismo rozamiento en agua que en aire.'])]
    if source['id'] in WEAPONS:
        abilities = WEAPONS[source['id']].get('abilities', [])
        if source['id']=='hacha_terremoto' and level:
            from copy import deepcopy
            abilities=deepcopy(abilities)
            base=2*WEAPONS[source['id']]['damage_total']
            abilities[0]['description'][0]=abilities[0]['description'][0].replace(fmt(base),fmt(base*MEJORA_DANO[level-1]))
        return abilities
    if kind == 'staff':
        return [dict(name='Proyectil arcano', trigger='CLIC DERECHO',
                     description=[f'Atraviesa hasta {len(HECHIZO_PERFORA)} enemigos.',
                                   'Daño: ' + '/'.join(f'{v:.0%}' for v in HECHIZO_PERFORA) + '.',
                                   'El daño de hechizo sube con la armadura de Mago.'],
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
        lore += tool_stats(source, level)
    else:
        lore += weapon_stats(source, level)
    ench = enchant_lines(comps)
    if ench:
        lore += [txt('')] + ench
    ayudas, bono_propio = set_propio_lines(source) if kind in ARMOR_PIECES and source['data'].get('set') in SETS_PROPIOS else ([], [])
    extras = ayudas if kind in ARMOR_PIECES else [] if kind in ('drill', 'saw') else extra_lines(source)
    if extras:
        lore += [txt('')] + [highlighted(e) for e in extras]
    for ability in abilities_for(source, level):
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
        bono = set_bonus_lines(source) + bono_propio
        if bono:
            lore += [txt('')] + bono
    if 'minecraft:max_damage' in comps and kind not in ('drill','saw'):
        lore.append(stat('Durabilidad',num(comps['minecraft:max_damage']),'white'))
    if not any('Velocidad' in l.get('text','') for l in lore):lore.append(txt('Velocidad: sin modificación'))
    lore.append(txt(f"Tier: {source['tier']}"))
    lore.append(txt(''))
    if not any(s.get('text','').startswith('Requiere:') for s in original):
        lore.append(txt('Requiere: sin nivel', 'red'))
    lore.extend(txt(s['text'], 'red') for s in original if s.get('text', '').startswith('Requiere:'))
    lore.append(txt(rarity + ' ' + TIPOS.get(kind, 'VARITA'), color, bold=True))
    return {'minecraft:item_name': name, 'minecraft:lore': lore}


def modifier(source, level):
    components = render(source, level)
    return [{'function': 'minecraft:set_name', 'target': 'item_name', 'name': components['minecraft:item_name']},
            {'function': 'minecraft:set_lore', 'mode': 'replace_all', 'lore': components['minecraft:lore']}]
