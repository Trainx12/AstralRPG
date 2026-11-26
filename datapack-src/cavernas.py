# -*- coding: utf-8 -*-
"""Cavernas de Cristal Astrales (plan E5 / tanda 7e, 19/11/2026). FUENTE UNICA.

Mundo `cavernas_cristal`: caverna enorme y cerrada (techo de roca, sin cielo), borde 1.000 x 1.000. Lo genera el
plugin propio AstralCavernas (modelo: AstralOceano), que ademas pone las reglas, el campamento de la entrada,
los mobs y mini jefes, las comisiones diarias, la venta y la regeneracion cada 3 dias.

Zonas (por posicion; el Corazon es el centro y lo mas hondo):
  Corazon de Opalo y Onix   radio < 150 alrededor de 0,0; el piso baja hasta ~50 bloques; tier 5
  Jardin de Amatista (N), Grietas de Jade (E), Forja de Rubi y Topacio (S), Lago de Zafiro (O); tier 4
Vetas = bloque de nota en campana (bell) con nota propia; cada una suelta su gema (calidad al azar, mejor en las
vetas profundas, y + con Polvo de Cristal). Se pican con taladro de RUBI (tier 4) o mejor, a mano o en area.
Menas para vender: Cristal Astral en bruto (comun) y Geoda Estelar (honda). Precios: economia.CAVERNAS_PRECIO.

Salidas: python cavernas.py [--jdk <bin JDK 25>]
  datapack (build.py: register)    items, tabla del bloque de nota, guardas del taladro, conteo para comisiones
  build/cavernas/AstralCavernas.jar  plugin (con --jdk); config.yml; comandos.txt
  build/mythicmobs/mobs/cavernas.yml  golems, aranas y 5 mini jefes
  build/menus/DeluxeMenus/gui_menus/cavernas_aviso.yml  ventana de aviso (boton del menu de Portales)
"""
import argparse
import json
import os
import subprocess
import zipfile
from pathlib import Path

import economia as E
import gemas as G

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = ROOT / 'build' / 'cavernas'
NS = 'astral'
WORLD = 'cavernas_cristal'
VERSION = '1.4.0'
STAMP = (2026, 11, 19, 0, 0, 0)
RADIO = 500                      # borde 1.000 x 1.000
REGENERAR_HORAS = 72
AVISOS_MIN = (10, 5, 1)
TIER = 4                         # zonas exteriores; el Corazon es TIER_CORAZON (build.py mob/roll)
TIER_CORAZON = 5
CORAZON_R = 150
CAMPAMENTO = (0, -300)           # x, z del campamento (spawn): Jardin de Amatista
CAMP_Y = 12
DRILL_TIER = 4                   # taladro de rubi o mejor
POLVO_MIN = 10                   # minutos de Polvo de Cristal por unidad

# zona: (nombre, color &, gemas, pesos de las vetas). El orden de las zonas es el de AstralCavernas.java.
ZONAS = {
    'amatista': ('Jardin de Amatista', '&5', ['amatista']),
    'jade': ('Grietas de Jade', '&a', ['jade']),
    'rubi': ('Forja de Rubi', '&c', ['rubi', 'topacio']),
    'zafiro': ('Lago de Zafiro', '&9', ['zafiro']),
    'corazon': ('Corazon de Opalo y Onix', '&8', ['opalo', 'onix']),
}

# ------------------------------------------------------------------ vetas (bloque de nota en campana)
INSTRUMENTO = 'bell'


def nota_gema(tipo, honda=False):
    return list(G.TIPOS).index(tipo) * 2 + (1 if honda else 0)


MENAS = {'cristal_caverna': 14, 'geoda_estelar': 15}
NOTAS = sorted([nota_gema(t, h) for t in G.TIPOS for h in (False, True)] + list(MENAS.values()))
# Pesos por mil de Cruda, Pulida, Impecable, Perfecta, Estelar. 20/11: menos Pulida y Perfecta/Estelar muy raras.
CALIDAD = {'normal': (879, 100, 20, 1, 0), 'honda': (719, 220, 55, 5, 1),
           'normal_polvo': (758, 190, 50, 2, 0), 'honda_polvo': (571, 320, 95, 12, 2)}
HONDA_Y = 0                      # una veta por debajo de esta altura es honda

# ------------------------------------------------------------------ items propios
ITEMS = {
    'cristal_caverna': ('Cristal Astral en bruto', '#b58cff', 'Se vende en el campamento de las Cavernas.'),
    'geoda_estelar': ('Geoda Estelar', '#7fe0ff', 'Rara y honda. Se vende en el campamento de las Cavernas.'),
    'polvo_cristal': ('Polvo de Cristal', '#f0d0ff', f'Clic derecho: {POLVO_MIN} min de gemas de mejor calidad en las Cavernas.'),
}

# ------------------------------------------------------------------ comisiones (3 por dia y por jugador)
# (clave, texto, tipo, objetivo, cantidad, dificultad, polvo)
COMISIONES = [
    ('amatista', 'Pica 60 vetas de Amatista', 'veta', 'amatista', 60, 'facil', 1),
    ('jade', 'Pica 60 vetas de Jade', 'veta', 'jade', 60, 'facil', 1),
    ('rubi', 'Pica 50 vetas de Rubi', 'veta', 'rubi', 50, 'facil', 1),
    ('topacio', 'Pica 50 vetas de Topacio', 'veta', 'topacio', 50, 'facil', 1),
    ('zafiro', 'Pica 60 vetas de Zafiro', 'veta', 'zafiro', 60, 'facil', 1),
    ('opalo', 'Pica 40 vetas de Opalo', 'veta', 'opalo', 40, 'media', 2),
    ('onix', 'Pica 40 vetas de Onix', 'veta', 'onix', 40, 'media', 2),
    ('cristal', 'Pica 200 Cristales Astrales', 'veta', 'cristal_caverna', 200, 'media', 2),
    ('geoda', 'Pica 15 Geodas Estelares', 'veta', 'geoda_estelar', 15, 'dificil', 3),
    ('golems', 'Mata 25 golems de cristal', 'matar', 'golem', 25, 'facil', 1),
    ('aranas', 'Mata 20 aranas de cristal', 'matar', 'arana', 20, 'facil', 1),
    ('corazon', 'Mata 15 mobs en el Corazon', 'matar', 'corazon', 15, 'media', 2),
    ('jefe', 'Derrota a un guardian de zona', 'jefe', 'any', 1, 'dificil', 3),
]

# ------------------------------------------------------------------ mobs (MythicMobs; vida base x tier en mob/roll)
# id: (nombre, tipo, modelo, escala, color de tinte o '', vida, dano, velocidad, zonas, clase)
MOBS = {
    'astral_cav_golem_amatista': ('&5Golem de Amatista', 'ZOMBIE', 'astral_golem_cristal', 1.6, '', 34, 6, 0.24, ['amatista'], 'golem'),
    'astral_cav_golem_jade': ('&aGolem de Jade', 'ZOMBIE', 'astral_golem_bosque', 1.6, '', 34, 6, 0.24, ['jade'], 'golem'),
    'astral_cav_golem_rubi': ('&cGolem de Rubi', 'ZOMBIE', 'astral_golem_cristal', 1.6, 'FF5A5A', 34, 7, 0.24, ['rubi'], 'golem'),
    'astral_cav_golem_zafiro': ('&9Golem de Zafiro', 'ZOMBIE', 'astral_golem_hielo', 1.6, '', 34, 6, 0.24, ['zafiro'], 'golem'),
    'astral_cav_golem_onix': ('&8Golem de Onix', 'ZOMBIE', 'astral_golem_cristal', 1.8, '4A4060', 40, 7, 0.25, ['corazon'], 'golem'),
    'astral_cav_arana': ('&dArana de Cristal', 'ZOGLIN', 'astral_arana', 1.2, 'D9A8FF', 28, 6, 0.32,
                         ['amatista', 'jade', 'rubi', 'zafiro', 'corazon'], 'arana'),
}
# Mini jefe por zona: id: (nombre, modelo, escala, tinte, zona, barra, [(gema, calidad, chance)])
JEFES = {
    'astral_cav_jefe_amatista': ('&5&lGuardian de Amatista', 'astral_golem_cristal', 3.0, '', 'amatista', 'PURPLE',
                                 [('amatista', 2, 1.0), ('amatista', 3, 0.35), ('azar', 2, 0.5)]),
    'astral_cav_jefe_jade': ('&a&lGuardian de Jade', 'astral_golem_bosque', 3.0, '', 'jade', 'GREEN',
                             [('jade', 2, 1.0), ('jade', 3, 0.35), ('azar', 2, 0.5)]),
    'astral_cav_jefe_rubi': ('&c&lGuardian de la Forja', 'astral_golem_cristal', 3.0, 'FF4A3A', 'rubi', 'RED',
                             [('rubi', 2, 1.0), ('topacio', 2, 0.6), ('rubi', 3, 0.3), ('topacio', 3, 0.2)]),
    'astral_cav_jefe_zafiro': ('&9&lGuardian del Lago', 'astral_golem_hielo', 3.0, '', 'zafiro', 'BLUE',
                               [('zafiro', 2, 1.0), ('zafiro', 3, 0.35), ('azar', 2, 0.5)]),
    'astral_cav_jefe_corazon': ('&8&lCorazón de Ónix', 'astral_golem_cristal', 3.6, '2E2840', 'corazon', 'WHITE',
                                [('onix', 2, 1.0), ('opalo', 2, 1.0), ('onix', 3, 0.4), ('opalo', 3, 0.4)]),
}
PERFECTA_JEFE, ESTELAR_JEFE = 0.05, 0.005   # 20/11: chance por guardian (se reparte entre sus gemas)
VIDA_JEFE = 500                  # vida en MythicMobs; la real la pone cavernas/jefe/<t>: 25 x VIDA_REF (jefe del mundo)
DANO_JEFE = 12
MOBS_CERCA = 5                   # mobs propios alrededor de cada jugador (32 bloques)
MOBS_TOPE = 60                   # en todo el mundo
JEFE_CADA_SEG = 60               # cada cuanto se intenta un mini jefe por zona
JEFE_PROB = 0.25
JEFE_ESPERA_MIN = 8              # minutos entre un jefe muerto y el siguiente de la misma zona


# ------------------------------------------------------------------ cuenta de plata por hora (documentada)
# Densidad medida en Paper (tools/probar_cavernas_paper.py, /cavernas medir 10 = 100 chunks, franja de 6 bloques
# de piso/paredes/techo): Cristal 0,78 %, Geoda 0,018 %, gemas 0,19 % de los bloques solidos.
DENSIDAD = {'cristal_caverna': 0.0078, 'geoda_estelar': 0.00018}
# Dos formas de jugar (la mas rentable manda el precio):
#  a ciegas: taladro 2x2 a ~1 golpe/s => 14.400 bloques/h, se vende lo que salga.
#  buscando vetas a la vista (lo normal en una caverna): ~800 Cristales/h y ~15 Geodas/h (caminar, encontrar, picar).
BLOQUES_HORA = 14_400
SELECTIVO_HORA = {'cristal_caverna': 800, 'geoda_estelar': 15}


def plata_hora(modo='selectivo'):
    """Plata por hora vendiendo lo picado: 'selectivo' (buscando vetas) o 'ciegas' (picando todo)."""
    p = E.CAVERNAS_PRECIO
    if modo == 'ciegas':
        return BLOQUES_HORA * sum(DENSIDAD[k] * p[k] for k in p)
    return sum(SELECTIVO_HORA[k] * p[k] for k in p)


# ------------------------------------------------------------------ datapack
def _txt(text, color='gray', **kw):
    d = {'text': text, 'color': color, 'italic': False}
    d.update(kw)
    return d


def _estado(nota):
    return {'instrument': INSTRUMENTO, 'note': str(nota)}


def _taladro_ok():
    """match_tool: taladro Astral de tier DRILL_TIER o mas (a mano o en area)."""
    return {'condition': 'minecraft:any_of', 'terms': [
        {'condition': 'minecraft:match_tool', 'predicate': {'predicates': {
            'minecraft:custom_data': '{astral:{tool:"drill",tier:%d}}' % t}}} for t in range(DRILL_TIER, 11)]}


POLVO = {'condition': 'minecraft:entity_properties', 'entity': 'this', 'predicate': {'nbt': '{Tags:["cav.polvo"]}'}}


def tabla_note_block(files):
    """Agrega las vetas a la tabla del bloque de nota (despues de Asura y del Oceano)."""
    path = 'data/minecraft/loot_table/blocks/note_block.json'
    table = json.loads(files[path])
    pools = []
    for t in G.TIPOS:
        for honda in (False, True):
            nota = nota_gema(t, honda)
            for polvo in (False, True):
                pesos = CALIDAD[('honda' if honda else 'normal') + ('_polvo' if polvo else '')]
                cond = [{'condition': 'minecraft:block_state_property', 'block': 'minecraft:note_block',
                         'properties': _estado(nota)}, _taladro_ok(),
                        POLVO if polvo else {'condition': 'minecraft:inverted', 'term': POLVO}]
                pools.append({'rolls': 1, 'conditions': cond, 'entries': [
                    {'type': 'minecraft:loot_table', 'value': f'{NS}:item/{G.item_id(t, q)}', 'weight': w}
                    for q, w in enumerate(pesos, 1) if w]})
    for iid, nota in MENAS.items():
        pools.append({'rolls': 1, 'conditions': [
            {'condition': 'minecraft:block_state_property', 'block': 'minecraft:note_block', 'properties': _estado(nota)},
            _taladro_ok()], 'entries': [{'type': 'minecraft:loot_table', 'value': f'{NS}:item/{iid}',
                                         'functions': [{'function': 'minecraft:set_count', 'count': 1}]}]})
    table['pools'] = pools + table['pools']
    # El bloque de nota comun no cae si es una veta (fuera de las Cavernas AstralCavernas devuelve el bloque).
    for pool in table['pools']:
        conds = pool.get('conditions', [])
        if any(c.get('condition') == 'minecraft:inverted' and c.get('term', {}).get('block') == 'minecraft:note_block'
               for c in conds):
            pool['conditions'] = conds + [{'condition': 'minecraft:inverted', 'term': {
                'condition': 'minecraft:block_state_property', 'block': 'minecraft:note_block', 'properties': _estado(n)}}
                for n in NOTAS]
            break
    else:
        raise AssertionError('no encontre la entrada comun del bloque de nota')
    files[path] = json.dumps(table, ensure_ascii=False, indent=1)


def tool_mine_lines():
    """tool/mine (taladro en area): vetas fuera de las Cavernas se borran sin soltar nada; adentro piden
    taladro tier 4+ y suman al conteo de comisiones (puntaje cav.n<nota>, lo lee AstralCavernas)."""
    ok = ' '.join(f'unless items entity @s weapon.mainhand *[minecraft:custom_data~{{astral:{{tool:"drill",tier:{t}}}}}]'
                  for t in range(DRILL_TIER, 11))
    out = []
    for n in NOTAS:
        st = f'minecraft:note_block[instrument={INSTRUMENTO},note={n}]'
        out += [f'execute unless dimension minecraft:{WORLD} if block ~ ~ ~ {st} run return run setblock ~ ~ ~ minecraft:air',
                f'execute if block ~ ~ ~ {st} {ok} run return 0',
                f'execute if block ~ ~ ~ {st} run scoreboard players add @s cav.n{n} 1']
    return out


def register(put, fn, add_item, txt):
    """build.py: items, funciones y objetivos. La tabla del bloque de nota va en tabla_note_block (al final)."""
    for iid, (nombre, color, desc) in ITEMS.items():
        add_item(iid, 'minecraft:paper', nombre, color, [txt(desc), txt('Cavernas de Cristal Astrales', 'dark_gray')],
                 {'type': 'cavernas'}, model=f'{NS}:cavernas/{iid}', glint=iid == 'geoda_estelar', kind='cavernas')
    fn('cavernas/load', [f'scoreboard objectives add cav.n{n} dummy' for n in NOTAS])
    # Mini jefes: vida de jefe del mundo del tier de su zona (mob/roll no los toca: llevan astral.seen).
    from escala import VIDA_REF
    for t in (TIER, TIER_CORAZON):
        fn(f'cavernas/jefe/{t}', [f'attribute @s minecraft:max_health base set {25 * VIDA_REF[t]}',
                                  'data modify entity @s Health set value 1.0E30f', f'scoreboard players set @s astral.mt {t}',
                                  f'tag @s add astral.mt{t}', 'tag @s add astral.seen', 'tag @s add ad.boss.scaled'])


def mob_roll_corazon():
    """Linea para mob/roll: dentro del Corazon el tier fijo es 5 (despues del TIER_FIJO del mundo)."""
    r = CORAZON_R
    return (f'execute if dimension minecraft:{WORLD} if entity @s[x={-r},z={-r},y=-64,dx={2 * r},dz={2 * r},dy=200] '
            f'run scoreboard players set #mt astral.tmp {TIER_CORAZON}')


# ------------------------------------------------------------------ MythicMobs
def mythic_yaml():
    from mobs.mythic import astral_drop
    L = ['# Generado por datapack-src/cavernas.py (plan E5 / 7e). Mobs de las Cavernas de Cristal Astrales.',
         '# Los aparece AstralCavernas (no hay apariciones naturales en el mundo). Vida base x tier: mob/roll.', '']

    def comun(mid, nombre, tipo, modelo, escala, tinte, vida, dano, vel, jefe=None):
        out = [f'{mid}:', f'  Type: {tipo}', f"  Display: '{nombre}'", f'  Health: {vida}', f'  Damage: {dano}',
               '  Options:', '    Silent: true', '    PreventOtherDrops: true', '    PreventSunburn: true',
               '    PreventRandomEquipment: true', '    PreventItemPickup: true', f'    MovementSpeed: {vel}',
               f"    Despawn: {'false' if jefe else 'true'}", '    FollowRange: 40']
        if jefe:
            out += ['    KnockbackResistance: 0.8']
        out += ['  AIGoalSelectors:', '  - clear', '  - meleeattack', '  - randomstroll', '  - lookatplayers',
                '  AITargetSelectors:', '  - clear', '  - attacker', '  - players']
        if jefe:
            out += ['  BossBar:', '    Enabled: true', f"    Title: '{nombre}'", '    Range: 48', f'    Color: {jefe}',
                    '    Style: SEGMENTED_10']
        sk = [f'- model{{m={modelo};s={escala}}} @self ~onSpawn', f'- model{{m={modelo};s={escala}}} @self ~onLoad']
        if tinte:
            sk += [f'- tint{{c={tinte}}} @self ~onSpawn', f'- tint{{c={tinte}}} @self ~onLoad']
        sk += ['- state{s=attack} @self ~onAttack', '- skill{s=AST_MUERTE} @self ~onDeath',
               '- sound{s=block.amethyst_block.hit;v=0.8} @self ~onDamaged',
               '- sound{s=block.amethyst_cluster.break;v=1;p=0.7} @self ~onDeath']
        return out, sk

    for mid, (nombre, tipo, modelo, escala, tinte, vida, dano, vel, zonas, clase) in MOBS.items():
        out, sk = comun(mid, nombre, tipo, modelo, escala, tinte, vida, dano, vel)
        sk += [f'- addtag{{tag=cav.mob}} @self ~onSpawn', f'- addtag{{tag=cav.{clase}}} @self ~onSpawn',
               # tier fijo de las Cavernas (4; 5 en el Corazon): la vida y la plata salen del tier
               '- command{c="execute as <caster.uuid> at @s run function astral:mob/roll"} @self ~onSpawn',
               '- skill{s=AST_PLATA_HOSTIL} @self ~onDeath ?~isplayer']
        sk += astral_drop('cristal_caverna', 0.35) + astral_drop('polvo_cristal', 0.02)
        L += out + ['  Skills:'] + ['  ' + s for s in sk] + ['']
    for mid, (nombre, modelo, escala, tinte, zona, barra, drops) in JEFES.items():
        out, sk = comun(mid, nombre, 'ZOMBIE', modelo, escala, tinte, VIDA_JEFE, DANO_JEFE, 0.27, jefe=barra)
        t = TIER_CORAZON if zona == 'corazon' else TIER
        sk += ['- addtag{tag=cav.mob} @self ~onSpawn', '- addtag{tag=cav.jefe} @self ~onSpawn',
               f'- command{{c="execute as <caster.uuid> run function astral:cavernas/jefe/{t}"}} @self ~onSpawn',
               '- skill{s=AST_PLATA_JEFE} @self ~onDeath ?~isplayer',
               '- skill{s=AST_JEFE_SALTO} @target ~onTimer:40']
        propias = list(dict.fromkeys(g for g, _, _ in drops if g != 'azar'))
        drops = list(drops) + [(g, 4, round(PERFECTA_JEFE / len(propias), 4)) for g in propias] + \
            [(g, 5, round(ESTELAR_JEFE / len(propias), 4)) for g in propias]
        for gema, q, ch in drops:
            if gema == 'azar':
                sk += [f'- command{{c="astralgema dar <trigger.name> azar {q} 1"}} @self ~onDeath ?~isplayer {ch}']
            else:
                sk += astral_drop(G.item_id(gema, q), ch)
        sk += astral_drop('polvo_cristal', 1.0, 2) + astral_drop('geoda_estelar', 0.5)
        L += out + ['  Skills:'] + ['  ' + s for s in sk] + ['']
    return '\n'.join(L)


# ------------------------------------------------------------------ menus y comandos
def aviso_menu():
    """Ventana de entrada (arte del dueno 19/11, ventanas_19_11.py): ilustracion + ENTRAR / VOLVER."""
    import ventanas_19_11 as V
    lore = ['&7Una caverna enorme llena de vetas de gemas.', '&7Las gemas se engarzan en el Herrero (GEMAS).', '',
            f'&7Monstruos &ftier {TIER}&7; el Corazon es &ftier {TIER_CORAZON}&7.',
            '&7Para entrar: haber ganado la &fTumba &7o llevar equipo &ftier 4&7.',
            '&7Las vetas se pican con &ftaladro de Rubi &7o mejor.', '',
            f'&8Las cavernas se regeneran cada {REGENERAR_HORAS // 24} dias.', '&8No dejes cosas tuyas ahi.']
    items = {}
    for k, slot in enumerate(s for r in range(4) for s in range(r * 9, r * 9 + 6)):
        items[f'info_{slot}'] = dict(material='PAPER', slot=slot, item_model='astral:viajes/blank',
                                     display_name='&d&lCavernas de Cristal', lore=lore)
    for t, slot in enumerate((15, 16, 17)):
        items[f'entrar_{t}'] = dict(material='PAPER', slot=slot, item_model=f'astral:ventanas1911/entrar_{t}',
                                    display_name='&a&lEntrar', lore=['&7Al campamento de la entrada.'],
                                    click_commands=['[close]', '[player] cavernas entrar<delay=3>'])
    for t, slot in enumerate((24, 25, 26)):
        items[f'volver_{t}'] = dict(material='PAPER', slot=slot, item_model=f'astral:ventanas1911/volver_{t}',
                                    display_name='&c&lVolver', lore=['&7Volver a los portales.'],
                                    click_commands=['[openguimenu] portales'])
    return dict(menu_title=V.titulo('cavernas_aviso'), size=36, items=items)


def portales_button():
    return {'material': 'AMETHYST_CLUSTER', 'slot': 48, 'display_name': '&d&lCavernas de Cristal',
            'lore': ['&7Vetas de gemas para la Reforja.', '&7Equipo tier 4 o Tumba ganada.', '', '&eClic para ver el aviso.'],
            'click_commands': ['[openguimenu] cavernas_aviso']}


def commands():
    w = WORLD
    return '\n'.join([
        '# Cavernas de Cristal (cavernas.py). Con AstralCavernas instalado y el server encendido:',
        f'mv create {w} normal -g AstralCavernas',
        f'execute in minecraft:{w} run gamerule minecraft:advance_time false',
        f'execute in minecraft:{w} run gamerule minecraft:advance_weather false',
        f'execute in minecraft:{w} run gamerule minecraft:spawn_monsters false',
        f'execute in minecraft:{w} run gamerule minecraft:spawn_mobs false',
        f'execute in minecraft:{w} run worldborder center 0 0',
        f'execute in minecraft:{w} run worldborder set {RADIO * 2}',
        f'rg flag -w {w} __global__ pvp deny',
        '# (opcional) despues de recorrerlo: cavernas plantilla',
    ]) + '\n'


def icono_comision(c):
    """Modelo del icono de una comision en el tablero."""
    tipo, obj = c[2], c[3]
    if tipo == 'veta':
        return f'{NS}:gemas/{obj}_2' if obj in G.TIPOS else f'{NS}:cavernas/{obj}'
    if tipo == 'jefe':
        return f'{NS}:gemas/onix_5'
    return f"{NS}:ventanas1911/" + {'golem': 'cristal_violeta', 'arana': 'cristal_azul'}.get(obj, 'cristal_rojo')


def config():
    zonas = {k: dict(nombre=v[0], color=v[1], gemas=v[2]) for k, v in ZONAS.items()}
    mobs = {k: dict(zonas=v[8], clase=v[9]) for k, v in MOBS.items()}
    jefes = {k: dict(zona=v[4], nombre=v[0]) for k, v in JEFES.items()}
    notas = {**{f'gema_{t}': nota_gema(t) for t in G.TIPOS}, **{f'gema_{t}_honda': nota_gema(t, True) for t in G.TIPOS},
             **MENAS}
    return dict(mundo=WORLD, radio=RADIO, **{'regenerar-cada-horas': REGENERAR_HORAS, 'avisos-minutos': list(AVISOS_MIN),
                'proxima-regeneracion': 0}, corazon=CORAZON_R, campamento=list(CAMPAMENTO), **{'camp-y': CAMP_Y},
                **{'taladro-tier': DRILL_TIER, 'polvo-minutos': POLVO_MIN, 'mobs-cerca': MOBS_CERCA, 'mobs-tope': MOBS_TOPE,
                   'jefe-cada-seg': JEFE_CADA_SEG, 'jefe-prob': JEFE_PROB, 'jefe-espera-min': JEFE_ESPERA_MIN,
                   'permiso-tumba': 'astral.fragmento.arena'},
                zonas=zonas, notas=notas, mobs=mobs, jefes=jefes,
                precios=dict(E.CAVERNAS_PRECIO),
                **{'titulo-comisiones': __import__('ventanas_19_11').titulo('comisiones')},
                comisiones=[dict(clave=c[0], texto=c[1], tipo=c[2], objetivo=c[3], cantidad=c[4],
                                 plata=E.CAVERNAS_COMISION[c[5]], polvo=c[6], icono=icono_comision(c)) for c in COMISIONES])


PLUGIN_YML = f"""name: AstralCavernas
version: {VERSION}
main: astral.AstralCavernas
api-version: '26.1.2'
load: STARTUP
softdepend: [Multiverse-Core, MythicMobs, Essentials]
commands:
  cavernas:
    description: Cavernas de Cristal (entrar, comisiones, vender, estado; admin regenerar, plantilla, jefe, medir)
permissions:
  astral.cavernas.admin:
    default: op
  astral.cavernas.editar:
    default: op
"""


def build_plugin(jdk, server):
    import yaml
    jdk, server = Path(jdk), Path(server)
    classes = ROOT / '.local' / 'cavernas-classes'
    classes.mkdir(parents=True, exist_ok=True)
    deps = [*server.joinpath('libraries').rglob('*.jar'), *server.joinpath('versions').rglob('*.jar')]
    javac = [str(jdk / ('java.exe' if os.name == 'nt' else 'java')), '-m', 'jdk.compiler/com.sun.tools.javac.Main']
    subprocess.run([*javac, '-encoding', 'UTF-8', '-source', '25', '-target', '25', '-nowarn', '-classpath',
                    os.pathsep.join(map(str, deps)), '-d', str(classes), str(HERE / 'runtime' / 'AstralCavernas.java')], check=True)
    OUT.mkdir(parents=True, exist_ok=True)
    dest = OUT / 'AstralCavernas.jar'
    with zipfile.ZipFile(dest, 'w', zipfile.ZIP_DEFLATED) as z:
        for p in sorted((classes / 'astral').glob('AstralCavernas*.class')):
            z.writestr(zipfile.ZipInfo('astral/' + p.name, STAMP), p.read_bytes())
        z.writestr(zipfile.ZipInfo('plugin.yml', STAMP), PLUGIN_YML)
        z.writestr(zipfile.ZipInfo('config.yml', STAMP), yaml.safe_dump(config(), sort_keys=False, allow_unicode=True))
    return dest


def generate():
    import yaml
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'config.yml').write_text(yaml.safe_dump(config(), sort_keys=False, allow_unicode=True), encoding='utf-8')
    (OUT / 'comandos.txt').write_text(commands(), encoding='utf-8')
    mm = ROOT / 'build' / 'mythicmobs' / 'mobs'
    mm.mkdir(parents=True, exist_ok=True)
    (mm / 'cavernas.yml').write_text(mythic_yaml(), encoding='utf-8')
    menus = ROOT / 'build' / 'menus' / 'DeluxeMenus' / 'gui_menus'
    menus.mkdir(parents=True, exist_ok=True)
    (menus / 'cavernas_aviso.yml').write_text(json.dumps(aviso_menu(), ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'cavernas: {len(NOTAS)} vetas, {len(MOBS)} mobs, {len(JEFES)} jefes -> {OUT}')
    return ['cavernas_aviso']


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--jdk')
    ap.add_argument('--server', default=str(ROOT / '.local' / 'testsrv'))
    a = ap.parse_args()
    generate()
    if a.jdk:
        print(build_plugin(a.jdk, a.server))


# ------------------------------------------------------------------ arte del pack (propio, sin texturas vanilla)
def _roca(oscura, semilla):
    """Roca 32x32 dibujada por codigo (gris; mas oscura para las vetas hondas)."""
    import random
    from PIL import Image
    rng = random.Random(semilla)
    im = Image.new('RGBA', (32, 32))
    px = im.load()
    base = (58, 56, 66) if oscura else (112, 110, 118)
    for y in range(32):
        for x in range(32):
            v = rng.randint(-14, 14) + (8 if (x // 4 + y // 4) % 3 == 0 else 0)
            px[x, y] = tuple(max(0, min(255, c + v)) for c in base) + (255,)
    return im


def _incrustar(roca, gema, lugares=((3, 4, 12), (17, 2, 11), (9, 17, 13), (21, 18, 10))):
    from PIL import Image
    for x, y, lado in lugares:
        roca.alpha_composite(gema.resize((lado, lado), Image.Resampling.LANCZOS), (x, y))
    return roca


def _gema(tipo, q):
    from PIL import Image
    return Image.open(G.TEX / f'{tipo}_{q}.png').convert('RGBA')


def _tenir(im, rgb, fuerza=0.55):
    from PIL import Image
    capa = Image.new('RGBA', im.size, rgb + (255,))
    out = Image.blend(im.convert('RGBA'), capa, fuerza)
    out.putalpha(im.getchannel('A'))
    return out


ARTE = HERE / 'pack-source' / 'arte-19-11' / 'cavernas'   # recortes de la referencia del dueno (arte_19_11.py)


def texturas():
    """{nombre: imagen} de bloques (vetas) e items propios de las Cavernas. Usa el arte del dueno si esta;
    si falta alguna pieza, la dibuja provisoria."""
    from PIL import Image, ImageDraw
    out = _texturas_provisorias()
    for nombre in list(out):
        p = ARTE / (nombre.split('/')[1] + '.png')
        if p.exists():
            out[nombre] = Image.open(p).convert('RGBA')
    return out


def _texturas_provisorias():
    from PIL import Image, ImageDraw
    out = {}
    for t in G.TIPOS:
        for honda in (False, True):
            nombre = f'veta_{t}' + ('_honda' if honda else '')
            out['block/' + nombre] = _incrustar(_roca(honda, nota_gema(t, honda)), _gema(t, 3 if honda else 2))
    cristal = _tenir(_gema('amatista', 1), (230, 200, 255), 0.35)
    out['block/veta_cristal_caverna'] = _incrustar(_roca(False, 14), cristal)
    out['block/veta_geoda_estelar'] = _incrustar(_roca(True, 15), _gema('opalo', 3), ((8, 8, 16),))
    out['item/cristal_caverna'] = cristal
    out['item/geoda_estelar'] = _gema('opalo', 4)
    polvo = Image.new('RGBA', (64, 64))
    d = ImageDraw.Draw(polvo)
    d.ellipse((10, 34, 54, 58), fill=(214, 170, 255, 255), outline=(120, 70, 170, 255), width=3)
    d.ellipse((18, 26, 46, 50), fill=(236, 210, 255, 255), outline=(140, 90, 190, 255), width=3)
    for x, y in ((14, 14), (44, 10), (30, 6), (52, 28), (8, 26)):
        d.line((x - 4, y, x + 4, y), fill=(255, 250, 220, 255), width=2)
        d.line((x, y - 4, x, y + 4), fill=(255, 250, 220, 255), width=2)
    out['item/polvo_cristal'] = polvo
    return out


def variantes_note_block():
    """Partes del bloque de nota para las vetas (campana, notas de NOTAS)."""
    nombres = {nota_gema(t, h): f'veta_{t}' + ('_honda' if h else '') for t in G.TIPOS for h in (False, True)}
    nombres.update({n: f'veta_{iid}' for iid, n in MENAS.items()})
    return [{'when': {'instrument': INSTRUMENTO, 'note': str(n)}, 'apply': {'model': f'{NS}:block/cavernas/{nombres[n]}'}}
            for n in NOTAS]


def parchar_note_block(bs):
    """El modelo comun del bloque de nota deja de aplicarse a las vetas (campana 0-15) y se suman sus partes."""
    parts = bs['multipart']
    comun = next(p for p in parts if p['apply'].get('model') == 'minecraft:block/note_block')
    ors = comun['when']['OR']
    instr = next(o for o in ors if set(o) == {'instrument'})
    lista = [i for i in instr['instrument'].split('|') if i != INSTRUMENTO]
    if len(lista) != len(instr['instrument'].split('|')):
        instr['instrument'] = '|'.join(lista)
        # La rama "por nota" era para el banjo (las demas ya entran por instrumento): que no tome la campana.
        for o in ors:
            if set(o) == {'note'}:
                o['instrument'] = 'banjo'
        ors.append({'instrument': INSTRUMENTO, 'note': '|'.join(str(n) for n in range(25) if n not in NOTAS)})
    parts[:] = [p for p in parts if not p['apply'].get('model', '').startswith(f'{NS}:block/cavernas/')] + variantes_note_block()
    return bs


def pack_assets():
    """Texturas, modelos e items de las Cavernas (no incluye el bloque de nota: ver parchar_note_block)."""
    import io
    files = {}
    for nombre, im in texturas().items():
        buf = io.BytesIO(); im.save(buf, 'PNG')
        files[f'assets/{NS}/textures/{nombre.split("/")[0]}/cavernas/{nombre.split("/")[1]}.png'] = buf.getvalue()
        if nombre.startswith('block/'):
            files[f'assets/{NS}/models/block/cavernas/{nombre[6:]}.json'] = json.dumps(
                {'parent': 'minecraft:block/cube_all', 'textures': {'all': f'{NS}:block/cavernas/{nombre[6:]}'}}).encode()
        else:
            files[f'assets/{NS}/models/item/cavernas/{nombre[5:]}.json'] = json.dumps(
                {'parent': 'minecraft:item/generated', 'textures': {'layer0': f'{NS}:item/cavernas/{nombre[5:]}'}}).encode()
            files[f'assets/{NS}/items/cavernas/{nombre[5:]}.json'] = json.dumps(
                {'model': {'type': 'minecraft:model', 'model': f'{NS}:item/cavernas/{nombre[5:]}'}}).encode()
    return files


def previews():
    """build/previews/cavernas_vetas.png: vetas e items a 4x."""
    from PIL import Image
    from escape_menu import text
    tex = texturas()
    hoja = Image.new('RGBA', (8 * 40 + 8, 3 * 40 + 8), '#1d1e20')
    for i, (n, im) in enumerate(sorted(tex.items())):
        hoja.alpha_composite(im.resize((32, 32), Image.Resampling.LANCZOS), (8 + (i % 8) * 40, 8 + (i // 8) * 40))
    p = ROOT / 'build' / 'previews' / 'cavernas_vetas.png'
    p.parent.mkdir(parents=True, exist_ok=True)
    hoja.resize((hoja.width * 3, hoja.height * 3), Image.Resampling.NEAREST).save(p)
    del text
    return p
