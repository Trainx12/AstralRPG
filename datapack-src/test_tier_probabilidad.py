"""Ejecuta las ramas generadas para los 100 resultados de cada tier."""
import re
import unittest
import zipfile
from collections import Counter
from pathlib import Path
from escala import TIER_MAX

ROOT = Path(__file__).resolve().parents[1]


class TierProbabilityTests(unittest.TestCase):
    def test_all_rolls_and_boundaries(self):
        with zipfile.ZipFile(ROOT/'build/AstralRPG-Items.zip') as z:
            funcs={name:z.read('data/astral/function/mob/'+name+'.mcfunction').decode()
                   for name in ('tier_mundo','tier_mundo_alto')}
        def roll(tier, r):
            def execute(name):
                nonlocal tier
                for line in funcs[name].splitlines():
                    if 'operation #mt' in line or 'random value' in line:continue
                    conditions=re.findall(r'if score #(mt|r) astral.tmp matches ([\d.]+)',line)
                    valid=True
                    for variable,bounds in conditions:
                        value=tier if variable=='mt' else r
                        low,high=bounds.split('..') if '..' in bounds else (bounds,bounds)
                        valid &= (not low or value>=int(low)) and (not high or value<=int(high))
                    if not valid:continue
                    if 'return 0' in line:return
                    if 'run function astral:mob/' in line:
                        execute(line.split('astral:mob/')[1]);return
                    if 'players add #mt' in line:tier+=1
                    if 'players remove #mt' in line:tier-=1
                    if 'return run' in line:return
            execute('tier_mundo')
            return tier
        for tier in range(1,TIER_MAX+1):
            with self.subTest(tier=tier):
                counts=Counter(roll(tier,r) for r in range(1,101))
                up=4 if tier<6 else 10
                self.assertEqual(counts[tier-1],10)
                self.assertEqual(counts[tier+1],up if tier<TIER_MAX else 0)
                self.assertEqual(counts[tier],100-10-(up if tier<TIER_MAX else 0))
                self.assertLessEqual(max(counts),TIER_MAX)


if __name__=='__main__':unittest.main()
