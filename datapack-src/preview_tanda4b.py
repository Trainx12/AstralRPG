"""Vista de modelos, exclusivamente privada; no reemplaza una prueba con jugador."""
import base64
from copy import deepcopy
import json
import uuid
from terceros import privado, ROOT
from build_privado import preview
from tanda4b import CLONES, SIMPLE, PLUSHIES


def java_model(reference, assets):
    ns, name = reference.split(':')
    data = json.loads((assets/ns/'models'/f'{name}.json').read_text(encoding='utf8'))
    textures = data.get('textures', {})
    ids, images = {}, []
    def texture(key):
        while key.startswith('#'):
            key = textures[key[1:]]
        if key not in ids:
            ns, name = key.split(':'); path = assets/ns/'textures'/f'{name}.png'
            from PIL import Image
            w,h = Image.open(path).size
            ids[key] = len(images)
            images.append({'source':'data:image/png;base64,'+base64.b64encode(path.read_bytes()).decode(),
                           'uv_width':16, 'uv_height':16})
        return ids[key]
    elements=[]
    for original in data.get('elements',[]):
        e=deepcopy(original); e['uuid']=str(uuid.uuid4()); e['type']='cube'
        rot=e.pop('rotation',None)
        if rot:
            e['origin']=rot['origin']; e['rotation']=[rot['angle'] if a==rot['axis'] else 0 for a in 'xyz']
        for f in e.get('faces',{}).values():
            f['texture']=texture(f['texture'])
            f.setdefault('uv',[0,0,16,16])
        elements.append(e)
    bone=str(uuid.uuid4())
    return {'textures':images, 'elements':elements, 'outliner':[{'uuid':bone,'name':'root','children':[e['uuid'] for e in elements]}]}


def main():
    base=privado()/'build'; assets=base/'item-pack/assets'; models={}
    ids=list(CLONES)+['carnivora_'+p for p in ('helmet','chestplate','leggings','boots')]+list(SIMPLE)
    for iid in ids:
        if iid=='colmillo_carnivoro': continue
        tree=json.loads((assets/'astral/items'/f'{iid}.json').read_text(encoding='utf8'))['model']
        while 'model' not in tree or isinstance(tree.get('model'),dict):
            tree=tree.get('on_false',tree.get('fallback',{}))
        try:
            model=java_model(tree['model'],assets)
            if model['elements']: models[iid]=model
        except FileNotFoundError:
            # Los tres iconos planos de armadura no son modelos 3D.
            continue
    # Armadura puesta en maniqui: UV del formato humanoide de dos capas.
    from PIL import Image
    layer=assets/'astral/textures/entity/equipment/humanoid/carnivora.png'
    layer2=assets/'astral/textures/entity/equipment/humanoid_leggings/carnivora.png'
    model={'textures':[{'source':'data:image/png;base64,'+base64.b64encode(p.read_bytes()).decode(),
                       'uv_width':64,'uv_height':32} for p in (layer,layer2)],'elements':[]}
    for name,lo,hi,uv,ti in [('casco',[-4,24,-4],[4,32,4],(0,0),0),('pechera',[-4,12,-2],[4,24,2],(16,16),0),
            ('brazo_i',[-8,12,-2],[-4,24,2],(40,16),0),('brazo_d',[4,12,-2],[8,24,2],(40,16),0),
            ('grebas_i',[-4,0,-2],[0,12,2],(0,16),1),('grebas_d',[0,0,-2],[4,12,2],(0,16),1),
            ('bota_i',[-4,0,-2],[0,3,2],(0,25),0),('bota_d',[0,0,-2],[4,3,2],(0,25),0)]:
        x,y=uv; w,h,d=[hi[i]-lo[i] for i in range(3)]
        faces={k:{'texture':ti,'uv':v} for k,v in {
            'north':[x+d,y+d,x+d+w,y+d+h],'south':[x+2*d+w,y+d,x+2*d+2*w,y+d+h],
            'west':[x,y+d,x+d,y+d+h],'east':[x+d+w,y+d,x+2*d+w,y+d+h],
            'up':[x+d,y,x+d+w,y+d],'down':[x+d+w,y,x+d+2*w,y+d]}.items()}
        model['elements'].append({'uuid':name,'from':lo,'to':hi,'faces':faces})
    model['outliner']=[{'uuid':'body','name':'body','children':[e['uuid'] for e in model['elements']]}]
    models={'Carnivora_armadura_puesta':model,**models}
    from tanda4b_world import own_textures
    originals=own_textures()
    for name, path, lo, hi in [('mena_asura_T4','block/asura_ore',[0,0,0],[16,16,16]),
                             ('colmillo_carnivoro','item/colmillo_carnivoro',[0,0,0],[16,16,0])]:
        source='data:image/png;base64,'+base64.b64encode(originals['assets/astral/textures/'+path+'.png']).decode()
        models[name]={'textures':[{'source':source,'uv_width':16,'uv_height':16}],
            'elements':[{'uuid':'cube','from':lo,'to':hi,'faces':{side:{'texture':0,'uv':[0,0,16,16]} for side in ('north','south','east','west','up','down')}}],
            'outliner':[{'uuid':'root','children':['cube']}]}
    models['planta_carnivora']=json.loads((ROOT/'build/models/astral_bosque_planta.bbmodel').read_text(encoding='utf8'))
    for p in sorted((base/'models').glob('astral_pet_*.bbmodel')):
        models[p.stem]=json.loads(p.read_text(encoding='utf8'))
    preview(models, 'tanda4b', include_sword=False)
    print('Vista privada tanda4b.png: modelos estaticos, sin captura en juego.')


if __name__=='__main__': main()
