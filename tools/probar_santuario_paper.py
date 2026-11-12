"""Paper aislado: dimension, puntos, cinco oleadas, cofre y rescate con jugador simulado.

Congela IA: no sustituye recorrido, combate ni capturas con cliente real.
"""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import time
import zipfile

ROOT=Path(__file__).resolve().parents[1]


def run(java,base,regions,work):
    if not work.is_relative_to(ROOT/'.local') or work.exists():
        raise ValueError('Elegir una carpeta nueva dentro de .local')
    server=work/'paper';server.mkdir(parents=True)
    for name in ('libraries','versions','cache'):
        shutil.copytree(base/name,server/name)
    shutil.copy2(base/'paper.jar',server/'paper.jar')
    (server/'eula.txt').write_text('eula=true\n')
    (server/'spigot.yml').write_text('settings:\n  attribute:\n    maxHealth:\n      max: 1000000000\n    attackDamage:\n      max: 10000000\n')
    (server/'server.properties').write_text('server-ip=127.0.0.1\nserver-port=25603\nonline-mode=false\nlevel-name=world\nlevel-type=minecraft:flat\ngenerator-settings={"layers":[{"block":"minecraft:bedrock","height":1}],"biome":"minecraft:plains"}\ngenerate-structures=false\nmanagement-server-enabled=false\nview-distance=10\nsimulation-distance=10\n')
    plugins=server/'plugins';plugins.mkdir()
    for name in ('nightcore.jar','excellentenchants.jar','packetevents.jar','mythicmobs.jar','bettermodel.jar','skript.jar','auraskills.jar'):
        shutil.copy2(ROOT/'.local/testsrv/plugins'/name,plugins/name)
    for plugin in ('NightCore','ExcellentEnchants','AuraSkills'):
        src=ROOT/'.local/testsrv/plugins'/plugin
        if src.exists():shutil.copytree(src,plugins/plugin)
    for sub in ('mobs','skills'):
        dest=plugins/'MythicMobs'/sub;dest.mkdir(parents=True)
        for p in (ROOT/'build/mythicmobs'/sub).glob('*.yml'):shutil.copy2(p,dest/p.name)
    models=plugins/'BetterModel/models';models.mkdir(parents=True)
    for p in (ROOT/'build/models').glob('*.bbmodel'):shutil.copy2(p,models/p.name)
    shutil.copy2(ROOT/'datapack-src/mobs/bettermodel_config.yml',plugins/'BetterModel/config.yml')
    scripts=plugins/'Skript/scripts';scripts.mkdir(parents=True)
    shutil.copy2(ROOT/'build/gameplay/astral_gameplay.sk',scripts/'astral_gameplay.sk')
    shutil.copy2(ROOT/'build/mapas_exploracion/astral_viajes.sk',scripts/'astral_viajes.sk')
    packs=server/'world/datapacks';packs.mkdir(parents=True)
    shutil.copy2(ROOT/'build/AstralRPG-Items.zip',packs/'AstralRPG-Items.zip')
    shutil.copytree(regions,server/'world/dimensions/minecraft/santuario_azeroth/region')
    deps=[*server.joinpath('libraries').rglob('*.jar'),*server.joinpath('versions').rglob('*.jar'),plugins/'mythicmobs.jar']
    subprocess.run([str(java),'-m','jdk.compiler/com.sun.tools.javac.Main','-encoding','UTF-8','-classpath',os.pathsep.join(map(str,deps)),'-d',str(work),str(ROOT/'datapack-src/test_runtime/SanctuaryProbe.java')],check=True)
    with zipfile.ZipFile(plugins/'SanctuaryProbe.jar','w') as z:
        z.write(work/'astraltest/SanctuaryProbe.class','astraltest/SanctuaryProbe.class')
        z.writestr('plugin.yml',"name: SanctuaryProbe\nversion: 1\nmain: astraltest.SanctuaryProbe\napi-version: '26.1.2'\ndepend: [MythicMobs, Skript]\ncommands:\n  sanctuaryprobe: {}\n")
    log=work/'paper.log'
    with log.open('w',encoding='utf8') as out:
        p=subprocess.Popen([str(java),'-Xms512M','-Xmx3G','-jar','paper.jar','--nogui'],cwd=server,stdin=subprocess.PIPE,stdout=out,stderr=subprocess.STDOUT,text=True)
        def command(c):p.stdin.write(c+'\n');p.stdin.flush()
        try:
            for _ in range(180):
                if 'For help, type' in log.read_text(encoding='utf8',errors='replace'):break
                if p.poll() is not None:raise RuntimeError('Paper termino: '+str(log))
                time.sleep(1)
            else:raise TimeoutError('Paper no arranco')
            command('sanctuaryprobe start');time.sleep(5)
            for i in range(5):command(f'sanctuaryprobe wave {i}');time.sleep(5)
            command('sanctuaryprobe final');time.sleep(2)
            command('sanctuaryprobe rescue');time.sleep(12)
            command('sanctuaryprobe result');time.sleep(1)
        finally:
            if p.poll() is None:command('stop');p.wait(timeout=60)
    content=log.read_text(encoding='utf8',errors='replace')
    print('\n'.join(l for l in content.splitlines() if 'SANCTUARY' in l or 'ERROR' in l))
    if 'SANCTUARY RESULT' not in content or 'failures=0' not in content or 'SANCTUARY FAIL' in content:
        raise AssertionError(str(log))
    if 'Failed to load' in content or 'Error loading' in content or 'Encountered ' in content:
        raise AssertionError('Errores de carga: '+str(log))


if __name__=='__main__':
    a=argparse.ArgumentParser(description=__doc__)
    for name in ('java','base','regions','work'):a.add_argument('--'+name,type=Path,required=True)
    args=a.parse_args();run(*(getattr(args,n).resolve() for n in ('java','base','regions','work')))
