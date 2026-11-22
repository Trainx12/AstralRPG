"""Ensayo local de los modelos del 22/11 (Capitan del Vacio rehecho, Ojo Vigia y animaciones de jugador). No toca el server.

python tools/probar_modelos_22_11.py --java <bin JDK25> [--base .local/testsrv]

- Paper local con BetterModel (player-animation prendido), MythicMobs y AstralClases.
- PosesProbe: modelos cargados, animaciones presentes, el Capitan aparece por MythicMobs y reproduce cada estado,
  y un bot (minecraft-protocol de .local/asw-test) entra para probar guadana_golpe, guadana_giro e invocar.
- De paso BetterModel convierte los modelos: los assets quedan en .local/modelos-2211-probe/srv/plugins/BetterModel/build.
"""
import argparse
import os
import shutil
import subprocess
import sys
import time
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'datapack-src'))
PORT = 25617


def config_bettermodel():
    """La config del repo con el modulo de animaciones de jugador prendido."""
    txt = (ROOT / 'datapack-src/mobs/bettermodel_config.yml').read_text(encoding='utf8')
    return txt.replace('player-animation: false', 'player-animation: true')


def run(java, base):
    sys.stdout.reconfigure(errors='replace')
    import nave
    import poses_jugador
    from mobs import capitan_vacio
    capitan_vacio.export(preview=False)
    nave.generate()
    poses_jugador.save()
    work = ROOT / '.local/modelos-2211-probe'
    if work.exists():
        shutil.rmtree(work)
    srv = work / 'srv'
    srv.mkdir(parents=True)
    for name in ('libraries', 'versions', 'cache'):
        shutil.copytree(base / name, srv / name)
    shutil.copy2(base / 'paper.jar', srv / 'paper.jar')
    (srv / 'eula.txt').write_text('eula=true\n')
    (srv / 'server.properties').write_text(f'server-ip=127.0.0.1\nserver-port={PORT}\nonline-mode=false\nlevel-name=world\n'
                                           'level-type=minecraft:flat\ngenerate-structures=false\nmanagement-server-enabled=false\n'
                                           'view-distance=4\nsimulation-distance=4\nspawn-protection=0\n')
    (srv / 'spigot.yml').write_text('settings:\n  attribute:\n    maxHealth:\n      max: 1000000000\n    attackDamage:\n      max: 10000000\n')
    plugins = srv / 'plugins'
    plugins.mkdir()
    for jar in ('mythicmobs.jar', 'bettermodel.jar', 'packetevents.jar', 'auraskills.jar'):
        if (base / 'plugins' / jar).exists():
            shutil.copy2(base / 'plugins' / jar, plugins / jar)
    shutil.copy2(ROOT / 'build/clases/AstralClases.jar', plugins / 'AstralClases.jar')
    bm = plugins / 'BetterModel'
    (bm / 'models').mkdir(parents=True)
    (bm / 'players').mkdir(parents=True)
    (bm / 'config.yml').write_text(config_bettermodel(), encoding='utf8')
    for m in ('astral_capitan_vacio', 'astral_ojo_vigia', 'astral_fx_clases'):
        shutil.copy2(ROOT / f'build/models/{m}.bbmodel', bm / f'models/{m}.bbmodel')
    shutil.copy2(ROOT / 'build/players/astral_poses.bbmodel', bm / 'players/astral_poses.bbmodel')
    (plugins / 'MythicMobs/Mobs').mkdir(parents=True)
    (plugins / 'MythicMobs/Skills').mkdir(parents=True)
    shutil.copy2(ROOT / 'build/mythicmobs/mobs/nave.yml', plugins / 'MythicMobs/Mobs/nave.yml')
    shutil.copy2(ROOT / 'build/mythicmobs/skills/nave.yml', plugins / 'MythicMobs/Skills/nave.yml')
    deps = [*srv.joinpath('libraries').rglob('*.jar'), *srv.joinpath('versions').rglob('*.jar'), plugins / 'bettermodel.jar']
    subprocess.run([str(java / 'java'), '-m', 'jdk.compiler/com.sun.tools.javac.Main', '-encoding', 'UTF-8', '-nowarn', '-classpath',
                    os.pathsep.join(map(str, deps)), '-d', str(work), str(ROOT / 'datapack-src/test_runtime/PosesProbe.java')], check=True)
    with zipfile.ZipFile(plugins / 'PosesProbe.jar', 'w') as z:
        for f in (work / 'astraltest').glob('PosesProbe*.class'):
            z.write(f, 'astraltest/' + f.name)
        z.writestr('plugin.yml', "name: PosesProbe\nversion: 1\nmain: astraltest.PosesProbe\napi-version: '26.1.2'\n"
                                 "depend: [BetterModel, MythicMobs]\n")
    (srv / 'ops.json').write_text('[]')
    (work / 'bot.js').write_text(BOT.replace('__PORT__', str(PORT)).replace('__NM__', (ROOT / '.local/asw-test/node_modules').as_posix()))
    log = work / 'paper.log'
    bot = None
    with log.open('w', encoding='utf8') as out:
        proc = subprocess.Popen([str(java / 'java'), '-Xmx4G', '-jar', 'paper.jar', '--nogui'], cwd=srv, stdin=subprocess.DEVNULL,
                                stdout=out, stderr=subprocess.STDOUT)
        t0 = time.time()
        while proc.poll() is None and time.time() - t0 < 1500:
            time.sleep(2)
            text = log.read_text(encoding='utf8', errors='replace')
            if bot is None and 'Done (' in text and 'POSES PASS modelo astral_ojo_vigia' in text:
                bot = subprocess.Popen(['node', str(work / 'bot.js')], cwd=ROOT / '.local/asw-test',
                                       stdout=(work / 'bot.log').open('w'), stderr=subprocess.STDOUT)
        if proc.poll() is None:
            proc.kill()
    if bot and bot.poll() is None:
        bot.kill()
    text = log.read_text(encoding='utf8', errors='replace')
    print('\n'.join(l for l in text.splitlines() if 'POSES ' in l or ('BetterModel' in l and ('rror' in l or 'xception' in l or 'arn' in l))
                    or ('MythicMobs' in l and 'rror' in l) or 'Exception' in l or 'astral_poses' in l))
    if 'POSES RESULT' not in text or 'failures=0' not in text.split('POSES RESULT')[1].splitlines()[0]:
        raise SystemExit('fallo: ' + str(log))


BOT = """
const mc = require('__NM__/minecraft-protocol');
const client = mc.createClient({host: '127.0.0.1', port: __PORT__, username: 'PoseProbe', auth: 'offline', version: '26.1.2'});
client.on('error', e => console.log('ERR', e.message));
client.on('login', () => console.log('LOGIN'));
client.on('position', p => { client.write('teleport_confirm', {teleportId: p.teleportId}); });
client.on('end', r => { console.log('END', r); process.exit(0); });
setTimeout(() => process.exit(0), 120000);
"""


if __name__ == '__main__':
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument('--java', type=Path, required=True, help='carpeta bin del JDK 25')
    a.add_argument('--base', type=Path, default=ROOT / '.local/testsrv')
    args = a.parse_args()
    run(args.java.resolve(), args.base.resolve())
