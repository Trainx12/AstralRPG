"""Regresiones de cabeza/torso y escala inicial de ancestrales del Survival."""
import json
import re
import unittest
from pathlib import Path

import yaml
from mobs.mythic import ANCESTRALES, MOBS, escala_mundo, metaskills
from mobs.tamanos import skills as size_skills, rotate

ROOT = Path(__file__).resolve().parents[1]


class AncestralModeloTests(unittest.TestCase):
    def test_escala_antes_del_modelo_en_todos_los_ancestrales(self):
        generated = yaml.safe_load(metaskills())
        installed = yaml.safe_load((ROOT / 'build/mythicmobs/skills/astral.yml').read_text('utf-8'))
        mobs = yaml.safe_load((ROOT / 'build/mythicmobs/mobs/astral.yml').read_text('utf-8'))
        for mid in ANCESTRALES:
            with self.subTest(mid=mid):
                key = f'AST_MODEL_{mid}_ancestral_mundo'
                steps = generated[key]['Skills']
                self.assertEqual(steps, installed[key]['Skills'])
                model = f'model{{m={mid};s={escala_mundo(mid)}}} @self'
                attrs = size_skills(mid, escala_mundo(mid), MOBS[mid]['type'])
                pos = steps.index(model)
                self.assertEqual(steps[pos-len(attrs):pos], attrs)
                self.assertFalse(any('minecraft:scale ' in s for s in steps[pos+1:]))
                self.assertEqual(steps[pos+1], 'delay 2')
                self.assertTrue(steps[pos+2].startswith('tint{'))
                for event in ('onSpawn', 'onLoad'):
                    self.assertIn(f'skill{{s={key}}} @self ~{event}', mobs[mid+'_ancestral']['Skills'])

    def test_otras_skills_conservan_su_orden(self):
        for key, definition in yaml.safe_load(metaskills()).items():
            if not key.startswith('AST_MODEL_') or key.endswith('_ancestral_mundo'):
                continue
            steps = definition['Skills']
            for pos, step in enumerate(steps):
                match = re.fullmatch(r'model\{m=([^;}]+)(?:;s=([^}]+))?\} @self', step)
                if match and MOBS[match[1]]['kind'] != 'montura':
                    attrs = size_skills(match[1], float(match[2] or 1), MOBS[match[1]]['type'])
                    self.assertEqual(steps[pos+1:pos+1+len(attrs)], attrs)

    def test_cuello_unido_en_modelo_y_animaciones(self):
        data = json.loads((ROOT / 'build/models/astral_momia.bbmodel').read_text('utf-8'))
        groups = {g['name']: g for g in data['groups']}
        parents = {}
        def visit(node, parent=None):
            if isinstance(node, dict):
                parents[node['uuid']] = parent
                for child in node.get('children', []):
                    visit(child, node['uuid'])
        for root in data['outliner']:
            visit(root)
        head, body = groups['head'], groups['body']
        self.assertEqual(parents[head['uuid']], body['uuid'])
        neck = head['origin']
        self.assertEqual(neck, [0, 24, 0])
        # El pivote del cuello pertenece al torso: todas sus transformaciones
        # (incluida traslacion) se heredan. Rotar head no desplaza ese pivote.
        for animation in data['animations']:
            animator = animation.get('animators', {}).get(head['uuid'], {})
            for frame in animator.get('keyframes', []):
                self.assertNotEqual(frame['channel'], 'position', animation['name'])
                if frame['channel'] == 'rotation':
                    point = frame['data_points'][0]
                    # Molang puede expresar el angulo con una senoide. El pivote
                    # es invariante para cualquier angulo, incluido este muestreo.
                    angles = [float(point[axis]) if re.fullmatch(r'-?\d+(?:\.\d+)?', str(point[axis])) else 45
                              for axis in ('x', 'y', 'z')]
                    result = rotate(neck, neck, angles)
                    s = escala_mundo('astral_momia')
                    self.assertEqual(tuple(v*s for v in result), tuple(v*s for v in neck))
        cubes = data['elements']
        self.assertTrue(any(e['from'][1] == 12 and e['to'][1] == 24
                            and e['from'][0] < 0 < e['to'][0]
                            and e['from'][2] < 0 < e['to'][2] for e in cubes))
        self.assertTrue(any(e['from'][1] == 24 and e['to'][1] == 32 for e in cubes))


if __name__ == '__main__':
    unittest.main()
