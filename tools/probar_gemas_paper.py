"""Ensayo aislado de la Reforja de gemas (7d) en Paper 26.1.2. Solo 127.0.0.1; no toca el server remoto.

Carga el datapack (build/AstralRPG-Items.zip) y los Skript (servicios, economia, puntaje y gemas) y prueba con un
soporte de armadura sin jugador: engarzar, no repetir tipo, tope de ranuras por tier, quitar y la gema extraida.
Uso: python tools/probar_gemas_paper.py --java <bin/java.exe>
"""
import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / '.local/testsrv'
SEL = '@e[type=minecraft:armor_stand,tag=gtest,limit=1]'


def main(java):
    work = ROOT / '.local/gemas-probe'
    srv = work / 'paper'
    srv.mkdir(parents=True, exist_ok=True)
    for n in ('libraries', 'versions', 'cache'):
        if not (srv / n).exists():
            shutil.copytree(BASE / n, srv / n, copy_function=os.link)
    shutil.copy2(BASE / 'paper.jar', srv / 'paper.jar')
    (srv / 'eula.txt').write_text('eula=true\n')
    (srv / 'server.properties').write_text(
        'server-ip=127.0.0.1\nserver-port=25632\nonline-mode=false\nlevel-name=probe\nlevel-type=minecraft:flat\n'
        'generate-structures=false\nspawn-protection=0\nmanagement-server-enabled=false\nview-distance=2\nsimulation-distance=2\n')
    plugins = srv / 'plugins'
    plugins.mkdir(exist_ok=True)
    for name in ('skript.jar', 'EssentialsX.jar', 'Vault.jar', 'nightcore.jar', 'excellentenchants.jar', 'packetevents.jar',
                 'auraskills.jar', 'mythicmobs.jar'):
        shutil.copy2(BASE / 'plugins' / name, plugins / name)
    shutil.copy2(ROOT / 'build/gemas/AstralGemas.jar', plugins / 'AstralGemas.jar')
    scripts = plugins / 'Skript/scripts'
    scripts.mkdir(parents=True, exist_ok=True)
    for old in scripts.glob('*.sk'):
        old.unlink()
    for src in (ROOT / 'build/economia/Skript/scripts/astral_economia.sk', ROOT / 'build/mazmorras/astral_puntaje.sk',
                ROOT / 'build/services/astral_servicios.sk', ROOT / 'build/gemas/astral_gemas.sk'):
        shutil.copy2(src, scripts / src.name)
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

        def item(cd, base='minecraft:diamond_sword'):
            cmd(f'minecraft:item replace entity {SEL} weapon.mainhand with {base}[minecraft:custom_data={cd}]')

        def run(fn):
            cmd(f'execute as {SEL} run function astral:{fn}')

        def mostrar(etiqueta):
            cmd(f'say GEMTEST {etiqueta}')
            cmd(f'data get entity {SEL} equipment.mainhand.components."minecraft:enchantments"')
            cmd(f'data get entity {SEL} Tags')
        try:
            for _ in range(300):
                if 'For help, type' in log.read_text('utf8', errors='replace'):
                    break
                if p.poll() is not None:
                    raise RuntimeError('Paper termino: ' + str(log))
                time.sleep(1)
            time.sleep(10)
            cmd('forceload add 0 0')
            cmd('summon minecraft:armor_stand 0 -60 0 {Tags:["gtest"],NoGravity:1b,Invulnerable:1b}', 2)
            # Arma tier 2: 1 ranura
            item('{astral:{type:"weapon",tier:2,id:"prueba"}}')
            run('gemas/poner/rubi/3')
            mostrar('T2 rubi3')
            run('gemas/poner/jade/1')
            mostrar('T2 lleno jade (no debe entrar)')
            run('gemas/poner/rubi/5')
            mostrar('T2 rubi repetido (no debe entrar)')
            run('gemas/quitar/rubi')
            mostrar('T2 quitar rubi')
            # Armadura tier 9: 3 ranuras
            item('{astral:{type:"armor",tier:9,id:"prueba",def:100}}', 'minecraft:diamond_chestplate')
            for g in ('opalo/2', 'onix/5', 'topacio/4', 'zafiro/1'):
                run(f'gemas/poner/{g}')
            mostrar('T9 armadura 3 gemas (zafiro no entra)')
            run('gemas/gui/ver')
            mostrar('T9 ver')
            # Gema en la mano
            cmd(f'loot replace entity {SEL} weapon.mainhand loot astral:item/gema_amatista_4')
            run('gemas/gui/gema')
            mostrar('gema amatista 4')
            run('gemas/dar/rubi/2')
            cmd(f'data get entity {SEL} equipment.mainhand')
            # Talisman: no admite gemas
            item('{astral:{type:"talisman",tier:3,id:"prueba"}}', 'minecraft:paper')
            run('gemas/poner/rubi/1')
            mostrar('talisman (no debe entrar)')
            cmd('astralgema dar Nadie rubi 3')
            cmd('astralgema cofre Nadie 3 6')
            cmd('stop', 15)
        finally:
            if p.poll() is None:
                p.kill()
    text = log.read_text('utf8', errors='replace')
    keep = [l for l in text.splitlines() if 'GEMTEST' in l or 'has the following' in l or 'Reforja' in l or 'AstralGemas' in l or 'gema' in l.lower()
            or 'error' in l.lower() or 'Line ' in l or 'scripts' in l and 'loaded' in l or 'Failed' in l]
    sys.stdout.reconfigure(errors='replace')
    print('\n'.join(keep[-120:]))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--java', required=True)
    main(Path(ap.parse_args().java))
