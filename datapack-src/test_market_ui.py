"""Los mosaicos deben ejecutar una sola compra y referenciar arte existente."""
import io
import json
import unittest
import yaml
from PIL import Image
import menus
import market_ui
from auction_ui import patch_config
from lobby import GACHAS, TIRADAS
from test_bazar import run_deluxemenus_actions


class MarketUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files,cls.providers=market_ui.assets()
        from menu_ui import assets
        cls.files.update(assets()[0])

    def check_models(self,data):
        for item in data['items'].values():
            model=item.get('item_model')
            if model:self.assertIn('assets/astral/items/'+model.split(':')[1]+'.json',self.files)

    def test_every_roll_tile_keeps_its_price_and_single_charge(self):
        for gid,g in GACHAS.items():
            data=yaml.safe_load(menus.gacha_menu(gid,g));self.check_models(data)
            self.assertEqual(data['size'],54)
            for (_,slots),count in zip(market_ui.regions(gid),TIRADAS):
                for index,slot in enumerate(slots):
                    item=data['items'][f'x{count}_{index}']
                    self.assertEqual(item['slot'],slot)
                    self.assertEqual(item['click_requirement']['requirements']['plata']['amount'],g['cost']*count)
                    cmds=item['click_commands']
                    self.assertEqual([c for c in cmds if c.startswith('[takemoney]')],[f"[takemoney] {g['cost']*count}"])
                    opens=[c for c in cmds if 'crates forceopen ' in c]
                    self.assertEqual(len(opens),2)
                    self.assertTrue(all(c.endswith('<delay=3>') for c in opens))
                    # Las condiciones de garantia son mutuamente excluyentes.
                    self.assertIn(' unless score ',opens[1])
                    if count>1:self.assertIn(f'virtual {gid} {count-1}', ' '.join(cmds))

    def test_auction_navigation_and_no_automatic_listing(self):
        data=yaml.safe_load(menus.subastas_menu());self.check_models(data)
        for key,command in [('mercado','ah'),('publicaciones','ah listed'),('retirar','ah collect')]:
            for i in range(8):
                self.assertEqual(run_deluxemenus_actions(data['items'][f'{key}_{i}']['click_commands']),command)
        for i in range(8):
            self.assertFalse(any(c.startswith('[player]') for c in data['items'][f'publicar_{i}']['click_commands']))

    def test_font_width_and_client_limits(self):
        advances={}
        for provider in self.providers:
            if provider['type']=='space':advances.update(provider['advances'])
            else:
                im=Image.open(io.BytesIO(self.files['assets/astral/textures/'+provider['file'].split(':')[1]]))
                self.assertLessEqual(max(im.size),256)
                advances[provider['chars'][0]]=im.getbbox()[2]+1
        for kind in market_ui.GLYPHS:self.assertEqual(sum(advances[c] for c in market_ui.title(kind)[2:]),0)

    def test_native_skin_changes_only_titles(self):
        original='Settings:\n  GUIName: old\n  Players-Current-Items: old\n  Cancelled/Expired-Items: old\n  Percent-Tax: 5.0 # conservar\n  Sell-Time: 2d\n'
        changed=patch_config(original)
        self.assertIn('  Percent-Tax: 5.0 # conservar\n  Sell-Time: 2d\n',changed)
        self.assertEqual(patch_config(changed),changed)
        with self.assertRaises(ValueError):patch_config('Settings: {}')

    def test_catalog_titles_are_told_apart(self):
        # CrazyAuctions elige la logica del clic con title.contains(<titulo>).
        changed=patch_config('Settings:\n  GUIName: a\n  Players-Current-Items: b\n  Cancelled/Expired-Items: c\n')
        titles=[line.split(': ',1)[1].strip("'") for line in changed.splitlines()[1:]]
        for a in titles:
            for b in titles:
                if a is not b:self.assertNotIn(b,a)
        spaces={}
        for provider in self.providers:
            if provider['type']=='space':spaces.update(provider['advances'])
        for tag in market_ui.CATALOG_TAGS.values():self.assertEqual(spaces[tag],0)


if __name__=='__main__':unittest.main()
