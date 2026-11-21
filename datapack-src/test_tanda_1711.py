"""Regresiones de la tanda: lugares, mundos y contrato menu/premio/runtime."""
import importlib.util
from pathlib import Path
import unittest
import yaml
from lobby import GACHAS, NPC_POS, CARTELES_SUELTOS, holo_cmds, crate_yml
from minas import LOBBY_NPC
from minijuegos import parkour_worlds, arena_worlds, dropper_worlds
from gameplay import script
from menus import gacha_menu
from rankings import carteles

ROOT = Path(__file__).resolve().parents[1]


class Tanda1711Tests(unittest.TestCase):
    def test_jump_guard_covers_every_registered_game_before_impulse(self):
        handler = script().split('on player jump key press:', 1)[1].split('on ', 1)[0]
        guard = handler.split('if gamemode', 1)[0]
        for world in set(parkour_worlds()+arena_worlds()+dropper_worlds()):
            self.assertIn('"'+world+'"', guard)
        self.assertNotIn('"world"', guard)
        self.assertNotIn('"lobby"', guard)

    def test_mines_sign_and_ranking_have_separate_places(self):
        self.assertEqual(NPC_POS['astral_npc_minas'], LOBBY_NPC)
        rid, dim, x, y, z = next(c for c in carteles() if c[0] == 'minas')
        self.assertEqual(dim, 'minecraft:lobby')
        # 20/11: el ranking va arriba del cartel del NPC, en el piso de minerales.
        self.assertLess(abs(x-LOBBY_NPC[0]) + abs(z-LOBBY_NPC[2]), 1)
        self.assertGreater(y, LOBBY_NPC[1]+3)
        commands = '\n'.join(holo_cmds())
        self.assertIn('146.511 104.1 237.506', commands)
        self.assertIn('178.699 109.727 225.649', commands)
        self.assertIn('tag=astral.amb.expediciones', commands)
        self.assertEqual(CARTELES_SUELTOS['expediciones'][3:], (178.699, 109.727, 225.649))

    def test_menu_no_longer_changes_counter_before_result(self):
        for gid, g in GACHAS.items():
            menu = gacha_menu(gid, g)
            self.assertNotIn('scoreboard players add', menu)
            for count in (1, 10, 25, 50):
                self.assertIn(f'astralgacha %player_name% {gid} {count} false', menu)
            for guaranteed in (False, True):
                for lucky in (False, True):
                    prizes = yaml.safe_load(crate_yml(gid, g, guaranteed, lucky))['Crate']['Prizes']
                    for prize in prizes.values():
                        self.assertEqual(prize['Commands'][-1], f'astralgacha %player% {gid} ack false')

    def test_config_patch_changes_only_gui_toggle_and_keeps_crlf(self):
        spec = importlib.util.spec_from_file_location('ccpatch', ROOT/'tools/configurar_crazycrates.py')
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        old = '# test\r\ngui:\r\n  # comment\r\n  toggle: true # keep\r\n  inventory:\r\n    rows: 5\r\nother:\r\n  toggle: true\r\n'
        new = module.patch(old)
        self.assertEqual(new, old.replace('  toggle: true # keep', '  toggle: false # keep'))
        self.assertEqual(module.patch(new), new)
        with self.assertRaises(ValueError):
            module.patch('other:\n  toggle: true\n')


if __name__ == '__main__':
    unittest.main()
