"""Paper aislado: FINAL auditado, items reales, modelos y ciclo de vida de efectos."""
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
from pack_audit import audit


def run(java, base, work, economy=None):
    audit(privado() / 'build/entregas/modelos-3d-efectos/AstralRPG-Textures.zip')
    server = work / 'paper'
    server.mkdir(parents=True, exist_ok=False)
    for name in ('libraries', 'versions', 'cache'):
        shutil.copytree(base / name, server / name, copy_function=os.link)
    shutil.copy2(base / 'paper.jar', server / 'paper.jar')
    (server / 'eula.txt').write_text('eula=true\n')
    (server / 'server.properties').write_text('server-ip=127.0.0.1\nserver-port=25593\nonline-mode=false\nlevel-name=probe\nlevel-type=minecraft:flat\ngenerator-settings={"layers":[{"block":"minecraft:bedrock","height":1}],"biome":"minecraft:plains"}\ngenerate-structures=false\nspawn-protection=0\nmanagement-server-enabled=false\n')
    (server / 'spigot.yml').write_text('settings:\n  attribute:\n    maxHealth:\n      max: 1.0E12\n    attackDamage:\n      max: 1.0E12\n')
    plugins = server / 'plugins'; plugins.mkdir()
    for name in ('bettermodel', 'mythicmobs', 'nightcore', 'excellentenchants', 'packetevents'):
        shutil.copy2(base / f'plugins/{name}.jar', plugins / f'{name}.jar')
    for name in ('AstralDecor', 'AstralEfectos'):
        shutil.copy2(ROOT / f'build/runtime/{name}.jar', plugins / f'{name}.jar')
    if economy:
        shutil.copy2(ROOT / '.local/deploy-16-11/EconomyShopGUI.jar', plugins / 'EconomyShopGUI.jar')
        shutil.copy2(base / 'plugins/Vault.jar', plugins / 'Vault.jar')
        shutil.copytree(economy, plugins / 'EconomyShopGUI')
    for sub in ('mobs', 'skills'):
        dest = plugins / 'MythicMobs' / sub; dest.mkdir(parents=True)
        for source in (ROOT / 'build/mythicmobs' / sub, privado() / 'build/entregas/modelos-3d-efectos/mythicmobs' / sub):
            for p in source.glob('*.yml'): shutil.copy2(p, dest / p.name)
    models = plugins / 'BetterModel/models'; models.mkdir(parents=True)
    for source in (ROOT / 'build/models', privado() / 'build/models', privado() / 'build/entregas/correcciones-goblin-golems/models', privado() / 'build/entregas/modelos-3d-efectos/models'):
        for p in source.glob('*.bbmodel'): shutil.copy2(p, models / p.name)
    shutil.copy2(ROOT / 'datapack-src/mobs/bettermodel_config.yml', plugins / 'BetterModel/config.yml')
    packs = server / 'probe/datapacks'; packs.mkdir(parents=True)
    shutil.copy2(ROOT / 'build/AstralRPG-Items.zip', packs / 'AstralRPG-Items.zip')
    if economy:
        shutil.copy2(privado() / 'build/entregas/crop-kettle/CropAndKettle-Astral.zip', packs / 'CropAndKettle-Astral.zip')
    deps = [*server.joinpath('libraries').rglob('*.jar'), *server.joinpath('versions').rglob('*.jar'), plugins / 'mythicmobs.jar']
    subprocess.run([str(java), '-m', 'jdk.compiler/com.sun.tools.javac.Main', '-encoding', 'UTF-8', '-classpath', os.pathsep.join(map(str,deps)), '-d', str(work), str(ROOT / 'datapack-src/test_runtime/ModelosEfectosProbe.java')], check=True)
    with zipfile.ZipFile(plugins / 'ModelosEfectosProbe.jar','w') as z:
        for p in work.joinpath('astraltest').glob('ModelosEfectosProbe*.class'): z.write(p, 'astraltest/' + p.name)
        z.writestr('plugin.yml', "name: ModelosEfectosProbe\nversion: 1\nmain: astraltest.ModelosEfectosProbe\napi-version: '26.1.2'\ndepend: [MythicMobs,BetterModel]\nsoftdepend: [Vault]\nloadbefore: [EconomyShopGUI]\ncommands:\n  modelosprobe: {}\n")
    log = work / 'paper.log'
    with log.open('w',encoding='utf8') as out:
        p = subprocess.Popen([str(java), '-Dastral.probe.economia='+str(bool(economy)).lower(), '-Xms512M', '-Xmx2G', '-jar', 'paper.jar', '--nogui'], cwd=server, stdin=subprocess.PIPE, stdout=out, stderr=subprocess.STDOUT, text=True)
        def cmd(value): p.stdin.write(value+'\n'); p.stdin.flush()
        try:
            for _ in range(180):
                if 'For help, type' in log.read_text('utf8', errors='replace'): break
                if p.poll() is not None: raise RuntimeError('Paper termino: '+str(log))
                time.sleep(1)
            else: raise TimeoutError('Paper no arranco')
            cmd('modelosprobe')
            time.sleep(8)
        finally:
            if p.poll() is None: cmd('stop'); p.wait(timeout=60)
    content = log.read_text('utf8',errors='replace')
    print('\n'.join(s for s in content.splitlines() if 'FX ' in s or 'ERROR' in s))
    if 'FX RESULT failures=0' not in content or any(s in content for s in ('FX FAIL','Error loading','Failed to load','Configuration Error','Could not find MetaSkill','Encountered ')):
        raise AssertionError('Revisar '+str(log))
    print('Log privado:',log)


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--java',type=Path,required=True)
    parser.add_argument('--base',type=Path,required=True)
    parser.add_argument('--work',type=Path,required=True)
    parser.add_argument('--economy-config',type=Path,help='Copia privada de EconomyShopGUI; usa .local/deploy-16-11/EconomyShopGUI.jar')
    args=parser.parse_args();run(args.java.resolve(),args.base.resolve(),args.work.resolve(),args.economy_config)
