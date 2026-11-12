"""Ensayo local de la Mazmorra Infinita: ventanas, party, salas, tier, subida, mobs y limpieza. No toca el server.

python tools/probar_infinita_paper.py --java <java25> --base .local/testsrv
Tiempos acortados: primera subida 20 s, despues cada 10 s, aviso a los 5 s.
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
    sys.stdout.reconfigure(errors="replace")
    import infinita
    from mazmorras_copias import script as copias_script
    work = ROOT/'.local/infinita-probe'
    if work.exists():
        shutil.rmtree(work)
    srv = work/'srv'
    srv.mkdir(parents=True)
    for name in ('libraries', 'versions', 'cache'):
        shutil.copytree(base/name, srv/name)
    shutil.copy2(base/'paper.jar', srv/'paper.jar')
    (srv/'eula.txt').write_text('eula=true\n')
    # Como en el server: topes de atributos subidos (vida de mobs con tier).
    (srv/'spigot.yml').write_text('settings:\n  attribute:\n    maxHealth:\n      max: 1000000000\n    attackDamage:\n      max: 10000000\n')
    (srv/'server.properties').write_text('server-ip=127.0.0.1\nserver-port=25608\nonline-mode=false\nlevel-name=world\n'
        'level-type=minecraft:flat\ngenerate-structures=false\nmanagement-server-enabled=false\nspawn-protection=0\n')
    packs = srv/'world/datapacks'
    packs.mkdir(parents=True)
    shutil.copy2(ROOT/'build/AstralRPG-Items.zip', packs/'AstralRPG-Items.zip')
    plugins = srv/'plugins'
    plugins.mkdir()
    shutil.copy2(base/'plugins/skript.jar', plugins/'skript.jar')
    scripts = plugins/'Skript/scripts'
    scripts.mkdir(parents=True)
    (scripts/'astral_mazmorras_copias.sk').write_text(copias_script(), encoding='utf8')
    (scripts/'astral_infinita.sk').write_text(infinita.script(20, 10, 5), encoding='utf8')
    from panel_mundos import script as panel_script
    (scripts/'astral_panel_mundos.sk').write_text(panel_script(), encoding='utf8')
    deps = [*srv.joinpath('libraries').rglob('*.jar'), *srv.joinpath('versions').rglob('*.jar')]
    subprocess.run([str(java), '-m', 'jdk.compiler/com.sun.tools.javac.Main', '-encoding', 'UTF-8', '-classpath',
                    os.pathsep.join(map(str, deps)), '-d', str(work), str(ROOT/'datapack-src/test_runtime/InfinitaProbe.java')], check=True)
    with zipfile.ZipFile(plugins/'InfinitaProbe.jar', 'w') as z:
        z.write(work/'astraltest/InfinitaProbe.class', 'astraltest/InfinitaProbe.class')
        z.writestr('plugin.yml', "name: InfinitaProbe\nversion: 1\nmain: astraltest.InfinitaProbe\napi-version: '26.1.2'\n"
                   "loadbefore: [Skript]\ncommands:\n  infprobe: {}\n  spawn: {}\n")
    # Arena de las salas 1 y 2 (mismos comandos que el server, sin Multiverse ni WorldGuard).
    # Mapa real (regiones de tools/pegar_infinita.py) en las salas 1 y 2.
    for w in ('infinita', 'infinita_2'):
        dest = srv/f'world/dimensions/minecraft/{w}/region'; dest.mkdir(parents=True)
        for f in (ROOT/'.local/infinita-mapa/entrega/region').glob('*.mca'): shutil.copy2(f, dest/f.name)
    arena = [f'execute in minecraft:{w} run gamerule minecraft:{g} {v}' for w in ('infinita', 'infinita_2')
              for g, v in (('spawn_mobs', 'false'), ('mob_griefing', 'false'), ('keep_inventory', 'true'))]
    # Los jugadores simulados no cargan chunks: se fuerza la arena para poder contar los mobs.
    arena += [f'execute in minecraft:{w} run forceload add -48 -46 51 48' for w in ('infinita', 'infinita_2')]
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
            for c in arena:
                command(c); time.sleep(0.1)
            steps = [('setup', 3), ('tierA', 1), ('pickA', 1), ('velA', 2), ('tierC', 1), ('pickC', 1), ('velC', 2),
                     ('inside', 1), ('', 8), ('mobs', 1), ('', 14), ('raise', 1), ('boom', 2), ('leave', 4), ('clean', 1), ('result', 1)]
            for c, wait in steps:
                if c: command('infprobe ' + c)
                time.sleep(wait)
        finally:
            command('stop')
            p.wait(timeout=120)
    text = log.read_text(encoding='utf8', errors='replace')
    print('\n'.join(l for l in text.splitlines() if 'INF ' in l or ('Skript' in l and ('error' in l.lower() or 'loaded' in l.lower()))
                    or 'Line ' in l or 'encountered' in l))
    if 'INF RESULT failures=0' not in text or 'All scripts loaded without errors' not in text:
        raise AssertionError(str(log))


if __name__ == '__main__':
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument('--java', type=Path, required=True)
    a.add_argument('--base', type=Path, required=True)
    args = a.parse_args()
    run(args.java.resolve(), args.base.resolve())
