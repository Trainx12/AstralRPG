# -*- coding: utf-8 -*-
"""Clases nuevas (pedido del dueno, 22/11/2026): Segador, Invocador y Asesino.

- Segador: guadanas (las que ya existian). Tajo en area (semicirculo); cura al matar. (23/11: Cosecha retirada)
  Armadura solo en T1, T3, T5, T7 y T10.
- Invocador: libros (T1, T3, T5, T7, T9, T10). Invoca esqueletos (mini tanques) con mana y recarga.
  Armadura en los mismos tiers. Los libros 3D los hace el dueno: aca solo queda el id del modelo.
- Asesino: cuchillos (los que ya existian). Golpe por la espalda, veneno e invisibilidad (no en PvP).
  Armadura T1-T10.

Los numeros viven aca (una sola fuente). Las habilidades las corre el plugin propio AstralClases
(runtime/AstralClases.java), que lee clases.json dentro del JAR.
Los modelos de armadura son de terceros: su arte va solo al pack FINAL privado (armaduras_t6_10.py,
deploy_clases.py). En el pack publico las piezas no tienen arte propio.

Uso: python clases.py --jdk <bin de JDK 25> --server <Paper local>   (compila AstralClases.jar)
"""
import json
import os
import zipfile
from pathlib import Path

from escala import (DANO, VIDA_SET, DEFENSA_SET, DANO_MOB, MANA_SET_MAGO, MANA_BASTON, REGEN_POR_MANA,
                    TIER_MAZMORRA, fmt)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = ROOT / 'build' / 'clases'
NS = 'astral'

PIEZAS = ('helmet', 'chestplate', 'leggings', 'boots')

# ---------------------------------------------------------------------------------------------- sets
# Modelo elegido por el dueno (ids de armaduras_t6_10.SETS) y nombre de cada tier.
SETS = {
    'segador': {
        'clase': 'Segador', 'color': '#b23a48', 'arma': 'guadana',
        'piezas': {'helmet': 'Capucha', 'chestplate': 'Manto', 'leggings': 'Faldar', 'boots': 'Botas'},
        'tiers': {1: ('picaro', 'del Picaro'), 3: ('guardia_niebla', 'de la Guardia de la Niebla'),
                  5: ('centinela_tumba', 'del Centinela de la Tumba'), 7: ('verdugo_dorado', 'del Verdugo Dorado'),
                  10: ('redentor', 'del Redentor')},
        'base': 'berserker',   # materiales de forja: los del Berserker del mismo tier
    },
    'invocador': {
        'clase': 'Invocador', 'color': '#7b5cff', 'arma': 'libro',
        'piezas': {'helmet': 'Capucha', 'chestplate': 'Tunica', 'leggings': 'Faldones', 'boots': 'Sandalias'},
        'tiers': {1: ('prior_oscuro', 'del Prior Oscuro'), 3: ('medico_peste', 'del Medico de la Peste'),
                  5: ('kintsugi', 'Kintsugi'), 7: ('brujo_errante', 'del Brujo Errante'),
                  9: ('archievocador', 'del Archievocador'), 10: ('prior_dorado', 'del Prior Dorado')},
        'base': 'mago',
    },
    'asesino': {
        'clase': 'Asesino', 'color': '#3fbf8f', 'arma': 'cuchillo',
        'piezas': {'helmet': 'Capucha', 'chestplate': 'Jubon', 'leggings': 'Calzas', 'boots': 'Botas'},
        'tiers': {1: ('asesino', 'del Asesino'), 2: ('encapuchado_verde', 'del Encapuchado Verde'),
                  3: ('asesino_netherita', 'del Asesino de Netherita'), 4: ('dama_cazadora', 'de la Dama Cazadora'),
                  5: ('encapuchado_turquesa', 'del Encapuchado Turquesa'), 6: ('encapuchado_dorado', 'del Encapuchado Dorado'),
                  7: ('fantasma_ocaso', 'del Fantasma del Ocaso'), 8: ('ronin', 'del Ronin'),
                  9: ('valquiria', 'de la Valquiria'), 10: ('caceria_dorada', 'de la Caceria Dorada')},
        'base': 'arquero',
    },
}
SET_IDS = tuple(SETS)
# Modelos sin casco en el mod: el casco conserva su asset_id (cabeza vacia) y un icono con la paleta del set.
SIN_CASCO = {'kintsugi'}

# Stats del set completo (cada pieza da 1/4). Claves comunes con items.ARMOR_SETS (hp, def, spd, crit, mana,
# mregen, cdr) + propias que aplica AstralClases:
#   guadana: % dano con guadana   radio: bloques extra del barrido   tajo: % dano extra del tajo en area
#   cura: % mas de curacion al matar
#   ivida / idano: % vida / dano de las invocaciones
#   critd: % dano critico (AuraSkills crit_damage)
_SEG = {1: (5, 5, .25, 10, 0), 3: (15, 15, .5, 20, 10), 5: (25, 25, .75, 35, 20), 7: (35, 35, 1.0, 50, 30),
        10: (50, 50, 1.5, 75, 40)}
# Regeneracion del Invocador: la mitad que la del Mago del mismo tier (items.ARMOR_SETS/items_t6_10).
_MREGEN_MAGO = {1: 0, 3: 10, 5: 25, 7: 35, 9: 45, 10: 50}
_INV = {1: (10, 10, 0), 3: (20, 20, 0), 5: (30, 30, 5), 7: (40, 40, 10), 9: (50, 50, 10), 10: (60, 60, 15)}
_ASE_CRIT = (4, 7, 10, 14, 18, 22, 26, 30, 34, 38)
_ASE_CRITD = (10, 15, 20, 30, 40, 50, 60, 70, 80, 100)
_ASE_SPD = (3, 5, 7, 9, 11, 13, 15, 17, 19, 21)


def stats(sid, t):
    if sid == 'segador':
        hp, g, r, c, cura = _SEG[t]
        return {'hp': hp, 'guadana': g, 'radio': r, 'tajo': c, 'cura': cura}
    if sid == 'invocador':
        v, d, cdr = _INV[t]
        out = {'mana': round(MANA_SET_MAGO[t] * 0.6), 'mregen': _MREGEN_MAGO[t] // 2, 'ivida': v, 'idano': d,
               'hp': -5, 'def': -10}
        if cdr:
            out['cdr'] = cdr
        return out
    return {'crit': _ASE_CRIT[t - 1], 'critd': _ASE_CRITD[t - 1], 'spd': _ASE_SPD[t - 1], 'hp': -10, 'def': -10}


# Bonus del set completo (4 piezas de la clase, de cualquier tier).
SET_COMPLETO = {
    'segador': 'el tajo en area pega 80% del golpe en vez de 60%',
    'invocador': 'mientras tengas invocaciones vivas recibis 10% menos de dano',
    'asesino': 'despues de matar un mob, el proximo golpe con cuchillo pega doble (x1,5 a jefes)',
}

# ---------------------------------------------------------------------------------------------- Segador
SEGADOR = {
    'radio': 3.5,            # bloques del barrido (semicirculo de 180 grados adelante)
    'angulo': 90,            # grados a cada lado de la mirada
    'barrido_pct': 60,       # % del golpe a cada mob extra
    'barrido_max': 8,        # mobs extra como maximo
    'carga_min': 0.9,        # el barrido solo sale con el golpe cargado (no spam de clic)
    'barrido_pct_set': 80,   # con el set completo de Segador
    'cura_alma': 0.5,        # % de la vida maxima al matar con guadana
    # 23/11: la Cosecha (clic derecho, giro 360) se saco por pedido del dueno.
}

# ---------------------------------------------------------------------------------------------- Asesino
ASESINO = {
    'espalda_pct': 50,       # golpe por la espalda contra mobs
    'espalda_pvp_pct': 15,   # en arenas (lo suma astral_pvp en gameplay.py con la etiqueta astral.espalda)
    'espalda_angulo': 70,    # grados desde la espalda del objetivo
    'veneno_pct': 8,         # % del golpe por segundo
    'veneno_seg': 3,
    'invis_seg': 2,
    'invis_cd': 20,
    'set_kill_mult': 2.0,
    'set_kill_mult_jefe': 1.5,
    'set_kill_seg': 10,
}

# ---------------------------------------------------------------------------------------------- Mobs de mazmorra
# 23/11: pedido del dueno. Siempre agresivos, un poco mas rapidos que el vanilla (sin llegar al jugador corriendo)
# y en el agua se mueven como en tierra y algo mas (asi meterse al agua no sirve para escaparles).
MOBS_MAZMORRA = {
    'velocidad_pct': 15,      # + sobre la velocidad base del mob (zombi 0,23 -> 0,26; jugador corriendo ~0,3 equivalente)
    'agua_pct': 35,           # + extra mientras esta en el agua
    'eficiencia_agua': 1.0,   # water_movement_efficiency (1 = como en tierra)
    'rango_min': 32,          # follow_range minimo
    'busca_radio': 16,        # elige al jugador mas cercano a esta distancia si no tiene objetivo
}

# ---------------------------------------------------------------------------------------------- Invocador
LIBRO_TIERS = (1, 3, 5, 7, 9, 10)
LIBROS = {1: 'Libro Podrido', 3: 'Libro del Muneco Maldito', 5: 'Libro del Evocador', 7: 'Libro de Piel de Dragon',
          9: 'Necronomicon', 10: 'Libro de Oro'}
INVOCADOR = {
    'cantidad': {1: 1, 3: 2, 5: 2, 7: 3, 9: 3, 10: 4},
    'duracion': 20,          # segundos
    'recarga': 30,           # segundos (menos el % de enfriamiento de la armadura)
    # Mana: ~40% del mana maximo del Invocador de ese tier (base 100 + libro + set)
    'mana': {1: 80, 3: 180, 5: 400, 7: 650, 9: 1100, 10: 1400},
    'vida_pct': 25,          # % de la vida de un set completo del tier
    'dano_pct': 30,          # % del golpe de la espada del tier
    'jefe_recibe': 3.0,      # los jefes les pegan x3
    'jefe_dano': 0.5,        # y ellas les pegan la mitad a los jefes
    'provoca_radio': 8,      # mobs que persiguen al dueno a esta distancia de una invocacion la atacan a ella
    'provoca_prob': 0.5,     # por revision (cada segundo)
    'distancia_max': 24,     # mas lejos del dueno: vuelve al lado
    'set_menos_dano': 10,
}
MANA_LIBRO = {t: round(MANA_BASTON[t] * 0.6) for t in LIBRO_TIERS}


def invocacion(t):
    """Vida, defensa y dano de una invocacion de tier t (sin los bonus de armadura)."""
    return {'vida': round(VIDA_SET[t] * INVOCADOR['vida_pct'] / 100),
            'defensa': DEFENSA_SET[t],
            'dano': round(DANO[t] * INVOCADOR['dano_pct'] / 100)}


# ---------------------------------------------------------------------------------------------- items
# 23/11 (dueno): tier 1 mas facil: Defensa 3, Combate 4, Hechiceria 0 (sin baston no se sube Hechiceria).
# 23/11 (dueno): cada armadura pide la skill de su clase en lugar de Defensa.
SKILL_ARMADURA = {'segador': 'fighting', 'invocador': 'sorcery', 'asesino': 'fighting'}
ARMOR_DEFENSE_LEVELS = (3, 10, 14, 18, 22, 26, 30, 34, 38, 42)


def armor_level(sid, t):
    """24/11 (dueno): mismo nivel que el arma de la clase en ese tier (guadana, baston, cuchillo)."""
    from items import SCYTHES, STAFFS, CUCHILLOS
    return {'segador': SCYTHES, 'invocador': STAFFS, 'asesino': CUCHILLOS}[sid][t - 1]['lvl']
NOMBRES_STAT = {'guadana': 'dano con guadana', 'radio': 'bloques de barrido', 'tajo': 'dano del tajo en area',
                'cura': 'curacion al matar', 'ivida': 'vida de invocaciones', 'idano': 'dano de invocaciones',
                'critd': 'dano critico'}


def _texto_stat(k, v):
    if k == 'radio':
        return f'+{str(v).replace(".", ",")} {NOMBRES_STAT[k]}'
    return f'+{v}% {NOMBRES_STAT[k]}'


def _costo(base_set, desde, hasta, armor_sets):
    """Materiales de los tiers (desde, hasta] del set base (se saltean tiers: se pagan todos)."""
    out = []
    for t in range(desde + 1, hasta + 1):
        out += list(armor_sets[base_set]['tiers'][t - 1]['cost'])
    return out


def register(add_item, recipes, txt, armor_attrs, aura_pdc, defensa_pieza, req_line, armor_sets, durability,
             vida_pieza, staffs):
    for sid, s in SETS.items():
        prev = 0
        for t, (vid, nombre) in sorted(s['tiers'].items()):
            st = stats(sid, t)
            lvl = armor_level(sid, t)
            for piece in PIEZAS:
                iid = f'{sid}_{t}_{piece}'
                lore = [txt(f"{s['clase']} {roman(t)}", s['color'])]
                lore += [txt(_texto_stat(k, v), 'light_purple') for k, v in st.items() if k in NOMBRES_STAT]
                lore.append(txt('Cada pieza da 1/4 del bonus', 'dark_gray'))
                lore.append(txt(f"Set completo: {SET_COMPLETO[sid]}"))
                lore.append(req_line(SKILL_ARMADURA[sid], lvl))
                std = {k: v for k, v in st.items() if k in ('hp', 'spd')}
                extra = {'minecraft:max_damage': int(durability[t - 1] * {'helmet': .8, 'chestplate': 1, 'leggings': .95,
                                                                          'boots': .85}[piece]),
                         'minecraft:attribute_modifiers': armor_attrs(iid, piece, 'iron', std, vida=vida_pieza[t]),
                         'minecraft:equippable': {'slot': {'helmet': 'head', 'chestplate': 'chest', 'leggings': 'legs',
                                                           'boots': 'feet'}[piece],
                                                  'asset_id': f'{NS}:{sid}_{t}',
                                                  'equip_sound': 'minecraft:item.armor.equip_iron'}}
                if piece == 'helmet' and vid not in SIN_CASCO:
                    del extra['minecraft:equippable']['asset_id']   # casco 3D: item en la cabeza (pack FINAL)
                traits = []
                if 'mana' in st:
                    traits.append(('max_mana', st['mana'] / 4, 'add'))
                    traits.append(('mana_regen', round(st['mana'] / 4 * REGEN_POR_MANA * (1 + st['mregen'] / 100), 3), 'add'))
                if 'crit' in st:
                    traits.append(('crit_chance', st['crit'] / 4, 'add'))
                if 'critd' in st:
                    traits.append(('crit_damage', st['critd'] / 4, 'add'))
                pdc = aura_pdc('armor', SKILL_ARMADURA[sid], lvl, traits)
                pdc[f'{NS}:clase_set'] = sid
                pdc[f'{NS}:clase_tier'] = t
                astral = {'type': 'armor', 'set': sid, 'tier': t, 'piece': piece,
                          'def': defensa_pieza(t, piece, st.get('def', 0))}
                if 'cdr' in st:
                    astral['cdr'] = int(round(st['cdr'] * 100 / 4))
                add_item(iid, f'minecraft:iron_{piece}', f"{s['piezas'][piece]} {nombre}", s['color'], lore, astral,
                         extra=extra, pdc=pdc, model=f'{NS}:{sid}_{t}_{piece}', glint=False, kind='armor')
                if prev == 0:
                    ings = [('v', f'minecraft:leather_{piece}', 1)] + _costo(s['base'], 0, t, armor_sets)
                else:
                    ings = [('c', f'{sid}_{prev}_{piece}', 1)] + _costo(s['base'], prev, t, armor_sets)
                recipes.append((iid, 1, _juntar(ings), f"Armaduras {s['clase']}"))
            prev = t

    # Libros del Invocador (arma). Mana en la mano como los bastones (60%).
    prev = 0
    for t in LIBRO_TIERS:
        iid = f'libro_invocador_{t}'
        inv = invocacion(t)
        n = INVOCADOR['cantidad'][t]
        lvl = staffs[t - 1]['lvl']
        lore = [txt(f'Invocador {roman(t)}', SETS['invocador']['color']),
                txt(f'Clic derecho: invoca {n} esqueleto{"s" if n > 1 else ""} por {INVOCADOR["duracion"]} s'),
                txt(f"Cada uno: {fmt(inv['vida'])} de vida, {fmt(inv['dano'])} de dano por golpe", 'gray'),
                txt('Atraen a los mobs: te cubren de los golpes', 'gray'),
                txt(f"Costo: {INVOCADOR['mana'][t]} de mana", 'aqua'),
                txt(f"Recarga: {INVOCADOR['recarga']} s", 'green'),
                txt(f'+{MANA_LIBRO[t]} de mana en la mano', 'aqua'),
                req_line('sorcery', lvl)]
        traits = [('max_mana', MANA_LIBRO[t], 'add'), ('mana_regen', round(MANA_LIBRO[t] * REGEN_POR_MANA, 3), 'add')]
        pdc = aura_pdc('item', 'sorcery', lvl, traits)
        pdc['auraskills:ignore_interact'] = True
        pdc[f'{NS}:clase_arma'] = 'libro'
        pdc[f'{NS}:clase_tier'] = t
        add_item(iid, 'minecraft:book', LIBROS[t], SETS['invocador']['color'], lore,
                 {'type': 'book', 'w': 'book', 'tier': t}, pdc=pdc, model=f'{NS}:libro_invocador_{t}', glint=False,
                 extra={'minecraft:max_stack_size': 1})
        cost = _juntar([c for k in range(prev + 1, t + 1) for c in staffs[k - 1]['cost']])
        ings = ([('v', 'minecraft:book', 1)] if prev == 0 else [('c', f'libro_invocador_{prev}', 1)]) + cost
        recipes.append((iid, 1, _juntar(ings), 'Armas Invocador'))
        prev = t


def _juntar(ings):
    out = {}
    for kind, iid, n in ings:
        out[(kind, iid)] = out.get((kind, iid), 0) + n
    return [(k, i, n) for (k, i), n in out.items()]


def roman(t):
    return ('I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X')[t - 1]


# Tier de armadura que corresponde a un tier cualquiera (el ultimo set disponible <= t).
def tier_set(sid, t):
    return max(k for k in SETS[sid]['tiers'] if k <= t)


# ---------------------------------------------------------------------------------------------- runtime
def runtime_data():
    from minijuegos import arena_worlds
    from escala import DANO_MOB as DM, DANO_JEFE as DJ
    return {
        'sets': {sid: {str(t): stats(sid, t) for t in s['tiers']} for sid, s in SETS.items()},
        'segador': SEGADOR, 'asesino': ASESINO,
        'invocador': dict(INVOCADOR, cantidad={str(k): v for k, v in INVOCADOR['cantidad'].items()},
                          mana={str(k): v for k, v in INVOCADOR['mana'].items()},
                          stats={str(t): invocacion(t) for t in LIBRO_TIERS}),
        'dano_mob': {str(k): v for k, v in DM.items()},
        'dano_jefe': {str(k): v for k, v in DJ.items()},   # 23/11: jefes de mazmorra con su escala propia
        'mazmorras': {w: t for w, t in TIER_MAZMORRA.items()},
        # 23/11 (dueno): en estos mundos los mobs son siempre agresivos, algo mas rapidos y no se frenan en el agua.
        'agresivos': sorted(set(TIER_MAZMORRA) | {w for w in __import__('escala').TIER_FIJO if w.startswith('fosa')}
                            | set(__import__('infinita').WORLDS)),
        'agresivos_cfg': MOBS_MAZMORRA,
        'arenas': sorted(arena_worlds()),
        'modelo': 'astral_invocacion',
        'libro_nivel': {str(t): _staff_lvl(t) for t in LIBRO_TIERS},
    }


def _staff_lvl(t):
    from items import STAFFS
    return STAFFS[t - 1]['lvl']


PLUGIN_YML = """name: AstralClases
version: 1.1.0
main: astral.AstralClases
api-version: '26.1.2'
depend: [AuraSkills]
softdepend: [MythicMobs, BetterModel]
description: Clases Segador, Invocador y Asesino (tajo en area, invocaciones, espalda, veneno, invisibilidad)
"""


def mythic_yml():
    """Mob de la invocacion: modelo propio (creatures_tanda3b.invocacion). Vida y dano los pone el plugin."""
    return '\n'.join([
        'astral_invocacion:',
        '  Type: ZOMBIE',
        "  Display: '&5Invocacion'",
        '  Health: 20',
        '  Damage: 1',
        '  Options:',
        '    Silent: true',
        '    PreventSunburn: true',
        '    PreventOtherDrops: true',
        '    PreventItemPickup: true',
        '    Despawn: false',
        '    Persistent: false',
        '    MovementSpeed: 0.3',
        '    FollowRange: 24',
        '    KnockbackResistance: 0.8',
        '  AIGoalSelectors:',
        '  - clear',
        '  - float',
        '  - meleeattack',
        '  - randomlookaround',
        '  AITargetSelectors:',
        '  - clear',
        '  Skills:',
        '  - model{m=astral_invocacion} @self ~onSpawn',
        '  - effect:particles{p=witch;a=6;hs=0.3;vs=0.6;y=1} @self ~onTimer:20',
        ''])


def build_plugin(jdk, server):
    import subprocess
    jdk, server = Path(jdk), Path(server)
    classes = ROOT / '.local' / 'clases-classes'
    classes.mkdir(parents=True, exist_ok=True)
    jars = list((server / 'libraries').rglob('*.jar')) + [server / 'plugins' / 'auraskills.jar',
                                                          server / 'plugins' / 'mythicmobs.jar',
                                                          server / 'plugins' / 'bettermodel.jar']
    javac = [str(jdk / ('java.exe' if os.name == 'nt' else 'java')), '-m', 'jdk.compiler/com.sun.tools.javac.Main']
    subprocess.run([*javac, '-encoding', 'UTF-8', '-source', '25', '-target', '25', '-classpath',
                    os.pathsep.join(map(str, jars)), '-d', str(classes), str(HERE / 'runtime' / 'AstralClases.java')],
                   check=True)
    OUT.mkdir(parents=True, exist_ok=True)
    dest = OUT / 'AstralClases.jar'
    stamp = (2026, 11, 22, 0, 0, 0)
    with zipfile.ZipFile(dest, 'w', zipfile.ZIP_DEFLATED) as z:
        for p in sorted((classes / 'astral').glob('AstralClases*.class')):
            z.writestr(zipfile.ZipInfo(p.relative_to(classes).as_posix(), stamp), p.read_bytes())
        z.writestr(zipfile.ZipInfo('clases.json', stamp), json.dumps(runtime_data(), sort_keys=True))
        z.writestr(zipfile.ZipInfo('plugin.yml', stamp), PLUGIN_YML)
    return dest


def write_outputs():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'MythicMobs').mkdir(exist_ok=True)
    (OUT / 'MythicMobs' / 'astral_clases.yml').write_text(mythic_yml(), encoding='utf-8')
    (OUT / 'clases.json').write_text(json.dumps(runtime_data(), indent=1, sort_keys=True), encoding='utf-8')


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--jdk')
    ap.add_argument('--server', default=str(ROOT / '.local' / 'testsrv'))
    a = ap.parse_args()
    write_outputs()
    if a.jdk:
        print(build_plugin(a.jdk, a.server))
