"""Prueba recetas en Paper aislado, incluida colocacion desde el libro y quick move NMS."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import time
import zipfile
import yaml

ROOT = Path(__file__).resolve().parents[1]


def run(java, base):
    work = ROOT / '.local/recetas-probe'
    server = work / 'paper'
    server.mkdir(parents=True, exist_ok=True)
    for name in ('libraries', 'versions', 'cache'):
        if not (server / name).exists():
            shutil.copytree(base / name, server / name)
    shutil.copy2(base / 'paper.jar', server / 'paper.jar')
    (server / 'eula.txt').write_text('eula=true\n')
    (server / 'server.properties').write_text('server-ip=127.0.0.1\nserver-port=25597\nonline-mode=false\nlevel-name=probe\nlevel-type=minecraft:flat\ngenerator-settings={"layers":[{"block":"minecraft:bedrock","height":1}],"biome":"minecraft:plains"}\ngenerate-structures=false\nspawn-protection=0\nmanagement-server-enabled=false\n')
    plugins = server / 'plugins'
    plugins.mkdir(exist_ok=True)
    shutil.copy2(ROOT / 'build/runtime/AstralDecor.jar', plugins / 'AstralDecor.jar')
    for name in ('nightcore.jar', 'excellentenchants.jar', 'packetevents.jar', 'auraskills.jar'):
        shutil.copy2(base / 'plugins' / name, plugins / name)
    if not (plugins / 'AuraSkills').exists():
        shutil.copytree(base / 'plugins/AuraSkills', plugins / 'AuraSkills')
    config_path = plugins / 'AuraSkills/config.yml'
    config = yaml.safe_load(config_path.read_text(encoding='utf8'))
    config['action_bar']['enabled'] = False  # El jugador simulado no tiene canal PacketEvents.
    config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding='utf8')
    packs = server / 'probe/datapacks'
    packs.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / 'build/AstralRPG-Items.zip', packs / 'AstralRPG-Items.zip')
    deps = [*server.joinpath('libraries').rglob('*.jar'), *server.joinpath('versions').rglob('*.jar'), plugins / 'auraskills.jar']
    subprocess.run([str(java), '-m', 'jdk.compiler/com.sun.tools.javac.Main', '-encoding', 'UTF-8',
                    '-classpath', os.pathsep.join(map(str, deps)), '-d', str(work), str(ROOT / 'datapack-src/test_runtime/TableProbe.java')], check=True)
    with zipfile.ZipFile(plugins / 'TableProbe.jar', 'w') as z:
        for p in (work / 'astraltest').glob('TableProbe*.class'):
            z.write(p, 'astraltest/' + p.name)
        z.writestr('plugin.yml', "name: TableProbe\nversion: 1\nmain: astraltest.TableProbe\napi-version: '26.1.2'\ndepend: [AstralDecor, AuraSkills]\ncommands:\n  tableprobe: {}\n")
    for cycle in (1, 2):
        log = work / f'paper-{cycle}.log'
        with log.open('w', encoding='utf8') as out:
            process = subprocess.Popen([str(java), '-Xms512M', '-Xmx2G', '-jar', 'paper.jar', '--nogui'], cwd=server,
                                       stdin=subprocess.PIPE, stdout=out, stderr=subprocess.STDOUT, text=True)
            def cmd(c):
                process.stdin.write(c + '\n')
                process.stdin.flush()
            try:
                for _ in range(180):
                    if 'For help, type' in log.read_text(encoding='utf8', errors='replace'):
                        break
                    if process.poll() is not None:
                        raise RuntimeError('Paper termino; ver ' + str(log))
                    time.sleep(1)
                else:
                    raise TimeoutError('Paper no arranco')
                for step in ('start', 'exact', 'level', 'vanilla', 'shift', 'book', 'migration', 'forge', 'forgecheck', 'result'):
                    cmd('tableprobe ' + step)
                    time.sleep(3)
            finally:
                if process.poll() is None:
                    cmd('stop')
                    process.wait(timeout=60)
        content = log.read_text(encoding='utf8', errors='replace')
        print('\n'.join(l for l in content.splitlines() if 'TABLE' in l or 'ERROR' in l or 'recetas exactas' in l), flush=True)
        if 'TABLE RESULT failures=0' not in content or 'TABLE FAIL' in content:
            raise AssertionError('Fallo: ' + str(log))
        if 'Failed to load' in content or 'Error loading' in content:
            raise AssertionError('Fallo carga datapack: ' + str(log))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--java', type=Path, required=True)
    parser.add_argument('--base', type=Path, required=True)
    args = parser.parse_args()
    run(args.java.resolve(), args.base.resolve())
