"""La Guia Astral en cofre: cada pagina tiene su fondo y cada boton abre algo que existe."""
import json
import unittest
import zipfile
import yaml
from guia_cofre import ROOT, assets, menus, title, entries

DATAPACK = ROOT.parent / 'build/AstralRPG-Items.zip'


class GuiaCofreTest(unittest.TestCase):
    def test_pages_and_links(self):
        data = {k: yaml.safe_load(v) for k, v in menus(DATAPACK).items()}
        self.assertEqual(data['guia_astral']['open_command'], 'guiaastral')
        with zipfile.ZipFile(DATAPACK) as z:
            names = set(z.namelist())
        for menu in data.values():
            for it in menu['items'].values():
                for cmd in it.get('click_commands', []):
                    if 'dialog show' in cmd:
                        target = cmd.split()[-1].split('<')[0]
                        self.assertIn('data/' + target.replace(':', '/dialog/', 1) + '.json', names)
                    if '[openguimenu]' in cmd:
                        self.assertIn(cmd.split()[-1], data)
        self.assertEqual(sum(len([k for k in m['items'] if k.endswith('_icono')]) for m in data.values()), len(entries(DATAPACK)))

    def test_font_covers_titles_and_glyphs_fit(self):
        files, providers = assets(DATAPACK)
        chars = {c for p in providers for c in (p.get('chars') or []) + list(p.get('advances', {}))}
        for page in range(len(menus(DATAPACK))):
            self.assertTrue(set(title(page)[2:]) <= chars)
        for p in providers:
            if 'file' in p:
                self.assertIn('assets/astral/textures/' + p['file'].split(':')[1], files)

    def test_esc_opens_launcher(self):
        with zipfile.ZipFile(DATAPACK) as z:
            esc = json.loads(z.read('data/astral/dialog/guia_esc.json'))
        self.assertEqual(esc['action']['action'], {'type': 'run_command', 'command': 'guiaastral'})


if __name__ == '__main__':
    unittest.main()
