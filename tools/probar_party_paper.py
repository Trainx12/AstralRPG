"""Ensayo aislado Paper/Skript/PAPI. Solo escucha 127.0.0.1; no modifica el servidor remoto."""
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


def run(java,base,papi,copies=None,work=None):
    work=work or ROOT/'.local/party-probe';srv=work/'paper';srv.mkdir(parents=True,exist_ok=True)
    for n in ('libraries','versions','cache'):
        if not (srv/n).exists():shutil.copytree(base/n,srv/n)
    shutil.copy2(base/'paper.jar',srv/'paper.jar')
    (srv/'eula.txt').write_text('eula=true\n')
    (srv/'server.properties').write_text('server-ip=127.0.0.1\nserver-port=25629\nonline-mode=false\nlevel-name=world\nlevel-type=minecraft:flat\ngenerator-settings={"layers":[{"block":"minecraft:bedrock","height":1}],"biome":"minecraft:plains"}\ngenerate-structures=false\nspawn-protection=0\nmanagement-server-enabled=false\nview-distance=2\nsimulation-distance=2\nmax-tick-time=-1\n')
    plugins=srv/'plugins';plugins.mkdir(exist_ok=True)
    for src in (base/'plugins/skript.jar',papi,ROOT/'build/runtime/AstralParty.jar'):shutil.copy2(src,plugins/src.name)
    scripts=plugins/'Skript/scripts';scripts.mkdir(parents=True,exist_ok=True)
    for src in (copies or ROOT/'build/mazmorras/astral_mazmorras_copias.sk',ROOT/'build/infinita/astral_infinita.sk'):shutil.copy2(src,scripts/src.name)
    # Minimizar scripts: mismo archivo real de copias; todas sus funciones/variables se cargan.
    deps=[*srv.joinpath('libraries').rglob('*.jar'),*srv.joinpath('versions').rglob('*.jar'),ROOT/'build/runtime/AstralParty.jar',papi]
    subprocess.run([str(java),'-m','jdk.compiler/com.sun.tools.javac.Main','-encoding','UTF-8','-classpath',os.pathsep.join(map(str,deps)),'-d',str(work),str(ROOT/'datapack-src/test_runtime/PartyProbe.java')],check=True)
    with zipfile.ZipFile(plugins/'PartyProbe.jar','w') as z:
        for p in (work/'astral').glob('PartyProbe*.class'):z.write(p,'astral/'+p.name)
        z.writestr('plugin.yml',"name: PartyProbe\nversion: 1\nmain: astral.PartyProbe\napi-version: '26.1.2'\ndepend: [AstralParty]\ncommands:\n  partyprobe: {}\n")
    log=work/'paper.log'
    with log.open('w',encoding='utf8') as out:
        process=subprocess.Popen([str(java),'-Xms256M','-Xmx2G','-jar','paper.jar','--nogui'],cwd=srv,stdin=subprocess.PIPE,stdout=out,stderr=subprocess.STDOUT,text=True)
        def cmd(s):process.stdin.write(s+'\n');process.stdin.flush()
        try:
            for _ in range(180):
                if 'For help, type' in log.read_text('utf8',errors='replace'):break
                if process.poll() is not None:raise RuntimeError('Paper termino: '+str(log))
                time.sleep(1)
            else:raise TimeoutError('Paper no arranco')
            time.sleep(8)
            for step,delay in [('setup',22),('controls',2),('prepareborders',2),('borders',2),('bridge',2),('fall',1),('wipe',1),('actualdeath',1),('checkactual',1),('cleanup',1)]:
                cmd('partyprobe '+step);time.sleep(delay)
        finally:
            cmd('stop');process.wait(timeout=90)
    text=log.read_text('utf8',errors='replace')
    print('\n'.join(l for l in text.splitlines() if 'PARTY ' in l or 'ERROR' in l or '[Skript]' in l))
    if 'failures=0' not in text or 'All scripts loaded without errors' not in text or 'PARTY FAIL' in text or 'generated an exception' in text:raise AssertionError(log)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--java',type=Path,required=True);p.add_argument('--base',type=Path,required=True);p.add_argument('--papi',type=Path,required=True)
    p.add_argument('--copies',type=Path,help='Version aislada de copias para verificar el archivo publicado')
    p.add_argument('--work',type=Path,help='Directorio aislado alternativo para no interferir con otro ensayo')
    a=p.parse_args();run(a.java.resolve(),a.base.resolve(),a.papi.resolve(),a.copies.resolve() if a.copies else None,a.work.resolve() if a.work else None)
