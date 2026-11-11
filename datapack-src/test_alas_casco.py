"""Regresion de entrega aislada, migracion sin perdida y geometria privada."""
import io
import itertools
import json
import subprocess
import unittest
import zipfile
from terceros import ROOT, privado
from tanda4b_privado import rotate


class AlasCascoTests(unittest.TestCase):
    def test_datapack_changes_only_helmet_and_targeted_migration(self):
        previous=subprocess.check_output(['git','show','75f49c4fde2f39faeb178f4b364da02b9c5bf8a6:build/AstralRPG-Items.zip'],cwd=ROOT)
        with zipfile.ZipFile(io.BytesIO(previous)) as old, zipfile.ZipFile(ROOT/'build/AstralRPG-Items.zip') as new:
            added=set(new.namelist())-set(old.namelist())
            self.assertEqual(added,{'data/astral/item_modifier/carnivora_head.json','data/astral/function/upgrade/carnivora_head.mcfunction'})
            self.assertTrue(set(old.namelist())<=set(new.namelist()))
            changed=[n for n in old.namelist() if old.read(n)!=new.read(n)]
            for n in changed:
                if n.endswith('.json'):
                    a=json.loads(old.read(n));b=json.loads(new.read(n))
                    self.assertIn('carnivora_helmet',old.read(n).decode())
                    def repair(value):
                        if isinstance(value,dict):
                            eq=value.get('minecraft:equippable')
                            if eq and eq.get('slot')=='head':eq.pop('asset_id',None)
                            for v in value.values():repair(v)
                        elif isinstance(value,list):
                            for v in value:repair(v)
                    repair(a);self.assertEqual(a,b,n)
                else:
                    self.assertTrue(n=='data/astral/function/upgrade/check.mcfunction' or '/upgrade/' in n and n.endswith('/carnivora_helmet.mcfunction'),n)
            modifier=json.loads(new.read('data/astral/item_modifier/carnivora_head.json'))
            self.assertEqual(modifier,{'function':'minecraft:set_components','components':{'minecraft:equippable':{'slot':'head'}}})
            self.assertTrue(new.read('data/astral/function/upgrade/check.mcfunction').startswith(b'function astral:upgrade/carnivora_head\n'))

    def test_final_preserves_cosmetics_and_every_other_asset(self):
        folder=privado()/'build/entregas'
        with zipfile.ZipFile(folder/'cosmeticos-skins/AstralRPG-Textures.zip') as old,zipfile.ZipFile(folder/'alas-casco/AstralRPG-Textures.zip') as new:
            self.assertEqual(old.namelist(),new.namelist())
            changed={n for n in old.namelist() if old.read(n)!=new.read(n)}
            self.assertEqual(changed,{f'assets/astral/models/cosmetics/{i}_alas.json' for i in ('asura','carnivora')})
            helmet=json.loads(new.read('assets/elitecreatures/models/carnivoret_weapon_set/hat.json'))
            self.assertIn('head',helmet['display'])
            self.assertGreater(min(helmet['display']['head']['scale']),0)

    def test_both_wing_tips_above_shoulders_and_geometry_behind_back(self):
        with zipfile.ZipFile(privado()/'build/entregas/alas-casco/AstralRPG-Textures.zip') as pack:
            for iid in ('asura_alas','carnivora_alas'):
                wrapper=json.loads(pack.read(f'assets/astral/models/cosmetics/{iid}.json'))
                ns,model=wrapper['parent'].split(':');raw=json.loads(pack.read(f'assets/{ns}/models/{model}.json'))
                fixed=wrapper['display']['fixed'];points=[]
                for e in raw['elements']:
                    for p in itertools.product(*zip(e['from'],e['to'])):
                        if r:=e.get('rotation'):p=rotate(p,r['origin'],r['axis'],r['angle'])
                        p=rotate([(v-8)*fixed['scale'][a] for a,v in enumerate(p)],[0,0,0],'y',fixed['rotation'][1])
                        points.append([p[a]+fixed['translation'][a] for a in range(3)])
                self.assertAlmostEqual(max(p[1] for p in points)/16,.65,places=5)
                self.assertAlmostEqual(max(p[2] for p in points),0,places=4)
                self.assertAlmostEqual(max(p[0] for p in points)+min(p[0] for p in points),0,places=4)


if __name__=='__main__':unittest.main()
