# -*- coding: utf-8 -*-
"""Vacio Estelar (plan E6 / 7f, 23/11/2026). FUENTE UNICA.

Dimension de late game: islas flotantes en el espacio (end stone, purpur, obsidiana), de noche siempre y con gravedad
baja. Las mismas 7 gemas de las Cavernas de Cristal pero mejores: vetas Impecables (comun), Perfectas (raras) y
Estelares (muy raras). Plugin propio AstralVacio (modelo: AstralCavernas) con generador, reglas, mobs, venta,
meteoritos y regeneracion cada 3 dias.

- Entrada: /vacio (o el boton del menu de Portales). Requisito: Santuario ganado o equipo tier 6.
- Vetas = bloque de nota en campanilla (chime): gema t normal = nota t (0-6), nucleo de meteorito de esa gema = 7+t,
  Fragmento Estelar = 14, Nucleo de Meteorito (llave del jefe) = 15. Taladro tier 6 o mejor.
- Meteorito cada 20-30 min: aviso global, cae en una isla cerca de un jugador, deja un crater con vetas de nucleo
  (Perfecta/Estelar) y Nucleos de Meteorito; desaparece a los 6 min.
- Altar (piedra iman de la isla central) + Nucleo de Meteorito = Coloso Estelar (jefe tier 8).
- Mobs tier 6 (centro), 7 (> 200 bloques) y 8 (> 400): Golem, Acechador y Ojo del Vacio (vuela). Cada meteorito trae
  3 guardianes. Coloso con el modelo del Capitan del Vacio. Barril del campamento: venta.

Salidas: python vacio.py [--jdk <bin JDK 25>]
  datapack (build.py: register, tabla_note_block, mob_roll, tool_mine_lines)
  build/vacio/AstralVacio.jar (con --jdk), config.yml, comandos.txt
  build/mythicmobs/mobs/vacio.yml
"""
import argparse
import json
import os
import subprocess
import zipfile
from pathlib import Path

import gemas as G

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = ROOT / 'build' / 'vacio'
NS = 'astral'
WORLD = 'vacio_estelar'
VERSION = '1.1.0'
STAMP = (2026, 11, 23, 0, 0, 0)
RADIO = 600                       # borde 1.200 x 1.200
CELDA = 72                        # una isla (o hueco) por celda de 72 x 72
CENTRO_R, CENTRO_Y = 34, 92       # isla central (campamento)
REGENERAR_HORAS = 72
AVISOS_MIN = (10, 5, 1)
TIER = 6                          # centro; 7 a mas de TIER7_D bloques; 8 a mas de TIER8_D
TIER7_D, TIER8_D = 200, 400
DRILL_TIER = 6
METEORO_MIN, METEORO_MAX, METEORO_DURA = 20, 30, 360
GRAVEDAD_PCT, SALTO_PCT, CAIDA_SEGURA = -35, 20, 8
INSTRUMENTO = 'chime'
NOTA_FRAGMENTO, NOTA_NUCLEO = 14, 15
# Pesos por mil de Cruda, Pulida, Impecable, Perfecta, Estelar (las Cavernas casi nunca dan Perfecta/Estelar).
CALIDAD = {'normal': (0, 0, 880, 110, 10), 'meteoro': (0, 0, 450, 450, 100)}

ITEMS = {
    'fragmento_estelar': ('Fragmento Estelar', '#b9a4ff', 'Se vende en el barril del Vacio Estelar.'),
    'nucleo_meteorito': ('Nucleo de Meteorito', '#ff8a5c', 'Sale de los meteoritos. En el altar despierta al Coloso Estelar.'),
}
# Plata por hora (cuenta documentada): buscando vetas a la vista ~600 Fragmentos/h + ~2 meteoritos/h con ~1 Nucleo c/u.
#   600 x 110.000 = 66M  +  2 x 3.000.000 = 6M  ->  ~72M/h sin contar las gemas (Perfectas/Estelares valen mucho mas en la
#   Reforja). Con taladro en area y mobs tier 8 se llega a ~120-150M/h. Objetivo del plan: 50-150M/h.
PRECIOS = dict(__import__('economia').VACIO_PRECIO)   # 25/11: bajado con el recorte de las Minas (ver economia.py)
SELECTIVO_HORA = {'fragmento_estelar': 600, 'nucleo_meteorito': 2}


def plata_hora():
    return sum(SELECTIVO_HORA[k] * PRECIOS[k] for k in PRECIOS)


# ------------------------------------------------------------------ mobs (MythicMobs; vida base x tier en mob/roll)
# id: (nombre, tipo, modelo, escala, tinte, vida, dano, velocidad)
MOBS = {
    'astral_vac_golem': ('&5Golem de Meteorito', 'ZOMBIE', 'astral_golem_cristal', 1.7, '7A4CFF', 40, 8, 0.25),
    'astral_vac_acechador': ('&dAcechador Estelar', 'ZOGLIN', 'astral_arana', 1.3, 'B89CFF', 30, 7, 0.33),
    # 24/11: vuela (el modelo de los Ojos Vigias de la Nave) y dispara rayos; aparece en el aire aunque la isla sea chica.
    'astral_vac_ojo': ('&aOjo del Vacio', 'VEX', 'astral_ojo_vigia', 1.5, None, 22, 6, 0.3),
}
VOLADOR = 'astral_vac_ojo'
MOBS_TANDA, MOBS_CERCA, MOBS_TOPE = 2, 7, 90   # por jugador cada 3 s / cerca de cada jugador / en todo el mundo
GUARDIANES = 3                                 # monstruos que aparecen con cada meteorito
CAMPAMENTO_R = 16                              # zona sin monstruos alrededor del centro
JEFE = 'astral_vac_coloso'
JEFE_NOMBRE = '&d&lColoso Estelar'
# 24/11: el Coloso usa el modelo del Capitan del Vacio (mobs/capitan_vacio.py) y sus ataques (cubo, salto, barrido);
# a la mitad de vida llama Ojos del Vacio.
JEFE_OJOS = 3
JEFE_ALTO = 5                     # bloques (pedido del dueno 23/11); AstralTamanos pone la caja al 90%
JEFE_BARRA = '&5✦ Tier VIII ✦ &d&lColoso Estelar'
JEFE_TIER = 8
VIDA_JEFE, DANO_JEFE = 600, 16
# Botin del Coloso: (item, chance). Gemas: 1 Perfecta segura de una gema al azar, Estelar 10%.
EQUIPO_JEFE = [f'{c}_7_{p}' for c in ('mago', 'berserker', 'arquero') for p in ('helmet', 'chestplate', 'leggings', 'boots')]


def _estado(nota):
    return {'instrument': INSTRUMENTO, 'note': str(nota)}


def _taladro_ok():
    return {'condition': 'minecraft:any_of', 'terms': [
        {'condition': 'minecraft:match_tool', 'predicate': {'predicates': {
            'minecraft:custom_data': '{astral:{tool:"drill",tier:%d}}' % t}}} for t in range(DRILL_TIER, 11)]}


NOTAS = list(range(16))


# ------------------------------------------------------------------ datapack
def register(put, fn, add_item, txt):
    for iid, (nombre, color, desc) in ITEMS.items():
        add_item(iid, 'minecraft:paper', nombre, color, [txt(desc), txt('Vacio Estelar', 'dark_gray')],
                 {'type': 'vacio'}, model=f'{NS}:vacio/{iid}', glint=iid == 'nucleo_meteorito', kind='vacio')
    from escala import VIDA_REF
    fn('vacio/jefe', [f'attribute @s minecraft:max_health base set {30 * VIDA_REF[JEFE_TIER]}',
                      'data modify entity @s Health set value 1.0E30f', f'scoreboard players set @s astral.mt {JEFE_TIER}',
                      f'tag @s add astral.mt{JEFE_TIER}', 'tag @s add astral.seen', 'tag @s add ad.boss.scaled'])


def mob_roll():
    """Lineas para mob/roll: tier 7 a mas de TIER7_D bloques del centro y 8 a mas de TIER8_D (despues del TIER_FIJO 6)."""
    out = []
    for t, d in ((7, TIER7_D), (8, TIER8_D)):
        out.append(f'execute if dimension minecraft:{WORLD} unless entity @s[x={-d},z={-d},y=-64,dx={2 * d},dz={2 * d},dy=400] '
                   f'run scoreboard players set #mt astral.tmp {t}')
    return out


def tool_mine_lines():
    """tool/mine (taladro en area del datapack): fuera del Vacio una veta se borra sin soltar nada."""
    return [f'execute unless dimension minecraft:{WORLD} if block ~ ~ ~ minecraft:note_block[instrument={INSTRUMENTO},note={n}] '
            'run return run setblock ~ ~ ~ minecraft:air' for n in NOTAS]


def tabla_note_block(files):
    """Agrega las vetas del Vacio a la tabla del bloque de nota y saca la campanilla 0-15 de la entrada comun."""
    path = 'data/minecraft/loot_table/blocks/note_block.json'
    table = json.loads(files[path])
    pools = []
    for i, t in enumerate(G.TIPOS):
        for nota, tabla in ((i, 'normal'), (7 + i, 'meteoro')):
            pools.append({'rolls': 1, 'conditions': [
                {'condition': 'minecraft:block_state_property', 'block': 'minecraft:note_block', 'properties': _estado(nota)},
                _taladro_ok()], 'entries': [{'type': 'minecraft:loot_table', 'value': f'{NS}:item/{G.item_id(t, q)}', 'weight': w}
                                            for q, w in enumerate(CALIDAD[tabla], 1) if w]})
    for iid, nota in (('fragmento_estelar', NOTA_FRAGMENTO), ('nucleo_meteorito', NOTA_NUCLEO)):
        pools.append({'rolls': 1, 'conditions': [
            {'condition': 'minecraft:block_state_property', 'block': 'minecraft:note_block', 'properties': _estado(nota)},
            _taladro_ok()], 'entries': [{'type': 'minecraft:loot_table', 'value': f'{NS}:item/{iid}'}]})
    table['pools'] = pools + table['pools']
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


# ------------------------------------------------------------------ MythicMobs
def mythic_yaml():
    from mobs.mythic import astral_drop
    L = ['# Generado por datapack-src/vacio.py (plan E6 / 7f). Mobs del Vacio Estelar (los aparece AstralVacio).', '']

    def comun(mid, nombre, tipo, modelo, escala, tinte, vida, dano, vel, barra=None):
        out = [f'{mid}:', f'  Type: {tipo}', f"  Display: '{nombre}'", f'  Health: {vida}', f'  Damage: {dano}',
               '  Options:', '    Silent: true', '    PreventOtherDrops: true', '    PreventSunburn: true',
               '    PreventRandomEquipment: true', '    PreventItemPickup: true', f'    MovementSpeed: {vel}',
               f"    Despawn: {'false' if barra else 'true'}", '    FollowRange: 40']
        if barra:
            out += ['    KnockbackResistance: 0.9']
        if tipo != 'VEX':   # el Vex usa su IA propia (vuela y embiste)
            out += ['  AIGoalSelectors:', '  - clear', '  - meleeattack', '  - randomstroll', '  - lookatplayers']
        out += ['  AITargetSelectors:', '  - clear', '  - attacker', '  - players']
        if barra:
            out += ['  BossBar:', '    Enabled: true', f"    Title: '{nombre}'", '    Range: 64', f'    Color: {barra}',
                    '    Style: SEGMENTED_10']
        sk = [f'- model{{m={modelo};s={escala}}} @self ~onSpawn', f'- model{{m={modelo};s={escala}}} @self ~onLoad']
        if tinte:
            sk += [f'- tint{{c={tinte}}} @self ~onSpawn', f'- tint{{c={tinte}}} @self ~onLoad']
        sk += ['- state{s=attack} @self ~onAttack', '- skill{s=AST_MUERTE} @self ~onDeath',
              '- sound{s=block.amethyst_block.hit;v=0.8;p=0.6} @self ~onDamaged',
              "- effect:particles{p=end_rod;a=4;hs=0.4;vs=0.8;y=1} @self ~onTimer:20"]
        return out, sk

    for mid, (nombre, tipo, modelo, escala, tinte, vida, dano, vel) in MOBS.items():
        out, sk = comun(mid, nombre, tipo, modelo, escala, tinte, vida, dano, vel)
        if tipo == 'VEX':
            sk += [f'- command{{c="attribute <caster.uuid> minecraft:scale base set {escala}"}} @self ~onSpawn',
                   '- skill{s=NAVE_OJO_RAYO} @PlayersInRadius{r=24;sort=NEAREST;limit=1} ~onTimer:70']
        sk += ['- addtag{tag=vac.mob} @self ~onSpawn',
               '- command{c="execute as <caster.uuid> at @s run function astral:mob/roll"} @self ~onSpawn',
               '- skill{s=AST_PLATA_HOSTIL} @self ~onDeath ?~isplayer']
        sk += astral_drop('fragmento_estelar', 0.4) + astral_drop('nucleo_meteorito', 0.004)
        L += out + ['  Skills:'] + ['  ' + s for s in sk] + ['']
    from mobs import capitan_vacio as cv
    s_jefe = round(JEFE_ALTO / cv.alto_modelo(), 3)
    out, sk = comun(JEFE, JEFE_NOMBRE, 'ZOMBIE', cv.MODEL_ID, s_jefe, None, VIDA_JEFE, DANO_JEFE, 0.27, barra='PURPLE')
    out = [f"    Title: '{JEFE_BARRA}'" if l.startswith('    Title:') else l for l in out]
    sk += ['- command{c="attribute <caster.uuid> minecraft:step_height base set 2"} @self ~onSpawn',
           '- state{s=aparece} @self ~onSpawn',
           '- addtag{tag=vac.mob} @self ~onSpawn', '- addtag{tag=vac.jefe} @self ~onSpawn',
           '- command{c="execute as <caster.uuid> run function astral:vacio/jefe"} @self ~onSpawn',
           '- skill{s=AST_PLATA_JEFE} @self ~onDeath ?~isplayer',
           '- skill{s=NAVE_CAP_CUBO} @PlayersInRing{min=5;max=40;sort=RANDOM;limit=1} ~onTimer:120',
           '- skill{s=NAVE_CAP_SALTO} @PlayersInRadius{r=40;sort=RANDOM;limit=1} ~onTimer:260',
           '- skill{s=NAVE_CAP_BARRIDO} @self ~onTimer:180 ?playerwithin{d=7}',
           # a la mitad de vida llama Ojos del Vacio (summon antes del addtag: las dos lineas miran la misma etiqueta)
           f'- summon{{type={VOLADOR};amount={JEFE_OJOS};radius=5;yRadius=3}} @self ~onDamaged ?healthpercent{{p=<0.5}} ?!hastag{{tag=vac.f2}}',
           "- message{m='&5El Coloso Estelar llama a los Ojos del Vacio.'} @PlayersInRadius{r=48} ~onDamaged ?healthpercent{p=<0.5} ?!hastag{tag=vac.f2}",
           '- addtag{tag=vac.f2} @self ~onDamaged ?healthpercent{p=<0.5}']
    for t in G.TIPOS:
        sk += astral_drop(G.item_id(t, 4), round(1 / len(G.TIPOS), 4)) + astral_drop(G.item_id(t, 5), round(0.10 / len(G.TIPOS), 4))
    sk += astral_drop('fragmento_estelar', 1.0, 12)
    for iid in EQUIPO_JEFE:
        sk += astral_drop(iid, round(0.15 / len(EQUIPO_JEFE), 4))
    L += out + ['  Skills:'] + ['  ' + s for s in sk] + ['']
    return '\n'.join(L)


# ------------------------------------------------------------------ menu, comandos y config
def portales_button(slot):
    return {'material': 'END_CRYSTAL', 'slot': slot, 'display_name': '&5&lVacio Estelar',
            'lore': ['&7Islas flotantes con gemas &fImpecables&7,', '&dPerfectas &7y &bEstelares&7. Meteoritos y el Coloso.',
                     '&7Santuario ganado o equipo tier 6.', '', '&eClic para entrar.'],
            'click_commands': ['[close]', '[player] vacio entrar<delay=3>']}


def commands():
    w = WORLD
    return '\n'.join([
        '# Vacio Estelar (vacio.py). Con AstralVacio instalado y el server encendido:',
        f'mv create {w} normal -g AstralVacio --no-adjust-spawn',
        'vacio crear',
        f'execute in minecraft:{w} run gamerule minecraft:advance_time false',
        f'execute in minecraft:{w} run gamerule minecraft:advance_weather false',
        f'execute in minecraft:{w} run gamerule minecraft:spawn_monsters false',
        f'execute in minecraft:{w} run gamerule minecraft:spawn_mobs false',
        f'execute in minecraft:{w} run time set 18000',
        f'execute in minecraft:{w} run worldborder center 0 0',
        f'execute in minecraft:{w} run worldborder set {RADIO * 2}',
        f'rg flag -w {w} __global__ pvp deny',
        f'lp group default permission set astral.vacio.entrar true',
    ]) + '\n'


def config():
    return {'mundo': WORLD, 'radio': RADIO, 'celda': CELDA, 'centro-radio': CENTRO_R, 'centro-y': CENTRO_Y,
            'regenerar-cada-horas': REGENERAR_HORAS, 'avisos-minutos': list(AVISOS_MIN), 'proxima-regeneracion': 0,
            'taladro-tier': DRILL_TIER, 'mobs-cerca': MOBS_CERCA, 'mobs-tope': MOBS_TOPE, 'mobs-tanda': MOBS_TANDA,
            'meteoro-guardianes': GUARDIANES, 'campamento-radio': CAMPAMENTO_R, 'volador': VOLADOR,
            'meteoro-min': METEORO_MIN, 'meteoro-max': METEORO_MAX, 'meteoro-dura-seg': METEORO_DURA,
            'gravedad-pct': GRAVEDAD_PCT, 'salto-pct': SALTO_PCT, 'caida-segura': CAIDA_SEGURA,
            'mobs': list(MOBS), 'jefe': JEFE, 'jefe-vida': 30 * __import__('escala').VIDA_REF[JEFE_TIER], 'permiso-santuario': 'astral.fragmento.corazon', 'precios': dict(PRECIOS)}


PLUGIN_YML = f"""name: AstralVacio
version: {VERSION}
main: astral.AstralVacio
api-version: '26.1.2'
load: STARTUP
softdepend: [Multiverse-Core, MythicMobs, Essentials]
commands:
  vacio:
    description: Vacio Estelar (entrar, vender, estado; admin meteorito, jefe, regenerar, crear)
permissions:
  astral.vacio.admin:
    default: op
  astral.vacio.editar:
    default: op
"""


def build_plugin(jdk, server):
    import yaml
    jdk, server = Path(jdk), Path(server)
    classes = ROOT / '.local' / 'vacio-classes'
    classes.mkdir(parents=True, exist_ok=True)
    jars = list((server / 'libraries').rglob('*.jar'))
    javac = [str(jdk / ('java.exe' if os.name == 'nt' else 'java')), '-m', 'jdk.compiler/com.sun.tools.javac.Main']
    subprocess.run([*javac, '-encoding', 'UTF-8', '-source', '25', '-target', '25', '-nowarn', '-classpath',
                    os.pathsep.join(map(str, jars)), '-d', str(classes), str(HERE / 'runtime' / 'AstralVacio.java')], check=True)
    OUT.mkdir(parents=True, exist_ok=True)
    dest = OUT / 'AstralVacio.jar'
    with zipfile.ZipFile(dest, 'w', zipfile.ZIP_DEFLATED) as z:
        for p in sorted((classes / 'astral').glob('AstralVacio*.class')):
            z.writestr(zipfile.ZipInfo(p.relative_to(classes).as_posix(), STAMP), p.read_bytes())
        z.writestr(zipfile.ZipInfo('plugin.yml', STAMP), PLUGIN_YML)
        z.writestr(zipfile.ZipInfo('config.yml', STAMP), yaml.safe_dump(config(), allow_unicode=True, sort_keys=False))
    return dest


def generate():
    import yaml
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'config.yml').write_text(yaml.safe_dump(config(), allow_unicode=True, sort_keys=False), encoding='utf-8')
    (OUT / 'comandos.txt').write_text(commands(), encoding='utf-8')
    mm = ROOT / 'build' / 'mythicmobs' / 'mobs'
    mm.mkdir(parents=True, exist_ok=True)
    (mm / 'vacio.yml').write_text(mythic_yaml(), encoding='utf-8')
    return OUT


# ------------------------------------------------------------------ pack (vetas e items)
def texturas():
    """Vetas: roca del espacio (end stone oscurecido) con la gema incrustada; las de meteorito sobre magma oscuro."""
    from PIL import Image
    import cavernas as C
    out = {}
    for i, t in enumerate(G.TIPOS):
        for nombre, oscura, q in ((f'veta_{t}', False, 3), (f'veta_{t}_meteoro', True, 5)):
            roca = C._roca(oscura, 700 + i * 7 + (1 if oscura else 0))
            roca = C._tenir(roca, (90, 60, 140) if not oscura else (150, 60, 40), 0.45)
            out['block/' + nombre] = C._incrustar(roca, C._gema(t, q))
    frag = C._tenir(C._roca(False, 931), (150, 120, 230), 0.5)
    out['block/veta_fragmento'] = C._incrustar(frag, C._gema('amatista', 3).convert('RGBA'))
    nuc = C._tenir(C._roca(True, 932), (230, 110, 60), 0.6)
    out['block/veta_nucleo'] = C._incrustar(nuc, C._gema('rubi', 5))
    out['item/fragmento_estelar'] = C._gema('amatista', 4).resize((16, 16), Image.Resampling.LANCZOS)
    out['item/nucleo_meteorito'] = C._gema('rubi', 5).resize((16, 16), Image.Resampling.LANCZOS)
    return out


def _nombres():
    n = {i: f'veta_{t}' for i, t in enumerate(G.TIPOS)}
    n.update({7 + i: f'veta_{t}_meteoro' for i, t in enumerate(G.TIPOS)})
    n.update({NOTA_FRAGMENTO: 'veta_fragmento', NOTA_NUCLEO: 'veta_nucleo'})
    return n


def parchar_note_block(bs):
    """El modelo comun del bloque de nota deja de aplicarse a la campanilla 0-15 y se suman las vetas del Vacio."""
    parts = bs['multipart']
    comun = next(p for p in parts if p['apply'].get('model') == 'minecraft:block/note_block')
    ors = comun['when']['OR']
    instr = next(o for o in ors if set(o) == {'instrument'})
    lista = instr['instrument'].split('|')
    if INSTRUMENTO in lista:
        instr['instrument'] = '|'.join(i for i in lista if i != INSTRUMENTO)
        ors.append({'instrument': INSTRUMENTO, 'note': '|'.join(str(n) for n in range(25) if n not in NOTAS)})
    nombres = _nombres()
    parts[:] = [p for p in parts if not p['apply'].get('model', '').startswith(f'{NS}:block/vacio/')] + [
        {'when': {'instrument': INSTRUMENTO, 'note': str(n)}, 'apply': {'model': f'{NS}:block/vacio/{nombres[n]}'}} for n in NOTAS]
    return bs


def pack_assets():
    import io
    files = {}
    for nombre, im in texturas().items():
        kind, base = nombre.split('/')
        buf = io.BytesIO(); im.save(buf, 'PNG')
        files[f'assets/{NS}/textures/{kind}/vacio/{base}.png'] = buf.getvalue()
        if kind == 'block':
            files[f'assets/{NS}/models/block/vacio/{base}.json'] = json.dumps(
                {'parent': 'minecraft:block/cube_all', 'textures': {'all': f'{NS}:block/vacio/{base}'}}).encode()
        else:
            files[f'assets/{NS}/models/item/vacio/{base}.json'] = json.dumps(
                {'parent': 'minecraft:item/generated', 'textures': {'layer0': f'{NS}:item/vacio/{base}'}}).encode()
            files[f'assets/{NS}/items/vacio/{base}.json'] = json.dumps(
                {'model': {'type': 'minecraft:model', 'model': f'{NS}:item/vacio/{base}'}}).encode()
    return files


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--jdk')
    ap.add_argument('--server', default=str(ROOT / '.local' / 'testsrv'))
    a = ap.parse_args()
    print(generate())
    print('plata/hora estimada:', f'{plata_hora():,}')
    if a.jdk:
        print(build_plugin(a.jdk, a.server))
