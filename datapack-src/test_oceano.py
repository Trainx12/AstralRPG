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


class OceanoTandaB(unittest.TestCase):
    def setUp(self):
        self.z = zipfile.ZipFile(ROOT / 'build/AstralRPG-Items.zip')

    def test_items_y_recetas(self):
        names = self.z.namelist()
        for iid in ('perla_abisal', 'coral_astral', 'agua_espada', 'agua_hacha', 'agua_arco', 'agua_pico',
                    'agua_helmet', 'agua_chestplate', 'agua_leggings', 'agua_boots'):
            self.assertIn(f'data/astral/loot_table/item/{iid}.json', names, iid)
        casco = self.z.read('data/astral/loot_table/item/agua_helmet.json').decode()
        for attr in ('water_movement_efficiency', 'submerged_mining_speed', 'oxygen_bonus'):
            self.assertIn(attr, casco)
        self.assertIn('set:\\"agua\\"', casco)
        mesa = json.loads((ROOT / 'build/runtime/mesa.json').read_text(encoding='utf8'))
        self.assertTrue(any('agua_espada' in json.dumps(r) for r in mesa))

    def test_menas_y_taladro(self):
        table = json.loads(self.z.read('data/minecraft/loot_table/blocks/note_block.json'))
        dumped = json.dumps(table)
        self.assertIn('astral:item/perla_abisal', dumped)
        self.assertIn('astral:item/coral_astral', dumped)
        mine = self.z.read('data/astral/function/tool/mine.mcfunction').decode()
        self.assertIn('execute if dimension minecraft:oceano run return run setblock ~ ~ ~ minecraft:water', mine)
        self.assertIn('note_block[instrument=banjo,note=22]', mine)
        self.assertIn('tool:"drill",tier:3', mine)
        self.assertNotIn('tool:"drill",tier:2', mine)
        self.assertIn('data/astral/loot_table/chests/oceano.json', self.z.namelist())


class Fosa(unittest.TestCase):
    def test_config_y_copias(self):
        import oceano_fosa
        cfg = oceano.config()
        self.assertIn('fosa:\n  mundos: [fosa, fosa_2, fosa_3]', cfg)
        self.assertIn('jefe: astral_fosa_cangrejo', cfg)
        self.assertEqual(len(oceano_fosa.WORLDS), 3)
        sk = (ROOT / 'build/mazmorras/astral_mazmorras_copias.sk').read_text(encoding='utf8')
        self.assertIn('if {_key} is "fosa":', sk)
        self.assertNotIn('fosa_4', sk)

    def test_jefe_tier3(self):
        from escala import TIER_FIJO, VIDA_JEFE
        self.assertEqual(TIER_FIJO['fosa_2'], 3)
        yml = (ROOT / 'build/mythicmobs/mobs/fosa.yml').read_text(encoding='utf8')
        self.assertIn('astral_fosa_cangrejo:', yml)
        self.assertIn(f"Health: {round(VIDA_JEFE['tumba'])}", yml)
        self.assertIn('addtag{tag=fosa.jefe}', yml)
        self.assertIn('WATER_BREATHING', yml)
