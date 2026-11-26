"""Contrato de entrega: contenido generado y preservacion del FINAL instalado."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import yaml
from terceros import ROOT, privado
from correcciones_goblin import GOLEM_DUNGEONS, GOLEM_XP, MERCHANT, MERCHANT_SPECIAL, definitions
from tanda_xp import XP
from escala import DANO
from final_base import select_base


class CorreccionesTests(unittest.TestCase):
    def test_removed_crossbows_and_existing_crossbows(self):
        import re
        forbidden=re.compile(r'ballesta_(?:1|2|6|7|8|9|10)(?![0-9])')
        for name in ('AstralRPG-Items.zip','AstralRPG-Textures.zip'):
            with zipfile.ZipFile(ROOT/'build'/name) as z:
                for p in z.namelist():
                    self.assertIsNone(forbidden.search(p),p)
                    if p.endswith(('.json','.mcfunction')):
                        self.assertIsNone(forbidden.search(z.read(p).decode('utf8')),p)
                for t in (3,4,5):
                    self.assertTrue(any(f'/ballesta_{t}.json' in p for p in z.namelist()))

    def test_xp_probabilities_are_generated_for_every_tier(self):
        with zipfile.ZipFile(ROOT/'build/AstralRPG-Items.zip') as z:
            for t,values in GOLEM_XP.items():
                for iid,chance in zip(XP,values):
                    self.assertEqual(json.loads(z.read(f'data/astral/predicate/golems/t{t}/{iid}.json'))['chance'],chance)
                    if t>1:self.assertGreaterEqual(chance,GOLEM_XP[t-1][list(XP).index(iid)])

    def test_room_conversion_and_limits(self):
        from mobs.mazmorra import MINA
        from mobs.mazmorras_data import catalog
        from mobs.tanda2 import WAVES
        mobs,skills=definitions()
        for d in [MINA]+catalog():
            if d['key'] not in GOLEM_DUNGEONS:continue
            key=d['key'];kind=GOLEM_DUNGEONS[key]
            for room,original in zip(d['rooms'],WAVES[key]):
                for wave,old in zip(room['oleadas'],original):
                    self.assertEqual(sum(n for _,n,_ in wave),sum(n for _,n in old))
                    self.assertIn(next(n for m,n,_ in wave if m=='ASTRAL_GOLEM'),range(2,5))
                mid=f'astral_golem_{kind}_{key}_{room["id"]}'
                self.assertIn(mid,mobs)
                startup=skills[f'AST_GOLEM_INICIO_{key}_{room["id"]}']['Skills']
                self.assertTrue(any('astral:mob/roll' in s for s in startup))
                self.assertTrue(any(f'ad.{key}.{room["id"]}.wave' in s for s in startup))
        for file in ('bosque','cumbre','mazmorra'):
            data=yaml.safe_load((ROOT/f'build/mythicmobs/mobs/{file}.yml').read_text('utf8'))
            for mob in data.values():
                for skill in mob.get('Skills',[]):
                    if 'AST_GOLEM_CONVIERTE_' in skill:
                        name=skill.split('s=',1)[1].split(';',1)[0]
                        self.assertIn(name,skills)

    def test_merchant_neutral_and_special_catalog(self):
        mobs,_=definitions();mob=mobs['astral_goblin_vendedor']
        self.assertEqual(mob['AITargetSelectors'],['clear'])
        self.assertFalse(any('steal' in s.lower() for s in mob['Skills']))
        self.assertTrue(set(XP)<=set(iid for iid,_,_ in MERCHANT))
        self.assertIn('llave_cosmeticos',MERCHANT_SPECIAL)
        self.assertNotIn('cosmetico_balde',MERCHANT_SPECIAL)
        with zipfile.ZipFile(ROOT/'build/runtime/AstralDecor.jar') as z:
            data=json.loads(z.read('mercader.json'))
            for iid,price,stock in MERCHANT:
                self.assertEqual((data[iid]['price'],data[iid]['stock']),(price,stock))

    def test_hero_tier_damage_recipe_and_ability(self):
        with zipfile.ZipFile(ROOT/'build/AstralRPG-Items.zip') as z:
            c=json.loads(z.read('data/astral/loot_table/item/espada_heroe_errante.json'))['pools'][0]['entries'][0]['functions'][0]['components']
            damage=next(a['amount'] for a in c['minecraft:attribute_modifiers'] if a['type']=='minecraft:attack_damage')+1
            self.assertEqual(damage,DANO[2])
            self.assertIn('Giro del Heroe',str(c))
            self.assertIn('Valor del Heroe',str(c))
        recipes=json.loads((ROOT/'build/runtime/mesa.json').read_text('utf8'))
        self.assertIn('espada_heroe_errante',str(recipes))
        script=(ROOT/'build/gameplay/astral_armas_especiales.sk').read_text('utf8')
        self.assertIn('asw_area({_p}, location of {_p}, 3, {_heroDamage}',script)
        self.assertNotIn('__HERO_MEJORAS__',script)

    def test_infinita_tenth_wave_reserves_three_slots(self):
        text=(ROOT/'build/infinita/astral_infinita.sk').read_text('utf8')
        self.assertIn('set {-inf.olas::%{_n}%} to 0',text)
        self.assertIn('if mod({-inf.olas::%{_n}%}, 10) is 0:',text)
        pending=text.split('if {-inf.golems::%{_n}%} is true:',1)[1].split('    loop {_pj} times:',1)[0]
        self.assertLess(pending.index('if {_vivos} + 3 <= {_tope}:'),pending.index('inf_golems({_n})'))
        special=text.split('function inf_golems(n: text):',1)[1].split('function inf_spawn(',1)[0]
        self.assertEqual(special.count('mm mobs spawn astral_golem_'),3)
        for kind in ('bosque','hielo','cristal'):self.assertIn('astral_golem_'+kind+'_infinita',special)
        self.assertIn('function astral:inf/apply/t%{_t}%',special)

    def test_base_rejects_stale_default_and_allows_explicit(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'.local') as tmp:
            root=Path(tmp);folder=root/'build/entregas'
            for name in ('old','new'):
                p=folder/name/'AstralRPG-Textures.zip';p.parent.mkdir(parents=True);p.write_bytes(b'x')
            import os
            old=folder/'old/AstralRPG-Textures.zip';new=folder/'new/AstralRPG-Textures.zip'
            os.utime(old,(10,10));os.utime(new,(20,20))
            with patch('final_base.privado',return_value=root):
                self.assertEqual(select_base(),new)
                with self.assertRaisesRegex(ValueError,'Base antigua'):select_base(old)
                self.assertEqual(select_base(old,explicit=old),old.resolve())

    def test_final_keeps_installed_entries_and_crossbows(self):
        folder=privado()/'build/entregas/correcciones-goblin-golems'
        if not (folder/'delta.json').exists():self.skipTest('Falta generar FINAL privado')
        delta=json.loads((folder/'delta.json').read_text('utf8'))
        changed=set().union(*(delta[k] for k in ('public_delta','private_delta','balance_delta','converted','removed')))
        changed.update(p.relative_to(folder/'pack').as_posix() for p in (folder/'pack').rglob('*') if p.is_file())
        base=privado()/'build/entregas/arreglos-16-11/AstralRPG-Textures.zip'
        self.assertTrue(hashlib.sha1(base.read_bytes()).hexdigest().startswith('4322b8ca'))
        with zipfile.ZipFile(base) as before,zipfile.ZipFile(folder/'AstralRPG-Textures.zip') as after:
            for name in set(before.namelist())-changed:
                self.assertEqual(before.read(name),after.read(name),name)
            for kind in ('bosque','hielo','cristal'):
                self.assertTrue(any('golem_'+kind in n and '/models/' in n for n in after.namelist()))
            old=json.loads(before.read('assets/minecraft/font/default.json'))['providers']
            new=json.loads(after.read('assets/minecraft/font/default.json'))['providers']
            def glyphs(providers):
                return set().union(*(set(p.get('advances',{}))|set(''.join(p.get('chars',[]))) for p in providers))
            self.assertLessEqual(glyphs(old),glyphs(new))
            # Conservar exactamente las definiciones privadas de cofres/barril.
            for provider in old:
                if 'container/chests/' in provider.get('file',''):self.assertIn(provider,new)


if __name__=='__main__':unittest.main()
