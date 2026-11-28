"""Prueba aislada de orbes y skills; nunca instala el probe en remoto."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import time
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def run(java, source):
    work = Path(tempfile.mkdtemp(prefix='spawner-xp-test-', dir=ROOT / '.local'))
    server = work / 'paper'
    server.mkdir(parents=True, exist_ok=True)
    for name in ('libraries', 'versions', 'cache', 'plugins'):
        shutil.copytree(source / name, server / name, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns('*Probe*', '.paper-remapped'))
    shutil.copy2(source / 'paper.jar', server / 'paper.jar')
    shutil.copy2(source / 'eula.txt', server / 'eula.txt')
    properties = (source / 'server.properties').read_text()
    import re
    properties = re.sub(r'(?m)^server-port=.*$', 'server-port=25649', properties)
    (server / 'server.properties').write_text(properties + '\nmanagement-server-enabled=false\n')
    shutil.copy2(ROOT / 'build/spawner-xp/AstralSpawnerXp.jar', server / 'plugins/AstralSpawnerXp.jar')
    shutil.copy2(ROOT / 'build/spawner-skill-xp/AstralProgression.jar', server / 'plugins/AstralProgression.jar')
    classes = work / 'classes'
    classes.mkdir(exist_ok=True)
    jars = list((server / 'libraries').rglob('*.jar')) + list((server / 'versions').rglob('*.jar')) + list((server / 'plugins').glob('*.jar'))
    args = ['-encoding', 'UTF-8', '-classpath', os.pathsep.join(map(str, jars)), '-d', str(classes),
            str(ROOT / 'datapack-src/test_runtime/SpawnerXpProbe.java')]
    argfile = work / 'compile.args'
    argfile.write_text('\n'.join('"' + v.replace('\\', '/') + '"' for v in args))
    subprocess.run([str(java), '-m', 'jdk.compiler/com.sun.tools.javac.Main', '@' + str(argfile)], check=True)
    with zipfile.ZipFile(server / 'plugins/SpawnerXpProbe.jar', 'w') as jar:
        for p in (classes / 'astraltest').glob('SpawnerXpProbe*.class'):
            jar.write(p, 'astraltest/' + p.name)
        jar.writestr('plugin.yml', "name: SpawnerXpProbe\nversion: 1\nmain: astraltest.SpawnerXpProbe\napi-version: '26.1.2'\ndepend: [AstralSpawnerXp, AstralProgression]\ncommands:\n  spawnerxpprobe: {}\n")
    log = work / 'paper.log'
    with log.open('w', encoding='utf8') as output:
        proc = subprocess.Popen([str(java), '-Xms512M', '-Xmx2G', '-jar', 'paper.jar', '--nogui'],
                                cwd=server, stdin=subprocess.PIPE, stdout=output, stderr=subprocess.STDOUT, text=True)
        def command(value):
            proc.stdin.write(value + '\n'); proc.stdin.flush()
        try:
            for _ in range(180):
                content = log.read_text(encoding='utf8', errors='replace')
                if 'For help, type' in content: break
                if proc.poll() is not None or "can't proceed with server load" in content:
                    raise RuntimeError('Paper no pudo iniciar: ' + str(log))
                time.sleep(1)
            else: raise TimeoutError(str(log))
            command('spawnerxpprobe player')
            time.sleep(8)
            command('spawnerxpprobe run')
            for _ in range(40):
                content = log.read_text(encoding='utf8', errors='replace')
                if 'SPAWNERXP RESULT' in content: break
                time.sleep(1)
        finally:
            if proc.poll() is None:
                command('stop')
                try: proc.wait(timeout=30)
                except subprocess.TimeoutExpired:
                    proc.terminate(); proc.wait(timeout=15)
    content = log.read_text(encoding='utf8', errors='replace')
    print('\n'.join(line for line in content.splitlines() if 'SPAWNERXP' in line or 'ERROR' in line))
    assert 'SPAWNERXP RESULT failures=0' in content, str(log)
    assert 'SPAWNERXP FAIL' not in content, str(log)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--java', type=Path, required=True)
    parser.add_argument('--source', type=Path, default=ROOT / '.local/tier-soporte-paper/paper')
    args = parser.parse_args()
    run(args.java.resolve(), args.source.resolve())
