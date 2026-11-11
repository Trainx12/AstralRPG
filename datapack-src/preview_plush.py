"""Verificacion geometrica y vista CPU privada; nunca es captura de Minecraft."""
import itertools
import json
import re
import shutil
import tempfile
import zipfile
from copy import deepcopy
from pathlib import Path
from terceros import ROOT,privado
from tanda4b_privado import rotate
from preview_tanda4b import java_model
from build_privado import preview


def layouts():
    code=(ROOT/'datapack-src/runtime/AstralDecor.java').read_text(encoding='utf8')
    return {key:[float(n.strip().removesuffix('f')) for n in values.split(',')]
            for key,values in re.findall(r'"(alex|steve|creaking|ocelot|tropical_fish|zombie_horse)",new float\[\]\{([^}]+)\}',code)}


def vertices(raw,key=None):
    points=[]
    for e in raw['elements']:
        for p in itertools.product(*zip(e['from'],e['to'])):
            if r:=e.get('rotation'):p=rotate(p,r['origin'],r['axis'],r['angle'])
            if key=='tropical_fish':p=[n+8 for n in rotate([n-8 for n in p],[0,0,0],'x',-90)]
            points.append(p)
    return points


def main():
    target=privado()/'build/entregas/yeti-bastones-guia'
    models={};angles={}
    with tempfile.TemporaryDirectory(dir=ROOT/'.local') as tmp:
        with zipfile.ZipFile(target/'AstralRPG-Textures.zip') as z:
            for n in z.namelist():
                if n.startswith('assets/nogs_menagerie/'):
                    p=Path(tmp)/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(n))
        for key,v in layouts().items():
            data=java_model('nogs_menagerie:plushies/nm_plushie_'+key,Path(tmp)/'assets')
            offset=v[1:4]
            if key=='tropical_fish':
                offset=rotate(offset,[0,0,0],'x',90)
                data['outliner'][0].update(rotation=[-90,0,0],origin=[0,0,0])
            for e in data['elements']:
                for field in ('from','to','origin'):
                    if field in e:e[field]=[(n-8)*v[0]+16*offset[a] for a,n in enumerate(e[field])]
            for label,yaw in (('frente',0),('costado',90)):
                name='CPU_'+key+'_'+label;models[name]=deepcopy(data);angles[name]=(yaw,0)
    preview(models,'peluches-derechos-CPU',include_sword=False,angles=angles)
    out=target/'previews/peluches-derechos-CPU.png';out.parent.mkdir(exist_ok=True)
    shutil.copy2(privado()/'build/previews/peluches-derechos-CPU.png',out)
    print('Vista CPU privada:',out)


if __name__=='__main__':main()
