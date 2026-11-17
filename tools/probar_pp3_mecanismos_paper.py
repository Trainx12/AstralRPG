"""Ensayo aislado de recuperacion PP3 en Paper, sin tocar mundos del usuario."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'datapack-src'))
from minijuegos_datapack import Adapter


def run(java, base):
    server = ROOT / '.local/pp3-mecanismos-probe'
    server.mkdir(exist_ok=True)
    for name in ('libraries', 'versions', 'cache'):
        if not (server / name).exists():
            shutil.copytree(base / name, server / name)
    shutil.copy2(base / 'paper.jar', server / 'paper.jar')
    (server / 'eula.txt').write_text('eula=true\n')
    (server / 'server.properties').write_text(
        'server-ip=127.0.0.1\nserver-port=25608\nonline-mode=false\n'
        'level-name=probe\nlevel-type=minecraft:flat\n'
        'generator-settings={"layers":[{"block":"minecraft:bedrock","height":1}],'
        '"biome":"minecraft:plains"}\ngenerate-structures=false\n'
        'management-server-enabled=false\nview-distance=2\nsimulation-distance=2\n')
    adapter = Adapter('parkour_paradise3', ROOT / '.local/mapas/parkour_paradise3.zip', 'pp3')
    files = adapter.build()
    packs = server / 'probe/datapacks'
    packs.mkdir(parents=True, exist_ok=True)
    # Carga todas las funciones adaptadas reales para detectar errores de sintaxis,
    # pero sin tags load/tick: las pruebas controlan cada cambio explicitamente.
    with zipfile.ZipFile(packs / 'pp3.zip', 'w') as z:
        for name, data in files.items():
            if name.startswith('data/minecraft/tags/function/'):
                continue
            z.writestr(name, data)
        z.writestr('data/minecraft/dimension/parkour_paradise3.json', json.dumps({
            'type': 'minecraft:overworld', 'generator': {'type': 'minecraft:flat',
                'settings': {'biome': 'minecraft:plains', 'layers': [
                    {'block': 'minecraft:bedrock', 'height': 1}], 'structure_overrides': []}}}))
    log = server / 'probe.log'
    prefix = 'execute in minecraft:parkour_paradise3 run '
    checks = []
    with log.open('w', encoding='utf8') as out:
        proc = subprocess.Popen([str(java), '-Xms256M', '-Xmx1G', '-jar', 'paper.jar', '--nogui'],
            cwd=server, stdin=subprocess.PIPE, stdout=out, stderr=subprocess.STDOUT, text=True)

        def cmd(command):
            proc.stdin.write(command + '\n')
            proc.stdin.flush()

        def check(condition, label):
            checks.append(label)
            cmd(prefix + 'execute ' + condition + ' run say PP3_PASS_' + label)

        try:
            for _ in range(120):
                if 'For help, type' in log.read_text(encoding='utf8', errors='replace'):
                    break
                if proc.poll() is not None:
                    raise RuntimeError('Paper termino; ver ' + str(log))
                time.sleep(1)
            else:
                raise TimeoutError('Paper no arranco')
            cmd(prefix + 'forceload add -64 832 -32 880')
            time.sleep(2)
            # El marcador esta fuera de los chunks del ensayo: cargarlo tambien.
            cmd(prefix + 'forceload add -34 766')
            time.sleep(2)
            cmd(prefix + 'kill @e[type=marker]')
            cmd(prefix + 'summon marker -34 130 766 {CustomName:"console"}')
            for c in ['setblock -52 44 858 smooth_quartz', 'setblock -52 44 842 air',
                      'setblock -52 45 858 air', 'setblock -52 45 840 air',
                      'setblock -37 44 863 lava', 'setblock -37 45 865 air']:
                cmd(prefix + c)
            cmd('function pp3_main:astral/reparar_sala5')
            check('if block -52 45 858 stone_button[face=floor,facing=south,powered=false]', 'boton')
            check('if block -52 45 840 acacia_pressure_plate', 'placa_norte')
            check('if block -37 45 865 acacia_pressure_plate', 'placa_lava')
            cmd(prefix + 'setblock -52 45 858 stone_button[face=floor,facing=south,powered=true]')
            cmd('function pp3_main:astral/reparar_sala5')
            check('if block -52 45 858 stone_button[powered=true]', 'presionado')
            # Probar la conexion real boton -> redstone del tick original adaptado.
            cmd(prefix + 'execute as @e[type=marker,name=console,limit=1] run function pp3_main:levels/level5/tick')
            check('if block -52 42 861 redstone_block', 'salida_redstone')
            cmd(prefix + 'setblock -52 45 858 stone_button[face=floor,facing=south,powered=false]')
            cmd(prefix + 'execute as @e[type=marker,name=console,limit=1] run function pp3_main:levels/level5/tick')
            check('if block -52 42 861 air', 'salida_apagada')
            # Progreso marcado, incluso con piso todavia sin actualizar.
            cmd(prefix + 'tag @e[type=marker,name=console] add lvl5_first')
            cmd(prefix + 'setblock -52 45 858 air')
            cmd('function pp3_main:astral/reparar_sala5')
            check('if block -52 45 858 air', 'tag_completado')
            cmd(prefix + 'tag @e[type=marker,name=console] remove lvl5_first')
            cmd(prefix + 'setblock -52 44 858 yellow_stained_glass')
            cmd(prefix + 'setblock -37 44 863 orange_stained_glass')
            cmd(prefix + 'setblock -37 45 865 air')
            cmd('function pp3_main:astral/reparar_sala5')
            check('if block -52 45 858 air', 'piso_completado')
            check('if block -37 45 865 air', 'lava_completada')
            cmd(prefix + 'setblock -52 44 858 smooth_quartz')
            cmd(prefix + 'setblock -52 45 858 stone')
            cmd('function pp3_main:astral/reparar_sala5')
            check('if block -52 45 858 stone', 'bloque_inesperado')
            # Invocada desde overworld no debe escribir ahi.
            cmd('forceload add -52 858')
            time.sleep(1)
            cmd('setblock -52 45 858 diamond_block')
            cmd('function pp3_main:astral/reparar_sala5')
            checks.append('otro_mundo')
            cmd('execute if block -52 45 858 diamond_block run say PP3_PASS_otro_mundo')
            time.sleep(2)
        finally:
            if proc.poll() is None:
                cmd('stop')
                proc.wait(timeout=60)
    content = log.read_text(encoding='utf8', errors='replace')
    missing = [label for label in checks if 'PP3_PASS_' + label not in content]
    errors = [line for line in content.splitlines() if 'ERROR' in line or 'Failed to load' in line]
    print(f'PP3 Paper: {len(checks) - len(missing)}/{len(checks)} verificaciones; '
          f'{len(errors)} errores. Log privado: {log}')
    if missing or errors:
        raise AssertionError((missing, errors))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--java', type=Path, required=True)
    parser.add_argument('--base', type=Path, required=True)
    args = parser.parse_args()
    run(args.java.resolve(), args.base.resolve())
