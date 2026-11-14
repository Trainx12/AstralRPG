"""Ropa de oficio (Minero y Talador): items, recetas, efectos, tienda y arte."""
import json
import unittest
import zipfile
from pathlib import Path

import yaml

import oficios

ROOT = Path(__file__).resolve().parent.parent


class Oficios(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.zip = zipfile.ZipFile(ROOT / 'build/AstralRPG-Items.zip')

    def read(self, name):
        return self.zip.read(name).decode('utf-8')

    def test_items_con_atributos(self):
        for iid in oficios.item_ids():
            table = json.loads(self.read(f'data/astral/loot_table/item/{iid}.json'))
            comps = table['pools'][0]['entries'][0]['functions'][0]['components']
            types = [m['type'] for m in comps['minecraft:attribute_modifiers']]
            self.assertIn('minecraft:block_break_speed', types)
            self.assertEqual('minecraft:mining_efficiency' in types, iid.startswith('minero_'))
            eq = comps['minecraft:equippable']
            self.assertEqual(eq.get('asset_id'), None if iid.endswith('helmet') else 'astral:' + iid.split('_')[0])

    def test_recetas_baratas(self):
        mesa = json.loads((ROOT / 'build/runtime/mesa.json').read_text(encoding='utf-8'))
        text = json.dumps(mesa)
        for iid in oficios.item_ids():
            self.assertIn(iid, text)
        for sdef in oficios.SETS.values():
            for ings in sdef['recipes'].values():
                for kind, ing, n in ings:
                    self.assertTrue(kind == 'v' or ing == 'cuero_tratado', ing)

    def test_efectos(self):
        check = self.read('data/astral/function/oficios/check.mcfunction')
        for tag in ('astral.ofi_minero', 'astral.ofi_talador'):
            self.assertIn(tag, check)
        self.assertIn('night_vision', check)
        self.assertIn('#minecraft:axes', check)
        self.assertIn('function astral:oficios/check', self.read('data/astral/function/loop/t20.mcfunction'))
        self.assertIn('astral.ofi_minero', (ROOT / 'build/minas/Skript/scripts/astral_minas.sk').read_text(encoding='utf-8'))
        self.assertIn('astral.ofi_talador', (ROOT / 'build/bosque/astral_bosque.sk').read_text(encoding='utf-8'))

    def test_tienda(self):
        base = ROOT / 'build/shop/EconomyShopGUI'
        section = yaml.safe_load((base / 'sections/Oficios.yml').read_text(encoding='utf-8'))
        self.assertEqual(section['title'], oficios.SHOP_TITLE)
        self.assertNotIn(section['slot'], (1, 13, 15, 21, 23, 25, 29, 31, 33, 35, 39, 40, 41, 42))
        menu = yaml.safe_load((ROOT / 'build/menus/DeluxeMenus/gui_menus/oficios.yml').read_text(encoding='utf-8'))
        compras = [i for i in menu['items'].values() if any('[takemoney]' in c for c in i.get('click_commands', []))]
        self.assertEqual(len(compras), 10)
        for i in compras:
            self.assertIn('click_requirement', i)
        self.assertIn('oficios:', (ROOT / 'build/menus/DeluxeMenus/config-gui_menus.yml').read_text(encoding='utf-8'))
        java = (ROOT / 'datapack-src/runtime/AstralDecor.java').read_text(encoding='utf-8')
        self.assertIn(oficios.SHOP_TITLE, java)

    def test_arte(self):
        files = oficios.own_textures()
        for sid in oficios.SETS:
            self.assertIn(f'assets/astral/equipment/{sid}.json', files)
            self.assertIn(f'assets/astral/textures/entity/equipment/humanoid/{sid}.png', files)
            self.assertIn(f'assets/astral/textures/entity/equipment/humanoid_leggings/{sid}.png', files)
        with zipfile.ZipFile(ROOT / 'build/AstralRPG-Textures.zip') as pack:
            for name in files:
                self.assertIn(name, pack.namelist())


if __name__ == '__main__':
    unittest.main()
