"""Contratos del prototipo contra los datos y artefactos realmente generados."""
import json
import unittest
import zipfile
from pathlib import Path
from guia_atlas import ROOT, bestiary
from mobs.mythic import MOBS, ELITES, ANCESTRALES
from tanda_xp import XP


class AtlasTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with zipfile.ZipFile(ROOT / 'build/AstralRPG-Items.zip') as z:
            cls.files = {n: z.read(n) for n in z.namelist()}
        cls.pages = {n: json.loads(b) for n, b in cls.files.items() if '/dialog/atlas/' in n}

    def test_production_entrypoints(self):
        for n in ('pause_screen_additions', 'quick_actions'):
            self.assertEqual(json.loads(self.files[f'data/minecraft/tags/dialog/{n}.json'])['values'], ['astral:guia_esc'])
        self.assertNotIn('atlas/', self.files['data/astral/dialog/guia.json'].decode())

    def test_new_trigger_is_independent(self):
        self.assertIn(b'astral.guia2 trigger', self.files['data/astral/function/atlas/load.mcfunction'])
        for tag in ('load', 'tick'):
            values = json.loads(self.files[f'data/minecraft/tags/function/{tag}.json'])['values']
            self.assertIn('astral:' + tag, values)
            self.assertIn('astral:atlas/' + tag, values)

    def test_all_dialog_links_exist(self):
        def walk(obj):
            if isinstance(obj, dict):
                if obj.get('type') == 'show_dialog':
                    target = obj['dialog'].replace(':', '/dialog/', 1)
                    self.assertIn('data/' + target + '.json', self.files)
                for v in obj.values():
                    walk(v)
            elif isinstance(obj, list):
                for v in obj:
                    walk(v)
        for obj in self.pages.values():
            walk(obj)

    def test_multi_action_never_empty(self):
        # Un multi_action sin botones rompe la carga de TODOS los dialogos en Paper.
        for name, page in self.pages.items():
            if page['type'] == 'minecraft:multi_action':
                self.assertTrue(page['actions'], name)

    def test_full_index_two_columns(self):
        index = self.pages['data/astral/dialog/atlas/indice.json']
        original = json.loads(self.files['data/astral/dialog/guia.json'])
        self.assertEqual(index['columns'], 2)
        self.assertGreaterEqual(len(index['actions']), len(original['actions']) + 1)

    def test_all_berserker_tiers(self):
        for tier in range(1, 11):
            page = self.pages[f'data/astral/dialog/atlas/catalogo/armadura_{tier}/1.json']
            models = [b['item']['components']['minecraft:item_model'] for b in page['body'] if b['type'] == 'minecraft:item']
            self.assertEqual(len(models), 4)
            self.assertTrue(all(m.startswith(f'astral:berserker_{tier}_') for m in models))

    def test_recipe_uses_real_components_and_forge(self):
        recipes = [p for n, p in self.pages.items() if '/atlas/receta/' in n]
        self.assertEqual(len(recipes), 70)
        for page in recipes:
            self.assertEqual(page['after_action'], 'close')
            command = page['actions'][0]['action']['command']
            rid = command.split()[-1]
            self.assertIn(f'data/astral/function/forge/r/{rid}.mcfunction', self.files)
            item = next(b['item'] for b in page['body'] if b['type'] == 'minecraft:item')
            self.assertIn('minecraft:custom_data', item['components'])
            self.assertIn('Cantidades requeridas', json.dumps(page))

    def test_consumables_use_real_items(self):
        page = self.pages['data/astral/dialog/atlas/seccion/consumibles.json']
        models = [b['item']['components']['minecraft:item_model'] for b in page['body'] if b['type'] == 'minecraft:item']
        self.assertEqual(set(models), {'astral:' + i for i in XP} | {'astral:manzana_esmeralda'})
        for amount in XP.values():
            self.assertIn(f'{amount:,}', json.dumps(page))

    def test_bestiary_tracks_all_generated_variants(self):
        rows = bestiary()
        ids = {r['id'] for r in rows}
        self.assertTrue(set(MOBS) <= ids)
        self.assertTrue({m + '_elite' for m in ELITES} <= ids)
        self.assertTrue({m + '_ancestral' for m in ANCESTRALES} <= ids)
        self.assertTrue(any(i.startswith('vanilla_') for i in ids))
        self.assertEqual(len(ids), len(rows))

    def test_current_mount_behaviour(self):
        rows = {r['id']: r for r in bestiary()}
        self.assertEqual(rows['astral_mapache']['kind'], 'hostil')
        self.assertEqual(rows['astral_pinguino']['kind'], 'hostil')
        self.assertEqual(rows['astral_lagarto']['kind'], 'montura')
        page = self.pages['data/astral/dialog/atlas/criatura/astral_lagarto.json']
        self.assertIn('WASD bajo agua', json.dumps(page))

    def test_drops_and_base_stats_match_source(self):
        rows = {r['id']: r for r in bestiary()}
        for mid, source in MOBS.items():
            self.assertEqual(rows[mid]['hp'], source['hp'])
            self.assertEqual(rows[mid]['astral'], source.get('astral', []))
            self.assertEqual(rows[mid]['spawn'], source.get('spawn', {}))


if __name__ == '__main__':
    unittest.main()
