# -*- coding: utf-8 -*-
"""AstralEstadisticas (26/11/2026): al ganar una mazmorra, resumen en el chat de quien pego mas al jefe, quien mato
mas mobs, quien cayo menos y quien curo mas (Varita de Curacion).

Liviano: sin tareas repetidas, solo suma en un mapa cuando pasa un golpe o muere un mob, y solo en copias en curso.
Lo conectan astral_puntaje.sk (mazmorras_puntaje.py: `astralstats inicio|fin|muerte`) y AstralMesaMagia (curacion).
Ver runtime/AstralEstadisticas.java.

python estadisticas_mazmorra.py --jdk <bin JDK 25> [--server .local/testsrv]  ->  build/estadisticas/AstralEstadisticas.jar
Subir a /plugins y reiniciar. OCULTO (regla del dueno): publico: false = solo lo ve ByTrainx.
`/mazstats` estado, `/mazstats ver` en curso, `/mazstats publico si` lo abre a todos (solo con OK del dueno).
"""
import argparse
import os
import subprocess
import zipfile
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = ROOT / 'build' / 'estadisticas'
VERSION = '1.0.0'
STAMP = (2026, 11, 26, 0, 0, 0)
ETIQUETAS = ['ad.boss.scaled', 'cav.jefe', 'nave.jefe', 'fosa.jefe']   # igual que jefes_inmunes.py
PROBADORES = ['ByTrainx']
PUBLICO = False
DEMORA_TICKS = 100   # 5 s despues del cartel de "conquistada" y la nota

PLUGIN_YML = f"""name: AstralEstadisticas
version: {VERSION}
main: astral.AstralEstadisticas
api-version: '26.1.2'
softdepend: [MythicMobs]
commands:
  astralstats:
    description: Uso interno (consola) de las estadisticas de mazmorra
  mazstats:
    description: Estadisticas de mazmorra (admin)
    permission: astral.estadisticas.admin
permissions:
  astral.estadisticas.admin:
    default: op
"""


def config():
    return {'publico': PUBLICO, 'probadores': PROBADORES, 'etiquetas-jefe': ETIQUETAS, 'demora-ticks': DEMORA_TICKS}


def build(jdk, server):
    jdk, server = Path(jdk), Path(server)
    classes = ROOT / '.local' / 'estadisticas-classes'
    classes.mkdir(parents=True, exist_ok=True)
    jars = list((server / 'libraries').rglob('*.jar')) + [server / 'plugins' / 'mythicmobs.jar']
    javac = [str(jdk / ('java.exe' if os.name == 'nt' else 'java')), '-m', 'jdk.compiler/com.sun.tools.javac.Main']
    subprocess.run([*javac, '-encoding', 'UTF-8', '-source', '25', '-target', '25', '-nowarn', '-classpath',
                    os.pathsep.join(map(str, jars)), '-d', str(classes),
                    str(HERE / 'runtime' / 'AstralEstadisticas.java')], check=True)
    OUT.mkdir(parents=True, exist_ok=True)
    dest = OUT / 'AstralEstadisticas.jar'
    with zipfile.ZipFile(dest, 'w', zipfile.ZIP_DEFLATED) as z:
        for p in sorted((classes / 'astral').glob('AstralEstadisticas*.class')):
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
