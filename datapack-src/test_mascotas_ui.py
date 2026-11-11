"""Las tarjetas del santuario conservan permisos, niveles y ordenes de mascota."""
import io
import json
import unittest
import yaml
from PIL import Image
from menus import mascotas_menu,SCORE
from mascotas_ui import assets,title,regions,REST_SLOTS,portrait,panel
from mobs.mascotas import MASCOTAS


class PetsUITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files,cls.providers=assets()
        cls.menu=yaml.safe_load(mascotas_menu())

    def test_all_tiles_have_the_correct_permission_and_invocation(self):
        self.assertEqual(self.menu['menu_title'],title())
        self.assertEqual(self.menu['size'],54)
        self.assertEqual(self.menu['open_command'],'mascotas')
        self.assertEqual(self.menu['update_interval'],1)
        occupied=set()
        for pid,slots in regions():
            for index,slot in enumerate(slots):
                self.assertNotIn(slot,occupied);occupied.add(slot)
                key=f'm_{pid}' if index==0 else f'm_{pid}_hit_{index}'
                owned=self.menu['items'][key];locked=self.menu['items'][key+'_no']
                self.assertEqual(owned['slot'],slot)
                self.assertEqual(locked['slot'],slot)
                for kind in ('view_requirement','left_click_requirement'):
                    self.assertEqual(owned[kind]['requirements']['tiene']['permission'],'astral.mascota.'+pid)
                self.assertEqual(owned['left_click_commands'],['[close]',f'[console] scoreboard players set %player_name% mascota {MASCOTAS[pid]["n"]}'])
                self.assertTrue(all(c.startswith(('[message]','[sound]')) for c in locked['left_click_commands']))
                for entry in (owned,locked):self.assertEqual(entry['right_click_commands'],[f'[openguimenu] mascota_{pid}'])
                self.assertIn(SCORE.format('plv_'+pid),str(owned['lore']))
                self.assertIn(MASCOTAS[pid]['fuente'],str(locked['lore']))

    def test_rest_button_and_navigation_do_not_overlap_cards(self):
        cards={slot for _,slots in regions() for slot in slots}
        for i,slot in enumerate(REST_SLOTS):
            item=self.menu['items']['guardar' if i==0 else f'guardar_hit_{i}']
            self.assertEqual(item['slot'],slot)
            self.assertNotIn(slot,cards)
            self.assertEqual(item['click_commands'],['[close]','[console] scoreboard players set %player_name% mascota 98'])
        self.assertEqual(self.menu['items']['gacha']['click_commands'],['[openguimenu] gacha_monturas'])
        self.assertEqual(self.menu['items']['volver']['click_commands'],['[openguimenu] principal'])
        for key in ('info','gacha','volver','cerrar'):
            self.assertNotIn(self.menu['items'][key]['slot'],cards|set(REST_SLOTS))

    def test_all_models_and_real_pet_portraits_exist(self):
        for item in self.menu['items'].values():
            path=item.get('item_model')
            if not path:continue
            path=path.split(':')[1]
            definition=json.loads(self.files[f'assets/astral/items/{path}.json'])
            model=definition['model']['model'].split(':')[1]
            model=json.loads(self.files[f'assets/astral/models/{model}.json'])
            texture=model['textures']['layer0'].split(':')[1]
            image=Image.open(io.BytesIO(self.files[f'assets/astral/textures/{texture}.png']))
            self.assertEqual(image.size,(18,18))
            self.assertTrue(definition['oversized_in_gui'])
        for pid in (pid for pid, d in MASCOTAS.items() if d["n"] <= 6):
            self.assertIsNotNone(portrait(pid).getbbox())
            self.assertLessEqual(portrait(pid).width,46)
            self.assertLessEqual(portrait(pid).height,22)

    def test_font_limits_and_transparent_inventory(self):
        advances={}
        for provider in self.providers:
            if provider['type']=='space':advances.update(provider['advances']);continue
            image=Image.open(io.BytesIO(self.files['assets/astral/textures/'+provider['file'].split(':')[1]]))
            self.assertLessEqual(max(image.size),256)
            self.assertLessEqual(provider['ascent'],provider['height'])
            advances[provider['chars'][0]]=image.getbbox()[2]+1
        self.assertEqual(sum(advances[c] for c in title()[2:]),0)
        image=panel()
        for slot in (4,8,45,53,*REST_SLOTS,*[s for _,slots in regions() for s in slots]):
            self.assertEqual(image.getpixel((39+slot%9*18,65+slot//9*18))[3],0)
        for y in (187,205,223,245):
            for col in range(9):self.assertEqual(image.getpixel((39+col*18,y))[3],0)


if __name__=='__main__':unittest.main()


class PetDetailTests(unittest.TestCase):
    """Mi companero: una pantalla por mascota, con nivel, barra y mejoras reales."""

    def test_detail_menus(self):
        from menus import mascota_detalle_menu
        from companero_ui import title as detail_title, LEVEL_SLOTS, XP_SLOTS, PERK_ROWS, PERK_LEVELS, assets as companero_assets
        files, _ = companero_assets()
        for pid in (pid for pid, d in MASCOTAS.items() if d["n"] <= 6):
            data = yaml.safe_load(mascota_detalle_menu(pid))
            items = data['items']
            self.assertEqual(data['menu_title'], detail_title(pid))
            for i, slot in enumerate(LEVEL_SLOTS):
                for level in (1, 12, 30):
                    entry = items[f'nivel_{level}_{i}']
                    self.assertEqual(entry['slot'], slot)
                    self.assertEqual(entry['view_requirement']['requirements']['nivel']['output'], str(level))
                self.assertEqual(items[f'nivel_base_{i}']['priority'], 31)
            for j, slot in enumerate(XP_SLOTS):
                full = items[f'xp_{j}_full']
                self.assertEqual(full['slot'], slot)
                self.assertEqual(full['view_requirement']['minimum_requirements'], 1)
                self.assertEqual(full['view_requirement']['requirements']['lleno']['input'], SCORE.format('pmod_' + pid))
            for row, level in zip(PERK_ROWS, PERK_LEVELS):
                ok = items[f'estado_{level}']
                self.assertEqual(ok['slot'], row * 9 + 8)
                self.assertEqual(ok['view_requirement']['requirements']['nivel']['output'], str(level))
            self.assertEqual(items['invocar']['click_requirement']['requirements']['tiene']['permission'], 'astral.mascota.' + pid)
            self.assertEqual(items['coleccion']['click_commands'], ['[openguimenu] mascotas'])
            slots = [entry['slot'] for entry in items.values()]
            self.assertTrue(all(0 <= slot < 54 for slot in slots))
            for entry in items.values():
                model = entry.get('item_model')
                if model and model.startswith('astral:companero/'):
                    self.assertIn('assets/astral/items/companero/' + model.split('/')[1] + '.json', files)
