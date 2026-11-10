import unittest
import yaml

from gameplay import realistic_hook, script
from lobby import TAB_SECTIONS
from sidebar import SIDEBAR_WIDTH, TEXT, centered_location, text_width, world_labels
from mobs import mythic
from mobs.mazmorra import mob_yml, skill_yml
from mobs.mazmorras_data import variant


class WorldNamesTests(unittest.TestCase):
    def test_every_live_dimension_resolves_through_root_condition(self):
        data = yaml.safe_load(TAB_SECTIONS)
        conditions = data['conditions']
        for world, label in world_labels().items():
            for root in ('mundo', 'sidebar_world'):
                value = '%condition:'+root+'%'
                seen = set()
                while value.startswith('%condition:'):
                    key = value[len('%condition:'):-1]
                    self.assertNotIn(key, seen)
                    seen.add(key)
                    condition = conditions[key]
                    expected = condition['conditions'][0].removeprefix('%world%=')
                    value = condition[True if world == expected else False]
                self.assertEqual(value, centered_location(label) if root == 'sidebar_world' else label)
                self.assertNotIn('_', value)

    def test_names_do_not_widen_the_board_with_trailing_spaces(self):
        for label in world_labels().values():
            result = centered_location(label).replace(TEXT, '')
            self.assertEqual(result, result.rstrip(' '))
            self.assertLessEqual(text_width(result), max(SIDEBAR_WIDTH, text_width(label)))
            left = len(result)-len(result.lstrip(' '))
            self.assertLessEqual(abs(left*4 + text_width(label)/2 - max(SIDEBAR_WIDTH,text_width(label))/2), 2)


class BossScaleTests(unittest.TestCase):
    def test_every_boss_and_ancestral_uses_absolute_two(self):
        skills = yaml.safe_load(mythic.metaskills())
        for mid, mob in mythic.MOBS.items():
            if mob['kind'] == 'jefe':
                self.assertIn(f'model{{m={mid};s=2.0}} @self', skills['AST_MODEL_'+mid]['Skills'])
        for mid in mythic.ANCESTRALES:
            self.assertIn(f'model{{m={mid};s=2.0}} @self', skills['AST_MODEL_'+mid+'_ancestral']['Skills'])
        self.assertIn('model{m=astral_yeti;s=8.0} @self', skills['AST_MODEL_astral_yeti_cumbre']['Skills'])

    def test_only_cumbre_yeti_gets_the_eight_override(self):
        for key in ('cumbre', 'santuario', 'otra'):
            _, text, _ = variant(key, 'yeti', boss=True)
            self.assertEqual('AST_MODEL_astral_yeti_cumbre' in text, key == 'cumbre')
        mobs = yaml.safe_load(mob_yml())
        for mid in ('astral_mina_capataz','astral_mina_golem'):
            self.assertNotIn(mid, mobs)
        self.assertIn('model{m=astral_coloso_musgoso;s=2.0} @self',
                      yaml.safe_load(skill_yml())['MINA_MODELO_astral_mina_guardian']['Skills'])


class ResponsiveMovementTests(unittest.TestCase):
    def test_hook_has_no_cooldown_and_compensates_native_gravity(self):
        text = realistic_hook()
        self.assertNotIn('astral.grapple.cd', text)
        self.assertNotIn('wait ', text)
        anchored = text.split('if {-astral.realistic::%{_id}%::anchor} is set:')[1].split('set {_block} to astral_hook_contact')[0]
        self.assertIn('teleport {_hook} to {-astral.realistic::%{_id}%::anchor}', anchored)
        self.assertIn('set velocity of {_hook} to vector(0, 0.03, 0)', anchored)
        self.assertIn('on unload:', text)

    def test_second_press_is_edge_triggered_without_time_gate(self):
        text = script()
        jump = text.split('on jump:')[1].split('every tick:')[0]
        self.assertIn('on player jump key release:', jump)
        self.assertIn('astral.jump.released', jump)
        self.assertNotIn('milliseconds', jump)
        self.assertNotIn('wait ', jump)
        self.assertNotIn('difference between now', jump)
        self.assertIn('set {_v} to vector(0, 0.65, 0)', jump)
        self.assertIn('set {_v} to vector({_vx} * 1.1, 0.65, {_vz} * 1.1)', jump)


if __name__ == '__main__':
    unittest.main()
