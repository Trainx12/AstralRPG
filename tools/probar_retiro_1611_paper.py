"""Paper aislado: migracion Skript, llaves, despawn y reinicio; sin tocar servidor remoto."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import time
import zipfile
ROOT=Path(__file__).resolve().parents[1]

def run(java,base,work):
    server=work/'paper';server.mkdir(parents=True,exist_ok=True)
    for name in ('libraries','versions','cache'):
        if not (server/name).exists():shutil.copytree(base/name,server/name,copy_function=os.link)
    shutil.copy2(base/'paper.jar',server/'paper.jar')
    (server/'eula.txt').write_text('eula=true\n')
    (server/'server.properties').write_text('server-ip=127.0.0.1\nserver-port=25594\nonline-mode=false\nlevel-name=probe\nlevel-type=minecraft:flat\ngenerator-settings={"layers":[{"block":"minecraft:bedrock","height":1}],"biome":"minecraft:plains"}\ngenerate-structures=false\nspawn-protection=0\nmanagement-server-enabled=false\n')
    plugins=server/'plugins';plugins.mkdir(exist_ok=True)
    for name in ('nightcore.jar','excellentenchants.jar','packetevents.jar','skript.jar'):
        shutil.copy2(base/'plugins'/name,plugins/name)
    shutil.copy2(ROOT/'build/oceano/AstralOceano.jar',plugins/'AstralOceano.jar')
    # Config de prueba: no crea ni regenera el Oceano del servidor de produccion.
    cfg=plugins/'AstralOceano';cfg.mkdir(exist_ok=True);(cfg/'config.yml').write_text('mundo: no_existe\nproxima-regeneracion: 9999999999999\n')
    scripts=plugins/'Skript/scripts';scripts.mkdir(parents=True,exist_ok=True)
    shutil.copy2(ROOT/'build/mascotas/astral_mascotas_retiro.sk',scripts/'astral_mascotas_retiro.sk')
    packs=server/'probe/datapacks';packs.mkdir(parents=True,exist_ok=True)
    shutil.copy2(ROOT/'build/AstralRPG-Items.zip',packs/'AstralRPG-Items.zip')
    deps=[*server.joinpath('libraries').rglob('*.jar'),*server.joinpath('versions').rglob('*.jar')]
    subprocess.run([str(java),'-m','jdk.compiler/com.sun.tools.javac.Main','-encoding','UTF-8','-classpath',os.pathsep.join(map(str,deps)),'-d',str(work),str(ROOT/'datapack-src/test_runtime/RetiroProbe.java')],check=True)
    with zipfile.ZipFile(plugins/'RetiroProbe.jar','w') as z:
        for p in work.joinpath('astraltest').glob('RetiroProbe*.class'):z.write(p,'astraltest/'+p.name)
        z.writestr('plugin.yml',"name: RetiroProbe\nversion: 1\nmain: astraltest.RetiroProbe\napi-version: '26.1.2'\ndepend: [Skript]\ncommands:\n  retiroprobe: {}\n  crates: {}\n")
    for cycle in (1,2):
        log=work/f'paper-{cycle}.log'
        with log.open('w',encoding='utf8') as out:
            p=subprocess.Popen([str(java),'-Xms512M','-Xmx2G','-jar','paper.jar','--nogui'],cwd=server,stdin=subprocess.PIPE,stdout=out,stderr=subprocess.STDOUT,text=True)
            def cmd(c):p.stdin.write(c+'\n');p.stdin.flush()
            try:
                for _ in range(180):
                    if 'For help, type' in log.read_text(encoding='utf8',errors='replace'):break
                    if p.poll() is not None:raise RuntimeError('Paper termino: '+str(log))
                    time.sleep(1)
                else:raise TimeoutError('Paper no arranco')
                for step in (('start','check','again','all','five','result') if cycle==1 else ('persist','noextra','result')):
                    cmd('retiroprobe '+step);time.sleep(4)
            finally:
                if p.poll() is None:cmd('stop');p.wait(timeout=60)
        content=log.read_text(encoding='utf8',errors='replace')
        print('\n'.join(l for l in content.splitlines() if 'RET ' in l or 'ERROR' in l),flush=True)
        if 'RET RESULT failures=0' not in content or 'RET FAIL' in content or 'Error loading' in content or 'Encountered ' in content:raise AssertionError('Revisar '+str(log))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--java',required=True,type=Path);p.add_argument('--base',required=True,type=Path);p.add_argument('--work',type=Path,default=ROOT/'.local/retiro-1611-probe');a=p.parse_args();run(a.java.resolve(),a.base.resolve(),a.work.resolve())
