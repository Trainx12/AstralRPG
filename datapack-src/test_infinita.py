"""Mazmorra Infinita: salas, tiempos, mobs y entrada."""
import unittest

import infinita


class InfinitaTests(unittest.TestCase):
    def test_six_rooms_tiers_and_speeds(self):
        self.assertEqual(infinita.WORLDS, ['infinita'] + [f'infinita_{n}' for n in range(2, 7)])
        self.assertEqual([t for t, _, _ in infinita.TIERS], [1, 2, 3, 4, 5, 6])
        self.assertEqual([n for _, n, _, _ in infinita.SPEEDS], ['Facil', 'Normal', 'Dificil', 'Pesadilla'])
        self.assertEqual([s for *_, s in infinita.SPEEDS], sorted([s for *_, s in infinita.SPEEDS], reverse=True))

    def test_timers_warning_and_message(self):
        sk = infinita.script()
        self.assertIn(f'set {{-inf.next::%{{_n}}%}} to {20 * 60}', sk)
        self.assertIn(f'add {10 * 60} to {{-inf.next::%{{_n}}%}}', sk)
        self.assertIn(f'<= {5 * 60}:', sk)
        self.assertIn('Te veo muy tranquilo, creo que podes dar mas pelea', sk)

    def test_mobs_cover_requested_families_and_never_break_blocks(self):
        kinds = {m for m, _, _ in infinita.MOBS}
        for k in ('zombie', 'husk', 'drowned', 'skeleton', 'stray', 'bogged', 'wither_skeleton', 'spider', 'creeper',
                  'witch', 'pillager', 'vindicator', 'enderman'):
            self.assertIn(k, kinds)
        self.assertTrue(any('powered:1b' in n for m, _, n in infinita.MOBS if m == 'creeper'))
        self.assertIn('mob_griefing false', infinita.commands())
        self.assertIn('damage cause is entity explosion', infinita.script())

    def test_datapack_applies_tier_and_plus(self):
        files = {}
        infinita.generate(files)
        for t in range(1, 6):
            self.assertIn(f'function astral:mob/t{t}', files[f'data/astral/function/inf/apply/t{t}.mcfunction'])
        self.assertIn('astral:infinita 0.25 add_multiplied_total', files['data/astral/function/inf/plus.mcfunction'])

    def test_spawn_points_inside_the_dome(self):
        for x, y, z in infinita.SPAWN_POINTS + [infinita.ARRIVAL[:3]]:
            self.assertEqual(y, 63)
            self.assertLess(x * x + z * z, 33 * 33)


if __name__ == '__main__':
    unittest.main()
