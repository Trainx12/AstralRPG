"""Arma el mundo astral_bosque nuevo en un Paper local (sin tocar el server).

python tools/bosque_armar.py --java <java25> --base .local/testsrv
Antes: python tools/bosque_mapa.py. Salida: .local/bosque-mapas/entrega/region/*.mca (privado, nunca al repo).
"""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'datapack-src'))
import bosque_talar as B  # noqa: E402

DATA = ROOT / '.local/bosque-mapas/datos'
OUT = ROOT / '.local/bosque-mapas/entrega'
WALL_TOP = 200


def run(java, base):
    work = ROOT / '.local/bosque-mapas/paper'
    if work.exists():
        shutil.rmtree(work)
    server = work / 'srv'
    server.mkdir(parents=True)
    for name in ('libraries', 'versions', 'cache'):
        shutil.copytree(base / name, server / name)
    shutil.copy2(base / 'paper.jar', server / 'paper.jar')
    (server / 'eula.txt').write_text('eula=true\n')
    (server / 'server.properties').write_text('server-ip=127.0.0.1\nserver-port=25605\nonline-mode=false\nlevel-name=world\n'
        'level-type=minecraft:flat\ngenerate-structures=false\nmanagement-server-enabled=false\n')
    plugins = server / 'plugins'
    plugins.mkdir()
    deps = [*server.joinpath('libraries').rglob('*.jar'), *server.joinpath('versions').rglob('*.jar')]
    subprocess.run([str(java), '-m', 'jdk.compiler/com.sun.tools.javac.Main', '-encoding', 'UTF-8', '-classpath',
                    os.pathsep.join(map(str, deps)), '-d', str(work), str(ROOT / 'datapack-src/test_runtime/BosqueArmar.java')],
                   check=True)
    with zipfile.ZipFile(plugins / 'BosqueArmar.jar', 'w') as z:
        z.write(work / 'astraltest/BosqueArmar.class', 'astraltest/BosqueArmar.class')
        z.writestr('plugin.yml', "name: BosqueArmar\nversion: 1\nmain: astraltest.BosqueArmar\napi-version: '26.1.2'\n"
                   "commands:\n  bosquearmar: {}\n")
    log = work / 'paper.log'
    with log.open('w', encoding='utf8') as out:
        p = subprocess.Popen([str(java), '-Xmx4G', '-jar', 'paper.jar', '--nogui'], cwd=server,
                             stdin=subprocess.PIPE, stdout=out, stderr=subprocess.STDOUT, text=True)

        def command(c):
            p.stdin.write(c + '\n'); p.stdin.flush()
        try:
            for _ in range(300):
                if 'For help, type' in log.read_text(encoding='utf8', errors='replace'):
                    break
                time.sleep(1)
            command(f'bosquearmar {DATA} {B.MOLD_DY} {WALL_TOP}')
            for _ in range(900):
                text = log.read_text(encoding='utf8', errors='replace')
                if 'ARMAR FASE1 OK' in text or 'ARMAR FAIL' in text:
                    break
                time.sleep(1)
            time.sleep(10)
            command(f'bosquearmar {DATA} {B.MOLD_DY} {WALL_TOP} copiar')
            for _ in range(900):
                text = log.read_text(encoding='utf8', errors='replace')
                if 'ARMAR OK' in text or 'ARMAR FAIL' in text:
                    break
                time.sleep(1)
            time.sleep(3)
            command('save-all flush'); time.sleep(15)
        finally:
            if p.poll() is None:
                command('stop'); p.wait(timeout=300)
    text = log.read_text(encoding='utf8', errors='replace')
    print('\n'.join(l for l in text.splitlines() if 'ARMAR' in l))
    if 'ARMAR OK' not in text:
        raise AssertionError(str(log))
    dim = server / 'world/dimensions/minecraft/astral_bosque'
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(dim / 'region', OUT / 'region')
    print('Regiones:', sorted(p.name for p in (OUT / 'region').iterdir()))


if __name__ == '__main__':
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument('--java', type=Path, required=True)
    a.add_argument('--base', type=Path, required=True)
    args = a.parse_args()
    run(args.java.resolve(), args.base.resolve())
