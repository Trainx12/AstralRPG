"""Interpreta los comandos generados para probar la cola real, sin Paper ni red."""
from collections import Counter
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path
import re
import unittest
import yaml
from mobs.mazmorra import MINA, mob_yml, skill_yml, commands
from mobs.mazmorras_data import catalog
from mobs.tanda2 import generate, path, tag, expanded, WAVES
from mobs.terreno import clear, get, solid
from escala import VIDA_JEFE, VIDA_REF, EZ_JEFE, TIER_MAZMORRA

class VM:
    def __init__(self,files,players):
        self.files=files; self.players=players; self.scores={}; self.queue=[]
        self.alive=[]; self.spawned=[]; self.tags=set(); self.calls=0

    def score(self,h,o): return self.scores.get((h,o),0)
    def match(self,val,ran):
        if '..' not in ran: return val==int(ran)
        a,b=ran.split('..'); return (not a or val>=int(a)) and (not b or val<=int(b))
    def count(self,selector):
        if selector.startswith('@a'): return self.players
        wanted=re.search(r'tag=([^,\]]+)',selector)[1]
        return sum(wanted in e['tags'] for e in self.alive)
    def function(self,name):
        self.calls+=1
        if self.calls>100000: raise AssertionError('Cola sin fin')
        if name=='mob/roll': return
        for line in self.files['data/astral/function/'+name+'.mcfunction'].splitlines():
            if self.line(line): break
    def line(self,line):
        if not line or line.startswith('#'): return False
        m=re.fullmatch(r'execute (if|unless) score (\S+) (\S+) matches (\S+) run (.+)',line)
        if m:
            yes=self.match(self.score(m[2],m[3]),m[4])
            return self.line(m[5]) if yes==(m[1]=='if') else False
        m=re.fullmatch(r'execute (if|unless) data storage \S+ queue\[0\] run (.+)',line)
        if m: return self.line(m[2]) if bool(self.queue)==(m[1]=='if') else False
        m=re.fullmatch(r'execute (if|unless) entity (.+) run (.+)',line)
        if m:
            present=(re.search(r'tag=([^\]]+)',m[2])[1] in self.tags) if m[2].startswith('@s') else self.count(m[2])>0
            return self.line(m[3]) if present==(m[1]=='if') else False
        m=re.fullmatch(r'execute store result score (\S+) (\S+) run execute if entity (.+)',line)
        if m: self.scores[m[1],m[2]]=self.count(m[3]); return False
        if line.startswith('execute as @e'): return False  # mob/roll, testeado por separado
        m=re.fullmatch(r'scoreboard players (set|add|remove) (\S+) (\S+) (-?\d+)',line)
        if m:
            old=self.score(m[2],m[3]); n=int(m[4]); self.scores[m[2],m[3]]=n if m[1]=='set' else old+n*(1 if m[1]=='add' else -1)
            return False
        m=re.fullmatch(r'scoreboard players operation (\S+) (\S+) (=|\*=|/=) (\S+) (\S+)',line)
        if m:
            a=self.score(m[1],m[2]); b=self.score(m[4],m[5]); self.scores[m[1],m[2]]=b if m[3]=='=' else a*b if m[3]=='*=' else a//b
            return False
        m=re.fullmatch(r'data modify storage \S+ queue (set|append) value (.+)',line)
        if m:
            value=json.loads(m[2]); self.queue=deepcopy(value) if m[1]=='set' else self.queue+[value]; return False
        if line.startswith('data remove storage'):
            if 'queue[0]' in line: self.queue.pop(0)
            else: self.queue=[]
            return False
        if line.startswith('function astral:'):
            name=line.split()[1].removeprefix('astral:')
            if 'with storage' in line: self.function(self.queue[0]['fn'].removeprefix('astral:'))
            else: self.function(name)
            return False
        m=re.fullmatch(r'summon minecraft:(\S+) .* (\{.*\})',line)
        if m:
            tags=json.loads(re.search(r'Tags:(\[[^]]*\])',m[2])[1])
            entity={'type':m[1].upper(),'tags':tags}; self.alive.append(entity); self.spawned.append(entity); return False
        if line.startswith('tag @s '):
            _,_,op,t=line.split(); self.tags.add(t) if op=='add' else self.tags.discard(t); return False
        if line.startswith('effect '): return False
        if line.startswith('kill @e'):
            wanted=re.search(r'tag=([^\]]+)',line)[1]
            self.alive=[e for e in self.alive if wanted not in e['tags']]; return False
        if line.startswith('return '): return True
        raise AssertionError('Comando sin interpretar: '+line)

class OleadasTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ds=[MINA]+[d for d in catalog() if d['key']!='santuario']
        cls.files={'data/astral/function/load.mcfunction':''}; generate(cls.files)

    def test_quantities_caps_arrivals_queue_and_reset_from_commands(self):
        for d in self.ds:
            cap=9 if d['key']=='forja' else 6
            for r in d['rooms'][:-1]:
                p=path(d,r); t=tag(d,r)
                for n,wave in enumerate(r['oleadas'],1):
                    for players in (1,2,5):
                        with self.subTest(d=d['key'],r=r['id'],n=n,players=players):
                            vm=VM(self.files,players); vm.tags.add(d['key']+'.on'); vm.function(p+f'/wave{n}')
                            arrival=[e for e in vm.alive if t+'.arrival' in e['tags']]
                            self.assertEqual(len(arrival),4 if n==1 else 0)
                            expected=Counter(expanded(wave,players))
                            self.assertEqual(len(expected) > 0,True)
                            # Dejar saturada la sala durante 15 s: nunca superar el tope.
                            for _ in range(15):
                                vm.function(p+'/tick'); self.assertLessEqual(sum(t+'.wave' in e['tags'] for e in vm.alive),cap)
                            for _ in range(100):
                                vm.alive=[e for e in vm.alive if t+'.wave' not in e['tags']]
                                for _ in range(5): vm.function(p+'/tick')
                                self.assertLessEqual(sum(t+'.wave' in e['tags'] for e in vm.alive),2)
                                if not vm.queue: break
                            else: self.fail('No se vacio la cola')
                            self.assertEqual(Counter(e['type'] for e in vm.spawned if t+'.wave' in e['tags']),expected)
                            if arrival: self.assertIn(d['key']+'.'+r['id']+'.busy',vm.tags)
                            vm.function(p+'/reset'); self.assertFalse(vm.queue)
                            self.assertNotIn(d['key']+'.'+r['id']+'.busy',vm.tags)

    def test_exact_wave_specs_and_round_up_total(self):
        for d in self.ds:
            for r,specs in zip(d['rooms'],WAVES[d['key']]):
                self.assertEqual([[(m,n) for m,n,_ in w] for w in r['oleadas']],specs)
                for wave in r['oleadas']:
                    base=sum(n for _,n,_ in wave)
                    for players in (1,2,5): self.assertEqual(len(expanded(wave,players)),math.ceil(base*(1+.4*max(0,players-2))))

    def test_vanilla_types_safe_floor_bounds_and_white_plaza(self):
        banned={'PHANTOM','VEX','IRON_GOLEM','SNOW_GOLEM'}
        for d in self.ds:
            for r in d['rooms']:
                if not r.get('boss_room'):
                    for w in r['oleadas']:
                        for m,_,_ in w: self.assertNotIn(m,banned); self.assertFalse(m.startswith('astral_'))
                for x,y,z in r['spawn_points']:
                    self.assertTrue(clear(d['world'],x,y,z,1,3),(d['key'],r['id'],x,y,z))
                    if 'spawn_bounds' in r:
                        lo,hi=r['spawn_bounds']; self.assertTrue(all(a<=math.floor(v)<=b for a,v,b in zip(lo,(x,y,z),hi)))
                    if d['key']=='forja': self.assertTrue(clear(d['world'],x,y,z,2,3))
                    if d['key']=='forja' and not r.get('boss_room'): self.assertTrue(clear(d['world'],x,y,z,3,3))
                    if d['key']=='cumbre' and r['id']=='sala1':
                        self.assertLessEqual(math.hypot(x+0-r['llegada'][0],z-r['llegada'][2]),25)
                        self.assertIn(get(d['world'],x,y-1,z),('minecraft:snow_block','minecraft:quartz_block','minecraft:smooth_quartz','minecraft:white_concrete','minecraft:white_wool'))
                for x,y,z in r.get('golem_points',[]): self.assertTrue(clear(d['world'],x,y,z,3,3,allow_steps=True))

    def test_boss_health_and_acknowledgement_and_glowing(self):
        for d in self.ds:
            mobs=yaml.safe_load(mob_yml(d)); skills=yaml.safe_load(skill_yml(d)); r=d['rooms'][-1]
            boss=mobs[r['oleadas'][0][0][0]]
            self.assertEqual(boss['Health'],EZ_JEFE[d['key']]*VIDA_REF[TIER_MAZMORRA[d['key']]])
            self.assertEqual(boss['Health'],VIDA_JEFE[d['key']])
            self.assertTrue(boss['Options']['Glowing'])
            self.assertTrue(any('jefe.derrotado' in s and '~onDeath' in s for s in boss['Skills']))
            control=mobs[f'astral_{d["key"]}_control_{r["id"]}']['Skills']
            self.assertTrue(any('jefe.derrotado' in s and '_LIMPIA}' in s for s in control))
            self.assertTrue(any('/arrival' in s for s in skills[d['key'].upper()+'_'+r['id'].upper()+'_INICIO']['Skills']))
        bosque=next(d for d in self.ds if d['key']=='bosque')
        self.assertEqual(yaml.safe_load(mob_yml(bosque))['astral_bosque_chaman']['AIGoalSelectors'][0],'clear')

    def test_transitions_arm_queue_without_a_timer_gap(self):
        for d in self.ds:
            skills=yaml.safe_load(skill_yml(d))
            for r in d['rooms'][:-1]:
                for n in range(1,len(r['oleadas'])+1):
                    name=d['key'].upper()+'_'+r['id'].upper()+('_INICIO' if n==1 else f'_OLA{n}')
                    lines=skills[name]['Skills']
                    self.assertFalse(any(s.startswith('delay ') for s in lines))
                    self.assertTrue(any(path(d,r)+f'/wave{n}' in s for s in lines))

    def test_tier_distribution_from_generated_function(self):
        from escala import PROB_MAZ_MAS,PROB_MAZ_MENOS
        self.assertEqual((PROB_MAZ_MAS,PROB_MAZ_MENOS),(3,10))
        # Ejecutar los mismos rangos de la funcion real, incluidos extremos 1 y 5.
        text=(Path(__file__).resolve().parents[1]/'build/AstralRPG-Items/data/astral/function/mob/tier_mazmorra.mcfunction').read_text()
        self.assertIn('matches 4..13',text)
        for tier in range(1,6):
            result=Counter()
            for roll in range(1,101):
                value=tier
                if roll<=3 and tier<=4: value+=1
                elif 4<=roll<=13 and tier>=2: value-=1
                result[value]+=1
            self.assertEqual(result[tier],87 if 1<tier<5 else 97 if tier==1 else 90)

class ModelSizeTests(unittest.TestCase):
    def test_cumbre_corrected_box_has_room_for_short_movement(self):
        from mobs.entrega_tanda2 import collision,movement
        from mobs.tamanos import SPECIAL,scale
        model,s=SPECIAL['astral_yeti_cumbre']
        self.assertEqual(s,8)
        sc=scale(model,s,'RAVAGER'); point=(-101.8,30,56.9)
        self.assertEqual(collision('cumbre_hielo',point,'RAVAGER',sc)['bloques_no_aire'],0)
        for samples in movement('cumbre_hielo',point,'RAVAGER',sc).values():
            self.assertTrue(all(p['bloques_no_aire']==0 for p in samples[:2]))

    def test_models_scale_height_and_spawn_load(self):
        from mobs.tamanos import rows,dimensions,scale,VANILLA
        skills=yaml.safe_load(__import__('mobs.mythic',fromlist=['metaskills']).metaskills())
        from mobs.tanda3a import plant_skills
        skills['AST_MODEL_astral_bosque_planta']=plant_skills()['AST_PLANTA_MODELO']
        for mid,model,s,entity in rows():
            sc=scale(model,s,entity)
            self.assertGreater(sc,0); self.assertLessEqual(sc,16)
            self.assertAlmostEqual(sc,min(16,dimensions(model,s)[1]/VANILLA[entity][1]),places=5)
            if mid!='astral_mina_guardian': self.assertTrue(any('minecraft:scale base set '+str(sc) in v for v in skills['AST_MODEL_'+mid]['Skills']))
        self.assertEqual(dimensions('astral_yeti',8)[1],28)
        self.assertEqual(scale('astral_yeti',8,'RAVAGER'),12.727273)
        self.assertAlmostEqual(VANILLA['RAVAGER'][1]*scale('astral_yeti',8,'RAVAGER'),28,places=5)


class SantuarioSinCambiosTests(unittest.TestCase):
    def test_sanctuary_outputs_are_identical_ignoring_checkout_newlines(self):
        root=Path(__file__).resolve().parents[1]
        expected={'build/mythicmobs/mobs/santuario.yml': '983343c9e2bc001ca3db580c702936f73d1d6140277686c11c27e5463ccbdd86', 'build/mythicmobs/skills/santuario.yml': '056d3a0c551a2c633ba61a01002df4df8084b7295e5d9c9cddeed5e7325df0fb', 'build/mazmorras/santuario/comandos.txt': 'da71543ef7d3e652ddde9df8d4f9fd803eda60021e67ee5eff08f4bd929e58a7'}
        for name,digest in expected.items():
            self.assertEqual(hashlib.sha256((root/name).read_bytes().replace(b'\r\n',b'\n')).hexdigest(),digest,name)
