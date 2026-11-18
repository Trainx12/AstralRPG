"""Ensayo real aislado de AstralDuelos + Duels 8.3 + Skript, solo localhost."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import time
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def run(java, base):
    import yaml
    work = ROOT / '.local/duelos-ui-probe'
    srv = work / 'paper'
    srv.mkdir(parents=True, exist_ok=True)
    for name in ('libraries', 'versions', 'cache'):
        if not (srv / name).exists():
            shutil.copytree(base / name, srv / name)
    shutil.copyfile(base / 'paper.jar', srv / 'paper.jar')
    (srv / 'eula.txt').write_text('eula=true\n')
    (srv / 'server.properties').write_text('server-ip=127.0.0.1\nserver-port=25612\nonline-mode=false\nlevel-name=world\nlevel-type=minecraft:flat\ngenerate-structures=false\nmanagement-server-enabled=false\nspawn-protection=0\nview-distance=2\nsimulation-distance=2\nmax-tick-time=-1\n')
    plugins = srv / 'plugins'
    plugins.mkdir(exist_ok=True)
    for src, name in [(ROOT / '.local/duels/Duels-Optimised-8.3.jar', 'Duels.jar'), (base / 'plugins/skript.jar', 'skript.jar'), (ROOT / 'build/runtime/AstralDuelos.jar', 'AstralDuelos.jar')]:
        shutil.copyfile(src, plugins / name)
    shutil.copytree(ROOT / 'build/plugins-basicos/Duels', plugins / 'Duels', dirs_exist_ok=True)
    config = plugins / 'Duels/config.yml'
    data = yaml.safe_load(config.read_text('utf8'))
    data['duel']['whitelisted-commands'] += ['duelos', 'astralduelos:duelos', 'duels:duel', 'desafiar', 'astralduelos:desafiar']
    config.write_text(yaml.safe_dump(data, allow_unicode=True), 'utf8')
    scripts = plugins / 'Skript/scripts'
    scripts.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / 'build/duelos/astral_duelos.sk', scripts / 'astral_duelos.sk')
    deps = [*srv.joinpath('libraries').rglob('*.jar'), *srv.joinpath('versions').rglob('*.jar'), plugins / 'Duels.jar', plugins / 'AstralDuelos.jar']
    subprocess.run([str(java), '-m', 'jdk.compiler/com.sun.tools.javac.Main', '-encoding', 'UTF-8', '-classpath', os.pathsep.join(map(str, deps)), '-d', str(work), str(ROOT / 'datapack-src/test_runtime/DuelosUIProbe.java')], check=True)
    with zipfile.ZipFile(plugins / 'DuelosUIProbe.jar', 'w') as z:
        for p in (work / 'astral').glob('DuelosUIProbe*.class'):
            z.write(p, 'astral/' + p.name)
        z.writestr('plugin.yml', "name: DuelosUIProbe\nversion: 1\nmain: astral.DuelosUIProbe\napi-version: '26.1.2'\nloadbefore: [Duels]\ncommands:\n  duelosuiprobe: {}\n")
    log = work / 'paper.log'
    with log.open('w', encoding='utf8') as out:
        process = subprocess.Popen([str(java), '-Xms256M', '-Xmx2G', '-jar', 'paper.jar', '--nogui'], cwd=srv, stdin=subprocess.PIPE, stdout=out, stderr=subprocess.STDOUT, text=True)
        def cmd(s):
            process.stdin.write(s + '\n')
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
            for step, delay in [('setup', 8), ('menus', 2), ('players', 2), ('arenas', 2), ('confirm', 2), ('requests', 9), ('combat', 15), ('after', 2), ('rematch', 9), ('surrender', 15), ('final', 5), ('pages', 2)]:
                cmd('duelosuiprobe ' + step)
                time.sleep(delay)
        finally:
            cmd('stop')
            try:
                process.wait(timeout=60)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=15)
                raise RuntimeError('Paper de prueba no respondio a stop: ' + str(log))
    text = log.read_text('utf8', errors='replace')
    print('\n'.join(l for l in text.splitlines() if 'DUELOSUI ' in l or 'ERROR' in l or '[Skript]' in l))
    if 'failures=0' not in text or 'DUELOSUI FAIL' in text or 'generated an exception' in text:
        raise AssertionError(log)


if __name__ == '__main__':
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument('--java', type=Path, required=True)
    a.add_argument('--base', type=Path, required=True)
    args = a.parse_args()
    run(args.java.resolve(), args.base.resolve())
