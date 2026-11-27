"""Ensayo local Paper + Skript, sin acceso al servidor remoto."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def run(java):
    sys.stdout.reconfigure(errors='replace')
    source = ROOT / '.local/asw-native/server'
    work = Path(tempfile.mkdtemp(prefix='zombis-probe-', dir=ROOT / '.local'))
    server = work / 'paper'
    server.mkdir(parents=True, exist_ok=True)
    for name in ('libraries', 'versions', 'cache'):
        if not (server / name).exists():
            shutil.copytree(source / name, server / name)
    shutil.copy2(source / 'paper.jar', server / 'paper.jar')
    plugins = server / 'plugins'
    scripts = plugins / 'Skript/scripts'
    scripts.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source / 'plugins/skript.jar', plugins / 'skript.jar')
    shutil.copy2(ROOT / 'build/gameplay/astral_zombis_sin_ahogados.sk', scripts)
    (server / 'eula.txt').write_text('eula=true\n')
    (server / 'server.properties').write_text('server-ip=127.0.0.1\nserver-port=25641\nonline-mode=false\n'
        'level-type=minecraft:flat\ngenerator-settings={"layers":[{"block":"minecraft:bedrock","height":1}],"biome":"minecraft:plains"}\n'
        'management-server-enabled=false\nview-distance=2\nsimulation-distance=2\nspawn-protection=0\n')
    (server / 'spigot.yml').write_text('settings:\n  attribute:\n    maxHealth:\n      max: 1000000000\n')
    classes = work / 'classes'
    classes.mkdir(exist_ok=True)
    jars = list((server / 'libraries').rglob('*.jar')) + list((server / 'versions').rglob('*.jar'))
    args = ['-encoding', 'UTF-8', '-classpath', os.pathsep.join(map(str, jars)), '-d', str(classes),
            str(ROOT / 'datapack-src/test_runtime/ZombieConversionProbe.java')]
    argfile = work / 'compile.args'
    argfile.write_text('\n'.join('"' + s.replace('\\', '/') + '"' for s in args))
    subprocess.run([str(java), '-m', 'jdk.compiler/com.sun.tools.javac.Main', '@' + str(argfile)], check=True)
    with zipfile.ZipFile(plugins / 'ZombieConversionProbe.jar', 'w') as z:
        for p in (classes / 'astraltest').glob('ZombieConversionProbe*.class'):
            z.write(p, 'astraltest/' + p.name)
        z.writestr('plugin.yml', "name: ZombieConversionProbe\nversion: 1\nmain: astraltest.ZombieConversionProbe\n"
                   "api-version: '26.1.2'\ndepend: [Skript]\ncommands:\n  zombieprobe: {}\n")
    log = work / 'paper.log'
    with log.open('w', encoding='utf8') as out:
        proc = subprocess.Popen([str(java), '-Xms256M', '-Xmx1G', '-Dterminal.jline=false', '-Dterminal.ansi=false', '-jar', 'paper.jar', '--nogui'], cwd=server,
            stdin=subprocess.PIPE, stdout=out, stderr=subprocess.STDOUT, text=True)
        def command(c):
            proc.stdin.write(c + '\n'); proc.stdin.flush()
        try:
            for _ in range(180):
                content = log.read_text('utf8', errors='replace')
                if 'Finished loading.' in content:
                    break
                if proc.poll() is not None:
                    raise RuntimeError('Paper termino: ' + str(log))
                time.sleep(1)
            else:
                raise TimeoutError(str(log))
            command('zombieprobe')
            for _ in range(30):
                if 'ZOMBIE RESULT' in log.read_text('utf8', errors='replace'):
                    break
                time.sleep(1)
        finally:
            if proc.poll() is None:
                command('stop'); proc.wait(timeout=60)
    content = log.read_text('utf8', errors='replace')
    print('\n'.join(l for l in content.splitlines() if 'ZOMBIE ' in l or 'ERROR' in l or '[Skript]' in l))
    assert 'ZOMBIE RESULT' in content and 'failures=0' in content and 'ZOMBIE FAIL' not in content
    assert 'ERROR' not in content


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--java', type=Path, required=True)
    run(parser.parse_args().java.resolve())
