"""Convierte Spires en privado: vanilla 1.6.4 -> DataFixer de Paper 26.1.2.

No descarga ni ejecuta codigo del mapa. Usar --anvil para reutilizar la etapa 1.6.4.
La salida debe ser nueva y estar bajo .local; ningun mapa se publica.
"""
import argparse
from collections import Counter
import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import zipfile
import zlib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'datapack-src'))
from mapas import NBT, sanitize
from santuario_mapa import write_nbt, package
from santuario_azeroth import BOUNDS, WORLD

VANILLA_SHA1 = '050f93c1f3fe9e2052398f7bd6aca10c63d64a87'


def records(raw):
    for slot in range(1024):
        offset = int.from_bytes(raw[slot*4:slot*4+3], 'big')*4096
        if not offset:
            continue
        size = int.from_bytes(raw[offset:offset+4], 'big')
        payload = raw[offset+5:offset+4+size]
        kind = raw[offset+4]
        if kind == 2:
            payload = zlib.decompress(payload)
        elif kind == 1:
            payload = gzip.decompress(payload)
        else:
            raise ValueError(f'Compresion antigua inesperada: {kind}')
        yield slot, NBT(payload, typed=True).root()


def vanilla(source, jar, java, out):
    if hashlib.sha1(jar.read_bytes()).hexdigest() != VANILLA_SHA1:
        raise ValueError('Se requiere el server.jar oficial 1.6.4 verificado por Mojang')
    work = out/'vanilla164'
    work.mkdir()
    with zipfile.ZipFile(source) as archive:
        for name in archive.namelist():
            rel = Path(name)
            if rel.parts[0] != 'Spires of Azeroth':
                continue  # excluye __MACOSX
            rel = rel.relative_to('Spires of Azeroth')
            if rel.as_posix() != 'level.dat' and not (len(rel.parts)==2 and rel.parts[0]=='region' and rel.suffix=='.mcr'):
                continue
            target = work/'map'/rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(archive.read(name))
    (work/'server.properties').write_text('server-ip=127.0.0.1\nserver-port=25602\nonline-mode=false\nlevel-name=map\n')
    log = out/'vanilla164.log'
    with log.open('w') as stream:
        process = subprocess.Popen([str(java), '-Xmx1G', '-jar', str(jar), 'nogui'], cwd=work,
                                   stdin=subprocess.PIPE, stdout=stream, stderr=subprocess.STDOUT, text=True)
        try:
            deadline = time.monotonic()+120
            while 'For help, type' not in log.read_text(errors='replace'):
                if process.poll() is not None or time.monotonic()>deadline:
                    raise RuntimeError(f'Conversion vanilla fallida: {log}')
                time.sleep(.5)
        finally:
            if process.poll() is None:
                process.communicate('stop\n', timeout=60)
    return work/'map/region'


def prepare(source, anvil, paper, java, out):
    legacy = out/'legacy'
    legacy.mkdir()
    x0,z0,x1,z1 = BOUNDS
    chunks = before = 0
    tiles = Counter()
    # Solo chunks presentes en el ZIP original; excluir generacion del servidor 1.6.4.
    with zipfile.ZipFile(source) as archive:
        for name in archive.namelist():
            if not name.startswith('Spires of Azeroth/region/') or not name.endswith('.mcr'):
                continue
            original = {slot for slot,_ in records(archive.read(name))}
            path = anvil/Path(name).with_suffix('.mca').name
            for slot, tree in records(path.read_bytes()):
                c = tree[1]['Level'][1]
                cx,cz = c['xPos'][1],c['zPos'][1]
                if slot not in original or not(x0//16<=cx<=x1//16 and z0//16<=cz<=z1//16):
                    continue
                c['Entities'] = (9, [])
                for _,entity in c.get('TileEntities',(9,[]))[1]:
                    tiles[entity['id'][1]] += 1
                    for field in ('Items','LootTable','LootTableSeed','Record','RecordItem'):
                        entity.pop(field,None)
                for _,section in c['Sections'][1]:
                    before += sum(b!=0 for b in section['Blocks'][1])
                write_nbt(legacy/f'{cx}.{cz}.nbt', tree)
                chunks += 1
    jars = [*paper.joinpath('versions').rglob('*.jar'), *paper.joinpath('libraries').rglob('*.jar')]
    args = ['-Xmx2G','-cp',os.pathsep.join(map(str,jars)),str(ROOT/'datapack-src/ConvertLegacyChunks.java'),
            str(legacy),str(out/'modern'),'-1']
    argfile = out/'java-args.txt'
    argfile.write_text('\n'.join('"'+s.replace('\\','/')+'"' for s in args),encoding='utf8')
    with (out/'dfu.log').open('w') as log:
        subprocess.run([str(java),'@'+str(argfile)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
    trimmed = out/'trimmed'
    trimmed.mkdir()
    versions=set()
    for f in (out/'modern').glob('*.nbt'):
        tree = NBT(gzip.decompress(f.read_bytes()),typed=True).root()
        if 'Level' in tree[1]:
            raise ValueError('DataFixer no produjo chunks modernos')
        versions.add(tree[1]['DataVersion'][1])
        sanitize(tree)
        write_nbt(trimmed/f.name,tree)
    if len(list(trimmed.glob('*.nbt'))) != chunks or chunks != 169:
        raise ValueError('Recorte incompleto; no instalar')
    package(trimmed,out/WORLD/'region')
    report={'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(), 'bounds_xz':BOUNDS,
            'chunks':chunks,'non_air_before':before,'original_block_entities':dict(tiles),
            'data_versions':sorted(versions),'regions':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                for p in sorted((out/WORLD/'region').glob('*.mca'))}}
    (out/'conversion.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('source','java','paper','out'):
        parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--anvil',type=Path)
    parser.add_argument('--vanilla164',type=Path)
    a=parser.parse_args()
    a.out=a.out.resolve()
    if not a.out.is_relative_to(ROOT/'.local') or a.out.exists():
        parser.error('--out debe ser una carpeta NUEVA bajo .local')
    if not a.anvil and not a.vanilla164:
        parser.error('Falta --anvil o --vanilla164 oficial')
    a.out.mkdir(parents=True)
    region=a.anvil.resolve() if a.anvil else vanilla(a.source,a.vanilla164.resolve(),a.java.resolve(),a.out)
    prepare(a.source,region,a.paper.resolve(),a.java.resolve(),a.out)
