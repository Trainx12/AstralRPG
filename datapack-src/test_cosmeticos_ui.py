"""El diseno de cosmeticos conserva la propiedad permanente de los titulos."""
import io
import json
import unittest
from PIL import Image
from lobby import TITLES
from cosmeticos import menu_data,script
from cosmeticos_ui import assets,title,TITLE_SLOTS,CLEAR_SLOTS,key_for,panel


class CosmeticsUITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files,cls.providers=assets()
        from menu_ui import assets as menu_assets
        cls.files.update(menu_assets()[0])

    def test_owned_titles_recheck_permission_and_locked_titles_cannot_equip(self):
        data=menu_data();items=data['items']
        self.assertEqual(data['size'],54)
        self.assertEqual(data['menu_title'],title())
        for index,(_,name,_) in enumerate(TITLES):
            key=key_for(name);owned=items[key];locked=items[key+'_locked']
            self.assertEqual(owned['slot'],TITLE_SLOTS[index])
            self.assertEqual(owned['slot'],locked['slot'])
            for kind in ('view_requirement','click_requirement'):
                self.assertEqual(owned[kind]['requirements']['obtenido']['permission'],'astral.cosmetico.titulo.'+key)
            self.assertEqual(owned['click_commands'],['[close]','[player] titulo '+key])
            self.assertTrue(all(c.startswith(('[message]','[sound]')) for c in locked['click_commands']))
        self.assertNotIn('permission unset',script())
        self.assertNotIn('[takemoney]',str(data))

    def test_navigation_and_entire_clear_button_have_consistent_actions(self):
        items=menu_data()['items'];occupied=set(TITLE_SLOTS)
        for i,slot in enumerate(CLEAR_SLOTS):
            entry=items['none' if i==0 else f'none_hit_{i}']
            self.assertEqual(entry['slot'],slot)
            self.assertNotIn(slot,occupied);occupied.add(slot)
            self.assertEqual(entry['click_commands'],['[close]','[player] titulo quitar'])
        self.assertEqual(items['gacha']['click_commands'],['[openguimenu] gacha_cosmeticos'])
        self.assertEqual(items['back']['click_commands'],['[openguimenu] principal'])
        for key in ('info','gacha','back','close'):self.assertNotIn(items[key]['slot'],occupied)

    def test_all_models_and_textures_resolve(self):
        for entry in menu_data()['items'].values():
            if 'item_model' not in entry:continue
            path=entry['item_model'].split(':')[1]
            definition=json.loads(self.files[f'assets/astral/items/{path}.json'])
            model=definition['model']['model'].split(':')[1]
            model=json.loads(self.files[f'assets/astral/models/{model}.json'])
            texture=model['textures']['layer0'].split(':')[1]
            image=Image.open(io.BytesIO(self.files[f'assets/astral/textures/{texture}.png']))
            self.assertEqual(image.size,(18,18))
            self.assertTrue(definition['oversized_in_gui'])

    def test_title_advance_and_transparency_match_chest_coordinates(self):
        advances={}
        for provider in self.providers:
            if provider['type']=='space':advances.update(provider['advances']);continue
            path=provider['file'].split(':')[1]
            image=Image.open(io.BytesIO(self.files['assets/astral/textures/'+path]))
            self.assertLessEqual(max(image.size),256)
            self.assertLessEqual(provider['ascent'],provider['height'])
            advances[provider['chars'][0]]=image.getbbox()[2]+1
        self.assertEqual(sum(advances[c] for c in title()[2:]),0)
        image=panel()
        for slot in (*TITLE_SLOTS,*CLEAR_SLOTS,4,8,45,53):
            self.assertEqual(image.getpixel((39+slot%9*18,65+slot//9*18))[3],0)
        for y in (187,205,223,245):
            for col in range(9):self.assertEqual(image.getpixel((39+col*18,y))[3],0)


if __name__=='__main__':unittest.main()
