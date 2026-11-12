"""Ensayo local de Duels Optimised + /desafiar (Skript) con dos jugadores NMS. No toca el server.

python tools/probar_duelos_paper.py --java <java25> --base .local/testsrv
Requiere .local/duels/Duels-Optimised-8.3.jar (BuiltByBit, nunca al repo).
"""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import time
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def run(java, base):
    work = ROOT/'.local/duels/probe'
    if work.exists():
        shutil.rmtree(work)
    srv = work/'srv'
    srv.mkdir(parents=True)
    for name in ('libraries', 'versions', 'cache'):
        shutil.copytree(base/name, srv/name)
    shutil.copy2(base/'paper.jar', srv/'paper.jar')
    (srv/'eula.txt').write_text('eula=true\n')
    (srv/'server.properties').write_text('server-ip=127.0.0.1\nserver-port=25606\nonline-mode=false\nlevel-name=world\n'
        'level-type=minecraft:flat\ngenerate-structures=false\nmanagement-server-enabled=false\nspawn-protection=0\n')
    plugins = srv/'plugins'
    plugins.mkdir()
    shutil.copy2(ROOT/'.local/duels/Duels-Optimised-8.3.jar', plugins/'Duels.jar')
    shutil.copy2(base/'plugins/skript.jar', plugins/'skript.jar')
    shutil.copytree(ROOT/'build/plugins-basicos/Duels', plugins/'Duels')
    scripts = plugins/'Skript/scripts'
    scripts.mkdir(parents=True)
    shutil.copy2(ROOT/'build/duelos/astral_duelos.sk', scripts/'astral_duelos.sk')
    deps = [*srv.joinpath('libraries').rglob('*.jar'), *srv.joinpath('versions').rglob('*.jar')]
    subprocess.run([str(java), '-m', 'jdk.compiler/com.sun.tools.javac.Main', '-encoding', 'UTF-8', '-classpath',
                    os.pathsep.join(map(str, deps)), '-d', str(work), str(ROOT/'datapack-src/test_runtime/DuelsProbe.java')], check=True)
    with zipfile.ZipFile(plugins/'DuelsProbe.jar', 'w') as z:
        z.write(work/'astraltest/DuelsProbe.class', 'astraltest/DuelsProbe.class')
        z.writestr('plugin.yml', "name: DuelsProbe\nversion: 1\nmain: astraltest.DuelsProbe\napi-version: '26.1.2'\n"
                   "loadbefore: [Duels]\ncommands:\n  duelsprobe: {}\n")
    log = work/'paper.log'
    with log.open('w', encoding='utf8') as out:
        p = subprocess.Popen([str(java), '-Xmx2G', '-jar', 'paper.jar', '--nogui'], cwd=srv,
                             stdin=subprocess.PIPE, stdout=out, stderr=subprocess.STDOUT, text=True)
        def command(c):
            try:
                p.stdin.write(c + '\n'); p.stdin.flush()
            except OSError:
                pass
        try:
            for _ in range(240):
                if 'For help, type' in log.read_text(encoding='utf8', errors='replace'): break
                time.sleep(1)
            steps = [('setup', 4), ('gui', 3), ('request', 2)]
            for arena, world in (('Astral', 'arena'), ('TFT2', 'arenas_tft')):
                steps += [(f'start {arena}', 8), (f'inarena {world}', 15), ('after', 3), ('loser', 2)]
            for c, wait in steps + [('result', 1)]:
                command('duelsprobe ' + c); time.sleep(wait)
        finally:
            command('stop')
            p.wait(timeout=120)
    text = log.read_text(encoding='utf8', errors='replace')
    print('\n'.join(l for l in text.splitlines() if 'DUELS' in l or 'ERROR' in l or ('Skript' in l and 'error' in l.lower())))
    if 'DUELS RESULT failures=0' not in text:
        raise AssertionError(str(log))


if __name__ == '__main__':
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument('--java', type=Path, required=True)
    a.add_argument('--base', type=Path, required=True)
    args = a.parse_args()
    run(args.java.resolve(), args.base.resolve())
