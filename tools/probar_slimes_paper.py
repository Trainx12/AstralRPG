"""Reproduce divisiones reales en Paper local, sin acceder al servidor remoto."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import time
import zipfile
import re

ROOT=Path(__file__).resolve().parents[1]


def run(java, source, jar, work, baseline=False, reset_bases=False):
    server=work/'paper';server.mkdir(parents=True,exist_ok=True)
    for name in ('libraries','versions','cache'):
        if not (server/name).exists():shutil.copytree(source/name,server/name)
    shutil.copy2(source/'paper.jar',server/'paper.jar')
    plugins=server/'plugins';plugins.mkdir(exist_ok=True)
    for name,path in [('auraskills.jar',ROOT/'.local/asw-native/server/plugins/auraskills.jar'),
                      ('mythicmobs.jar',ROOT/'.local/asw-native/server/plugins/mythicmobs.jar'),
                      ('GriefPrevention.jar',ROOT/'.local/tanda5a/GriefPrevention.jar'),
                      ('AstralProgression.jar',jar)]:
        shutil.copy2(path,plugins/name)
    shutil.copy2(source/'plugins/skript.jar',plugins/'skript.jar')
    for name in ('Vault.jar','EssentialsX.jar'):
        shutil.copy2(source/'plugins'/name,plugins/name)
    scripts=plugins/'Skript/scripts';scripts.mkdir(parents=True,exist_ok=True)
    economy=(ROOT/'build/economia/Skript/scripts/astral_economia.sk').read_text(encoding='utf8')
    normal=int(re.search(r'set \{-eco.vanilla::3\} to (\d+)',economy)[1])
    money='''
command /slimemoneyprobe:
    trigger:
        set {_w} to world "world"
        spawn a slime at spawn location of {_w}
        set {_e} to last spawned slime
        add "astral.mt3" to scoreboard tags of {_e}
        set max health of {_e} to 1000000
        set {_before} to astral_eco_vanilla({_e})
        add "astral.split" to scoreboard tags of {_e}
        set {_after} to astral_eco_vanilla({_e})
        if {_before} is __BEFORE__:
            if {_after} is __AFTER__:
                send "SLIME MONEY PASS normal tier cap, elite health" to console
            else:
                send "SLIME MONEY FAIL child=%{_after}%" to console
        else:
            send "SLIME MONEY FAIL parent=%{_before}%" to console
        delete {_e}
'''.replace('__BEFORE__',str(normal*10)).replace('__AFTER__',str(normal))
    (scripts/'astral_economia.sk').write_text(economy,encoding='utf8')
    (scripts/'split_money.sk').write_text(money,encoding='utf8')
    (server/'eula.txt').write_text('eula=true\n')
    port=25630 if baseline else 25629
    (server/'server.properties').write_text('online-mode=false\nserver-ip=127.0.0.1\nserver-port='+str(port)+'\nlevel-name=world\nlevel-type=minecraft:flat\ngenerator-settings={"layers":[{"block":"minecraft:bedrock","height":1}],"biome":"minecraft:plains"}\nspawn-protection=0\nview-distance=2\nsimulation-distance=2\nmanagement-server-enabled=false\n')
    (server/'spigot.yml').write_text('settings:\n  attribute:\n    maxHealth:\n      max: 1000000000\n    attackDamage:\n      max: 10000000\n')
    classes=work/'classes';classes.mkdir(exist_ok=True)
    jars=list((server/'libraries').rglob('*.jar'))+list((server/'versions').rglob('*.jar'))
    args=['-encoding','UTF-8','-classpath',os.pathsep.join(map(str,jars)),'-d',str(classes),str(ROOT/'datapack-src/test_runtime/SlimeSplitProbe.java')]
    argfile=work/'compile.args';argfile.write_text('\n'.join('"'+s.replace('\\','/')+'"' for s in args))
    subprocess.run([str(java),'-m','jdk.compiler/com.sun.tools.javac.Main','@'+str(argfile)],check=True)
    with zipfile.ZipFile(plugins/'SlimeSplitProbe.jar','w') as z:
        for p in (classes/'astraltest').glob('SlimeSplitProbe*.class'):z.write(p,'astraltest/'+p.name)
        z.writestr('plugin.yml',"name: SlimeSplitProbe\nversion: 1\nmain: astraltest.SlimeSplitProbe\napi-version: '26.1.2'\ndepend: [AstralProgression]\ncommands:\n  slimeprobe: {}\n")
    log=work/'paper.log'
    with log.open('w',encoding='utf8') as out:
        proc=subprocess.Popen([str(java),'-Xms512M','-Xmx2G',f'-Dslimeprobe.reset={str(reset_bases).lower()}','-jar','paper.jar','--nogui'],cwd=server,stdin=subprocess.PIPE,stdout=out,stderr=subprocess.STDOUT,text=True)
        def command(c):proc.stdin.write(c+'\n');proc.stdin.flush()
        try:
            for _ in range(180):
                content=log.read_text(encoding='utf8',errors='replace')
                if 'For help, type' in content:break
                if proc.poll() is not None:raise RuntimeError('Paper termino; '+str(log))
                time.sleep(1)
            else:raise TimeoutError(str(log))
            time.sleep(4)  # Skript finishes its async script load after Paper's ready message.
            command('slimemoneyprobe')
            command('slimeprobe')
            for _ in range(90):
                content=log.read_text(encoding='utf8',errors='replace')
                if 'SLIME RESULT' in content:break
                time.sleep(1)
        finally:
            if proc.poll() is None:command('stop');proc.wait(timeout=60)
    content=log.read_text(encoding='utf8',errors='replace')
    print('\n'.join(l for l in content.splitlines() if 'SLIME ' in l or 'ERROR' in l))
    if baseline:
        if reset_bases:
            assert 'SLIME INJECT bases=20/1/0.2 max=500.0' in content, 'No se reprodujo 225 -> 500'
            assert 'SLIME FAIL tick +1' in content and 'SLIME FAIL tick +20' in content, 'Baseline no detecta regresion diferida'
        else:
            assert 'SLIME FAIL max inherited' in content and 'SLIME FAIL tick +20' in content, 'No se reprodujo regresion nativa'
    else:
        assert 'SLIME RESULT' in content and 'failures=0' in content and 'SLIME FAIL' not in content
        assert 'ERROR' not in content, str(log)
        assert 'SLIME MONEY PASS' in content and 'SLIME MONEY FAIL' not in content
        if reset_bases:
            assert 'SLIME INJECT bases=20/1/0.2 max=500.0' in content


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--java',type=Path,required=True);p.add_argument('--source',type=Path,required=True)
    p.add_argument('--jar',type=Path,default=ROOT/'build/runtime/AstralProgression.jar')
    p.add_argument('--work',type=Path,default=ROOT/'.local/slimes-paper');p.add_argument('--baseline',action='store_true')
    p.add_argument('--reset-bases',action='store_true',help='Simular bases 20/1/0.2 despues de SPLIT, como en el servidor real')
    a=p.parse_args();run(a.java.resolve(),a.source.resolve(),a.jar.resolve(),a.work.resolve(),a.baseline,a.reset_bases)
