import unittest
from stellarity_tiers import *
from stellarity_balance import defense_patch
from mesa_encantamientos import precio_subasta

class StellarityTests(unittest.TestCase):
    def test_catalog_complete(self):
        table=rows()
        self.assertEqual(set(table),set(CATALOG))
        for k,r in CATALOG.items():
            if r['group'] in ('weapons','armor','tools','trinkets','books'):
                self.assertGreater(table[k]['tier'],0,k)
                if k!='reinforced_horse_armor': self.assertGreater(table[k]['level'],0,k)
    def test_reference_damage(self):
        for k,(t,f) in WEAPONS.items():
            damage=rows()[k]['damage']
            if f=='sword': self.assertAlmostEqual(damage,DANO[t],places=3)
            if f=='spear': self.assertAlmostEqual(damage,DANO[t]*.9,places=3)
            if f=='axe': self.assertAlmostEqual(damage,AXES[t-1]['dmg']*(1+AXES[t-1]['bonus']/100)*FACTOR_ARMA[t],places=3)
            if f in ('bow','crossbow'): self.assertEqual(damage,round(9*PUNTERIA[t-1]*FACTOR_ARMA[t]))
    def test_prices_use_live_bases(self):
        p=precio_subasta()
        for r in rows().values(): self.assertGreater(suggested(r,p['base-arma'],p['base-armadura']),0)
        r=rows()['dragonblade']
        self.assertEqual(suggested(r,{5:123456},{5:44}),123456)
        self.assertEqual(suggested(rows()['void_locket'],{5:200},{5:44}),100)
    def test_armor(self):
        for k,(t,p) in ARMOR.items():
            self.assertEqual(rows()[k]['defense'],defensa_pieza(t,p))
            self.assertEqual(rows()[k]['health'],VIDA_PIEZA[t])
        self.assertEqual(rows()['dragon_wings']['defense'],round(defensa_pieza(6,'chestplate')*.6))
        self.assertAlmostEqual(rows()['dragon_wings']['health'],VIDA_PIEZA[6]*.6)
    def test_defense_compat(self):
        line='execute if data storage astral:tmp eq.chest.components."minecraft:custom_data".astral.def run scoreboard players remove #v astral.tmp 40\n'
        self.assertIn('unless data storage astral:tmp eq.chest.components."minecraft:custom_data".astral.stellarity',defense_patch(line))
    def test_fixed_no_requirements(self):
        for k in FIXED:
            self.assertEqual(rows()[k]['tier'],0)
            self.assertNotIn('skill',rows()[k])

if __name__=='__main__': unittest.main()
