"""Destello real de Skript con jugador NMS en world y lobby; captura paquetes sin cliente visual.
No incluye Multiverse ni todos los plugins remotos; mana usa un doble de consola.
"""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import time
import zipfile

ROOT=Path(__file__).resolve().parents[1]


def run(java,base):
    work=ROOT/'.local/blink-probe';server=work/'paper'
    server.mkdir(parents=True,exist_ok=True)
    for name in ('libraries','versions','cache'):
        if not (server/name).exists():shutil.copytree(base/name,server/name)
    shutil.copy2(base/'paper.jar',server/'paper.jar')
    (server/'eula.txt').write_text('eula=true\n')
    (server/'server.properties').write_text('server-ip=127.0.0.1\nserver-port=25598\nonline-mode=false\nlevel-name=world\nlevel-type=minecraft:flat\ngenerator-settings={"layers":[{"block":"minecraft:bedrock","height":1}],"biome":"minecraft:plains"}\ngenerate-structures=false\nspawn-protection=0\nmanagement-server-enabled=false\n')
    plugins=server/'plugins';plugins.mkdir(exist_ok=True)
    shutil.copy2(ROOT/'build/runtime/AstralDecor.jar',plugins/'AstralDecor.jar')
    for name in ('nightcore.jar','excellentenchants.jar','packetevents.jar','skript.jar'):
        shutil.copy2(base/'plugins'/name,plugins/name)
    scripts=plugins/'Skript/scripts';scripts.mkdir(parents=True,exist_ok=True)
    shutil.copy2(ROOT/'build/gameplay/astral_armas_especiales.sk',scripts/'special_weapons.sk')
    (scripts/'blinkprobe.sk').write_text('''command /blinkskill <player>:
    executable by: console
    trigger:
        set {-asw.mana::%uuid of arg-1%} to 100
        asw_blink(arg-1)
''',encoding='utf8')
    packs=server/'world/datapacks';packs.mkdir(parents=True,exist_ok=True)
    shutil.copy2(ROOT/'build/AstralRPG-Items.zip',packs/'AstralRPG-Items.zip')
    deps=[*server.joinpath('libraries').rglob('*.jar'),*server.joinpath('versions').rglob('*.jar')]
    subprocess.run([str(java),'-m','jdk.compiler/com.sun.tools.javac.Main','-encoding','UTF-8',
        '-classpath',os.pathsep.join(map(str,deps)),'-d',str(work),str(ROOT/'datapack-src/test_runtime/BlinkProbe.java')],check=True)
    with zipfile.ZipFile(plugins/'BlinkProbe.jar','w') as z:
        for p in (work/'astraltest').glob('BlinkProbe*.class'):z.write(p,'astraltest/'+p.name)
        z.writestr('plugin.yml',"name: BlinkProbe\nversion: 1\nmain: astraltest.BlinkProbe\napi-version: '26.1.2'\ndepend: [AstralDecor]\ncommands:\n  blinkprobe: {}\n")
    log=work/'paper.log'
    with log.open('w',encoding='utf8') as out:
        process=subprocess.Popen([str(java),'-Xms512M','-Xmx2G','-jar','paper.jar','--nogui'],cwd=server,
            stdin=subprocess.PIPE,stdout=out,stderr=subprocess.STDOUT,text=True)
        def cmd(c):process.stdin.write(c+'\n');process.stdin.flush()
        try:
            for _ in range(180):
                text=log.read_text(encoding='utf8',errors='replace')
                if 'For help, type' in text and 'All scripts loaded without errors' in text:break
                if process.poll() is not None:raise RuntimeError('Paper termino; ver '+str(log))
                time.sleep(1)
            else:raise TimeoutError('Paper no arranco')

            for world in ('world','lobby'):
                for step in ('start','skill','moved','cancelled'):
                    cmd('blinkprobe '+step+' '+world);time.sleep(3)
            cmd('blinkprobe result');time.sleep(1)
        finally:
            if process.poll() is None:cmd('stop');process.wait(timeout=60)
    content=log.read_text(encoding='utf8',errors='replace')
    print('\n'.join(l for l in content.splitlines() if 'BLINK' in l or 'ERROR' in l))
    if 'BLINK RESULT failures=0' not in content or 'BLINK FAIL' in content:raise AssertionError('Fallo: '+str(log))
    if 'ERROR' in content:raise AssertionError('Error en consola: '+str(log))
    if 'encountered' in content and 'error' in content:raise AssertionError('Revisar carga Skript: '+str(log))
    if any(s in content for s in ('Failed to load', 'Error loading', "Couldn't parse data file")):
        raise AssertionError('Fallo carga datapack: '+str(log))


if __name__=='__main__':
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('--java',type=Path,required=True);a.add_argument('--base',type=Path,required=True)
    args=a.parse_args();run(args.java.resolve(),args.base.resolve())
