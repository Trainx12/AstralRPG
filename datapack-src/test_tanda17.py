import io
import json
import unittest
import zipfile
import numpy as np
import yaml
from PIL import Image
from panorama import ROOT, direction, face_image
from terceros import privado
from deploy_tanda17 import NAME, BASE_SHA1


class Tanda17Tests(unittest.TestCase):
    def test_cube_edges(self):
        v=np.linspace(-1,1,31);one=np.ones_like(v)
        for f in range(4):
            np.testing.assert_allclose(direction(f,one,v),direction((f+1)%4,-one,v))
        np.testing.assert_allclose(direction(0,v,-one),direction(4,v,one))
        np.testing.assert_allclose(direction(0,v,one),direction(5,v,-one))

    def test_projection_longitude_and_poles(self):
        a=np.zeros((128,256,3),dtype=np.uint8)
        a[:,:,0]=np.arange(256);a[:,:,1]=np.arange(128)[:,None]*2
        face=np.asarray(face_image(Image.fromarray(a),0,64))
        self.assertTrue(abs(int(face[32,32,0])-128)<4)
        self.assertTrue(abs(int(face[32,32,1])-128)<4)

    def test_public_pack_and_selectors(self):
        with zipfile.ZipFile(ROOT/'build/AstralRPG-Textures.zip') as z:
            for n in range(6):self.assertEqual(Image.open(io.BytesIO(z.read(f'assets/minecraft/textures/gui/title/background/panorama_{n}.png'))).size,(1024,1024))
        with zipfile.ZipFile(ROOT/'build/AstralRPG-Items.zip') as z:
            self.assertIn('tag=!astral.pet',z.read('data/astral/function/spell/ray.mcfunction').decode())

    def test_private_final_delta(self):
        folder=privado()/'build/entregas'/NAME
        report=json.loads((folder/'delta.json').read_text('utf8'))
        self.assertEqual(report['base_sha1'],BASE_SHA1)
        with zipfile.ZipFile(folder/'AstralRPG-Textures.zip') as new,zipfile.ZipFile(privado()/'build/entregas/pack-17-11/AstralRPG-Textures.zip') as old:
            for n in old.namelist():
                if n not in report['changed']:self.assertEqual(old.read(n),new.read(n),n)
            barrel=json.loads(new.read('assets/astral/items/barril_xp.json'))['model']
            self.assertEqual(barrel['type'],'minecraft:model')
            self.assertNotIn('fallback',barrel)
        private=yaml.safe_load((folder/'mythicmobs/skills/mascotas.yml').read_text('utf8'))
        self.assertGreaterEqual(report['private_pet_variants'],18)
        for key,value in private.items():
            if key.startswith('PET_MODELO_'):
                self.assertIn('addtag{tag=astral.pet} @self',value['Skills'])
                self.assertTrue(any('Invulnerable:1b' in s for s in value['Skills']))


if __name__=='__main__':unittest.main()
