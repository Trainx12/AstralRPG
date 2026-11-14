"""Ensayo local de los tiers 6-10: datapack y Skript cargan, un mob T10 (y elite) con su vida y cartel, items T10.

python tools/probar_tiers6_10_paper.py --java <java25> --base .local/testsrv
No toca el server. Logs en .local/tiers6-10-probe/paper.log.
"""
import argparse
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]

COMANDOS = [
    'datapack list enabled',
    'forceload add 0 0',
    'scoreboard players set #mt astral.tmp 10',
    'summon minecraft:zombie 0.5 -60 0.5 {Tags:["astral.seen","probe.a"],NoAI:1b,PersistenceRequired:1b}',
    'execute as @e[tag=probe.a] run function astral:mob/t10',
    'execute as @e[tag=probe.a] run data modify entity @s Health set value 1.0E30f',
    'execute as @e[tag=probe.a] run function astral:mob/nombre',
    'execute as @e[tag=probe.a] run attribute @s minecraft:max_health get',
    'data get entity @e[tag=probe.a,limit=1] CustomName',
    'execute as @e[tag=probe.a] run function astral:fx/victim_pct',
    'scoreboard players get #pct astral.tmp',
    # Elite Astral sobre T10: pasa los 2.000 millones (cartel en miles).
    'summon minecraft:zombie 2.5 -60 0.5 {Tags:["astral.seen","probe.b"],NoAI:1b,PersistenceRequired:1b}',
    'execute as @e[tag=probe.b] run function astral:mob/t10',
    'execute as @e[tag=probe.b] run function astral:elite/t5',
    'execute as @e[tag=probe.b] run data modify entity @s Health set value 1.0E30f',
    'execute as @e[tag=probe.b] run function astral:mob/nombre',
    'execute as @e[tag=probe.b] run attribute @s minecraft:max_health get',
    'data get entity @e[tag=probe.b,limit=1] CustomName',
    'execute as @e[tag=probe.b] run function astral:fx/victim_pct',
    'scoreboard players get #pct astral.tmp',
    'loot spawn 0.5 -60 4.5 loot astral:item/espada_10',
    'loot spawn 0.5 -60 4.5 loot astral:item/berserker_10_helmet',
    'loot spawn 0.5 -60 4.5 loot astral:item/mago_6_chestplate',
    'loot spawn 0.5 -60 4.5 loot astral:item/corazon_fin',
    'execute as @e[type=item,distance=..10,x=0,y=-60,z=4] run say ITEM',
    'data get entity @e[type=item,limit=1,sort=nearest,x=0.5,y=-60,z=4.5] Item.components."minecraft:item_name"',
]


def run(java, base):
    sys.stdout.reconfigure(errors='replace')
    sys.path.insert(0, str(ROOT/'datapack-src'))
    work = ROOT/'.local/tiers6-10-probe'
    if work.exists():
        shutil.rmtree(work)
    srv = work/'srv'
    srv.mkdir(parents=True)
    for name in ('libraries', 'versions', 'cache'):
        shutil.copytree(base/name, srv/name)
    shutil.copy2(base/'paper.jar', srv/'paper.jar')
    (srv/'eula.txt').write_text('eula=true\n')
    # Topes de atributos para T10 (como hay que dejarlos en el server).
    (srv/'spigot.yml').write_text('settings:\n  attribute:\n    maxHealth:\n      max: 1.0E12\n    attackDamage:\n      max: 1.0E12\n')
    (srv/'server.properties').write_text('server-ip=127.0.0.1\nserver-port=25611\nonline-mode=false\nlevel-name=world\n'
        'level-type=minecraft:flat\ngenerate-structures=false\nmanagement-server-enabled=false\nspawn-protection=0\n')
    packs = srv/'world/datapacks'
    packs.mkdir(parents=True)
    shutil.copy2(ROOT/'build/AstralRPG-Items.zip', packs/'AstralRPG-Items.zip')
    plugins = srv/'plugins'
    plugins.mkdir()
    shutil.copy2(base/'plugins/skript.jar', plugins/'skript.jar')
    scripts = plugins/'Skript/scripts'
    scripts.mkdir(parents=True)
    import infinita
    (scripts/'astral_infinita.sk').write_text(infinita.script(), encoding='utf8')
    for name in ('astral_gameplay.sk', 'astral_armas_especiales.sk'):
        shutil.copy2(ROOT/'build/gameplay'/name, scripts/name)
    log = work/'paper.log'
    with log.open('w', encoding='utf8') as out:
        p = subprocess.Popen([str(java), '-Xmx2G', '-jar', 'paper.jar', '--nogui'], cwd=srv,
                             stdin=subprocess.PIPE, stdout=out, stderr=subprocess.STDOUT, text=True)
        try:
            for _ in range(240):
                if 'For help, type' in log.read_text(encoding='utf8', errors='replace'):
                    break
                time.sleep(1)
            time.sleep(8)
            for c in COMANDOS:
                p.stdin.write(c + '\n'); p.stdin.flush()
                time.sleep(0.6)
            time.sleep(3)
        finally:
            try:
                p.stdin.write('stop\n'); p.stdin.flush()
            except OSError:
                pass
            p.wait(timeout=120)
    text = log.read_text(encoding='utf8', errors='replace')
    keys = ('astral', 'Skript', 'error', 'Error', 'ERROR', 'WARN', 'has the following', 'max_health', 'CustomName',
            'pct', 'ITEM', 'Item', 'enabled data pack', 'Couldn', 'Failed')
    print('\n'.join(l for l in text.splitlines() if any(k in l for k in keys))[-12000:])


if __name__ == '__main__':
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument('--java', type=Path, required=True)
    a.add_argument('--base', type=Path, required=True)
    args = a.parse_args()
    run(args.java.resolve(), args.base.resolve())
