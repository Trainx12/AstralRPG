"""Verifica en Paper el tier exacto del inventario y el dano de jefes, solo local."""
import argparse
from pathlib import Path
import shutil
import re
import subprocess
import time
import zipfile
import yaml

ROOT=Path(__file__).resolve().parents[1]


def verify(content):
    for kind,tier in (('weapon',1),('armor',5),('staff',10)):
        assert f'[Iron Golem] BOSS TIER PASS {kind} {tier}' in content
        assert f'[Server] BOSS HEALTH PASS {tier}' in content
    assert '[Server] BOSS ANCESTRAL PASS' in content
    assert '] BOSS NO HEAL PASS' in content
    assert float(re.search(r'BOSS DAMAGE ([\d.]+)',content)[1])==375
    assert 'Failed to load function astral:mob/jefe_mundo' not in content
    print('PASS: arma T1, armadura guardada T5, baston T10; vida por tier; dano con multiples tags; cangrejo ancestral y sin curacion posterior')


def run(java, source, work, port):
    server=work/'paper'
    server.mkdir(parents=True,exist_ok=True)
    for name in ('libraries','versions','cache'):
        if not (server/name).exists(): shutil.copytree(source/name,server/name)
    shutil.copy2(source/'paper.jar',server/'paper.jar')
    plugins=server/'plugins'
    plugins.mkdir(exist_ok=True)
    shutil.copy2(source/'plugins/skript.jar',plugins/'skript.jar')
    shutil.copy2(ROOT/'.local/asw-native/server/plugins/mythicmobs.jar',plugins/'mythicmobs.jar')
    for name,path in [('auraskills.jar',ROOT/'.local/asw-native/server/plugins/auraskills.jar'),
                      ('GriefPrevention.jar',ROOT/'.local/tanda5a/GriefPrevention.jar'),
                      ('AstralProgression.jar',ROOT/'build/runtime/AstralProgression.jar')]:
        shutil.copy2(path,plugins/name)
    mobs=plugins/'MythicMobs/mobs'
    mobs.mkdir(parents=True,exist_ok=True)
    crab=yaml.safe_load((ROOT/'build/mythicmobs/mobs/astral.yml').read_text(encoding='utf8'))['astral_cangrejo_ancestral']
    # Usar vida y comandos reales; el modelo visual requiere BetterModel y no participa del balance.
    crab['Skills']=[s for s in crab['Skills'] if 'command{' in s and '~onSpawn' in s]
    crab['Skills'].insert(0,'addtag{tag=astral.seen} @self ~onSpawn')
    (mobs/'crab.yml').write_text(yaml.safe_dump({'astral_cangrejo_ancestral':crab},allow_unicode=True),encoding='utf8')
    scripts=plugins/'Skript/scripts'
    scripts.mkdir(parents=True,exist_ok=True)
    text=(ROOT/'build/balance-mobs/astral_gameplay.sk').read_text(encoding='utf8')
    func='function astral_dano_tier('+text.split('function astral_dano_tier(',1)[1].split('function astral_dano_mundo(',1)[0]
    import sys
    sys.path.insert(0,str(ROOT/'datapack-src'))
    from escala import DANO_JEFE_MUNDO, VIDA_REF
    func+='''
command /bossdamageprobe:
    trigger:
        spawn a zombie at spawn location of world "world"
        set {_e} to last spawned zombie
        add "astral.seen" to scoreboard tags of {_e}
        add "ad.boss.scaled" to scoreboard tags of {_e}
        add "astral.jm5" to scoreboard tags of {_e}
        set {_d} to astral_dano_tier({_e})
        send "BOSS DAMAGE %{_d}%" to console
        kill {_e}
'''
    (scripts/'bossprobe.sk').write_text(func,encoding='utf8')
    packs=server/'world/datapacks'
    packs.mkdir(parents=True,exist_ok=True)
    shutil.copy2(ROOT/'.local/balance-mobs-generated.zip',packs/'AstralRPG-Items.zip')
    shutil.copy2(ROOT/'build/balance-mobs/zz-AstralRPG-BalanceMobs.zip',packs/'zz-AstralRPG-BalanceMobs.zip')
    (server/'eula.txt').write_text('eula=true\n')
    (server/'server.properties').write_text('online-mode=false\nserver-ip=127.0.0.1\nserver-port='+str(port)+'\nlevel-name=world\nlevel-type=minecraft:flat\ngenerator-settings={"layers":[{"block":"minecraft:bedrock","height":1}],"biome":"minecraft:plains"}\nview-distance=2\nsimulation-distance=2\nmanagement-server-enabled=false\n')
    (server/'spigot.yml').write_text('settings:\n  attribute:\n    maxHealth:\n      max: 1000000000000\n    attackDamage:\n      max: 1000000000000\n')
    bot=work/'bot.cjs'
    bot.write_text("const mc=require("+repr(str(ROOT/'.local/asw-test/node_modules/minecraft-protocol').replace('\\','/'))+"); const c=mc.createClient({host:'127.0.0.1',port:"+str(port)+",username:'BossProbe',auth:'offline',version:'26.1.2'}); c.on('error',console.error);",encoding='utf8')
    log=work/'paper.log'
    def read(): return log.read_text(encoding='utf8',errors='replace')
    def wait_for(marker, attempts=180):
        for _ in range(attempts):
            if marker in read(): return
            if proc.poll() is not None: raise RuntimeError(read()[-3000:])
            time.sleep(1)
        raise TimeoutError(marker)
    with log.open('w',encoding='utf8') as out:
        proc=subprocess.Popen([str(java),'-Xms512M','-Xmx2G','-jar','paper.jar','--nogui'],cwd=server,stdin=subprocess.PIPE,stdout=out,stderr=subprocess.STDOUT,text=True)
        client=None
        def command(c): proc.stdin.write(c+'\n');proc.stdin.flush()
        try:
            wait_for('For help, type')
            command('datapack enable "file/zz-AstralRPG-BalanceMobs.zip" last')
            client=subprocess.Popen(['node',str(bot)],stdout=out,stderr=subprocess.STDOUT)
            wait_for('BossProbe joined the game')
            command('gamemode creative BossProbe')
            command('kill @e[type=minecraft:zoglin]')
            command('kill @e[tag=bossprobe]')
            command('tp BossProbe 0 10 0')
            time.sleep(5)
            for kind,tier in (('weapon',1),('armor',5),('staff',10)):
                command('clear BossProbe')
                command(f'item replace entity BossProbe container.0 with minecraft:diamond_sword[minecraft:custom_data={{astral:{{type:"{kind}",tier:{tier}}}}}]')
                if kind=='armor':
                    command('item replace entity BossProbe container.1 with minecraft:diamond_sword[minecraft:custom_data={astral:{type:"weapon",tier:1}}]')
                    command('item replace entity BossProbe container.2 with minecraft:diamond_pickaxe[minecraft:custom_data={astral:{type:"tool",tier:10}}]')
                command('execute at BossProbe run summon minecraft:iron_golem ~3 ~ ~ {Tags:["bossprobe","astral.seen"],NoAI:1b}')
                command('execute as @e[tag=bossprobe,limit=1] at @s run function astral:mob/jefe_mundo')
                command(f'execute as @e[tag=bossprobe,limit=1] if score @s astral.mt matches {tier} run say BOSS TIER PASS {kind} {tier}')
                command('execute store result score #bosscheck astral.tmp run attribute @e[tag=bossprobe,limit=1] minecraft:max_health base get 0.0001')
                command(f'execute if score #bosscheck astral.tmp matches {int(25*VIDA_REF[tier]*0.0001)} run say BOSS HEALTH PASS {tier}')
                command('kill @e[tag=bossprobe]')
            command('bossdamageprobe')
            wait_for('BOSS DAMAGE')
            command('mm mobs spawn astral_cangrejo_ancestral 1 world,3,10,0')
            time.sleep(2)
            command('execute as @e[type=minecraft:zoglin,tag=astral.jm10,limit=1] store result score #crabcheck astral.tmp run attribute @s minecraft:max_health get 0.0001')
            command('data get entity @e[type=minecraft:zoglin,tag=astral.jm10,limit=1] attributes')
            command(f'execute if score #crabcheck astral.tmp matches {int(125*VIDA_REF[10]*0.0001)} run say BOSS ANCESTRAL PASS')
            wait_for('[Server] BOSS ANCESTRAL PASS',30)
            command('data modify entity @e[type=minecraft:zoglin,tag=astral.jm10,limit=1] Health set value 100.0f')
            time.sleep(2)
            command('execute as @e[type=minecraft:zoglin,tag=astral.jm10,limit=1] if data entity @s {Health:100.0f} run say BOSS NO HEAL PASS')
            wait_for('] BOSS NO HEAL PASS',30)
            content=read()
            verify(content)
        finally:
            if client: client.terminate()
            if proc.poll() is None: command('stop');proc.wait(timeout=60)


if __name__=='__main__':
    import sys
    if '--verify-log' in sys.argv:
        verify(Path(sys.argv[sys.argv.index('--verify-log')+1]).read_text(encoding='utf8',errors='replace'))
        sys.exit(0)
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--java',type=Path,required=True)
    p.add_argument('--source',type=Path,required=True)
    p.add_argument('--work',type=Path,default=ROOT/'.local/balance-mobs-paper')
    p.add_argument('--port',type=int,default=25640)
    a=p.parse_args();run(a.java.resolve(),a.source.resolve(),a.work.resolve(),a.port)
