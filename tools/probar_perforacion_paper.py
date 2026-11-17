"""Ensayo Paper aislado; no se conecta al servidor remoto ni instala el probe alli."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import time
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def run(java, base, artifacts=ROOT):
    work = ROOT / '.local/perforacion-probe'
    server = work / 'paper'
    server.mkdir(parents=True, exist_ok=True)
    for name in ('libraries', 'versions', 'cache'):
        if not (server / name).exists():
            shutil.copytree(base / name, server / name)
    shutil.copy2(base / 'paper.jar', server / 'paper.jar')
    (server / 'eula.txt').write_text('eula=true\n')
    (server / 'server.properties').write_text(
        'server-ip=127.0.0.1\nserver-port=25623\nonline-mode=false\nlevel-name=world\n'
        'level-type=minecraft:flat\ngenerator-settings={"layers":[{"block":"minecraft:bedrock","height":1}],"biome":"minecraft:plains"}\n'
        'generate-structures=false\nspawn-protection=0\nmanagement-server-enabled=false\nview-distance=2\nsimulation-distance=2\n')
    (server / 'spigot.yml').write_text('settings:\n  attribute:\n    maxHealth:\n      max: 1.0E12\n    attackDamage:\n      max: 1.0E12\n')
    plugins = server / 'plugins'
    plugins.mkdir(exist_ok=True)
    for name in ('bettermodel', 'mythicmobs', 'nightcore', 'excellentenchants', 'packetevents', 'Vault'):
        source = base / 'plugins' / (name + '.jar')
        if source.exists():
            shutil.copy2(source, plugins / source.name)
    for name in ('AstralDecor', 'AstralEfectos'):
        shutil.copy2(artifacts / 'build/runtime' / (name + '.jar'), plugins / (name + '.jar'))
    for name in ('.cache', '.libs'):
        source = base / 'plugins/BetterModel' / name
        if source.exists():
            shutil.copytree(source, plugins / 'BetterModel' / name, dirs_exist_ok=True)
    packs = server / 'world/datapacks'
    packs.mkdir(parents=True, exist_ok=True)
    shutil.copy2(artifacts / 'build/AstralRPG-Items.zip', packs / 'AstralRPG-Items.zip')
    deps = [*server.joinpath('libraries').rglob('*.jar'), *server.joinpath('versions').rglob('*.jar')]
    subprocess.run([str(java), '-m', 'jdk.compiler/com.sun.tools.javac.Main', '-encoding', 'UTF-8',
        '-classpath', os.pathsep.join(map(str, deps)), '-d', str(work),
        str(ROOT / 'datapack-src/test_runtime/SpellProbe.java')], check=True)
    with zipfile.ZipFile(plugins / 'SpellProbe.jar', 'w') as z:
        for path in (work / 'astraltest').glob('SpellProbe*.class'):
            z.write(path, 'astraltest/' + path.name)
        z.writestr('plugin.yml', "name: SpellProbe\nversion: 1\nmain: astraltest.SpellProbe\napi-version: '26.1.2'\ndepend: [AstralDecor]\ncommands:\n  spellprobe: {}\n")
    log = work / 'paper.log'
    with log.open('w', encoding='utf8') as output:
        process = subprocess.Popen([str(java), '-Xms512M', '-Xmx2G', '-jar', 'paper.jar', '--nogui'],
            cwd=server, stdin=subprocess.PIPE, stdout=output, stderr=subprocess.STDOUT, text=True)
        def cmd(value):
            process.stdin.write(value + '\n')
            process.stdin.flush()
        try:
            for _ in range(180):
                if 'For help, type' in log.read_text('utf8', errors='replace'):
                    break
                if process.poll() is not None:
                    raise RuntimeError('Paper termino: ' + str(log))
                time.sleep(1)
            else:
                raise TimeoutError('Paper no arranco')
            cmd('spellprobe setup')
            time.sleep(3)
            for mode, tier in [('line', 1), ('line', 1), ('line', 4), ('line', 8), ('wall', 1),
                               ('pet', 1), ('owned', 1), ('noai', 1), ('invulnerable', 1), ('off', 1), ('low', 1)]:
                cmd(f'spellprobe case {mode} {tier}')
                time.sleep(1)
            cmd('spellprobe result')
            time.sleep(1)
        finally:
            if process.poll() is None:
                cmd('stop')
                process.wait(timeout=60)
    content = log.read_text('utf8', errors='replace')
    print('\n'.join(line for line in content.splitlines() if 'SPELL ' in line or 'ERROR' in line))
    if 'failures=0' not in content or any(s in content for s in
        ('SPELL FAIL', 'Error loading', 'Failed to load', 'Encountered an unexpected', 'Could not load')):
        raise AssertionError('Revisar ' + str(log))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--java', required=True, type=Path)
    parser.add_argument('--base', required=True, type=Path)
    parser.add_argument('--artifacts', type=Path, default=ROOT, help='Raiz con los build/ a verificar')
    args = parser.parse_args()
    run(args.java.resolve(), args.base.resolve(), args.artifacts.resolve())
