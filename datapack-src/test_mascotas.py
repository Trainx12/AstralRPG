"""Modelos, previsualizacion de beneficios y permisos de las mascotas."""
import unittest
import re
import yaml
from menus import mascotas_menu
from mascotas_ui import regions, card
from mobs.mascotas import MASCOTAS, beneficios_actuales
from mobs import build_models


class MascotasTests(unittest.TestCase):
    def test_real_bonuses_accumulate_and_upgrades_replace_lower_amplifiers(self):
        self.assertEqual(beneficios_actuales('zorro', 9), ['Velocidad I'])
        self.assertEqual(beneficios_actuales('zorro', 10), ['Velocidad I', 'Salto I'])
        self.assertEqual(beneficios_actuales('zorro', 20), ['Velocidad II', 'Salto I'])
        self.assertEqual(beneficios_actuales('lobo', 30), ['Fuerza I', 'Velocidad I', 'Resistencia I'])
        for level, minutes in ((1, 10), (10, 7), (20, 5)):
            self.assertIn(f'cada {minutes} min', beneficios_actuales('fenix', level)[0])
        self.assertIn('Marca a los mobs cercanos', beneficios_actuales('cuervo', 1))

    def test_every_portrait_tile_previews_current_and_future_bonuses(self):
        data = yaml.safe_load(mascotas_menu())
        for pid, slots in regions():
            for index, slot in enumerate(slots):
                key = f'm_{pid}' if index == 0 else f'm_{pid}_hit_{index}'
                for priority, level in enumerate((20, 10, 1), 1):
                    entry = data['items'][key if level == 1 else key + f'_nv{level}']
                    self.assertEqual(entry['slot'], slot)
                    self.assertEqual(entry['priority'], priority)
                    reqs = entry['view_requirement']['requirements']
                    self.assertEqual(reqs['tiene']['permission'], 'astral.mascota.' + pid)
                    if level > 1:
                        self.assertEqual(reqs['nivel']['type'], '>=')
                        self.assertEqual(reqs['nivel']['output'], str(level))
                    for bonus in beneficios_actuales(pid, level):
                        self.assertIn('&f+ ' + bonus, entry['lore'])
                    self.assertIn('left_click_requirement', entry)
                    self.assertEqual(entry['right_click_commands'], [f'[openguimenu] mascota_{pid}'])
                locked = data['items'][key + '_no']
                self.assertEqual(locked['priority'], 4)
                self.assertTrue(all(c.startswith(('[message]', '[sound]')) for c in locked['left_click_commands']))
                self.assertEqual(locked['right_click_commands'], [f'[openguimenu] mascota_{pid}'])
                for stage in MASCOTAS[pid]['texto']:
                    self.assertTrue(any(stage in line for line in locked['lore']))

    def test_exported_geometry_and_animation_references_are_valid(self):
        for pid in MASCOTAS:
            m = getattr(build_models.creatures, 'mascota_' + pid)()
            data, texture = m.export()
            self.assertEqual(m.name, 'astral_pet_' + pid)
            self.assertEqual(set(m.anims), {'idle', 'walk'})
            self.assertTrue(all(c['bone'] in m.bones for c in m.cubes))
            for c in m.cubes:
                self.assertTrue(all(b > a for a, b in zip(c['from'], c['to'])))
            for _, _, channels in m.anims.values():
                self.assertTrue(set(channels) <= set(m.bones))
                # BetterModel rechaza numerales Molang excesivamente largos.
                self.assertIsNone(re.search(r'\d+\.\d{10}', str(channels)))
            for e in data['elements']:
                for face in e['faces'].values():
                    x0,y0,x1,y1 = face['uv']
                    self.assertTrue(0 <= x0 < x1 <= texture.width)
                    self.assertTrue(0 <= y0 < y1 <= texture.height)
            self.assertEqual(card(pid).size, (54, 36))
            self.assertEqual(card(pid, locked=True).size, (54, 36))


if __name__ == '__main__':
    unittest.main()
