"""Compilar solo AstralDuelos; no modifica los otros runtimes ni el pack."""
import argparse
import os
from pathlib import Path
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def build(java, server, duels):
    target = ROOT / '.local/duelos-ui-classes'
    target.mkdir(parents=True, exist_ok=True)
    deps = list((server / 'libraries').rglob('*.jar')) + [duels]
    # Copias nuevas: algunos JAR historicos tienen ACL incompatibles con Java en Windows.
    copies = ROOT / '.local/duelos-ui-deps'
    copies.mkdir(parents=True, exist_ok=True)
    import shutil
    local = []
    for i, dep in enumerate(deps):
        dest = copies / f'{i}-{dep.name}'
        shutil.copyfile(dep, dest)
        local.append(dest)
    subprocess.run([str(java), '-m', 'jdk.compiler/com.sun.tools.javac.Main', '-encoding', 'UTF-8',
        '-classpath', os.pathsep.join(map(str, local)), '-d', str(target),
        str(ROOT / 'datapack-src/runtime/AstralDuelos.java')], check=True)
    dest = ROOT / 'build/runtime/AstralDuelos.jar'
    with zipfile.ZipFile(dest, 'w', zipfile.ZIP_DEFLATED) as z:
        for p in sorted((target / 'astral').glob('AstralDuelos*.class')):
            z.writestr(zipfile.ZipInfo('astral/' + p.name, (2026, 11, 17, 0, 0, 0)), p.read_bytes())
        z.writestr(zipfile.ZipInfo('plugin.yml', (2026, 11, 17, 0, 0, 0)),
            "name: AstralDuelos\nversion: 1.1.0\nmain: astral.AstralDuelos\napi-version: '26.1.2'\ndepend: [Duels]\ncommands:\n  duelos: {}\n  desafiar: {}\n")
        import duelos_party_ui   # titulos (glifos) de las ventanas ilustradas de Gemini
        z.writestr(zipfile.ZipInfo('titulos-ui.properties', (2026, 11, 18, 0, 0, 0)), duelos_party_ui.titles_properties())
    return dest


if __name__ == '__main__':
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument('--java', type=Path, required=True)
    a.add_argument('--server', type=Path, required=True)
    a.add_argument('--duels', type=Path, default=ROOT / '.local/duels/Duels-Optimised-8.3.jar')
    args = a.parse_args()
    print(build(args.java.resolve(), args.server.resolve(), args.duels.resolve()))
