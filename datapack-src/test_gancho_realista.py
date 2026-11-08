import json
from pathlib import Path
import unittest

from gameplay import realistic_hook

PACK = Path(__file__).resolve().parent.parent / 'build/AstralRPG-Items/data/astral'


class RealisticHookTests(unittest.TestCase):
    def test_two_distinct_hooks_saltador_slime_and_gancho_skin(self):
        def item(iid):
            return json.loads((PACK / f'loot_table/item/{iid}.json').read_text(encoding='utf-8'))['pools'][0]['entries'][0]
        old, new = item('gancho'), item('gancho_realista')
        self.assertEqual(old['name'], 'minecraft:carrot_on_a_stick')
        self.assertEqual(new['name'], 'minecraft:fishing_rod')
        components = new['functions'][0]['components']
        self.assertEqual(components['minecraft:item_model'], 'astral:gancho')
        self.assertEqual(old['functions'][0]['components']['minecraft:item_model'], 'minecraft:slime_ball')
        self.assertIn('Gancho', str(components['minecraft:item_name']))
        self.assertIn('Saltador', str(old['functions'][0]['components']['minecraft:item_name']))
        self.assertIn('astral:item/gancho_realista', (PACK / 'loot_table/kit/especiales.json').read_text())

    def test_identity_uses_custom_data(self):
        text = (PACK / 'function/grapple/realistic_check.mcfunction').read_text()
        self.assertIn('weapon.mainhand minecraft:fishing_rod[minecraft:custom_data~{astral:{id:"gancho_realista"}}]', text)
        self.assertNotIn('item_name', text)

    def test_no_air_launch_or_teleport(self):
        text = realistic_hook()
        self.assertLess(text.index('if event-fishing state is reel in:'), text.index('set velocity of player'))
        self.assertIn('location of fishing hook', text)
        self.assertIn('location of hooked entity', text)
        self.assertIn('vector from eye location of player to {_anchor}', text)
        self.assertNotIn('teleport player', text)
        self.assertNotIn('teleport loop-player', text)
        self.assertNotIn('pitch of player', text)

    def test_ownership_limits_and_dungeon_guards(self):
        text = realistic_hook()
        self.assertIn('uuid of fishing hook is not {-astral.realistic::%{_id}%}', text)
        self.assertEqual(text.count('if astral_dungeon(world of player) is true:'), 2)
        self.assertIn('if {_distance} > 32:', text)
        self.assertNotIn('astral.grapple.cd', text)
        self.assertNotIn('wait ', text)
        self.assertIn('on death of player:', text)
        self.assertIn('on world change:', text)

    def test_wall_contact_is_saved_before_reeling(self):
        text = realistic_hook()
        self.assertIn('function astral_hook_contact(at: location) :: block:', text)
        self.assertIn('if block at {_probe} is solid:', text)
        self.assertIn('set gravity of {_hook} to false', text)
        self.assertIn('teleport {_hook} to {-astral.realistic::%{_id}%::anchor}', text)
        self.assertIn('set {_anchor} to {-astral.realistic::%{_id}%::anchor}', text)
        self.assertIn('if {_anchor} is not set:', text)
        self.assertIn('if {_block} is not solid:', text)
        self.assertIn('set velocity of {_hook} to vector(0, 0.03, 0)', text)
        self.assertIn('astral_hook_clear(player)', text)


if __name__ == '__main__':
    unittest.main()
