"""Duelos dentro de Arenas: arenas de Duels y ventana /desafiar."""
import unittest

import duelos
import minijuegos


class DuelosTests(unittest.TestCase):
    def test_every_pvp_arena_world_is_registered_with_two_facing_points(self):
        data = duelos.arenas_json()
        self.assertEqual([a['name'] for a in data], ['Astral', 'TFT1', 'TFT2', 'TFT3'])
        self.assertEqual({a['positions']['1']['world'] for a in data}, set(minijuegos.arena_worlds()))
        for arena in data:
            a, b = arena['positions']['1'], arena['positions']['2']
            self.assertEqual(a['world'], b['world'])
            self.assertGreater(((a['x']-b['x'])**2 + (a['z']-b['z'])**2) ** .5, 10)
            self.assertEqual(abs(a['yaw'] - b['yaw']), 180)

    def test_legacy_selector_is_retired_without_duplicate_commands(self):
        sk = duelos.script()
        self.assertNotIn('command /', sk)
        self.assertIn('AstralDuelos.jar', sk)
        self.assertEqual(duelos.arenas_button()['click_commands'], ['[close]', '[player] duelos<delay=3>'])

    def test_both_menu_entries_open_the_new_hub(self):
        import menus
        import yaml
        hub = yaml.safe_load(menus.principal_menu())
        commands = [c for v in hub['items'].values() for c in v.get('click_commands', [])]
        self.assertIn('[player] duelos<delay=3>', commands)
        arena = minijuegos.menu_data('arena')['items']['desafiar']
        self.assertEqual(arena['display_name'], '&c&lDuelos')
        self.assertEqual(arena['slot'], duelos.ARENAS_BUTTON_SLOT)

    def test_generated_handoff_contains_no_runtime_commands(self):
        self.assertTrue(all(line.startswith('#') for line in duelos.script().splitlines()))


if __name__ == '__main__':
    unittest.main()
