"""Contrato del menu publico: destinos, filas, saldo y apertura entre plugins."""
import unittest
import yaml
from menus import principal_menu, comandos_menu


class PrincipalMenuTests(unittest.TestCase):
    def setUp(self):
        self.menu = yaml.safe_load(principal_menu())
        self.items = self.menu['items']

    def test_layout_and_vanilla_icons(self):
        self.assertEqual(self.menu['open_command'], 'menu')
        self.assertTrue(self.menu['register_command'])
        self.assertEqual(self.menu['menu_title'], '&8Menu Astral')
        self.assertEqual(self.menu['size'], 54)
        self.assertEqual(sorted(i['slot'] for i in self.items.values()), list(range(54)))
        self.assertTrue(all('item_model' not in i for i in self.items.values()))
        self.assertEqual(self.items['cerrar']['slot'], 49)
        self.assertEqual(self.items['info']['slot'], 4)
        self.assertTrue(self.items['info']['update'])
        self.assertIn('%vault_eco_balance_formatted%$', ' '.join(self.items['info']['lore']))

    def test_services_and_delayed_external_commands(self):
        for destination in ('bazar', 'mazmorras', 'expediciones', 'portales', 'misiones',
                            'mascotas', 'cosmeticos', 'comandos'):
            self.assertIn('[openguimenu] '+destination, self.items[destination]['click_commands'])
        for key, command in {'minas': 'minas', 'skills': 'skills', 'spawn': 'spawn',
                             'guia': 'trigger astral.guia set 1'}.items():
            commands = self.items[key]['click_commands']
            self.assertIn('[close]', commands)
            self.assertIn('[player] '+command+'<delay=3>', commands)
        self.assertIn('lobby', ' '.join(self.items['minas']['lore']))
        self.assertTrue(any('astral:quest/gui/page/0' in c for c in self.items['misiones']['click_commands']))

    def test_commands_explain_star(self):
        data = yaml.safe_load(comandos_menu())
        self.assertIn('Estrella del slot 9', str(data))


if __name__ == '__main__':
    unittest.main()
