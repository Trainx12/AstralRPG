"""Contratos de entrega: arte privado aislado, head intacto y sonidos conservados."""
import io
import json
import unittest
import zipfile
import subprocess

import numpy as np
import yaml
from PIL import Image

import cascos_planos as C
from deploy_cascos_silencio import BASE, OUT, ROOT, pack, refs
from mobs.silencio import modeled_mobs, silence


class CascosSilencio(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.before=pack(BASE);cls.after=pack(OUT/'AstralRPG-Textures.zip')

    def test_delta_preserva_panorama_barril_y_resto(self):
        delta=json.loads((OUT/'delta.json').read_bytes())
        changed={n for n,b in self.after.items() if self.before.get(n)!=b}
        self.assertEqual(changed,set(delta['changed']))
        self.assertFalse(set(self.before)-set(self.after))
        self.assertEqual(delta['icons'],48)
        self.assertEqual(delta['preview_icons'],48)
        for n in changed:
            self.assertIn('/cascos_planos/',n) # Solo PNG y modelo plano (gui_light).

    def test_head_contextos_condiciones_y_paleta(self):
        count=0
        for n,b in self.after.items():
            if '/textures/item/cascos_planos/' in n and n.endswith('.png'):
                im=Image.open(io.BytesIO(b)).convert('RGBA');a=np.array(im)
                self.assertEqual(im.size,(32,32));self.assertEqual(set(np.unique(a[...,3])),{0,255})
                box=im.getbbox();self.assertTrue(all(x>=1 for x in box[:2]));self.assertTrue(all(x<=31 for x in box[2:]))
                self.assertGreaterEqual(max(box[2]-box[0],box[3]-box[1]),29)
                self.assertLessEqual(len(set(map(tuple,a[a[...,3]>0,:3]))),25)
                count+=1
            if n.startswith('assets/astral/items/') and n.endswith('.json') and n in self.before:
                old=json.loads(self.before[n]);new=json.loads(b)
                self.assertEqual(old,new,n) # Incluso contextos y condiciones: solo cambian modelos/PNG.
        self.assertEqual(count,48)

    def test_silencio_publico_y_privado_y_sonidos_intactos(self):
        skills={}
        for p in (ROOT/'build/mythicmobs/skills').glob('*.yml'):
            skills.update(yaml.safe_load(p.read_text('utf8')) or {})
        total=0
        for folder in (ROOT/'build/mythicmobs/mobs',OUT/'mythicmobs/mobs'):
            for p in folder.glob('*.yml'):
                mobs=yaml.safe_load(p.read_text('utf8')) or {}
                for mid in modeled_mobs(mobs,skills):
                    self.assertIs(mobs[mid]['Options']['Silent'],True,(p,mid));total+=1
        self.assertGreater(total,200)
        # No se edita ninguna skill; en cada mob publico solo cambia Options.Silent.
        for p in (ROOT/'build/mythicmobs/mobs').glob('*.yml'):
            previous=subprocess.run(['git','show','HEAD:'+p.relative_to(ROOT).as_posix()],capture_output=True,check=True).stdout
            old=yaml.safe_load(previous);new=yaml.safe_load(p.read_text('utf8'))
            for mid in old:
                if new[mid].get('Options',{}).get('Silent') is True:
                    old[mid].setdefault('Options',{})['Silent']=True
            self.assertEqual(old,new,p)

    def test_resolver_ciclos_y_excepcion_vanilla(self):
        mobs={'custom':{'Skills':['skill{s=a} @self']},'vanilla':{'Type':'ZOMBIE'}}
        skills={'a':{'Skills':['skill{s=b} @self']},'b':{'Skills':['skill{s=a} @self','model{m=propio} @self','sound{s=custom.hurt} @self']}}
        original=json.dumps(skills)
        self.assertEqual(silence(mobs,skills),{'custom'})
        self.assertEqual(json.dumps(skills),original)
        self.assertNotIn('Options',mobs['vanilla'])


if __name__=='__main__':unittest.main()
