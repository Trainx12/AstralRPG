"""Integracion del escenario con la cinta CSGO y la fuente del pack."""
import io
import unittest
import yaml
from PIL import Image
import gacha_ui
from lobby import GACHAS, crate_yml


class GachaUI(unittest.TestCase):
    def test_titles_resolve_to_zero_width_and_fit_client(self):
        files, providers = gacha_ui.assets()
        advances = {}
        for provider in providers:
            if provider['type'] == 'space':
                advances.update(provider['advances'])
            else:
                path = 'assets/astral/textures/'+provider['file'].split(':')[1]
                image = Image.open(io.BytesIO(files[path]))
                self.assertLessEqual(max(image.size),256)
                self.assertLessEqual(provider['ascent'],provider['height'])
                advances[provider['chars'][0]] = image.getbbox()[2]+1
        for kind in gacha_ui.KINDS:
            self.assertEqual(sum(advances[c] for c in gacha_ui.title(kind).split('<white>')[1]),0)
            image = gacha_ui.panel(kind)
            self.assertEqual(image.size,(224,224))
            for col in range(9):
                # La cinta tiene fondo; el inventario conserva sus huecos.
                self.assertEqual(image.getpixel((32+col*18,76))[3],255)
                self.assertEqual(image.getpixel((32+col*18,126))[3],0)

    def test_regular_and_pity_crates_use_same_scene_without_glass(self):
        for kind,g in GACHAS.items():
            for pity in (False,True):
                crate = yaml.safe_load(crate_yml(kind,g,pity))['Crate']
                self.assertEqual(crate['CrateType'],'CSGO')
                self.assertEqual(crate['Animation']['Name'],gacha_ui.title(kind))
                self.assertFalse(crate['Settings']['Border']['Glass-Border']['Toggle'])
                self.assertEqual(crate['Settings']['CSGO'],{'Finished-Material':'air','Cycle-Material':'air'})
                self.assertEqual(crate['Animation']['Glass-Frame']['Items'],{})
                self.assertTrue(crate['Prizes'])
                self.assertAlmostEqual(sum(p['Weight'] for p in crate['Prizes'].values()),100,places=2)


if __name__ == '__main__':
    unittest.main()
