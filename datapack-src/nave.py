"""Nave del Vacio (evento del End, 22/11/2026): mazmorra tier 5 dentro de la nave con forma de mano, 3 copias.

- Mapa: "spaceship.schem" (TERCEROS: vive solo en .local/nave, nunca en el repo). Se pega con WorldEdit en un
  mundo vacio en ORIGEN (esquina del schematic). Las salas no se conectan caminando: el recorrido es por
  compuertas. Al limpiar una sala se abre la compuerta (centro de la sala); pisarla, o esperar ESPERA_COMPUERTA
  segundos, lleva a todo el grupo a la sala siguiente y la anterior queda cerrada (no se puede volver).
- Si un jugador cae al casco hueco (sale de los limites de su sala) vuelve a la llegada de esa sala.
- Salas: 1 Hangar (pasillo largo) -> 2 Dedo Menor -> 3 Dedo Anular -> 4 Punta del Indice -> 5 Puente de Mando
  (minijefe: Timonel del Vacio) -> 6 Palma (jefe: Capitan del Vacio, mobs/capitan_vacio.py).
- Oleadas, compuertas y jefe: plugin AstralNave (runtime/AstralNave.java, config generada aca).
- Tier 5 fijo con vida x1,5 (como el Santuario). Entrada, party y 8 minutos tras el jefe: mazmorras_copias.py.

python nave.py --java <java25>      -> build/nave/ (AstralNave.jar, comandos.txt), MythicMobs, cofre
python ../tools/nave_salas.py       -> recalcula nave_salas.json desde el schematic (solo si cambian las salas)
"""
import json
import os
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORLDS = ('nave', 'nave_2', 'nave_3')        # 3 copias (pedido del dueno: la mano es muy grande)
NOMBRE = 'Nave del Vacio'
TIER = 5
EXTRA_VIDA = 1.5                              # como el Santuario
ORIGEN = (-80, 40, -100)                      # esquina minima del schematic en el mundo
SCHEM = '.local/nave/spaceship.schem'
ESPERA_COMPUERTA = 20                         # segundos hasta que la compuerta lleva sola al grupo
EXTRA_JUGADOR = 0.5                           # +50% de mobs por cada jugador extra (como la Fosa)

# Salas (coordenadas del SCHEMATIC): caja donde buscar el piso, centro (compuerta / jefe) y llegada aproximada.
SALAS = [
    dict(id='hangar', nombre='Hangar', caja=(5, 22, 78, 74, 44, 200), centro=(59, 185), llegada=(41, 82)),
    dict(id='menor', nombre='Dedo Menor', caja=(43, 65, 119, 73, 69, 153), centro=(58, 136), llegada=(70, 136)),
    dict(id='anular', nombre='Dedo Anular', caja=(66, 68, 72, 88, 76, 117), centro=(77, 106), llegada=(77, 78)),
    dict(id='indice', nombre='Punta del Indice', caja=(68, 52, 7, 93, 60, 54), centro=(81, 45), llegada=(78, 15)),
    dict(id='puente', nombre='Puente de Mando', caja=(95, 74, 75, 126, 79, 126), centro=(106, 114), llegada=(115, 85)),
    dict(id='palma', nombre='Palma', caja=(66, 65, 150, 130, 69, 184), centro=(113, 167), llegada=(72, 167)),
]

# Oleadas por sala para 1-2 jugadores (cada jugador extra suma EXTRA_JUGADOR). Tipos: vanilla con brillo o mobs de
# MythicMobs (prefijo mm:). 'minijefe' y 'jefe' aparecen en el centro de la sala.
OLEADAS = {
    'hangar': [{'enderman': 5, 'endermite': 6}, {'enderman': 6, 'mm:astral_nave_cria': 4}],
    'menor': [{'wither_skeleton': 5, 'enderman': 4}, {'mm:astral_nave_cria': 5, 'vex': 4}],
    'anular': [{'enderman': 6, 'vex': 5}, {'wither_skeleton': 5, 'mm:astral_nave_cria': 5}],
    'indice': [{'enderman': 6, 'endermite': 8}, {'wither_skeleton': 6, 'vex': 5}],
    'puente': [{'minijefe': 1, 'enderman': 4}],
    'palma': [{'jefe': 1}],
}
MINIJEFE = 'astral_nave_timonel'
JEFE = 'astral_nave_capitan'
TOPE = 9                                      # mobs vivos a la vez por sala (como la Forja)
# Vista de la mano desde afuera al entrar (15 s, se saltea agachandose): puntos de la camara y adonde mira
# (x, y, z, mira x, mira y, mira z), en coordenadas del mundo. La nave ocupa x -80..83, y 40..131, z -100..106.
INTRO_RUTA = [(0, 170, -170, 0, 85, 0), (-110, 150, -120, 0, 85, 0), (-150, 115, 10, 0, 85, 10),
              (-115, 95, 130, 0, 85, 30), (-45, 90, 150, -30, 80, 60)]
INTRO_VISTA = 14                              # chunks que se mandan durante la vista (solo a ese jugador)


def salas():
    """Salas con sus coordenadas del mundo (nave_salas.json, sacado del schematic por tools/nave_salas.py)."""
    datos = {s['id']: s for s in json.loads((Path(__file__).parent / 'nave_salas.json').read_text('utf8'))}
    return [dict(s, **datos[s['id']]) for s in SALAS]


def plugin_config():
    L = [f'# Generado por datapack-src/nave.py ({NOMBRE}). Abierta/cerrada: /nave abrir | cerrar (estado.yml).',
         f'mundos: [{", ".join(WORLDS)}]',
         f'espera-compuerta: {ESPERA_COMPUERTA}', f'extra-jugador: {EXTRA_JUGADOR}', f'tope: {TOPE}',
         f'jefe: {JEFE}', f'minijefe: {MINIJEFE}', f'escudo: {__import__("mobs.capitan_vacio", fromlist=["x"]).ESCUDO}',
         'intro:', '  activa: true', f'  distancia-vista: {INTRO_VISTA}',
         '  ruta: [' + ', '.join('"' + ','.join(str(v) for v in r) + '"' for r in INTRO_RUTA) + ']', 'salas:']
    for s in salas():
        f = lambda c: '"' + ','.join(str(v) for v in c) + '"'
        L += [f'  - id: {s["id"]}', f'    nombre: "{s["nombre"]}"', f'    llegada: {f(s["llegada"])}',
              f'    centro: {f(s["centro"])}', f'    limites: {f(s["limites"])}',
              '    puntos: [' + ', '.join(f(p) for p in s['puntos']) + ']',
              '    oleadas:'] + ['      - "' + ','.join(f'{k}:{v}' for k, v in o.items()) + '"' for o in OLEADAS[s['id']]]
    return '\n'.join(L) + '\n'


def llegada():
    """Llegada de la primera sala (x, y, z, yaw) para mazentrar."""
    import math
    s = salas()[0]
    (x, y, z), (cx, _, cz) = s['llegada'], s['centro']
    return (x + 0.5, y, z + 0.5, round(math.degrees(math.atan2(-(cx - x), cz - z))))   # mirando hacia el pasillo


def dungeon():
    """Datos del cofre (cofre_mazmorra.py): tier 5, premios del Santuario (el dueno los puede cambiar)."""
    return {'key': 'nave', 'name': NOMBRE, 'money': 6000, 'reward': [('esencia_elite', 8), ('alma_corrupta', 3)]}


def commands():
    x, y, z = salas()[0]['llegada']
    ox, oy, oz = ORIGEN
    L = [f'# {NOMBRE} (nave.py). Con AstralNave y WorldEdit; subir antes {SCHEM} a plugins/WorldEdit/schematics/spaceship.schem',
         '# 1) Crear los mundos (vacios, el generador es el de AstralOceano):']
    for w in WORLDS:
        L += [f'mv create {w} normal --generator AstralOceano:vacio --no-structures']
    L += ['# 2) Pegar la nave en cada uno (consola). La schematic carga en segundo plano: esperar el mensaje',
          '#    "spaceship.schem loaded" antes de //paste. Despues del paste, revisar un bloque de piso.']
    for w in WORLDS:
        L += [f'//world {w}', f'//pos1 {ox},{oy},{oz}', '//schem load spaceship.schem', '//placement pos1', '//paste -a']
    L += ['# 3) Reglas de cada mundo:']
    for w in WORLDS:
        L += [f'execute in minecraft:{w} run setworldspawn {x} {y} {z}',
              *[f'execute in minecraft:{w} run gamerule minecraft:{g}' for g in
                ('spawn_mobs false', 'mob_griefing false', 'advance_time false', 'advance_weather false',
                 'keep_inventory true', 'fall_damage false')],
              f'rg flag -w {w} __global__ block-break deny', f'rg flag -w {w} __global__ block-place deny',
              f'rg flag -w {w} __global__ pvp deny', f'rg flag -w {w} __global__ enderpearl deny',
              f'rg flag -w {w} __global__ chorus-fruit-teleport deny']
    return '\n'.join(L) + '\n'


def mythic():
    """MythicMobs: jefe, minijefe, crias, Ojos Vigias, cofre y guia."""
    from mobs import capitan_vacio as cv
    return cv.mobs_yaml(), cv.skills_yaml()


def premio_block():
    """Cofre y guia al ganar (los pone AstralNave en el centro de la Palma; tag nave.premio)."""
    return f'''
astral_nave_cofre:
  Type: SHEEP
  Display: '&6&lCofre de la {NOMBRE} &7(clic)'
  Health: 100
  Options:
    NoAI: true
    Invincible: true
    Silent: true
    Despawn: false
    Persistent: true
    Collidable: false
    PreventItemPickup: true
    PreventOtherDrops: true
    AlwaysShowName: true
  Skills:
  - addtag{{tag=nave.premio}} @self ~onSpawn
  - addtag{{tag=astral.seen}} @self ~onSpawn
  - cancelevent @self ~onInteract
  - model{{m=astral_cofre_rpg}} @self ~onSpawn
  - model{{m=astral_cofre_rpg}} @self ~onLoad
  - state{{s=open}} @self ~onInteract
  - command{{c="dm open cofre_nave <trigger.name>"}} @self ~onInteract
astral_nave_guia:
  Type: VILLAGER
  Display: '&b&lExpediciones Astrales &7- elegir destino'
  Health: 100
  Options:
    NoAI: true
    Invincible: true
    Silent: true
    Despawn: false
    Persistent: true
    Collidable: false
    PreventItemPickup: true
    PreventOtherDrops: true
    AlwaysShowName: true
    Profession: CARTOGRAPHER
    VillagerType: PLAINS
  Skills:
  - addtag{{tag=nave.premio}} @self ~onSpawn
  - addtag{{tag=astral.seen}} @self ~onSpawn
  - cancelevent @self ~onInteract
  - skill{{s=AST_NPC_mago}} @self ~onSpawn
  - skill{{s=AST_NPC_mago}} @self ~onLoad
  - state{{s=saludo}} @self ~onInteract
  - command{{c="dm open expediciones <trigger.name>"}} @self ~onInteract
'''


def build_plugin(java):
    """Compila AstralNave.jar con las librerias del Paper local (.local/testsrv)."""
    srv = ROOT / '.local/testsrv'
    target = ROOT / '.local/nave-classes'
    target.mkdir(parents=True, exist_ok=True)
    deps = [*srv.joinpath('libraries').rglob('*.jar'), *srv.joinpath('versions').rglob('*.jar')]
    subprocess.run([str(java), '-m', 'jdk.compiler/com.sun.tools.javac.Main', '-encoding', 'UTF-8', '-nowarn',
                    '-classpath', os.pathsep.join(map(str, deps)), '-d', str(target),
                    str(ROOT / 'datapack-src/runtime/AstralNave.java')], check=True)
    dest = ROOT / 'build/nave/AstralNave.jar'
    dest.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(dest, 'w', zipfile.ZIP_DEFLATED) as z:
        for p in sorted((target / 'astral').glob('AstralNave*.class')):
            z.writestr(zipfile.ZipInfo('astral/' + p.name, (2026, 11, 22, 0, 0, 0)), p.read_bytes())
        z.writestr('plugin.yml', "name: AstralNave\nversion: 1.0.0\nmain: astral.AstralNave\napi-version: '26.1.2'\n"
                                 "depend: [MythicMobs]\ncommands:\n  nave:\n    permission: astral.nave.admin\n")
        z.writestr('config.yml', plugin_config())
    return dest


def generate(java=None):
    out = []
    mobs_yml, skills_yml = mythic()
    m = ROOT / 'build/mythicmobs/mobs/nave.yml'
    m.parent.mkdir(parents=True, exist_ok=True)
    m.write_text(f'# Generado por nave.py: {NOMBRE} (tier 5).\n' + mobs_yml + premio_block(), encoding='utf-8')
    s = ROOT / 'build/mythicmobs/skills/nave.yml'
    s.parent.mkdir(parents=True, exist_ok=True)
    s.write_text(skills_yml, encoding='utf-8')
    c = ROOT / 'build/nave/comandos.txt'
    c.parent.mkdir(parents=True, exist_ok=True)
    c.write_text(commands(), encoding='utf-8')
    (ROOT / 'build/nave/config.yml').write_text(plugin_config(), encoding='utf-8')
    out += [m, s, c]
    if java:
        out.append(build_plugin(java))
    return out


if __name__ == '__main__':
    import argparse
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument('--java', help='java 25 (para compilar AstralNave.jar)')
    args = a.parse_args()
    for p in generate(args.java):
        print(p)
