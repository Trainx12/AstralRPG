# -*- coding: utf-8 -*-
"""AstralJefesInmunes (26/11/2026): a los jefes no se los puede envenenar, quemar, congelar ni ponerles efectos malos.

Jefe = MythicMob con barra de jefe, etiquetas de jefe (ETIQUETAS) o jefe vanilla. Los efectos buenos que el jefe se pone
con sus habilidades siguen. Ver runtime/AstralJefesInmunes.java.

python jefes_inmunes.py --jdk <bin JDK 25> [--server .local/testsrv]  ->  build/jefes/AstralJefesInmunes.jar
Subir a /plugins y reiniciar. ABIERTO A TODOS desde 26/11 (publico: false = solo jefes cerca de ByTrainx).
Tambien saca el congelamiento del Aspecto de Hielo al golpe y marca astral.sinestados (AstralClases: sin veneno del Asesino).
`/jefesinmunes` muestra el estado; `/jefesinmunes publico si` lo abre a todos (solo con OK del dueno).
"""
import argparse
import os
import subprocess
import zipfile
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = ROOT / 'build' / 'jefes'
VERSION = '1.1.0'
STAMP = (2026, 11, 26, 0, 0, 0)
ETIQUETAS = ['ad.boss.scaled', 'cav.jefe', 'nave.jefe', 'fosa.jefe']
PROBADORES = ['ByTrainx']
PUBLICO = True   # 26/11: el dueno pidio abrirlo a todos

PLUGIN_YML = f"""name: AstralJefesInmunes
version: {VERSION}
main: astral.AstralJefesInmunes
api-version: '26.1.2'
softdepend: [MythicMobs]
commands:
  jefesinmunes:
    description: Jefes sin veneno, fuego, congelamiento ni efectos malos
    permission: astral.jefesinmunes.admin
permissions:
  astral.jefesinmunes.admin:
    default: op
"""


def config():
    return {'publico': PUBLICO, 'probadores': PROBADORES, 'etiquetas-jefe': ETIQUETAS}


def build(jdk, server):
    jdk, server = Path(jdk), Path(server)
    classes = ROOT / '.local' / 'jefes-classes'
    classes.mkdir(parents=True, exist_ok=True)
    jars = list((server / 'libraries').rglob('*.jar')) + [server / 'plugins' / 'mythicmobs.jar']
    javac = [str(jdk / ('java.exe' if os.name == 'nt' else 'java')), '-m', 'jdk.compiler/com.sun.tools.javac.Main']
    subprocess.run([*javac, '-encoding', 'UTF-8', '-source', '25', '-target', '25', '-nowarn', '-classpath',
                    os.pathsep.join(map(str, jars)), '-d', str(classes),
                    str(HERE / 'runtime' / 'AstralJefesInmunes.java')], check=True)
    OUT.mkdir(parents=True, exist_ok=True)
    dest = OUT / 'AstralJefesInmunes.jar'
    with zipfile.ZipFile(dest, 'w', zipfile.ZIP_DEFLATED) as z:
        for p in sorted((classes / 'astral').glob('AstralJefesInmunes*.class')):
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
