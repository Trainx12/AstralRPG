"""Genera un plugin aislado: spawners sin XP vanilla, conservando XP de skills."""
import argparse
import os
from pathlib import Path
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = """name: AstralSpawnerXp
version: 1.0.0
main: astral.AstralSpawnerXp
api-version: '26.1.2'
softdepend: [AstralProgression, AuraSkills, MythicMobs]
"""


def build(java, server):
    classes = ROOT / '.local/spawner-xp/classes'
    classes.mkdir(parents=True, exist_ok=True)
    jars = sorted((server / 'libraries').rglob('*.jar'))
    args = ['-encoding', 'UTF-8', '-classpath', os.pathsep.join(map(str, jars)),
            '-d', str(classes), str(ROOT / 'datapack-src/runtime/AstralSpawnerXp.java')]
    argfile = classes.parent / 'compile.args'
    argfile.write_text('\n'.join('"' + s.replace('\\', '/') + '"' for s in args))
    subprocess.run([str(java), '-m', 'jdk.compiler/com.sun.tools.javac.Main', '@' + str(argfile)], check=True)
    dest = ROOT / 'build/spawner-xp/AstralSpawnerXp.jar'
    dest.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(dest, 'w', zipfile.ZIP_DEFLATED) as jar:
        for p in sorted((classes / 'astral').glob('AstralSpawnerXp*.class')):
            jar.writestr(zipfile.ZipInfo(p.relative_to(classes).as_posix(), (2026, 11, 27, 0, 0, 0)), p.read_bytes())
        jar.writestr(zipfile.ZipInfo('plugin.yml', (2026, 11, 27, 0, 0, 0)), PLUGIN)
    (dest.parent / 'instalacion.txt').write_text(
        'AstralSpawnerXp 1.0.0 - Solo orbes de experiencia vanilla\n'
        'Subir AstralSpawnerXp.jar a /plugins/AstralSpawnerXp.jar.\n'
        'Plugin nuevo: carga en el siguiente reinicio completo autorizado.\n'
        'No usar /reload ni carga dinamica de plugins. No modificar mundos.\n'
        'Verificar consola: Enabling AstralSpawnerXp v1.0.0 sin errores.\n'
        'SPAWNER y TRIAL_SPAWNER: cero XP vanilla; XP de skills segun\n'
        'AstralProgression/AuraSkills actuales (no cambia sus multiplicadores).\n'
        'Conversiones y divisiones sucesivas conservan el origen.\n'
        'Otros origenes y drops de items no se modifican.\n', encoding='utf8')
    return dest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--java', type=Path, required=True)
    parser.add_argument('--server', type=Path, default=ROOT / '.local/testsrv')
    args = parser.parse_args()
    print(build(args.java.resolve(), args.server.resolve()))
