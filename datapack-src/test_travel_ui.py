"""Contratos de fuentes, acciones, regeneración y salidas de Portales/Minas."""
import io
import json
import math
import minijuegos
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
    def test_imagegen_sources_and_preview_sizes(self):
        for kind,(art,cuts,_,_,_) in ui.THEMES.items():
            source=Image.open(ROOT/f'datapack-src/pack-source/ref/{art}-frame.png')
            self.assertEqual(source.mode,'RGBA')
            self.assertEqual(source.getextrema()[3],(0,255))
            left,top,right,bottom=cuts
            self.assertTrue(0<left<right<source.width)
            self.assertTrue(0<top<bottom<source.height)
            with Image.open(ROOT/f'build/Interfaces-preview/{kind}.png') as preview:
                self.assertEqual(preview.size,(672,840))

    def test_all_inventory_holes_and_grid_alignment(self):
        for kind in ui.KINDS:
            panel=ui.panel(kind)
            shift=(6-ui.ROWS[kind])*18
            for row in range(4):
                y=(179+row*18 if row<3 else 237)-shift
                for col in range(9):
                    self.assertEqual(panel.getpixel(((32+col*18)*2,(y+1)*2))[3],0)
            # Ascent 53 coloca el primer slot en y=57, igual que servicios.
            self.assertEqual(ui.GRID_Y,57)
            for mapping in (ui.CARD_SLOTS,ui.ARENA_SLOTS):
                for slots in mapping.values():
                    self.assertEqual({s//9 for s in slots},{0,1,2,3})

    def test_portal_buttons_and_yaml(self):
        data=yaml.safe_load((ROOT/'build/menus/DeluxeMenus/gui_menus/portales.yml').read_text(encoding='utf-8'))
        self.assertEqual(data,portales.menu_data())
        self.assertEqual({i['slot'] for i in data['items'].values()},ui.USED['portales'])
        for key,item in data['items'].items():
            self.assertTrue(item['click_commands'],key)
            if key=='lobby':self.assertEqual(item['material'],'BARRIER')
            elif key=='oceano':self.assertEqual(item['material'],'HEART_OF_THE_SEA')  # item vanilla visible
            else:self.assertEqual(item['item_model'],'astral:viajes/blank')
            base=key.split('_')[0]
            self.assertEqual(item['click_commands'],data['items'][base]['click_commands'])
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
                        'if {_slot} is 49:', 'if {_slot} is 53:', 'if {_slot} is between 28 and 34:',
                        'else if {_slot} is 35:', 'am_sell(player)', 'cancel event'):
            self.assertIn(snippet,script)
        self.assertIn(ui.title('minas'),script)
        self.assertIn(ui.title('minas-venta'),script)

    def test_cards_cover_exact_slots_and_actions(self):
        for kind,data,mapping in [('portales',portales.menu_data(),ui.CARD_SLOTS),('arenas',minijuegos.menu_data('arena'),ui.ARENA_SLOTS)]:
            slots=[i['slot'] for i in data['items'].values()]
            self.assertEqual(len(slots),len(set(slots)))
            # Arenas suma el boton de duelos (duelos.py) en la fila de abajo, fuera del arte.
            from duelos import ARENAS_BUTTON_SLOT
            self.assertEqual(set(slots),ui.USED[kind]|({ARENAS_BUTTON_SLOT} if kind=='arenas' else set()))
            self.assertEqual(data['size'],ui.ROWS[kind]*9)
            self.assertEqual(data['menu_title'],ui.title(kind))
            for key,expected in mapping.items():
                card=[v for k,v in data['items'].items() if k==key or k.startswith(key+'_')]
                self.assertEqual({i['slot'] for i in card},set(expected))
                for item in card:
                    self.assertEqual(item['click_commands'],data['items'][key]['click_commands'])
                    self.assertEqual(item['item_model'],'astral:viajes/blank')
            if kind=='arenas':
                self.assertFalse(any(k.startswith('proximo') for k in data['items']))
                for d in minijuegos.ARENAS:
                    self.assertEqual(data['items'][d['id']]['click_commands'],['[close]',f'[player] arenas {d["id"]}<delay=3>'])
                self.assertEqual(data['items']['desafiar']['click_commands'],['[close]','[player] desafiar<delay=3>'])

    def test_sale_states_and_transparent_inventory(self):
        script=minas.script()
        self.assertEqual(ui.SALE_SLOTS,tuple(range(28,35)))
        for value in ('loop 7 times:', 'set {_s} to 27 + loop-number','if {_slot} is between 28 and 34:', 'else if {_slot} is 35:', 'set slot 35 of {_inv}', 'Recibis: &6%{_value}% oro'):
            self.assertIn(value,script)
        self.assertIn('astral:viajes/mine_%{_i}%_%{_state}%',script)
        for state in ('open','next','locked'):self.assertIn(f'set {{_state}} to "{state}"',script)
        files,_=ui.assets()
        self.assertIsNone(Image.open(io.BytesIO(files['assets/astral/textures/item/viajes/blank.png'])).getbbox())
        for kind in ui.KINDS:
            panel=ui.panel(kind)
            y=179-(6-ui.ROWS[kind])*18
            self.assertEqual(panel.getpixel((64,(y+1)*2))[3],0)
        # La venta compartida conserva exclusiones y el cobro de Minas.
        for snippet in ('if name of {_it} is not set:', 'if lore of {_it} is not set:',
                        'set {_price} to {-am.price::%type of {_it}%}',
                        'set {_price} to {-ab.price::%type of {_it}%}',
                        "set slot {_slot} of {_p}'s inventory to air", "add {_total} to {_p}'s balance"):
            self.assertIn(snippet, script)

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
            self.assertLessEqual(im.height,256)
            self.assertEqual(im.width,224)
            self.assertLessEqual(provider['ascent'],provider['height'])
            advances[provider['chars'][0]]=math.ceil(im.getbbox()[2]*provider['height']/im.height)+1
        for kind in ui.KINDS:
            self.assertEqual(sum(advances[c] for c in ui.title(kind)[2:]),0)
        models=re.findall(r'"astral:viajes/([a-z0-9]+)"',minas.script())
        models += ['blank']
        models += [f'mine_{i}_{state}' for i in range(1,21) for state in ('open','next','locked')]
        for name in models:
            self.assertIn(f'assets/astral/items/viajes/{name}.json',files)
            json.loads(files[f'assets/astral/items/viajes/{name}.json'])

    def test_tiled_font_reconstructs_every_panel(self):
        files,providers=ui.assets()
        for kind in ui.KINDS:
            source=ui.panel(kind)
            restored=Image.new('RGBA',source.size)
            for n,(start,end) in enumerate(ui.slices(kind)):
                for col in range(2):
                    path=f'assets/astral/textures/font/viajes/{kind}_{n}_{col}.png'
                    tile=Image.open(io.BytesIO(files[path]))
                    restored.alpha_composite(tile,(col*224,start*2))
            self.assertEqual(restored.tobytes(),source.tobytes())
        # Se simula el cursor real: cada par de mosaicos comienza en x=0 y x=112.
        advances=next(p['advances'] for p in providers if p['type']=='space')
        for kind in ui.KINDS:
            cursor=0;positions=[]
            for char in ui.title(kind)[2:]:
                if char in advances:cursor+=advances[char]
                else:
                    positions.append(cursor)
                    provider=next(p for p in providers if p.get('chars')==[char])
                    im=Image.open(io.BytesIO(files['assets/astral/textures/'+provider['file'].split(':')[1]]))
                    cursor+=math.ceil(im.getbbox()[2]/2)+1
            self.assertEqual(positions,[-32,80]*len(ui.slices(kind)))
            self.assertEqual(cursor,0)

    def test_pack_has_exact_assets_and_no_glyph_collisions(self):
        files,_=ui.assets()
        with zipfile.ZipFile(ROOT/'build/AstralRPG-Textures.zip') as pack:
            for path,data in files.items(): self.assertEqual(pack.read(path),data,path)
            seen=set()
            for provider in json.loads(pack.read('assets/minecraft/font/default.json'))['providers']:
                chars=provider.get('advances',{}) if provider['type']=='space' else ''.join(provider.get('chars',[]))
                for char in chars:
                    if 0xe900<=ord(char)<=0xe93f:
                        self.assertNotIn(char,seen,'glifo de viajes repetido')
                        seen.add(char)
            self.assertEqual(len(seen),sum(len(ui.title(k))-2 for k in ui.KINDS))


if __name__=='__main__': unittest.main()
