"""Ensayo aislado, sin cliente real ni servidor remoto. Copia dependencias en este worktree."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def run(java, base):
    srv = ROOT / '.local/minas-limite-paper'
    srv.mkdir(parents=True, exist_ok=True)
    for name in ('libraries', 'versions', 'cache'):
        if not (srv / name).exists():
            shutil.copytree(base / name, srv / name)
    if not (srv / 'paper.jar').exists():
        shutil.copy2(base / 'paper.jar', srv / 'paper.jar')
    plugins = srv / 'plugins'
    scripts = plugins / 'Skript/scripts'
    scripts.mkdir(parents=True, exist_ok=True)
    for n in ('skript.jar', 'EssentialsX.jar', 'Vault.jar'):
        if not (plugins / n).exists():
            shutil.copy2(base / 'plugins' / n, plugins / n)
    shutil.copy2(ROOT / 'build/minas/AstralMinasLimite.jar', plugins)
    shutil.copy2(ROOT / 'build/minas/Skript/scripts/astral_minas.sk', scripts)
    shutil.copy2(ROOT / 'build/rankings/astral_rankings.sk', scripts)
    (scripts / 'minas_probe.sk').write_text('''command /mlscript <player> <text>:
    executable by: console
    trigger:
        if arg-2 is "give":
            am_give(arg-1, 16 diamonds)
        if arg-2 is "sale":
            set {_v} to am_sell_value(arg-1, true)
            send "MLTEST sale value=%{_v}%" to console
''', encoding='utf8')
    (srv / 'eula.txt').write_text('eula=true\n')
    (srv / 'server.properties').write_text('server-ip=127.0.0.1\nserver-port=25643\nonline-mode=false\nlevel-name=world\n'
        'level-type=minecraft:flat\ngenerate-structures=false\nmanagement-server-enabled=false\nview-distance=2\nsimulation-distance=2\n')
    classes = ROOT / '.local/minas-limite-probe-classes'
    classes.mkdir(parents=True, exist_ok=True)
    jars = list((srv / 'libraries').rglob('*.jar')) + list((srv / 'versions').rglob('*.jar'))
    subprocess.run([str(java), '-m', 'jdk.compiler/com.sun.tools.javac.Main', '-encoding', 'UTF-8', '-classpath',
                    os.pathsep.join(map(str, jars)), '-d', str(classes), str(ROOT / 'datapack-src/test_runtime/MinasLimiteProbe.java')], check=True)
    with zipfile.ZipFile(plugins / 'MinasLimiteProbe.jar', 'w') as z:
        for p in classes.rglob('*.class'):
            z.write(p, p.relative_to(classes).as_posix())
        z.writestr('plugin.yml', "name: MinasLimiteProbe\nversion: 1\nmain: astraltest.MinasLimiteProbe\napi-version: '26.1.2'\ndepend: [AstralMinasLimite]\n")
    log = srv.parent / 'minas-limite-paper.log'
    with log.open('w', encoding='utf8') as output:
        p = subprocess.Popen([str(java), '-Xmx2G', '-jar', 'paper.jar', '--nogui'], cwd=srv, stdin=subprocess.PIPE,
                             stdout=output, stderr=subprocess.STDOUT, text=True)
        try:
            p.wait(timeout=240)
        finally:
            if p.poll() is None:
                p.stdin.write('stop\n'); p.stdin.flush()
                try:
                    p.wait(timeout=30)
                except subprocess.TimeoutExpired:
                    p.kill()
    result = log.read_text('utf8', errors='replace')
    print('\n'.join(l for l in result.splitlines() if any(k in l for k in ('MLTEST', 'AstralMinasLimite', 'Line ', 'Error', 'Exception', 'WARN', 'scripts loaded'))))
    assert 'failures=0' in result and 'MLTEST RESULT' in result, f'Fallo de ensayo: {log}'
    plain = re.sub(r'\x1b\[[0-9;]*m', '', result)
    assert not re.search(r'Line \d+:', plain), f'Error de Skript: {log}'
    assert 'Encountered' not in result and 'Can\'t understand' not in result, f'Error de Skript: {log}'


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--java', type=Path, required=True)
    ap.add_argument('--base', type=Path, required=True)
    a = ap.parse_args()
    run(a.java.resolve(), a.base.resolve())
