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

    def test_picker_runs_duel_and_never_gives_items(self):
        sk = duelos.script()
        self.assertIn('command /desafiar:', sk)
        self.assertIn('cancel event', sk)
        self.assertIn('make player execute command "duel %{_t}%"', sk)
        self.assertIn('loop-player is not {_p}', sk)
        self.assertEqual(duelos.arenas_button()['click_commands'], ['[close]', '[player] desafiar<delay=3>'])


if __name__ == '__main__':
    unittest.main()
