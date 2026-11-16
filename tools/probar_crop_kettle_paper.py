"""Paper aislado: baseline, CNK+Astral+Skript+MythicMobs, olla y cultivo real.

Los logs, datos de terceros y plugin de prueba permanecen en .local.
"""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'datapack-src'))
from terceros import privado


def run(java, base, work):
    server = work / 'paper'
    server.mkdir(parents=True, exist_ok=True)
    for name in ('libraries', 'versions', 'cache'):
        if not (server / name).exists():
            shutil.copytree(base / name, server / name)
    shutil.copy2(base / 'paper.jar', server / 'paper.jar')
    (server / 'eula.txt').write_text('eula=true\n')
    (server / 'server.properties').write_text(
        'server-ip=127.0.0.1\nserver-port=25596\nonline-mode=false\nlevel-name=survival\n'
        'level-type=minecraft:flat\ngenerator-settings={"layers":[{"block":"minecraft:bedrock","height":1}],"biome":"minecraft:plains"}\n'
        'generate-structures=false\nspawn-protection=0\nmanagement-server-enabled=false\nview-distance=3\nsimulation-distance=3\n')
    plugins = server / 'plugins'
    plugins.mkdir(exist_ok=True)
    for name in ('mythicmobs', 'bettermodel', 'nightcore', 'excellentenchants', 'packetevents', 'skript'):
        shutil.copy2(base / 'plugins' / (name + '.jar'), plugins / (name + '.jar'))
    shutil.copytree(base / 'plugins/BetterModel/models', plugins / 'BetterModel/models', dirs_exist_ok=True)
    shutil.copy2(base / 'plugins/BetterModel/config.yml', plugins / 'BetterModel/config.yml')
    for sub in ('mobs', 'skills', 'randomspawns'):
        dest = plugins / 'MythicMobs' / sub
        dest.mkdir(parents=True, exist_ok=True)
        for path in (ROOT / 'build/mythicmobs' / sub).glob('*.yml'):
            shutil.copy2(path, dest / path.name)
    scripts = plugins / 'Skript/scripts'
    scripts.mkdir(parents=True, exist_ok=True)
    for src in ('build/gameplay/astral_armas_especiales.sk', 'build/mazmorras/astral_mazmorras_copias.sk', 'build/infinita/astral_infinita.sk'):
        shutil.copy2(ROOT / src, scripts / Path(src).name)
    packs = server / 'survival/datapacks'
    packs.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / 'build/AstralRPG-Items.zip', packs / 'AstralRPG-Items.zip')
    deps = [*server.joinpath('libraries').rglob('*.jar'), *server.joinpath('versions').rglob('*.jar')]
    subprocess.run([str(java), '-m', 'jdk.compiler/com.sun.tools.javac.Main', '-encoding', 'UTF-8',
                    '-classpath', os.pathsep.join(map(str, deps)), '-d', str(work),
                    str(ROOT / 'datapack-src/test_runtime/CropKettleProbe.java')], check=True)
    with zipfile.ZipFile(plugins / 'CropKettleProbe.jar', 'w') as z:
        for path in work.joinpath('astraltest').glob('CropKettleProbe*.class'):
            z.write(path, 'astraltest/' + path.name)
        z.writestr('plugin.yml', "name: CropKettleProbe\nversion: 1\nmain: astraltest.CropKettleProbe\napi-version: '26.1.2'\ncommands:\n  cnkprobe: {}\n")
    target = packs / 'CropAndKettle-Astral.zip'
    if target.exists():
        raise RuntimeError('Usar un directorio de prueba nuevo; no se borra un ensayo previo')
    for cycle in ('baseline', 'cnk'):
        if cycle == 'cnk':
            shutil.copy2(privado() / 'build/entregas/crop-kettle/CropAndKettle-Astral.zip', target)
        log = work / (cycle + '.log')
        with log.open('w', encoding='utf8') as out:
            process = subprocess.Popen([str(java), '-Xms512M', '-Xmx2G', '-jar', 'paper.jar', '--nogui'], cwd=server,
                                       stdin=subprocess.PIPE, stdout=out, stderr=subprocess.STDOUT, text=True)
            def cmd(text):
                process.stdin.write(text + '\n')
                process.stdin.flush()
            try:
                for _ in range(180):
                    text = log.read_text('utf8', errors='replace')
                    if 'For help, type' in text:
                        break
                    if process.poll() is not None:
                        raise RuntimeError('Paper termino: ' + str(log))
                    time.sleep(1)
                else:
                    raise TimeoutError('Paper no arranco')
                cmd('cnkprobe player')
                time.sleep(15)
                cmd('mspt')
                if cycle == 'cnk':
                    cmd('datapack list enabled')
                    cmd('cnkprobe setup')
                    time.sleep(16)
                    cmd('cnkprobe check')
                    time.sleep(10)
                    cmd('mspt')
                    cmd('cnkprobe cost')
                    time.sleep(3)
            finally:
                if process.poll() is None:
                    cmd('stop')
                    process.wait(timeout=60)
        content = log.read_text('utf8', errors='replace')
        print('\n'.join(line for line in content.splitlines() if any(x in line for x in ('CNK ', 'ERROR', 'tick times', 'CNK cost'))), flush=True)
        if cycle == 'cnk' and ('CNK RESULT failures=0' not in content or 'CNK FAIL' in content):
            raise AssertionError('Fallo del ensayo: ' + str(log))
        if any(x in content for x in ('Failed to load function', 'Failed to parse', "Couldn't parse", 'Error loading')):
            raise AssertionError('Error de carga: ' + str(log))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--java', type=Path, required=True)
    parser.add_argument('--base', type=Path, required=True)
    parser.add_argument('--work', type=Path, default=ROOT / '.local/crop-kettle-probe')
    args = parser.parse_args()
    run(args.java.resolve(), args.base.resolve(), args.work.resolve())
