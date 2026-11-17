"""Regresiones del retiro y de las seis ventanas Gemini."""
from pathlib import Path
import io
import json
import re
import unittest
import zipfile
import yaml
from PIL import Image
from mobs.mascotas import MASCOTAS,RETIRADAS,skill_yml,migration_skript
from mascotas_ui import regions,page_regions,PAGES
from ventanas_1611 import WINDOWS,assets,apply
ROOT=Path(__file__).resolve().parents[1]

class RetiroVentanasTests(unittest.TestCase):
    def test_catalog_compact_and_stable_ids(self):
        pets=[p for p,_ in regions()]+[p for page in PAGES for p,_ in page_regions(page)]
        self.assertEqual(pets,list(MASCOTAS));self.assertEqual(len(pets),18)
        self.assertEqual(len(set(pets)),18);self.assertEqual(MASCOTAS['fenix']['n'],6)
        self.assertEqual([d['n'] for d in MASCOTAS.values()],list(range(6,24)))
        self.assertTrue(set(RETIRADAS).isdisjoint(pets))
        self.assertEqual([len(regions()),*[len(page_regions(page)) for page in PAGES]],[6,6,6])

    def test_no_retired_routes_in_outputs(self):
        folder=ROOT/'build/menus/DeluxeMenus/gui_menus'
        for pid in RETIRADAS:
            self.assertFalse((folder/f'mascota_{pid}.yml').exists())
            self.assertNotIn('PET_GANAR_'+pid.upper(),skill_yml())
        self.assertFalse((folder/'mascotas_4.yml').exists())
        for folder in (folder,ROOT/'build/lobby/CrazyCrates/crates',ROOT/'build/mythicmobs'):
            for p in folder.rglob('*.yml'):
                text=p.read_text(encoding='utf8')
                for pid in RETIRADAS:
                    self.assertNotRegex(text,r'astral\.mascota\.'+pid+r'\b',str(p))
                    self.assertNotIn('PET_GANAR_'+pid.upper(),text,str(p))
        with zipfile.ZipFile(ROOT/'build/AstralRPG-Items.zip') as z:
            guide=''.join(z.read(f'data/astral/dialog/guia/mascotas_{i}.json').decode() for i in (1,2,3))
            for name in ('Lobo del Bosque','Cuervo Arcano','Golem de Piedra','Zorro Espectral','Dragoncito de Fuego'):self.assertNotIn(name,guide)
            self.assertIn('Fenix',guide)

    def test_migration_is_per_uuid_pet_and_keeps_data(self):
        sk=migration_skript()
        self.assertIn('uuid of player',sk)
        self.assertEqual(sk.count('crates give virtual gacha_monturas 1'),5)
        for pid in RETIRADAS:
            self.assertIn(f'astral.pet_retiro_1611::%{{_u}}%::{pid}',sk)
            self.assertIn(f'tag=astral.pet.{pid},distance=0..',sk)
        self.assertNotIn('delete ',sk);self.assertNotIn('reset ',sk)
        self.assertNotIn('pxp_',sk);self.assertNotIn('permission unset',sk)

    def test_aurora_no_longer_generated_or_scheduled(self):
        java=(ROOT/'datapack-src/runtime/AstralOceano.java').read_text(encoding='utf8')
        self.assertNotIn('aurora',java.lower())
        mobs=yaml.safe_load((ROOT/'build/mythicmobs/mobs/fosa.yml').read_text(encoding='utf8'))
        self.assertNotIn('astral_aurora',mobs)
        with zipfile.ZipFile(ROOT/'build/oceano/AstralOceano.jar') as z:
            self.assertNotIn(b'auroraTick',z.read('astral/AstralOceano.class'))
            self.assertIn('1.4.0',z.read('plugin.yml').decode())

    def test_gemini_layouts_slots_actions_active_and_models(self):
        files,providers=assets()
        for p in providers:
            if p['type']=='bitmap':self.assertLessEqual(p['height'],256)
        for kind,(_,rows,*_) in WINDOWS.items():
            data=yaml.safe_load((ROOT/f'build/menus/DeluxeMenus/gui_menus/{kind}.yml').read_text(encoding='utf8'))
            if kind == 'configuraciones':
                self.assertEqual(data['size'],45)
                continue
            self.assertEqual(data['size'],rows*9)
            self.assertIn('\uf100',data['menu_title'])
            occupied={}
            for key,item in data['items'].items():
                slot=item['slot'];self.assertTrue(0<=slot<data['size'],(kind,key,slot))
                if slot in occupied:self.assertIn('priority',item,(kind,key,slot))
                occupied[slot]=key
                if any(k.endswith('commands') for k in item):self.assertTrue(item.get('item_model'),(kind,key))
        cfg=yaml.safe_load((ROOT/'build/menus/DeluxeMenus/gui_menus/configuraciones.yml').read_text(encoding='utf8'))
        self.assertEqual(cfg['items']['volver']['slot'],40)  # quinta fila del menu ampliado
        for n,key in enumerate(('bajo','medio','alto')):
            active=cfg['items'][f'efectos_{key}_activo'];self.assertIn('[ACTIVO]',active['display_name'])
            self.assertEqual(active['view_requirement']['requirements']['activo']['output'],str(n))
        ocean=yaml.safe_load((ROOT/'build/menus/DeluxeMenus/gui_menus/oceano_aviso.yml').read_text(encoding='utf8'))
        self.assertEqual(ocean['items']['volver']['click_commands'],['[close]'])
        self.assertIn('[player] oceano entrar<delay=3>',ocean['items']['entrar']['click_commands'])
        jobs=yaml.safe_load((ROOT/'build/menus/DeluxeMenus/gui_menus/oficios.yml').read_text(encoding='utf8'))
        self.assertNotEqual(jobs['items']['ayuda']['slot'],jobs['items']['talador_leggings']['slot'])

    def test_skript_navigation_models(self):
        for rel in ('services/astral_servicios.sk','duelos/astral_duelos.sk'):
            text=(ROOT/'build'/rel).read_text(encoding='utf8')
            self.assertIn('astral:menu/icon_back',text)
            self.assertIn('astral:menu/icon_close',text)

    def test_final_art_crops_and_navigation_source_png(self):
        from ventanas_1611 import SHEETS,BUTTONS
        for keys in SHEETS.values():
            for key in keys:
                im=Image.open(BUTTONS/f'boton_{key}.png').convert('RGBA')
                self.assertEqual(im.size,(32,32));self.assertGreater(len(set(im.getdata())),50)
                self.assertFalse(any(r>250 and g<5 and b>250 and a>0 for r,g,b,a in im.getdata()))
        from navegacion_provisoria import ROOT as navroot,icon
        for family in ('cosmeticos','mascotas'):
            for key in ('gacha','back','close','info'):
                im=icon(family,key);self.assertEqual(im.size,(18,18));self.assertTrue((navroot/f'{family}_nav_{key}.png').exists())
                self.assertGreater(len(set(im.getdata())),5)

if __name__=='__main__':unittest.main()
