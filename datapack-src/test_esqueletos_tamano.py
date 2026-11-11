"""Regresion contra la formula historica real, incluida la variante montada."""
import subprocess
import unittest
import yaml
from mobs import tamanos
from mobs.tanda3b import definitions
from mobs.mythic import metaskills


class RestoredSizeTests(unittest.TestCase):
    def test_matches_parent_of_d51e4de_except_requested_cumbre(self):
        source=subprocess.check_output(['git','show','d51e4de^:datapack-src/mobs/tamanos.py'],cwd=tamanos.ROOT).decode('utf8')
        old={'__file__':tamanos.__file__,'__name__':'historical_tamanos'}
        exec(compile(source,'historical_tamanos','exec'),old)
        rows=tamanos.rows()+[(f'astral_esq_{k}',f'astral_esq_{k}',1,'SKELETON') for k in ('arquero','escudero','guardian','nigromante')]
        for mid,model,s,entity in rows:
            self.assertEqual(tamanos.scale(model,s,entity),old['scale'](model,s,entity),mid)

    def test_skeleton_spawn_and_load_use_restored_skill(self):
        mobs,skills=definitions()
        for mid,mob in mobs.items():
            if not mid.startswith('astral_esq_'):continue
            kind=mid.removeprefix('astral_esq_').split('_')[0]
            name='AST_ESQ_MODELO_'+kind
            for event in ('onSpawn','onLoad'):
                self.assertIn(f'skill{{s={name}}} @self ~{event}',mob['Skills'])
            expected=tamanos.scale('astral_esq_'+kind,1,'SKELETON')
            self.assertTrue(any(f'minecraft:scale base set {expected}' in v for v in skills[name]['Skills']))

    def test_cumbre_and_ancestral_model_and_attributes_equal(self):
        sk=yaml.safe_load(metaskills())
        def size(key):return [v for v in sk[key]['Skills'] if v.startswith('model{') or 'minecraft:scale' in v or 'minecraft:step_height' in v]
        self.assertEqual(size('AST_MODEL_astral_yeti_cumbre'),size('AST_MODEL_astral_yeti_ancestral'))


if __name__=='__main__':unittest.main()
