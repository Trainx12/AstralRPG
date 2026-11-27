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
        # 19/11: la guia ya no esta en el datapack; sus dialogos son la fuente de las ventanas de cofre.
        from guia_cofre import load
        cls.source = load()
        cls.pages = {f'data/astral/dialog/{k}.json': d for k, d in cls.source['dialogs'].items() if k.startswith('atlas/')}

    def test_production_entrypoints(self):
        for n in ('pause_screen_additions', 'quick_actions'):
            self.assertEqual(json.loads(self.files[f'data/minecraft/tags/dialog/{n}.json'])['values'], [])
        old = [n for n in self.files if n.startswith(('data/astral/dialog/guia', 'data/astral/dialog/receta/', 'data/astral/dialog/atlas/'))]
        self.assertEqual(old, [])

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
                    key = obj['dialog'].split(':', 1)[1]
                    self.assertTrue(key in self.source['dialogs'] or key == 'atlas/indice', key)
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
        original = self.source['dialogs']['guia'] if 'guia' in self.source['dialogs'] else None
        self.assertGreaterEqual(len(self.source['index']), 21)

    def test_indice_ampliado_y_fuente_preservada(self):
        from guia_ampliacion import extend_source, catalog
        raw = json.loads((ROOT / 'build/runtime/guia_fuente.json').read_text(encoding='utf8'))
        before = json.dumps(raw, sort_keys=True)
        data = extend_source(raw)
        self.assertEqual(before, json.dumps(raw, sort_keys=True))
        self.assertEqual(data, extend_source(data))
        entries = {e.get('dialog'): e['caption'] for e in data['index']}
        self.assertEqual(entries['atlas/seccion/cocina'], 'Comida')
        self.assertEqual(entries['atlas/seccion/crafteos'], 'Crafteos')
        self.assertEqual(entries['atlas/seccion/stellarity'], 'Stellarity (El End)')
        self.assertEqual(catalog()['version'], '5.4.2')

    def test_catalogo_cubre_las_recetas_del_original_local(self):
        import sys
        sys.path.insert(0, str(ROOT / 'tools'))
        from inventariar_stellarity import inventory
        from guia_ampliacion import catalog
        datapack = ROOT / '.local/dp-server/Stellarity-5.4.2.zip'
        resource = ROOT / 'datapack-src/pack-source/terceros/Stellarity-6.0.1-RP.zip'
        if not datapack.exists() or not resource.exists():
            self.skipTest('Originales privados no disponibles')
        original, _ = inventory(datapack, resource)
        self.assertEqual(catalog()['recipes'], original['recipes'])
        self.assertEqual(set(catalog()['items']), set(original['items']))
        self.assertEqual(len({r['id'] for r in original['recipes']}), len(original['recipes']))
        self.assertTrue(any(r.get('warning') for r in original['recipes']))

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
