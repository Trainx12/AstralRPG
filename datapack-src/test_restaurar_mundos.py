"""La reparacion del generador no debe alterar metadatos ajenos."""
from copy import deepcopy
import unittest
from restaurar_mundos import void_generator


class VoidGeneratorTests(unittest.TestCase):
    def test_changes_only_overworld_generator_and_structures(self):
        original = (10, {'DataVersion': (3, 4790), 'data': (10, {
            'seed': (4, -123), 'generate_structures': (1, 1),
            'bonus_chest': (1, 0), 'dimensions': (10, {
                'minecraft:overworld': (10, {'type': (8, 'minecraft:overworld'),
                    'generator': (10, {'type': (8, 'minecraft:noise')})}),
                'minecraft:the_nether': (10, {'sentinel': (8, 'keep')})})})})
        before = deepcopy(original)
        result = void_generator(original)
        self.assertEqual(original, before)
        data = result[1]['data'][1]
        self.assertEqual(data['seed'], (4, -123))
        self.assertEqual(data['dimensions'][1]['minecraft:the_nether'],
                         before[1]['data'][1]['dimensions'][1]['minecraft:the_nether'])
        generator = data['dimensions'][1]['minecraft:overworld'][1]['generator'][1]
        self.assertEqual(generator['type'], (8, 'minecraft:flat'))
        self.assertEqual(generator['settings'][1]['layers'][1][0][1]['block'],
                         (8, 'minecraft:air'))
        self.assertEqual(data['generate_structures'], (1, 0))


if __name__ == '__main__':
    unittest.main()
