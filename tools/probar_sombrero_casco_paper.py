"""Sombrero sobre el casco con Paper real; los JAR de prueba nunca van al servidor remoto."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import time
import zipfile

ROOT=Path(__file__).resolve().parents[1]


def run(java,base):
    server=ROOT/'.local/sombrero-casco-paper'
    work=ROOT/'.local/sombrero-casco-probe'
    server.mkdir(exist_ok=True);work.mkdir(exist_ok=True)
    for name in ('libraries','versions','cache'):
        if not (server/name).exists():shutil.copytree(base/name,server/name)
    shutil.copy2(base/'paper.jar',server/'paper.jar')
    (server/'eula.txt').write_text('eula=true\n')
    (server/'server.properties').write_text('server-ip=127.0.0.1\nserver-port=25597\nonline-mode=false\nlevel-name=probe\nlevel-type=minecraft:flat\ngenerator-settings={"layers":[{"block":"minecraft:bedrock","height":1}],"biome":"minecraft:plains"}\ngenerate-structures=false\nspawn-protection=0\nmanagement-server-enabled=false\n')
    plugins=server/'plugins';plugins.mkdir(exist_ok=True)
    shutil.copy2(ROOT/'build/runtime/AstralDecor.jar',plugins/'AstralDecor.jar')
    deps=[*server.joinpath('libraries').rglob('*.jar'),*server.joinpath('versions').rglob('*.jar')]
    subprocess.run([str(java),'-m','jdk.compiler/com.sun.tools.javac.Main','-encoding','UTF-8',
        '-classpath',os.pathsep.join(map(str,deps)),'-d',str(work),str(ROOT/'datapack-src/test_runtime/HatHelmetProbe.java')],check=True)
    with zipfile.ZipFile(plugins/'HatHelmetProbe.jar','w') as z:
        for p in (work/'astraltest').glob('HatHelmetProbe*.class'):z.write(p,'astraltest/'+p.name)
        z.writestr('plugin.yml',"name: HatHelmetProbe\nversion: 1\nmain: astraltest.HatHelmetProbe\napi-version: '26.1.2'\ndepend: [AstralDecor]\ncommands:\n  hatprobe: {}\n")
    log=work/'paper.log'
    with log.open('w',encoding='utf8') as out:
        p=subprocess.Popen([str(java),'-Xms512M','-Xmx2G','-jar','paper.jar','--nogui'],cwd=server,
            stdin=subprocess.PIPE,stdout=out,stderr=subprocess.STDOUT,text=True)
        def cmd(c):p.stdin.write(c+'\n');p.stdin.flush()
        try:
            for _ in range(180):
                if 'For help, type' in log.read_text(encoding='utf8',errors='replace'):break
                if p.poll() is not None:raise RuntimeError('Paper termino; ver '+str(log))
                time.sleep(1)
            else:raise TimeoutError('Paper no arranco')
            for step in ('start','worn','change','moved','again','off','bare','bare2','bare3','death','drops','result'):
                cmd('hatprobe '+step);time.sleep(2)
        finally:
            if p.poll() is None:cmd('stop');p.wait(timeout=60)
    content=log.read_text(encoding='utf8',errors='replace')
    print('\n'.join(l for l in content.splitlines() if 'HATHELM' in l or 'ERROR' in l))
    if 'HATHELM RESULT failures=0' not in content:raise AssertionError('Fallo: '+str(log))


if __name__=='__main__':
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('--java',type=Path,required=True);a.add_argument('--base',type=Path,required=True)
    args=a.parse_args();run(args.java.resolve(),args.base.resolve())
