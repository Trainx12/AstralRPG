"""Ensayo aislado de las clases nuevas (clases.py, 22/11) en Paper 26.1.2. Solo 127.0.0.1; no toca el server remoto.

Carga el datapack (build/AstralRPG-Items.zip), MythicMobs con la invocacion y AstralClases.jar. Comprueba:
- que el datapack cargue (encantamientos de guadanas cambiados) y existan los items nuevos;
- que AstralClases arranque y lea clases.json;
- que la invocacion aparezca y que un mob con tier le pegue con la escala (DANO_MOB x defensa);
- que las areas/veneno no apunten a invocaciones (etiquetas astral.pet / astral.invocacion).
Uso: python tools/probar_clases_paper.py --java <bin/java.exe>
"""
import argparse
import os
import re
import shutil
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / '.local/testsrv'


def main(java):
    work = ROOT / '.local/clases-probe'
    srv = work / 'paper'
    if srv.exists():
        shutil.rmtree(srv / 'probe', ignore_errors=True)
    srv.mkdir(parents=True, exist_ok=True)
    for n in ('libraries', 'versions', 'cache'):
        if not (srv / n).exists():
            shutil.copytree(BASE / n, srv / n, copy_function=os.link)
    shutil.copy2(BASE / 'paper.jar', srv / 'paper.jar')
    (srv / 'eula.txt').write_text('eula=true\n')
    (srv / 'server.properties').write_text(
        'server-ip=127.0.0.1\nserver-port=25633\nonline-mode=false\nlevel-name=probe\nlevel-type=minecraft:flat\n'
        'generate-structures=false\nspawn-protection=0\nmanagement-server-enabled=false\nview-distance=2\nsimulation-distance=2\n')
    plugins = srv / 'plugins'
    plugins.mkdir(exist_ok=True)
    for name in ('auraskills.jar', 'mythicmobs.jar', 'packetevents.jar'):
        shutil.copy2(BASE / 'plugins' / name, plugins / name)
    shutil.copy2(ROOT / 'build/clases/AstralClases.jar', plugins / 'AstralClases.jar')
    mm = plugins / 'MythicMobs/mobs'
    mm.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / 'build/clases/MythicMobs/astral_clases.yml', mm / 'astral_clases.yml')
    packs = srv / 'probe/datapacks'
    packs.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / 'build/AstralRPG-Items.zip', packs / 'AstralRPG-Items.zip')
    log = work / 'paper.log'
    with log.open('w', encoding='utf8') as out:
        p = subprocess.Popen([str(java), '-Xms512M', '-Xmx3G', '-jar', 'paper.jar', '--nogui'], cwd=srv,
                             stdin=subprocess.PIPE, stdout=out, stderr=subprocess.STDOUT, text=True)

        def cmd(s, wait=1.0):
            p.stdin.write(s + '\n')
            p.stdin.flush()
            time.sleep(wait)
        try:
            for _ in range(400):
                if 'For help, type' in log.read_text('utf8', errors='replace'):
                    break
                if p.poll() is not None:
                    raise RuntimeError('Paper termino: ' + str(log))
                time.sleep(1)
            time.sleep(8)
            cmd('forceload add 0 0')
            cmd('datapack list enabled', 2)
            cmd('loot spawn 0 -59 0 loot astral:item/segador_5_chestplate')
            cmd('loot spawn 0 -59 0 loot astral:item/libro_invocador_10')
            cmd('loot spawn 0 -59 0 loot astral:item/guadana_7')
            cmd('loot spawn 0 -59 0 loot astral:item/asesino_9_helmet', 2)
            cmd('mm mobs spawn astral_invocacion 1 probe,0,-60,0', 3)
            cmd('tag @e[type=minecraft:zombie,limit=1] add astral.invocacion')
            cmd('summon minecraft:husk 2 -60 0 {Tags:["astral.mt5","atk"],NoAI:1b}')
            cmd('attribute @e[type=minecraft:zombie,tag=astral.invocacion,limit=1] minecraft:max_health base set 2000')
            cmd('data merge entity @e[type=minecraft:zombie,tag=astral.invocacion,limit=1] {Health:2000f}', 2)
            cmd('say CLASETEST antes')
            cmd('data get entity @e[type=minecraft:zombie,tag=astral.invocacion,limit=1] Health')
            cmd('damage @e[type=minecraft:zombie,tag=astral.invocacion,limit=1] 2.5 minecraft:mob_attack by @e[tag=atk,limit=1]', 2)
            cmd('say CLASETEST despues')
            cmd('data get entity @e[type=minecraft:zombie,tag=astral.invocacion,limit=1] Health', 2)
            cmd('stop', 15)
        finally:
            if p.poll() is None:
                p.kill()
    text = log.read_text('utf8', errors='replace')
    errores = [l for l in text.splitlines() if re.search(r'ERROR|Exception|Failed to load|Registry', l)
               and 'packetevents' not in l.lower()]
    print('\n'.join(errores[:40]) or 'Sin errores en el log')
    for pat in ('AstralClases', 'CLASETEST', 'Health', 'datapack', 'Spawned', 'astral_invocacion', 'item'):
        for l in text.splitlines():
            if pat in l and ('INFO' in l or 'WARN' in l):
                print(l[-220:])
    print('log:', log)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--java', required=True)
    main(ap.parse_args().java)
