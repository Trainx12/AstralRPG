"""Oceano Astral (tanda A): menu de aviso, boton en Portales, tier fijo y comandos."""
import json
import sys
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'datapack-src'))
import oceano


class Oceano(unittest.TestCase):
    def test_aviso_y_portales(self):
        menu = oceano.aviso_menu()
        self.assertEqual(menu['items']['entrar']['click_commands'], ['[close]', '[player] oceano entrar<delay=3>'])
        self.assertTrue(any('tier 3' in l for l in menu['items']['info']['lore']))
        self.assertTrue(any('no hay superficie' in l for l in menu['items']['info']['lore']))
        import portales
        self.assertEqual(portales.menu_data()['items']['oceano']['click_commands'], ['[openguimenu] oceano_aviso'])

    def test_tier_fijo_en_el_datapack(self):
        z = zipfile.ZipFile(ROOT / 'build/AstralRPG-Items.zip')
        roll = z.read('data/astral/function/mob/roll.mcfunction').decode()
        self.assertIn('execute if dimension minecraft:oceano run scoreboard players set #mt astral.tmp 2', roll)
        self.assertIn('execute if dimension minecraft:oceano run scoreboard players set #dg astral.tmp 2', roll)

    def test_config_y_comandos(self):
        cfg = oceano.config()
        self.assertIn('regenerar-cada-horas: 72', cfg)
        self.assertIn('mv create oceano normal -g AstralOceano', oceano.commands())
        self.assertIn(f'worldborder set {oceano.RADIO * 2}', oceano.commands())

    def test_santuario_sin_cangrejo(self):
        from santuario_azeroth import WAVES
        self.assertEqual(WAVES[0], 'coloso_musgoso')
        self.assertNotIn('cangrejo', WAVES)


if __name__ == '__main__':
    unittest.main()
