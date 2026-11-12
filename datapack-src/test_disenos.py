"""Regresiones de navegacion, derechos antiguos y aislamiento de arte."""
import json
import unittest
import zipfile
import yaml
from terceros import ROOT, privado
from mobs.mascotas import MASCOTAS
from menus import mascota_detalle_menu
from cosmeticos import menu_data, equipment_menu
from lobby import cosmetic_rewards, crate_yml, GACHAS
from menu_ui import icon, NEW_KEYS


class DesignsTests(unittest.TestCase):
    def test_all_details_use_same_slots_and_return_to_correct_page(self):
        for pid,d in MASCOTAS.items():
            menu=yaml.safe_load(mascota_detalle_menu(pid))
            self.assertNotIn('&8',menu['menu_title'])
            items=menu['items']
            self.assertEqual(items['invocar']['slot'],46)
            self.assertEqual(items['descansar']['slot'],49)
            self.assertIn('mascota '+str(d['n']),str(items['invocar']['click_commands']))
            page='mascotas' if d['n']<=6 else f"mascotas_{2+(d['n']-7)//9}"
            self.assertEqual(items['coleccion']['click_commands'],['[openguimenu] '+page])

    def test_no_wings_in_rewards_or_navigation_and_legacy_rights_work(self):
        self.assertNotIn('alas',menu_data()['items'])
        for guaranteed in (False,True):
            self.assertNotIn('astral.cosmetico.alas',crate_yml('gacha_cosmeticos',GACHAS['gacha_cosmeticos'],guaranteed))
        hats=equipment_menu('sombrero')['items']
        for key,legacy in [('carnivora','carnivora'),('diablo','asura')]:
            self.assertEqual(hats[key]['view_requirement']['minimum_requirements'],1)
            self.assertIn('astral.cosmetico.alas.'+legacy,str(hats[key]['click_requirement']))

    def test_new_icons_are_distinct(self):
        blobs=[icon(key).tobytes() for key in NEW_KEYS]
        self.assertEqual(len(set(blobs)),len(blobs))

    def test_private_final_keeps_train_and_no_wing_models(self):
        from deploy_disenos import DELIVERY
        path=privado()/DELIVERY/'AstralRPG-Textures.zip'
        if not path.exists():self.skipTest('Regenerar entrega privada')
        with zipfile.ZipFile(path) as z:
            names=z.namelist()
            self.assertFalse(any('/cosmetics/' in n and '_alas' in n for n in names))
            for iid in ('asura_alas','carnivora_alas'):
                self.assertEqual(json.loads(z.read(f'assets/astral/items/{iid}.json'))['model']['model'],'minecraft:item/feather')
            for pid in MASCOTAS:
                self.assertIn(f'assets/astral/textures/font/companero/{pid}_0a.png',names)
            font=json.loads(z.read('assets/minecraft/font/default.json'))
            seen=set()
            for provider in font['providers']:
                chars=set(provider.get('advances',{}))|set(''.join(provider.get('chars',[])))
                # Las fuentes heredadas pueden repetir espacios comunes; los PUA de UI son unicos.
                chars={c for c in chars if '\ue000'<=c<='\uf8ff'}
                self.assertFalse(seen&chars,repr(seen&chars));seen.update(chars)


if __name__=='__main__':unittest.main()
