"""Contratos de entrega: arte final, modelos, migracion y conservacion privada."""
import io
import json
import unittest
import zipfile
from PIL import Image
from arte_1611 import ROOT, ART, ITEMS, BUTTONS, PACK
from deploy_arte_1611 import read, NAME
from terceros import privado
from pack_audit import audit


class ArteTests(unittest.TestCase):
    def test_item_art_and_vanilla_bottle_exact(self):
        with zipfile.ZipFile(ROOT/'build/AstralRPG-Textures.zip') as z:
            for iid in ITEMS:
                item=json.loads(z.read(f'assets/astral/items/{iid}.json'))['model']
                model=json.loads(z.read('assets/astral/models/'+item['model'].split(':')[1]+'.json'))
                tex=model['textures']['layer0'].split(':')[1]
                blob=z.read(f'assets/astral/textures/{tex}.png')
                self.assertEqual(blob,(ART/f'{iid}.png').read_bytes())
                self.assertGreater(len(Image.open(io.BytesIO(blob)).getcolors(4096)),10)
            self.assertEqual(z.read('assets/minecraft/textures/item/experience_bottle.png'),(ART/'experience_bottle.png').read_bytes())
            with Image.open(ART/'experience_bottle.png') as image:self.assertEqual(image.size,(24,24))

    def test_datapack_names_and_distinct_hooks(self):
        with zipfile.ZipFile(ROOT/'build/AstralRPG-Items.zip') as z:
            def comp(iid):return json.loads(z.read(f'data/astral/loot_table/item/{iid}.json'))['pools'][0]['entries'][0]['functions'][0]['components']
            self.assertIn('Manzana de la Suerte',str(comp('manzana_esmeralda')['minecraft:item_name']))
            self.assertEqual(comp('gancho')['minecraft:item_model'],'astral:saltador')
            self.assertEqual(comp('gancho_realista')['minecraft:item_model'],'astral:gancho')
            for iid in ITEMS[5:10]:self.assertEqual(comp(iid)['minecraft:item_model'],'astral:'+iid)
            for name in z.namelist():
                if name.endswith(('.json','.mcfunction')):self.assertNotIn('Manzana de Esmeralda',z.read(name).decode())
        for folder in ('build/menus','build/lobby','build/mythicmobs'):
            for path in (ROOT/folder).rglob('*.yml'):self.assertNotIn('Manzana de Esmeralda',path.read_text(encoding='utf8'))

    def test_buttons_final_no_magenta(self):
        paths=[PACK/f'provisorias/boton_{key}.png' for key in BUTTONS]
        paths += [PACK/f'provisorias/navegacion/{family}_nav_{key}.png'
                  for family in ('mascotas','cosmeticos') for key in ('back','close','info','gacha')]
        paths += [PACK/'provisorias/navegacion/mascotas_nav_next.png']
        for path in paths:
            im=Image.open(path).convert('RGBA')
            self.assertEqual(im.size,(18,18) if 'navegacion' in path.parts else (32,32))
            self.assertFalse(any(r>250 and g<5 and b>250 and a for r,g,b,a in im.get_flattened_data()),path.name)
            self.assertGreater(len(im.getcolors(4096)),10)
        with zipfile.ZipFile(ROOT/'build/AstralRPG-Textures.zip') as z:
            for path in paths:
                if 'navegacion' in path.parts:
                    family,kind=path.stem.split('_nav_')
                    resource=f'assets/astral/textures/item/{family}/nav_{kind}.png'
                else:resource=f'assets/astral/textures/item/provisorias/{path.name}'
                self.assertEqual(z.read(resource),path.read_bytes())

    def test_final_delta_and_private_barrel(self):
        out=privado()/'build/entregas'/NAME
        report=json.loads((out/'delta.json').read_text())
        old=read(ROOT/report['base']);new=read(out/'AstralRPG-Textures.zip')
        for name,blob in old.items():
            if name not in report['changed']:self.assertEqual(blob,new[name],name)
        barrel=json.loads(new['assets/astral/items/barril_xp.json'])['model']
        self.assertEqual(barrel['property'],'minecraft:display_context')
        self.assertEqual(barrel['cases'][0]['when'],'gui')
        self.assertEqual(barrel['fallback'],json.loads(old['assets/astral/items/barril_xp.json'])['model'])
        self.assertFalse(any('infinita_alto_' in p for p in report['changed']))
        for path in (ROOT/'build/AstralRPG-Textures.zip',out/'AstralRPG-Textures.zip'):self.assertGreater(audit(path),0)
