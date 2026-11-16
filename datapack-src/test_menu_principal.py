"""Contrato del menu publico: destinos, filas, saldo y apertura entre plugins."""
import unittest
import yaml
from menus import principal_menu, comandos_menu


class PrincipalMenuTests(unittest.TestCase):
    def setUp(self):
        self.menu = yaml.safe_load(principal_menu())
        self.items = self.menu['items']

    def test_layout_and_icons(self):
        self.assertEqual(self.menu['open_command'], 'menu')
        self.assertTrue(self.menu['register_command'])
        from menu_ui import title, SLOTS, KEYS
        self.assertEqual(self.menu['menu_title'], title())
        self.assertEqual(self.menu['size'], 54)
        # Sin relleno de vidrio: el marco de menu_ui dibuja el fondo.
        self.assertEqual(sorted(i['slot'] for i in self.items.values()), sorted([*SLOTS, 4, 31, 49]))
        for key in KEYS:
            self.assertEqual(self.items[key]['item_model'], f'astral:menu/icon_{key}')
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

    def test_effects_button_opens_existing_settings_with_custom_model(self):
        import json
        from menu_ui import assets
        from menus import configuraciones_menu
        button = self.items['configuraciones']
        self.assertIn('[openguimenu] configuraciones', button['click_commands'])
        settings = yaml.safe_load(configuraciones_menu())
        for level in ('bajo', 'medio', 'alto'):
            self.assertIn('[player] efectos ' + level, settings['items']['efectos_' + level]['click_commands'])
        files, _ = assets()
        namespace, path = button['item_model'].split(':')
        definition = json.loads(files[f'assets/{namespace}/items/{path}.json'])
        namespace, path = definition['model']['model'].split(':')
        model = json.loads(files[f'assets/{namespace}/models/{path}.json'])
        namespace, path = model['textures']['layer0'].split(':')
        self.assertIn(f'assets/{namespace}/textures/{path}.png', files)


if __name__ == '__main__':
    unittest.main()
