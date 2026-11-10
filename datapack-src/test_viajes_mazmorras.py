"""Comprueba que el menu y el comando no permitan saltar el descubrimiento."""
import unittest
import yaml
from mobs.mazmorra import mob_yml
from viajes_mazmorras import destinations, menu_data, permission, script, exploration_menu, exploration_script, EXPLORATION


class TravelTests(unittest.TestCase):
    def test_only_guardian_interaction_grants_discovery(self):
        for d in destinations():
            npc=yaml.safe_load(mob_yml(d))[d['npc']]
            grants=[s for s in npc['Skills'] if 'permission set' in s]
            self.assertEqual(len(grants),1)
            self.assertIn(permission(d['key']),grants[0])
            self.assertIn('~onInteract',grants[0])
            self.assertIn('<trigger.name>',grants[0])
            self.assertIn('?~!haspermission',grants[0])

    def test_locked_items_cannot_travel_or_unlock(self):
        items=menu_data()['items']
        for d in destinations():
            commands=items[d['key']+'_bloqueada']['click_commands']
            self.assertTrue(all(c.startswith(('[message]','[sound]')) for c in commands))
        self.assertNotIn('permission set',str(menu_data()))

    def test_menu_rechecks_permission_and_uses_guarded_command(self):
        for d in destinations():
            item=menu_data()['items'][d['key']]
            for kind in ('view_requirement','click_requirement'):
                self.assertEqual(item[kind]['requirements']['descubierta']['permission'],permission(d['key']))
            self.assertEqual(item['click_commands'],['[close]',f'[player] mazmorras {d["key"]}'])
        self.assertNotIn('open_command',menu_data()) # Skript owns /mazmorras.

    def test_every_direct_route_checks_discovery_before_teleport(self):
        text=script()
        for d in destinations():
            branch=text.split(f'        if {{_destino}} is "{d["key"]}":\n',1)[1].split('        if {_destino}',1)[0]
            check=f'if player does not have permission "{permission(d["key"])}"'
            self.assertIn(check,branch)
            self.assertLess(branch.index(check),branch.index('minecraft:tp') if d['enabled'] else branch.index('en preparacion'))
            self.assertIn('                stop',branch)
        self.assertNotIn('%arg-1%',text)
        self.assertIn('executable by: players',text)

    def test_no_destination_requires_story_completion(self):
        from mobs.mazmorra import skill_yml
        self.assertNotIn('aq.state', script())
        self.assertNotIn('historia', str(menu_data()))
        for d in destinations():
            self.assertNotIn('aq.state', skill_yml(d))

    def test_exploration_routes_are_ordered_and_separate_from_dungeons(self):
        menu=exploration_menu()['items']
        self.assertEqual([EXPLORATION[d['key']][0] for d in destinations()],
                         ['cavernas','cavernas','exp_desierto','exp_nieve','forja','exp_santuario'])
        for d in destinations():
            self.assertEqual(menu[d['key']]['click_commands'],['[close]',f'[player] expediciones {d["key"]}'])
        self.assertEqual(menu['lobby']['click_commands'],['[close]','[player] spawn'])
        self.assertNotIn('permission set',exploration_script())


if __name__=='__main__':unittest.main()
