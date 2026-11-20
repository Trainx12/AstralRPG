# -*- coding: utf-8 -*-
"""Reforja de gemas (plan E4 / tanda 7d, 19/11/2026). FUENTE UNICA de las gemas.

7 gemas x 5 calidades. Cada gema engarzada es un ENCANTAMIENTO del datapack `astral:gema_<tipo>_<arma|armadura>_<q>`
(q = calidad 1..5). Asi sobrevive a la migracion de items (set_enchantments conserva los encantamientos que no
toca) y se ve sola en el tooltip con su icono, nombre y efecto. Una pieza no puede tener dos gemas del mismo tipo.

Donde se aplica cada efecto (no hay un segundo lugar que lo sume):
  dano                          encantamiento, efecto minecraft:damage (multiplica el golpe del arma)
  vida, velocidades, empuje     encantamiento, atributos (add_multiplied_base: no se multiplican con mejoras/talismanes)
  robo de vida, espinas, dano a elites y jefes   plugin AstralGemas (eventos de dano; tambien en PvP;
                                jefes = barra de jefe de MythicMobs o etiquetas astral.elite / ad.boss.scaled)
  defensa (Opalo armadura)      funcion player/def -> gemas/defensa (despues del Talisman de Roca)
  suerte (Topacio)              funcion drop/give -> gemas/suerte (chance de duplicar un drop Astral)
  plata (Topacio)               AstralGemas deja etiquetas astral.gp0..5 (binario) y astral_economia.sk solo las lee
  mana y critico (Zafiro, Amatista)   plugin AstralGemas (modificadores de AuraSkills, se borran al salir)
Nada de esto corre un comando por baja: el plugin revisa el equipo 1 vez por segundo y lee el arma en cada golpe.

Ranuras por tier del equipo: T1-T3 1, T4-T7 2, T8-T10 3. Costos: economia.py (gema_costo).

Salidas:
  datapack (lo llama build.py: register)            encantamientos, items de gema, funciones gemas/*
  build/gemas/astral_gemas.sk                        ventana "Reforja de gemas", /astralgema, gemas del cofre por nota
  build/gemas/AstralGemas.jar (python gemas.py --jdk <bin>)   mana y critico via AuraSkills
  pack: pack_assets()                                 texturas PNG de las gemas (reemplazables) + modelos

Texturas reemplazables: datapack-src/pack-source/assets/astral/textures/item/gemas/<tipo>_<calidad>.png (16x16).
Si el archivo NO existe se dibuja uno provisorio; si existe, se usa tal cual (no se pisa).
"""
import argparse
import io
import json
import os
import zipfile
from pathlib import Path

import economia as E

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = ROOT / 'build' / 'gemas'
TEX = HERE / 'pack-source' / 'assets' / 'astral' / 'textures' / 'item' / 'gemas'
NS = 'astral'

# ------------------------------------------------------------------ tabla
# tipo: (nombre, genero, color hex, color &)
TIPOS = {
    'rubi': ('Rubí', 'm', '#e0204a', '&c'),
    'zafiro': ('Zafiro', 'm', '#2f6bff', '&9'),
    'jade': ('Jade', 'm', '#2fbf6a', '&a'),
    'topacio': ('Topacio', 'm', '#f2b632', '&6'),
    'amatista': ('Amatista', 'f', '#a35cff', '&5'),
    'opalo': ('Ópalo', 'm', '#b9e6ee', '&b'),
    'onix': ('Ónix', 'm', '#3a3a46', '&8'),
}
TIPOS_ASCII = {'rubi': 'Rubi', 'zafiro': 'Zafiro', 'jade': 'Jade', 'topacio': 'Topacio', 'amatista': 'Amatista',
               'opalo': 'Opalo', 'onix': 'Onix'}
CALIDADES = {1: ('Crudo', 'Cruda'), 2: ('Pulido', 'Pulida'), 3: ('Impecable', 'Impecable'),
             4: ('Perfecto', 'Perfecta'), 5: ('Estelar', 'Estelar')}
CALIDAD_NOMBRE = {q: f for q, (_, f) in CALIDADES.items()}     # "calidad Pulida" (gema es femenino)
VARIANTES = ('arma', 'armadura')

# Efectos: variante -> tipo -> [(stat, (v1..v5))]. El primero es el principal; los que tienen 0 en Cruda..Impecable
# son el efecto secundario chico de Perfecta y Estelar. En armadura los valores son POR PIEZA (4 piezas suman).
EFECTOS = {
    'arma': {
        'rubi': [('dano', (4, 7, 11, 16, 22)), ('vida', (0, 0, 0, 1, 2))],
        'zafiro': [('mana', (4, 7, 11, 16, 22)), ('mana_regen', (5, 8, 12, 18, 25)), ('dano', (0, 0, 0, 2, 3))],
        'jade': [('vel_ataque', (3, 5, 8, 11, 15)), ('vel_mov', (0, 0, 0, 1, 2))],
        'topacio': [('plata', (5, 8, 12, 17, 25)), ('suerte', (0, 0, 0, 1, 2))],
        'amatista': [('crit', (2, 3, 5, 7, 10)), ('crit_dano', (0, 0, 0, 5, 10))],
        'opalo': [('dano_jefes', (6, 10, 15, 21, 28)), ('dano', (0, 0, 0, 2, 3))],
        'onix': [('robo', (1, 1.25, 1.5, 2, 2.5)), ('vida', (0, 0, 0, 1, 2))],
    },
    'armadura': {
        'rubi': [('vida', (1.5, 2.5, 3.5, 5, 6.5)), ('dano_base', (0, 0, 0, 1, 2))],
        'zafiro': [('mana_regen', (3, 5, 8, 11, 15)), ('mana', (0, 0, 0, 2, 4))],
        'jade': [('vel_mov', (1, 1.5, 2, 2.5, 3.5)), ('vel_ataque', (0, 0, 0, 1, 2))],
        'topacio': [('suerte', (1, 2, 3, 4, 5)), ('plata', (0, 0, 0, 2, 3))],
        'amatista': [('crit_dano', (3, 5, 7, 10, 14)), ('crit', (0, 0, 0, 0.5, 1))],
        'opalo': [('defensa', (3, 5, 8, 11, 15)), ('empuje', (0, 0, 0, 5, 10))],
        'onix': [('espinas', (0.2, 0.35, 0.5, 0.7, 1.0)), ('vida', (0, 0, 0, 1, 2))],
    },
}
# Robo de vida (Onix arma): 40% de chance por golpe de curar el % de TU vida maxima; como mucho una cura cada
# medio segundo (si no, los cuchillos de 3 golpes por segundo serian inmortales). Ver balance en la entrega.
ROBO_PROB = 0.40
ROBO_ESPERA_TICKS = 10
ESPINAS_PROB = 0.10                # chance por golpe recibido y por pieza (tambien en PvP)
ESPINAS_JEFES = 0.5                # contra elites y jefes devuelve la mitad
# Elites y jefes: estas etiquetas (build.py: mob/elite_chance y mob/jefe_mundo) o un mob de MythicMobs con barra de jefe
# (todos los jefes de mazmorra, de evento y del mundo).
TAGS_JEFES = ('astral.elite', 'ad.boss.scaled')
# Texto de cada stat (el valor va con formato %). 'arma' / 'armadura' cambian solo la palabra.
TEXTO = {
    'dano': '+{v}% daño', 'dano_base': '+{v}% daño del arma', 'vida': '+{v}% vida máxima',
    'mana': '+{v}% maná máximo', 'mana_regen': '+{v}% regeneración de maná',
    'vel_ataque': '+{v}% velocidad de ataque', 'vel_mov': '+{v}% velocidad',
    'plata': '+{v}% plata por baja', 'suerte': '+{v}% de duplicar drops Astral',
    'crit': '+{v}% prob. crítica', 'crit_dano': '+{v}% daño crítico',
    'dano_jefes': '+{v}% daño a élites y jefes', 'defensa': '+{v}% Defensa de la pieza',
    'empuje': '+{v}% resistencia al empuje', 'robo': '40% de curar {v}% de tu vida al golpear',
    'espinas': 'devuelve {v}% de la vida del atacante',
}
# Rasgos de AuraSkills (plugin AstralGemas): stat -> (rasgo, operacion)
AURASKILLS = {'mana': ('max_mana', 'ADD_PERCENT'), 'mana_regen': ('mana_regen', 'ADD_PERCENT'),
              'crit': ('crit_chance', 'ADD'), 'crit_dano': ('crit_damage', 'ADD')}

# Gemas en el cofre de mazmorra segun la nota (pedido del dueno 19/11: queda fijo, ademas de las Cavernas).
# Chance de una gema por cofre; con A o S la calidad usa la tabla del tier siguiente (DROP_BONUS_TIER).
DROP_COFRE = {'F': 0, 'D': 0.05, 'C': 0.10, 'B': 0.18, 'A': 0.30, 'S': 0.45}
DROP_BONUS_TIER = {'A': 1, 'S': 1}
# Calidad segun el tier de la mazmorra: pesos de Cruda, Pulida, Impecable, Perfecta, Estelar.
DROP_CALIDAD = {1: (1000, 0, 0, 0, 0), 2: (1000, 0, 0, 0, 0), 3: (800, 200, 0, 0, 0), 4: (598, 350, 50, 2, 0),
                5: (400, 450, 138, 10, 2)}   # por mil; 20/11: Perfecta y Estelar muy raras


def ranuras(tier):
    return 1 if tier <= 3 else 2 if tier <= 7 else 3


def fmt(v):
    return (f'{v:g}').replace('.', ',')


def nombre(tipo, q, ascii_=False):
    n, genero, _, _ = TIPOS[tipo]
    if ascii_:
        n = TIPOS_ASCII[tipo]
    return f"{n} {CALIDADES[q][0 if genero == 'm' else 1]}"


def efectos(variante, tipo, q):
    """[(stat, valor)] activos de esa gema en esa calidad (sin los ceros)."""
    return [(s, vals[q - 1]) for s, vals in EFECTOS[variante][tipo] if vals[q - 1]]


def texto_efectos(variante, tipo, q):
    return ', '.join(TEXTO[s].format(v=fmt(v)) for s, v in efectos(variante, tipo, q))


def ench_id(tipo, variante, q):
    return f'gema_{tipo}_{variante}_{q}'


def item_id(tipo, q):
    return f'gema_{tipo}_{q}'


def todas():
    return [(t, q) for t in TIPOS for q in CALIDADES]


# ------------------------------------------------------------------ datapack
def _txt(text, color='gray', **kw):
    d = {'text': text, 'color': color, 'italic': False}
    d.update(kw)
    return d


def _ench_json(tipo, variante, q):
    nombre_t, _, color, _ = TIPOS[tipo]
    slot = 'mainhand' if variante == 'arma' else 'armor'
    desc = _txt('◆ ', color, extra=[_txt(nombre(tipo, q), color), _txt(' · ' + texto_efectos(variante, tipo, q), 'gray')])
    eff = {}
    attrs = []
    rid = f'{NS}:{ench_id(tipo, variante, q)}'
    attr_map = {'vida': 'minecraft:max_health', 'vel_ataque': 'minecraft:attack_speed',
                'vel_mov': 'minecraft:movement_speed', 'dano_base': 'minecraft:attack_damage'}
    for s, v in efectos(variante, tipo, q):
        if s in attr_map:
            attrs.append({'id': f'{rid}.{s}', 'attribute': attr_map[s], 'operation': 'add_multiplied_base',
                          'amount': round(v / 100, 5)})
        elif s == 'empuje':
            attrs.append({'id': f'{rid}.{s}', 'attribute': 'minecraft:knockback_resistance', 'operation': 'add_value',
                          'amount': round(v / 100, 5)})
        elif s == 'dano':
            eff.setdefault('minecraft:damage', []).append(
                {'effect': {'type': 'minecraft:multiply', 'factor': round(1 + v / 100, 5)}})
        # mana, crit, robo, espinas, dano_jefes, plata: plugin AstralGemas. suerte y defensa: funciones del datapack.
    if attrs:
        eff['minecraft:attributes'] = attrs
    return {'description': desc, 'supported_items': f'#{NS}:sin_mesa', 'weight': 1, 'max_level': 1,
            'min_cost': {'base': 999, 'per_level_above_first': 0}, 'max_cost': {'base': 999, 'per_level_above_first': 0},
            'anvil_cost': 40, 'slots': [slot], 'effects': eff}


def _ench_tag(ids):
    return {'values': [f'{NS}:{i}' for i in ids]}


def _has(slot, ref):
    return f'items entity @s {slot} *[minecraft:enchantments~[{{enchantments:"{ref}"}}]]'


def _con_stat(variante, stat):
    """[(tipo, q, valor)] de todas las gemas que dan ese stat en esa variante."""
    return [(t, q, vals[q - 1]) for t in TIPOS for s, vals in EFECTOS[variante][t] if s == stat
            for q in CALIDADES if vals[q - 1]]


ARMOR_SLOTS = ('armor.head', 'armor.chest', 'armor.legs', 'armor.feet')
TAGS_VER = (['asgem.valid', 'asgem.arma', 'asgem.armadura', 'asgem.lleno', 'asgem.r1', 'asgem.r2', 'asgem.r3']
            + [f'asgem.t{t}' for t in range(1, 11)] + [f'asgem.has.{t}' for t in TIPOS]
            + [f'asgem.q.{t}.{q}' for t, q in todas()])


def register(put, fn, add_item, txt, items_kind='gema'):
    """build.py: items de gema, encantamientos, etiquetas y funciones gemas/*."""
    # Items de gema (se apilan; custom_data astral:{type:"gema",gema:"rubi",q:3})
    for t, q in todas():
        nombre_t, _, color, _ = TIPOS[t]
        lore = [txt(f'Gema de calidad {CALIDAD_NOMBRE[q]}', color),
                txt('En arma: ' + texto_efectos('arma', t, q), 'gray'),
                txt('En armadura: ' + texto_efectos('armadura', t, q) + ' (por pieza)', 'gray'),
                txt('Se engarza en la Reforja de gemas (Herrero).', 'dark_gray')]
        add_item(item_id(t, q), 'minecraft:paper', nombre(t, q), color, lore,
                 {'type': 'gema', 'gema': t, 'q': q}, model=f'{NS}:gemas/{t}_{q}', glint=q >= 4, kind=items_kind)
    # Encantamientos y etiquetas
    for t in TIPOS:
        for v in VARIANTES:
            for q in CALIDADES:
                put(f'data/{NS}/enchantment/{ench_id(t, v, q)}.json', _ench_json(t, v, q))
            put(f'data/{NS}/tags/enchantment/gema_{t}_{v}.json', _ench_tag(ench_id(t, v, q) for q in CALIDADES))
        put(f'data/{NS}/tags/enchantment/gema_{t}.json', _ench_tag(ench_id(t, v, q) for v in VARIANTES for q in CALIDADES))
    put(f'data/{NS}/tags/enchantment/gemas.json', _ench_tag(ench_id(t, v, q) for t in TIPOS for v in VARIANTES for q in CALIDADES))
    for stat in ('suerte',):
        for v in VARIANTES:
            put(f'data/{NS}/tags/enchantment/gema_{stat}_{v}.json',
                _ench_tag(ench_id(t, v, q) for t, q, _ in _con_stat(v, stat)))

    # --- Ventana: ver el equipo (en la mano) y la gema (en la mano). Skript lee las etiquetas.
    ver = [f'tag @s remove {x}' for x in TAGS_VER] + [
        'execute if items entity @s weapon.mainhand *[minecraft:custom_data~{astral:{type:"armor"}}] run tag @s add asgem.armadura',
        'execute if items entity @s weapon.mainhand *[minecraft:custom_data~{astral:{type:"weapon"}}] run tag @s add asgem.arma',
        'execute if items entity @s weapon.mainhand *[minecraft:custom_data~{astral:{type:"staff"}}] run tag @s add asgem.arma',
        'execute unless entity @s[tag=asgem.arma] unless entity @s[tag=asgem.armadura] run return 0']
    ver += [f'execute if items entity @s weapon.mainhand *[minecraft:custom_data~{{astral:{{tier:{t}}}}}] run tag @s add asgem.t{t}'
            for t in range(1, 11)]
    ver += [f'execute if entity @s[tag=asgem.t{t}] run tag @s add asgem.r{ranuras(t)}' for t in range(1, 11)]
    ver += ['execute unless entity @s[tag=asgem.r1] unless entity @s[tag=asgem.r2] unless entity @s[tag=asgem.r3] run return 0',
            'tag @s add asgem.valid', 'scoreboard players set #gn astral.tmp 0']
    for t in TIPOS:
        ver.append(f'execute if {_has("weapon.mainhand", "#" + NS + ":gema_" + t)} run function {NS}:gemas/gui/ver_{t}')
        fn(f'gemas/gui/ver_{t}', ['scoreboard players add #gn astral.tmp 1', f'tag @s add asgem.has.{t}'] + [
            f'execute if {_has("weapon.mainhand", NS + ":" + ench_id(t, v, q))} run tag @s add asgem.q.{t}.{q}'
            for v in VARIANTES for q in CALIDADES])
    ver += ['execute if entity @s[tag=asgem.r1] if score #gn astral.tmp matches 1.. run tag @s add asgem.lleno',
            'execute if entity @s[tag=asgem.r2] if score #gn astral.tmp matches 2.. run tag @s add asgem.lleno',
            'execute if entity @s[tag=asgem.r3] if score #gn astral.tmp matches 3.. run tag @s add asgem.lleno']
    fn('gemas/gui/ver', ver)
    gema = ['tag @s remove asgem.gema'] + [f'tag @s remove asgem.g.{t}.{q}' for t, q in todas()] + [
        'execute unless items entity @s weapon.mainhand *[minecraft:custom_data~{astral:{type:"gema"}}] run return 0',
        'tag @s add asgem.gema']
    gema += [f'execute if items entity @s weapon.mainhand *[minecraft:custom_data~{{astral:{{gema:"{t}",q:{q}}}}}] '
             f'run tag @s add asgem.g.{t}.{q}' for t, q in todas()]
    fn('gemas/gui/gema', gema)
    # --- Engarzar / quitar / devolver la gema extraida (siempre sobre el item en la mano)
    for t in TIPOS:
        quitar = {f'{NS}:{ench_id(t, v, q)}': 0 for v in VARIANTES for q in CALIDADES}
        fn(f'gemas/quitar/{t}', [
            'tag @s remove asgem.ok',
            f'execute unless {_has("weapon.mainhand", "#" + NS + ":gema_" + t)} run return 0',
            'item modify entity @s weapon.mainhand ' + json.dumps(
                {'function': 'minecraft:set_enchantments', 'enchantments': quitar, 'add': False}, separators=(',', ':')),
            'tag @s add asgem.ok'])
        for q in CALIDADES:
            lines = ['tag @s remove asgem.ok', f'function {NS}:gemas/gui/ver',
                     'execute unless entity @s[tag=asgem.valid] run return 0',
                     f'execute if entity @s[tag=asgem.has.{t}] run return 0',
                     'execute if entity @s[tag=asgem.lleno] run return 0']
            for v in VARIANTES:
                mod = {'function': 'minecraft:set_enchantments', 'enchantments': {f'{NS}:{ench_id(t, v, q)}': 1}, 'add': False}
                lines.append(f'execute if entity @s[tag=asgem.{v}] run item modify entity @s weapon.mainhand '
                             + json.dumps(mod, separators=(',', ':')))
            lines.append('tag @s add asgem.ok')
            fn(f'gemas/poner/{t}/{q}', lines)
            fn(f'gemas/dar/{t}/{q}', [f'loot replace entity @s weapon.mainhand loot {NS}:item/{item_id(t, q)}'])

    # --- Opalo en armadura: % de la Defensa Astral de cada pieza (despues del Talisman de Roca, sin multiplicarse).
    defensa = ['scoreboard players set #gb astral.tmp 0']
    for slot, key in zip(ARMOR_SLOTS, ('head', 'chest', 'legs', 'feet')):
        defensa.append('scoreboard players set #gp astral.tmp 0')
        defensa += [f'execute if {_has(slot, NS + ":" + ench_id(t, "armadura", q))} run scoreboard players set #gp astral.tmp {int(v)}'
                    for t, q, v in _con_stat('armadura', 'defensa')]
        defensa += [f'execute store result score #p astral.tmp run data get storage {NS}:tmp eq.{key}.components."minecraft:custom_data".astral.def',
                    'scoreboard players operation #p astral.tmp *= #gp astral.tmp',
                    'scoreboard players operation #gb astral.tmp += #p astral.tmp']
    defensa += ['scoreboard players set #base astral.tmp 100', 'scoreboard players operation #gb astral.tmp /= #base astral.tmp',
                'scoreboard players operation #d astral.tmp += #gb astral.tmp']
    fn('gemas/defensa', defensa)

    # --- Topacio: suerte (duplicar un drop Astral). Solo corre cuando cae un drop.
    def suma(stat, score):
        out = [f'scoreboard players set {score} astral.tmp 0']
        for slot in ARMOR_SLOTS:
            out += [f'execute if {_has(slot, NS + ":" + ench_id(t, "armadura", q))} run scoreboard players add {score} astral.tmp {int(v)}'
                    for t, q, v in _con_stat('armadura', stat)]
        out += [f'execute if {_has("weapon.mainhand", NS + ":" + ench_id(t, "arma", q))} run scoreboard players add {score} astral.tmp {int(v)}'
                for t, q, v in _con_stat('arma', stat)]
        return out
    for stat in ('suerte',):
        for v in VARIANTES:
            for _, _, val in _con_stat(v, stat):
                assert val == int(val), f'{stat} tiene que ser entero (lo suma un puntaje)'
    fn('gemas/suerte', [
        f'execute unless {_has("armor.*", "#" + NS + ":gema_suerte_armadura")} unless {_has("weapon.mainhand", "#" + NS + ":gema_suerte_arma")} run return 0',
        *suma('suerte', '#gs'),
        'execute store result score #r astral.tmp run random value 1..100',
        'execute if score #r astral.tmp > #gs astral.tmp run return 0',
        f'$loot give @s loot {NS}:item/$(id)',
        '$title @s actionbar ' + json.dumps([_txt('◆ Suerte de Topacio: ', '#f2b632'), _txt('$(name) x2', 'light_purple')], ensure_ascii=False),
        'playsound minecraft:block.amethyst_block.chime player @s ~ ~ ~ 0.8 1.4'])


# Lineas que build.py agrega en player/def y drop/give.
DEFENSA_HOOK = (f'execute if {_has("armor.*", "#" + NS + ":gema_opalo_armadura")} run function {NS}:gemas/defensa')
SUERTE_HOOK = f'$function {NS}:gemas/suerte {{id:"$(id)",name:"$(name)"}}'


# ------------------------------------------------------------------ Skript: ventana Reforja de gemas
SLOT_ITEM, SLOT_GEMA, SLOT_COSTO = 19, 21, 26
RANURAS_SLOTS = (23, 24, 25)
BAR = tuple(range(28, 35))
BTN_ENGARZAR, BTN_EXTRAER, BTN_HERRERO = tuple(range(38, 43)), tuple(range(46, 50)), (50, 51, 52)
SLOT_DEVOLVER, SLOT_CERRAR, SLOT_AYUDA = 45, 53, 8
BARRAS = {'gem_empty': ('COLOCA EQUIPO Y GEMA', '#ddc699'), 'gem_invalid': ('NO ADMITE GEMAS', '#ec998b'),
          'gem_ok': ('GEMA ENGARZADA', '#9ed7b0'), 'gem_out': ('GEMA EXTRAIDA', '#9ed7b0'),
          'gem_confirm': ('CONFIRMA: SE DESTRUYE', '#ec998b'),
          **{f'gem_slots_{n}_{r}': (f'RANURAS {n}/{r}', '#ddc699') for r in (1, 2, 3) for n in range(r + 1)}}
# Botones (diseno del dueno 19/11, ventanas_19_11.boton_forja): (pieza, casillas, estado)
BOTONES = {'gems': ('gemas', 3, 'listo'), 'forge_back': ('forja', 3, 'listo'),
           'gem_set_ready': ('engarzar', 5, 'listo'), 'gem_set_blocked': ('engarzar', 5, 'apagado'),
           'gem_set_confirm': ('engarzar', 5, 'confirma'),
           'gem_out_ready': ('extraer', 4, 'listo'), 'gem_out_off': ('extraer', 4, 'apagado')}


def _sk(texto):
    """Texto literal dentro de un string de Skript: % se escribe %%."""
    return texto.replace('%', '%%')


def _tags(cond_tag, player='{_p}'):
    return f'{player} has the scoreboard tag "{cond_tag}"'


def skript():
    from services_ui import title
    L = ['# Generado por datapack-src/gemas.py (plan E4 / 7d, 19/11/2026). No editar a mano.',
         '# Ventana "Reforja de gemas" (boton GEMAS del Herrero), /astralgema (OP) y gemas del cofre segun la nota.',
         '# El datapack hace los cambios sobre el item en la mano (gemas/*); Skript lo presta un instante y lo vuelve.',
         '', 'options:', f'    titulo: {title("reforja")}', '',
         'on load:', '    delete {-agem.gui::*}', '    delete {-agem.sel::*}', '    delete {-agem.conf::*}',
         '    delete {-agem.busy::*}', '    delete {-agem.aviso::*}', '    set {-agem.cargado} to true']
    for t in range(1, 11):
        for q in CALIDADES:
            L += [f'    set {{-agem.poner::{t}::{q}}} to {E.gema_costo(t, q)}',
                  f'    set {{-agem.extraer::{t}::{q}}} to {E.gema_costo(t, q, True)}']
    for i, t in enumerate(TIPOS, 1):
        L += [f'    set {{-agem.tipo::{i}}} to "{t}"', f'    set {{-agem.color::{t}}} to "{TIPOS[t][3]}"']
        for q in CALIDADES:
            L += [f'    set {{-agem.nombre::{t}::{q}}} to "{nombre(t, q)}"',
                  f'    set {{-agem.efecto::arma::{t}::{q}}} to "{_sk(texto_efectos("arma", t, q))}"',
                  f'    set {{-agem.efecto::armadura::{t}::{q}}} to "{_sk(texto_efectos("armadura", t, q))} (por pieza)"']
    for q in CALIDADES:
        L.append(f'    set {{-agem.cal::{q}}} to "{CALIDAD_NOMBRE[q]}"')
    for n, p in DROP_COFRE.items():
        L.append(f'    set {{-agem.drop::{E.NOTAS.index(n) + 1}}} to {p}')
        L.append(f'    set {{-agem.dropbonus::{E.NOTAS.index(n) + 1}}} to {DROP_BONUS_TIER.get(n, 0)}')
    for t, pesos in DROP_CALIDAD.items():
        L += [f'    set {{-agem.dropq::{t}::{q}}} to {w}' for q, w in enumerate(pesos, 1)]
    L += ['    send "[AstralRPG] Reforja de gemas cargada." to console', '']

    # Lectura de las etiquetas que deja el datapack (desenrollado: Skript no anida bien loops con etiquetas).
    leer = ['function agem_leer(p: player):', '    set {_id} to uuid of {_p}',
            '    delete {-agem.t::%{_id}%}', '    delete {-agem.r::%{_id}%}', '    delete {-agem.var::%{_id}%}',
            '    delete {-agem.has::%{_id}%::*}', '    delete {-agem.ran::%{_id}%::*}',
            '    delete {-agem.gt::%{_id}%}', '    delete {-agem.gq::%{_id}%}',
            '    set {_it} to {agem.item::%{_id}%}',
            '    if {_it} is set:',
            '        agem_run({_p}, {_it}, "gemas/gui/ver")',
            f'        if {_tags("asgem.valid")}:',
            '            set {-agem.var::%{_id}%} to "arma"',
            f'            if {_tags("asgem.armadura")}:',
            '                set {-agem.var::%{_id}%} to "armadura"']
    for t in range(1, 11):
        leer += [f'            if {_tags(f"asgem.t{t}")}:', f'                set {{-agem.t::%{{_id}}%}} to {t}',
                 f'                set {{-agem.r::%{{_id}}%}} to {ranuras(t)}']
    leer.append('            set {_k} to 0')
    for t in TIPOS:
        leer += [f'            if {_tags(f"asgem.has.{t}")}:', '                add 1 to {_k}',
                 f'                set {{-agem.ran::%{{_id}}%::%{{_k}}%}} to "{t}"']
        for q in CALIDADES:
            leer += [f'                if {_tags(f"asgem.q.{t}.{q}")}:', f'                    set {{-agem.has::%{{_id}}%::{t}}} to {q}']
    leer += ['    set {_g} to {agem.gema::%{_id}%}', '    if {_g} is set:', '        agem_run({_p}, {_g}, "gemas/gui/gema")']
    for t, q in todas():
        leer += [f'        if {_tags(f"asgem.g.{t}.{q}")}:', f'            set {{-agem.gt::%{{_id}}%}} to "{t}"',
                 f'            set {{-agem.gq::%{{_id}}%}} to {q}']
    L += leer + ['']
    L += [SK_CUERPO.replace('__RANURAS__', ', '.join(map(str, RANURAS_SLOTS[:-1])) + ' and ' + str(RANURAS_SLOTS[-1]))]
    return '\n'.join(L) + '\n'


SK_CUERPO = r'''
function agem_icon(model: text, label: text) :: item:
    set {_i} to paper named colored {_label}
    set item model of {_i} to {_model}
    return {_i}

# Presta {_it} al jugador (en la mano), corre la funcion del datapack y devuelve como quedo el item.
function agem_run(p: player, it: item, fn: text) :: item:
    set {_original} to {_p}'s tool
    set {_p}'s tool to {_it}
    execute console command "execute as %name of {_p}% at @s run function astral:%{_fn}%"
    set {_r} to {_p}'s tool
    set {_p}'s tool to {_original}
    return {_r}

function agem_es_gema(p: player, i: item) :: boolean:
    agem_run({_p}, {_i}, "gemas/gui/gema")
    if {_p} has the scoreboard tag "asgem.gema":
        return true
    return false

function agem_give(p: player, i: item):
    {_i} is set
    {_i} is not air
    if {_p} has enough space for {_i}:
        give {_i} to {_p}
    else:
        drop {_i} at location of {_p}

function agem_return(p: player):
    set {_id} to uuid of {_p}
    set {_a} to {agem.item::%{_id}%}
    set {_b} to {agem.gema::%{_id}%}
    delete {agem.item::%{_id}%}
    delete {agem.gema::%{_id}%}
    delete {-agem.gui::%{_id}%}
    delete {-agem.sel::%{_id}%}
    delete {-agem.conf::%{_id}%}
    delete {-agem.busy::%{_id}%}
    delete {-agem.aviso::%{_id}%}
    agem_give({_p}, {_a})
    agem_give({_p}, {_b})

function agem_bar(p: player, model: text, label: text):
    set {_inv} to {-agem.gui::%uuid of {_p}%}
    loop 7 times:
        set {_slot} to loop-number + 27
        set slot {_slot} of {_inv} to agem_icon("astral:servicios/bar_%{_model}%_%loop-number - 1%", {_label})

function agem_boton(p: player, start: number, n: number, model: text, label: text, lines: texts):
    set {_inv} to {-agem.gui::%uuid of {_p}%}
    loop {_n} times:
        set {_i} to agem_icon("astral:servicios/%{_model}%_%loop-number - 1%", {_label})
        set lore of {_i} to {_lines::*}
        set slot ({_start} + loop-number - 1) of {_inv} to {_i}

function agem_refresh(p: player):
    set {_id} to uuid of {_p}
    set {_inv} to {-agem.gui::%{_id}%}
    {_inv} is set
    agem_leer({_p})
    set {_item} to {agem.item::%{_id}%}
    set {_gema} to {agem.gema::%{_id}%}
    set slot 19 of {_inv} to air
    set slot 21 of {_inv} to air
    if {_item} is set:
        set slot 19 of {_inv} to {_item}
    if {_gema} is set:
        set slot 21 of {_inv} to {_gema}
    set {_r} to {-agem.r::%{_id}%} ? 0
    set {_var} to {-agem.var::%{_id}%} ? "arma"
    set {_n} to size of {-agem.ran::%{_id}%::*}
    # Ranuras: gema engarzada, libre o bloqueada por el tier.
    set {_k} to 0
    loop __RANURAS__:
        add 1 to {_k}
        set {_s} to loop-value
        if {_item} is not set:
            set {_i} to agem_icon("astral:servicios/gem_socket_empty", "&7Ranura")
            set lore of {_i} to "&7Coloca un arma o armadura de AstralRPG."
        else if {_k} > {_r}:
            set {_i} to agem_icon("astral:servicios/gem_socket_locked", "&8Ranura bloqueada")
            set lore of {_i} to "&7Tier 1-3: 1 ranura. Tier 4-7: 2. Tier 8-10: 3."
        else if {-agem.ran::%{_id}%::%{_k}%} is set:
            set {_t} to {-agem.ran::%{_id}%::%{_k}%}
            set {_q} to {-agem.has::%{_id}%::%{_t}%}
            set {_label} to "%{-agem.color::%{_t}%}%◆ %{-agem.nombre::%{_t}%::%{_q}%}%"
            set {_sel} to "&eClic: seleccionar (para extraer o reemplazar)."
            if {-agem.sel::%{_id}%} is {_t}:
                set {_label} to "&a» %{_label}% &a«"
                set {_sel} to "&a&lSELECCIONADA &7(clic de nuevo para soltar)"
            set {_i} to agem_icon("astral:gemas/%{_t}%_%{_q}%", {_label})
            set lore of {_i} to "&7%{-agem.efecto::%{_var}%::%{_t}%::%{_q}%}%", "&7Extraer: &e%{-agem.extraer::%{-agem.t::%{_id}%}%::%{_q}%}%$" and {_sel}
        else:
            set {_i} to agem_icon("astral:servicios/gem_socket_empty", "&7Ranura libre")
            set lore of {_i} to "&7Pon una gema en el recuadro GEMA y pulsa ENGARZAR."
        set slot {_s} of {_inv} to {_i}
    # Costo y saldo
    set {_c} to gold nugget named "&6Costos"
    set {_gt} to {-agem.gt::%{_id}%}
    set {_gq} to {-agem.gq::%{_id}%}
    if {_r} > 0:
        if {_gq} is set:
            set lore of {_c} to "&7Engarzar esta gema: &e%{-agem.poner::%{-agem.t::%{_id}%}%::%{_gq}%}%$", "&7Extraer sin romperla: &ex{@x} el costo de engarzar" and "&7Tu saldo: &e%balance of {_p}%$"
        else:
            set lore of {_c} to "&7Coloca una gema para ver el costo." and "&7Tu saldo: &e%balance of {_p}%$"
    else:
        set lore of {_c} to "&7Primero coloca tu equipo." and "&7Tu saldo: &e%balance of {_p}%$"
    set slot 26 of {_inv} to {_c}
    # Barra de estado
    if {_item} is not set:
        agem_bar({_p}, "gem_empty", "&eColoca un equipo (recuadro EQUIPO) y una gema (recuadro GEMA).")
    else if {_r} is 0:
        agem_bar({_p}, "gem_invalid", "&cSolo armas, bastones y armaduras de AstralRPG con tier.")
    else if {-agem.conf::%{_id}%} is set:
        agem_bar({_p}, "gem_confirm", "&cLa gema que reemplazas se DESTRUYE. Pulsa CONFIRMAR.")
    else if {-agem.aviso::%{_id}%} is set:
        agem_bar({_p}, {-agem.aviso::%{_id}%}, "&eResultado de la ultima accion.")
    else:
        agem_bar({_p}, "gem_slots_%{_n}%_%{_r}%", "&eRanuras ocupadas de tu equipo.")
    # Boton ENGARZAR
    set {_m} to "gem_set_blocked"
    set {_l} to "&cENGARZAR"
    set {_lore::*} to "&7Pone la gema del recuadro en una ranura libre." and "&7Si el equipo ya tiene esa gema, o no hay lugar, reemplaza (la vieja se destruye)."
    if {_r} > 0:
        if {_gq} is set:
            set {_m} to "gem_set_ready"
            set {_l} to "&a&lENGARZAR &7(%{-agem.poner::%{-agem.t::%{_id}%}%::%{_gq}%}%$)"
            if {-agem.conf::%{_id}%} is set:
                set {_m} to "gem_set_confirm"
                set {_l} to "&c&lCONFIRMAR &7(la gema vieja se destruye)"
    agem_boton({_p}, 38, 5, {_m}, {_l}, {_lore::*})
    # Boton EXTRAER
    set {_m} to "gem_out_off"
    set {_l} to "&7EXTRAER"
    set {_lore::*} to "&7Saca la gema seleccionada sin romperla." and "&7Cuesta x{@x} lo de engarzar. Deja libre el recuadro GEMA."
    set {_st} to {-agem.sel::%{_id}%}
    if {_n} is 1:
        set {_st} to {-agem.ran::%{_id}%::1}
    if {_st} is set:
        if {-agem.has::%{_id}%::%{_st}%} is set:
            set {_m} to "gem_out_ready"
            set {_l} to "&b&lEXTRAER %{-agem.nombre::%{_st}%::%{-agem.has::%{_id}%::%{_st}%}%}% &7(%{-agem.extraer::%{-agem.t::%{_id}%}%::%{-agem.has::%{_id}%::%{_st}%}%}%$)"
    agem_boton({_p}, 46, 4, {_m}, {_l}, {_lore::*})

function agem_open(p: player):
    close {_p}'s inventory
    agem_return({_p})
    set {_id} to uuid of {_p}
    set {_inv} to a new chest inventory with 6 rows named colored "{@titulo}"
    set {-agem.gui::%{_id}%} to {_inv}
    set slot 8 of {_inv} to book named "&eComo usar"
    set lore of slot 8 of {_inv} to "&71. Shift+clic en tu equipo y en una gema.", "&72. ENGARZAR la pone en una ranura (cobra plata).", "&73. Clic en una ranura para elegirla: EXTRAER o reemplazar.", "&7Reemplazar destruye la gema vieja; extraer cuesta mas." and "&7Cerrar o desconectarte devuelve todo."
    set slot 45 of {_inv} to agem_icon("astral:servicios/forja_atras_0", "&eDevolver objetos")
    set slot 53 of {_inv} to agem_icon("astral:servicios/forja_cerrar_0", "&cCerrar y devolver")
    loop 3 times:
        set {_b} to agem_icon("astral:servicios/forge_back_%loop-number - 1%", "&6Volver al Herrero")
        set lore of {_b} to "&7Mejorar y Reparar. Tus objetos vuelven a tu inventario."
        set slot (49 + loop-number) of {_inv} to {_b}
    agem_refresh({_p})
    open {_inv} to {_p}

function agem_avisar(p: player, aviso: text):
    set {-agem.aviso::%uuid of {_p}%} to {_aviso}

function agem_engarzar(p: player):
    set {_id} to uuid of {_p}
    agem_leer({_p})
    set {_item} to {agem.item::%{_id}%}
    set {_gema} to {agem.gema::%{_id}%}
    if {_item} is not set:
        send "&cColoca primero tu equipo." to {_p}
        stop
    if {-agem.r::%{_id}%} is not set:
        send "&cEse objeto no admite gemas." to {_p}
        stop
    if {-agem.gq::%{_id}%} is not set:
        send "&cColoca una gema en el recuadro GEMA." to {_p}
        stop
    set {_t} to {-agem.gt::%{_id}%}
    set {_q} to {-agem.gq::%{_id}%}
    set {_tier} to {-agem.t::%{_id}%}
    set {_n} to size of {-agem.ran::%{_id}%::*}
    set {_viejo} to ""
    if {-agem.has::%{_id}%::%{_t}%} is set:
        set {_viejo} to {_t}
    else if {_n} >= {-agem.r::%{_id}%}:
        if {-agem.sel::%{_id}%} is not set:
            send "&eTodas las ranuras estan ocupadas: hace clic en la que queres reemplazar." to {_p}
            stop
        set {_viejo} to {-agem.sel::%{_id}%}
    set {_costo} to {-agem.poner::%{_tier}%::%{_q}%}
    if balance of {_p} < {_costo}:
        send "&cNecesitas %{_costo}%$ para engarzar esa gema." to {_p}
        stop
    if {_viejo} is not "":
        set {_clave} to "%{_viejo}%>%{_t}%%{_q}%"
        if {-agem.conf::%{_id}%} is not {_clave}:
            set {-agem.conf::%{_id}%} to {_clave}
            send "&c&l¡Atencion! &7La gema de &f%{-agem.nombre::%{_viejo}%::%{-agem.has::%{_id}%::%{_viejo}%}%}% &7se &c&lDESTRUYE&7. Pulsa &cCONFIRMAR &7para seguir." to {_p}
            play sound "block.note_block.bass" to {_p}
            stop
    set {-agem.busy::%{_id}%} to true
    set {_nuevo} to {_item}
    if {_viejo} is not "":
        set {_nuevo} to agem_run({_p}, {_nuevo}, "gemas/quitar/%{_viejo}%")
    set {_nuevo} to agem_run({_p}, {_nuevo}, "gemas/poner/%{_t}%/%{_q}%")
    if {_p} has the scoreboard tag "asgem.ok":
        remove {_costo} from balance of {_p}
        set {agem.item::%{_id}%} to {_nuevo}
        if item amount of {_gema} > 1:
            set item amount of {_gema} to (item amount of {_gema}) - 1
            set {agem.gema::%{_id}%} to {_gema}
        else:
            delete {agem.gema::%{_id}%}
        send "&aGema engarzada: &f%{-agem.nombre::%{_t}%::%{_q}%}% &7(-%{_costo}%$)" to {_p}
        play sound "block.amethyst_block.resonate" to {_p}
        agem_avisar({_p}, "gem_ok")
        log "%now% %name of {_p}% %{_id}% engarzar %{_t}% %{_q}% tier=%{_tier}% viejo=%{_viejo}% costo=%{_costo}%" to "astral-gemas"
    else:
        send "&cNo se pudo engarzar. Tu equipo y tu gema quedaron igual." to {_p}
    delete {-agem.conf::%{_id}%}
    delete {-agem.sel::%{_id}%}
    delete {-agem.busy::%{_id}%}

function agem_extraer(p: player):
    set {_id} to uuid of {_p}
    agem_leer({_p})
    set {_item} to {agem.item::%{_id}%}
    if {_item} is not set:
        stop
    set {_t} to {-agem.sel::%{_id}%}
    if size of {-agem.ran::%{_id}%::*} is 1:
        set {_t} to {-agem.ran::%{_id}%::1}
    if {_t} is not set:
        send "&eHace clic en la ranura de la gema que queres extraer." to {_p}
        stop
    set {_q} to {-agem.has::%{_id}%::%{_t}%}
    if {_q} is not set:
        stop
    if {agem.gema::%{_id}%} is set:
        send "&cVacia el recuadro GEMA: ahi vas a recibir la gema extraida." to {_p}
        stop
    set {_costo} to {-agem.extraer::%{-agem.t::%{_id}%}%::%{_q}%}
    if balance of {_p} < {_costo}:
        send "&cNecesitas %{_costo}%$ para extraerla sin romperla." to {_p}
        stop
    set {-agem.busy::%{_id}%} to true
    set {_nuevo} to agem_run({_p}, {_item}, "gemas/quitar/%{_t}%")
    if {_p} has the scoreboard tag "asgem.ok":
        set {_g} to agem_run({_p}, air, "gemas/dar/%{_t}%/%{_q}%")
        if {_g} is set:
            if {_g} is not air:
                remove {_costo} from balance of {_p}
                set {agem.item::%{_id}%} to {_nuevo}
                set {agem.gema::%{_id}%} to {_g}
                send "&aGema extraida: &f%{-agem.nombre::%{_t}%::%{_q}%}% &7(-%{_costo}%$). Quedo en el recuadro GEMA." to {_p}
                play sound "block.amethyst_cluster.break" to {_p}
                agem_avisar({_p}, "gem_out")
                log "%now% %name of {_p}% %{_id}% extraer %{_t}% %{_q}% costo=%{_costo}%" to "astral-gemas"
    delete {-agem.sel::%{_id}%}
    delete {-agem.conf::%{_id}%}
    delete {-agem.busy::%{_id}%}

command /astralreforja [<player>]:
    trigger:
        if arg-1 is set:
            if sender is not console:
                stop
            agem_open(arg-1)
        else:
            if sender is a player:
                agem_open(player)

on inventory click:
    set {_id} to uuid of player
    set {_inv} to {-agem.gui::%{_id}%}
    if {_inv} is not set:
        stop
    if player's current inventory is not {_inv}:
        agem_return(player)
        stop
    cancel event
    if {-agem.busy::%{_id}%} is true:
        stop
    if clicked inventory is player's inventory:
        if click type is left mouse button or right mouse button:
            uncancel event
            stop
        if click type is left mouse button with shift or right mouse button with shift:
            set {_item} to event-slot
            if {_item} is air:
                stop
            if agem_es_gema(player, {_item}) is true:
                if {agem.gema::%{_id}%} is set:
                    send "&cYa hay una gema en el recuadro GEMA." to player
                    stop
                set {agem.gema::%{_id}%} to {_item}
            else:
                if {agem.item::%{_id}%} is set:
                    send "&cYa hay un equipo en el recuadro EQUIPO." to player
                    stop
                if item amount of {_item} is not 1:
                    send "&cColoca una sola pieza de equipo." to player
                    stop
                set {agem.item::%{_id}%} to {_item}
            set event-slot to air
            delete {-agem.sel::%{_id}%}
            delete {-agem.conf::%{_id}%}
            delete {-agem.aviso::%{_id}%}
            agem_refresh(player)
        stop
    if clicked inventory is not {_inv}:
        stop
    if click type is not left mouse button:
        if click type is not right mouse button:
            stop
    set {_slot} to index of event-slot
    if {_slot} is 53:
        close player's inventory
        stop
    if {_slot} is 45:
        set {_a} to {agem.item::%{_id}%}
        set {_b} to {agem.gema::%{_id}%}
        delete {agem.item::%{_id}%}
        delete {agem.gema::%{_id}%}
        agem_give(player, {_a})
        agem_give(player, {_b})
        delete {-agem.sel::%{_id}%}
        delete {-agem.conf::%{_id}%}
        delete {-agem.aviso::%{_id}%}
        agem_refresh(player)
        stop
    if {_slot} is between 50 and 52:
        close player's inventory
        wait 1 tick
        execute console command "astralherrero %name of player%"
        stop
    if {_slot} is 19:
        set {_cursor} to cursor slot of player
        set {_old} to {agem.item::%{_id}%}
        if {_cursor} is air:
            if {_old} is set:
                delete {agem.item::%{_id}%}
                set cursor slot of player to {_old}
        else:
            if agem_es_gema(player, {_cursor}) is true:
                send "&cLas gemas van en el recuadro GEMA." to player
                stop
            if item amount of {_cursor} is not 1:
                send "&cColoca una sola pieza de equipo." to player
                stop
            set {agem.item::%{_id}%} to {_cursor}
            if {_old} is set:
                set cursor slot of player to {_old}
            else:
                set cursor slot of player to air
        delete {-agem.sel::%{_id}%}
        delete {-agem.conf::%{_id}%}
        delete {-agem.aviso::%{_id}%}
        agem_refresh(player)
        stop
    if {_slot} is 21:
        set {_cursor} to cursor slot of player
        set {_old} to {agem.gema::%{_id}%}
        if {_cursor} is air:
            if {_old} is set:
                delete {agem.gema::%{_id}%}
                set cursor slot of player to {_old}
        else:
            if agem_es_gema(player, {_cursor}) is false:
                send "&cEse recuadro es solo para gemas." to player
                stop
            set {agem.gema::%{_id}%} to {_cursor}
            if {_old} is set:
                set cursor slot of player to {_old}
            else:
                set cursor slot of player to air
        delete {-agem.conf::%{_id}%}
        delete {-agem.aviso::%{_id}%}
        agem_refresh(player)
        stop
    if {_slot} is between 23 and 25:
        set {_k} to {_slot} - 22
        set {_t} to {-agem.ran::%{_id}%::%{_k}%}
        if {_t} is set:
            if {-agem.sel::%{_id}%} is {_t}:
                delete {-agem.sel::%{_id}%}
            else:
                set {-agem.sel::%{_id}%} to {_t}
            delete {-agem.conf::%{_id}%}
            delete {-agem.aviso::%{_id}%}
            agem_refresh(player)
        stop
    if {_slot} is between 38 and 42:
        delete {-agem.aviso::%{_id}%}
        agem_engarzar(player)
        agem_refresh(player)
        stop
    if {_slot} is between 46 and 49:
        delete {-agem.aviso::%{_id}%}
        agem_extraer(player)
        agem_refresh(player)

on inventory drag:
    if {-agem.gui::%uuid of player%} is set:
        if player's current inventory is {-agem.gui::%uuid of player%}:
            cancel event

on inventory close:
    if {-agem.gui::%uuid of player%} is set:
        agem_return(player)

on quit:
    agem_return(player)

on join:
    if {agem.item::%uuid of player%} is set:
        wait 1 tick
        agem_return(player)
    else if {agem.gema::%uuid of player%} is set:
        wait 1 tick
        agem_return(player)

on unload:
    loop all players:
        if {-agem.gui::%uuid of loop-player%} is set:
            agem_return(loop-player)
            close loop-player's inventory

# ------------------------------------------------------------------ OP y gemas del cofre
# /astralgema dar <jugador> <tipo|azar> <calidad 1-5> [cantidad]   (OP o consola)
# /astralgema cofre <jugador> <tier> <nota 1-6>                    (consola: cofre de mazmorra, astral_puntaje.sk)
command /astralgema [<text>] [<text>] [<text>] [<text>] [<text>]:
    trigger:
        if sender is a player:
            if player is not op:
                send "&cSolo para OP." to player
                stop
        if arg-1 is "dar":
            set {_p} to arg-2 parsed as player
            if {_p} is not set:
                send "&cUso: /astralgema dar <jugador> <rubi|zafiro|jade|topacio|amatista|opalo|onix|azar> <calidad 1-5> [cantidad]" to sender
                stop
            set {_q} to (arg-4 parsed as integer) ? 1
            if {_q} < 1:
                set {_q} to 1
            if {_q} > 5:
                set {_q} to 5
            set {_c} to (arg-5 parsed as integer) ? 1
            if {_c} < 1:
                set {_c} to 1
            if {_c} > 64:
                set {_c} to 64
            loop {_c} times:
                set {_t} to arg-3
                if {_t} is "azar":
                    set {_t} to {-agem.tipo::%random integer between 1 and 7%}
                if {-agem.color::%{_t}%} is not set:
                    send "&cTipo de gema desconocido: %arg-3%" to sender
                    stop
                execute console command "loot give %name of {_p}% loot astral:item/gema_%{_t}%_%{_q}%"
            send "&aGemas entregadas a %name of {_p}%." to sender
            stop
        if arg-1 is "cofre":
            if sender is a player:
                stop
            set {_p} to arg-2 parsed as player
            if {_p} is not set:
                stop
            set {_tier} to (arg-3 parsed as integer) ? 1
            set {_nota} to (arg-4 parsed as integer) ? 0
            if {-agem.drop::%{_nota}%} is not set:
                stop
            if random number between 0 and 1 >= {-agem.drop::%{_nota}%}:
                stop
            add ({-agem.dropbonus::%{_nota}%} ? 0) to {_tier}
            if {_tier} < 1:
                set {_tier} to 1
            if {_tier} > 5:
                set {_tier} to 5
            set {_total} to 0
            loop 5 times:
                add ({-agem.dropq::%{_tier}%::%loop-number%} ? 0) to {_total}
            set {_r} to random integer between 1 and {_total}
            set {_q} to 1
            set {_acc} to 0
            loop 5 times:
                add ({-agem.dropq::%{_tier}%::%loop-number%} ? 0) to {_acc}
                if {_r} <= {_acc}:
                    set {_q} to loop-number
                    exit loop
            set {_t} to {-agem.tipo::%random integer between 1 and 7%}
            execute console command "loot give %name of {_p}% loot astral:item/gema_%{_t}%_%{_q}%"
            send "&d&l◆ &dEncontraste una gema en el cofre: %{-agem.color::%{_t}%}%%{-agem.nombre::%{_t}%::%{_q}%}%&d!" to {_p}
            play sound "block.amethyst_block.chime" to {_p}
            log "%now% %name of {_p}% %uuid of {_p}% cofre tier=%{_tier}% nota=%{_nota}% gema=%{_t}% q=%{_q}%" to "astral-gemas"
            stop
        send "&eUso: /astralgema dar <jugador> <tipo|azar> <calidad 1-5> [cantidad]" to sender
'''.replace('{@x}', str(E.GEMA_EXTRAER_MULT))


# ------------------------------------------------------------------ texturas (PNG propios, reemplazables)
def _dibujar(tipo, q):
    """Gema provisoria 16x16 dibujada por codigo. Calidad: mas facetas, brillo y destellos."""
    from PIL import Image, ImageDraw
    col = TIPOS[tipo][2]
    r, g, b = int(col[1:3], 16), int(col[3:5], 16), int(col[5:7], 16)

    def tono(f):
        return tuple(max(0, min(255, int(c * f))) for c in (r, g, b)) + (255,)
    im = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if q == 1:   # cruda: piedra irregular, apagada
        d.polygon([(4, 5), (8, 2), (12, 4), (13, 9), (10, 13), (5, 12), (3, 9)], fill=tono(0.55), outline=tono(0.3))
        d.polygon([(6, 6), (9, 4), (11, 7), (8, 9)], fill=tono(0.75))
    else:        # tallada: diamante con facetas
        d.polygon([(8, 1), (14, 6), (8, 15), (2, 6)], fill=tono(0.8), outline=tono(0.35))
        d.polygon([(4, 6), (8, 2), (12, 6), (8, 7)], fill=tono(1.05))
        d.line([(2, 6), (14, 6)], fill=tono(0.5))
        d.polygon([(8, 7), (12, 6), (8, 15)], fill=tono(0.65))
        if q >= 3:
            d.point([(6, 4), (7, 3)], fill=(255, 255, 255, 230))
        if q >= 4:
            d.point([(11, 3), (12, 2), (10, 2), (11, 1)], fill=(255, 255, 230, 255))
        if q == 5:
            for x, y in ((1, 1), (14, 12), (2, 13), (14, 1)):
                d.point([(x, y)], fill=(255, 245, 200, 255))
            d.point([(1, 2), (2, 1), (0, 1), (1, 0)], fill=(255, 245, 200, 150))
    return im


def asegurar_texturas():
    """Crea los PNG provisorios que falten. Los que ya existen (por ejemplo los del dueno) no se tocan."""
    TEX.mkdir(parents=True, exist_ok=True)
    nuevos = []
    for t, q in todas():
        p = TEX / f'{t}_{q}.png'
        if not p.exists():
            _dibujar(t, q).save(p)
            nuevos.append(p.name)
    return nuevos


def pack_assets():
    """Archivos del resource pack: texturas de gemas, modelos e items (assets/astral/items/gemas/*)."""
    asegurar_texturas()
    files = {}
    for t, q in todas():
        name = f'{t}_{q}'
        files[f'assets/astral/textures/item/gemas/{name}.png'] = (TEX / f'{name}.png').read_bytes()
        files[f'assets/astral/models/item/gemas/{name}.json'] = json.dumps(
            {'parent': 'minecraft:item/generated', 'textures': {'layer0': f'astral:item/gemas/{name}'}}).encode()
        files[f'assets/astral/items/gemas/{name}.json'] = json.dumps(
            {'model': {'type': 'minecraft:model', 'model': f'astral:item/gemas/{name}'}}).encode()
    return files


# ------------------------------------------------------------------ plugin AstralGemas (AuraSkills)
RUNTIME = ('robo', 'espinas', 'dano_jefes', 'plata')


def tabla_auraskills():
    """{clave del encantamiento: [[rasgo, operacion, valor]]}: lo que AstralGemas pasa a AuraSkills."""
    out = {}
    for t in TIPOS:
        for v in VARIANTES:
            for q in CALIDADES:
                mods = [[AURASKILLS[s][0], AURASKILLS[s][1], val] for s, val in efectos(v, t, q) if s in AURASKILLS]
                if mods:
                    out[f'{NS}:{ench_id(t, v, q)}'] = mods
    return out


def tabla_runtime():
    """gemas.json de AstralGemas: rasgos de AuraSkills, efectos propios por encantamiento y constantes."""
    efx = {}
    for t in TIPOS:
        for v in VARIANTES:
            for q in CALIDADES:
                d = {s: val for s, val in efectos(v, t, q) if s in RUNTIME}
                if d:
                    efx[f'{NS}:{ench_id(t, v, q)}'] = d
    return {'traits': tabla_auraskills(), 'efectos': efx, 'robo_prob': ROBO_PROB, 'robo_espera': ROBO_ESPERA_TICKS,
            'espinas_prob': ESPINAS_PROB, 'espinas_jefes': ESPINAS_JEFES, 'tags_jefes': list(TAGS_JEFES)}


PLUGIN_YML = """name: AstralGemas
version: 1.1.0
main: astral.AstralGemas
api-version: '26.1.2'
depend: [AuraSkills]
softdepend: [MythicMobs]
description: Gemas engarzadas - mana, critico, robo de vida, espinas, dano a jefes y plata
"""


def build_plugin(jdk, server):
    import subprocess
    jdk = Path(jdk)
    server = Path(server)
    classes = ROOT / '.local' / 'gemas-classes'
    classes.mkdir(parents=True, exist_ok=True)
    jars = list((server / 'libraries').rglob('*.jar')) + [server / 'plugins' / 'auraskills.jar', server / 'plugins' / 'mythicmobs.jar']
    javac = [str(jdk / ('java.exe' if os.name == 'nt' else 'java')), '-m', 'jdk.compiler/com.sun.tools.javac.Main']
    subprocess.run([*javac, '-encoding', 'UTF-8', '-source', '25', '-target', '25', '-classpath',
                    os.pathsep.join(map(str, jars)), '-d', str(classes), str(HERE / 'runtime' / 'AstralGemas.java')], check=True)
    OUT.mkdir(parents=True, exist_ok=True)
    dest = OUT / 'AstralGemas.jar'
    with zipfile.ZipFile(dest, 'w', zipfile.ZIP_DEFLATED) as z:
        for p in sorted((classes / 'astral').glob('AstralGemas*.class')):
            z.writestr(zipfile.ZipInfo(p.relative_to(classes).as_posix(), (2026, 11, 19, 0, 0, 0)), p.read_bytes())
        z.writestr(zipfile.ZipInfo('gemas.json', (2026, 11, 19, 0, 0, 0)), json.dumps(tabla_runtime(), sort_keys=True))
        z.writestr(zipfile.ZipInfo('plugin.yml', (2026, 11, 19, 0, 0, 0)), PLUGIN_YML)
    return dest


# ------------------------------------------------------------------ tabla para la entrega
def tabla_md():
    out = ['| Gema | Calidad | En arma | En armadura (por pieza) |', '|---|---|---|---|']
    for t, q in todas():
        out.append(f'| {TIPOS[t][0]} | {CALIDAD_NOMBRE[q]} | {texto_efectos("arma", t, q)} | {texto_efectos("armadura", t, q)} |')
    return '\n'.join(out)


def costos_md():
    out = ['| Tier | Ranuras | ' + ' | '.join(f'{CALIDAD_NOMBRE[q]} (engarzar / extraer)' for q in CALIDADES) + ' |',
           '|---|---|' + '---|' * len(CALIDADES)]
    for t in range(1, 11):
        out.append(f'| {t} | {ranuras(t)} | ' + ' | '.join(
            f'{E.texto(E.gema_costo(t, q))} / {E.texto(E.gema_costo(t, q, True))}' for q in CALIDADES) + ' |')
    return '\n'.join(out)


def generate():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'astral_gemas.sk').write_text(skript(), encoding='utf-8')
    nuevos = asegurar_texturas()
    print(f'gemas: {len(todas())} gemas, skript -> {OUT / "astral_gemas.sk"}; texturas nuevas: {len(nuevos)}')


# ------------------------------------------------------------------ vistas previas (build/previews/)
def previews():
    """Ventana Reforja (3 estados), Herrero con el boton GEMAS y la hoja de las 35 gemas."""
    from PIL import Image
    import services_ui as S
    from escape_menu import text
    from ventanas_19_11 import boton_forja
    out = ROOT / 'build' / 'previews'
    out.mkdir(parents=True, exist_ok=True)
    asegurar_texturas()

    def pos(slot):
        return S.OFFSET[0] + 8 + (slot % 9) * 18, S.OFFSET[1] + 18 + (slot // 9) * 18

    def icon(im, slot, sprite):
        im.alpha_composite(sprite.resize((16, 16), Image.Resampling.LANCZOS), pos(slot))

    def gema(t, q):
        return Image.open(TEX / f'{t}_{q}.png').convert('RGBA')

    def espada():
        sp = Image.new('RGBA', (16, 16))
        for i in range(11):
            sp.putpixel((3 + i, 12 - i), (200, 220, 235, 255))
            sp.putpixel((4 + i, 12 - i), (150, 170, 190, 255))
        for i in range(4):
            sp.putpixel((2 + i, 10 + i), (120, 80, 40, 255))
        return sp

    estados = [('VACIA', 'gem_empty', None, [], 0, 'gem_set_blocked', 'gem_out_off'),
               ('EQUIPO T5 + GEMA', 'gem_slots_1_2', ('rubi', 3), [('jade', 2)], 2, 'gem_set_ready', 'gem_out_ready'),
               ('REEMPLAZO', 'gem_confirm', ('jade', 5), [('jade', 2), ('onix', 4)], 2, 'gem_set_confirm', 'gem_out_ready')]
    sheet = Image.new('RGBA', (S.SIZE[0] * 3, S.SIZE[1] + 24), '#252a28')
    for col, (titulo, barra, en_gema, puestas, r, b1, b2) in enumerate(estados):
        im = Image.new('RGBA', S.SIZE, '#252a28')
        im.alpha_composite(S.panel('reforja'))
        im.alpha_composite(S.banner(*BARRAS[barra]), (S.OFFSET[0] + 25, S.OFFSET[1] + 71))
        for name, start in ((b1, 38), (b2, 46)):
            bf = boton_forja(*BOTONES[name])
            im.alpha_composite(bf.resize((bf.width // 2, 18), Image.Resampling.LANCZOS), (pos(start)[0] - 1, pos(start)[1] - 1))
        bf = boton_forja(*BOTONES['forge_back'])
        im.alpha_composite(bf.resize((bf.width // 2, 18), Image.Resampling.LANCZOS), (pos(50)[0] - 1, pos(50)[1] - 1))
        for sl, pieza in ((45, 'atras'), (53, 'cerrar')):
            bf = boton_forja(pieza, 1)
            im.alpha_composite(bf.resize((18, 18), Image.Resampling.LANCZOS), (pos(sl)[0] - 1, pos(sl)[1] - 1))
        if r:
            icon(im, 19, espada())
        if en_gema:
            icon(im, 21, gema(*en_gema))
        for k, slot in enumerate(RANURAS_SLOTS):
            if k < len(puestas):
                icon(im, slot, gema(*puestas[k]))
            else:
                icon(im, slot, S.socket(r and k >= r))
        text(im, 'Inventario', (S.OFFSET[0] + 37, S.OFFSET[1] + 129), color='#383c40')
        sheet.alpha_composite(im, (col * S.SIZE[0], 24))
        text(sheet, titulo, (col * S.SIZE[0] + 112, 8), color='#fff0cd')
    sheet.resize((sheet.width * 3, sheet.height * 3), Image.Resampling.NEAREST).save(out / 'reforja_gemas.png')
    her = Image.new('RGBA', S.SIZE, '#252a28')
    her.alpha_composite(S.panel('herrero'))
    for nombre, sl in ((('mejorar', 5, 'listo'), 38), (('reparar', 4, 'listo'), 46), (BOTONES['gems'], 50), (('atras', 1), 45), (('cerrar', 1), 53)):
        bf = boton_forja(*nombre)
        her.alpha_composite(bf.resize((bf.width // 2, 18), Image.Resampling.LANCZOS), (pos(sl)[0] - 1, pos(sl)[1] - 1))
    her.resize((her.width * 3, her.height * 3), Image.Resampling.NEAREST).save(out / 'herrero_gemas.png')
    celda = 72
    hoja = Image.new('RGBA', (5 * celda + 90, 7 * celda + 24), '#1d1e20')
    for i, t in enumerate(TIPOS):
        text(hoja, TIPOS_ASCII[t].upper(), (44, 24 + i * celda + celda // 2 - 3), color='#eac58a')
        for q in CALIDADES:
            hoja.alpha_composite(gema(t, q).resize((64, 64), Image.Resampling.LANCZOS), (90 + (q - 1) * celda + 4, 24 + i * celda + 4))
    for q in CALIDADES:
        text(hoja, CALIDAD_NOMBRE[q].upper(), (90 + (q - 1) * celda + celda // 2, 8), color='#d6b8ff')
    hoja.resize((hoja.width * 2, hoja.height * 2), Image.Resampling.NEAREST).save(out / 'gemas_texturas.png')
    return [out / 'reforja_gemas.png', out / 'herrero_gemas.png', out / 'gemas_texturas.png']


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--jdk', help='carpeta bin del JDK 25: tambien compila build/gemas/AstralGemas.jar')
    ap.add_argument('--server', default=str(ROOT / '.local' / 'testsrv'), help='Paper local con libraries/ y plugins/auraskills.jar')
    a = ap.parse_args()
    generate()
    print('vistas', *previews())
    if a.jdk:
        print(build_plugin(a.jdk, a.server))
