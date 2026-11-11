"""Render privado de alas con pechera, usando las transformaciones del pack FINAL."""
import base64
from copy import deepcopy
import io
import json
from pathlib import Path
import shutil
import tempfile
import zipfile
from PIL import Image
from terceros import ROOT,privado
from preview_tanda4b import java_model
from tanda4b_privado import rotate
from build_privado import preview


def main():
    delivery=privado()/'build/entregas/tienda-modelo'
    models,angles={},{}
    with tempfile.TemporaryDirectory(dir=ROOT/'.local') as folder:
        assets=Path(folder)/'assets'
        with zipfile.ZipFile(delivery/'AstralRPG-Textures.zip') as z:
            for n in z.namelist():
                if n.startswith(('assets/asura/','assets/elitecreatures/','assets/astral/textures/entity/equipment/humanoid/')):
                    p=Path(folder)/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(n))
            armor=z.read('assets/astral/textures/entity/equipment/humanoid/carnivora.png')
            for iid,ref in [('asura_alas','asura:asura_wings'),('carnivora_alas','elitecreatures:carnivoret_weapon_set/wing')]:
                wrapper=json.loads(z.read(f'assets/astral/models/cosmetics/{iid}.json'))['display']['fixed']
                data=java_model(ref,assets)
                scale=wrapper['scale'][0];yaw=wrapper['rotation'][1]
                translation=rotate(wrapper['translation'],[0,0,0],'y',-yaw)
                # Maniqui mira -Z (= jugador yaw180). Pasajero a 1,8 b, offset -0,35 y -0,32 atras.
                offset=rotate([0,23.2,5.12],[0,0,0],'y',-(yaw+180))
                for e in data['elements']:
                    for field in ('from','to','origin'):
                        if field in e:e[field]=[(v-8)*scale+translation[a]+offset[a] for a,v in enumerate(e[field])]
                data['outliner'][0].update(rotation=[0,yaw+180,0],origin=[0,0,0])
                ati=len(data['textures'])
                data['textures'].append({'source':'data:image/png;base64,'+base64.b64encode(armor).decode(),'uv_width':64,'uv_height':32})
                skin=Image.new('RGBA',(16,16),'#bca185');b=io.BytesIO();skin.save(b,format='PNG')
                sti=len(data['textures']);data['textures'].append({'source':'data:image/png;base64,'+base64.b64encode(b.getvalue()).decode(),'uv_width':16,'uv_height':16})
                parts=[]
                for name,lo,hi,uv,ti in [('cara',[-4,24,-4],[4,32,4],(0,0),sti),
                        ('pechera',[-4.4,12,-2.4],[4.4,24.4,2.4],(16,16),ati),
                        ('brazo_i',[-8,12,-2],[-4,24,2],(40,16),ati),('brazo_d',[4,12,-2],[8,24,2],(40,16),ati),
                        ('pierna_i',[-4,0,-2],[-.2,12,2],(0,0),sti),('pierna_d',[.2,0,-2],[4,12,2],(0,0),sti)]:
                    x,y=uv;w,h,d=(8,12,4) if name=='pechera' else [hi[a]-lo[a] for a in range(3)]
                    faces={f:{'texture':ti,'uv':v} for f,v in {
                        'north':[x+d,y+d,x+d+w,y+d+h],'south':[x+2*d+w,y+d,x+2*d+2*w,y+d+h],
                        'west':[x,y+d,x+d,y+d+h],'east':[x+d+w,y+d,x+2*d+w,y+d+h],
                        'up':[x+d,y,x+d+w,y+d],'down':[x+d+w,y,x+d+2*w,y+d]}.items()}
                    if ti==sti:
                        for f in faces.values():f['uv']=[0,0,16,16]
                    data['elements'].append({'uuid':name,'from':lo,'to':hi,'faces':faces});parts.append(name)
                data['outliner'].append({'uuid':'maniqui','name':'maniqui','children':parts})
                for label,yaw_view in [('frente',0),('espalda',180),('costado',90)]:
                    name=iid+'_'+label;models[name]=deepcopy(data);angles[name]=(yaw_view,5)
    preview(models,'tienda-alas',include_sword=False,angles=angles)
    target=delivery/'previews/alas-pechera.png';target.parent.mkdir(exist_ok=True)
    shutil.copy2(privado()/'build/previews/tienda-alas.png',target)
    print(target)


if __name__=='__main__':main()
