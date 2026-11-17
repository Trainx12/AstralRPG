"""CrazyCrates real aislado: 1000 forceopen/mass-open por tabla, preview y pity por premio."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import zipfile
import yaml

ROOT = Path(__file__).resolve().parents[1]


def run(java, base, pity_only=False):
    sys.path.insert(0, str(ROOT/'datapack-src'))
    from lobby import GACHAS
    from gacha_balance import RARITY_WEIGHT
    work = ROOT/'.local/gacha-1711-probe'
    server = work/'paper'
    server.mkdir(parents=True, exist_ok=True)
    for name in ('libraries', 'versions', 'cache'):
        if not (server/name).exists():
            shutil.copytree(base/name, server/name)
    shutil.copy2(base/'paper.jar', server/'paper.jar')
    (server/'eula.txt').write_text('eula=true\n')
    (server/'server.properties').write_text('server-ip=127.0.0.1\nserver-port=25596\nonline-mode=false\nlevel-name=probe\nlevel-type=minecraft:flat\ngenerator-settings={"layers":[{"block":"minecraft:bedrock","height":1}],"biome":"minecraft:plains"}\ngenerate-structures=false\nspawn-protection=0\nmanagement-server-enabled=false\nview-distance=2\nsimulation-distance=2\nmax-tick-time=-1\n')
    plugins = server/'plugins'
    plugins.mkdir(exist_ok=True)
    shutil.copy2(ROOT/'build/runtime/AstralDecor.jar', plugins/'AstralDecor.jar')
    for name in ('mythicmobs','bettermodel','nightcore','excellentenchants','packetevents'):
        shutil.copy2(base/'plugins'/f'{name}.jar', plugins/f'{name}.jar')
    packs=server/'probe/datapacks'
    packs.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT/'build/AstralRPG-Items.zip', packs/'AstralRPG-Items.zip')
    shutil.copy2(base/'plugins/skript.jar', plugins/'skript.jar')
    scripts=plugins/'Skript/scripts'
    scripts.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT/'build/gameplay/astral_gameplay.sk', scripts/'astral_gameplay.sk')
    shutil.copy2(ROOT/'.local/crazycrates-server/CrazyCrates-26.1.2-560610d.jar', plugins/'CrazyCrates.jar')
    cc = plugins/'CrazyCrates'
    cc.mkdir(exist_ok=True)
    shutil.copy2(ROOT/'.local/crazycrates-server/config-sin-menu.yml', cc/'config.yml')
    crates = cc/'crates'
    crates.mkdir(exist_ok=True)
    for source in (ROOT/'build/lobby/CrazyCrates/crates').glob('*.yml'):
        data = yaml.safe_load(source.read_text('utf8'))
        gid = next(g for g in GACHAS if source.stem.startswith(g))
        g = GACHAS[gid]
        rewards = sorted(g['rewards'](), key=lambda r: list(g.get('rarity_weight', RARITY_WEIGHT)).index(r[0]), reverse=True)
        if '_garantia' in source.stem:
            rewards = [r for r in rewards if r[0] in ('epic', 'legendary')]
        for reward, prize in zip(rewards, data['Crate']['Prizes'].values(), strict=True):
            prize['Commands'] = [f'gachaprobe reward {gid} {reward[0]} {source.stem}'] + [c for c in prize['Commands'] if c.startswith(('scoreboard ', 'astralgacha '))]
        (crates/source.name).write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), 'utf8')
    deps = [*server.joinpath('libraries').rglob('*.jar'), *server.joinpath('versions').rglob('*.jar'), plugins/'CrazyCrates.jar']
    subprocess.run([str(java), '-m', 'jdk.compiler/com.sun.tools.javac.Main', '-encoding', 'UTF-8', '-classpath', os.pathsep.join(map(str, deps)), '-d', str(work), str(ROOT/'datapack-src/test_runtime/GachaProbe.java')], check=True)
    with zipfile.ZipFile(plugins/'GachaProbe.jar', 'w') as z:
        for p in work.joinpath('astraltest').glob('GachaProbe*.class'):
            z.write(p, 'astraltest/'+p.name)
        z.writestr('plugin.yml', "name: GachaProbe\nversion: 1\nmain: astraltest.GachaProbe\napi-version: '26.1.2'\ndepend: [AstralDecor, CrazyCrates]\ncommands:\n  gachaprobe: {}\n")
    log = work/('paper-pity.log' if pity_only else 'paper.log')
    with log.open('w', encoding='utf8') as out:
        p = subprocess.Popen([str(java), '-Xms512M', '-Xmx3G', '-jar', 'paper.jar', '--nogui'], cwd=server, stdin=subprocess.PIPE, stdout=out, stderr=subprocess.STDOUT, text=True)
        def cmd(c):
            p.stdin.write(c+'\n'); p.stdin.flush()
        try:
            for _ in range(180):
                if 'For help, type' in log.read_text('utf8', errors='replace'):
                    break
                if p.poll() is not None:
                    raise RuntimeError('Paper termino: '+str(log))
                time.sleep(1)
            else:
                raise TimeoutError('Paper no arranco')
            cmd('tick rate 10000')  # Acelera el reloj; CSGO conserva su animacion/seleccion reales.
            cmd('gachaprobe start'+(' pity' if pity_only else ''))
            for _ in range(1800):
                if p.poll() is not None:
                    raise RuntimeError('Paper termino durante el ensayo: '+str(log))
                if 'GACHA RESULT' in log.read_text('utf8', errors='replace'):
                    break
                time.sleep(1)
            else:
                raise TimeoutError('Ensayo sin finalizar: '+str(log))
        finally:
            if p.poll() is None:
                cmd('stop'); p.wait(timeout=60)
    content = log.read_text('utf8', errors='replace')
    print('\n'.join(l for l in content.splitlines() if 'GACHA COUNTS' in l or 'GACHA FAIL' in l or 'GACHA RESULT' in l))
    if 'GACHA RESULT failures=0' not in content or 'GACHA FAIL' in content or 'Encountered ' in content or 'Error occurred' in content or ' ERROR]' in content or 'All scripts loaded without errors.' not in content:
        raise AssertionError('Revisar '+str(log))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--java', type=Path, required=True)
    p.add_argument('--base', type=Path, required=True)
    p.add_argument('--pity-only', action='store_true', help='Repetir lotes/GUI con el JAR final sin repetir estadisticas')
    args = p.parse_args()
    run(args.java.resolve(), args.base.resolve(), args.pity_only)
