"""Ensayo aislado Paper 26.1.2: arranque, eventos XP/suerte/mochilas y reinicio."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import time
import zipfile

ROOT=Path(__file__).resolve().parents[1]


def run(java,base):
    work=ROOT/'.local/tanda-xp-probe';server=work/'paper'
    server.mkdir(parents=True,exist_ok=True)
    for name in ('libraries','versions','cache'):
        if not (server/name).exists():shutil.copytree(base/name,server/name,copy_function=os.link)
    shutil.copy2(base/'paper.jar',server/'paper.jar')
    (server/'eula.txt').write_text('eula=true\n')
    (server/'server.properties').write_text('server-ip=127.0.0.1\nserver-port=25598\nonline-mode=false\nlevel-name=probe\nlevel-type=minecraft:flat\ngenerator-settings={"layers":[{"block":"minecraft:bedrock","height":1}],"biome":"minecraft:plains"}\ngenerate-structures=false\nspawn-protection=0\nmanagement-server-enabled=false\n')
    plugins=server/'plugins';plugins.mkdir(exist_ok=True)
    shutil.copy2(ROOT/'build/runtime/AstralDecor.jar',plugins/'AstralDecor.jar')
    # Encantamientos del datapack existentes: se registran antes de cargar sus loot modifiers.
    for name in ('nightcore.jar','excellentenchants.jar','packetevents.jar'):
        shutil.copy2(base/'plugins'/name,plugins/name)
    packs=server/'probe/datapacks';packs.mkdir(parents=True,exist_ok=True)
    shutil.copy2(ROOT/'build/AstralRPG-Items.zip',packs/'AstralRPG-Items.zip')
    deps=[*server.joinpath('libraries').rglob('*.jar'),*server.joinpath('versions').rglob('*.jar')]
    subprocess.run([str(java),'-m','jdk.compiler/com.sun.tools.javac.Main','-encoding','UTF-8','-classpath',os.pathsep.join(map(str,deps)),
                    '-d',str(work),str(ROOT/'datapack-src/test_runtime/XPProbe.java')],check=True)
    with zipfile.ZipFile(plugins/'XPProbe.jar','w') as z:
        for p in work.joinpath('astraltest').glob('XPProbe*.class'):z.write(p,'astraltest/'+p.name)
        z.writestr('plugin.yml',"name: XPProbe\nversion: 1\nmain: astraltest.XPProbe\napi-version: '26.1.2'\ndepend: [AstralDecor]\ncommands:\n  xpprobe: {}\n")
    for cycle in (1,2):
        log=work/f'paper-{cycle}.log'
        with log.open('w',encoding='utf8') as out:
            p=subprocess.Popen([str(java),'-Xms512M','-Xmx2G','-jar','paper.jar','--nogui'],cwd=server,
                               stdin=subprocess.PIPE,stdout=out,stderr=subprocess.STDOUT,text=True)
            def cmd(c):p.stdin.write(c+'\n');p.stdin.flush()
            try:
                for _ in range(180):
                    if 'For help, type' in log.read_text(encoding='utf8',errors='replace'):break
                    if p.poll() is not None:raise RuntimeError('Paper termino: '+str(log))
                    time.sleep(1)
                else:raise TimeoutError('Paper no arranco')
                steps=('start','one','stack','offhand','denied','apple','roll','snapshot','backpacks','result') if cycle==1 else ('start','persist','result')
                for step in steps:
                    cmd('xpprobe '+step);time.sleep(9 if step=='roll' else 2)
            finally:
                if p.poll() is None:cmd('stop');p.wait(timeout=60)
        content=log.read_text(encoding='utf8',errors='replace')
        print('\n'.join(l for l in content.splitlines() if 'XP ' in l or 'ERROR' in l or 'recetas exactas' in l),flush=True)
        if 'XP RESULT failures=0' not in content or 'XP FAIL' in content or 'Failed to load' in content or 'Error loading' in content:
            raise AssertionError('Fallo del ensayo: '+str(log))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--java',required=True,type=Path);p.add_argument('--base',required=True,type=Path)
    args=p.parse_args();run(args.java.resolve(),args.base.resolve())
