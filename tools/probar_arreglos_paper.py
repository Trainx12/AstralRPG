"""Smoke local de los YAML y glow del modelo. Nunca se conecta al servidor remoto.

Requiere un Paper de pruebas existente, detenido, y JDK 25. No crea clientes ni
certifica la apariencia visual. El log y el plugin auxiliar quedan en .local.
"""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import time
import zipfile

ROOT=Path(__file__).resolve().parents[1]


def run(java,server):
    if not server.resolve().is_relative_to(ROOT/'.local'):
        raise ValueError('Solo se permite un servidor de prueba dentro de .local')
    work=ROOT/'.local/arreglos-probe';work.mkdir(parents=True,exist_ok=True)
    deps=[*server.joinpath('libraries').rglob('*.jar'),server/'plugins/bettermodel.jar']
    compiler=[str(java),'-m','jdk.compiler/com.sun.tools.javac.Main']
    subprocess.run([*compiler,'-encoding','UTF-8','-classpath',os.pathsep.join(map(str,deps)),
        '-d',str(work),str(ROOT/'datapack-src/test_runtime/ArreglosProbe.java')],check=True)
    with zipfile.ZipFile(server/'plugins/ArreglosProbe.jar','w') as z:
        z.write(work/'astraltest/ArreglosProbe.class','astraltest/ArreglosProbe.class')
        z.writestr('plugin.yml',"name: ArreglosProbe\nversion: 1.0\nmain: astraltest.ArreglosProbe\napi-version: '26.1.2'\ndepend: [BetterModel, MythicMobs]\ncommands:\n  astralprobe: {}\n")
    for p in (ROOT/'build/models').glob('*.bbmodel'):
        shutil.copy2(p,server/'plugins/BetterModel/models'/p.name)
    for sub in ('mobs','skills'):
        for p in (ROOT/'build/mythicmobs'/sub).glob('*.yml'):
            shutil.copy2(p,server/'plugins/MythicMobs'/sub/p.name)
    shutil.copy2(ROOT/'build/AstralRPG-Items.zip',server/'prueba/datapacks/AstralRPG-Items.zip')
    log=work/'paper.log'
    run_tag='arreglos.run.'+str(time.time_ns())
    with log.open('w',encoding='utf8') as out:
        process=subprocess.Popen([str(java),'-Dterminal.jline=false','-Dterminal.ansi=false','-Xms512M','-Xmx2G','-jar','paper.jar','--nogui'],cwd=server,stdin=subprocess.PIPE,stdout=out,stderr=subprocess.STDOUT,text=True)
        def command(text):process.stdin.write(text+'\n');process.stdin.flush()
        try:
            deadline=time.monotonic()+180
            while time.monotonic()<deadline:
                content=log.read_text(encoding='utf8',errors='replace')
                if 'For help, type' in content:break
                if process.poll() is not None:raise RuntimeError('Paper termino antes del arranque')
                time.sleep(1)
            else:raise TimeoutError('Paper no arranco')
            command('minecraft:kill @e[tag=arreglos.probe]')
            command('minecraft:gamerule advance_time false')
            command('minecraft:time set midnight')
            names=['astral_esq_arquero_bosque_sala1','astral_bosque_planta','astral_mina_guardian',
                   'astral_bosque_chaman','astral_tumba_momia','astral_cumbre_yeti','astral_forja_golem_forja',
                   'astral_esq_arquero','astral_planta_salvaje','astral_creeper_nuclear']
            for i,name in enumerate(names):
                x=1000+i*40
                command(f'minecraft:forceload add {x} 1000')
                time.sleep(.5)
                command(f'mm mobs spawn {name} 1 prueba,{x},-60,1000')
                time.sleep(.4)
                selector=f'@e[type=!minecraft:interaction,type=!minecraft:item_display,tag=!arreglos.probe,distance=..8]'
                command(f'execute positioned {x} -60 1000 run tag {selector} add {run_tag}')
                command(f'tag @e[tag={run_tag}] add arreglos.probe')
                if i<7:command(f'execute positioned {x} -60 1000 run tag @e[tag={run_tag},distance=..8] add arreglos.expected_glow')
            time.sleep(8);command('astralprobe '+run_tag);time.sleep(2)
            command(f'minecraft:kill @e[tag={run_tag}]')
            for i in range(len(names)):command(f'minecraft:forceload remove {1000+i*40} 1000')
        finally:
            if process.poll() is None:
                command('stop');process.wait(timeout=60)
    content=log.read_text(encoding='utf8',errors='replace')
    lines=[l for l in content.splitlines() if 'ARREGLOS_PROBE' in l]
    print('\n'.join(lines))
    if any('FAIL' in l for l in lines) or 'tested=10' not in '\n'.join(lines):
        raise AssertionError('Fallo la prueba real de displays; revisar '+str(log))
    print('Paper finalizo',process.returncode,'log privado:',log)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--java',type=Path,required=True)
    parser.add_argument('--server',type=Path,required=True)
    args=parser.parse_args();run(args.java.resolve(),args.server.resolve())
