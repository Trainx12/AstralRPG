"""Integracion del arte con las zonas de clic y los permisos de viaje."""
import json
import unittest
import yaml
from adventure_ui import assets, regions, THEMES, title
from viajes_mazmorras import menu_data, exploration_menu
from menus import principal_menu


class AdventureUITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files,cls.providers=assets()
        cls.menus={'principal':yaml.safe_load(principal_menu()),
                   'mazmorras':menu_data(),'expediciones':exploration_menu()}

    def test_click_regions_match_models_and_have_no_overlaps(self):
        for kind,data in self.menus.items():
            self.assertEqual(data['size'],54)
            self.assertEqual(data['menu_title'],title(kind))
            occupied=set()
            for key,slots in regions(kind):
                self.assertFalse(occupied.intersection(slots))
                occupied.update(slots)
                for index,slot in enumerate(slots):
                    matching=[item for item in data['items'].values()
                              if item.get('item_model')==f'astral:aventuras/{kind}_{key}_{index}']
                    self.assertEqual(len(matching),1)
                    self.assertEqual(matching[0]['slot'],slot)
            for entry in data['items'].values():
                if not entry.get('item_model','').startswith('astral:aventuras/'):
                    self.assertNotIn(entry['slot'],occupied)

    def test_every_locked_and_unlocked_tile_keeps_permissions(self):
        items=self.menus['mazmorras']['items']
        for key,slots in regions('mazmorras'):
            for index,slot in enumerate(slots):
                for locked in (False,True):
                    name=key+('_bloqueada' if locked else '')
                    entry=items[name if index==0 else f'{name}_hit_{index}']
                    self.assertEqual(entry['slot'],slot)
                    self.assertEqual(entry['click_commands'],items[name]['click_commands'])
                    if locked:
                        self.assertTrue(all(c.startswith(('[message]','[sound]')) for c in entry['click_commands']))
                    else:
                        self.assertEqual(entry['click_requirement'],items[key]['click_requirement'])
                        self.assertEqual(entry['view_requirement'],items[key]['view_requirement'])

    def test_resource_references_resolve(self):
        for data in self.menus.values():
            for entry in data['items'].values():
                model=entry.get('item_model')
                if not model:continue
                namespace,path=model.split(':')
                definition=json.loads(self.files[f'assets/{namespace}/items/{path}.json'])
                model_path=definition['model']['model'].split(':')[1]
                rendered=json.loads(self.files[f'assets/{namespace}/models/{model_path}.json'])
                texture=rendered['textures']['layer0'].split(':')[1]
                self.assertIn(f'assets/{namespace}/textures/{texture}.png',self.files)

    def test_font_glyphs_are_unique_and_resolve(self):
        seen=set()
        for provider in self.providers:
            chars=''.join(provider['chars']) if provider['type']=='bitmap' else provider['advances']
            self.assertFalse(seen.intersection(chars))
            seen.update(chars)
            if provider['type']=='bitmap':
                path=provider['file'].split(':')[1]
                self.assertIn('assets/astral/textures/'+path,self.files)
        for kind in THEMES:
            self.assertTrue(set(title(kind)[2:]).issubset(seen))


if __name__=='__main__':unittest.main()
