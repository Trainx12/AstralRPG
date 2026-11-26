"""Pesos reales exportados, aislamiento de cajas y contrato de monturas/hostiles."""
from pathlib import Path
from collections import defaultdict
import unittest
import yaml
from lobby import GACHAS, crate_yml, mount_rewards, icon
from mobs.mythic import MOBS, mob_block

ROOT=Path(__file__).resolve().parents[1]
class MountTests(unittest.TestCase):
    def test_exported_weights(self):
        expected=[55,20,10,11,3.5,.5]
        for suffix,kwargs in [('',{}),('_suerte',dict(suerte=True)),('_garantia',dict(garantia=True))]:
            prizes=yaml.safe_load(crate_yml('gacha_monturas',GACHAS['gacha_monturas'],**kwargs))['Crate']['Prizes']
            sums=defaultdict(float)
            for p in prizes.values():
                rarity=p['DisplayLore'][1].split(': ')[-1]
                sums[rarity]+=p['Weight']
            labels=['Basura','Comun','Poco comun','Raro','Epico','Legendario']
            actual={next(n for n in labels if k.endswith('>'+n)):v for k,v in sums.items()}
            values=expected.copy()
            if suffix=='_suerte':values=[v*(1.5 if i>=3 else 1) / 107.5 *100 for i,v in enumerate(values)]
            if suffix=='_garantia':
                self.assertEqual(set(actual),{'Epico','Legendario'})
                values=[0,0,0,0,87.5,12.5]
            for label,value in zip(labels,values):self.assertAlmostEqual(actual.get(label,0),value,delta=.003)
            self.assertEqual((ROOT/f'build/lobby/CrazyCrates/crates/gacha_monturas{suffix}.yml').read_text('utf8'),crate_yml('gacha_monturas',GACHAS['gacha_monturas'],**kwargs))

    def test_trash_icons_and_no_pity_reset(self):
        trash=[r for r in mount_rewards() if r[0]=='trash']
        self.assertEqual(len(trash),10)
        self.assertEqual(len({icon(r[3])[0] for r in trash}),10)
        for r in trash:
            self.assertEqual(r[1],1)
            self.assertTrue(r[3][0].startswith('give %player% minecraft:'))
        self.assertTrue(any('damage=64' in r[3][0] for r in trash))
        text=crate_yml('gacha_monturas',GACHAS['gacha_monturas'])
        self.assertIn('<dark_gray>☆☆☆☆☆',text)
        for p in yaml.safe_load(text)['Crate']['Prizes'].values():
            if 'Basura' in p['DisplayLore'][1]:self.assertFalse(any('scoreboard' in c for c in p['Commands']))

    def test_hostiles_and_mount_contracts(self):
        for mid in ('astral_mapache','astral_pinguino'):
            d=MOBS[mid];block=mob_block(mid,d)
            self.assertEqual(d['kind'],'hostil');self.assertTrue(d['hostile_ai'])
            self.assertIn('astral:mob/roll',block)
            self.assertNotIn('astral:mob/roll', '\n'.join(x for x in block.splitlines() if '~onLoad' in x))
        for mid in ('astral_grillo','astral_chocobo','astral_escarabajo','astral_lagarto'):
            block=mob_block(mid,MOBS[mid]);self.assertIn('astralmount',block)
            self.assertNotIn('mountmodel',block);self.assertIn('Tame:1b',block)
        for mid in ('astral_ave','astral_pterodactilo'):
            self.assertIn('astralmount',mob_block(mid,MOBS[mid]));self.assertTrue(MOBS[mid]['fly'])
        self.assertEqual(MOBS['astral_lagarto']['kind'],'montura')
        self.assertEqual(MOBS['astral_lagarto']['type'],'SKELETON_HORSE')

if __name__=='__main__':unittest.main()
