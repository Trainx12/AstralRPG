"""Arma las regiones de la Mazmorra Infinita pegando doubledungeonspawn.schem en un Paper local (sin tocar el server).

python tools/pegar_infinita.py --java <java25> --base .local/testsrv
Salida: .local/infinita-mapa/entrega/region/*.mca (privado, nunca al repo).
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
sys.path.insert(0, str(ROOT/'datapack-src'))
from infinita import PASTE_ORIGIN, SCHEM as SCHEM_REL  # noqa: E402
WORLD = 'infinita'

SCHEM = ROOT/SCHEM_REL
OUT = ROOT/'.local/infinita-mapa/entrega'


def run(java, base):
    work = ROOT/'.local/infinita-mapa/paper'
    if work.exists():
        shutil.rmtree(work)
    server = work/'srv'
    server.mkdir(parents=True)
    for name in ('libraries', 'versions', 'cache'):
        shutil.copytree(base/name, server/name)
    shutil.copy2(base/'paper.jar', server/'paper.jar')
    (server/'eula.txt').write_text('eula=true\n')
    (server/'server.properties').write_text('server-ip=127.0.0.1\nserver-port=25604\nonline-mode=false\nlevel-name=world\n'
        'level-type=minecraft:flat\ngenerate-structures=false\nmanagement-server-enabled=false\n')
    plugins = server/'plugins'
    plugins.mkdir()
    shutil.copy2(ROOT/'.local/tanda4a-paper/plugins/worldedit.jar', plugins/'worldedit.jar')
    packs = server/'world/datapacks'
    packs.mkdir(parents=True)
    deps = [*server.joinpath('libraries').rglob('*.jar'), *server.joinpath('versions').rglob('*.jar'), plugins/'worldedit.jar']
    subprocess.run([str(java), '-m', 'jdk.compiler/com.sun.tools.javac.Main', '-encoding', 'UTF-8', '-classpath',
                    os.pathsep.join(map(str, deps)), '-d', str(work), str(ROOT/'datapack-src/test_runtime/SchemPaste.java')], check=True)
    with zipfile.ZipFile(plugins/'SchemPaste.jar', 'w') as z:
        z.write(work/'astraltest/SchemPaste.class', 'astraltest/SchemPaste.class')
        z.writestr('plugin.yml', "name: SchemPaste\nversion: 1\nmain: astraltest.SchemPaste\napi-version: '26.1.2'\n"
                   "depend: [WorldEdit]\ncommands:\n  schempaste: {}\n")
    log = work/'paper.log'
    with log.open('w', encoding='utf8') as out:
        p = subprocess.Popen([str(java), '-Xmx3G', '-jar', 'paper.jar', '--nogui'], cwd=server,
                             stdin=subprocess.PIPE, stdout=out, stderr=subprocess.STDOUT, text=True)
        def command(c): p.stdin.write(c+'\n'); p.stdin.flush()
        try:
            for _ in range(240):
                if 'For help, type' in log.read_text(encoding='utf8', errors='replace'): break
                time.sleep(1)
            x, y, z = PASTE_ORIGIN
            command(f'schempaste {WORLD} {SCHEM} {x} {y} {z}')
            for _ in range(120):
                text = log.read_text(encoding='utf8', errors='replace')
                if 'PASTE OK' in text or 'PASTE FAIL' in text: break
                time.sleep(1)
            time.sleep(3)
            command('save-all flush'); time.sleep(10)
        finally:
            if p.poll() is None: command('stop'); p.wait(timeout=120)
    text = log.read_text(encoding='utf8', errors='replace')
    print('\n'.join(l for l in text.splitlines() if 'PASTE' in l))
    if 'PASTE OK' not in text: raise AssertionError(str(log))
    region = server/f'world/dimensions/minecraft/{WORLD}/region'
    if OUT.exists(): shutil.rmtree(OUT)
    shutil.copytree(region, OUT/'region')
    print('Regiones:', sorted(p.name for p in (OUT/'region').iterdir()))


if __name__ == '__main__':
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument('--java', type=Path, required=True)
    a.add_argument('--base', type=Path, required=True)
    args = a.parse_args()
    run(args.java.resolve(), args.base.resolve())
