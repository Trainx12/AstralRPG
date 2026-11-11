"""Compila exclusivamente codigo propio con un JDK y librerias Paper locales."""
import argparse
import os
from pathlib import Path
import subprocess
import zipfile

ROOT=Path(__file__).resolve().parents[1]


def build(jdk,server):
    target=ROOT/'.local/tanda4b-classes'
    target.mkdir(parents=True,exist_ok=True)
    jars=list((server/'libraries').rglob('*.jar'))
    if not jars:
        raise FileNotFoundError('Faltan dependencias Paper locales')
    compiler = [str(jdk/('java.exe' if os.name=='nt' else 'java')), '-m','jdk.compiler/com.sun.tools.javac.Main']
    subprocess.run([*compiler, '-encoding','UTF-8','-source','25','-target','25',
        '-classpath',os.pathsep.join(str(p) for p in jars),'-d',str(target),str(ROOT/'datapack-src/runtime/AstralDecor.java')],check=True)
    dest=ROOT/'build/runtime/AstralDecor.jar'; dest.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted((target/'astral').glob('AstralDecor*.class')):
            z.writestr(zipfile.ZipInfo(p.relative_to(target).as_posix(),(2026,11,10,0,0,0)),p.read_bytes())
        z.writestr(zipfile.ZipInfo('plugin.yml',(2026,11,10,0,0,0)), 'name: AstralDecor\nversion: 1.0.0\nmain: astral.AstralDecor\napi-version: \'26.1.2\'\nsoftdepend: [WorldGuard, MythicMobs, Vault, EconomyShopGUI]\n')
    print(dest)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jdk',required=True,type=Path,help='Carpeta bin del JDK 25')
    parser.add_argument('--server',required=True,type=Path)
    args=parser.parse_args(); build(args.jdk.resolve(),args.server.resolve())
