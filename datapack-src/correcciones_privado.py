"""Adaptacion privada de Q Cursed One y BBcosmetics. No exporta arte publico."""
import json
import uuid
from copy import deepcopy
from terceros import privado
from build_privado import adapted, item_assets, write_json
from mobs.tamanos import bounds_data


def prepare():
    root=privado();out=root/'build/entregas/correcciones-goblin-golems'
    for kind,source in [('bosque','forest'),('hielo','ice'),('cristal','crystal')]:
        mid='astral_golem_'+kind
        path=next((root/'x/golems/Q_Cursed_One').rglob('q_cursed_one_'+source+'.bbmodel'))
        raw=json.loads(path.read_text('utf8'))
        # La misma limpieza de metadatos de ModelEngine que usan las mascotas.
        data=adapted(raw,'astral_pet_golem_'+kind);data['name']=mid
        box=bounds_data(data)
        group=dict(name='mtag_nombre',uuid=str(uuid.uuid5(uuid.NAMESPACE_URL,mid+'/name')),
                   origin=[0,box[1][1]*16+3,0],children=[])
        data.setdefault('groups',[]).append({k:v for k,v in group.items() if k!='children'})
        data['outliner'].append(group)
        assert {'idle','walk','attack','death'} <= {a['name'] for a in data['animations']}
        write_json(out/'models'/f'{mid}.bbmodel',data)
        print(mid, 'alto',round(box[1][1]-box[1][0],3))
    files={}
    for key in ('pitchfork','barrel','wooden_bucket','wooden_wheel','wooden_wheel_blocking'):
        raw=json.loads((root/'x/barrel/BBcosmetics'/f'{key}.bbmodel').read_text('utf8'))
        generated=item_assets(raw)
        for path,blob in generated.items():
            new=path.replace('espada_heroe_errante','bbcosmetics_'+key)
            if path.endswith('.json'):blob=blob.replace(b'espada_heroe_errante',('bbcosmetics_'+key).encode())
            files[new]=blob
        model={'model':{'type':'minecraft:model','model':'privado:item/bbcosmetics_'+key}}
        files[f'assets/astral/items/cosmeticos/espalda_{key}.json']=json.dumps(model).encode()
        if key=='barrel':
            from arte_1611 import assets
            files.update(assets())
            gui=json.loads(files['assets/astral/items/barril_xp.json'])['model']
            files['assets/astral/items/barril_xp.json']=json.dumps({'model':{
                'type':'minecraft:select','property':'minecraft:display_context',
                'cases':[{'when':'gui','model':gui}],'fallback':model['model']}}).encode()
    for name,blob in files.items():
        p=out/'pack'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(blob)
    return out


if __name__=='__main__':prepare()
