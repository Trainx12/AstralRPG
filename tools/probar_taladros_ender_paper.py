"""Prueba local de Herrero y Ender; dos arranques para verificar persistencia real."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import time
import zipfile

ROOT=Path(__file__).resolve().parents[1]


def run(java,base):
    work=ROOT/'.local/ender-probe';server=work/'paper';server.mkdir(parents=True,exist_ok=True)
    for name in ('libraries','versions','cache'):
        if not (server/name).exists():shutil.copytree(base/name,server/name)
    shutil.copy2(base/'paper.jar',server/'paper.jar')
    (server/'eula.txt').write_text('eula=true\n')
    (server/'server.properties').write_text('server-ip=127.0.0.1\nserver-port=25607\nonline-mode=false\nlevel-name=probe\nlevel-type=minecraft:flat\ngenerator-settings={"layers":[{"block":"minecraft:bedrock","height":1}],"biome":"minecraft:plains"}\ngenerate-structures=false\nspawn-protection=0\nmanagement-server-enabled=false\n')
    plugins=server/'plugins';plugins.mkdir(exist_ok=True)
    for name in ('bettermodel','mythicmobs','nightcore','excellentenchants','packetevents'):
        shutil.copy2(base/'plugins'/f'{name}.jar',plugins/f'{name}.jar')
    for name in ('ExcellentEnchants','NightCore'):
        if (base/'plugins'/name).exists():shutil.copytree(base/'plugins'/name,plugins/name,dirs_exist_ok=True)
    shutil.copy2(ROOT/'build/mochilas-ender/AstralDecor.jar',plugins/'AstralDecor.jar')
    shutil.copy2(ROOT/'.local/expendable/ExpendableBackpacks-1.2.0.jar',plugins/'ExpendableBackpacks.jar')
    config=plugins/'ExpendableBackpacks/config.yml';config.parent.mkdir(exist_ok=True)
    shutil.copy2(ROOT/'datapack-src/plugin-presets/ExpendableBackpacks--config.yml',config)
    packs=server/'probe/datapacks';packs.mkdir(parents=True,exist_ok=True)
    shutil.copy2(ROOT/'build/mochilas-ender/AstralRPG-Items.zip',packs/'AstralRPG-Items.zip')
    deps=[*server.joinpath('libraries').rglob('*.jar'),*server.joinpath('versions').rglob('*.jar'),plugins/'ExpendableBackpacks.jar']
    subprocess.run([str(java),'-m','jdk.compiler/com.sun.tools.javac.Main','-encoding','UTF-8','-classpath',os.pathsep.join(map(str,deps)),
                    '-d',str(work),str(ROOT/'datapack-src/test_runtime/EnderProbe.java')],check=True)
    with zipfile.ZipFile(plugins/'EnderProbe.jar','w') as z:
        for p in work.joinpath('astraltest').glob('EnderProbe*.class'):z.write(p,'astraltest/'+p.name)
        z.writestr('plugin.yml',"name: EnderProbe\nversion: 1\nmain: astraltest.EnderProbe\napi-version: '26.1.2'\ndepend: [AstralDecor,ExpendableBackpacks]\ncommands:\n  enderprobe: {}\n")
    for passno,steps in enumerate((('smith','bags','result'),('persisted','result')),1):
        log=work/f'paper-{passno}.log'
        with log.open('w',encoding='utf8') as out:
            p=subprocess.Popen([str(java),'-Xms512M','-Xmx2G','-jar','paper.jar','--nogui'],cwd=server,
                               stdin=subprocess.PIPE,stdout=out,stderr=subprocess.STDOUT,text=True)
            def cmd(c):p.stdin.write(c+'\n');p.stdin.flush()
            try:
                for _ in range(240):
                    if 'For help, type' in log.read_text('utf8',errors='replace'):break
                    if p.poll() is not None:raise RuntimeError('Paper termino: '+str(log))
                    time.sleep(1)
                else:raise TimeoutError('Paper no arranco')
                for step in steps:
                    cmd('enderprobe '+step)
                    marker='ENDER RESULT failures=' if step=='result' else f'ENDER STEP {step} DONE'
                    for _ in range(120):
                        if marker in log.read_text('utf8',errors='replace'):break
                        if p.poll() is not None:raise RuntimeError('Paper termino: '+str(log))
                        time.sleep(.5)
                    else:raise TimeoutError('No termino '+step)
            finally:
                if p.poll() is None:cmd('stop');p.wait(timeout=60)
        content=log.read_text('utf8',errors='replace')
        print('\n'.join(l for l in content.splitlines() if 'ENDER FAIL' in l or 'ENDER STEP' in l or 'ENDER RESULT' in l or 'ERROR' in l))
        if 'ENDER RESULT failures=0' not in content or any(s in content for s in ('ENDER FAIL','Error loading','Failed to load','Encountered ')):
            raise AssertionError('Revisar '+str(log))
        print('PASS',passno,'comprobaciones:',content.count('ENDER PASS'),'log privado:',log)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--java',required=True,type=Path);p.add_argument('--base',required=True,type=Path)
    a=p.parse_args();run(a.java.resolve(),a.base.resolve())
