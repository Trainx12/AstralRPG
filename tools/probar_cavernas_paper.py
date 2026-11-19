"""Ensayo aislado de las Cavernas de Cristal (7e) en Paper 26.1.2. Solo 127.0.0.1; no toca el server remoto.

Crea el mundo con AstralCavernas (sin Multiverse), mide chunks/segundo y densidad de menas (/cavernas medir),
dibuja planta y cortes (/cavernas mapa -> build/previews/cavernas_*.png), prueba la tabla de las vetas con un
soporte que tiene un taladro de Rubi y uno de Diamante, y hace aparecer un golem y un guardian de MythicMobs.
Uso: python tools/probar_cavernas_paper.py --java <bin/java.exe>
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / '.local/testsrv'
W = 'cavernas_cristal'


def main(java):
    work = ROOT / '.local/cavernas-probe'
    srv = work / 'paper'
    for viejo in [srv / W, *srv.glob(f'probe/**/{W}')]:   # Paper 26.1 guarda las dimensiones dentro del nivel
        if viejo.is_dir():
            shutil.rmtree(viejo)
    srv.mkdir(parents=True, exist_ok=True)
    for n in ('libraries', 'versions', 'cache'):
        if not (srv / n).exists():
            shutil.copytree(BASE / n, srv / n, copy_function=os.link)
    shutil.copy2(BASE / 'paper.jar', srv / 'paper.jar')
    (srv / 'eula.txt').write_text('eula=true\n')
    (srv / 'server.properties').write_text(
        'server-ip=127.0.0.1\nserver-port=25633\nonline-mode=false\nlevel-name=probe\nlevel-type=minecraft:flat\n'
        'generate-structures=false\nspawn-protection=0\nmanagement-server-enabled=false\nview-distance=4\nsimulation-distance=4\n')
    plugins = srv / 'plugins'
    plugins.mkdir(exist_ok=True)
    for name in ('nightcore.jar', 'excellentenchants.jar', 'packetevents.jar', 'mythicmobs.jar', 'bettermodel.jar'):
        shutil.copy2(BASE / 'plugins' / name, plugins / name)
    old = plugins / 'AstralCavernas'
    if old.exists():
        shutil.rmtree(old)
    shutil.copy2(ROOT / 'build/cavernas/AstralCavernas.jar', plugins / 'AstralCavernas.jar')
    mm = plugins / 'MythicMobs/mobs'
    mm.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / 'build/mythicmobs/mobs/cavernas.yml', mm / 'cavernas.yml')
    packs = srv / 'probe/datapacks'
    packs.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / 'build/AstralRPG-Items.zip', packs / 'AstralRPG-Items.zip')
    log = work / 'paper.log'
    with log.open('w', encoding='utf8') as out:
        p = subprocess.Popen([str(java), '-Xms1G', '-Xmx3G', '-jar', 'paper.jar', '--nogui'], cwd=srv,
                             stdin=subprocess.PIPE, stdout=out, stderr=subprocess.STDOUT, text=True)

        def cmd(s, wait=1.0):
            p.stdin.write(s + '\n')
            p.stdin.flush()
            time.sleep(wait)

        def esperar(texto, seg=300):
            for _ in range(seg):
                if texto in log.read_text('utf8', errors='replace'):
                    return True
                time.sleep(1)
            return False
        try:
            if not esperar('For help, type'):
                raise RuntimeError('Paper no arranco: ' + str(log))
            time.sleep(8)
            cmd('cavernas crear')
            esperar('CREAR', 180)
            cmd('cavernas mapa', 2)
            esperar('MAPA listo', 120)
            t0 = time.time()
            cmd('cavernas medir 10', 1)
            esperar('MEDIR chunks=100', 600)
            print(f'GEN 100 chunks en {time.time() - t0:.1f} s', flush=True)
            # Tabla de las vetas: veta de Rubi (nota 0) con taladro de Rubi (tier 4) y de Diamante (tier 1).
            x, y, z = 4, 30, -300
            cmd(f'execute in minecraft:{W} run forceload add {x} {z}', 2)
            cmd(f'execute in minecraft:{W} run summon minecraft:armor_stand {x} {y + 2} {z} {{Tags:["ct"],NoGravity:1b,Invulnerable:1b}}', 2)
            for etiqueta, tier in (('RUBI', 4), ('DIAMANTE', 1)):
                cmd(f'execute in minecraft:{W} run setblock {x} {y} {z} minecraft:air')
                cmd(f'execute in minecraft:{W} run setblock {x} {y} {z} minecraft:note_block[instrument=bell,note=0]')
                cmd(f'execute in minecraft:{W} run minecraft:item replace entity @e[tag=ct,limit=1] weapon.mainhand with '
                    f'minecraft:diamond_pickaxe[minecraft:custom_data={{astral:{{tool:"drill",tier:{tier},id:"t"}}}}]')
                cmd(f'execute in minecraft:{W} run kill @e[type=item]')
                cmd(f'execute in minecraft:{W} as @e[tag=ct,limit=1] run loot spawn {x} {y + 1} {z} mine {x} {y} {z} mainhand', 2)
                cmd(f'say CT {etiqueta}')
                cmd(f'execute in minecraft:{W} run data get entity @e[type=item,limit=1,sort=nearest,x={x},y={y},z={z}] Item', 2)
            cmd(f'execute in minecraft:{W} run setblock {x} {y} {z} minecraft:note_block[instrument=bell,note=14]')
            cmd(f'execute in minecraft:{W} run minecraft:item replace entity @e[tag=ct,limit=1] weapon.mainhand with '
                'minecraft:diamond_pickaxe[minecraft:custom_data={astral:{tool:"drill",tier:5,id:"t"}}]')
            cmd('say CT CRISTAL')
            cmd(f'execute in minecraft:{W} run kill @e[type=item]')
            cmd(f'execute in minecraft:{W} as @e[tag=ct,limit=1] run loot spawn {x} {y + 1} {z} mine {x} {y} {z} mainhand', 2)
            cmd(f'execute in minecraft:{W} run data get entity @e[type=item,limit=1,sort=nearest,x={x},y={y},z={z}] Item', 2)
            cmd(f'mm mobs spawn astral_cav_golem_amatista 1 {W},0,13,-296', 3)
            cmd(f'mm mobs spawn astral_cav_jefe_corazon 1 {W},0,13,-294', 3)
            cmd('say CT MOBS')
            cmd(f'execute in minecraft:{W} as @e[tag=cav.mob] run say soy mob de cavernas', 2)
            cmd('cavernas', 1)
            cmd('stop', 20)
        finally:
            if p.poll() is None:
                p.kill()
    text = log.read_text('utf8', errors='replace')
    for n in ('planta.png', 'corte_x.png', 'corte_z.png'):
        f = plugins / 'AstralCavernas' / n
        if f.exists():
            dst = ROOT / 'build/previews' / f'cavernas_{n}'
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dst)
    clean = re.sub(r'\x1b\[[0-9;]*m', '', text)
    keep = [l for l in clean.splitlines() if any(k in l for k in ('CREAR', 'MEDIR', 'MAPA', 'CT ', 'has the following', 'Cavernas', 'soy mob',
                                                                   'Exception', 'ERROR', 'Failed', 'Could not'))]
    sys.stdout.reconfigure(errors='replace')
    print('\n'.join(keep[-80:]))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--java', required=True)
    main(Path(ap.parse_args().java))
