"""Ensayo aislado de paquetes de gorros con dos jugadores NMS; sin cliente ni remoto."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import time
import zipfile

ROOT=Path(__file__).resolve().parents[1]


def run(java,base):
    work=ROOT/'.local/disenos-probe';server=work/'paper'
    server.mkdir(parents=True,exist_ok=True)
    for name in ('libraries','versions','cache'):
        if not (server/name).exists():shutil.copytree(base/name,server/name)
    shutil.copy2(base/'paper.jar',server/'paper.jar')
    (server/'eula.txt').write_text('eula=true\n')
    (server/'server.properties').write_text('server-ip=127.0.0.1\nserver-port=25597\nonline-mode=false\nlevel-name=probe\nlevel-type=minecraft:flat\ngenerate-structures=false\nspawn-protection=0\nmanagement-server-enabled=false\n')
    plugins=server/'plugins';plugins.mkdir(exist_ok=True)
    shutil.copy2(ROOT/'build/runtime/AstralDecor.jar',plugins/'AstralDecor.jar')
    for name in ('nightcore.jar','excellentenchants.jar','packetevents.jar'):
        shutil.copy2(base/'plugins'/name,plugins/name)
    packs=server/'probe/datapacks';packs.mkdir(parents=True,exist_ok=True)
    shutil.copy2(ROOT/'build/AstralRPG-Items.zip',packs/'AstralRPG-Items.zip')
    deps=[*server.joinpath('libraries').rglob('*.jar'),*server.joinpath('versions').rglob('*.jar')]
    subprocess.run([str(java),'-m','jdk.compiler/com.sun.tools.javac.Main','-encoding','UTF-8','-classpath',os.pathsep.join(map(str,deps)),'-d',str(work),str(ROOT/'datapack-src/test_runtime/DesignsProbe.java')],check=True)
    with zipfile.ZipFile(plugins/'DesignsProbe.jar','w') as z:
        for p in (work/'astraltest').glob('DesignsProbe*.class'):z.write(p,'astraltest/'+p.name)
        z.writestr('plugin.yml',"name: DesignsProbe\nversion: 1\nmain: astraltest.DesignsProbe\napi-version: '26.1.2'\ndepend: [AstralDecor]\ncommands:\n  designsprobe: {}\n")
    log=work/'paper.log'
    with log.open('w',encoding='utf8') as out:
        process=subprocess.Popen([str(java),'-Xms512M','-Xmx2G','-jar','paper.jar','--nogui'],cwd=server,stdin=subprocess.PIPE,stdout=out,stderr=subprocess.STDOUT,text=True)
        def cmd(c):process.stdin.write(c+'\n');process.stdin.flush()
        try:
            for _ in range(180):
                if 'For help, type' in log.read_text(encoding='utf8',errors='replace'):break
                if process.poll() is not None:raise RuntimeError('Paper termino: '+str(log))
                time.sleep(1)
            else:raise TimeoutError('Paper no arranco')
            for step in ('start','equipped','helmet','restore','clear','legacy','result'):
                cmd('designsprobe '+step);time.sleep(2)
        finally:
            if process.poll() is None:cmd('stop');process.wait(timeout=60)
    content=log.read_text(encoding='utf8',errors='replace')
    print('\n'.join(l for l in content.splitlines() if 'DESIGNS' in l or 'ERROR' in l))
    if 'DESIGNS RESULT failures=0' not in content:raise AssertionError('Fallo: '+str(log))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--java',type=Path,required=True);parser.add_argument('--base',type=Path,required=True)
    args=parser.parse_args();run(args.java.resolve(),args.base.resolve())
