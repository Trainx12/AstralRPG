"""Paridad de cantidades/ingredientes, salida exacta y exclusiones de la mesa."""
import json
from pathlib import Path
import re
import unittest
import zipfile
from mesa import fits

ROOT = Path(__file__).resolve().parents[1]


class MesaTests(unittest.TestCase):
    def test_every_forge_recipe_is_exported_without_changing_cost(self):
        rows = json.loads((ROOT / 'build/runtime/mesa.json').read_text(encoding='utf8'))
        self.assertEqual(len({r['output'] for r in rows}), len(rows))
        with zipfile.ZipFile(ROOT / 'build/AstralRPG-Items.zip') as z:
            functions = [p for p in z.namelist() if re.fullmatch(r'data/astral/function/forge/r/\d+.mcfunction', p)]
            self.assertEqual(len(rows), len(functions))
            for i, row in enumerate(rows, 1):
                function = z.read(f'data/astral/function/forge/r/{i}.mcfunction').decode()
                self.assertEqual(function.count('loot give @s loot astral:item/' + row['output'] + '\n'), row['count'])
                for kind, ident, count in row['ingredients']:
                    if kind == 'c':
                        pred = f'*[minecraft:custom_data~{{astral:{{id:"{ident}"}}}}]'
                    elif ident == 'water_bottle':
                        pred = 'minecraft:potion[minecraft:potion_contents={potion:"minecraft:water"}]'
                    else:
                        pred = ident + '[!minecraft:custom_data]'
                    self.assertIn(f'clear @s {pred} {count}\n', function)
                self.assertEqual(row['table'], fits(row['ingredients']))
                components = json.loads(z.read(f'data/astral/loot_table/item/{row["output"]}.json'))['pools'][0]['entries'][0]['functions'][0]['components']
                text = '\n'.join(line.get('text', '') for line in components['minecraft:lore'])
                self.assertIn('mesa de crafteo o en la Forja' if row['table'] else 'solo en la Forja', text)
                dialog = z.read(f'data/astral/dialog/receta/{i}.json').decode()
                self.assertIn('Tambien en la mesa de crafteo' if row['table'] else 'Solo Forja:', dialog)
                for skill, level in row['requirements'].items():
                    self.assertRegex(components['minecraft:custom_data'], re.escape('"' + skill + '":' + str(level)))

    def test_grid_limits_count_units_not_distinct_types(self):
        self.assertTrue(fits([('c', 'material', 9)]))
        self.assertFalse(fits([('c', 'material', 10)]))
        self.assertFalse(fits([]))
        self.assertFalse(fits([('c', 'material', 8), ('v', 'minecraft:stick', 2)]))

    def test_packaged_catalog_matches_generated_source(self):
        with zipfile.ZipFile(ROOT / 'build/runtime/AstralDecor.jar') as z:
            self.assertEqual(z.read('mesa.json'), (ROOT / 'build/runtime/mesa.json').read_bytes())
            self.assertIn('version: 1.6.0', z.read('plugin.yml').decode())

    def test_quick_actions_preserves_existing_guide(self):
        with zipfile.ZipFile(ROOT / 'build/AstralRPG-Items.zip') as z:
            self.assertIn('astral:guia', json.loads(z.read('data/minecraft/tags/dialog/quick_actions.json'))['values'])
