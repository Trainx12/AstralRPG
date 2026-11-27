"""Compila el ajuste de Combate de spawners sobre los recursos publicados.

No instala archivos ni reinicia el servidor. Conserva los recursos del JAR base.
"""
import argparse
import io
import os
from pathlib import Path
import subprocess
import zipfile
import yaml

ROOT = Path(__file__).resolve().parents[1]


def build(java, server, revision='HEAD'):
    def read(path):
        return subprocess.check_output(['git', 'show', f'{revision}:{path}'], cwd=ROOT)
    work = ROOT/'.local/spawner-skill-xp-build'
    source = work/'AstralProgression.java'
    work.mkdir(parents=True, exist_ok=True)
    source.write_bytes((ROOT/'datapack-src/runtime/AstralProgression.java').read_bytes())
    classes = work/'classes'
    classes.mkdir(exist_ok=True)
    jars = list((server/'libraries').rglob('*.jar')) + [
        ROOT/'.local/asw-native/server/plugins/auraskills.jar',
        ROOT/'.local/asw-native/server/plugins/mythicmobs.jar',
        ROOT/'.local/tanda5a/GriefPrevention.jar']
    args = ['-encoding', 'UTF-8', '-classpath', os.pathsep.join(map(str, jars)),
            '-d', str(classes), str(source)]
    argfile = work/'compile.args'
    argfile.write_text('\n'.join('"'+v.replace('\\', '/')+'"' for v in args))
    subprocess.run([str(java), '-m', 'jdk.compiler/com.sun.tools.javac.Main', '@'+str(argfile)], check=True)
    dest = ROOT/'build/spawner-skill-xp/AstralProgression.jar'
    dest.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(read('build/runtime/AstralProgression.jar'))) as old, \
            zipfile.ZipFile(dest, 'w', zipfile.ZIP_DEFLATED) as out:
        for name in old.namelist():
            if name.startswith('astral/AstralProgression') and name.endswith('.class'):
                continue
            data = old.read(name)
            if name == 'plugin.yml':
                cfg = yaml.safe_load(data)
                cfg['version'] = '1.6.5'
                data = yaml.safe_dump(cfg, sort_keys=False).encode()
            if name == 'config.yml':
                cfg = yaml.safe_load(data)
                cfg.pop('tier-bonus', None)
                cfg['tier-bonus-multipliers'] = {'1': 4, '2': 10}
                data = yaml.safe_dump(cfg, sort_keys=False).encode()
            out.writestr(zipfile.ZipInfo(name, (2026, 11, 27, 0, 0, 0)), data)
        for path in sorted((classes/'astral').glob('AstralProgression*.class')):
            out.writestr(zipfile.ZipInfo('astral/'+path.name, (2026, 11, 27, 0, 0, 0)), path.read_bytes())
    print(dest)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--java', type=Path, required=True)
    parser.add_argument('--server', type=Path, required=True)
    parser.add_argument('--revision', default='HEAD')
    args = parser.parse_args()
    build(args.java.resolve(), args.server.resolve(), args.revision)
