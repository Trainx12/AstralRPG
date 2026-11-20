"""Ensayo local del Bosque Astral nuevo: carga astral_bosque.sk con Skript, tala arboles como la motosierra
(sin eventos) y comprueba que vuelven desde el molde. No toca el server.

python tools/probar_bosque_paper.py --java <java25> --base .local/testsrv
Necesita .local/bosque-mapas/entrega/region (tools/bosque_armar.py).
"""
import argparse
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'datapack-src'))
import bosque_talar as B  # noqa: E402

STUBS = '''function rk_sumar(p: player, r: text, n: number):
    stop
function am_give(p: player, items: items):
    stop
function am_sale_menu(p: player):
    stop
'''
SAMPLE = (1, 50, 120, 200, 300, 400)


def run(java, base):
    work = ROOT / '.local/bosque-mapas/probe'
    if work.exists():
        shutil.rmtree(work)
    srv = work / 'srv'
    srv.mkdir(parents=True)
    for name in ('libraries', 'versions', 'cache'):
        shutil.copytree(base / name, srv / name)
    shutil.copy2(base / 'paper.jar', srv / 'paper.jar')
    (srv / 'eula.txt').write_text('eula=true\n')
    (srv / 'server.properties').write_text('server-ip=127.0.0.1\nserver-port=25614\nonline-mode=false\nlevel-name=world\n'
                                           'level-type=minecraft:flat\ngenerate-structures=false\nmanagement-server-enabled=false\n')
    shutil.copytree(ROOT / '.local/bosque-mapas/entrega/region', srv / 'world/dimensions/minecraft/astral_bosque/region')
    plugins = srv / 'plugins'
    plugins.mkdir()
    shutil.copy2(base / 'plugins/skript.jar', plugins / 'skript.jar')
    scripts = plugins / 'Skript/scripts'
    scripts.mkdir(parents=True)
    text = B.script().replace(f'>= {B.REGROW_MIN} minutes', '>= 5 seconds')
    (scripts / 'astral_bosque.sk').write_text(text, encoding='utf8')
    (scripts / 'stubs.sk').write_text(STUBS, encoding='utf8')
    (plugins / 'BosqueProbe').mkdir()
    boxes = [B.ARBOLES[i - 1]['box'] for i in SAMPLE if i <= len(B.ARBOLES)]
    (plugins / 'BosqueProbe/boxes.txt').write_text(f'{B.MOLD_DY}\n' + ''.join(' '.join(map(str, b)) + '\n' for b in boxes))
    deps = [*srv.joinpath('libraries').rglob('*.jar'), *srv.joinpath('versions').rglob('*.jar')]
    subprocess.run([str(java), '-m', 'jdk.compiler/com.sun.tools.javac.Main', '-encoding', 'UTF-8', '-nowarn', '-classpath',
                    os.pathsep.join(map(str, deps)), '-d', str(work), str(ROOT / 'datapack-src/test_runtime/BosqueProbe.java')],
                   check=True)
    with zipfile.ZipFile(plugins / 'BosqueProbe.jar', 'w') as z:
        z.write(work / 'astraltest/BosqueProbe.class', 'astraltest/BosqueProbe.class')
        z.writestr('plugin.yml', "name: BosqueProbe\nversion: 1\nmain: astraltest.BosqueProbe\napi-version: '26.1.2'\n"
                                 "depend: [Skript]\n")
    log = work / 'paper.log'
    with log.open('w', encoding='utf8') as out:
        subprocess.run([str(java), '-Xmx4G', '-jar', 'paper.jar', '--nogui'], cwd=srv, stdin=subprocess.DEVNULL,
                       stdout=out, stderr=subprocess.STDOUT, timeout=900)
    text = log.read_text(encoding='utf8', errors='replace')
    keep = [l for l in text.splitlines() if 'PROBE' in l or 'error' in l.lower() or 'Line ' in l or 'astral_bosque.sk' in l
            or 'Loaded' in l and 'script' in l]
    print('\n'.join(keep[:80]))
    if 'PROBE OK' not in text:
        raise SystemExit('FALLO: ver ' + str(log))


if __name__ == '__main__':
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument('--java', type=Path, required=True)
    a.add_argument('--base', type=Path, required=True)
    args = a.parse_args()
    run(args.java.resolve(), args.base.resolve())
