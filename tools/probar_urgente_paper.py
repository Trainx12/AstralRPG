"""Reproduce con jugador NMS simulado. Solo Paper local; logs privados en .local.

No es cliente grafico ni certifica aspecto visual. Nunca instalar UrgenteProbe en remoto.
"""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import time
import zipfile

ROOT=Path(__file__).resolve().parents[1]


def run(java,server,all_pets=False,install=False):
    import sys
    sys.stdout.reconfigure(encoding='utf-8',errors='replace')
    if not server.resolve().is_relative_to(ROOT/'.local'):
        raise ValueError('Solo servidores locales dentro de .local')
    work=ROOT/'.local/urgente-probe';work.mkdir(exist_ok=True)
    deps=[*server.joinpath('libraries').rglob('*.jar'),*server.joinpath('versions').rglob('*.jar'),
          server/'plugins/mythicmobs.jar',server/'plugins/bettermodel.jar']
    subprocess.run([str(java),'-m','jdk.compiler/com.sun.tools.javac.Main','-encoding','UTF-8',
        '-classpath',os.pathsep.join(map(str,deps)),'-d',str(work),
        str(ROOT/'datapack-src/test_runtime/UrgenteProbe.java')],check=True)
    with zipfile.ZipFile(server/'plugins/UrgenteProbe.jar','w') as z:
        for p in work.joinpath('astraltest').glob('UrgenteProbe*.class'):
            z.write(p,'astraltest/'+p.name)
        z.writestr('plugin.yml',"name: UrgenteProbe\nversion: 1\nmain: astraltest.UrgenteProbe\napi-version: '26.1.2'\ndepend: [BetterModel, MythicMobs]\ncommands:\n  urgenteprobe: {}\n")
    (server/'plugins/MythicMobs/skills/urgente_probe.yml').write_text(
        'URGENTE_VARIABLE:\n  Skills:\n  - setvariable{var=global.pet_owner;value="AstralProbe";type=STRING}\n')
    if install:
        import sys
        sys.path.insert(0,str(ROOT/'datapack-src'))
        from terceros import privado
        for folder,target in [('models','BetterModel/models'),('mythicmobs/mobs','MythicMobs/mobs'),('mythicmobs/skills','MythicMobs/skills')]:
            for base in (ROOT,privado()):
                for p in (base/'build'/folder).glob('*'):
                    if p.is_file():shutil.copy2(p,server/'plugins'/target/p.name)
        shutil.copy2(ROOT/'build/AstralRPG-Items.zip',server/'prueba/datapacks/AstralRPG-Items.zip')
    log=work/('corregido.log' if install else 'repro.log')
    with log.open('w',encoding='utf8') as out:
        p=subprocess.Popen([str(java),'-Dterminal.jline=false','-Dterminal.ansi=false','-Xms512M','-Xmx2G','-jar','paper.jar','--nogui'],cwd=server,stdin=subprocess.PIPE,stdout=out,stderr=subprocess.STDOUT,text=True)
        def cmd(c):p.stdin.write(c+'\n');p.stdin.flush()
        try:
            for _ in range(180):
                if 'For help, type' in log.read_text(encoding='utf8',errors='replace'):break
                if p.poll()!=None:raise RuntimeError('Paper termino antes del arranque: '+str(log))
                time.sleep(1)
            else:raise TimeoutError('Paper no arranco')
            cmd('urgenteprobe player');time.sleep(2);cmd('urgenteprobe vars');time.sleep(1)
            import sys
            sys.path.insert(0,str(ROOT/'datapack-src'))
            from mobs.mascotas import MASCOTAS
            for pid,d in MASCOTAS.items():
                if not all_pets and pid!='lobo':continue
                cmd(f'urgenteprobe pet {pid} {d["n"]}');time.sleep(14)
            if install:
                for mid in ['esq_arquero','esq_escudero','esq_nigromante','esq_guardian','creeper_nuclear',
                            'bosque_planta','goblin','abejorro','yeti','momia','golem_forja','mina_guardian']:
                    cmd('urgenteprobe death astral_'+mid);time.sleep(3)
            if install:cmd('urgenteprobe progress');time.sleep(2)
            cmd('urgenteprobe result');time.sleep(1)
        finally:
            if p.poll()==None:cmd('stop');p.wait(timeout=60)
    content=log.read_text(encoding='utf8',errors='replace')
    print('\n'.join(l for l in content.splitlines() if 'URGENTE' in l or 'ERROR' in l))
    print('Log privado:',log)
    if install and ('URGENTE RESULT failures=0' not in content or 'URGENTE FAIL ' in content
                    or 'Cannot parse this datapoint' in content or 'Error has been occurred while parsing' in content):
        raise AssertionError('Fallo una prueba real; revisar '+str(log))


if __name__=='__main__':
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('--java',type=Path,required=True);a.add_argument('--server',type=Path,required=True)
    a.add_argument('--all-pets',action='store_true');a.add_argument('--install',action='store_true')
    args=a.parse_args();run(args.java.resolve(),args.server.resolve(),args.all_pets,args.install)
