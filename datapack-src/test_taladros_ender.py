"""Contrato de mejoras de taladros y Guía/pack de Ender, sobre salidas reales."""
import json
from pathlib import Path
import unittest
import zipfile
import yaml
from items import MEJORA_MINADO, mejora_de
from tools import DRILLS, CHAINSAWS
from guia_cofre import mochila_menus
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
PACK=ROOT/'build/AstralRPG-Items'


class TaladrosEnder(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with zipfile.ZipFile(ROOT/'build/mochilas-ender/AstralRPG-Items.zip') as z:
            cls.generated={n:z.read(n) for n in z.namelist()}

    def read(self, path):return self.generated['data/astral/'+path].decode('utf8')

    def test_enchantment_is_mining_only(self):
        e=json.loads(self.read('enchantment/mejora_taladro.json'))
        self.assertEqual(e['supported_items'],'#astral:sin_mesa')
        self.assertEqual(e['slots'],['mainhand'])
        effect=e['effects']['minecraft:attributes'][0]
        self.assertEqual(effect['attribute'],'minecraft:block_break_speed')
        self.assertEqual(effect['operation'],'add_multiplied_base')
        self.assertEqual(effect['amount']['values'],MEJORA_MINADO)
        self.assertEqual(set(e['effects']),{'minecraft:attributes'})

    def test_all_drills_levels_forge_migration_and_cards(self):
        for i,d in enumerate(DRILLS):
            iid=d['id'];self.assertEqual(mejora_de(iid,'weapon'),'mejora_taladro')
            for level in range(1,11):
                with self.subTest(item=iid,level=level):
                    card=json.loads(self.read(f'item_modifier/ficha/{iid}/{level}.json'))
                    text=json.dumps(card,ensure_ascii=False)
                    self.assertEqual(text.count('✪'),level)
                    self.assertIn(f'(+{round(MEJORA_MINADO[level-1]*100)}%)',text)
                    upgraded=json.loads(self.read(f'item_modifier/upgrade/{iid}/{level}.json'))
                    self.assertNotIn('minecraft:enchantments',upgraded[0]['components'])
                    slot=self.read('function/upgrade/slot/container_0.mcfunction')
                    self.assertIn(f'astral:upgrade/{iid}/{level}',slot)
                    if i:
                        prev=DRILLS[i-1]['id']
                        self.assertIn(f'data/astral/item_modifier/forja/{iid}/{prev}/{level}.json',self.generated)
            gm=self.read(f'function/upgrade/gm1/{iid}.mcfunction')
            self.assertIn('mejora_taladro',gm)
        for d in CHAINSAWS:
            self.assertNotIn(f'data/astral/item_modifier/ficha/{d["id"]}/1.json',self.generated)
        forge='\n'.join(b.decode('utf8') for n,b in self.generated.items() if n.startswith('data/astral/function/forge/') and n.endswith('.mcfunction'))
        self.assertIn('mejora_taladro',forge)

    def test_private_gate_and_success(self):
        for path in ('function/mejora/ver.mcfunction','function/mejora/gui/inspect.mcfunction'):
            s=self.read(path)
            self.assertIn('#pub astral.mejtal matches 0 if entity @s[name=ByTrainx]',s)
            self.assertIn('#pub astral.mejtal matches 1',s)
            self.assertIn('tool:"drill"',s)
        for n in range(1,11):
            s=self.read(f'function/mejora/ok/{n}.mcfunction')
            self.assertIn(f'"astral:mejora_taladro":{n}',s)
            self.assertIn('matches 3',s)
        self.assertIn('#pub astral.mejtal matches 0 if entity @s[name=ByTrainx]',self.read('function/mejora/hacer.mcfunction'))
        load=self.read('function/load.mcfunction')
        for o in ('mejtal','mochender'):
            self.assertIn(f'unless score #pub astral.{o} matches 0..1',load)

    def test_guide_recipe_navigation_slots_and_private_text(self):
        menus={k:yaml.safe_load(v) for k,v in mochila_menus().items()}
        ender=menus['g_mochila_ender']['items']
        self.assertEqual([ender[f'g{i}']['material'] for i in range(9)],
                         ['ENDER_EYE','ENDER_PEARL','ENDER_EYE','ENDER_PEARL','CHEST','ENDER_PEARL','ENDER_EYE','IRON_BLOCK','ENDER_EYE'])
        for name,menu in menus.items():
            slots=[i['slot'] for i in menu['items'].values() if 'slot' in i]
            self.assertEqual(len(slots),len(set(slots)),name)
        self.assertIn('[openguimenu] g_mochila_ender',str(menus['g_mochila_netherite']))
        self.assertIn('No se puede meter una mochila dentro de otra',' '.join(menus['g_mochilas']['items']['info']['lore']).replace('&7',''))
        with patch('guia_cofre.ENDER_PUBLICO',True):
            self.assertIn('Solo la Mochila',str(mochila_menus()))

    def test_public_pack_has_provisional_ender(self):
        with zipfile.ZipFile(ROOT/'build/mochilas-ender/AstralRPG-Textures.zip') as z:
            model=json.loads(z.read('assets/astral/models/provisorias/mochila_ender.json'))
            self.assertEqual(model['parent'],'astral:provisorias/mochila_base')


if __name__=='__main__':unittest.main()
