"""Ensayo local de la revision del 23/11 (pedido del dueno). No toca el server remoto.

python tools/probar_revision_23_11.py --java <bin JDK25> [--base .local/testsrv]

Paper local con el datapack, AuraSkills, MythicMobs + BetterModel (invocacion), AstralClases y AstralDueno.
Un bot entra y Revision23Probe comprueba: invocaciones (aparecen, cartel con duenio/tier/vida, pegan y reciben),
guadana sin Cosecha, mobs de mazmorra mas rapidos/agresivos/sin freno en el agua, /modo admin|jugador y /sala.
"""
import argparse
import hashlib
import os
import shutil
import subprocess
import sys
import time
import uuid
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PORT = 25619
BOT_NAME = 'R23Probe'


def offline_uuid(name):
    h = bytearray(hashlib.md5(('OfflinePlayer:' + name).encode()).digest())
    h[6] = (h[6] & 0x0f) | 0x30
    h[8] = (h[8] & 0x3f) | 0x80
    return str(uuid.UUID(bytes=bytes(h)))


def run(java, base):
    work = ROOT / '.local/revision-23-probe'
    if work.exists():
        shutil.rmtree(work)
    srv = work / 'srv'
    srv.mkdir(parents=True)
    for name in ('libraries', 'versions', 'cache'):
        shutil.copytree(base / name, srv / name, copy_function=os.link)
    shutil.copy2(base / 'paper.jar', srv / 'paper.jar')
    (srv / 'eula.txt').write_text('eula=true\n')
    (srv / 'server.properties').write_text(f'server-ip=127.0.0.1\nserver-port={PORT}\nonline-mode=false\nlevel-name=world\n'
                                           'level-type=minecraft:flat\ngenerate-structures=false\nmanagement-server-enabled=false\n'
                                           'view-distance=4\nsimulation-distance=4\nspawn-protection=0\n')
    (srv / 'spigot.yml').write_text('settings:\n  attribute:\n    maxHealth:\n      max: 1000000000\n    attackDamage:\n      max: 10000000\n')
    (srv / 'world/datapacks').mkdir(parents=True)
    shutil.copy2(ROOT / 'build/AstralRPG-Items.zip', srv / 'world/datapacks/AstralRPG-Items.zip')
    plugins = srv / 'plugins'
    plugins.mkdir()
    for jar in ('mythicmobs.jar', 'bettermodel.jar', 'packetevents.jar', 'auraskills.jar'):
        shutil.copy2(base / 'plugins' / jar, plugins / jar)
    shutil.copy2(ROOT / 'build/clases/AstralClases.jar', plugins / 'AstralClases.jar')
    shutil.copy2(ROOT / 'build/dueno/AstralDueno.jar', plugins / 'AstralDueno.jar')
    shutil.copy2(ROOT / 'build/runtime/AstralEfectos.jar', plugins / 'AstralEfectos.jar')
    (plugins / 'AstralDueno').mkdir()
    (plugins / 'AstralDueno/config.yml').write_text(f"duenos:\n- '{offline_uuid(BOT_NAME)}'\nmundo_inicio: world\n")
    bm = plugins / 'BetterModel'
    (bm / 'models').mkdir(parents=True)
    for m in ('astral_invocacion', 'astral_fx_clases'):
        shutil.copy2(ROOT / f'build/models/{m}.bbmodel', bm / f'models/{m}.bbmodel')
    (plugins / 'MythicMobs/Mobs').mkdir(parents=True)
    shutil.copy2(ROOT / 'build/clases/MythicMobs/astral_clases.yml', plugins / 'MythicMobs/Mobs/astral_clases.yml')
    deps = [*srv.joinpath('libraries').rglob('*.jar'), plugins / 'auraskills.jar']
    subprocess.run([str(java / 'java'), '-m', 'jdk.compiler/com.sun.tools.javac.Main', '-encoding', 'UTF-8', '-nowarn', '-classpath',
                    os.pathsep.join(map(str, deps)), '-d', str(work), str(ROOT / 'datapack-src/test_runtime/Revision23Probe.java')],
                   check=True)
    with zipfile.ZipFile(plugins / 'Revision23Probe.jar', 'w') as z:
        for f in (work / 'astraltest').glob('Revision23Probe*.class'):
            z.write(f, 'astraltest/' + f.name)
        z.writestr('plugin.yml', "name: Revision23Probe\nversion: 1\nmain: astraltest.Revision23Probe\napi-version: '26.1.2'\n"
                                 "depend: [AuraSkills, AstralClases, AstralDueno]\n")
    (work / 'bot.js').write_text(BOT.replace('__PORT__', str(PORT)).replace('__NAME__', BOT_NAME)
                                 .replace('__NM__', (ROOT / '.local/asw-test/node_modules').as_posix()))
    log = work / 'paper.log'
    bot = None
    with log.open('w', encoding='utf8') as out:
        proc = subprocess.Popen([str(java / 'java'), '-Xmx4G', '-jar', 'paper.jar', '--nogui'], cwd=srv, stdin=subprocess.DEVNULL,
                                stdout=out, stderr=subprocess.STDOUT)
        t0 = time.time()
        while proc.poll() is None and time.time() - t0 < 900:
            time.sleep(2)
            text = log.read_text(encoding='utf8', errors='replace')
            if bot is None and 'Done (' in text:
                time.sleep(5)
                bot = subprocess.Popen(['node', str(work / 'bot.js')], cwd=ROOT / '.local/asw-test',
                                       stdout=(work / 'bot.log').open('w'), stderr=subprocess.STDOUT)
        if proc.poll() is None:
            proc.kill()
    if bot and bot.poll() is None:
        bot.kill()
    text = log.read_text(encoding='utf8', errors='replace')
    print('\n'.join(l[-260:] for l in text.splitlines() if 'R23 ' in l or 'Exception' in l or
                    (('AstralClases' in l or 'AstralDueno' in l or 'AstralEfectos' in l) and ('rror' in l or 'arn' in l))))
    res = [l for l in text.splitlines() if 'R23 RESULT' in l]
    if not res or 'failures=0' not in res[0]:
        raise SystemExit('fallo: ' + str(log))


BOT = """
const mc = require('__NM__/minecraft-protocol');
const client = mc.createClient({host: '127.0.0.1', port: __PORT__, username: '__NAME__', auth: 'offline', version: '26.1.2'});
client.on('error', e => console.log('ERR', e.message));
client.on('login', () => console.log('LOGIN'));
client.on('position', p => { client.write('teleport_confirm', {teleportId: p.teleportId}); });
client.on('end', r => { console.log('END', r); process.exit(0); });
setTimeout(() => process.exit(0), 300000);
"""


if __name__ == '__main__':
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument('--java', type=Path, required=True, help='carpeta bin del JDK 25')
    a.add_argument('--base', type=Path, default=ROOT / '.local/testsrv')
    args = a.parse_args()
    run(args.java.resolve(), args.base.resolve())
