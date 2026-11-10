"""Regresion del relevo cola -> Mythic, probabilidades, assets y limites de mundo."""
from collections import Counter
import json
from pathlib import Path
import re
import unittest
import yaml
from mobs.tanda3b import definitions, script, WEIGHTS
from mobs.tanda2 import generate, path, expanded
from mobs.mazmorra import MINA, mob_yml
from mobs.mazmorras_data import catalog
from test_oleadas_tanda2 import VM

ROOT=Path(__file__).resolve().parents[1]


class Tanda3bTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mobs,cls.skills=definitions()
        cls.ds=[MINA]+[d for d in catalog() if d['key'] not in ('santuario','forja')]
        cls.files={'data/astral/function/load.mcfunction':''}; generate(cls.files)

    def test_generated_weights_and_every_room_identity(self):
        for d in self.ds:
            key=d['key']; controls=yaml.safe_load(mob_yml(d))
            for r in d['rooms']:
                room=r['id']; skill=self.skills[f'AST_ESQ_CONVIERTE_{key}_{room}']
                self.assertEqual(skill['TargetConditions'],[f'hastag{{tag=ad.esq.{key}.{room}}} true'])
                lines=skill['Skills']
                self.assertTrue(lines[0].startswith('removetag{'))  # consumido antes de summon diferido
                self.assertEqual(lines[-1],'remove{sync=true}')
                self.assertFalse(any('@self' in s for s in lines))  # nunca borrar el controlador
                choices=re.search(r'randomskill\{s=(.*);sync=true}',lines[1])[1].split(',')
                weights=Counter()
                for choice in choices:
                    name,n=choice.split(); kind=name.split('_')[-1]; weights[kind]=int(n)
                    summon=self.skills[name]['Skills'][0]
                    mid=re.search(r'type=([^;]+)',summon)[1]
                    init=self.mobs[mid]['Skills'][0]
                    initname=re.search(r's=([^}]+)',init)[1]
                    tags=self.skills[initname]['Skills']
                    suffix='companion' if r.get('boss_room') else 'wave'
                    self.assertIn(f'addtag{{tag=ad.{key}.{room}.{suffix}}} @self',tags)
                    self.assertEqual(sum('mob/roll' in s for s in tags),1)
                    self.assertFalse(any('mob/roll' in s and '~onLoad' in s for s in self.mobs[mid]['Skills']))
                self.assertEqual(dict(weights),WEIGHTS)
                self.assertEqual(sum(weights.values()),100)
                self.assertTrue(any(s.startswith('foreach{') and f'AST_ESQ_CONVIERTE_{key}_{room}' in s and 'sync=true' in s and '~onTimer:5' in s for s in controls[f'astral_{key}_control_{room}']['Skills']))

    def test_reservations_keep_skeleton_totals_and_caps_for_1_2_5(self):
        for d in self.ds:
            for r in d['rooms'][:-1]:
                for n,wave in enumerate(r['oleadas'],1):
                    for players in (1,2,5):
                        vm=VM(self.files,players); vm.tags.add(d['key']+'.on'); p=path(d,r)
                        vm.function(p+f'/wave{n}')
                        for _ in range(150):
                            self.assertLessEqual(sum('ad.'+d['key']+'.'+r['id']+'.wave' in e['tags'] for e in vm.alive),6)
                            # Todos los tipos de esqueleto reservan una plaza; el relevo no agrega plazas.
                            for e in vm.alive:
                                if e['type'] in ('SKELETON','STRAY'):
                                    self.assertIn(f'ad.esq.{d["key"]}.{r["id"]}',e['tags'])
                            vm.alive=[e for e in vm.alive if '.wave' not in ' '.join(e['tags'])]
                            for _ in range(5): vm.function(p+'/tick')
                            if not vm.queue: break
                        got=Counter(e['type'] for e in vm.spawned if any(t.endswith('.wave') for t in e['tags']))
                        self.assertEqual(got,Counter(expanded(wave,players)))

    def test_models_textures_alpha_and_pack(self):
        from mobs.tamanos import dimensions, scale
        import base64,io,zipfile
        from PIL import Image
        names=['astral_esq_'+k for k in WEIGHTS]+['astral_creeper_fantasma']
        with zipfile.ZipFile(ROOT/'build/AstralRPG-Textures.zip') as z:
            for name in names:
                data=json.loads((ROOT/'build/models'/f'{name}.bbmodel').read_text())
                anim={a['name'] for a in data['animations']}
                self.assertTrue({'idle','walk','swell' if 'creeper' in name else 'attack'}<=anim)
                self.assertTrue(any(name in p for p in z.namelist()))
                if 'creeper' not in name:
                    self.assertGreater(dimensions(name,1)[1],1.9)
                    self.assertLess(scale(name,1,'SKELETON'),1.3)
                else:
                    im=Image.open(io.BytesIO(base64.b64decode(data['textures'][0]['source'].split(',')[1])))
                    self.assertTrue(any(0<a<255 for a in im.getchannel('A').get_flattened_data()))
                    png=z.read('assets/bettermodel/textures/item/'+name+'_'+name+'.png')
                    converted=Image.open(io.BytesIO(png))
                    self.assertTrue(any(0<a<255 for a in converted.getchannel('A').get_flattened_data()))

    def test_combat_and_ghost_boundaries(self):
        for kind,hp in ((k,26 if k=='guardian' else 20) for k in WEIGHTS):
            m=self.mobs['astral_esq_'+kind]
            self.assertEqual(m['Health'],hp); self.assertTrue(m['Options']['Glowing'])
            self.assertTrue(any('meleeattack' in s for s in m['AIGoalSelectors']) or kind in ('arquero','nigromante'))
        ghost=self.mobs['astral_creeper_fantasma']
        self.assertEqual(ghost['Options']['ExplosionRadius'],12)
        self.assertFalse(ghost['Options']['Glowing'])
        sk=script(); self.assertIn('spawn reason is natural',sk)
        self.assertIn('name of world of event-entity is "world"',sk)
        self.assertIn('chance of 30%',sk); self.assertIn('damage * 4',sk)
        self.assertIn('priority low',sk); self.assertIn('angle',sk)
        self.assertFalse(any('mm ' in v for p,v in self.files.items() if p.endswith('.mcfunction')))
        for d in catalog():
            if d['key']=='forja': self.assertNotIn('AST_ESQ_CONVIERTE',mob_yml(d))


if __name__=='__main__': unittest.main()
