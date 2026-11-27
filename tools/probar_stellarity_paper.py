"""Ensayo aislado Paper 26.1.2 con Stellarity 5.4.2 original y dos clientes de protocolo. No toca el servidor remoto."""
import argparse, os, re, shutil, subprocess, time, zipfile, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BOT='''const mc=require(process.argv[2]+'/minecraft-protocol');
const c=mc.createClient({host:'127.0.0.1',port:25638,username:process.argv[3],auth:'offline',version:'26.1.2'});
c.on('error',e=>console.log(e.message));c.on('position',p=>c.write('teleport_confirm',{teleportId:p.teleportId}));'''

def run(a):
    original_sha=hashlib.sha256(a.stellarity.read_bytes()).hexdigest()
    work=ROOT/'.local'/('stellarity-probe-'+str(time.time_ns()));server=work/'paper';server.mkdir(parents=True)
    for name in ('libraries','versions','cache'): shutil.copytree(a.base/name,server/name)
    shutil.copy2(a.base/'paper.jar',server/'paper.jar')
    (server/'eula.txt').write_text('eula=true\n')
    (server/'server.properties').write_text('server-ip=127.0.0.1\nserver-port=25638\nonline-mode=false\nlevel-name=probe\nlevel-type=minecraft:flat\ngenerate-structures=false\nspawn-protection=0\nmanagement-server-enabled=false\nspawn-monsters=false\nview-distance=2\nsimulation-distance=2\n')
    plugins=server/'plugins';plugins.mkdir()
    for name in ('auraskills.jar','packetevents.jar','skript.jar','nightcore.jar','excellentenchants.jar'): shutil.copy2(a.base/'plugins'/name,plugins/name)
    shutil.copy2(ROOT/'build/stellarity/AstralStellarity.jar',plugins/'AstralStellarity.jar')
    shutil.copy2(ROOT/'build/mesa/AstralMesa.jar',plugins/'AstralMesa.jar')
    scripts=plugins/'Skript/scripts';scripts.mkdir(parents=True)
    shutil.copy2(ROOT/'build/gameplay/astral_gameplay.sk',scripts/'astral_gameplay.sk')
    dp=server/'probe/datapacks';dp.mkdir(parents=True)
    shutil.copy2(a.stellarity,dp/'Stellarity-5.4.2.zip')
    published=subprocess.check_output(['git','show','HEAD:build/AstralRPG-Items.zip'],cwd=ROOT)
    (dp/'AstralRPG-Items.zip').write_bytes(published)
    shutil.copy2(ROOT/'build/stellarity/AstralStellarity-Compat.zip',dp/'z-AstralStellarity-Compat.zip')
    # Topes de atributos como en el servidor; solo configuracion del ensayo.
    (server/'spigot.yml').write_text('settings:\n  attribute:\n    maxHealth:\n      max: 1000000000.0\n    attackDamage:\n      max: 1000000000.0\n')
    deps=[*server.joinpath('libraries').rglob('*.jar'),*server.joinpath('versions').rglob('*.jar'),*plugins.glob('*.jar')]
    src=ROOT/'datapack-src/test_runtime/StellarityProbe.java'
    subprocess.run([str(a.java),'-m','jdk.compiler/com.sun.tools.javac.Main','-encoding','UTF-8','-nowarn','-classpath',os.pathsep.join(map(str,deps)),'-d',str(work),str(src)],check=True)
    with zipfile.ZipFile(plugins/'StellarityProbe.jar','w') as z:
        z.write(work/'astraltest/StellarityProbe.class','astraltest/StellarityProbe.class')
        z.writestr('plugin.yml',"name: StellarityProbe\nversion: 1\nmain: astraltest.StellarityProbe\napi-version: '26.1.2'\ndepend: [AstralStellarity, AstralMesa, AuraSkills]\ncommands:\n  stellarprobe: {}\n")
    bot=work/'bot.cjs';bot.write_text(BOT)
    log=work/'paper.log';bots=[];handles=[]
    with log.open('w',encoding='utf8') as out:
        p=subprocess.Popen([str(a.java),'-Xms512M','-Xmx2G','-jar','paper.jar','--nogui'],cwd=server,stdin=subprocess.PIPE,stdout=out,stderr=subprocess.STDOUT,text=True,encoding='utf8')
        def content():return re.sub(r'\x1b\[[0-9;]*m','',log.read_text(encoding='utf8',errors='replace'))
        def cmd(c,delay=.6):p.stdin.write(c+'\n');p.stdin.flush();time.sleep(delay)
        def wait_for(text,timeout=180):
            end=time.time()+timeout
            while time.time()<end:
                if text in content():return
                if p.poll() is not None:raise RuntimeError('Paper termino: '+str(log))
                time.sleep(1)
            raise TimeoutError(text+'; '+str(log))
        def phase(name):
            cmd('stellarprobe '+name,1)
            if 'STELLAR PHASE '+name+' OK' not in content():raise AssertionError(name+'; '+str(log))
        try:
            wait_for('For help, type')
            if 'Error occurred while enabling' in content():raise AssertionError('Carga: '+str(log))
            cmd('datapack enable "file/z-AstralStellarity-Compat.zip" last',3)
            for name in ('ByTrainx','StellarOther'):
                h=(work/(name+'.log')).open('w');handles.append(h)
                bots.append(subprocess.Popen([str(a.node),str(bot),str(a.node_modules),name],stdout=h,stderr=subprocess.STDOUT))
            wait_for('StellarOther joined the game',60);wait_for('ByTrainx joined the game',60)
            cmd('tp ByTrainx 0 -59 0');cmd('tp StellarOther 30 -59 0')
            phase('initial')
            cmd('auraskills:skills skill setlevel ByTrainx fighting 50',2)
            phase('high')
            cmd('execute as ByTrainx run function astral:player/lvl')
            cmd('execute as ByTrainx run function astral:player/def')
            phase('functions')
            phase('native_prepare')
            cmd('execute as @e[tag=prismprobe,limit=1] at @s run function stellarity:item/prismember/spin/damage',1)
            phase('native_check')
            phase('arena_prepare')
            phase('arena_check')
            cmd('auraskills:skills skill setlevel ByTrainx fighting 1',2)
            phase('low')
            cmd('stellarity publico si');phase('public');cmd('stellarity publico no');phase('closed')
            assert hashlib.sha256(a.stellarity.read_bytes()).hexdigest()==original_sha
            print('\n'.join(l for l in content().splitlines() if 'STELLAR ' in l));print('LOG LOCAL',log)
        finally:
            for b in bots:
                if b.poll() is None:b.terminate()
            if p.poll() is None:cmd('stop',0);p.wait(timeout=60)
            for h in handles:h.close()

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ('java','base','node','node-modules','stellarity'):p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args()
    for k,v in vars(a).items():setattr(a,k,v.resolve())
    run(a)
