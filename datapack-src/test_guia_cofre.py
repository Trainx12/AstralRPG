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

    def test_ampliacion_protegida_y_recetas_sin_forja_astral(self):
        from guia_ampliacion import catalog, PERMISSION
        from guia_cofre import INGREDIENTS, OUTPUT, FORGE, text_width, SHORT
        for key in ('cocina', 'crafteos', 'stellarity'):
            name = 'g_atlas_seccion_' + key
            self.assertIn(name, self.menus)
            self.assertLessEqual(text_width(SHORT[key][0]), 53)
            req = self.menus[name]['open_requirement']['requirements']['prueba']
            self.assertEqual(req['permission'], PERMISSION)
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

    def test_cocina_denegada_abre_publica_original(self):
        import subprocess
        original = subprocess.check_output(['git', 'show', '52a04a3:build/menus/DeluxeMenus/gui_menus/g_atlas_seccion_cocina.yml'], cwd=ROOT.parent)
        public = self.menus['g_atlas_seccion_cocina_publica']
        self.assertEqual(public, yaml.safe_load(original))
        self.assertNotIn('open_requirement', public)
        commands = self.menus['g_atlas_seccion_cocina']['open_requirement']['deny_commands']
        self.assertEqual(commands, ['[openguimenu] g_atlas_seccion_cocina_publica'])
        self.assertIn('[openguimenu] guia_astral', public['items']['volver']['click_commands'])
        for name in ('g_atlas_seccion_crafteos', 'g_atlas_seccion_stellarity', 'g_guia_comida_cnk'):
            self.assertTrue(self.menus[name]['open_requirement']['deny_commands'][0].startswith('[message]'))

    def test_indice_privado_exige_permiso_y_nombre(self):
        from guia_ampliacion import requirements
        expected = requirements()
        count = 0
        for menu_name in ('guia_astral', 'guia_astral_3'):
            for item in self.menus[menu_name]['items'].values():
                commands = item.get('click_commands', [])
                if any(cmd in commands for cmd in ('[openguimenu] g_atlas_seccion_crafteos', '[openguimenu] g_atlas_seccion_stellarity')):
                    self.assertEqual(item['view_requirement']['requirements'], expected)
                    self.assertNotIn('minimum_requirements', item['view_requirement'])
                    count += 1
        self.assertEqual(count, 8)
        gate = self.menus['guia_astral_3']['open_requirement']
        self.assertEqual(gate['requirements'], expected)
        self.assertEqual(gate['deny_commands'], ['[openguimenu] guia_astral_3_publica'])
        for name, permission, allowed in [('ByTrainx', True, True), ('ByTrainx', False, False), ('Jugador', True, False), ('Jugador', False, False)]:
            self.assertEqual(permission and name == expected['dueno']['output'], allowed)

    def test_indice_publico_conserva_botones_y_huecos_originales(self):
        import subprocess
        from guia_cofre import PUBLIC_INDEX_CHARS
        for name in ('guia_astral', 'guia_astral_2', 'guia_astral_3'):
            original = yaml.safe_load(subprocess.check_output(['git', 'show', '52a04a3:build/menus/DeluxeMenus/gui_menus/' + name + '.yml'], cwd=ROOT.parent))
            public = self.menus[name + '_publica' if name == 'guia_astral_3' else name]
            self.assertNotIn('open_requirement', public)
            for item in original['items'].values():
                if item.get('display_name') == '&bCocina (Crop & Kettle)':
                    item['display_name'] = '&bComida'
            self.assertEqual(public['items'], original['items'], name)
            if name == 'guia_astral_3':
                self.assertIn(PUBLIC_INDEX_CHARS[0], public['menu_title'])

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
