"""Compila AstralProgression y genera la entrega aislada de balance de mobs."""
import argparse
import os
from pathlib import Path
import re
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
VERSION = '1.6.3'
STAMP = (2026, 11, 27, 0, 0, 0)


def build(java, server, jar_only=False):
    from skill_tiers import generate as generate_skill_tiers
    generate_skill_tiers()
    from minijuegos import parkour_worlds
    target = ROOT / '.local/slimes-classes'
    target.mkdir(parents=True, exist_ok=True)
    jars = list((server/'libraries').rglob('*.jar')) + list((server/'versions').rglob('*.jar'))
    jars += [ROOT/'.local/asw-native/server/plugins/auraskills.jar',
             ROOT/'.local/asw-native/server/plugins/mythicmobs.jar', ROOT/'.local/tanda5a/GriefPrevention.jar']
    args = ['-encoding', 'UTF-8', '-classpath', os.pathsep.join(map(str, jars)), '-d', str(target),
            str(ROOT/'datapack-src/runtime/AstralProgression.java')]
    argfile = target/'compile.args'
    argfile.write_text('\n'.join('"'+s.replace('\\','/')+'"' for s in args))
    subprocess.run([str(java), '-m', 'jdk.compiler/com.sun.tools.javac.Main', '@'+str(argfile)], check=True)
    jar = ROOT/'build/runtime/AstralProgression.jar'
    with zipfile.ZipFile(jar) as z:
        files = {n:z.read(n) for n in z.namelist() if not n.endswith('.class')}
    files['plugin.yml'] = re.sub(rb'(?m)^version: .*$', b'version: '+VERSION.encode(), files['plugin.yml'])
    files['split-excluded-worlds.txt'] = ('\n'.join(parkour_worlds())+'\n').encode()
    for p in (target/'astral').glob('AstralProgression*.class'):
        files[p.relative_to(target).as_posix()] = p.read_bytes()
    with zipfile.ZipFile(jar, 'w', zipfile.ZIP_DEFLATED) as z:
        for name, data in sorted(files.items()):
            z.writestr(zipfile.ZipInfo(name, STAMP), data)
    if jar_only:
        return jar
    from deploy_balance_mobs import generate
    generate()
    return jar


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--java', type=Path, required=True)
    p.add_argument('--server', type=Path, required=True)
    p.add_argument('--jar-only', action='store_true', help='Compilar solo el plugin; no regenerar economia ni entrega historica')
    a = p.parse_args()
    build(a.java.resolve(), a.server.resolve(), a.jar_only)
