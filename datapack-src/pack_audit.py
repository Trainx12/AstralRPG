"""Verifica atlas, existencia de texturas y capas en un resource pack terminado."""
import json
from pathlib import Path
import zipfile


def palette_sprites(files):
    """Sprites sinteticos registrados por Minecraft/Stellarity: no son rutas PNG."""
    result=set()
    for name,blob in files.items():
        if not name.endswith('/atlases/items.json'):continue
        for source in json.loads(blob).get('sources',[]):
            if source.get('type','').endswith('paletted_permutations'):
                result.update(texture+'_'+key for texture in source['textures'] for key in source['permutations'])
    return result


def relocate_model_textures(files):
    """Normaliza PNG reales sin alterar el arte ni los sprites de paleta del atlas."""
    synthetic=palette_sprites(files)
    for name,blob in list(files.items()):
        if '/models/' not in name or not name.endswith('.json'):continue
        data=json.loads(blob);changed=False
        for key,ref in data.get('textures',{}).items():
            if not isinstance(ref,str) or ref.startswith('#') or ref in synthetic:continue
            ns,tex=ref.split(':',1) if ':' in ref else ('minecraft',ref)
            if tex.startswith(('item/','block/')):continue
            source=f'assets/{ns}/textures/{tex}.png'
            if source not in files:continue
            target=f'assets/{ns}/textures/item/{tex}.png'
            files[target]=files[source]
            if source+'.mcmeta' in files:files[target+'.mcmeta']=files[source+'.mcmeta']
            data['textures'][key]=f'{ns}:item/{tex}';changed=True
        if changed:files[name]=json.dumps(data,ensure_ascii=False).encode('utf8')


def audit(path):
    errors=[];checked=0
    with zipfile.ZipFile(path) as z:
        names=set(z.namelist())
        synthetic=palette_sprites({n:z.read(n) for n in names if n.endswith('/atlases/items.json')})
        for name in sorted(names):
            if not name.endswith('.json'):continue
            parts=name.split('/')
            if len(parts)<4 or parts[0]!='assets':continue
            data=json.loads(z.read(name))
            if parts[2]=='models':
                for ref in data.get('textures',{}).values():
                    if not isinstance(ref,str) or ref.startswith('#'):continue
                    ns,tex=ref.split(':',1) if ':' in ref else ('minecraft',ref)
                    checked+=1
                    if ref in synthetic:continue
                    if not tex.startswith(('item/','block/')):
                        errors.append(f'{name}: fuera del atlas: {ref}')
                    if ns!='minecraft' and f'assets/{ns}/textures/{tex}.png' not in names:
                        errors.append(f'{name}: falta textura: {ref}')
            elif parts[2]=='equipment':
                for layer,entries in data.get('layers',{}).items():
                    for entry in entries:
                        ns,tex=entry['texture'].split(':',1) if ':' in entry['texture'] else ('minecraft',entry['texture'])
                        if ns!='minecraft' and f'assets/{ns}/textures/entity/equipment/{layer}/{tex}.png' not in names:
                            errors.append(f'{name}: falta capa {layer}: {entry["texture"]}')
    if errors:raise ValueError('\n'.join(errors))
    return checked


if __name__=='__main__':
    import sys
    print('Referencias verificadas:',audit(Path(sys.argv[1])))
