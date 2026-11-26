"""Ensayo aislado de esta entrega. Nunca se conecta al servidor remoto."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'datapack-src'))


def run(java,base):
    work=ROOT/'.local/dungeon-17-probe';srv=work/'paper';srv.mkdir(parents=True,exist_ok=True)
    for name in ('libraries','versions','cache'):
        if not (srv/name).exists():shutil.copytree(base/name,srv/name)
    shutil.copy2(base/'paper.jar',srv/'paper.jar')
    (srv/'eula.txt').write_text('eula=true\n')
    (srv/'server.properties').write_text('server-ip=127.0.0.1\nserver-port=25591\nonline-mode=false\nlevel-name=world\nlevel-type=minecraft:flat\ngenerator-settings={"layers":[{"block":"minecraft:bedrock","height":1}],"biome":"minecraft:plains"}\ngenerate-structures=false\nspawn-protection=0\nmanagement-server-enabled=false\nview-distance=2\nsimulation-distance=2\nmax-tick-time=-1\n')
    plugins=srv/'plugins';plugins.mkdir(exist_ok=True)
    for name in ('bettermodel','mythicmobs','nightcore','excellentenchants','packetevents','Vault','skript'):
        src=base/'plugins'/f'{name}.jar'
        if src.exists():shutil.copy2(src,plugins/src.name)
    shutil.copy2(ROOT/'build/runtime/AstralDecor.jar',plugins/'AstralDecor.jar')
    from terceros import privado
    delivery=privado()/'build/entregas/chaman-hitboxes-17-11'
    for sub in ('mobs','skills'):
        target=plugins/'MythicMobs'/sub;target.mkdir(parents=True,exist_ok=True)
        for folder in (ROOT/'build/mythicmobs'/sub,delivery/'mythicmobs'/sub):
            for p in folder.glob('*.yml'):shutil.copy2(p,target/p.name)
    models=plugins/'BetterModel/models';models.mkdir(parents=True,exist_ok=True)
    for source in (ROOT/'build/models',privado()/'build/models',delivery/'models'):
        for p in source.glob('*.bbmodel'):shutil.copy2(p,models/p.name)
    shutil.copy2(ROOT/'datapack-src/mobs/bettermodel_config.yml',plugins/'BetterModel/config.yml')
    scripts=plugins/'Skript/scripts';scripts.mkdir(parents=True,exist_ok=True)
    shutil.copy2(ROOT/'build/mazmorras/astral_mazmorras_copias.sk',scripts/'astral_mazmorras_copias.sk')
    packs=srv/'world/datapacks';packs.mkdir(parents=True,exist_ok=True)
    shutil.copy2(ROOT/'build/AstralRPG-Items.zip',packs/'AstralRPG-Items.zip')
    deps=[*srv.joinpath('libraries').rglob('*.jar'),*srv.joinpath('versions').rglob('*.jar'),plugins/'mythicmobs.jar',plugins/'bettermodel.jar']
    subprocess.run([str(java),'-m','jdk.compiler/com.sun.tools.javac.Main','-encoding','UTF-8','-classpath',os.pathsep.join(map(str,deps)),
                    '-d',str(work),str(ROOT/'datapack-src/test_runtime/DungeonFixProbe.java')],check=True)
    with zipfile.ZipFile(plugins/'DungeonFixProbe.jar','w') as z:
        for p in work.joinpath('astraltest').glob('DungeonFixProbe*.class'):z.write(p,'astraltest/'+p.name)
        z.writestr('plugin.yml',"name: DungeonFixProbe\nversion: 1\nmain: astraltest.DungeonFixProbe\napi-version: '26.1.2'\ndepend: [AstralDecor,MythicMobs,BetterModel]\ncommands:\n  dungeonprobe: {}\n")
    log=work/'paper.log'
    with log.open('w',encoding='utf8') as out:
        process=subprocess.Popen([str(java),'-Xms512M','-Xmx3G','-jar','paper.jar','--nogui'],cwd=srv,stdin=subprocess.PIPE,stdout=out,stderr=subprocess.STDOUT,text=True)
        def cmd(s):process.stdin.write(s+'\n');process.stdin.flush()
        try:
            for _ in range(180):
                if 'For help, type' in log.read_text('utf8',errors='replace'):break
                if process.poll() is not None:raise RuntimeError('Paper termino: '+str(log))
                time.sleep(1)
            else:raise TimeoutError('Paper no arranco')
            time.sleep(8);cmd('dungeonprobe setup');time.sleep(2)
            mids=['astral_'+n+suffix for n in ('chaman','momia','yeti','golem_forja','cangrejo') for suffix in ('','_ancestral')]
            mids+=['astral_bosque_chaman','astral_tumba_momia','astral_cumbre_yeti','astral_forja_golem_forja','astral_mina_guardian',
                   'astral_santuario_chaman_eco','astral_santuario_momia_eco','astral_santuario_yeti_eco','astral_santuario_golem_forja_eco',
                   'astral_santuario_coloso_musgoso_eco','astral_santuario_trainx','astral_fosa_cangrejo','astral_ave','astral_pterodactilo']
            for mid in mids:
                cmd('dungeonprobe model '+mid);time.sleep(7)
            cmd('dungeonprobe ice');time.sleep(2);cmd('dungeonprobe reset');time.sleep(2);cmd('dungeonprobe result');time.sleep(1)
        finally:
            if process.poll() is None:cmd('stop');process.wait(timeout=60)
    content=log.read_text('utf8',errors='replace')
    print('\n'.join(l for l in content.splitlines() if 'DUNGEON ' in l or 'ERROR' in l))
    if 'failures=0' not in content or any(s in content for s in ('DUNGEON FAIL','Error loading','Failed to load','Encountered ','Configuration Error','Could not find MetaSkill')):
        raise AssertionError('Revisar '+str(log))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--java',required=True,type=Path);p.add_argument('--base',required=True,type=Path)
    a=p.parse_args();run(a.java.resolve(),a.base.resolve())

