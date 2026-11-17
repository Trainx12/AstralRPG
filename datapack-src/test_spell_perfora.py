"""Contrato de generacion y reparacion del FINAL, complementado por SpellProbe real."""
import json
from pathlib import Path
import unittest
import zipfile
from escala import HECHIZO_PERFORA
from deploy_bastones_golems import repair, KINDS

ROOT = Path(__file__).resolve().parents[1]


class SpellPerforaTest(unittest.TestCase):
    def test_damage_and_cleanup(self):
        with zipfile.ZipFile(ROOT/'build/AstralRPG-Items.zip') as z:
            trace=z.read('data/astral/function/spell/trace.mcfunction').decode()
            for n, factor in enumerate(HECHIZO_PERFORA, 1):
                self.assertIn(f'spell.dmg float {factor} run scoreboard', trace)
                self.assertIn(f'remove astral.spell.hit{n}', trace)
            self.assertEqual(trace.count('run function astral:spell/hit with storage'), 3)
            self.assertIn('spell.len float 0.001', trace)
            for tier in (1,4,8,10):
                loot=json.loads(z.read(f'data/astral/loot_table/item/baston_{tier}.json'))
                def text(value):
                    if isinstance(value,dict):
                        return value.get('text','') + ''.join(text(c) for c in value.get('extra',[]))
                    return ''
                lore=loot['pools'][0]['entries'][0]['functions'][0]['components']['minecraft:lore']
                rendered='\n'.join(text(line) for line in lore)
                self.assertIn('Atraviesa hasta 3 enemigos',rendered)
                self.assertIn('100%/70%/70%',rendered)

    def test_repair_preserves_other_assets_and_resolves_textures(self):
        files={'pack.mcmeta':b'unchanged', 'assets/other/textures/test.png':b'previous'}
        for kind in KINDS:
            stem='astral_golem_'+kind+'_0'
            files[f'bettermodel/models/{stem}.json']=json.dumps({'textures':{'0':'bettermodel:item/'+stem}}).encode()
            files[f'bettermodel/textures/item/{stem}.png']=b'png'
        result, delta=repair(files)
        self.assertEqual(len(delta),6)
        self.assertEqual(result['pack.mcmeta'],b'unchanged')
        self.assertEqual(result['assets/other/textures/test.png'],b'previous')
        self.assertEqual(repair(result),(result,[]))
        del files['bettermodel/textures/item/astral_golem_bosque_0.png']
        with self.assertRaisesRegex(ValueError,'Textura ausente'):
            repair(files)


if __name__ == '__main__':
    unittest.main()
