"""Ensayo aislado de Skript y autoventa con jugadores NMS simulados.

Usa un doble local de DeluxeMenus/PAPI para respuestas numericas y ausentes.
No instala nada en el servidor remoto. --base requiere Paper 26.1.2 y los JAR
Skript, Vault, EssentialsX, AstralMinasLimite, NightCore y ExcellentEnchants.
"""
import argparse
import os
import re
from pathlib import Path
import shutil
import subprocess
import time
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def run(java, base, work):
    server = work / 'paper'
    server.mkdir(parents=True, exist_ok=True)
    for name in ('libraries', 'versions', 'cache'):
        if not (server / name).exists():
            shutil.copytree(base / name, server / name)
    shutil.copy2(base / 'paper.jar', server / 'paper.jar')
    (server / 'eula.txt').write_text('eula=true\n')
    (server / 'server.properties').write_text(
        'server-ip=127.0.0.1\nserver-port=25638\nonline-mode=false\nlevel-name=world\n'
        'level-type=minecraft:flat\ngenerator-settings={"layers":[{"block":"minecraft:bedrock","height":1}],"biome":"minecraft:plains"}\n'
        'generate-structures=false\nmanagement-server-enabled=false\n')
    plugins = server / 'plugins'
    plugins.mkdir(exist_ok=True)
    for name in ('skript.jar', 'Vault.jar', 'EssentialsX.jar', 'AstralMinasLimite.jar', 'nightcore.jar', 'excellentenchants.jar'):
        shutil.copy2(base / 'plugins' / name, plugins / name)
    scripts = plugins / 'Skript/scripts'
    scripts.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / 'build/minas/Skript/scripts/astral_minas.sk', scripts / 'astral_minas.sk')
    (scripts / 'probe.sk').write_text('''function rk_sumar(p: player, tipo: text, valor: number):
    stop

command /avtest <player> <text>:
    executable by: console
    trigger:
        if arg-2 is "reset":
            delete {-am.autoventa.uso::%uuid of arg-1%}
            delete {-am.autoventa.aviso::%uuid of arg-1%}
        if arg-2 is "quote":
            set metadata value "avbalance" of arg-1 to arg-1's balance
            set metadata value "avquote" of arg-1 to am_sell_value(arg-1, false)
        if arg-2 is "give":
            am_give(arg-1, (64 coal))
        if arg-2 is "gesture":
            delete {-am.autoventa.toggle::%uuid of arg-1%}
''', encoding='utf8')
    packs = server / 'world/datapacks'
    packs.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / 'build/AstralRPG-Items.zip', packs / 'AstralRPG-Items.zip')
    deps = [*server.joinpath('libraries').rglob('*.jar'), *server.joinpath('versions').rglob('*.jar'), plugins / 'skript.jar']
    subprocess.run([str(java), '-m', 'jdk.compiler/com.sun.tools.javac.Main', '-encoding', 'UTF-8',
                    '-classpath', os.pathsep.join(map(str, deps)), '-d', str(work),
                    str(ROOT / 'datapack-src/test_runtime/AutoventaProbe.java')], check=True)
    with zipfile.ZipFile(plugins / 'AutoventaProbe.jar', 'w') as z:
        for p in (work / 'astraltest').glob('AutoventaProbe*.class'):
            z.write(p, 'astraltest/' + p.name)
        z.writestr('plugin.yml', "name: AutoventaProbe\nversion: 1\nmain: astraltest.AutoventaProbe\napi-version: '26.1.2'\ndepend: [Skript, Essentials, Vault]\ncommands:\n  autoventaprobe: {}\n  dm: {}\n")
    log = work / 'paper-behavior.log'
    with log.open('w', encoding='utf8') as out:
        process = subprocess.Popen([str(java), '-Xms512M', '-Xmx1536M', '-jar', 'paper.jar', '--nogui'], cwd=server,
                                   stdin=subprocess.PIPE, stdout=out, stderr=subprocess.STDOUT, text=True)
        def command(c):
            process.stdin.write(c + '\n')
            process.stdin.flush()
        def until(marker, timeout=180):
            for _ in range(timeout):
                content = re.sub(r'\x1b\[[0-9;]*m', '', log.read_text('utf8', errors='replace'))
                if marker in content:
                    return
                if process.poll() is not None:
                    raise RuntimeError('Paper termino: ' + str(log))
                time.sleep(1)
            raise TimeoutError(marker + ': ' + str(log))
        try:
            until('Done (')
            until('All scripts loaded without errors.')
            command('autoventaprobe start')
            time.sleep(8)
            command('autoventaprobe test')
            until('AUTOVENTA RESULT failures=')
        finally:
            if process.poll() is None:
                command('stop')
                process.wait(timeout=60)
    # Segundo arranque real: la variable persistente debe seguir apagada.
    with log.open('a', encoding='utf8') as out:
        process = subprocess.Popen([str(java), '-Xms512M', '-Xmx1536M', '-jar', 'paper.jar', '--nogui'], cwd=server,
                                   stdin=subprocess.PIPE, stdout=out, stderr=subprocess.STDOUT, text=True)
        try:
            for _ in range(180):
                if log.read_text('utf8', errors='replace').count('Done (') >= 2:
                    break
                if process.poll() is not None:
                    raise RuntimeError('Paper termino en el segundo arranque: ' + str(log))
                time.sleep(1)
            else:
                raise TimeoutError('Segundo arranque de Paper')
            command('autoventaprobe start')
            time.sleep(8)
            command('autoventaprobe persisted')
            until('AUTOVENTA PERSIST failures=')
        finally:
            if process.poll() is None:
                command('stop')
                process.wait(timeout=60)
    content = log.read_text('utf8', errors='replace')
    print('\n'.join(l for l in content.splitlines() if 'AUTOVENTA' in l or 'Encountered' in l), flush=True)
    assert 'AUTOVENTA RESULT failures=0' in content
    assert 'AUTOVENTA PERSIST failures=0' in content
    assert all(s not in content for s in ('AUTOVENTA FAIL', 'Encountered', 'Failed to load', 'Error loading'))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--java', type=Path, required=True)
    p.add_argument('--base', type=Path, required=True)
    p.add_argument('--work', type=Path, default=ROOT / '.local/autoventa-probe')
    args = p.parse_args()
    run(args.java.resolve(), args.base.resolve(), args.work.resolve())
