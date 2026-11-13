"""Ensayo local del Oceano Astral: genera el mundo con AstralOceano, mide aire, prueba reglas y dibuja el fondo.

python tools/probar_oceano_paper.py --java <java25> --base .local/testsrv [--radio 96] [--guardar]
--guardar copia las regiones generadas a .local/oceano-mundo/ (plantilla para subir al server).
"""
import argparse
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(java, base, radio, guardar):
    sys.stdout.reconfigure(errors='replace')
    work = ROOT / '.local/oceano-probe'
    if work.exists():
        shutil.rmtree(work)
    srv = work / 'srv'
    srv.mkdir(parents=True)
    for name in ('libraries', 'versions', 'cache'):
        shutil.copytree(base / name, srv / name)
    shutil.copy2(base / 'paper.jar', srv / 'paper.jar')
    (srv / 'eula.txt').write_text('eula=true\n')
    (srv / 'server.properties').write_text('server-ip=127.0.0.1\nserver-port=25611\nonline-mode=false\nlevel-name=world\n'
                                           'level-type=minecraft:flat\ngenerate-structures=false\nmanagement-server-enabled=false\n')
    packs = srv / 'world/datapacks'
    packs.mkdir(parents=True)
    shutil.copy2(ROOT / 'build/AstralRPG-Items.zip', packs / 'AstralRPG-Items.zip')
    plugins = srv / 'plugins'
    plugins.mkdir()
    shutil.copy2(ROOT / 'build/oceano/AstralOceano.jar', plugins / 'AstralOceano.jar')
    deps = [*srv.joinpath('libraries').rglob('*.jar'), *srv.joinpath('versions').rglob('*.jar')]
    subprocess.run([str(java), '-m', 'jdk.compiler/com.sun.tools.javac.Main', '-encoding', 'UTF-8', '-nowarn', '-classpath',
                    os.pathsep.join(map(str, deps)), '-d', str(work), str(ROOT / 'datapack-src/test_runtime/OceanoProbe.java')], check=True)
    with zipfile.ZipFile(plugins / 'OceanoProbe.jar', 'w') as z:
        z.write(work / 'astraltest/OceanoProbe.class', 'astraltest/OceanoProbe.class')
        z.writestr('plugin.yml', "name: OceanoProbe\nversion: 1\nmain: astraltest.OceanoProbe\napi-version: '26.1.2'\ndepend: [AstralOceano]\n")
    log = work / 'paper.log'
    with log.open('w', encoding='utf8') as out:
        subprocess.run([str(java), '-Xmx4G', f'-Doceano.radio={radio}', '-jar', 'paper.jar', '--nogui'], cwd=srv,
                       stdin=subprocess.DEVNULL, stdout=out, stderr=subprocess.STDOUT, timeout=3600)
    text = log.read_text(encoding='utf8', errors='replace')
    print('\n'.join(l for l in text.splitlines() if 'OCE ' in l or 'Exception' in l or 'ERROR' in l)[:6000])
    for img in ('oceano-fondo.png', 'oceano-corte.png'):
        if (srv / img).exists():
            (ROOT / 'build/previews').mkdir(parents=True, exist_ok=True)
            shutil.copy2(srv / img, ROOT / 'build/previews' / img)
    if guardar:
        world = next(p for p in srv.rglob('oceano') if (p / 'region').is_dir())
        dest = ROOT / '.local/oceano-mundo'
        if dest.exists():
            shutil.rmtree(dest)
        for sub in ('region', 'entities', 'poi'):
            if (world / sub).is_dir():
                shutil.copytree(world / sub, dest / sub)
        print('plantilla ->', dest, sum(f.stat().st_size for f in dest.rglob('*') if f.is_file()) // 1_000_000, 'MB')
    if 'OCE RESULT failures=0' not in text:
        raise SystemExit('fallo: ' + str(log))


if __name__ == '__main__':
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument('--java', type=Path, required=True)
    a.add_argument('--base', type=Path, required=True)
    a.add_argument('--radio', type=int, default=96)
    a.add_argument('--guardar', action='store_true')
    args = a.parse_args()
    run(args.java.resolve(), args.base.resolve(), args.radio, args.guardar)
