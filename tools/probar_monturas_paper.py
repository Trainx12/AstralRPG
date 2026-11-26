"""Paper local con MythicMobs/BetterModel: control nativo, hostiles y nado. Sin cliente visual."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import time
import zipfile

ROOT=Path(__file__).resolve().parents[1]


def run(java,base,runtime):
    import sys
    sys.path.insert(0,str(ROOT/'datapack-src'))
    from terceros import privado
    work=ROOT/'.local/mount-probe';server=work/'paper';server.mkdir(parents=True,exist_ok=True)
    for name in ('libraries','versions','cache'):
        if not (server/name).exists():shutil.copytree(base/name,server/name)
    shutil.copy2(base/'paper.jar',server/'paper.jar')
    (server/'eula.txt').write_text('eula=true\n')
    (server/'server.properties').write_text('server-ip=127.0.0.1\nserver-port=25597\nonline-mode=false\nlevel-name=probe\nlevel-type=minecraft:flat\ngenerator-settings={"layers":[{"block":"minecraft:bedrock","height":1}],"biome":"minecraft:plains"}\ngenerate-structures=false\nspawn-protection=0\nmanagement-server-enabled=false\n')
    import yaml
    config_path=server/'spigot.yml'
    config=yaml.safe_load(config_path.read_text('utf8')) if config_path.exists() else {}
    attributes=config.setdefault('settings',{}).setdefault('attribute',{})
    for attr in ('maxHealth','attackDamage'):attributes.setdefault(attr,{})['max']=1.0E12
    config_path.write_text(yaml.safe_dump(config),'utf8')
    plugins=server/'plugins';plugins.mkdir(exist_ok=True)
    for name in ('bettermodel','mythicmobs','nightcore','excellentenchants','packetevents'):
        shutil.copy2(base/'plugins'/f'{name}.jar',plugins/f'{name}.jar')
    shutil.copy2(ROOT/'.local/balance-probe/paper/plugins/skript.jar',plugins/'skript.jar')
    shutil.copy2(runtime,plugins/'AstralDecor.jar')
    scripts=plugins/'Skript/scripts';scripts.mkdir(parents=True,exist_ok=True)
    shutil.copy2(ROOT/'build/gameplay/astral_gameplay.sk',scripts/'astral_gameplay.sk')
    for sub in ('mobs','skills'):
        dest=plugins/'MythicMobs'/sub;dest.mkdir(parents=True,exist_ok=True)
        for p in (ROOT/'build/mythicmobs'/sub).glob('*.yml'):shutil.copy2(p,dest/p.name)
    models=plugins/'BetterModel/models';models.mkdir(parents=True,exist_ok=True)
    for source in (ROOT/'build/models',privado()/'build/models',privado()/'build/entregas/correcciones-goblin-golems/models'):
        for p in source.glob('*.bbmodel'):shutil.copy2(p,models/p.name)
    shutil.copy2(ROOT/'datapack-src/mobs/bettermodel_config.yml',plugins/'BetterModel/config.yml')
    packs=server/'probe/datapacks';packs.mkdir(parents=True,exist_ok=True)
    shutil.copy2(ROOT/'build/AstralRPG-Items.zip',packs/'AstralRPG-Items.zip')
    deps=[*server.joinpath('libraries').rglob('*.jar'),*server.joinpath('versions').rglob('*.jar'),plugins/'mythicmobs.jar',plugins/'bettermodel.jar']
    subprocess.run([str(java),'-m','jdk.compiler/com.sun.tools.javac.Main','-encoding','UTF-8','-classpath',os.pathsep.join(map(str,deps)),
                    '-d',str(work),str(ROOT/'datapack-src/test_runtime/MountProbe.java')],check=True)
    with zipfile.ZipFile(plugins/'MountProbe.jar','w') as z:
        for p in work.joinpath('astraltest').glob('MountProbe*.class'):z.write(p,'astraltest/'+p.name)
        z.writestr('plugin.yml',"name: MountProbe\nversion: 1\nmain: astraltest.MountProbe\napi-version: '26.1.2'\ndepend: [AstralDecor,MythicMobs,BetterModel]\ncommands:\n  mountprobe: {}\n")
    log=work/'paper.log'
    with log.open('w',encoding='utf8') as out:
        p=subprocess.Popen([str(java),'-Xms512M','-Xmx2G','-jar','paper.jar','--nogui'],cwd=server,
                           stdin=subprocess.PIPE,stdout=out,stderr=subprocess.STDOUT,text=True)
        def cmd(c):p.stdin.write(c+'\n');p.stdin.flush()
        try:
            for _ in range(180):
                if 'For help, type' in log.read_text('utf8',errors='replace'):break
                if p.poll() is not None:raise RuntimeError('Paper termino: '+str(log))
                time.sleep(1)
            else:raise TimeoutError('Paper no arranco')
            for step in ('mounts','clicks','legacy','flying','eggs','lobby','saddle','hostiles','swim','ice','statues','modes','follow','followall','persist','result'):
                cmd('mountprobe '+step)
                marker='MOUNT RESULT failures=' if step=='result' else f'MOUNT STEP {step} DONE'
                for _ in range(120):
                    if marker in log.read_text('utf8',errors='replace'):break
                    if p.poll() is not None:raise RuntimeError('Paper termino: '+str(log))
                    time.sleep(.5)
                else:raise TimeoutError('No termino la fase '+step)
        finally:
            if p.poll() is None:cmd('stop');p.wait(timeout=60)
    content=log.read_text('utf8',errors='replace')
    print('\n'.join(l for l in content.splitlines() if 'MOUNT ' in l or 'ERROR' in l or 'Encountered ' in l))
    if 'MOUNT RESULT failures=0' not in content or any(s in content for s in ('MOUNT FAIL','Error loading','Failed to load','Encountered ','Configuration Error','Could not find MetaSkill')):
        raise AssertionError('Revisar '+str(log))
    print('Log privado:',log)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--java',required=True,type=Path);p.add_argument('--base',required=True,type=Path)
    p.add_argument('--runtime',type=Path,default=ROOT/'build/monturas/AstralDecor.jar')
    a=p.parse_args();run(a.java.resolve(),a.base.resolve(),a.runtime.resolve())
