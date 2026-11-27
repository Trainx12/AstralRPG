"""Contrato del item privado, receta y generacion de Minas."""
import json
from pathlib import Path
import unittest
import zipfile
import autoventa
import minas

ROOT = Path(__file__).resolve().parents[1]


class Autoventa(unittest.TestCase):
    def test_item_y_sin_guia(self):
        with zipfile.ZipFile(ROOT / 'build/AstralRPG-Items.zip') as z:
            item = json.loads(z.read('data/astral/loot_table/item/autoventa.json'))
            entry = item['pools'][0]['entries'][0]
            comp = entry['functions'][0]['components']
            self.assertEqual(entry['name'], 'minecraft:heart_of_the_sea')
            self.assertEqual(comp['minecraft:max_stack_size'], 1)
            self.assertTrue(comp['minecraft:enchantment_glint_override'])
            self.assertNotIn('minecraft:item_model', comp)
            self.assertIn('"auraskills:item_requirements":{"auraskills:mining":100}', comp['minecraft:custom_data'])
            for path in z.namelist():
                if '/guia' in path or '/recipe/' in path or '/forge/' in path or '/atlas/' in path:
                    self.assertNotIn(b'autoventa', z.read(path), path)
            identify = z.read('data/astral/function/autoventa/identify.mcfunction').decode()
            for slot in ('hotbar.*', 'inventory.*', 'weapon.offhand'):
                self.assertIn(slot, identify)

    def test_receta_reservada(self):
        from items import MATERIALS
        recipe = autoventa.RECIPE
        self.assertGreaterEqual(len(set((k, i) for k, i, n in recipe[2])), 8)
        for kind, iid, n in recipe[2]:
            self.assertGreater(n, 0)
            if kind == 'c':
                self.assertIn(iid, MATERIALS)
        self.assertFalse(json.loads((ROOT / 'build/autoventa/receta-desactivada.json').read_text())['enabled'])

    def test_script(self):
        text = minas.script()
        self.assertEqual(text, (minas.OUT / 'Skript/scripts/astral_minas.sk').read_text(encoding='utf8'))
        body = text.split('function am_autoventa(', 1)[1].split('function am_give(', 1)[0]
        for expected in ('is not "astral_minas"', 'is not "ByTrainx"', '{am.autoventa.publico} is not true',
                         '< 2 seconds', '%%auraskills_mining%%', 'if {_nivel} is not set:',
                         'if {_nivel} < 100:', 'am_sell_value({_p}, true)', "add {_total} to {_p}'s balance"):
            self.assertIn(expected, body)
        self.assertLess(body.index('is not "ByTrainx"'), body.index('am_sell_value'))
        self.assertIn('command /autoventa <text>:\n    permission: op', text)
        give = text.split('function am_give(', 1)[1].split('# 25/11 (dueno): cartel', 1)[0]
        self.assertIn('{_antes::*} does not contain loop-value', give)
        self.assertIn('give {_drop} to {_p}', give)

    def test_entrega_aditiva(self):
        from deploy_autoventa import OLD_GIVE, patch_script
        generated = minas.script()
        start = generated.index('command /am_autoventa_nivel ')
        end = generated.index('\n# 25/11 (dueno): cartel', start)
        old = generated[:start] + OLD_GIVE + generated[end:]
        self.assertEqual(patch_script(old), generated)
        with self.assertRaises(ValueError):
            patch_script(generated)
        with zipfile.ZipFile(ROOT / 'build/autoventa/AstralRPG-Autoventa.zip') as z:
            self.assertEqual(set(z.namelist()), {'pack.mcmeta',
                'data/astral/loot_table/item/autoventa.json',
                'data/astral/function/autoventa/identify.mcfunction'})


if __name__ == '__main__':
    unittest.main()
