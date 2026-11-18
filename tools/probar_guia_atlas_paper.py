"""Ensayo local aislado; nunca se conecta al servidor remoto."""
import argparse
from pathlib import Path
import os
import shutil
import subprocess
import time
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def run(java, base, artifacts):
    work = ROOT / '.local/atlas-probe'
    server = work / 'paper'
    server.mkdir(parents=True, exist_ok=True)
    for name in ('libraries', 'versions', 'cache'):
        if not (server / name).exists():
            shutil.copytree(base / name, server / name)
    shutil.copy2(base / 'paper.jar', server / 'paper.jar')
    (server / 'eula.txt').write_text('eula=true\n')
    (server / 'server.properties').write_text('server-ip=127.0.0.1\nserver-port=25589\nonline-mode=false\nlevel-name=probe\nlevel-type=minecraft:flat\ngenerator-settings={"layers":[{"block":"minecraft:bedrock","height":1}],"biome":"minecraft:plains"}\ngenerate-structures=false\nmanagement-server-enabled=false\nview-distance=2\nsimulation-distance=2\nmax-tick-time=-1\n')
    plugins = server / 'plugins'
    plugins.mkdir(exist_ok=True)
    packs = server / 'probe/datapacks'
    packs.mkdir(parents=True, exist_ok=True)
    shutil.copy2(artifacts / 'build/AstralRPG-Items.zip', packs / 'AstralRPG-Items.zip')
    deps = [*server.joinpath('libraries').rglob('*.jar'), *server.joinpath('versions').rglob('*.jar')]
    subprocess.run([str(java), '-m', 'jdk.compiler/com.sun.tools.javac.Main', '-encoding', 'UTF-8',
                    '-classpath', os.pathsep.join(map(str, deps)), '-d', str(work),
                    str(ROOT / 'datapack-src/test_runtime/AtlasProbe.java')], check=True)
    with zipfile.ZipFile(artifacts / 'build/AstralRPG-Items.zip') as z:
        expected = ['astral:' + n.removeprefix('data/astral/dialog/').removesuffix('.json') for n in z.namelist() if n.startswith('data/astral/dialog/atlas/')]
    with zipfile.ZipFile(plugins / 'AtlasProbe.jar', 'w') as z:
        for path in (work / 'astraltest').glob('AtlasProbe*.class'):
            z.write(path, 'astraltest/' + path.name)
        z.writestr('plugin.yml', "name: AtlasProbe\nversion: 1\nmain: astraltest.AtlasProbe\napi-version: '26.1.2'\n")
        z.writestr('expected.txt', '\n'.join(expected))
    log = work / 'paper.log'
    with log.open('w', encoding='utf8') as output:
        process = subprocess.Popen([str(java), '-Xms512M', '-Xmx2G', '-jar', 'paper.jar', '--nogui'], cwd=server,
                                   stdin=subprocess.PIPE, stdout=output, stderr=subprocess.STDOUT, text=True)
        try:
            for _ in range(240):
                content = log.read_text('utf8', errors='replace')
                if 'ATLAS RESULT' in content:
                    break
                if process.poll() is not None:
                    raise RuntimeError('Paper termino: ' + str(log))
                time.sleep(1)
            else:
                raise TimeoutError('Falta resultado: ' + str(log))
        finally:
            if process.poll() is None:
                process.stdin.write('stop\n')
                process.stdin.flush()
                process.wait(timeout=60)
    content = log.read_text('utf8', errors='replace')
    result = [l for l in content.splitlines() if 'ATLAS RESULT' in l]
    print('\n'.join(result))
    if not result or 'failures=0' not in result[-1] or 'ATLAS FAIL' in content:
        raise AssertionError('Fallo: ' + str(log))
    if any(s in content for s in ('Failed to parse', 'Failed to load', 'Error loading', 'Couldn\'t parse')):
        raise AssertionError('Error de carga: ' + str(log))
    print('Registro y apertura nativos aprobados. Sin cliente visual. Log:', log)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--java', type=Path, required=True)
    parser.add_argument('--base', type=Path, required=True)
    parser.add_argument('--artifacts', type=Path, default=ROOT)
    args = parser.parse_args()
    run(args.java.resolve(), args.base.resolve(), args.artifacts.resolve())
