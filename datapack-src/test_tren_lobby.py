"""Conversion privada, conservacion de la cadena anterior y configuracion de plazas."""
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
import zipfile

from tren_lobby import BASE, DELIVERY, configuration, prepare_private


class TrainBuildTests(unittest.TestCase):
    def test_three_seats_and_no_locomotive_seat(self):
        carts=configuration()['carts']
        self.assertEqual(len(carts),3)
        self.assertEqual([sum(a['type']=='SEAT' for a in c['model']['attachments']) for c in carts],[0,2,2])
        self.assertFalse(configuration()['allowMobEnter'])
        self.assertFalse(configuration()['playerTakeable'])

    def test_locomotive_uses_tall_model_and_wagons_the_low_one(self):
        # En el pack original basic_coaster_cart es la locomotora alta.
        models=[c['astral-model'] for c in configuration()['carts']]
        self.assertEqual(models,['cart','head','head'])

    def test_trip_stops_two_blocks_before_the_wall_and_returns_from_the_other(self):
        from tren_lobby import trip, STATION, WALL_EXIT, LOCO, FIRST_RAIL_ENTRY
        t=trip(); home=STATION[2]+.5
        self.assertAlmostEqual(home+t['teleport']+LOCO/2,WALL_EXIT-2,places=2)
        self.assertGreater(t['teleport'],t['parada'])
        self.assertLess(t['salida'],0)
        self.assertAlmostEqual(home+t['salida']-(LOCO/2+3.6275125),FIRST_RAIL_ENTRY,places=2)

    def source(self,path):
        inner=io.BytesIO()
        with zipfile.ZipFile(inner,'w') as z:
            prefix='EC - Steam Roller Coaster/'
            for kind in ('head','cart'):
                z.writestr(prefix+f'assets/ec_roller_coaster/models/basic_coaster_{kind}.json',
                    json.dumps({'textures':{'0':f'ec_roller_coaster:basic_coaster_{kind}'},'display':{},'elements':[]}))
                z.writestr(prefix+f'assets/ec_roller_coaster/textures/basic_coaster_{kind}.png',b'synthetic-test-texture')
            z.writestr(prefix+'assets/minecraft/models/item/paper.json','{"overrides":[]}')
            z.writestr(prefix+'pack.mcmeta','{"pack":{"pack_format":9}}')
        with zipfile.ZipFile(path,'w') as z:z.writestr('EC - Steam Roller Coaster.zip',inner.getvalue())

    def test_private_pack_preserves_every_prior_entry_and_has_modern_models(self):
        with TemporaryDirectory() as temp:
            root=Path(temp);base=root/BASE;base.parent.mkdir(parents=True)
            with zipfile.ZipFile(base,'w') as z:
                z.writestr('pack.mcmeta','{"pack":{"min_format":84,"max_format":84}}')
                z.writestr('assets/astral/keep.txt',b'previous-task-unchanged')
            source=root/'source.zip';self.source(source)
            with patch('tren_lobby.privado',return_value=root):
                result=prepare_private(source)
                final=root/DELIVERY/'AstralRPG-Textures.zip';first=final.read_bytes()
                second=prepare_private(source)
            self.assertEqual(first,final.read_bytes())
            self.assertEqual(result,second)
            self.assertEqual(result['preserved_entries'],2)
            self.assertEqual(result['removed'],[])
            with zipfile.ZipFile(final) as z,zipfile.ZipFile(base) as old:
                for name in old.namelist():self.assertEqual(z.read(name),old.read(name))
                self.assertNotIn('assets/minecraft/models/item/paper.json',z.namelist())
                for kind in ('head','cart'):
                    d=json.loads(z.read(f'assets/astral/items/tren_{kind}.json'))
                    self.assertEqual(d['model']['type'],'minecraft:model')
                    model=json.loads(z.read(f'assets/ec_roller_coaster/models/basic_coaster_{kind}.json'))
                    self.assertTrue(model['textures']['0'].startswith('ec_roller_coaster:item/'))

    def test_missing_previous_final_does_not_create_outputs(self):
        with TemporaryDirectory() as temp,patch('tren_lobby.privado',return_value=Path(temp)):
            with self.assertRaises(FileNotFoundError):prepare_private(Path(temp)/'source.zip')
            self.assertFalse((Path(temp)/DELIVERY).exists())

    def test_conversion_cannot_overwrite_previous_assets(self):
        with TemporaryDirectory() as temp:
            root=Path(temp);base=root/BASE;base.parent.mkdir(parents=True)
            with zipfile.ZipFile(base,'w') as z:z.writestr('assets/astral/items/tren_head.json','previous')
            source=root/'source.zip';self.source(source)
            with patch('tren_lobby.privado',return_value=root),self.assertRaisesRegex(ValueError,'pisaria'):
                prepare_private(source)


if __name__=='__main__':unittest.main()
