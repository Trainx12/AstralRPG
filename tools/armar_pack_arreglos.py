"""Entrega privada aislada sobre el pack APROBADO de 3c; no mezcla otras tareas."""
import hashlib
import io
import json
import shutil
from pathlib import Path
import subprocess
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'datapack-src'))
from terceros import privado,PETS

BASE_SHA1='a18b694f5002cef979fe72ad6caf24134550db03'


def files(blob):
    with zipfile.ZipFile(io.BytesIO(blob)) as z:return {n:z.read(n) for n in z.namelist()}


def main():
    base=subprocess.check_output(['git','-C',str(privado()),'show','a6d26e9:build/AstralRPG-Textures.zip'])
    if hashlib.sha1(base).hexdigest()!=BASE_SHA1:raise ValueError('La base privada no coincide con 3c desplegada')
    before=files(subprocess.check_output(['git','show','c3d4af8:build/AstralRPG-Textures.zip'],cwd=ROOT))
    after=files((ROOT/'build/AstralRPG-Textures.zip').read_bytes())
    result=files(base)
    changed=sorted(n for n,data in after.items() if before.get(n)!=data)
    # Solo arte propio de interfaz, retratos propios y modelos de esta tarea.
    allowed=('assets/astral/items/menu/','assets/astral/models/menu/','assets/astral/textures/item/menu/',
             'assets/astral/textures/font/menu/','assets/astral/items/mascotas/catalogo_',
             'assets/astral/models/mascotas/catalogo_','assets/astral/textures/item/mascotas/catalogo_',
             'assets/bettermodel/models/model/astral_esq_')
    for name in changed:
        if not name.startswith(allowed):raise ValueError('Cambio publico fuera de esta tarea: '+name)
        result[name]=after[name]
    if set(before)-set(after):raise ValueError('Hay eliminaciones publicas para revisar')
    private_names=[]
    for pid,*_ in PETS:
        for relative in (f'items/mascotas/catalogo_{pid}.json',f'models/mascotas/catalogo_{pid}.json',
                         f'textures/item/mascotas/catalogo_{pid}.png'):
            name='assets/astral/'+relative
            result[name]=(privado()/'build/item-pack'/name).read_bytes();private_names.append(name)
    folder=ROOT/'.local/arreglos-pack';folder.mkdir(parents=True,exist_ok=True)
    target=folder/'AstralRPG-Textures.zip'
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
        for name,data in sorted(result.items()):
            z.writestr(zipfile.ZipInfo(name,(2026,11,11,0,0,0)),data,compress_type=zipfile.ZIP_DEFLATED)
    sha=hashlib.sha1(target.read_bytes()).hexdigest()
    (folder/'pack.sha1').write_text(sha+'\n')
    (folder/'procedencia.json').write_text(json.dumps({'base_sha1':BASE_SHA1,'public_changes':changed,
        'private_icons':private_names,'final_sha1':sha},indent=2),encoding='utf8')
    # Ruta nueva y exclusiva para publicar esta entrega privada sin agregar
    # el resto del build ni las ediciones concurrentes de otras tandas.
    delivery=privado()/'build/entregas/arreglos-esqueleto-volcano'
    delivery.mkdir(parents=True,exist_ok=True)
    for name in ('AstralRPG-Textures.zip','pack.sha1','procedencia.json'):
        shutil.copy2(folder/name,delivery/name)
    print('Pack aislado:',target,'SHA1',sha,'cambios publicos',len(changed),'iconos privados',len(private_names))


if __name__=='__main__':main()
