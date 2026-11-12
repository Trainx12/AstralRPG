"""Ensayo local de LynExp (mesa de encantamientos): lista los libros que ofrece. No toca el server.

python tools/probar_lynexp_paper.py --java <java25> --base .local/testsrv --jar .local/lynexp/LynExp-1.0.0-mc26.1-26.1.2.jar
"""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def run(java, base, jar):
    work = ROOT/'.local/lynexp-probe'
    if work.exists():
        shutil.rmtree(work)
    srv = work/'srv'
    srv.mkdir(parents=True)
    for name in ('libraries', 'versions', 'cache'):
        shutil.copytree(base/name, srv/name)
    shutil.copy2(base/'paper.jar', srv/'paper.jar')
    (srv/'eula.txt').write_text('eula=true\n')
    (srv/'server.properties').write_text('server-ip=127.0.0.1\nserver-port=25609\nonline-mode=false\nlevel-name=world\n'
        'level-type=minecraft:flat\ngenerate-structures=false\nmanagement-server-enabled=false\n')
    packs = srv/'world/datapacks'
    packs.mkdir(parents=True)
    shutil.copy2(ROOT/'build/AstralRPG-Items.zip', packs/'AstralRPG-Items.zip')
    plugins = srv/'plugins'
    plugins.mkdir()
    shutil.copy2(jar, plugins/jar.name)
    deps = [*srv.joinpath('libraries').rglob('*.jar'), *srv.joinpath('versions').rglob('*.jar')]
    subprocess.run([str(java), '-m', 'jdk.compiler/com.sun.tools.javac.Main', '-encoding', 'UTF-8', '-classpath',
                    os.pathsep.join(map(str, deps)), '-d', str(work), str(ROOT/'datapack-src/test_runtime/LynProbe.java')], check=True)
    with zipfile.ZipFile(plugins/'LynProbe.jar', 'w') as z:
        z.write(work/'astraltest/LynProbe.class', 'astraltest/LynProbe.class')
        z.writestr('plugin.yml', "name: LynProbe\nversion: 1\nmain: astraltest.LynProbe\napi-version: '26.1.2'\ndepend: [LynExp]\n")
    log = work/'paper.log'
    with log.open('w', encoding='utf8') as out:
        subprocess.run([str(java), '-Xmx2G', '-jar', 'paper.jar', '--nogui'], cwd=srv, stdin=subprocess.DEVNULL,
                       stdout=out, stderr=subprocess.STDOUT, timeout=600)
    text = log.read_text(encoding='utf8', errors='replace')
    print('\n'.join(l for l in text.splitlines() if 'LYN' in l or 'LynExp' in l or 'Exception' in l))
    return text


if __name__ == '__main__':
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument('--java', type=Path, required=True)
    a.add_argument('--base', type=Path, required=True)
    a.add_argument('--jar', type=Path, required=True)
    args = a.parse_args()
    run(args.java.resolve(), args.base.resolve(), args.jar.resolve())
