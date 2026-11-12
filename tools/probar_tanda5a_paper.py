"""Ensayo aislado: no conecta al servidor remoto ni instala plugins de prueba alli."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import time
import zipfile

ROOT=Path(__file__).resolve().parents[1]


def run(java, source):
    server=ROOT/'.local/tanda5a/paper'
    server.mkdir(parents=True,exist_ok=True)
    for name in ['libraries','versions','cache']:
        shutil.copytree(source/name,server/name,dirs_exist_ok=True)
    shutil.copy2(source/'paper.jar',server/'paper.jar')
    plugins=server/'plugins';plugins.mkdir(exist_ok=True)
    for name,path in [('auraskills.jar',ROOT/'.local/asw-native/server/plugins/auraskills.jar'),
                      ('mythicmobs.jar',ROOT/'.local/asw-native/server/plugins/mythicmobs.jar'),
                      ('GriefPrevention.jar',ROOT/'.local/tanda5a/GriefPrevention.jar'),
                      ('ExpendableBackpacks.jar',ROOT/'.local/expendable/ExpendableBackpacks-1.2.0.jar'),
                      ('AstralProgression.jar',ROOT/'build/runtime/AstralProgression.jar')]:
        shutil.copy2(path,plugins/name)
    for name in ['nightcore.jar','excellentenchants.jar','packetevents.jar']:
        shutil.copy2(source/'plugins'/name,plugins/name)
    # Solo configuraciones de plugins propias del ensayo; ningun dato de jugadores previo.
    for folder in ['AstralProgression','GriefPreventionData','ExpendableBackpacks']:
        shutil.copytree(ROOT/'build/tanda5a'/folder,plugins/folder,dirs_exist_ok=True)
    mm=plugins/'MythicMobs/mobs';mm.mkdir(parents=True,exist_ok=True)
    (mm/'tanda5a_probe.yml').write_text('astral_mina_guardian:\n  Type: ZOMBIE\n  Health: 100\n  Damage: 1\n  Options:\n    NoAI: true\n  Drops: []\n')
    import sys
    sys.path.insert(0,str(ROOT/'datapack-src'))
    import yaml
    with zipfile.ZipFile(ROOT/'.local/asw-native/server/plugins/AuraSkills/presets/legacy.zip') as z:
        for name in z.namelist():
            if name.startswith('files/') and name.endswith('.yml'):
                path=plugins/'AuraSkills'/name[len('files/'):];path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(z.read(name))
    # El jugador NMS no tiene canal de cliente real para overlays de PacketEvents.
    # Se desactiva SOLO esa UI en el ensayo; los eventos y la XP siguen activos.
    aura=plugins/'AuraSkills/config.yml'
    cfg=yaml.safe_load(aura.read_text(encoding='utf8')) if aura.exists() else {}
    cfg.setdefault('hooks',{})['packetevents']={'enabled':False}
    cfg.setdefault('action_bar',{})['enabled']=False
    aura.write_text(yaml.safe_dump(cfg,sort_keys=False),encoding='utf8')
    # No natural mobs ni autenticacion en el ensayo local.
    (server/'eula.txt').write_text('eula=true\n')
    (server/'server.properties').write_text('online-mode=false\nserver-ip=127.0.0.1\nserver-port=25595\nlevel-name=world\nlevel-type=minecraft:flat\ngenerator-settings={"layers":[{"block":"minecraft:bedrock","height":1},{"block":"minecraft:stone","height":2},{"block":"minecraft:grass_block","height":1}],"biome":"minecraft:plains"}\nspawn-protection=0\nview-distance=2\nsimulation-distance=2\n')
    datapacks=server/'world/datapacks';datapacks.mkdir(parents=True,exist_ok=True)
    shutil.copy2(ROOT/'build/AstralRPG-Items.zip',datapacks/'AstralRPG-Items.zip')
    for slug in ['dungeons-and-taverns','explorify','structory','structory-towers']:
        import json
        v=json.loads((ROOT/f'.local/tanda5a/{slug}.json').read_text())[0]
        f=next(f for f in v['files'] if f['primary'])
        shutil.copy2(ROOT/'.local/tanda5a'/f['filename'],datapacks/f['filename'])
    jars=list((server/'libraries').rglob('*.jar'))+list((server/'versions').rglob('*.jar'))+list(plugins.glob('*.jar'))
    target=ROOT/'.local/tanda5a/probe';target.mkdir(exist_ok=True)
    subprocess.run([str(java),'-m','jdk.compiler/com.sun.tools.javac.Main','-encoding','UTF-8',
        '-classpath',os.pathsep.join(map(str,jars)),'-d',str(target),str(ROOT/'datapack-src/test_runtime/ProgressionProbe.java')],check=True)
    with zipfile.ZipFile(plugins/'ProgressionProbe.jar','w') as z:
        for p in (target/'astraltest').glob('ProgressionProbe*.class'):z.write(p,'astraltest/'+p.name)
        z.writestr('plugin.yml',"name: ProgressionProbe\nversion: 1\nmain: astraltest.ProgressionProbe\napi-version: '26.1.2'\ndepend: [AstralProgression, ExpendableBackpacks]\ncommands:\n  t5probe: {}\n")
    for phase in ['paper','restart']:
        log=ROOT/f'.local/tanda5a/{phase}.log'
        with log.open('w',encoding='utf8') as out:
            proc=subprocess.Popen([str(java),'-Dterminal.jline=false','-Dterminal.ansi=false','-Xms512M','-Xmx2G','-jar','paper.jar','--nogui'],cwd=server,stdin=subprocess.PIPE,stdout=out,stderr=subprocess.STDOUT,text=True)
            def command(c):proc.stdin.write(c+'\n');proc.stdin.flush()
            try:
                for _ in range(240):
                    content=log.read_text(encoding='utf8',errors='replace')
                    if 'For help, type' in content:break
                    if proc.poll() is not None:raise RuntimeError('Paper termino: '+str(log))
                    time.sleep(1)
                else:raise TimeoutError('Arranque: '+str(log))
                cases=[('player',5),('xp',6),('claims',6),('loot',6),('backpack',3),('result',1)] if phase=='paper' else [('player',5),('restart',3),('result',1)]
                for c,seconds in cases:
                    command('t5probe '+c);time.sleep(seconds)
            finally:
                if proc.poll() is None:command('stop');proc.wait(timeout=60)
        content=log.read_text(encoding='utf8',errors='replace')
        print('\n'.join(l for l in content.splitlines() if 'T5A' in l or 'ERROR' in l),flush=True)
        if 'T5A RESULT failures=0' not in content or 'ERROR' in content:
            raise AssertionError('Pruebas Paper fallaron; revisar '+str(log))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--java',type=Path,required=True);p.add_argument('--source',type=Path,required=True)
    args=p.parse_args();run(args.java.resolve(),args.source.resolve())
