"""Prueba aislada TrainCarts/Paper con jugadores NMS simulados. No toca remoto."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import time
import zipfile

ROOT=Path(__file__).resolve().parents[1]


def run(java,base,recovery_only=False):
    work=ROOT/'.local/tren-probe';server=work/'paper';server.mkdir(parents=True,exist_ok=True)
    for name in ('libraries','versions','cache'):
        if not (server/name).exists():shutil.copytree(base/name,server/name)
    shutil.copy2(base/'paper.jar',server/'paper.jar')
    (server/'eula.txt').write_text('eula=true\n')
    (server/'server.properties').write_text('server-ip=127.0.0.1\nserver-port=25597\nonline-mode=false\nlevel-name=world\nlevel-type=minecraft:flat\ngenerator-settings={"layers":[{"block":"minecraft:bedrock","height":1}],"biome":"minecraft:plains"}\ngenerate-structures=false\nspawn-protection=0\nmanagement-server-enabled=false\n')
    plugins=server/'plugins';plugins.mkdir(exist_ok=True)
    for name in ('traincarts','bkcommonlib'):shutil.copy2(ROOT/'.local/tren-deps'/f'{name}.jar',plugins/f'{name}.jar')
    shutil.copy2(ROOT/'build/tren/AstralTrain.jar',plugins/'AstralTrain.jar')
    (plugins/'AstralTrain').mkdir(exist_ok=True)
    shutil.copy2(ROOT/'build/tren/AstralTrain/train.yml',plugins/'AstralTrain/train.yml')
    if not recovery_only:shutil.copy2(ROOT/'build/tren/AstralTrain/config.yml',plugins/'AstralTrain/config.yml')
    deps=[*server.joinpath('libraries').rglob('*.jar'),*server.joinpath('versions').rglob('*.jar'),*plugins.glob('*.jar')]
    subprocess.run([str(java),'-m','jdk.compiler/com.sun.tools.javac.Main','-encoding','UTF-8',
        '-classpath',os.pathsep.join(map(str,deps)),'-d',str(work),str(ROOT/'datapack-src/test_runtime/TrainProbe.java')],check=True)
    with zipfile.ZipFile(plugins/'TrainProbe.jar','w') as z:
        for p in (work/'astraltest').glob('TrainProbe*.class'):z.write(p,'astraltest/'+p.name)
        z.writestr('plugin.yml',"name: TrainProbe\nversion: 1\nmain: astraltest.TrainProbe\napi-version: '26.1.2'\ndepend: [AstralTrain]\ncommands:\n  trainprobe: {}\n")

    def session(logname,steps,crash=False):
        log=work/logname
        with log.open('w',encoding='utf8') as out:
            process=subprocess.Popen([str(java),'-Xms512M','-Xmx2G','-jar','paper.jar','--nogui'],cwd=server,
                stdin=subprocess.PIPE,stdout=out,stderr=subprocess.STDOUT,text=True)
            def cmd(c):process.stdin.write(c+'\n');process.stdin.flush()
            try:
                for _ in range(180):
                    if 'For help, type' in log.read_text(encoding='utf8',errors='replace'):break
                    if process.poll() is not None:raise RuntimeError('Paper termino; ver '+str(log))
                    time.sleep(1)
                else:raise TimeoutError('Paper no arranco')
                time.sleep(4)
                cmd('spark health --memory');time.sleep(2)
                for step,delay in steps:cmd('trainprobe '+step);time.sleep(delay)
                if not crash:cmd('spark health --memory');time.sleep(2)
            finally:
                if process.poll() is None:
                    if crash:process.kill()
                    else:cmd('stop')
                    process.wait(timeout=60)
        text=log.read_text(encoding='utf8',errors='replace')
        print('\n'.join(l for l in text.splitlines() if 'TRAIN ' in l or 'ERROR' in l),flush=True)
        if 'TRAIN RESULT failures=0' not in text or 'TRAIN FAIL' in text:raise AssertionError('Fallo: '+str(log))
    if not recovery_only:
        session('paper.log',[('setup',4),('ready',1),('one',2),('countdown',8),('arrived',9),('back',1),
            ('three',2),('exit',9),('twoarrived',10),('three',10),('allarrived',10),('invalidbed',1),
            ('one',6),('outside',1),('result',1)])
    session('restart.log',[('recovered',2),('setup',4),('one',6),('persist',.2),('result',.2)],crash=True)
    session('crash-restart.log',[('recovered',2),('result',1)])


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--java',type=Path,required=True);p.add_argument('--base',type=Path,required=True)
    p.add_argument('--recovery-only',action='store_true')
    a=p.parse_args();run(a.java.resolve(),a.base.resolve(),a.recovery_only)
