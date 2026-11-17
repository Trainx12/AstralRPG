"""Contrato de requisitos PDC y orden de validacion para habilidades por clic."""
import json
from pathlib import Path
import re
import unittest
import zipfile

from items import STAFFS
from special_weapons import WEAPONS

ROOT = Path(__file__).resolve().parents[1]


class RequisitosClic(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.script = (ROOT/'build/gameplay/astral_armas_especiales.sk').read_text('utf8')

    def function(self, name):
        return self.script.split(f'function {name}(', 1)[1].split('\nfunction ', 1)[0]

    def test_todos_los_bastones_usan_el_requisito_del_pdc(self):
        with zipfile.ZipFile(ROOT/'build/AstralRPG-Items.zip') as z:
            for t, staff in enumerate(STAFFS, 1):
                loot = json.loads(z.read(f'data/astral/loot_table/item/baston_{t}.json'))
                custom = loot['pools'][0]['entries'][0]['functions'][0]['components']['minecraft:custom_data']
                self.assertIn(f'"auraskills:sorcery":{staff["lvl"]}', custom)
                self.assertRegex(self.script, rf'(?m)^    req_baston_{t}: {staff["lvl"]}$')
                self.assertIn(f'"Hechiceria", {{@req_baston_{t}}}', self.function('asw_requirement'))
        self.assertEqual(STAFFS[4]['lvl'], 32)
        self.assertEqual(len(STAFFS), 10)

    def test_se_valida_antes_de_cobrar_y_lanzar(self):
        staff = self.function('asw_staff')
        self.assertLess(staff.index('asw_request('), staff.index('asw_requirement('))
        self.assertLess(staff.index('asw_requirement('), staff.index('asw_pay('))
        self.assertLess(staff.index('asw_pay('), staff.index('astral:spell/cast'))
        click = self.script.split('on right click:', 1)[1].split('on uncancelled damage', 1)[0]
        water, special = click.split('if scoreboard tags of player does not contain "astral.special":', 1)
        self.assertLess(water.index('asw_requirement('), water.index('asw_pay('))
        self.assertLess(special.index('asw_requirement('), special.index('asw_hero('))
        for text in (staff, water, special):
            self.assertIn('is not {_held}', text)
            self.assertIn('asw_identify(', text)

    def test_sin_datos_no_se_permite_y_sin_datos_viejos(self):
        request = self.function('asw_request')
        self.assertIn('delete {-asw.skill::', request)
        self.assertIn('delete {-asw.mana::', request)
        for skill in ('sorcery', 'fighting', 'archery'):
            self.assertIn(f'%%auraskills_{skill}%%', request)
        level = self.function('asw_level')
        self.assertRegex(level, r'if \{_level\} is not set:[\s\S]*?return false')
        self.assertIn('if {_level} < {_req}:', level)
        self.assertIn('entity.villager.no', level)
        self.assertIn('No se pudo leer el mana.', level)

    def test_otros_clics_coinciden_con_pdc_y_especiales_sin_requisito(self):
        checks = self.function('asw_requirement')
        with zipfile.ZipFile(ROOT/'build/AstralRPG-Items.zip') as z:
            for iid in ('agua_espada', 'espada_heroe_errante'):
                loot = json.loads(z.read(f'data/astral/loot_table/item/{iid}.json'))
                custom = loot['pools'][0]['entries'][0]['functions'][0]['components']['minecraft:custom_data']
                req = int(re.search(r'"auraskills:fighting":(\d+)', custom)[1])
                self.assertIn(f'"fighting", "Combate", {req}', checks)
            for iid in WEAPONS:
                self.assertNotIn('astral.special.' + iid + '"', checks)


if __name__ == '__main__':
    unittest.main()
