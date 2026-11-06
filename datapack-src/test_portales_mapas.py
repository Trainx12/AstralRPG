"""Regresiones de los formatos usados al copiar las construcciones privadas."""
from pathlib import Path
import gzip
from tempfile import TemporaryDirectory
import unittest

import numpy as np
import yaml

from mapas import block, chunk_records, nbt_payload, nbt_string
from portales_mapas import (canonical_air, load_schematic, pack_padded, rotate_half,
                            schematic, unpack_continuous, unpack_padded, write_world)
from portales import menu_data, npc


class PortalMapFormats(unittest.TestCase):
    def test_sponge_v3_and_modern_chunk_version(self):
        root = {'Schematic': (10, {
            'Version': (3, 3), 'DataVersion': (3, 4790),
            'Width': (2, 2), 'Height': (2, 1), 'Length': (2, 1),
            'Blocks': (10, {'Palette': (10, {'minecraft:air': (3, 0),
                                           'minecraft:end_portal': (3, 1)}),
                           'Data': (7, bytes([1, 0]))})})}
        with TemporaryDirectory(dir=Path(__file__).resolve().parent.parent/'.local') as directory:
            path = Path(directory)/'end.schem'
            path.write_bytes(gzip.compress(b'\x0a'+nbt_string('')+nbt_payload((10, root))))
            palette, blocks = load_schematic(path)
            self.assertEqual(palette[blocks[0, 0, 0]], 'minecraft:end_portal')
            self.assertEqual(palette[blocks[0, 0, 1]], 'minecraft:air')
            write_world(Path(directory)/'region', palette, blocks, (0, 64, 0), data_version=4790)
            chunk = next(chunk_records((Path(directory)/'region/r.0.0.mca').read_bytes()))
            self.assertEqual(chunk['DataVersion'], 4790)
            self.assertEqual(block(chunk, 0, 64, 0), 'minecraft:end_portal')

    def test_generated_npc_and_menu_are_valid_configs(self):
        guardian = yaml.safe_load(npc())['astral_npc_portales']
        self.assertIn('cancelevent @self ~onInteract', guardian['Skills'])
        self.assertIn('command{c="dm open portales <trigger.name>"} @self ~onInteract', guardian['Skills'])
        menu = menu_data()
        self.assertEqual(menu['size'], 54)
        for key in ('nether', 'end'):
            self.assertLess(menu['items'][key]['slot'], menu['size'])

    def test_continuous_litematic_values_cross_word_boundaries(self):
        values = [(i * 31) % 452 for i in range(257)]
        bits = 9
        stream = sum(value << (i * bits) for i, value in enumerate(values))
        words = [(stream >> offset) & ((1 << 64) - 1)
                 for offset in range(0, len(values) * bits, 64)]
        self.assertEqual(unpack_continuous(words, len(values), bits).tolist(), values)

    def test_chunk_words_preserve_padding_and_negative_longs(self):
        values = np.asarray([(i * 37) % 512 for i in range(4096)], dtype=np.uint16)
        words = pack_padded(values, 9)
        np.testing.assert_array_equal(unpack_padded(words, len(values), 9), values)
        bytes_values = np.asarray([(i * 37) % 256 for i in range(4096)], dtype=np.uint16)
        words = pack_padded(bytes_values, 8)
        self.assertTrue(any(word < 0 for word in words))
        np.testing.assert_array_equal(unpack_padded(words, len(bytes_values), 8), bytes_values)

    def test_schematic_round_trip_and_nonzero_air_palette(self):
        palette, values = canonical_air(['minecraft:stone', 'minecraft:air'],
                                        np.array([0, 1], dtype=np.uint16))
        self.assertEqual(values.tolist(), [1, 0])
        palette = ['minecraft:air'] + [f'minecraft:test_{i}' for i in range(140)]
        source = np.arange(141, dtype=np.uint16).reshape(3, 47, 1)
        with TemporaryDirectory(dir=Path(__file__).resolve().parent.parent/'.local') as directory:
            path = Path(directory)/'roundtrip.schem'
            schematic(path, palette, source)
            result_palette, result = load_schematic(path)
            self.assertEqual(result_palette, palette)
            np.testing.assert_array_equal(result, source)

    def test_regions_preserve_blocks_across_negative_chunk_edges(self):
        palette = ['minecraft:air', 'minecraft:stone', 'minecraft:purple_stained_glass']
        source = np.zeros((20, 20, 20), dtype=np.uint16)
        source[0, 0, 0] = 1
        source[19, 19, 19] = 2
        source[10, :, :] = 1
        origin = (-17, 250, -17)
        with TemporaryDirectory(dir=Path(__file__).resolve().parent.parent/'.local') as directory:
            write_world(Path(directory), palette, source, origin)
            chunks = {}
            for path in Path(directory).glob('*.mca'):
                chunks.update({(c['xPos'], c['zPos']): c for c in chunk_records(path.read_bytes())})
            for x, y, z, name in [(-17, 250, -17, 'minecraft:stone'),
                                   (2, 269, 2, 'minecraft:purple_stained_glass'),
                                   (-1, 260, -1, 'minecraft:stone')]:
                self.assertEqual(block(chunks[x//16, z//16], x%16, y, z%16), name)

    def test_rotation_preserves_directional_block_properties(self):
        original = 'minecraft:oak_stairs[facing=north,half=bottom,shape=inner_left,waterlogged=false]'
        rotated = rotate_half(original)
        self.assertIn('facing=south', rotated)
        self.assertIn('shape=inner_left', rotated)
        self.assertEqual(rotate_half(rotated), original)
        self.assertEqual(rotate_half('minecraft:oak_sign[rotation=3,waterlogged=false]'),
                         'minecraft:oak_sign[rotation=11,waterlogged=false]')


if __name__ == '__main__':
    unittest.main()
