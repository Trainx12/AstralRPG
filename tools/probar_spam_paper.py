"""Ensayo aislado de oleadas, reset, cofre y log. No instala nada en remoto."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import tempfile
import zipfile

ROOT=Path(__file__).resolve().parents[1]


def run(java,base,baseline=None,port=25597):
    sys.stdout.reconfigure(encoding='utf-8',errors='replace')
    server=Path(tempfile.mkdtemp(prefix='spam-paper-',dir=ROOT/'.local'))
    for name in ('libraries','versions','cache'):
        shutil.copytree(base/name,server/name,copy_function=os.link)
    shutil.copy2(base/'paper.jar',server/'paper.jar')
    (server/'eula.txt').write_text('eula=true\n')
    (server/'server.properties').write_text(f'online-mode=false\nlevel-name=prueba\nserver-port={port}\nview-distance=3\nsimulation-distance=3\nspawn-protection=0\nlevel-type=minecraft:flat\n')
    plugins=server/'plugins';plugins.mkdir()
    for name in ('mythicmobs','bettermodel','packetevents','excellentenchants','nightcore'):
        shutil.copy2(base/'plugins'/f'{name}.jar',plugins/f'{name}.jar')
    for folder in ('MythicMobs','BetterModel'):
        shutil.copytree(base/'plugins'/folder,plugins/folder)
    for folder in ('ExcellentEnchants','NightCore'):
        if (base/'plugins'/folder).exists():shutil.copytree(base/'plugins'/folder,plugins/folder)
    for sub in ('mobs','skills'):
        for p in (ROOT/'build/mythicmobs'/sub).glob('*.yml'):
            shutil.copy2(p,plugins/'MythicMobs'/sub/p.name)
    datapacks=server/'prueba/datapacks';datapacks.mkdir(parents=True)
    shutil.copy2(ROOT/'build/AstralRPG-Items.zip',datapacks/'AstralRPG-Items.zip')
    if baseline:
        for name in ('build/AstralRPG-Items.zip',*[f'build/mythicmobs/mobs/{k}.yml' for k in ('mazmorra','bosque','tumba','cumbre','forja')]):
            target=datapacks/'AstralRPG-Items.zip' if name.endswith('.zip') else plugins/'MythicMobs/mobs'/Path(name).name
            target.write_bytes(subprocess.check_output(['git','show',baseline+':'+name],cwd=ROOT))
    sys.path.insert(0,str(ROOT/'datapack-src'))
    import yaml
    from mobs.mazmorra import MINA
    config=plugins/'SpamProbe';config.mkdir()
    (config/'config.yml').write_text(yaml.safe_dump(dict(world=MINA['world'],center=list(MINA['rooms'][0]['centro']),
        boss=list(MINA['rooms'][-1]['centro']),boss_id=MINA['rooms'][-1]['id'],points=[list(pt) for r in MINA['rooms'] for pt in r['spawn_points']])))
    classes=ROOT/'.local/spam-classes';classes.mkdir(exist_ok=True)
    deps=[*server.joinpath('libraries').rglob('*.jar'),*server.joinpath('versions').rglob('*.jar'),
          plugins/'mythicmobs.jar',plugins/'bettermodel.jar']
    subprocess.run([str(java),'-m','jdk.compiler/com.sun.tools.javac.Main','-encoding','UTF-8',
        '-classpath',os.pathsep.join(map(str,deps)),'-d',str(classes),
        *[str(ROOT/'datapack-src/test_runtime'/f'{name}.java') for name in ('UrgenteProbe','SpamProbe')]],check=True)
    for name in ('UrgenteProbe','SpamProbe'):
        with zipfile.ZipFile(plugins/f'{name}.jar','w') as z:
            for p in (classes/'astraltest').glob(name+'*.class'):z.write(p,'astraltest/'+p.name)
            z.writestr('plugin.yml',f"name: {name}\nversion: 1\nmain: astraltest.{name}\napi-version: '26.1.2'\ndepend: [BetterModel, MythicMobs]\ncommands:\n  {name.lower()}: {{}}\n")
    log=server/'probe.log'
    print('Ensayo privado:',server,flush=True)
    with log.open('w',encoding='utf8') as out:
        p=subprocess.Popen([str(java),'-Dterminal.jline=false','-Dterminal.ansi=false','-Xms512M','-Xmx2G','-jar','paper.jar','--nogui'],cwd=server,stdin=subprocess.PIPE,stdout=out,stderr=subprocess.STDOUT,text=True)
        def cmd(c):p.stdin.write(c+'\n');p.stdin.flush()
        try:
            for _ in range(180):
                if 'For help, type' in log.read_text(encoding='utf8',errors='replace'):break
                if p.poll()!=None:raise RuntimeError('Paper termino antes de arrancar')
                time.sleep(1)
            else:raise TimeoutError('Paper no arranco')
            cmd('urgenteprobe player');time.sleep(3)
            cmd('spamprobe start')
            for _ in range(160):
                if 'SPAM RESULT' in log.read_text(encoding='utf8',errors='replace'):break
                time.sleep(1)
            else:raise TimeoutError('No termino el ensayo: '+str(log))
        finally:
            if p.poll()==None:cmd('stop');p.wait(timeout=60)
    content=log.read_text(encoding='utf8',errors='replace')
    print('\n'.join(l for l in content.splitlines() if 'SPAM ' in l or 'ERROR' in l))
    import re
    spam=re.findall(r'(?:Running function|Function) astral:tanda2/[^\s]+/tick',content)
    print('Mensajes de mantenimiento por consola:',len(spam),'Log privado:',log)
    if ('SPAM RESULT failures=0' not in content or bool(spam)!=bool(baseline)
            or 'Failed to load function astral:tanda2/' in content):raise AssertionError('Fallo el ensayo')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--java',type=Path,required=True)
    parser.add_argument('--base',type=Path,required=True)
    parser.add_argument('--baseline',metavar='REF',help='Comparar con una revision Git anterior a la correccion')
    parser.add_argument('--port',type=int,default=25597)
    args=parser.parse_args();run(args.java.resolve(),args.base.resolve(),args.baseline,args.port)
