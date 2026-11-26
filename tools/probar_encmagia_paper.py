"""Ensayo aislado de magia en Paper real. Nunca se conecta al servidor remoto."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import time
import zipfile
import yaml

ROOT=Path(__file__).resolve().parents[1]


def run(java, base, work):
    server=work/'paper'
    server.mkdir(parents=True, exist_ok=True)
    for name in ('libraries','versions','cache'):
        if not (server/name).exists():
            shutil.copytree(base/name,server/name)
    shutil.copy2(base/'paper.jar',server/'paper.jar')
    (server/'eula.txt').write_text('eula=true\n')
    (server/'server.properties').write_text('server-ip=127.0.0.1\nserver-port=25633\nonline-mode=false\n'
        'level-name=probe\nlevel-type=minecraft:flat\n'
        'generator-settings={"layers":[{"block":"minecraft:bedrock","height":1}],"biome":"minecraft:plains"}\n'
        'generate-structures=false\nspawn-protection=0\nmanagement-server-enabled=false\n')
    plugins=server/'plugins'
    plugins.mkdir(exist_ok=True)
    for name in ('auraskills.jar','skript.jar','placeholderapi.jar','DeluxeMenus.jar','packetevents.jar','nightcore.jar','excellentenchants.jar'):
        shutil.copy2(base/'plugins'/name,plugins/name)
    for name in ('mythicmobs.jar','bettermodel.jar'):
        shutil.copy2(ROOT/'.local/testsrv/plugins'/name,plugins/name)
    aura=plugins/'AuraSkills'
    aura.mkdir(exist_ok=True)
    for p in (base/'plugins/AuraSkills').glob('*.yml'):
        shutil.copy2(p,aura/p.name)
    config_path=aura/'config.yml'
    config=yaml.safe_load(config_path.read_text('utf8'))
    config['action_bar']['enabled']=False
    config_path.write_text(yaml.safe_dump(config,sort_keys=False),encoding='utf8')
    shutil.copy2(ROOT/'build/mesa/AstralMesa.jar',plugins/'AstralMesa.jar')
    shutil.copy2(ROOT/'build/runtime/AstralDecor.jar',plugins/'AstralDecor.jar')
    shutil.copy2(ROOT/'build/runtime/AstralParty.jar',plugins/'AstralParty.jar')
    # Mesa sin PacketEvents en este ensayo: el jugador NMS no tiene canal de cliente real.
    mesa=plugins/'AstralMesa'
    mesa.mkdir(exist_ok=True)
    cfg=yaml.safe_load((ROOT/'build/mesa/config.yml').read_text('utf8'))
    cfg['tooltip']['activo']=False; cfg['precio-subasta']['activo']=False
    (mesa/'config.yml').write_text(yaml.safe_dump(cfg,sort_keys=False,allow_unicode=True),encoding='utf8')
    scripts=plugins/'Skript/scripts'; scripts.mkdir(parents=True,exist_ok=True)
    shutil.copy2(ROOT/'build/gameplay/astral_armas_especiales.sk',scripts/'special_weapons.sk')
    (scripts/'encmagiaprobe.sk').write_text('''command /encmagiapago <player>:
    executable by: console
    trigger:
        set {-asw.mana::%uuid of arg-1%} to 100
        set {_ok} to asw_pay(arg-1, 50)
        send "MAGIA PAY %{_ok}%" to console
''',encoding='utf8')
    packs=server/'probe/datapacks'; packs.mkdir(parents=True,exist_ok=True)
    shutil.copy2(ROOT/'build/AstralRPG-Items.zip',packs/'AstralRPG-Items.zip')
    deps=[*server.joinpath('libraries').rglob('*.jar'),*server.joinpath('versions').rglob('*.jar'),
          plugins/'auraskills.jar',plugins/'AstralMesa.jar']
    subprocess.run([str(java),'-m','jdk.compiler/com.sun.tools.javac.Main','-encoding','UTF-8','-classpath',
                    os.pathsep.join(map(str,deps)),'-d',str(work),str(ROOT/'datapack-src/test_runtime/EncMagiaProbe.java')],check=True)
    with zipfile.ZipFile(plugins/'EncMagiaProbe.jar','w') as z:
        for p in (work/'astral').glob('EncMagiaProbe*.class'):
            z.write(p,'astral/'+p.name)
        z.writestr('plugin.yml',"name: EncMagiaProbe\nversion: 1\nmain: astral.EncMagiaProbe\napi-version: '26.1.2'\ndepend: [AstralMesa, AuraSkills, Skript]\ncommands:\n  encmagiaprobe: {}\n")
    log=work/'paper.log'
    with log.open('w',encoding='utf8') as out:
        proc=subprocess.Popen([str(java),'-Xms512M','-Xmx2G','-jar','paper.jar','--nogui'],cwd=server,
            stdin=subprocess.PIPE,stdout=out,stderr=subprocess.STDOUT,text=True)
        def cmd(c):
            proc.stdin.write(c+'\n');proc.stdin.flush()
        try:
            for _ in range(180):
                if 'For help, type' in log.read_text('utf8',errors='replace'): break
                if proc.poll() is not None: raise RuntimeError('Paper terminó: '+str(log))
                time.sleep(1)
            else: raise TimeoutError('Paper no arrancó')
            time.sleep(4)
            cmd('encmagiaprobe start'); time.sleep(4)
            cmd('encmagiaprobe run'); time.sleep(3)
        finally:
            if proc.poll() is None:
                cmd('stop');proc.wait(timeout=60)
    text=log.read_text('utf8',errors='replace')
    print('\n'.join(l for l in text.splitlines() if 'MAGIA' in l or 'ERROR' in l or 'Line ' in l),flush=True)
    if 'MAGIA RESULT failures=0' not in text or 'MAGIA FAIL' in text or 'Encountered ' in text or 'Failed to load' in text or 'Error loading' in text:
        raise AssertionError('Falló integración: '+str(log))


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--java',required=True,type=Path)
    ap.add_argument('--base',type=Path,default=ROOT/'.local/baston-requisito-probe/paper')
    ap.add_argument('--work',type=Path,default=ROOT/'.local/encmagia-probe')
    a=ap.parse_args();run(a.java.resolve(),a.base.resolve(),a.work.resolve())
