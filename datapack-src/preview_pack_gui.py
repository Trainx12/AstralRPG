"""Render CPU de las definiciones GUI del ZIP FINAL, no de los bbmodel originales."""
import base64
from copy import deepcopy
import json
import tempfile
import zipfile
from terceros import privado
from preview_tanda4b import java_model
from build_privado import preview


def main():
    base=privado()/'build';models={}
    with tempfile.TemporaryDirectory(dir=base) as folder:
        from pathlib import Path
        root=Path(folder)
        with zipfile.ZipFile(base/'AstralRPG-Textures.zip') as z:
            for n in z.namelist():
                if n.startswith(('assets/elitecreatures/','assets/asura/','assets/nogs_menagerie/','assets/privado/','assets/astral/items/')):
                    p=root/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(n))
            for n in z.namelist():
                if not n.startswith('assets/astral/items/') or not n.endswith('.json'):continue
                iid=Path(n).stem
                if not iid.startswith(('carnivora_','asura_moneda_','asura_espada','asura_alas','peluche_','espada_heroe_errante')):continue
                tree=json.loads(z.read(n))['model']
                while not isinstance(tree.get('model'),str):tree=tree.get('on_false',tree.get('fallback',{}))
                ref=tree['model'];ns,name=ref.split(':',1)
                raw=json.loads((root/'assets'/ns/'models'/f'{name}.json').read_text())
                data=java_model(ref,root/'assets')
                if not data['elements']:
                    # Iconos generados: la capa PNG declarada por el modelo del pack.
                    texture=raw['textures']['layer0'];tn,tp=texture.split(':',1)
                    data={'textures':[dict(source='data:image/png;base64,'+base64.b64encode((root/'assets'/tn/'textures'/f'{tp}.png').read_bytes()).decode(),uv_width=16,uv_height=16)],
                          'elements':[dict(uuid='plane',type='cube',**{'from':[0,0,8],'to':[16,16,8]},faces={'north':dict(texture=0,uv=[0,0,16,16])})],
                          'outliner':[dict(uuid='root',name='root',children=['plane'])]}
                    gui={}
                else:gui=raw.get('display',{}).get('gui',{})
                scale=gui.get('scale',[1]*3);translation=gui.get('translation',[0]*3)
                for e in data['elements']:
                    for field in ('from','to','origin'):
                        if field in e:e[field]=[8+(v-8)*s+t for v,s,t in zip(e[field],scale,translation)]
                data['outliner'][0].update(origin=[8+t for t in translation],rotation=gui.get('rotation',[0,0,0]))
                models[iid]=data
    preview(models,'urgente-gui-desde-pack',include_sword=False,gui=True)
    print('Render CPU GUI privado desde ZIP FINAL:',len(models),'items')


if __name__=='__main__':main()
