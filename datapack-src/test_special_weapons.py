"""Integridad de la entrega: kits separados, modelos y objetos compatibles."""
import json
from pathlib import Path
import unittest
import zipfile
from special_weapons import WEAPONS
from special_weapons3d import MODELS
from varitas3d import check

ROOT=Path(__file__).resolve().parent.parent


class SpecialWeaponTests(unittest.TestCase):
    def test_specials_fit_in_box_and_are_excluded_from_class_kits(self):
        with zipfile.ZipFile(ROOT/'build/AstralRPG-Items.zip') as z:
            special=json.loads(z.read('data/astral/loot_table/kit/especiales.json'))
            entries=special['pools'][0]['entries'][0]['functions'][0]['entries']
            self.assertLessEqual(len(entries),27)
            ids={e['value'] for e in entries}
            self.assertTrue({'astral:item/'+i for i in WEAPONS} <= ids)
            for kit in ('berserker','arquero','mago','armas'):
                data=z.read(f'data/astral/loot_table/kit/{kit}.json').decode()
                for iid in WEAPONS:self.assertNotIn('astral:item/'+iid+'"',data)

    def test_every_weapon_has_a_resolved_animated_model(self):
        self.assertEqual(set(WEAPONS),{w.iid for w in MODELS})
        self.assertEqual(check(MODELS),[])
        with zipfile.ZipFile(ROOT/'build/AstralRPG-Textures.zip') as z:
            for iid in WEAPONS:
                item=json.loads(z.read(f'assets/astral/items/{iid}.json'))
                model=item['model']['model'].replace('astral:','assets/astral/models/')+'.json'
                self.assertTrue(json.loads(z.read(model))['elements'])
                self.assertIn(f'assets/astral/textures/item/armas3d/{iid}.png.mcmeta',z.namelist())

    def test_weapon_stats_and_auraskills_interaction_marker_survive_export(self):
        with zipfile.ZipFile(ROOT/'build/AstralRPG-Items.zip') as z:
            for iid,w in WEAPONS.items():
                loot=json.loads(z.read(f'data/astral/loot_table/item/{iid}.json'))
                comp=next(f['components'] for f in loot['pools'][0]['entries'][0]['functions'] if f['function']=='minecraft:set_components')
                self.assertEqual(comp['minecraft:item_model'],'astral:'+iid)
                self.assertIn('"auraskills:ignore_interact":1b',comp['minecraft:custom_data'])
                self.assertNotIn('requirements',comp['minecraft:custom_data'])
                damage=next(m for m in comp['minecraft:attribute_modifiers'] if m['type']=='minecraft:attack_damage')
                from escala import FACTOR_ARMA, TIER_ESPECIAL
                self.assertAlmostEqual(damage['amount']+1,w['damage']*FACTOR_ARMA[TIER_ESPECIAL],places=2)


if __name__=='__main__':unittest.main()
