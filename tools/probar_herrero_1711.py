"""Carga el Skript completo del Herrero en Paper aislado; sin red ni servidor remoto."""
import argparse
import re
from pathlib import Path
import shutil
import subprocess
import time

ROOT=Path(__file__).resolve().parents[1]


def run(java,base):
    work=ROOT/'.local/herrero-1711-probe'
    server=work/'paper'
    server.mkdir(parents=True,exist_ok=True)
    for name in ('libraries','versions','cache'):
        if not (server/name).exists():
            shutil.copytree(base/name,server/name)
    # Paperclip abre el cliente como ZIP; en Windows la prueba usa una copia
    # independiente para evitar restricciones de realpath sobre enlaces duros.
    for source in (base/'cache').glob('*.jar'):
        target=server/'cache'/source.name
        if target.exists() and target.stat().st_nlink>1:
            target.unlink()
            shutil.copy2(source,target)
    shutil.copy2(base/'paper.jar',server/'paper.jar')
    (server/'eula.txt').write_text('eula=true\n')
    (server/'server.properties').write_text('server-ip=127.0.0.1\nserver-port=25609\nonline-mode=false\nlevel-name=probe\nlevel-type=minecraft:flat\ngenerator-settings={"layers":[{"block":"minecraft:bedrock","height":1}],"biome":"minecraft:plains"}\ngenerate-structures=false\nspawn-protection=0\nmanagement-server-enabled=false\n')
    plugins=server/'plugins'
    config=server/'config'
    config.mkdir(exist_ok=True)
    # La carga/recarga del script completo tarda ~15 s en esta PC. Umbral de
    # aviso solo de este ensayo (no modifica la config del servidor real).
    (config/'paper-global.yml').write_text('watchdog:\n  early-warning-delay: 60000\n  early-warning-every: 10000\n')
    plugins.mkdir(exist_ok=True)
    for name in ('skript.jar','Vault.jar','EssentialsX.jar'):
        shutil.copy2(base/'plugins'/name,plugins/name)
    scripts=plugins/'Skript/scripts'
    scripts.mkdir(parents=True,exist_ok=True)
    shutil.copy2(ROOT/'build/services/astral_servicios.sk',scripts/'astral_servicios.sk')
    log=work/'paper.log'
    with log.open('w',encoding='utf8') as out:
        process=subprocess.Popen([str(java),'-Xms512M','-Xmx2G','-jar','paper.jar','--nogui'],cwd=server,
                                 stdin=subprocess.PIPE,stdout=out,stderr=subprocess.STDOUT,text=True)
        def cmd(c):
            process.stdin.write(c+'\n');process.stdin.flush()
        try:
            for _ in range(180):
                content=log.read_text(encoding='utf8',errors='replace')
                if 'For help, type' in content and ('All scripts loaded' in content or 'Encountered' in content):break
                if process.poll() is not None:raise RuntimeError('Paper termino: '+str(log))
                time.sleep(1)
            else:raise TimeoutError('Paper no termino de cargar')
            cmd('skript:skript reload astral_servicios')
            for _ in range(60):
                content=re.sub(r'\x1b\[[0-9;]*m','',log.read_text(encoding='utf8',errors='replace'))
                if 'Successfully reloaded astral_servicios.sk' in content:break
                if 'Encountered' in content:raise AssertionError('Error de Skript: '+str(log))
                time.sleep(1)
            else:raise TimeoutError('No termino la recarga de Skript')
        finally:
            if process.poll() is None:
                cmd('stop');process.wait(timeout=60)
    content=log.read_text(encoding='utf8',errors='replace')
    print('\n'.join(l for l in content.splitlines() if any(s in l for s in ('Skript','AstralRPG','ERROR','Line '))))
    if 'All scripts loaded without errors' not in content or 'Encountered' in content or 'ERROR' in content:
        raise AssertionError('Revisar '+str(log))
    print('HERRERO: carga y recarga sin errores. Interaccion con cliente pendiente.')


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--java',required=True,type=Path)
    p.add_argument('--base',required=True,type=Path)
    a=p.parse_args()
    run(a.java.resolve(),a.base.resolve())
