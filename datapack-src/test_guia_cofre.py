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

    def test_ampliacion_publica_y_recetas_sin_forja_astral(self):
        from guia_ampliacion import catalog
        from guia_cofre import INGREDIENTS, OUTPUT, FORGE, text_width, SHORT
        for key in ('cocina', 'stellarity'):
            name = 'g_atlas_seccion_' + key
            self.assertIn(name, self.menus)
            self.assertLessEqual(text_width(SHORT[key][0]), 53)
        for name, menu in self.menus.items():
            self.assertNotIn('open_requirement', menu, name)
            for item in menu['items'].values():
                self.assertNotIn('view_requirement', item, name)
        for recipe in catalog()['recipes']:
            menu = self.menus['g_guia_stellarity_r_' + recipe['id']]
            self.assertIn(BG_CHARS['receta_stellarity'][0], menu['menu_title'])
            slots = {i['slot']: i for i in menu['items'].values()}
            self.assertIn(OUTPUT, slots)
            for slot, ing in zip(INGREDIENTS, recipe['grid']):
                if ing:
                    self.assertIn(slot, slots, recipe['id'])
                    self.assertEqual(slots[slot]['amount'], min(ing['count'], 64))
                else:
                    self.assertNotIn(slot, slots, recipe['id'])
            for it in menu['items'].values():
                self.assertFalse(any('astral.forja' in c for c in it.get('click_commands', [])))
            self.assertFalse(any(slots[s].get('click_commands') for s in FORGE))

    def test_comida_disponible_y_curacion_publica(self):
        comida = self.menus['g_atlas_seccion_cocina']
        cnk = self.menus['g_guia_comida_cnk']
        lore = lambda menu: ' '.join(line.replace('&7', '') for item in menu['items'].values() for line in item.get('lore', []))
        self.assertIn('Disponible en el Survival', lore(comida))
        self.assertIn('Comer cura poco por si solo', lore(comida))
        self.assertIn('Tras 20 s sin recibir dano, curas 4% de tu vida maxima por segundo, sin gastar comida.', lore(comida))
        self.assertIn('Crop & Kettle', cnk['menu_title'])
        for text in ('sin confirmar', 'cuando se habilite', 'Solo ByTrainx', '20%', 'preparada'):
            self.assertNotIn(text, lore(comida) + lore(cnk))

    def test_crafteos_y_drops_retirados_sin_enlaces_rotos(self):
        import re as _re
        for name in ('g_atlas_seccion_crafteos', 'g_guia_drops', 'guia_astral_3_publica', 'g_atlas_seccion_cocina_publica'):
            self.assertNotIn(name, self.menus)
        for name, menu in self.menus.items():
            for item in menu['items'].values():
                for cmd in item.get('click_commands', []):
                    m = _re.match(r'\[openguimenu\] (\S+)', cmd)
                    if m and m.group(1).startswith(('g_', 'guia_astral')):
                        self.assertIn(m.group(1), self.menus, (name, cmd))

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
