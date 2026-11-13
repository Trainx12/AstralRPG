"""Ensayo local de la Fosa del Crustaceo: entrada escondida, respiracion, oleadas, jefe. No toca el server.

python tools/probar_fosa_paper.py --java <java25> --base .local/testsrv
Necesita las regiones de la arena en .local/acuatico/fosa-mundo/region (mapa de terceros, solo local).
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


def run(java, base):
    sys.stdout.reconfigure(errors='replace')
    from mazmorras_copias import script as copias_script
    work = ROOT / '.local/fosa-probe'
    if work.exists():
        shutil.rmtree(work)
    srv = work / 'srv'
    srv.mkdir(parents=True)
    for name in ('libraries', 'versions', 'cache'):
        shutil.copytree(base / name, srv / name)
    shutil.copy2(base / 'paper.jar', srv / 'paper.jar')
    (srv / 'eula.txt').write_text('eula=true\n')
    (srv / 'server.properties').write_text('server-ip=127.0.0.1\nserver-port=25613\nonline-mode=false\nlevel-name=world\n'
                                           'level-type=minecraft:flat\ngenerate-structures=false\nmanagement-server-enabled=false\n')
    (srv / 'spigot.yml').write_text('settings:\n  attribute:\n    maxHealth:\n      max: 1000000000\n    attackDamage:\n      max: 10000000\n')
    packs = srv / 'world/datapacks'
    packs.mkdir(parents=True)
    shutil.copy2(ROOT / 'build/AstralRPG-Items.zip', packs / 'AstralRPG-Items.zip')
    region = srv / 'world/dimensions/minecraft/fosa/region'
    shutil.copytree(ROOT / '.local/acuatico/fosa-mundo/region', region)
    plugins = srv / 'plugins'
    plugins.mkdir()
    shutil.copy2(ROOT / 'build/oceano/AstralOceano.jar', plugins / 'AstralOceano.jar')
    shutil.copy2(base / 'plugins/skript.jar', plugins / 'skript.jar')
    shutil.copy2(base / 'plugins/mythicmobs.jar', plugins / 'mythicmobs.jar')
    (plugins / 'MythicMobs/Mobs').mkdir(parents=True)
    shutil.copy2(ROOT / 'build/mythicmobs/mobs/fosa.yml', plugins / 'MythicMobs/Mobs/fosa.yml')
    scripts = plugins / 'Skript/scripts'
    scripts.mkdir(parents=True)
    (scripts / 'astral_mazmorras_copias.sk').write_text(copias_script(), encoding='utf8')
    deps = [*srv.joinpath('libraries').rglob('*.jar'), *srv.joinpath('versions').rglob('*.jar')]
    subprocess.run([str(java), '-m', 'jdk.compiler/com.sun.tools.javac.Main', '-encoding', 'UTF-8', '-nowarn', '-classpath',
                    os.pathsep.join(map(str, deps)), '-d', str(work), str(ROOT / 'datapack-src/test_runtime/FosaProbe.java')], check=True)
    with zipfile.ZipFile(plugins / 'FosaProbe.jar', 'w') as z:
        for f in (work / 'astraltest').glob('FosaProbe*.class'):
            z.write(f, 'astraltest/' + f.name)
        z.writestr('plugin.yml', "name: FosaProbe\nversion: 1\nmain: astraltest.FosaProbe\napi-version: '26.1.2'\n"
                                 "depend: [AstralOceano, Skript, MythicMobs]\n")
    log = work / 'paper.log'
    with log.open('w', encoding='utf8') as out:
        subprocess.run([str(java), '-Xmx4G', '-jar', 'paper.jar', '--nogui'], cwd=srv, stdin=subprocess.DEVNULL,
                       stdout=out, stderr=subprocess.STDOUT, timeout=1800)
    text = log.read_text(encoding='utf8', errors='replace')
    print('\n'.join(l for l in text.splitlines() if 'FOSA ' in l or ('Skript' in l and 'error' in l.lower()) or 'Line ' in l))
    if 'FOSA RESULT failures=0' not in text:
        raise SystemExit('fallo: ' + str(log))


if __name__ == '__main__':
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument('--java', type=Path, required=True)
    a.add_argument('--base', type=Path, required=True)
    args = a.parse_args()
    run(args.java.resolve(), args.base.resolve())
