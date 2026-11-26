"""Ensayo local de la Nave del Vacio (vista desde afuera, salas, compuertas, jefe). No toca el server.

python tools/probar_nave_paper.py --java <java25> --base .local/testsrv
Necesita .local/nave/spaceship.schem (mapa de terceros, solo local) y el WorldEdit de .local/tanda4a-paper.
De paso BetterModel convierte los modelos: los assets quedan en .local/nave-probe/srv/plugins/BetterModel/build.
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
    import nave
    work = ROOT / '.local/nave-probe'
    if work.exists():
        shutil.rmtree(work)
    srv = work / 'srv'
    srv.mkdir(parents=True)
    for name in ('libraries', 'versions', 'cache'):
        shutil.copytree(base / name, srv / name)
    shutil.copy2(base / 'paper.jar', srv / 'paper.jar')
    (srv / 'eula.txt').write_text('eula=true\n')
    (srv / 'server.properties').write_text('server-ip=127.0.0.1\nserver-port=25614\nonline-mode=false\nlevel-name=world\n'
                                           'level-type=minecraft:flat\ngenerate-structures=false\nmanagement-server-enabled=false\n'
                                           'view-distance=4\nsimulation-distance=4\n')
    (srv / 'spigot.yml').write_text('settings:\n  attribute:\n    maxHealth:\n      max: 1000000000\n    attackDamage:\n      max: 10000000\n')
    packs = srv / 'world/datapacks'
    packs.mkdir(parents=True)
    shutil.copy2(ROOT / 'build/AstralRPG-Items.zip', packs / 'AstralRPG-Items.zip')
    plugins = srv / 'plugins'
    plugins.mkdir()
    for jar in ('AstralOceano.jar', 'skript.jar', 'mythicmobs.jar', 'bettermodel.jar', 'packetevents.jar'):
        shutil.copy2(base / 'plugins' / jar, plugins / jar)
    shutil.copy2(ROOT / 'build/nave/AstralNave.jar', plugins / 'AstralNave.jar')
    shutil.copy2(ROOT / '.local/tanda4a-paper/plugins/worldedit.jar', plugins / 'worldedit.jar')
    (plugins / 'WorldEdit/schematics').mkdir(parents=True)
    shutil.copy2(ROOT / nave.SCHEM, plugins / 'WorldEdit/schematics/spaceship.schem')
    (plugins / 'BetterModel/models').mkdir(parents=True)
    shutil.copy2(ROOT / 'datapack-src/mobs/bettermodel_config.yml', plugins / 'BetterModel/config.yml')
    for m in ('astral_capitan_vacio', 'astral_ojo_vigia'):
        shutil.copy2(ROOT / f'build/models/{m}.bbmodel', plugins / f'BetterModel/models/{m}.bbmodel')
    (plugins / 'MythicMobs/Mobs').mkdir(parents=True)
    (plugins / 'MythicMobs/Skills').mkdir(parents=True)
    shutil.copy2(ROOT / 'build/mythicmobs/mobs/nave.yml', plugins / 'MythicMobs/Mobs/nave.yml')
    shutil.copy2(ROOT / 'build/mythicmobs/skills/nave.yml', plugins / 'MythicMobs/Skills/nave.yml')
    scripts = plugins / 'Skript/scripts'
    scripts.mkdir(parents=True)
    (scripts / 'astral_mazmorras_copias.sk').write_text(copias_script(), encoding='utf8')
    deps = [*srv.joinpath('libraries').rglob('*.jar'), *srv.joinpath('versions').rglob('*.jar')]
    subprocess.run([str(java), '-m', 'jdk.compiler/com.sun.tools.javac.Main', '-encoding', 'UTF-8', '-nowarn', '-classpath',
                    os.pathsep.join(map(str, deps)), '-d', str(work), str(ROOT / 'datapack-src/test_runtime/NaveProbe.java')], check=True)
    salas = nave.salas()
    props = ('llegadas=' + ';'.join(','.join(map(str, s['llegada'])) for s in salas) + '\n'
             'centros=' + ';'.join(','.join(map(str, s['centro'])) for s in salas) + '\n'
             'barreras=' + ';'.join(','.join(l.split()[i] for i in (0, 2, 3)) for l in
                                    (ROOT / 'datapack-src/nave_barreras.txt').read_text('utf8').splitlines()[1::400]) + '\n')
    with zipfile.ZipFile(plugins / 'NaveProbe.jar', 'w') as z:
        for f in (work / 'astraltest').glob('NaveProbe*.class'):
            z.write(f, 'astraltest/' + f.name)
        z.writestr('nave-probe.properties', props)
        z.writestr('plugin.yml', "name: NaveProbe\nversion: 1\nmain: astraltest.NaveProbe\napi-version: '26.1.2'\n"
                                 "depend: [AstralNave, AstralOceano, Skript, MythicMobs, WorldEdit]\n")
    log = work / 'paper.log'
    with log.open('w', encoding='utf8') as out:
        subprocess.run([str(java), '-Xmx4G', '-jar', 'paper.jar', '--nogui'], cwd=srv, stdin=subprocess.DEVNULL,
                       stdout=out, stderr=subprocess.STDOUT, timeout=1800)
    text = log.read_text(encoding='utf8', errors='replace')
    print('\n'.join(l for l in text.splitlines() if 'NAVE ' in l or 'Nave del Vacio' in l or ('Skript' in l and 'error' in l.lower())
                    or ('MythicMobs' in l and ('rror' in l or 'Loaded' in l)) or 'Exception' in l))
    if 'NAVE RESULT failures=0' not in text:
        raise SystemExit('fallo: ' + str(log))


if __name__ == '__main__':
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument('--java', type=Path, required=True)
    a.add_argument('--base', type=Path, required=True)
    args = a.parse_args()
    run(args.java.resolve(), args.base.resolve())
