"""Ensayo local de AstralMesa con ExcellentEnchants: lista lo que ofrece la mesa. No toca el server.

python tools/probar_mesa_paper.py --java <java25> --base .local/testsrv --jar build/mesa/AstralMesa.jar --ee .local/spam-paper-cs2dghr2/plugins
"""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def run(java, base, jar, ee):
    work = ROOT/'.local/mesa-probe'
    if work.exists():
        shutil.rmtree(work)
    srv = work/'srv'
    srv.mkdir(parents=True)
    for name in ('libraries', 'versions', 'cache'):
        shutil.copytree(base/name, srv/name)
    shutil.copy2(base/'paper.jar', srv/'paper.jar')
    (srv/'eula.txt').write_text('eula=true\n')
    (srv/'server.properties').write_text('server-ip=127.0.0.1\nserver-port=25611\nonline-mode=false\nlevel-name=world\n'
        'level-type=minecraft:flat\ngenerate-structures=false\nmanagement-server-enabled=false\n')
    packs = srv/'world/datapacks'
    packs.mkdir(parents=True)
    shutil.copy2(ROOT/'build/AstralRPG-Items.zip', packs/'AstralRPG-Items.zip')
    for z in (ROOT/'.local/dp-server').glob('*.zip'):  # datapacks del server con encantamientos (Stellarity, DnT)
        if 'Stellarity' in z.name or 'Dungeons and Taverns' in z.name:
            shutil.copy2(z, packs/z.name)
    plugins = srv/'plugins'
    plugins.mkdir()
    shutil.copy2(jar, plugins/jar.name)
    viejo = ROOT/'.local/mesa-config-server.yml'  # config.yml que ya tiene el server (de versiones viejas)
    if viejo.exists():
        (plugins/'AstralMesa').mkdir(exist_ok=True)
        shutil.copy2(viejo, plugins/'AstralMesa/config.yml')
    for n in ('excellentenchants.jar', 'nightcore.jar', 'packetevents.jar'):
        shutil.copy2(ee/n, plugins/n)
    trad = ROOT/'build/excellentenchants/enchants'
    if trad.exists():  # descripciones en espanol (ee_descripciones.py)
        shutil.copytree(trad, plugins/'ExcellentEnchants/enchants')
        if (trad.parent/'config.yml').exists():
            shutil.copy2(trad.parent/'config.yml', plugins/'ExcellentEnchants/config.yml')
    deps = [*srv.joinpath('libraries').rglob('*.jar'), *srv.joinpath('versions').rglob('*.jar')]
    subprocess.run([str(java), '-m', 'jdk.compiler/com.sun.tools.javac.Main', '-encoding', 'UTF-8', '-classpath',
                    os.pathsep.join(map(str, deps)), '-d', str(work), str(ROOT/'datapack-src/test_runtime/MesaProbe.java')], check=True)
    with zipfile.ZipFile(plugins/'MesaProbe.jar', 'w') as z:
        z.write(work/'astraltest/MesaProbe.class', 'astraltest/MesaProbe.class')
        z.writestr('plugin.yml', "name: MesaProbe\nversion: 1\nmain: astraltest.MesaProbe\napi-version: '26.1.2'\ndepend: [AstralMesa]\n")
    log = work/'paper.log'
    with log.open('w', encoding='utf8') as out:
        subprocess.run([str(java), '-Xmx2G', '-jar', 'paper.jar', '--nogui'], cwd=srv, stdin=subprocess.DEVNULL,
                       stdout=out, stderr=subprocess.STDOUT, timeout=600)
    text = log.read_text(encoding='utf8', errors='replace')
    print('\n'.join(l for l in text.splitlines() if 'MESA' in l or 'AstralMesa' in l or 'ExcellentEnchants' in l or 'Exception' in l))
    return text


if __name__ == '__main__':
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument('--java', type=Path, required=True)
    a.add_argument('--base', type=Path, required=True)
    a.add_argument('--jar', type=Path, required=True)
    a.add_argument('--ee', type=Path, required=True, help='carpeta con excellentenchants/nightcore/packetevents.jar')
    args = a.parse_args()
    run(args.java.resolve(), args.base.resolve(), args.jar.resolve(), args.ee.resolve())
