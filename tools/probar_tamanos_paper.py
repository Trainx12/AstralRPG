"""Prueba escalas y jinetes con Paper local; nunca despliega ni toma capturas falsas."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import time
import zipfile
import sys

ROOT=Path(__file__).resolve().parents[1]


def run(java,server):
    if not server.is_relative_to(ROOT/'.local'):raise ValueError('Solo Paper local en .local')
    sys.path.insert(0,str(ROOT/'datapack-src'))
    from mobs.tamanos import scale
    from terceros import privado
    from deploy_esqueletos import NAMES, main
    main()
    work=ROOT/'.local/tamanos-probe';work.mkdir(exist_ok=True)
    deps=[*server.joinpath('libraries').rglob('*.jar'),*server.joinpath('versions').rglob('*.jar'),server/'plugins/mythicmobs.jar',server/'plugins/bettermodel.jar']
    subprocess.run([str(java),'-m','jdk.compiler/com.sun.tools.javac.Main','-encoding','UTF-8','-classpath',os.pathsep.join(map(str,deps)),'-d',str(work),str(ROOT/'datapack-src/test_runtime/TamanosProbe.java')],check=True)
    with zipfile.ZipFile(server/'plugins/TamanosProbe.jar','w') as z:
        z.write(work/'astraltest/TamanosProbe.class','astraltest/TamanosProbe.class')
        z.writestr('plugin.yml',"name: TamanosProbe\nversion: 1\nmain: astraltest.TamanosProbe\napi-version: '26.1.2'\ndepend: [BetterModel, MythicMobs]\ncommands:\n  tamanosprobe: {}\n")
    for name in NAMES:
        source=(privado()/'build/entregas/esqueletos-tamano/mythicmobs/skills/astral.yml' if name=='astral' else ROOT/f'build/mythicmobs/skills/{name}.yml')
        shutil.copy2(source,server/f'plugins/MythicMobs/skills/{name}.yml')
    log=work/'paper.log'
    with log.open('w',encoding='utf8') as out:
        p=subprocess.Popen([str(java),'-Dterminal.jline=false','-Dterminal.ansi=false','-Xms512M','-Xmx2G','-jar','paper.jar','--nogui'],cwd=server,stdin=subprocess.PIPE,stdout=out,stderr=subprocess.STDOUT,text=True)
        def cmd(c):p.stdin.write(c+'\n');p.stdin.flush()
        try:
            for _ in range(180):
                if 'For help, type' in log.read_text(encoding='utf8',errors='replace'):break
                if p.poll() is not None:raise RuntimeError('Paper termino antes de arrancar')
                time.sleep(1)
            else:raise TimeoutError('Paper no arranco')
            for k in ('arquero','escudero','guardian','nigromante'):
                mid='astral_esq_'+k;sc=scale(mid,1,'SKELETON')
                cmd(f'tamanosprobe {mid} {sc}');time.sleep(2)
                cmd(f'tamanosprobe {mid} {sc} mounted');time.sleep(2)
            for mid in ('astral_yeti_ancestral','astral_cumbre_yeti'):
                cmd(f'tamanosprobe {mid} {scale("astral_yeti",2,"RAVAGER")}');time.sleep(2)
            cmd('tamanosprobe result');time.sleep(1)
        finally:
            if p.poll() is None:cmd('stop');p.wait(timeout=60)
    content=log.read_text(encoding='utf8',errors='replace')
    print('\n'.join(l for l in content.splitlines() if 'TAMANOS' in l or 'ERROR' in l))
    if 'TAMANOS RESULT tested=10 failures=0' not in content or 'TAMANOS FAIL' in content:raise AssertionError(str(log))
    print('Log privado:',log,'; pendiente revision visual con cliente')


if __name__=='__main__':
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('--java',type=Path,required=True);a.add_argument('--server',type=Path,required=True)
    args=a.parse_args();run(args.java.resolve(),args.server.resolve())
