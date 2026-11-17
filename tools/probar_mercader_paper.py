"""Ensayo aislado del Goblin Mercader en Paper/Mythic reales. Nunca instala en remoto."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import zipfile

ROOT=Path(__file__).resolve().parents[1]


def run(java,base):
    sys.path.insert(0,str(ROOT/'datapack-src'))
    from deploy_cascos_silencio import OUT
    work=ROOT/'.local/merchant-probe';server=work/'paper';server.mkdir(parents=True,exist_ok=True)
    for name in ('libraries','versions','cache'):
        if not (server/name).exists():shutil.copytree(base/name,server/name)
    shutil.copy2(base/'paper.jar',server/'paper.jar')
    (server/'eula.txt').write_text('eula=true\n')
    (server/'server.properties').write_text('server-ip=127.0.0.1\nserver-port=25592\nonline-mode=false\nlevel-name=world\nlevel-type=minecraft:flat\ngenerator-settings={"layers":[{"block":"minecraft:bedrock","height":1}],"biome":"minecraft:plains"}\ngenerate-structures=false\nspawn-protection=0\nmanagement-server-enabled=false\nview-distance=2\nsimulation-distance=2\nmax-tick-time=-1\n')
    plugins=server/'plugins';plugins.mkdir(exist_ok=True)
    for name in ('bettermodel','mythicmobs','nightcore','excellentenchants','packetevents','Vault'):
        shutil.copy2(base/'plugins'/f'{name}.jar',plugins/f'{name}.jar')
    shutil.copy2(ROOT/'build/runtime/AstralDecor.jar',plugins/'AstralDecor.jar')
    for sub in ('mobs','skills'):
        dest=plugins/'MythicMobs'/sub;dest.mkdir(parents=True,exist_ok=True)
        for p in (ROOT/'build/mythicmobs'/sub).glob('*.yml'):shutil.copy2(p,dest/p.name)
    # YAML exactos de la entrega, incluida la copia privada de astral.yml.
    for p in (OUT/'mythicmobs/mobs').glob('*.yml'):shutil.copy2(p,plugins/'MythicMobs/mobs'/p.name)
    from terceros import privado
    for name in ('astral.yml','trainx.yml'):
        shutil.copy2(privado()/'build/entregas/monturas-17-11/mythicmobs/skills'/name,plugins/'MythicMobs/skills'/name)
    shutil.copy2(privado()/'build/entregas/mascotas-oceano-panorama-17-11/mythicmobs/skills/mascotas.yml',plugins/'MythicMobs/skills/mascotas.yml')
    models=plugins/'BetterModel/models';models.mkdir(parents=True,exist_ok=True)
    for source in (ROOT/'build/models',privado()/'build/models',privado()/'build/entregas/correcciones-goblin-golems/models'):
        for p in source.glob('*.bbmodel'):shutil.copy2(p,models/p.name)
    shutil.copy2(ROOT/'datapack-src/mobs/bettermodel_config.yml',plugins/'BetterModel/config.yml')
    packs=server/'world/datapacks';packs.mkdir(parents=True,exist_ok=True)
    shutil.copy2(ROOT/'build/AstralRPG-Items.zip',packs/'AstralRPG-Items.zip')
    deps=[*server.joinpath('libraries').rglob('*.jar'),*server.joinpath('versions').rglob('*.jar'),plugins/'mythicmobs.jar',plugins/'Vault.jar']
    subprocess.run([str(java),'-m','jdk.compiler/com.sun.tools.javac.Main','-encoding','UTF-8','-classpath',os.pathsep.join(map(str,deps)),
                    '-d',str(work),str(ROOT/'datapack-src/test_runtime/MerchantProbe.java')],check=True)
    with zipfile.ZipFile(plugins/'MerchantProbe.jar','w') as z:
        for p in work.joinpath('astraltest').glob('MerchantProbe*.class'):z.write(p,'astraltest/'+p.name)
        z.writestr('plugin.yml',"name: MerchantProbe\nversion: 1\nmain: astraltest.MerchantProbe\napi-version: '26.1.2'\ndepend: [AstralDecor,MythicMobs,BetterModel,Vault]\ncommands:\n  merchantprobe: {}\n  dm: {}\n")
    log=work/'paper.log'
    with log.open('w',encoding='utf8') as out:
        process=subprocess.Popen([str(java),'-Xms512M','-Xmx2G','-jar','paper.jar','--nogui'],cwd=server,stdin=subprocess.PIPE,stdout=out,stderr=subprocess.STDOUT,text=True)
        def cmd(s):process.stdin.write(s+'\n');process.stdin.flush()
        try:
            for _ in range(180):
                if 'For help, type' in log.read_text('utf8',errors='replace'):break
                if process.poll() is not None:raise RuntimeError('Paper termino: '+str(log))
                time.sleep(1)
            else:raise TimeoutError('Paper no arranco')
            cmd('merchantprobe')
            for _ in range(120):
                if 'MERCHANT RESULT' in log.read_text('utf8',errors='replace'):break
                time.sleep(1)
            else:raise TimeoutError('Ensayo sin resultado')
        finally:
            if process.poll() is None:cmd('stop');process.wait(timeout=60)
    content=log.read_text('utf8',errors='replace')
    print('\n'.join(l for l in content.splitlines() if 'MERCHANT ' in l or 'ERROR' in l))
    if 'failures=0' not in content or any(s in content for s in ('MERCHANT FAIL','Error loading','Failed to load','Encountered ','Configuration Error','Could not find MetaSkill')):
        raise AssertionError('Revisar '+str(log))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--java',required=True,type=Path);p.add_argument('--base',required=True,type=Path)
    args=p.parse_args();run(args.java.resolve(),args.base.resolve())
