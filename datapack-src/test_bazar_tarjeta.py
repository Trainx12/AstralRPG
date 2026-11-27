"""Visibilidad privada/publica, respaldo y arte reemplazable del Bazar del Refugio."""
import io
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml
from PIL import Image
import menus
import services_ui as ui


class BazarCardTests(unittest.TestCase):
    def test_private_and_public_slots(self):
        slots = {32, 33, 34, 35, 41, 42, 43, 44}
        for public in (False, True):
            with self.subTest(public=public), patch.object(menus, 'BAZAR_PUBLICO', public):
                data = yaml.safe_load(menus.bazar_menu())
                for slot in slots:
                    items = [i for i in data['items'].values() if i['slot'] == slot]
                    self.assertEqual(len(items), 1 if public else 2)
                    bazar = next(i for i in items if i['display_name'] == '&6&lBazar')
                    self.assertEqual(bazar['click_commands'],
                                     ['[sound] UI_BUTTON_CLICK', '[close]', '[player] bazar<delay=3>'])
                    if public:
                        self.assertNotIn('view_requirement', bazar)
                    else:
                        self.assertEqual(bazar['view_requirement']['requirements']['permiso'],
                                         {'type': 'has permission', 'permission': 'astral.bazar.usar'})
                        trade = next(i for i in items if i != bazar)
                        self.assertLess(bazar['priority'], trade['priority'])
                        self.assertNotIn('view_requirement', trade)
                        self.assertIn('/trade <jugador>', str(trade))
                self.assertIn('/trade <jugador>', str(data['items']['ayuda']))

    def test_only_cards_and_help_change_from_committed_menu(self):
        root = Path(__file__).resolve().parents[1]
        base = root / 'build/abrir-todo-27-11/gui_menus/bazar.yml'
        old = yaml.safe_load(base.read_text(encoding='utf8') if base.exists() else subprocess.check_output(
            ['git', 'show', 'f32b7d1~1:build/menus/DeluxeMenus/gui_menus/bazar.yml'], cwd=root))
        new = yaml.safe_load(menus.bazar_menu())
        for key in list(new['items']):
            if key.startswith('bazar_'):
                del new['items'][key]
            elif key.startswith('intercambio_'):
                new['items'][key].pop('priority')
        new['items']['ayuda'] = old['items']['ayuda']
        self.assertEqual(old, new)

    def test_provisional_and_custom_art(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(ui, 'ROOT', Path(folder)):
            self.assertEqual(ui.bazar_card('bazar', 'BAZAR', 'ORDENES').size, (72, 36))
            path = Path(folder) / 'pack-source/ref/gemini/tarjeta_bazar.png'
            path.parent.mkdir(parents=True)
            Image.new('RGBA', (288, 144), '#123456').save(path)
            custom = ui.bazar_card('bazar', 'BAZAR', 'ORDENES')
            self.assertEqual(custom.size, (72, 36))
            self.assertEqual(custom.getpixel((36, 18)), (18, 52, 86, 255))

    def test_pack_tiles_resolve_and_keep_trade(self):
        import json
        files, _ = ui.assets()
        for key in ('bazar', 'intercambio'):
            for n in range(8):
                name = f'servicios/bazar_{key}_{n}'
                item = json.loads(files[f'assets/astral/items/{name}.json'])
                self.assertEqual(item['model']['model'], 'astral:' + name)
                model = json.loads(files[f'assets/astral/models/{name}.json'])
                texture = model['textures']['layer0'].replace('astral:', 'assets/astral/textures/') + '.png'
                self.assertEqual(Image.open(io.BytesIO(files[texture])).size, (18, 18))


if __name__ == '__main__':
    unittest.main()
