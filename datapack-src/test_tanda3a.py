"""Regresiones de modelos, controlador real de oleadas y estatuas aisladas."""
from copy import deepcopy
import json
import math
from pathlib import Path
import unittest
import yaml
from mobs.mazmorra import MINA, mob_yml, skill_yml
from mobs.mazmorras_data import catalog
from mobs.tanda2 import generate
from mobs.tanda3a import plant, plant_skills, statues, PLANT_POINTS, PLANT_COUNTS
from mobs.tamanos import dimensions, scale, VANILLA
from mobs.terreno import clear
from test_oleadas_tanda2 import VM

ROOT=Path(__file__).resolve().parents[1]


class Tanda3aTests(unittest.TestCase):
    def test_guardian_keeps_health_phases_and_four_companions(self):
        boss=yaml.safe_load(mob_yml(MINA))['astral_mina_guardian']
        self.assertEqual(boss['Health'],72000)
        self.assertIn('Coloso Musgoso',boss['Display'])
        self.assertTrue(any('MINA_GUARDIAN_F2' in s for s in boss['Skills']))
        self.assertTrue(any('MINA_GUARDIAN_F3' in s for s in boss['Skills']))
        sk=yaml.safe_load(skill_yml(MINA))['MINA_MODELO_astral_mina_guardian']['Skills']
        self.assertIn('model{m=astral_coloso_musgoso;s=2.0} @self',sk)
        self.assertFalse(any('tint{' in s or 'golem_forja' in s for s in sk))
        self.assertEqual(MINA['rooms'][-1]['companions'],('ZOMBIE',4))

    def test_plant_uses_tier_roll_only_on_spawn_and_cannot_move(self):
        p=plant()['astral_bosque_planta']; opt=p['Options']; skills=plant_skills()
        self.assertEqual(p['Health'],40)
        for key,val in dict(NoAI=True,MovementSpeed=0,KnockbackResistance=1,Collidable=False,Glowing=True).items():
            self.assertEqual(opt[key],val)
        init=' '.join(skills['AST_PLANTA_INICIO']['Skills'])
        self.assertIn('function astral:mob/roll',init)
        self.assertIn('ad.vanilla',init)
        self.assertNotIn('mob/roll',' '.join(skills['AST_PLANTA_MODELO']['Skills']))
        self.assertTrue(any('~onTimer:30' in s and 'd=3' in s for s in p['Skills']))
        self.assertTrue(any('~onTimer:80' in s and 'd=12' in s for s in p['Skills']))
        self.assertIn('@PlayersInRadius{r=12}',skills['AST_PLANTA_ESCUPIR']['Skills'][1])
        self.assertIn('type=POISON;duration=60',' '.join(skills['AST_PLANTA_VENENO']['Skills']))

    def test_fixed_plants_count_for_cap_completion_and_reset(self):
        d=next(d for d in catalog() if d['key']=='bosque')
        sk=yaml.safe_load(skill_yml(d)); files={'data/astral/function/load.mcfunction':''}; generate(files)
        r=d['rooms'][0]; arrival=r['llegada']; tag='ad.bosque.sala1'
        recorded=[list(p) for p in r['spawn_points']]
        for pt in PLANT_POINTS:
            self.assertIn(list(pt),recorded)
            self.assertGreater(math.dist(pt,arrival),12)
            self.assertTrue(clear('bosque',*pt,1,3))
        for a in PLANT_POINTS:
            for b in PLANT_POINTS:
                if a!=b: self.assertGreater(math.dist(a,b),12)
        self.assertFalse(any('AST_PLANTAS' in s for s in sk['BOSQUE_SALA1_INICIO']['Skills']))
        for n,count in PLANT_COUNTS.items():
            steps=sk[f'BOSQUE_SALA1_OLA{n}']['Skills']
            i=steps.index(f'skill{{s=AST_PLANTAS_OLA{n}}} @self')
            self.assertIn(f'/wave{n}',steps[i+1])
            self.assertEqual(len(plant_skills()[f'AST_PLANTAS_OLA{n}']['Skills']),count)
            vm=VM(files,1); vm.tags.add('bosque.on')
            # Efecto de la skill de MythicMobs, antes de ejecutar la cola real.
            vm.alive=[{'type':'PLANTA','tags':[tag,tag+'.wave']} for _ in range(count)]
            vm.function(f'tanda2/bosque/sala1/wave{n}')
            self.assertEqual(len(vm.alive),6)
            for _ in range(150):
                vm.alive=[e for e in vm.alive if e['type']=='PLANTA']
                vm.function('tanda2/bosque/sala1/tick')
                self.assertLessEqual(len(vm.alive),6)
            self.assertFalse(vm.queue)
            self.assertIn('bosque.sala1.busy',vm.tags)
            vm.function('tanda2/bosque/sala1/reset'); self.assertFalse(vm.alive)
        for name,content in files.items():
            if name.endswith('.mcfunction'): self.assertNotIn('mm ',content)

    def test_statues_only_model_and_cancel_events(self):
        from mobs.mythic import MOBS
        for mid,p in statues().items():
            original='astral_'+mid.removeprefix('astral_estatua_')
            self.assertEqual(p['Type'],MOBS[original]['type'])
            self.assertNotIn('Drops',p); self.assertNotIn('BossBar',p)
            self.assertEqual(len(p['Skills']),4)
            for k in ('NoAI','Invincible','Silent','Persistent','NoGravity','PreventOtherDrops'):
                self.assertTrue(p['Options'][k])
            self.assertFalse(p['Options']['Collidable']); self.assertFalse(p['Options']['Despawn'])
            self.assertIn('cancelevent @self ~onDamaged',p['Skills'])
            self.assertIn('cancelevent @self ~onInteract',p['Skills'])
            self.assertTrue(all('addtag' not in s and 'AST_MODEL' not in s for s in p['Skills']))
        roll=(ROOT/'build/AstralRPG-Items/data/astral/function/mob/roll.mcfunction').read_text()
        self.assertIn('execute if data entity @s {Invulnerable:1b} run return 0',roll)

    def test_hitbox_and_animations_match_new_models(self):
        for model,s,entity,anims in (('astral_coloso_musgoso',2,'IRON_GOLEM',{'idle','walk','attack'}),
                                   ('astral_bosque_planta',1,'HUSK',{'idle','attack','spit'})):
            d=json.loads((ROOT/'build/models'/f'{model}.bbmodel').read_text())
            self.assertEqual({a['name'] for a in d['animations']},anims|{'death'})
            self.assertGreaterEqual(VANILLA[entity][1]*scale(model,s,entity),dimensions(model,s)[1])
            for a in d['animations']:
                for channel in a['animators'].values():
                    for key in channel['keyframes']:
                        self.assertNotRegex(str(key['data_points']),r'\d\.\d{8,}')

    def test_v2_dimensions_and_attack_bones(self):
        width,height,_=dimensions('astral_coloso_musgoso',2)
        self.assertGreater(width/height,.95)
        self.assertGreaterEqual(dimensions('astral_bosque_planta',1)[1],2.2)
        self.assertLessEqual(dimensions('astral_bosque_planta',1)[1],2.5)
        for model,bone in (('astral_coloso_musgoso','arm_r'),('astral_bosque_planta','jaw')):
            data=json.loads((ROOT/'build/models'/f'{model}.bbmodel').read_text())
            attack=next(a for a in data['animations'] if a['name']=='attack')
            self.assertEqual(attack['loop'],'once')
            self.assertIn(bone,{a['name'] for a in attack['animators'].values()})


if __name__=='__main__': unittest.main()
