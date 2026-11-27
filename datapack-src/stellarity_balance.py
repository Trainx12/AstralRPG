"""Compila el complemento propio; no reconstruye ZIPs compartidos ni copia Stellarity."""
import argparse
import hashlib
import json
import os
import subprocess
import zipfile
from pathlib import Path
from stellarity_tiers import rows

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/stellarity'
STAMP = (2026, 11, 26, 0, 0, 0)
PLUGIN = '''name: AstralStellarity
version: 1.1.0
main: astral.stellarity.AstralStellarity
api-version: '26.1.2'
softdepend: [AuraSkills, AstralMesa]
commands:
  stellarity:
    permission: astral.stellarity.admin
permissions:
  astral.stellarity.admin:
    default: op
'''


def defense_patch(text):
    # Nuestro equipo tiene cero armadura vanilla; no descontar la barra visual de las piezas Astral.
    lines = []
    for line in text.splitlines():
        if ('run scoreboard players remove #v astral.tmp' in line or 'run scoreboard players add #bar astral.tmp' in line) and 'custom_data' in line and '.astral.def ' in line and '.astral.stellarity ' not in line:
            slot = line.split('eq.', 1)[1].split('.', 1)[0]
            line = line.replace(' run scoreboard', f' unless data storage astral:tmp eq.{slot}.components."minecraft:custom_data".astral.stellarity run scoreboard', 1)
        lines.append(line)
    return '\n'.join(lines) + '\n'


def generate():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/'tiers.json').write_text(json.dumps(rows(),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    # Solo una funcion propia como overlay; verifica contra la version publicada, sin empaquetar trabajo previo.
    published = subprocess.check_output(['git','show','HEAD:build/AstralRPG-Items.zip'],cwd=ROOT)
    import io
    with zipfile.ZipFile(io.BytesIO(published)) as z:
        original = z.read('data/astral/function/player/def.mcfunction').decode()
    with zipfile.ZipFile(OUT/'AstralStellarity-Compat.zip','w',zipfile.ZIP_DEFLATED) as z:
        z.writestr(zipfile.ZipInfo('pack.mcmeta',STAMP),json.dumps({'pack':{'min_format':[101,1],'max_format':[101,1],'description':'Compatibilidad propia AstralStellarity: Defensa sin barra vanilla'}}))
        z.writestr(zipfile.ZipInfo('data/astral/function/player/def.mcfunction',STAMP),defense_patch(original))


def menus():
    from guia_ampliacion import menus as guide_menus
    target=OUT/'menus'
    target.mkdir(parents=True,exist_ok=True)
    for name,body in guide_menus({}).items():
        if 'stellarity' in name: (target/(name+'.yml')).write_text(body,encoding='utf8')


def build(jdk, server):
    generate()
    classes=ROOT/'.local/stellarity-classes'
    classes.mkdir(parents=True,exist_ok=True)
    deps=[*server.joinpath('libraries').rglob('*.jar'),*server.joinpath('versions').rglob('*.jar')]
    subprocess.run([str(jdk/('java.exe' if os.name=='nt' else 'java')),'-m','jdk.compiler/com.sun.tools.javac.Main',
        '-encoding','UTF-8','-source','25','-target','25','-nowarn','-classpath',os.pathsep.join(map(str,deps)),
        '-d',str(classes),str(ROOT/'datapack-src/runtime/AstralStellarity.java')],check=True)
    dest=OUT/'AstralStellarity.jar'
    with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted((classes/'astral/stellarity').glob('AstralStellarity*.class')):
            z.writestr(zipfile.ZipInfo(p.relative_to(classes).as_posix(),STAMP),p.read_bytes())
        z.writestr(zipfile.ZipInfo('plugin.yml',STAMP),PLUGIN)
        z.writestr(zipfile.ZipInfo('config.yml',STAMP),'publico: false\n')
        z.writestr(zipfile.ZipInfo('tiers.json',STAMP),(OUT/'tiers.json').read_bytes())
    manifest = OUT/'manifest.json'
    if manifest.is_file():
        data = json.loads(manifest.read_text(encoding='utf8'))
        for entry in data['archivos']:
            entry['sha256'] = hashlib.sha256((ROOT/entry['local']).read_bytes()).hexdigest()
        manifest.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    return dest


if __name__=='__main__':
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('--jdk',type=Path)
    a.add_argument('--menus',action='store_true')
    a.add_argument('--server',type=Path,default=ROOT/'.local/testsrv')
    args=a.parse_args()
    if args.jdk: print(build(args.jdk,args.server))
    else: generate()
    if args.menus: menus()
