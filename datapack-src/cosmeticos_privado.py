"""Convierte sombreros licenciados sin escribir arte en el repositorio publico."""
import json
import shutil
import zipfile
from pathlib import Path
from terceros import privado
from cosmeticos_catalogo import HATS

ARCHIVES = ('halloween-0fcaup.zip', 'voxelspawns_villagerhats-dd66a1.zip')


def prepare(downloads=None):
    base=privado(); originals=base/'originales/cosmeticos'
    originals.mkdir(parents=True,exist_ok=True)
    out=base/'build/item-pack'
    def put(name,content):
        dest=out/name;dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_bytes(content if isinstance(content,bytes) else json.dumps(content,ensure_ascii=False).encode('utf8'))
    for index,archive in enumerate(ARCHIVES):
        source=originals/archive
        if not source.exists():
            download=(downloads or Path.home()/'Downloads')/archive
            shutil.copy2(download,source)
        with zipfile.ZipFile(source) as z:
            # Leer solo assets conocidos: nunca extraer rutas arbitrarias del ZIP.
            entries={n[n.index('assets/'):]:z.read(n) for n in z.namelist() if 'assets/' in n and not n.endswith('/')}
            prefix='halloween' if index==0 else 'aldeanos'
            def tex(ref):
                if ref.startswith('#'):return ref
                ns,sep,path=ref.partition(':')
                if not sep:ns,path='minecraft',ns
                name=f'assets/{ns}/textures/{path}.png'
                if name not in entries:raise ValueError('Falta textura original: '+ref)
                return f'astral_cosmeticos:item/{prefix}/{path}'
            for name,blob in entries.items():
                if '/textures/' in name and (name.endswith('.png') or name.endswith('.png.mcmeta')):
                    path=name.split('/textures/',1)[1]
                    put(f'assets/astral_cosmeticos/textures/item/{prefix}/{path}',blob)
            for key,_,_,model in HATS:
                if model is None or (key in ('frankenstein','bruja','diablo'))!=(index==0):continue
                raw=json.loads(entries[f'assets/minecraft/models/{model}.json'])
                raw.pop('overrides',None)
                raw['textures']={k:tex(v) for k,v in raw.get('textures',{}).items()}
                if 'head' not in raw.get('display',{}):raise ValueError('Falta ajuste head: '+key)
                put(f'assets/astral_cosmeticos/models/item/{key}.json',raw)
                put(f'assets/astral/items/cosmeticos/sombrero_{key}.json',
                    {'model':{'type':'minecraft:model','model':'astral_cosmeticos:item/'+key}})
    # El sombrero de Carnivora ya fue convertido por tanda4b_privado.
    put('assets/astral/items/cosmeticos/sombrero_carnivora.json',
        {'model':{'type':'minecraft:model','model':'elitecreatures:carnivoret_weapon_set/hat'}})
    print('20 sombreros preparados exclusivamente en el circuito privado.')


if __name__=='__main__':prepare()
