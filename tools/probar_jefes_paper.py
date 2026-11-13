"""Prueba local de jefes agresivos y noche fija (13/11/2026). Nunca se conecta al servidor remoto.

Requiere un Paper de pruebas detenido dentro de .local con MythicMobs, BetterModel y Skript, y JDK 25:
  python tools/probar_jefes_paper.py --java <java25.exe> --server .local/tanda3b-paper
Comprueba: MythicMobs carga los jefes y las skills sin errores, el golpe al piso (blockwave) no cambia
bloques ni deja entidades, el disparo y el salto corren, y el script de noche de Skript carga.
"""
import argparse
from pathlib import Path
import re
import shutil
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
JEFES = ['astral_cumbre_yeti', 'astral_tumba_momia', 'astral_bosque_chaman', 'astral_forja_golem_forja',
         'astral_mina_guardian', 'astral_mina_capataz', 'astral_mina_golem', 'astral_yeti', 'astral_cangrejo',
         'astral_golem_forja_ancestral', 'astral_santuario_coloso_musgoso_eco']
PROBE_MOBS = '''jefes_probe_caster:
  Type: ZOMBIE
  Options:
    Silent: true
    PreventSunburn: true
  AIGoalSelectors:
  - clear
  Skills:
  - skill{s=AST_JEFE_SLAM_astral_yeti} @self ~onSpawn
  - skill{s=AST_JEFE_DISPARO_astral_golem_forja} @EntitiesInRadius{r=30;ignore=self} ~onSpawn
  - delay 30
  - skill{s=AST_JEFE_SALTO} @EntitiesInRadius{r=30;ignore=self} ~onSpawn
'''
PROBE_SK = '''on load:
    wait 3 seconds
    set time in world "visual-test" to 0:00
    execute console command "say JEFES_PROBE time set"
'''


def run(java, server):
    if not server.resolve().is_relative_to(ROOT / '.local'):
        raise ValueError('Solo servidores de prueba dentro de .local')
    plugins = server / 'plugins'
    for p in (ROOT / 'build/models').glob('*.bbmodel'):
        shutil.copy2(p, plugins / 'BetterModel/models' / p.name)
    for sub in ('mobs', 'skills'):
        dest = plugins / 'MythicMobs' / sub
        dest.mkdir(parents=True, exist_ok=True)
        for p in (ROOT / 'build/mythicmobs' / sub).glob('*.yml'):
            shutil.copy2(p, dest / p.name)
    (plugins / 'MythicMobs/mobs/jefes_probe.yml').write_text(PROBE_MOBS, encoding='utf8')
    scripts = plugins / 'Skript/scripts'
    shutil.copy2(ROOT / 'build/mazmorras/astral_mazmorras_copias.sk', scripts / 'astral_mazmorras_copias.sk')
    (scripts / 'jefes_probe.sk').write_text(PROBE_SK, encoding='utf8')
    work = ROOT / '.local/jefes-probe'
    work.mkdir(exist_ok=True)
    log = work / 'paper.log'
    with log.open('w', encoding='utf8') as out:
        process = subprocess.Popen([str(java), '-Dterminal.jline=false', '-Dterminal.ansi=false', '-Xms512M', '-Xmx3G',
                                    '-jar', 'paper.jar', '--nogui'], cwd=server, stdin=subprocess.PIPE, stdout=out,
                                   stderr=subprocess.STDOUT, text=True)

        def command(text):
            process.stdin.write(text + '\n')
            process.stdin.flush()
        try:
            deadline = time.monotonic() + 240
            while 'For help, type' not in log.read_text(encoding='utf8', errors='replace'):
                if process.poll() is not None or time.monotonic() > deadline:
                    raise RuntimeError('Paper no arranco')
                time.sleep(1)
            time.sleep(8)
            command('minecraft:forceload add -16 -16 64 64')
            command('minecraft:fill -10 99 -10 30 99 30 minecraft:stone')
            command('minecraft:fill -10 95 -10 30 95 30 minecraft:stone')
            command('minecraft:fill -10 100 -10 30 106 30 minecraft:air')
            time.sleep(1)
            command('minecraft:summon minecraft:villager 10 100 24 {NoAI:1b,Tags:["jefes.probe"]}')
            command('mm mobs spawn jefes_probe_caster 1 visual-test,10,100,10')
            time.sleep(6)
            command('say JEFES_PROBE blocks:')
            command('execute if blocks -10 99 -10 30 99 30 -10 95 -10 all')
            command('say JEFES_PROBE falling:')
            command('execute if entity @e[type=minecraft:falling_block]')
            for i, mid in enumerate(JEFES):
                command(f'mm mobs spawn {mid} 1 visual-test,{-200 - i * 30},100,0')
            time.sleep(6)
            command('say JEFES_PROBE daytime:')
            command('time query daytime')
            command('minecraft:kill @e[type=!minecraft:player]')
        finally:
            if process.poll() is None:
                command('stop')
                process.wait(timeout=90)
    text = log.read_text(encoding='utf8', errors='replace')
    errores = [l for l in text.splitlines() if re.search(r'(ERROR|WARN).*(Mythic|Skript|AST_JEFE|mechanic|targeter|condition)', l, re.I)
               or ('AST_JEFE' in l and re.search('error|invalid|unknown|could not', l, re.I))]
    interesantes = [l for l in text.splitlines() if 'JEFES_PROBE' in l or 'Test passed' in l or 'Test failed' in l
                    or 'The time is' in l or 'astral_mazmorras_copias' in l]
    print('\n'.join(interesantes))
    print('--- posibles errores ---')
    print('\n'.join(errores[:60]) or '(ninguno)')
    print('log:', log)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--java', type=Path, required=True)
    parser.add_argument('--server', type=Path, required=True)
    args = parser.parse_args()
    run(args.java.resolve(), args.server.resolve())
