"""Ensayo aislado de protecciones/XP y persistencia del oceano, sin acceso remoto."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import time
import tempfile
import zipfile
import yaml

ROOT=Path(__file__).resolve().parents[1]


def run(java,base,existing=None):
    parent=ROOT/'.local/tanda17-probe';parent.mkdir(parents=True,exist_ok=True)
    work=existing or Path(tempfile.mkdtemp(prefix='run-',dir=parent));print('Ensayo:',work,flush=True)
    server=work/'paper';server.mkdir(parents=True,exist_ok=True)
    for name in ('libraries','versions','cache'):
        if not (server/name).exists():shutil.copytree(base/name,server/name)
    shutil.copy2(base/'paper.jar',server/'paper.jar')
    plugins=server/'plugins';plugins.mkdir(exist_ok=True)
    for name,source in [('AuraSkills.jar',ROOT/'.local/asw-native/server/plugins/auraskills.jar'),
                        ('MythicMobs.jar',ROOT/'.local/asw-native/server/plugins/mythicmobs.jar'),
                        ('GriefPrevention.jar',ROOT/'.local/tanda5a/GriefPrevention.jar'),
                        ('AstralProgression.jar',ROOT/'build/runtime/AstralProgression.jar'),
                        ('AstralOceano.jar',ROOT/'build/oceano/AstralOceano.jar')]:shutil.copy2(source,plugins/name)
    for name in ('nightcore','excellentenchants','packetevents'):shutil.copy2(base/f'plugins/{name}.jar',plugins/f'{name}.jar')
    shutil.copytree(ROOT/'build/tanda5a/AstralProgression',plugins/'AstralProgression',dirs_exist_ok=True)
    # Las skills de proteccion exactas; solo se omite la mecanica visual de BetterModel.
    mobs=yaml.safe_load((ROOT/'build/mythicmobs/mobs/mascotas.yml').read_text('utf8'))
    skills=yaml.safe_load((ROOT/'build/mythicmobs/skills/mascotas.yml').read_text('utf8'))
    pets={k:{**v,'Skills':[line for line in v['Skills'] if '~onSpawn' in line or '~onLoad' in line]} for k,v in mobs.items() if k.startswith('astral_pet_')}
    guards={k:{'Skills':[line for line in v['Skills'] if not line.startswith('model{')]} for k,v in skills.items() if k.startswith('PET_MODELO_')}
    for sub,data in [('mobs',pets),('skills',guards)]:
        dest=plugins/'MythicMobs'/sub/'tanda17.yml';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(yaml.safe_dump(data),'utf8')
    with zipfile.ZipFile(ROOT/'.local/asw-native/server/plugins/AuraSkills/presets/legacy.zip') as z:
        for name in z.namelist():
            if name.startswith('files/') and name.endswith('.yml'):
                path=plugins/'AuraSkills'/name[6:];path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(z.read(name))
    path=plugins/'AuraSkills/config.yml';cfg=yaml.safe_load(path.read_text('utf8')) if path.exists() else {}
    cfg.setdefault('hooks',{})['packetevents']={'enabled':False};cfg.setdefault('action_bar',{})['enabled']=False
    path.write_text(yaml.safe_dump(cfg),'utf8')
    ocean=plugins/'AstralOceano';ocean.mkdir(exist_ok=True)
    if not (ocean/'config.yml').exists():shutil.copy2(ROOT/'build/oceano/config.yml',ocean/'config.yml')
    (server/'eula.txt').write_text('eula=true\n')
    (server/'server.properties').write_text('server-ip=127.0.0.1\nserver-port=25619\nonline-mode=false\nmanagement-server-enabled=false\nlevel-name=world\nlevel-type=minecraft:flat\ngenerator-settings={"layers":[{"block":"minecraft:bedrock","height":1}],"biome":"minecraft:plains"}\ngenerate-structures=false\nview-distance=2\nsimulation-distance=2\nspawn-protection=0\n')
    packs=server/'world/datapacks';packs.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/'build/AstralRPG-Items.zip',packs/'AstralRPG-Items.zip')
    jars=[*server.joinpath('libraries').rglob('*.jar'),*server.joinpath('versions').rglob('*.jar'),*plugins.glob('*.jar')]
    subprocess.run([str(java),'-m','jdk.compiler/com.sun.tools.javac.Main','-encoding','UTF-8','-classpath',os.pathsep.join(map(str,jars)),
                    '-d',str(work),str(ROOT/'datapack-src/test_runtime/Tanda17Probe.java')],check=True)
    with zipfile.ZipFile(plugins/'Tanda17Probe.jar','w') as z:
        for p in work.joinpath('astraltest').glob('Tanda17Probe*.class'):z.write(p,'astraltest/'+p.name)
        z.writestr('plugin.yml',"name: Tanda17Probe\nversion: 1\nmain: astraltest.Tanda17Probe\napi-version: '26.1.2'\ndepend: [AstralProgression, AstralOceano]\ncommands:\n  t17probe: {}\n")
    for phase in (('restart',) if existing else ('initial','restart')):
        log=work/f'{phase}.log'
        with log.open('w',encoding='utf8') as out:
            proc=subprocess.Popen([str(java),'-Xms512M','-Xmx2G','-jar','paper.jar','--nogui'],cwd=server,stdin=subprocess.PIPE,stdout=out,stderr=subprocess.STDOUT,text=True)
            def cmd(c):proc.stdin.write(c+'\n');proc.stdin.flush()
            try:
                for _ in range(180):
                    if 'For help, type' in log.read_text('utf8',errors='replace'):break
                    if proc.poll() is not None:raise RuntimeError('Paper termino: '+str(log))
                    time.sleep(1)
                else:raise TimeoutError('Paper no arranco')
                phases=[('player',5),('damage',3),('mount',3),('normal',3),('mythic',3),('legacy',3),('save',20),('regen',20),('verify',2),('result',1)] if phase=='initial' else [('player',5),('damage',3),('mount',3),('normal',3),('mythic',3),('legacy',3),('restart',8),('result',1)]
                for step,delay in phases:cmd('t17probe '+step);time.sleep(delay)
            finally:
                if proc.poll() is None:cmd('stop');proc.wait(timeout=60)
        content=log.read_text('utf8',errors='replace')
        print('\n'.join(l for l in content.splitlines() if 'T17 ' in l or 'ERROR' in l),flush=True)
        if 'T17 RESULT failures=0' not in content or any(s in content for s in ('T17 FAIL','Error loading','Failed to load','Encountered ','Configuration Error')):raise AssertionError(str(log))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--java',type=Path,required=True);parser.add_argument('--base',type=Path,required=True)
    parser.add_argument('--resume',type=Path,help='Repetir solo el reinicio sobre un ensayo previo, sin borrar nada')
    a=parser.parse_args();run(a.java.resolve(),a.base.resolve(),a.resume.resolve() if a.resume else None)
