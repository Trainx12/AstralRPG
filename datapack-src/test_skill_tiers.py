import unittest
from pathlib import Path
from skill_tiers import requirements, java_block


class SkillTiersTest(unittest.TestCase):
    def test_requested_boundaries(self):
        data = requirements()
        self.assertEqual(data['fighting'][:3], [4, 16, 20])
        self.assertEqual(data['sorcery'][:3], [0, 14, 20])
        self.assertEqual(data['archery'][:3], [8, 14, 20])

    def test_all_tiers_are_monotonic(self):
        for skill, levels in requirements().items():
            with self.subTest(skill=skill):
                self.assertEqual(len(levels), 10)
                self.assertTrue(all(a < b for a, b in zip(levels, levels[1:])))

    def test_runtime_matches_equipment(self):
        source = Path(__file__).with_name('runtime').joinpath('AstralProgression.java').read_text(encoding='utf8')
        self.assertIn(java_block(), source)
        self.assertNotIn('private static final int[] TIER_LEVELS', source)


if __name__ == '__main__':
    unittest.main()
