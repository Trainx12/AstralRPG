from pathlib import Path
from tempfile import TemporaryDirectory
import gzip
import unittest

from mapas import NBT
from santuario_mapa import legacy_chunks, write_nbt
from mobs.mazmorras_data import catalog
from mobs.mazmorra import skill_yml
from santuario_azeroth import WORLD, BUKKIT_WORLD, ARRIVAL, BOSSES, CHEST, GUIDE, generate, commands
from escala import TIER_MAZMORRA, EXTRA_VIDA_MAZMORRA
from gameplay import DUNGEONS, RESCUE_HEIGHTS, patch_graves, script
from mobs.mascotas import MUNDOS_BONUS
import json
import yaml


class SantuarioMapTests(unittest.TestCase):
    def test_legacy_nibbles_logic_and_source_origin(self):
        with TemporaryDirectory(dir=Path(__file__).resolve().parent.parent/'.local') as name:
            root = Path(name)
            schematic = root/'scene.schematic'
            write_nbt(schematic, (10, {
                'Width': (2, 4), 'Length': (2, 1), 'Height': (2, 1),
                'WEOriginX': (3, -1), 'WEOriginY': (3, 70), 'WEOriginZ': (3, 0),
                'Blocks': (7, bytes([5, 137, 35, 52])),
                'Data': (7, bytes([2, 0, 7, 0])),
                'Entities': (9, [(10, {'id': (8, 'minecraft:creeper')})]),
                'TileEntities': (9, [(10, {'id': (8, 'minecraft:command_block'),
                    'Command': (8, 'say must_not_run'),
                    'x': (3, 1), 'y': (3, 0), 'z': (3, 0)})])}))
            self.assertEqual(legacy_chunks(schematic, root/'chunks')[0], (-1, 70, 0))
            chunk = NBT(gzip.decompress((root/'chunks/0.0.nbt').read_bytes())).root()['Level']
            self.assertEqual(chunk['Entities'], [])
            self.assertEqual(chunk['TileEntities'], [])
            section = chunk['Sections'][0]
            offset = 6*256
            self.assertEqual(section['Blocks'][offset:offset+3], bytes([98, 35, 98]))
            self.assertEqual(section['Data'][offset//2], 0x70)

    def test_new_map_arrival_activates_five_boss_waves(self):
        dungeon = next(d for d in catalog() if d['key'] == 'santuario')
        self.assertEqual(dungeon['world'], WORLD)
        room = dungeon['rooms'][0]
        self.assertEqual(room['llegada'], ARRIVAL)
        self.assertGreaterEqual(room['r'], 15)
        self.assertEqual(len(room['oleadas']), 6)
        skills = yaml.safe_load(skill_yml(dungeon))
        summons = [line for value in skills.values() for line in value['Skills']
                   if 'summon{type=astral_santuario_' in line and '_eco;' in line]
        self.assertTrue(any('coloso_musgoso_eco' in line for line in summons))
        self.assertTrue(any('golem_forja_eco' in line for line in summons))
        self.assertEqual(len(summons),5)  # la 6ta es un ZOMBIE vanilla provisorio
        self.assertTrue(any('summon{type=ZOMBIE;' in line for value in skills.values() for line in value['Skills']))
        for line,point in zip(summons,BOSSES[:5],strict=True):
            self.assertIn('onSurface=false',line)
            self.assertIn('x=%s;y=%s;z=%s' % point,line)
        self.assertEqual(room['final_npcs'],{'cofre':CHEST,'guia':GUIDE})
        self.assertEqual(sum((a-b)**2 for a,b in zip(CHEST,GUIDE)),4)

    def test_end_sky_without_end_generation_or_dragon(self):
        files={};generate(files)
        kind=json.loads(files['data/astral/dimension_type/santuario.json'])
        self.assertEqual(kind['skybox'],'end')
        self.assertNotIn('effects',kind)
        self.assertFalse(kind['has_ender_dragon_fight'])
        dim=json.loads(files[f'data/minecraft/dimension/{WORLD}.json'])
        self.assertEqual(dim['type'],'astral:santuario')
        self.assertEqual(dim['generator']['type'],'minecraft:flat')
        self.assertEqual(dim['generator']['settings']['layers'],[{'block':'minecraft:air','height':1}])
        self.assertNotIn('mv create', '\n'.join(l for l in commands().splitlines() if not l.startswith('#')))

    def test_fixed_tier_inventory_pets_and_void_rescue(self):
        self.assertEqual(TIER_MAZMORRA[WORLD],5)
        self.assertEqual(EXTRA_VIDA_MAZMORRA[WORLD],1.5)
        self.assertIn(WORLD,DUNGEONS)
        self.assertIn(WORLD,MUNDOS_BONUS)
        self.assertIn(BUKKIT_WORLD,MUNDOS_BONUS)
        self.assertIn(BUKKIT_WORLD,DUNGEONS)
        self.assertIn(WORLD,patch_graves({})['disabled-worlds'])
        self.assertIn(BUKKIT_WORLD,patch_graves({})['disabled-worlds'])
        self.assertEqual(RESCUE_HEIGHTS[WORLD],0)
        rescue=script().split('function astral_rescue(p: player):')[1].split('function ',1)[0]
        self.assertIn('at @s run minecraft:tp @s',rescue)  # en la misma copia
        self.assertIn(' '.join(map(str,ARRIVAL)),rescue)
        self.assertLess(rescue.index('santuario_azeroth'),rescue.index('spawn %name'))


if __name__ == '__main__':
    unittest.main()
