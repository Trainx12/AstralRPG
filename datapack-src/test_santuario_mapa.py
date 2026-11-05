from pathlib import Path
from tempfile import TemporaryDirectory
import gzip
import unittest

from mapas import NBT
from santuario_mapa import legacy_chunks, write_nbt
from mobs.mazmorras_data import catalog
from mobs.mazmorra import skill_yml
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
        self.assertEqual(dungeon['world'], 'santuario_freemap9')
        room = dungeon['rooms'][0]
        self.assertEqual(room['llegada'], (33.5, 103, -40.5))
        self.assertGreaterEqual(room['r'], 21)
        self.assertEqual(len(room['oleadas']), 5)
        skills = yaml.safe_load(skill_yml(dungeon))
        summons = [line for value in skills.values() for line in value['Skills']
                   if 'summon{type=astral_santuario_' in line]
        self.assertTrue(any('cangrejo_eco' in line for line in summons))
        self.assertTrue(any('golem_forja_eco' in line for line in summons))


if __name__ == '__main__':
    unittest.main()
