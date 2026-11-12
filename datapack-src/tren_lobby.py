"""Genera configuracion propia y entrega privada del tren; nunca modifica el lobby."""
import argparse
import hashlib
import io
import json
import os
import re
from pathlib import Path
import shutil
import subprocess
import urllib.request
import zipfile

import yaml
from terceros import ROOT, privado
from pack_audit import audit, relocate_model_textures

OUT = ROOT/'build/tren'
SOURCE = Path('C:/Users/Trainx/Downloads/Steam_Train_Coaster_Pack_2_1-hsxfj2.zip')
BASE = 'build/entregas/alas-casco/AstralRPG-Textures.zip'
DELIVERY = 'build/entregas/tren-lobby'
STAMP = (2026,11,11,0,0,0)


def dump(path, data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(yaml.safe_dump(data,sort_keys=False,allow_unicode=True),encoding='utf8')


def cart(kind):
    # Arte separado del YAML: solo referencias a item_model propio.
    item={'type':'PAPER','meta':{'==':'ItemMeta','meta-type':'UNSPECIFIC','item-model':'astral:tren_'+kind}}
    attachments=[{'type':'ITEM','item':item,'position':{'transform':'DISPLAY_FIXED','posY':2.0,
        'posZ':(-0.02313125 if kind=='head' else 0.0887875),
        'sizeX':2.0,'sizeY':2.0,'sizeZ':2.0}}]
    if kind=='cart':
        attachments.append({'type':'SEAT','position':{'posY':1.25,'posZ':0.1},'displayMode':'DEFAULT'})
    return {'entityType':'MINECART','astral-model':kind,'model':{'type':'EMPTY',
        'physical':{'cartLength':(3.6275125 if kind=='head' else 4.89375),'wheelCenter':0.0,'wheelDistance':1.5},'attachments':attachments}}


def configuration():
    return {'nameFormat':'astral_lobby_survival','speedLimit':0.08,'gravity':0.0,
        'slowDown':False,'keepChunksLoaded':True,'allowPlayerEnter':True,'allowPlayerExit':True,
        'allowMobEnter':False,'invincible':True,'playerTakeable':False,
        'collision':{'players':'CANCEL','misc':'CANCEL','train':'CANCEL','block':'DEFAULT'},
        'carts':[cart('head'),cart('cart'),cart('cart'),cart('cart')]}


def generate():
    OUT.mkdir(parents=True,exist_ok=True)
    dump(OUT/'AstralTrain/train.yml',configuration())
    dump(OUT/'Train_Carts/savedTrainModules/astral_lobby.yml',{'AstralLobby':configuration()})
    dump(OUT/'AstralTrain/config.yml',{'enabled':False,'station':{'x':0,'y':0,'z':0,'direction':'NORTH'}})
    versions=json.loads((ROOT/'datapack-src/tren-versions.json').read_text())
    (OUT/'versions.json').write_text(json.dumps(versions,indent=2)+'\n',encoding='utf8')


def download_dependencies():
    """Descargas oficiales fijadas por hash; nunca se publican los JAR de terceros."""
    folder=ROOT/'.local/tren-deps';folder.mkdir(parents=True,exist_ok=True)
    versions=json.loads((ROOT/'datapack-src/tren-versions.json').read_text())
    for name,entry in versions.items():
        target=folder/(name+'.jar')
        if target.exists() and hashlib.sha512(target.read_bytes()).hexdigest()==entry['sha512']:continue
        data=urllib.request.urlopen(entry['url'],timeout=60).read()
        if hashlib.sha512(data).hexdigest()!=entry['sha512']:raise ValueError('Hash incorrecto: '+name)
        target.write_bytes(data)


def compile_plugin(java,server):
    for name,entry in json.loads((ROOT/'datapack-src/tren-versions.json').read_text()).items():
        jar=ROOT/'.local/tren-deps'/(name+'.jar')
        if not jar.exists() or hashlib.sha512(jar.read_bytes()).hexdigest()!=entry['sha512']:
            raise ValueError('Dependencia faltante o hash incorrecto: '+name+'; usar --download-deps')
    classes=ROOT/'.local/tren-classes';classes.mkdir(parents=True,exist_ok=True)
    jars=[*server.joinpath('libraries').rglob('*.jar'),ROOT/'.local/tren-deps/traincarts.jar',ROOT/'.local/tren-deps/bkcommonlib.jar']
    subprocess.run([str(java),'-m','jdk.compiler/com.sun.tools.javac.Main','-encoding','UTF-8',
        '-source','25','-target','25','-classpath',os.pathsep.join(map(str,jars)),
        '-d',str(classes),str(ROOT/'datapack-src/runtime/AstralTrain.java')],check=True)
    dest=OUT/'AstralTrain.jar'
    with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
        for path in sorted((classes/'astral').glob('AstralTrain*.class')):
            z.writestr(zipfile.ZipInfo('astral/'+path.name,STAMP),path.read_bytes())
        z.writestr(zipfile.ZipInfo('plugin.yml',STAMP),"name: AstralTrain\nversion: 1.1.0\nmain: astral.AstralTrain\napi-version: '26.1.2'\ndepend: [Train_Carts, BKCommonLib]\nsoftdepend: [Multiverse-Core]\ncommands:\n  astraltren:\n    permission: astraltren.admin\npermissions:\n  astraltren.admin:\n    default: op\n")
        for name in ('config.yml','train.yml'):
            z.writestr(zipfile.ZipInfo(name,STAMP),(OUT/'AstralTrain'/name).read_bytes())
    return hashlib.sha256(dest.read_bytes()).hexdigest()


def prepare_private(source):
    base=privado()/BASE
    if not base.exists():raise FileNotFoundError('Falta FINAL Alas/casco. No usar pack global ni publico como base.')
    original=privado()/'x/tren/Steam_Train_Coaster_Pack_2_1.zip'
    original.parent.mkdir(parents=True,exist_ok=True)
    if original.exists() and original.read_bytes()!=source.read_bytes():raise ValueError('Original privado diferente; conservarlo y revisar')
    if not original.exists():shutil.copy2(source,original)
    with zipfile.ZipFile(base) as z:files={n:z.read(n) for n in z.namelist()}
    old=dict(files)
    # Extraer por nombres conocidos; nunca importar el override vanilla ni pack.mcmeta viejo.
    with zipfile.ZipFile(original) as outer:
        inner=next(n for n in outer.namelist() if n.endswith('EC - Steam Roller Coaster.zip'))
        with zipfile.ZipFile(io.BytesIO(outer.read(inner))) as z:
            prefix='EC - Steam Roller Coaster/'
            assets={n.removeprefix(prefix):z.read(n) for n in z.namelist() if n.startswith(prefix+'assets/ec_roller_coaster/') and not n.endswith('/')}
    for name,data in assets.items():
        if '/models/' in name:
            model=json.loads(data)
            # Contexto FIXED de displays modernos: ancho ~1.23, largo ~2.45 bloques.
            model['display']['fixed']={'scale':[2,2,2]}
            data=json.dumps(model,ensure_ascii=False,indent=2).encode()
        files[name]=data
    relocate_model_textures(files)
    for kind in ('head','cart'):
        files[f'assets/astral/items/tren_{kind}.json']=json.dumps({'model':{'type':'minecraft:model',
            'model':f'ec_roller_coaster:basic_coaster_{kind}'}}).encode()
    changed=sorted(n for n in files if files[n]!=old.get(n))
    if any(n in old for n in changed):raise ValueError('La conversion pisaria archivos previos: '+str(changed))
    dest=privado()/DELIVERY;dest.mkdir(parents=True,exist_ok=True)
    target=dest/'AstralRPG-Textures.zip'
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
        for name,data in sorted(files.items()):z.writestr(zipfile.ZipInfo(name,STAMP),data,compress_type=zipfile.ZIP_DEFLATED)
    refs=audit(target);sha=hashlib.sha1(target.read_bytes()).hexdigest()
    (dest/'pack.sha1').write_text(sha+'\n')
    provenance={'base':BASE,'base_sha1':hashlib.sha1(base.read_bytes()).hexdigest(),'final_sha1':sha,
        'source_sha256':hashlib.sha256(original.read_bytes()).hexdigest(),'changed':changed,'removed':[],
        'preserved_entries':len(old),'references':refs,'original_configs':'Paste TrainCarts HTTP 403; configuracion propia, no importada'}
    (dest/'procedencia.json').write_text(json.dumps(provenance,indent=2),encoding='utf8')
    return provenance


def manifest(provenance):
    template=(ROOT/'datapack-src/tren-lobby-entrega.md').read_text(encoding='utf8')
    sha=hashlib.sha256((OUT/'AstralTrain.jar').read_bytes()).hexdigest() if (OUT/'AstralTrain.jar').exists() else 'COMPILACION PENDIENTE'
    for key,value in {'PACK_SHA1':provenance['final_sha1'],'BASE_SHA1':provenance['base_sha1'],
        'JAR_SHA256':sha,'PRESERVED':str(provenance['preserved_entries'])}.items():template=template.replace('{{'+key+'}}',value)
    target=ROOT/'build/deploy/tren-lobby.md';target.parent.mkdir(parents=True,exist_ok=True);target.write_text(template,encoding='utf8')
    verification()


def verification():
    work=ROOT/'.local/tren-probe'
    jar=OUT/'AstralTrain.jar';tested=work/'paper/plugins/AstralTrain.jar'
    matched=jar.exists() and tested.exists() and jar.read_bytes()==tested.read_bytes()
    lines=['# Verificacion local del tren','',
        'Generado por `tren_lobby.py`; no es evidencia de despliegue remoto.',
        'Paper 26.1.2 build 74, Java 25; jugadores NMS simulados, sin clientes reales.','',
        'AstralTrain.jar SHA-256: `'+(hashlib.sha256(jar.read_bytes()).hexdigest() if jar.exists() else 'PENDIENTE')+'`.',
        'Los resultados solo se dan por correctos si el JAR del ensayo coincide byte por byte con la entrega.','',
        '| Ensayo | Resultado | Comprobaciones correctas |','|---|---|---|']
    for name in ('paper.log','restart.log','crash-restart.log'):
        path=work/name;text=path.read_text(encoding='utf8',errors='replace') if path.exists() else ''
        ok=matched and 'TRAIN RESULT failures=0' in text and 'TRAIN FAIL' not in text
        lines.append(f"| {name} | {'Correcto' if ok else 'Pendiente o fallido'} | {text.count('TRAIN PASS')} |")
    lines+=['','Memoria medida con `spark health --memory`, con TrainCarts/BKCommonLib cargados.',
        'Estas son muestras del ensayo local, no un diferencial contra Paper sin plugins.',
        'La primera es anterior a los viajes; la segunda posterior a los viajes.','',
        '| Muestra en paper.log | Heap | Non-heap |','|---|---|---|']
    path=work/'paper.log'
    text=path.read_text(encoding='utf8',errors='replace') if path.exists() else ''
    clean=re.sub(r'\x1b\[[0-9;]*m','',text)
    clean='\n'.join(line.lstrip('> ') for line in clean.splitlines())
    heaps=re.findall(r'\bMemory usage:\s*([\d.,]+ [MG]B)',clean)
    nonheaps=re.findall(r'Non-heap memory usage:\s*([\d.,]+ [MG]B)',clean)
    for i,(heap,nonheap) in enumerate(zip(heaps,nonheaps),1):lines.append(f'| {i} | {heap} | {nonheap} |')
    lines+=['','Pruebas Python: `python -m unittest discover -s datapack-src -p test_tren_lobby.py` (4 casos).',
        'Cubren plazas, reproducibilidad, preservacion de todas las entradas previas y rechazo de colisiones/falta de base.',
        'Auditoria de arte publico: ejecutar `tools/verificar_terceros.py` con rutas agregadas al indice.',
        '', 'Pendiente: XYZ exactos y construccion del anden, protecciones WorldGuard con jugador sin OP,',
        'click real, render de asientos/modelo con 1 y 3 clientes, reconexion real y memoria antes/despues en el hosting.',
        'No hay captura de Minecraft. Logs y arte permanecen privados.']
    (OUT/'verificacion.md').write_text('\n'.join(lines)+'\n',encoding='utf8')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--java',type=Path);parser.add_argument('--server',type=Path)
    parser.add_argument('--source',type=Path)
    parser.add_argument('--download-deps',action='store_true')
    args=parser.parse_args();generate()
    if args.download_deps:download_dependencies()
    if args.java and args.server:compile_plugin(args.java.resolve(),args.server.resolve())
    stored=privado()/'x/tren/Steam_Train_Coaster_Pack_2_1.zip'
    result=prepare_private(args.source or (stored if stored.exists() else SOURCE));manifest(result)
    print('FINAL privado SHA-1',result['final_sha1'],'entradas conservadas',result['preserved_entries'])
