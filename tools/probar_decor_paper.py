"""Pruebas con Paper real y jugador NMS simulado; nunca instalar DecorProbe en remoto."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import time
import zipfile
import yaml

ROOT=Path(__file__).resolve().parents[1]


def run(java,server):
    if not server.is_relative_to(ROOT/'.local'):
        raise ValueError('Solo Paper local dentro de .local')
    work=ROOT/'.local/decor-probe';work.mkdir(exist_ok=True)
    delivery=ROOT/'.local/terceros/AstralRPG-privado/build/entregas/yeti-bastones-guia'
    # Instalar exactamente la entrega conjunta en el Paper local, nunca en remoto.
    for kind in ('mobs','skills'):
        shutil.copy2(delivery/f'mythicmobs/{kind}/astral.yml',server/f'plugins/MythicMobs/{kind}/astral.yml')
        for name in ('mazmorra','bosque','tumba','cumbre','forja','tanda3a','tanda3b'):
            source=ROOT/f'build/mythicmobs/{kind}/{name}.yml'
            if source.exists():shutil.copy2(source,server/f'plugins/MythicMobs/{kind}/{name}.yml')
    shutil.copy2(ROOT/'build/AstralRPG-Items.zip',server/'prueba/datapacks/AstralRPG-Items.zip')
    deps=[*server.joinpath('libraries').rglob('*.jar'),*server.joinpath('versions').rglob('*.jar'),
          server/'plugins/mythicmobs.jar',server/'plugins/bettermodel.jar',server/'plugins/worldguard.jar',server/'plugins/worldedit.jar']
    subprocess.run([str(java),'-m','jdk.compiler/com.sun.tools.javac.Main','-encoding','UTF-8',
        '-classpath',os.pathsep.join(map(str,deps)),'-d',str(work),str(ROOT/'datapack-src/test_runtime/DecorProbe.java')],check=True)
    with zipfile.ZipFile(server/'plugins/DecorProbe.jar','w') as z:
        for p in work.joinpath('astraltest').glob('DecorProbe*.class'):z.write(p,'astraltest/'+p.name)
        z.writestr('plugin.yml',"name: DecorProbe\nversion: 1\nmain: astraltest.DecorProbe\napi-version: '26.1.2'\ndepend: [BetterModel, MythicMobs, AstralDecor, WorldGuard]\ncommands:\n  decorprobe: {}\n")
        import sys
        sys.path.insert(0,str(ROOT/'datapack-src'))
        from mobs.tamanos import dimensions
        heights=[1.95,dimensions('astral_esq_arquero',1)[1],10,.4,.5,
                 dimensions('astral_momia',2)[1],dimensions('astral_golem_forja',2)[1],
                 dimensions('astral_coloso_musgoso',2)[1],7]
        z.writestr('config.yml',yaml.safe_dump({'probe-heights':heights}))
    shutil.copy2(ROOT/'build/runtime/AstralDecor.jar',server/'plugins/AstralDecor.jar')
    # Config completa del runtime propio; no copiar configuraciones generales de pruebas al servidor.
    with zipfile.ZipFile(ROOT/'build/runtime/AstralDecor.jar') as z:
        cfg=server/'plugins/AstralDecor/config.yml';cfg.parent.mkdir(exist_ok=True);cfg.write_bytes(z.read('config.yml'))
    for sub in ('mobs','skills'):
        shutil.copy2(ROOT/f'build/mythicmobs/{sub}/tanda3c.yml',server/f'plugins/MythicMobs/{sub}/tanda3c.yml')
    shutil.copy2(ROOT/'build/models/astral_npc_comerciante.bbmodel',server/'plugins/BetterModel/models/astral_npc_comerciante.bbmodel')
    path=server/'plugins/MythicMobs/mobs/astral.yml'
    mobs=yaml.safe_load(path.read_text(encoding='utf8'))
    public=yaml.safe_load((ROOT/'build/mythicmobs/mobs/astral.yml').read_text(encoding='utf8'))
    mobs['astral_npc_tienda']=public['astral_npc_tienda'];path.write_text(yaml.safe_dump(mobs,sort_keys=False,allow_unicode=True),encoding='utf8')
    (server/'plugins/MythicMobs/skills/decor_probe.yml').write_text('AST_VENDEDOR_PRIVADO:\n  Skills:\n  - model{m=astral_vendedor} @self\n',encoding='utf8')
    for stage in ('primero','reinicio'):
        log=work/(stage+'.log')
        with log.open('w',encoding='utf8') as out:
            p=subprocess.Popen([str(java),'-Dterminal.jline=false','-Dterminal.ansi=false','-Xms512M','-Xmx2G','-jar','paper.jar','--nogui'],cwd=server,stdin=subprocess.PIPE,stdout=out,stderr=subprocess.STDOUT,text=True)
            def cmd(c):p.stdin.write(c+'\n');p.stdin.flush()
            try:
                for _ in range(180):
                    if 'For help, type' in log.read_text(encoding='utf8',errors='replace'):break
                    if p.poll() is not None:raise RuntimeError('Paper termino antes del arranque: '+str(log))
                    time.sleep(1)
                else:raise TimeoutError('Paper no arranco')
                if stage=='primero':
                    for c,wait in [('player',2),('npc',5),('wings',3),('combat',4),('plush',2),('result',1)]:
                        cmd('decorprobe '+c);time.sleep(wait)
                else:
                    time.sleep(5);cmd('decorprobe restart');time.sleep(2);cmd('decorprobe result');time.sleep(1)
            finally:
                if p.poll() is None:cmd('stop');p.wait(timeout=60)
        content=log.read_text(encoding='utf8',errors='replace')
        print('\n'.join(l for l in content.splitlines() if 'DECOR' in l or 'ERROR' in l),flush=True)
        if 'DECOR RESULT failures=0' not in content or 'DECOR FAIL' in content:
            raise AssertionError('Fallo una prueba real; revisar '+str(log))


if __name__=='__main__':
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('--java',type=Path,required=True);a.add_argument('--server',type=Path,required=True)
    args=a.parse_args();run(args.java.resolve(),args.server.resolve())
