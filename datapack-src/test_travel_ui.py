"""Contratos de fuentes, acciones, regeneración y salidas de Portales/Minas."""
import io
import json
import re
import unittest
import zipfile
from pathlib import Path
from PIL import Image
import yaml
import minas
import portales
import travel_ui as ui

ROOT = Path(__file__).resolve().parents[1]


class TravelUI(unittest.TestCase):
    def test_portal_buttons_and_yaml(self):
        data=yaml.safe_load((ROOT/'build/menus/DeluxeMenus/gui_menus/portales.yml').read_text(encoding='utf-8'))
        self.assertEqual(data,portales.menu_data())
        self.assertEqual({i['slot'] for i in data['items'].values()},ui.USED['portales'])
        for key,item in data['items'].items():
            self.assertTrue(item['click_commands'],key)
            self.assertEqual(item['item_model'],f'astral:viajes/{key}')
        for key in ('nether','end','lobby'):
            self.assertIn(f'[player] umbrales {key}<delay=3>',data['items'][key]['click_commands'])
        for key in ('parkour','arenas'):
            self.assertEqual(data['items'][key]['click_commands'],[f'[openguimenu] {key}'])

    def test_mine_click_mapping_and_generated_script(self):
        script=minas.script()
        self.assertEqual(script,(ROOT/'build/minas/Skript/scripts/astral_minas.sk').read_text(encoding='utf-8'))
        destinations=dict((int(s),int(i)) for s,i in re.findall(r'set \{-am.dest::(\d+)\} to (\d+)',script))
        self.assertEqual(destinations,{minas.slot(i):i for i in range(1,21)})
        self.assertEqual(set(destinations)|{4,9,18,27,45,49,53},ui.USED['minas'])
        for snippet in ('set {_dest} to {-am.dest::%{_slot}%}', 'am_travel(player, {_dest})',
                        'if {_slot} is 49:', 'if {_slot} is 53:', 'if {_slot} is 13:',
                        'else if {_slot} is 22:', 'am_sell(player)', 'cancel event'):
            self.assertIn(snippet,script)
        self.assertIn(ui.title('minas'),script)
        self.assertIn(ui.title('minas-venta'),script)

    def test_previous_sidebar_is_complete(self):
        from lobby import TAB_SECTIONS
        yaml.safe_load(TAB_SECTIONS)
        self.assertEqual(TAB_SECTIONS,(ROOT/'build/lobby/TAB/secciones-config.yml').read_text(encoding='utf-8'))
        script=minas.script()
        for score in ('am_regen_m','am_regen_s','am_left','am_segments'):
            self.assertIn(f'"{score}"',script)
            self.assertIn('am_score({_p}, "'+score+'",',script)
            self.assertIn('am_score',script)
            self.assertIn('am_'+score[3:],TAB_SECTIONS)
        for goal in minas.GOALS[1:]:
            for blocks in (0,goal//2,goal,goal+1):
                shown=min(blocks,goal)
                self.assertTrue(0<=8*shown//goal<=8)
                self.assertGreaterEqual(goal-shown,0)
        self.assertIn('am_regen_sidebar(loop-player, {_i})',script)
        self.assertIn('am_sidebar_blocks(loop-player)',script)

    def test_assets_dimensions_advances_and_models(self):
        files,providers=ui.assets(); advances={}
        for provider in providers:
            if provider['type']=='space': advances.update(provider['advances']); continue
            path='assets/astral/textures/'+provider['file'].split(':')[1]
            im=Image.open(io.BytesIO(files[path]))
            self.assertLessEqual(max(im.size),256)
            self.assertLessEqual(provider['ascent'],provider['height'])
            advances[provider['chars'][0]]=im.getbbox()[2]+1
        for kind in ui.KINDS:
            self.assertEqual(sum(advances[c] for c in ui.title(kind)[2:]),0)
        models=re.findall(r'"astral:viajes/([a-z0-9]+)"',minas.script())
        models += list(portales.menu_data()['items'])
        for name in models:
            self.assertIn(f'assets/astral/items/viajes/{name}.json',files)
            json.loads(files[f'assets/astral/items/viajes/{name}.json'])

    def test_pack_has_exact_assets_and_no_glyph_collisions(self):
        files,_=ui.assets()
        with zipfile.ZipFile(ROOT/'build/AstralRPG-Textures.zip') as pack:
            for path,data in files.items(): self.assertEqual(pack.read(path),data,path)
            seen=set()
            for provider in json.loads(pack.read('assets/minecraft/font/default.json'))['providers']:
                chars=provider.get('advances',{}) if provider['type']=='space' else ''.join(provider.get('chars',[]))
                for char in chars:
                    if 0xe900<=ord(char)<=0xe911:
                        self.assertNotIn(char,seen,'glifo de viajes repetido')
                        seen.add(char)
            self.assertEqual(len(seen),18)


if __name__=='__main__': unittest.main()
