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

    def test_model_identity_v4(self):
        # Death agrega rig/animacion; geometria, arte y animaciones anteriores intactos.
        import subprocess
        for name in ('astral_creeper_nuclear','astral_esq_nigromante'):
            with self.subTest(model=name):
                before=json.loads(subprocess.check_output(['git','show',f'6a8fef8:build/models/{name}.bbmodel'],cwd=ROOT))
                after=json.loads((ROOT/'build/models'/f'{name}.bbmodel').read_text())
                self.assertEqual(before['elements'],after['elements'])
                self.assertEqual(before['textures'],after['textures'])
                self.assertEqual(before['animations'],[a for a in after['animations'] if a['name']!='death'])

    def test_models_texture_density_and_pack(self):
        from mobs.tamanos import dimensions, scale
        import base64,io,zipfile
        from PIL import Image
        names=['astral_esq_'+k for k in WEIGHTS]+['astral_creeper_nuclear']
        with zipfile.ZipFile(ROOT/'build/AstralRPG-Textures.zip') as z:
            self.assertFalse(any('creeper_fantasma' in p for p in z.namelist()))
            for name in names:
                data=json.loads((ROOT/'build/models'/f'{name}.bbmodel').read_text())
                anim={a['name'] for a in data['animations']}
                self.assertTrue({'idle','walk','swell' if 'creeper' in name else 'attack'}<=anim)
                self.assertTrue(any(name in p for p in z.namelist()))
                # Esqueletos a 16 px/bloque; nuclear conserva 32 px/bloque.
                density=2 if "creeper" in name else 1
                for e in data['elements']:
                    uv=e['faces']['north']['uv']
                    self.assertGreaterEqual(uv[2]-uv[0],density*(e['to'][0]-e['from'][0])-.01)
                if 'creeper' not in name:
                    self.assertGreater(dimensions(name,1)[1],1.9)
                    self.assertGreaterEqual(1.99*scale(name,1,'SKELETON'),dimensions(name,1)[1])
                else:
                    im=Image.open(io.BytesIO(base64.b64decode(data['textures'][0]['source'].split(',')[1])))
                    self.assertFalse(any(0<a<255 for a in im.getchannel('A').get_flattened_data()))
                    png=z.read('assets/bettermodel/textures/item/'+name+'_'+name+'.png')
                    converted=Image.open(io.BytesIO(png))
                    self.assertEqual(im.convert('RGBA').tobytes(),converted.convert('RGBA').tobytes())
                    groups={g['name'] for g in data['groups']}
                    self.assertTrue({'face','head','body','leg0','leg1','leg2','leg3'}<=groups)

    def test_combat_and_nuclear_boundaries(self):
        for kind,hp in ((k,26 if k=='guardian' else 20) for k in WEIGHTS):
            m=self.mobs['astral_esq_'+kind]
            self.assertEqual(m['Health'],hp); self.assertTrue(m['Options']['Glowing'])
            self.assertTrue(any('meleeattack' in s for s in m['AIGoalSelectors']) or kind in ('arquero','nigromante'))
        nuclear=self.mobs['astral_creeper_nuclear']
        self.assertEqual(nuclear['Display'],'&e&lCreeper Nuclear')
        self.assertEqual(nuclear['Options']['ExplosionRadius'],6)
        self.assertFalse(nuclear['Options']['Glowing'])
        self.assertNotIn('astral_creeper_fantasma',self.mobs)
        sk=script(); self.assertIn('spawn reason is natural',sk)
        self.assertIn('name of world of event-entity is "world"',sk)
        self.assertIn('chance of 30%',sk); self.assertIn('damage * 2',sk)
        self.assertIn('brightness{pid=face;b=15;s=15} @self',self.skills['AST_NUCLEAR_MODELO']['Skills'])
        self.assertIn('brightness{b=15;s=15} @self',self.skills['AST_NUCLEAR_HINCHAR']['Skills'])
        self.assertTrue(any('particles{p=dust;color=#6f8a2f;' in s for s in nuclear['Skills']))
        self.assertIn('astral.nuclear',sk)
        self.assertIn('priority low',sk); self.assertIn('angle',sk)
        self.assertFalse(any('mm ' in v for p,v in self.files.items() if p.endswith('.mcfunction')))
        for d in catalog():
            if d['key']=='forja': self.assertNotIn('AST_ESQ_CONVIERTE',mob_yml(d))


if __name__=='__main__': unittest.main()
