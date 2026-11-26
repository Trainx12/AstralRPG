# -*- coding: utf-8 -*-
"""AstralTamanos (23/11/2026): la caja de golpe de cada mob hostil con modelo 3D sigue al modelo.

BetterModel dibuja el modelo a (alto del .bbmodel) x (s de model{}) x (escala de la entidad); la caja vanilla solo crece
con la escala de la entidad. El plugin pone la escala de la entidad en FACTOR x alto visible y compensa el modelo para
que se vea igual (runtime/AstralTamanos.java). Pedido del dueno: caja "un poco menos de lo que es".

python tamanos_runtime.py --jdk <bin JDK 25> [--server .local/testsrv]  ->  build/tamanos/AstralTamanos.jar
Subir a /plugins y reiniciar. `/tamanos` muestra cuantos ajusto; `/tamanos recargar` relee config y modelos.
"""
import argparse
import os
import subprocess
import zipfile
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = ROOT / 'build' / 'tamanos'
VERSION = '1.0.0'
STAMP = (2026, 11, 23, 0, 0, 0)
FACTOR = 0.9
EXCLUIR = ['astral_pet_', 'astral_npc_', 'astral_cofre_', 'astral_maquina_', 'astral_invocacion', 'astral_fx_',
           'astral_vendedor', 'astral_poses']
MUNDOS_EXCLUIDOS = ['santuario']   # como tamanos.skills(protect_sanctuary): el Santuario no escala

PLUGIN_YML = f"""name: AstralTamanos
version: {VERSION}
main: astral.AstralTamanos
api-version: '26.1.2'
depend: [BetterModel]
commands:
  tamanos:
    description: Cajas de golpe de los mobs 3D (recargar)
    permission: astral.tamanos.admin
permissions:
  astral.tamanos.admin:
    default: op
"""


def config():
    return {'factor': FACTOR, 'excluir-modelos': EXCLUIR, 'mundos-excluidos': MUNDOS_EXCLUIDOS}


def build(jdk, server):
    jdk, server = Path(jdk), Path(server)
    classes = ROOT / '.local' / 'tamanos-classes'
    classes.mkdir(parents=True, exist_ok=True)
    jars = list((server / 'libraries').rglob('*.jar')) + [server / 'plugins' / 'bettermodel.jar']
    javac = [str(jdk / ('java.exe' if os.name == 'nt' else 'java')), '-m', 'jdk.compiler/com.sun.tools.javac.Main']
    subprocess.run([*javac, '-encoding', 'UTF-8', '-source', '25', '-target', '25', '-nowarn', '-classpath',
                    os.pathsep.join(map(str, jars)), '-d', str(classes), str(HERE / 'runtime' / 'AstralTamanos.java')], check=True)
    OUT.mkdir(parents=True, exist_ok=True)
    dest = OUT / 'AstralTamanos.jar'
    with zipfile.ZipFile(dest, 'w', zipfile.ZIP_DEFLATED) as z:
        for p in sorted((classes / 'astral').glob('AstralTamanos*.class')):
            z.writestr(zipfile.ZipInfo(p.relative_to(classes).as_posix(), STAMP), p.read_bytes())
        z.writestr(zipfile.ZipInfo('plugin.yml', STAMP), PLUGIN_YML)
        z.writestr(zipfile.ZipInfo('config.yml', STAMP), yaml.safe_dump(config(), allow_unicode=True, sort_keys=False))
    return dest


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--jdk', required=True)
    ap.add_argument('--server', default=str(ROOT / '.local' / 'testsrv'))
    a = ap.parse_args()
    print(build(a.jdk, a.server))
