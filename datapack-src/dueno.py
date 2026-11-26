"""AstralDueno (23/11/2026): /modo admin|jugador y /sala privada con shulkers de todos los items.

Solo para las UUID de DUENOS. Uso (desde la raiz o datapack-src):
    python datapack-src/dueno.py --jdk <bin de JDK 25>        -> build/dueno/AstralDueno.jar
La lista de items sale del datapack generado (build/AstralRPG-Items.zip: data/astral/loot_table/item/*.json);
los que el server no tenga se saltean solos.
"""
import argparse
import os
import subprocess
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = ROOT / 'build' / 'dueno'
# ByTrainx (cuenta offline del server: lp user ByTrainx info, 22/11/2026).
DUENOS = ['20e59728-e27a-35f1-9062-ab65fa0453b8']
STAMP = (2026, 11, 23, 0, 0, 0)

PLUGIN_YML = """name: AstralDueno
version: 1.0.0
main: astral.AstralDueno
api-version: '26.1.2'
description: Herramientas del dueno (modo admin/jugador y sala privada)
commands:
  modo:
    description: Cambia entre el perfil de admin y el de jugador
    usage: /modo [admin|jugador]
  sala:
    description: Sala privada del dueno con shulkers de todos los items
    usage: /sala [rellenar]
"""


def config_yml():
    return 'duenos:\n' + ''.join(f"- '{u}'\n" for u in DUENOS) + "mundo_inicio: lobby\n"


def items():
    z = zipfile.ZipFile(ROOT / 'build' / 'AstralRPG-Items.zip')
    pre = 'data/astral/loot_table/item/'
    return sorted(n[len(pre):-5] for n in z.namelist() if n.startswith(pre) and n.endswith('.json') and '/' not in n[len(pre):])


def build(jdk, server):
    jdk, server = Path(jdk), Path(server)
    classes = ROOT / '.local' / 'dueno-classes'
    classes.mkdir(parents=True, exist_ok=True)
    jars = list((server / 'libraries').rglob('*.jar'))
    javac = [str(jdk / ('java.exe' if os.name == 'nt' else 'java')), '-m', 'jdk.compiler/com.sun.tools.javac.Main']
    subprocess.run([*javac, '-encoding', 'UTF-8', '-source', '25', '-target', '25', '-classpath',
                    os.pathsep.join(map(str, jars)), '-d', str(classes), str(HERE / 'runtime' / 'AstralDueno.java')],
                   check=True)
    OUT.mkdir(parents=True, exist_ok=True)
    dest = OUT / 'AstralDueno.jar'
    with zipfile.ZipFile(dest, 'w', zipfile.ZIP_DEFLATED) as z:
        for p in sorted((classes / 'astral').glob('AstralDueno*.class')):
            z.writestr(zipfile.ZipInfo(p.relative_to(classes).as_posix(), STAMP), p.read_bytes())
        z.writestr(zipfile.ZipInfo('plugin.yml', STAMP), PLUGIN_YML)
        z.writestr(zipfile.ZipInfo('config.yml', STAMP), config_yml())
        z.writestr(zipfile.ZipInfo('items.txt', STAMP), '\n'.join(items()) + '\n')
    return dest


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--jdk', required=True)
    ap.add_argument('--server', default=str(ROOT / '.local' / 'testsrv'))
    a = ap.parse_args()
    print(build(a.jdk, a.server))
