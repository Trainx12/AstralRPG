"""Pruebas de aislamiento y conservacion, sin necesitar arte privado."""
import json
import unittest
from pathlib import Path
from crop_kettle import adapt_resource, effective, encoded, merge_pack, patch_datapack, recipe_key
from crop_kettle import ROOT, privado, read_zip, sha


class CropKettleTests(unittest.TestCase):
    def test_pause_and_quick_actions_remove_cnk_and_optional_smithed_after_overlays(self):
        for tag in ('pause_screen_additions', 'quick_actions'):
            name = f'data/minecraft/tags/dialog/{tag}.json'
            raw = {'pack.mcmeta': encoded({'overlays': {'entries': [
                {'directory': 'current', 'min_format': [101, 1], 'max_format': [101, 1]}]}}),
                name: encoded({'values': ['cnk:main']}),
                'current/' + name: encoded({'replace': True, 'values': [
                    'cnk:main', {'id': 'smithed:main', 'required': False}, 'astral:guia']})}
            patched, _ = patch_datapack(raw)
            self.assertEqual(json.loads(patched[name]), {'values': ['astral:guia']})
            self.assertIn(b'cnk:main', raw[name])

    def test_final_datapacks_have_only_astral_pause_and_quick_actions(self):
        cnk = privado() / 'build/entregas/crop-kettle/CropAndKettle-Astral.zip'
        if not cnk.exists(): self.skipTest('Sin datapack privado')
        for tag in ('pause_screen_additions', 'quick_actions'):
            values = set()
            for pack in (cnk, ROOT / 'build/AstralRPG-Items.zip'):
                files = effective(read_zip(pack))
                obj = json.loads(files.get(f'data/minecraft/tags/dialog/{tag}.json', b'{}'))
                self.assertFalse(obj.get('replace', False))
                values.update(v['id'] if isinstance(v, dict) else v for v in obj.get('values', []))
            self.assertEqual(values, {'astral:guia'})

    def test_pan_de_cocina_conserva_material_y_se_distingue_para_ventas(self):
        name = 'data/cnk/loot_table/food/bread.json'
        recipe = {'pools': [{'rolls': 1, 'entries': [{'type': 'minecraft:item', 'name': 'minecraft:bread'}]}]}
        raw = {'pack.mcmeta': encoded({}), name: encoded(recipe)}
        patched, changed = patch_datapack(raw)
        result = json.loads(patched[name])
        self.assertEqual(result['pools'], recipe['pools'])
        self.assertEqual(result['functions'][0]['tag'], {'astral_cnk': {'cocina': True}})
        self.assertEqual(json.loads(raw[name]), recipe)
        self.assertIn(name, changed)

    def test_overlay_101_applied_in_order(self):
        files = {'pack.mcmeta': encoded({'overlays': {'entries': [
            {'directory': 'old', 'min_format': [94, 1], 'max_format': [94, 1]},
            {'directory': 'current', 'min_format': [94, 1], 'max_format': [101, 1]}]}}),
                 'data/cnk/a': b'base', 'old/data/cnk/a': b'wrong', 'current/data/cnk/a': b'right'}
        self.assertEqual(effective(files), {'data/cnk/a': b'right'})

    def test_survival_preserves_previous_conditions(self):
        advancement = {'criteria': {'place': {'trigger': 'minecraft:placed_block', 'conditions': {
            'player': {'flags': {'is_sneaking': True}}, 'location': []}}}, 'rewards': {'function': 'cnk:place'}}
        raw = {'pack.mcmeta': encoded({}), 'data/cnk/advancement/place.json': encoded(advancement),
               'data/cnk/function/tick.mcfunction': b'execute as @a[tag=foo] run say x\nexecute as @a run say y\n'}
        patched, _ = patch_datapack(raw)
        result = json.loads(patched['data/cnk/advancement/place.json'])
        self.assertEqual(result['criteria']['place']['conditions']['player'][0]['predicate'], {'flags': {'is_sneaking': True}})
        self.assertEqual(result['rewards'], advancement['rewards'])
        self.assertIn(b'@a[predicate=astral_cnk:survival,tag=foo]', patched['data/cnk/function/tick.mcfunction'])
        self.assertIn(b'@a[predicate=astral_cnk:survival]', patched['data/cnk/function/tick.mcfunction'])
        self.assertNotIn(b'astral_cnk', raw['data/cnk/function/tick.mcfunction'])

    def test_merge_keeps_astral_and_joins_atlas(self):
        atlas = 'assets/minecraft/atlases/blocks.json'
        a = {'source': 'astral', 'prefix': 'block/', 'type': 'directory'}
        b = {'source': 'cnk', 'prefix': 'entity/', 'type': 'directory'}
        base = {atlas: encoded({'sources': [a]}), 'assets/astral/items/x.json': b'ours', 'pack.mcmeta': b'ours'}
        extra = {atlas: encoded({'sources': [a, b]}), 'assets/astral/items/x.json': b'theirs',
                 'pack.mcmeta': b'theirs', 'assets/cnk/new': b'new'}
        merged, _ = merge_pack(base, extra)
        self.assertEqual(merged['pack.mcmeta'], b'ours')
        self.assertEqual(merged['assets/astral/items/x.json'], b'ours')
        self.assertEqual(json.loads(merged[atlas])['sources'], [a, b])
        self.assertEqual(base[atlas], encoded({'sources': [a]}))

    def test_entity_alias_has_png_animation_and_resolved_model(self):
        model = 'assets/cnk/models/entity/test.json'
        raw = {model: encoded({'textures': {'body': 'cnk:entity/test'}}),
               'assets/cnk/textures/cnk_entity/test.png': b'pixels',
               'assets/cnk/textures/cnk_entity/test.png.mcmeta': b'animation'}
        adapted, _ = adapt_resource(raw)
        self.assertEqual(adapted['assets/cnk/textures/item/entity/test.png'], b'pixels')
        self.assertEqual(adapted['assets/cnk/textures/item/entity/test.png.mcmeta'], b'animation')
        self.assertEqual(json.loads(adapted[model])['textures']['body'], 'cnk:item/entity/test')
        self.assertNotIn('assets/cnk/textures/item/entity/test.png', raw)

    def test_unresolved_texture_stops_build(self):
        with self.assertRaises(ValueError):
            adapt_resource({'assets/cnk/models/x.json': encoded({'textures': {'x': 'cnk:missing/x'}})})

    def test_shaped_pattern_compares_mirror_and_symbols(self):
        a = {'type': 'minecraft:crafting_shaped', 'pattern': ['AB'], 'key': {'A': 'stone', 'B': 'stick'}}
        b = {'type': 'minecraft:crafting_shaped', 'pattern': ['   ', ' XY'], 'key': {'X': 'stick', 'Y': 'stone'}}
        self.assertEqual(recipe_key(a), recipe_key(b))

    def test_private_output_preserves_all_prior_assets(self):
        folder = privado() / 'build/entregas/crop-kettle'
        if not (folder / 'audit.json').exists():
            self.skipTest('Sin entrega privada CNK')
        report = json.loads((folder / 'audit.json').read_text('utf8'))
        base_path = Path(report['base'])
        if not base_path.is_absolute(): base_path = ROOT / base_path
        self.assertEqual(sha(base_path), report['base_sha1'])
        base, final = read_zip(base_path), read_zip(folder / 'AstralRPG-Textures.zip')
        changed = [name for name, data in base.items() if final.get(name) != data]
        self.assertEqual(changed, ['assets/minecraft/atlases/blocks.json'])
        for name, digest in report['original_sha1'].items():
            self.assertEqual(sha(ROOT / '.local/terceros/crop-kettle' / name), digest)


if __name__ == '__main__':
    unittest.main()
