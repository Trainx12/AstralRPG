"""La Guia Astral en cofre: cada ventana tiene fondo, sus botones abren menus que existen y no quedan dialogos viejos."""
import json
import unittest
import zipfile
import yaml
from guia_cofre import ROOT, assets, menus, load, BG_CHARS, PAGE_CHARS, START

DATAPACK = ROOT.parent / 'build/AstralRPG-Items.zip'


class GuiaCofreTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = load()
        cls.menus = {k: yaml.safe_load(v) for k, v in menus(cls.source).items()}

    def test_every_link_opens_an_existing_menu(self):
        self.assertEqual(self.menus['guia_astral']['open_command'], 'guiaastral')
        for name, menu in self.menus.items():
            self.assertTrue(menu['menu_title'].startswith('&f' + START), name)
            for it in menu['items'].values():
                for cmd in it.get('click_commands', []):
                    self.assertNotIn('dialog show', cmd, name)
                    if cmd.startswith('[openguimenu]'):
                        self.assertIn(cmd.split()[-1], self.menus, name)

    def test_all_guide_pages_converted(self):
        for key in self.source['dialogs']:
            self.assertIn('g_' + key.replace('/', '_'), self.menus)

    def test_recipes_have_forge_and_ingredients(self):
        for name, menu in self.menus.items():
            if BG_CHARS['receta'][0] in menu['menu_title']:
                keys = menu['items']
                self.assertIn('resultado', keys, name)
                self.assertTrue(any(k.startswith('material') for k in keys), name)
                self.assertTrue(any('astral.forja set' in c for c in keys['forjar0']['click_commands']), name)

    def test_font_covers_backgrounds(self):
        files, providers = assets(self.source)
        chars = {c for p in providers for c in (p.get('chars') or []) + list(p.get('advances', {}))}
        for group in (*PAGE_CHARS[:3], *BG_CHARS.values()):
            self.assertTrue(set(group) <= chars)
        for p in providers:
            if 'file' in p:
                self.assertIn('assets/astral/textures/' + p['file'].split(':')[1], files)

    def test_old_guide_removed_and_no_esc_buttons(self):
        with zipfile.ZipFile(DATAPACK) as z:
            names = z.namelist()
            for tag in ('pause_screen_additions', 'quick_actions'):
                self.assertEqual(json.loads(z.read(f'data/minecraft/tags/dialog/{tag}.json'))['values'], [])
            self.assertNotIn(b'dialog show', z.read('data/astral/function/guide/give.mcfunction'))
        self.assertFalse([n for n in names if n.startswith(('data/astral/dialog/guia', 'data/astral/dialog/receta/',
                                                            'data/astral/dialog/atlas/'))])


if __name__ == '__main__':
    unittest.main()
