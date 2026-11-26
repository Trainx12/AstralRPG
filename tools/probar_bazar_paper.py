"""Prueba aislada AstralBazar con dos bots y Vault/Essentials reales; nunca remoto.

python tools/probar_bazar_paper.py --java <bin JDK25> [--base .local/testsrv]
Conserva cada ensayo en .local/bazar-probe-<fecha>; no borra ensayos anteriores.
"""
import argparse
import datetime
import os
import json
import re
from pathlib import Path
import shutil
import socket
import subprocess
import time
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def run(java, base):
    with zipfile.ZipFile(ROOT / 'build/bazar/AstralBazar.jar') as jar:
        if 'version: 1.2.0' not in jar.read('plugin.yml').decode():
            raise SystemExit('Generar AstralBazar 1.2.0 antes de probar.')
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    work = ROOT / '.local' / ('bazar-probe-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
    srv = work / 'srv'
    srv.mkdir(parents=True)
    for folder in ('libraries', 'versions', 'cache'):
        shutil.copytree(base / folder, srv / folder)
    shutil.copy2(base / 'paper.jar', srv / 'paper.jar')
    (srv / 'eula.txt').write_text('eula=true\n')
    (srv / 'server.properties').write_text(f'server-ip=127.0.0.1\nserver-port={port}\nonline-mode=false\n'
        'level-name=world\ngenerate-structures=false\n'
        'management-server-enabled=false\nview-distance=2\nsimulation-distance=2\nspawn-protection=0\n')
    plugins = srv / 'plugins'
    plugins.mkdir()
    for jar in ('Vault.jar', 'EssentialsX.jar'):
        shutil.copy2(base / 'plugins' / jar, plugins / jar)
    shutil.copy2(ROOT / 'build/bazar/AstralBazar.jar', plugins / 'AstralBazar.jar')
    (srv / 'world/datapacks').mkdir(parents=True)
    # Only the real registries used by the catalog. Running unrelated tick scripts
    # would mutate test players and couples this test to unfinished local work.
    with zipfile.ZipFile(ROOT / 'build/AstralRPG-Items.zip') as source, zipfile.ZipFile(srv / 'world/datapacks/bazar-registros.zip','w') as dest:
        for name in source.namelist():
            if name == 'pack.mcmeta' or '/enchantment/' in name or '/tags/item/' in name or '/tags/enchantment/' in name:
                dest.writestr(name, source.read(name))
    deps = list((srv / 'libraries').rglob('*.jar')) + list(plugins.glob('*.jar'))
    java_exe = str(java / ('java.exe' if os.name == 'nt' else 'java'))
    subprocess.run([java_exe, '-m', 'jdk.compiler/com.sun.tools.javac.Main', '-encoding', 'UTF-8',
                    '-classpath', os.pathsep.join(map(str, deps)), '-d', str(work),
                    str(ROOT / 'datapack-src/test_runtime/BazarProbe.java')], check=True)
    with zipfile.ZipFile(plugins / 'AstralBazar.jar', 'a') as z:
        for p in (work / 'astral').glob('BazarProbe*.class'):
            if '$Launcher' not in p.name:
                z.write(p, 'astral/' + p.name)
    with zipfile.ZipFile(plugins / 'BazarProbe.jar', 'w') as z:
        p = work / 'astral/BazarProbe$Launcher.class'
        z.write(p, 'astral/' + p.name)
        z.writestr('plugin.yml', "name: BazarProbe\nversion: 1\nmain: astral.BazarProbe$Launcher\napi-version: '26.1.2'\ndepend: [AstralBazar]\n")
    botfile = work / 'bots.cjs'
    botfile.write_text("const mc=require(" + repr(str(ROOT / '.local/asw-test/node_modules/minecraft-protocol').replace('\\', '/')) + ");\n"
        f"for(const username of ['BazarUno','BazarDos']){{const c=mc.createClient({{host:'127.0.0.1',port:{port},username,auth:'offline',version:'26.1.2'}});"
        "c.on('error',e=>console.log(username,e.message));c.on('position',p=>c.write('teleport_confirm',{teleportId:p.teleportId}));}"
        "setTimeout(()=>process.exit(1),240000);\n")
    log = work / 'paper.log'
    for phase in range(2):
        bot = None
        offset = log.stat().st_size if log.exists() else 0
        with log.open('a', encoding='utf8') as output, (work/'bots.log').open('a', encoding='utf8') as botout:
            proc = subprocess.Popen([java_exe, '-Xmx2G', '-jar', 'paper.jar', '--nogui'], cwd=srv,
                                    stdin=subprocess.PIPE, stdout=output, stderr=subprocess.STDOUT, text=True)
            try:
                start = time.time()
                while proc.poll() is None and time.time()-start < 300:
                    time.sleep(2)
                    with log.open('rb') as source:
                        source.seek(offset)
                        text = source.read().decode('utf8', errors='replace')
                    if bot is None and 'Done (' in text:
                        bot = subprocess.Popen(['node', str(botfile)], stdout=botout, stderr=subprocess.STDOUT)
                    if 'BAZ RESULT' in text or 'No se pudo iniciar Bazar' in text or 'Error occurred while enabling BazarProbe' in text:
                        break
                if proc.poll() is None:
                    proc.stdin.write('stop\n');proc.stdin.flush()
                    try:
                        proc.wait(timeout=40)
                    except subprocess.TimeoutExpired:
                        proc.kill()
            finally:
                if proc.poll() is None:
                    proc.kill()
                if bot and bot.poll() is None:
                    bot.kill()
                    bot.wait(timeout=10)
        text = log.read_text(encoding='utf8', errors='replace')
        if 'BAZ RESULT' in text or 'BAZ CRASH READY' not in text:
            break
    text = log.read_text(encoding='utf8', errors='replace')
    print('\n'.join(line for line in text.splitlines() if 'BAZ FAIL' in line or 'BAZ RESULT' in line or 'BAZ CRASH READY' in line or 'BAZ EXCEPTION' in line or ('AstralBazar' in line and 'BAZ OK' not in line) or 'Exception' in line))
    print('Ensayo:', work)
    results = [line for line in text.splitlines() if 'BAZ RESULT' in line]
    if not results or 'failures=0' not in results[-1]:
        raise SystemExit('Ensayo fallido: '+str(log))
    if 'BAZ CRASH READY' not in text:
        raise SystemExit('Falta la prueba de caída y reapertura de JVM.')
    count = int(re.search(r'checks=(\d+)', results[-1])[1])
    (work / 'resultado.json').write_text(json.dumps({'version': '1.2.0', 'checks': count,
        'failures': 0, 'crash_reopen': True, 'players': 2}, indent=2)+'\n', encoding='utf8')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--java', type=Path, required=True)
    ap.add_argument('--base', type=Path, default=ROOT / '.local/testsrv')
    args = ap.parse_args()
    run(args.java.resolve(), args.base.resolve())
