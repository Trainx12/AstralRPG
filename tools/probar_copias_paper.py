"""Ensayo local de las copias de mazmorra (party, copia libre, ocupada, salida tras el jefe). No toca el server.

python tools/probar_copias_paper.py --java <java25> --base .local/testsrv
Usa el Skript real de mazmorras_copias.py con el reloj acortado a 1 minuto.
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


def run(java, base):
    from mazmorras_copias import script
    work = ROOT/'.local/copias-probe'
    if work.exists():
        shutil.rmtree(work)
    srv = work/'srv'
    srv.mkdir(parents=True)
    for name in ('libraries', 'versions', 'cache'):
        shutil.copytree(base/name, srv/name)
    shutil.copy2(base/'paper.jar', srv/'paper.jar')
    (srv/'eula.txt').write_text('eula=true\n')
    (srv/'server.properties').write_text('server-ip=127.0.0.1\nserver-port=25607\nonline-mode=false\nlevel-name=world\n'
        'level-type=minecraft:flat\ngenerate-structures=false\nmanagement-server-enabled=false\nspawn-protection=0\n')
    plugins = srv/'plugins'
    plugins.mkdir()
    shutil.copy2(base/'plugins/skript.jar', plugins/'skript.jar')
    scripts = plugins/'Skript/scripts'
    scripts.mkdir(parents=True)
    sk=script(minutos=1)
    if os.environ.get('COPIAS_DEBUG'):
        dbg = '        broadcast "DBG [execute in minecraft:%{_d}% run minecraft:tp %uuid of loop-value% %{_tp}%]"'
        sk=sk.replace('        execute console command "execute in minecraft:%{_d}%', dbg + chr(10) + '        execute console command "execute in minecraft:%{_d}%')
    (scripts/'astral_mazmorras_copias.sk').write_text(sk, encoding='utf8')
    shutil.copy2(ROOT/'build/gameplay/astral_gameplay.sk', scripts/'astral_gameplay.sk')
    deps = [*srv.joinpath('libraries').rglob('*.jar'), *srv.joinpath('versions').rglob('*.jar')]
    subprocess.run([str(java), '-m', 'jdk.compiler/com.sun.tools.javac.Main', '-encoding', 'UTF-8', '-classpath',
                    os.pathsep.join(map(str, deps)), '-d', str(work), str(ROOT/'datapack-src/test_runtime/CopiesProbe.java')], check=True)
    with zipfile.ZipFile(plugins/'CopiesProbe.jar', 'w') as z:
        z.write(work/'astraltest/CopiesProbe.class', 'astraltest/CopiesProbe.class')
        z.writestr('plugin.yml', "name: CopiesProbe\nversion: 1\nmain: astraltest.CopiesProbe\napi-version: '26.1.2'\n"
                   "loadbefore: [Skript]\ncommands:\n  copiesprobe: {}\n  spawn: {}\n")
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
            # Las copias se marcan vacias cada 5 s y esperan 15 s antes de recibir un grupo.
            steps = [('setup', 3), ('party', 2), ('', 20), ('enter A', 2), ('enter C,D,E,F,G,H', 3), ('check1', 1)] if os.environ.get('COPIAS_DEBUG') else [('setup', 3), ('party', 2), ('', 20), ('enter A', 2), ('enter C,D,E,F,G,H', 3), ('check1', 1),
                     ('fin', 70), ('check2', 1), ('', 22), ('enter H', 3), ('check3', 1), ('result', 1)]
            for c, wait in steps:
                if c: command('copiesprobe ' + c)
                time.sleep(wait)
            for c in os.environ.get('COPIAS_CMDS', '').split(';'):
                if c: command(c); time.sleep(2)
        finally:
            command('stop')
            p.wait(timeout=120)
    text = log.read_text(encoding='utf8', errors='replace')
    print('\n'.join(l for l in text.splitlines() if 'COPIES' in l or 'ERROR' in l or 'Skript' in l))
    if 'COPIES RESULT failures=0' not in text or 'All scripts loaded without errors' not in text:
        raise AssertionError(str(log))


if __name__ == '__main__':
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument('--java', type=Path, required=True)
    a.add_argument('--base', type=Path, required=True)
    args = a.parse_args()
    run(args.java.resolve(), args.base.resolve())
