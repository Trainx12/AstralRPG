"""Contratos de la tanda XP, progresion, probabilidades y modelos publicados."""
import json
from pathlib import Path
import unittest
import zipfile
import yaml
from items import CUCHILLOS, SWORDS, ARMOR_SETS
from items_t6_10 import BALLESTAS
from escala import DANO, CUCHILLO_DANO, CUCHILLO_VELOCIDAD
from tanda_xp import XP, PRECIOS, SUERTE_SEGUNDOS

ROOT=Path(__file__).resolve().parents[1]


class TandaXPTests(unittest.TestCase):
    def item(self,z,iid):
        return json.loads(z.read(f'data/astral/loot_table/item/{iid}.json'))['pools'][0]['entries'][0]['functions'][0]['components']

    def test_consumables_exact_and_runtime_catalog(self):
        self.assertEqual(XP,{'frasco_xp_gigante':550,'barril_xp':5500})
        self.assertEqual(SUERTE_SEGUNDOS,300)
        with zipfile.ZipFile(ROOT/'build/AstralRPG-Items.zip') as z, zipfile.ZipFile(ROOT/'build/runtime/AstralDecor.jar') as jar:
            self.assertEqual(json.loads(jar.read('consumibles.json'))['xp'],XP)
            for iid in PRECIOS:
                c=self.item(z,iid)
                self.assertEqual(c['minecraft:max_stack_size'],16)
                self.assertIn('astral:consumible',c['minecraft:custom_data'])
                self.assertEqual(c['minecraft:item_model'],'astral:'+iid)
            self.assertTrue(self.item(z,'manzana_esmeralda')['minecraft:food']['can_always_eat'])

    def test_knives_actual_attributes_and_recipes(self):
        self.assertEqual(len(CUCHILLOS),10)
        recipes=json.loads((ROOT/'build/runtime/mesa.json').read_text(encoding='utf8'))
        with zipfile.ZipFile(ROOT/'build/AstralRPG-Items.zip') as z:
            for t in range(1,11):
                c=self.item(z,f'cuchillo_{t}')
                attrs={a['type']:a['amount'] for a in c['minecraft:attribute_modifiers']}
                damage=attrs['minecraft:attack_damage']+1
                speed=attrs['minecraft:attack_speed']+4
                self.assertAlmostEqual(damage,DANO[t]*CUCHILLO_DANO,places=3)
                self.assertEqual(speed,CUCHILLO_VELOCIDAD)
                self.assertLess(damage,DANO[t]);self.assertGreater(speed,1.6)
                self.assertLess(damage*speed,DANO[t]*1.6)
                self.assertIn('CUCHILLO',str(c['minecraft:lore']))
                self.assertIn('auraskills:fighting',c['minecraft:custom_data'])
                recipe=next(r for r in recipes if r['output']==f'cuchillo_{t}')
                if t>1:self.assertIn(['c',f'cuchillo_{t-1}',1],recipe['ingredients'])

    def test_crossbows_and_archer_complete(self):
        self.assertEqual(sorted(BALLESTAS),list(range(1,11)))
        self.assertEqual(len(ARMOR_SETS['arquero']['tiers']),10)
        with zipfile.ZipFile(ROOT/'build/AstralRPG-Items.zip') as z:
            charge=json.loads(z.read('data/astral/enchantment/carga_rapida.json'))['effects']['minecraft:crossbow_charge_time']
            self.assertIsInstance(charge,dict)
            self.assertEqual(len(charge['value']['values']),10)
            for t,b in BALLESTAS.items():
                c=self.item(z,f'ballesta_{t}')
                self.assertEqual(c['minecraft:enchantments']['astral:punteria'],t)
                self.assertEqual(c['minecraft:enchantments']['astral:carga_rapida'],t)
                if t>1:
                    self.assertIn(('c',f'ballesta_{t-1}',1),b['cost'])
                    self.assertLess(b['carga'],BALLESTAS[t-1]['carga'])
                    self.assertGreaterEqual(b['piercing'],BALLESTAS[t-1]['piercing'])

    def test_luck_normalized_and_pity_preserved(self):
        from lobby import GACHAS, crate_yml, RARITY_WEIGHT
        for gid,g in GACHAS.items():
            for lucky in (False,True):
                for guaranteed in (False,True):
                    prizes=yaml.safe_load(crate_yml(gid,g,garantia=guaranteed,suerte=lucky))['Crate']['Prizes']
                    self.assertAlmostEqual(sum(p['Weight'] for p in prizes.values()),100,delta=.003)
                    rewards=sorted(g['rewards'](),key=lambda r:list(RARITY_WEIGHT).index(r[0]),reverse=True)
                    if guaranteed:rewards=[r for r in rewards if r[0] in ('epic','legendary')]
                    rare=sum(p['Weight'] for r,p in zip(rewards,prizes.values()) if r[0] in ('rare','epic','legendary'))
                    if guaranteed:self.assertAlmostEqual(rare,100,delta=.003)
                    else:self.assertAlmostEqual(rare,100*22.5/107.5 if lucky else 15,delta=.003)

    def test_all_generated_clickable_buttons_have_models(self):
        # Sin excepciones clickeables por ahora. Rellenos y cabezas reales no accionables pueden ser vanilla.
        missing=[]
        with zipfile.ZipFile(ROOT/'build/AstralRPG-Textures.zip') as z:
            names=set(z.namelist())
            for p in (ROOT/'build/menus/DeluxeMenus/gui_menus').glob('*.yml'):
                data=yaml.safe_load(p.read_text(encoding='utf8'))
                for key,item in data.get('items',{}).items():
                    clickable=any(k.endswith('commands') for k in item)
                    if clickable and not item.get('item_model'):missing.append(f'{p.name}:{key}')
                    model=item.get('item_model','')
                    if model.startswith('astral:'):
                        self.assertIn('assets/astral/items/'+model.split(':',1)[1]+'.json',names,f'{p.name}:{key}')
            self.assertFalse(missing,missing)

    def test_lobby_speed_two_and_mines_models(self):
        from lobby import movement_mob
        self.assertIn('type=SPEED;duration=60;level=1;',movement_mob())
        script=(ROOT/'build/minas/Skript/scripts/astral_minas.sk').read_text(encoding='utf8')
        self.assertIn('set item model of slot 47',script)
        self.assertIn('set item model of slot 49',script)
        sale=script.split('function am_sale_menu',1)[1].split('function ',1)[0]
        self.assertNotIn('slot 47',sale)

    def test_backpacks_share_3d_body(self):
        with zipfile.ZipFile(ROOT/'build/AstralRPG-Textures.zip') as z:
            body=json.loads(z.read('assets/astral/models/provisorias/mochila_base.json'))
            self.assertEqual(len(body['elements']),5)
            for m in ('leather','copper','iron','gold','diamond','netherite'):
                model=json.loads(z.read(f'assets/astral/models/provisorias/mochila_{m}.json'))
                self.assertEqual(model['parent'],'astral:provisorias/mochila_base')

    def test_reward_sources_and_ancestral_chances(self):
        from mobs.mythic import MOBS, ANCESTRALES, ancestral_def, mob_block
        from cofre_mazmorra import cofre_menu
        from mobs.mazmorra import MINA
        from rankings import ITEMS
        self.assertIn(('barril_xp',1),ITEMS[1])
        for place in (1,2,3):self.assertIn(('manzana_esmeralda',1),ITEMS[place])
        self.assertIn('astral:xp/cofre',str(cofre_menu(MINA)))
        for mid,elite in ANCESTRALES.items():
            block=mob_block(mid+'_ancestral',ancestral_def(mid),model=mid,elite=elite)
            for iid,chance in [('frasco_xp_gigante',0.2),('barril_xp',0.025)]:
                lines=[line for line in block.splitlines() if 'loot astral:item/'+iid+'"' in line]
                self.assertEqual(len(lines),1)
                self.assertTrue(lines[0].endswith(str(chance)))


if __name__=='__main__':unittest.main()
