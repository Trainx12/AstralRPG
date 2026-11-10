"""Regresiones de la tanda 1, sin acceso a servicios ni mapas privados."""
from pathlib import Path
import unittest
import yaml

from adventure_ui import DESTINATIONS, LABELS, regions
from escala import TIER_MAZMORRA
from explosion_protection import SAFE_FLAGS, WORLDS, commands as explosion_commands
from lobby import ASTRAL_ROWS, TAB_SECTIONS
from minas import script as mines_script
from mobs.mazmorra import commands, mob_yml
from viajes_mazmorras import ORDER, PROGRESO, destinations, exploration_script, exploration_menu


class Tanda1(unittest.TestCase):
    def test_order_labels_and_requirements(self):
        expected = ('bosque', 'mina', 'tumba', 'cumbre', 'forja', 'santuario')
        self.assertEqual(ORDER, expected)
        self.assertEqual(PROGRESO, expected)
        self.assertEqual(DESTINATIONS, expected)
        self.assertEqual(LABELS[:3], ('BOSQUE', 'MINAS', 'TUMBA'))
        self.assertEqual([key for key, _ in regions('expediciones')], list(expected))
        text = exploration_script()
        for i, key in enumerate(expected):
            branch = text.split(f'        if arg-1 is "{key}":\n')[1].split('        if arg-1', 1)[0]
            self.assertNotIn('astral.descubierto', branch)
            if i:
                self.assertIn(f'astral.completada.{expected[i-1]}', branch)
                self.assertLess(branch.index('astral.completada'), branch.index('minecraft:tp'))
            else:
                self.assertNotIn('astral.completada', branch)
            self.assertIn(f'{i+1}. ', exploration_menu()['items'][key]['display_name'])

    def test_only_entrance_name_changes(self):
        for dungeon in destinations():
            mobs = yaml.safe_load(mob_yml(dungeon))
            self.assertIs(mobs[dungeon['npc']]['Options']['AlwaysShowName'], False)
            for key, value in mobs.items():
                if key.endswith(('_cofre', '_guia')):
                    self.assertIs(value['Options']['AlwaysShowName'], True)

    def test_tiers_and_safe_flags(self):
        self.assertEqual((TIER_MAZMORRA['bosque'], TIER_MAZMORRA['mina']), (1, 2))
        self.assertEqual(SAFE_FLAGS, ('enderdragon-block-damage',))
        self.assertNotIn('santuario', WORLDS)
        self.assertNotIn('santuario_interstellar', WORLDS)
        for dungeon in destinations():
            if dungeon['key'] != 'santuario':
                for line in explosion_commands(dungeon['world']):
                    self.assertIn(line, commands(dungeon))
        from mapas_exploracion import installation_commands, DEFINITIONS
        for key, definition in DEFINITIONS.items():
            for line in explosion_commands(key):
                self.assertIn(line, installation_commands(key, definition))

    def test_mines_any_world(self):
        branch = mines_script().split('command /minas:\n')[1].split('on inventory click:', 1)[0]
        self.assertIn('am_menu(player)', branch)
        self.assertNotIn('name of world', branch)
        self.assertNotIn('se abren desde el lobby', mines_script())

    def test_tab_general_and_toggle(self):
        config = yaml.safe_load(TAB_SECTIONS)
        self.assertEqual(list(config['scoreboard']['scoreboards']), ['minas', 'astral'])
        self.assertLessEqual(len(ASTRAL_ROWS), 15)
        self.assertEqual(len(ASTRAL_ROWS), 14)
        self.assertIn('%objective_score_{astraldef}%', str(ASTRAL_ROWS))
        self.assertNotIn('%player_armor%', str(ASTRAL_ROWS))
        self.assertNotIn('Conectados', str(ASTRAL_ROWS))
        self.assertIn('103.106.58.173:7004', ASTRAL_ROWS[-1])
        for label in ('Stats', 'Def', 'Poder', 'Oro', 'Rango', 'Diarias', 'Historia', 'Monstruos'):
            self.assertIn(label, str(ASTRAL_ROWS))
        import betterhud
        self.assertIn('[papi:objective_score_{astraldef}]', betterhud.layouts_yml())
        from explosion_protection import BLOCK_CONFIG
        self.assertEqual(yaml.safe_load(BLOCK_CONFIG)['mobs']['block-fireball-block-damage'], True)
        self.assertEqual(yaml.safe_load(BLOCK_CONFIG)['mobs']['block-fireball-explosions'], False)
        self.assertEqual(yaml.safe_load(betterhud.config_yml('default-hud: []\n'))['default-hud'], [])
        self.assertNotIn('hud hud add', betterhud.SKRIPT)
        self.assertIn('tab scoreboard on', betterhud.SKRIPT)
        self.assertIn('tab scoreboard off', betterhud.SKRIPT)


if __name__ == '__main__':
    unittest.main()
