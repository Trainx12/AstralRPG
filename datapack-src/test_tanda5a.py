import json
from pathlib import Path
import unittest
import yaml
from escala import XP_MOB, xp_skill_mob, xp_skill_level
from tanda5a import PAQUETES, PROBABILIDADES, catalog, loot_tier, mythic_catalog

ROOT=Path(__file__).resolve().parents[1]


class Tanda5aTests(unittest.TestCase):
    def test_xp_table_and_boss_cap(self):
        self.assertEqual([xp_skill_mob(t) for t in range(6)], [0,20,40,80,140,230.8])
        for t in range(1,6):
            self.assertEqual(xp_skill_mob(t,True,True),xp_skill_mob(t,jefe=True))
            self.assertLess(xp_skill_mob(t,jefe=True),xp_skill_level(15 if t<4 else 26))
        self.assertEqual(xp_skill_level(26),57700)
        self.assertAlmostEqual(XP_MOB[5]*250,57700)

    def test_shop_adds_area(self):
        self.assertEqual(PAQUETES,[(25,15000),(100,50000),(1225,500000),(2500,950000),(10000,3500000)])
        cfg=yaml.safe_load((ROOT/'build/tanda5a/GriefPreventionData/config.yml').read_text())['GriefPrevention']
        self.assertEqual(cfg['Claims']['InitialBlocks']+PAQUETES[0][0],61)
        self.assertEqual(cfg['Claims']['Claim Blocks Accrued Per Hour']['Default'],0)
        self.assertEqual(cfg['Claims']['MinimumWidth'],6)
        self.assertEqual(cfg['Claims']['MinimumArea'],36)
        self.assertGreater(cfg['Claims']['ExtendIntoGroundDistance'],384)
        self.assertEqual(cfg['Economy']['ClaimBlocksPurchaseCost'],0)

    def test_loot_catalog_is_equipment_and_materials_only(self):
        items=catalog()
        self.assertIn('espada_5',items)
        self.assertIn('fragmento_cristal',items)
        self.assertNotIn('espada_heroe_errante',items)
        self.assertNotIn('estrella_menu',items)
        self.assertEqual(items['espada_5']['chance'],.000003)
        self.assertEqual(items['espada_4']['chance'],.0004)
        self.assertEqual(items['nucleo_astral']['tier'],5)
        self.assertEqual(items['nucleo_astral']['chance'],.000003)
        self.assertEqual(PROBABILIDADES[1],.15)
        for iid in items:
            self.assertNotIn('peluche',iid)

    def test_structure_tiers(self):
        for key,tier in [('minecraft:chests/village/village_weaponsmith',2),
                         ('minecraft:chests/shipwreck_treasure',2),
                         ('minecraft:chests/abandoned_mineshaft',3),
                         ('minecraft:chests/bastion_treasure',5),
                         ('nova_structures:chests/wizard_tower',5),
                         ('structory:outcast/low',2),('structory_towers:top/ocean_pillar_top',5),
                         ('future:chests/new_dungeon',3)]:
            self.assertEqual(loot_tier(key),tier,key)

    def test_mythic_excludes_npcs_and_pets(self):
        mobs=mythic_catalog()
        self.assertIn('astral_goblin',mobs)
        self.assertTrue(mobs['astral_mina_guardian']['boss'])
        self.assertEqual(mobs['astral_mina_guardian']['tier'],2)
        for mid in mobs:
            self.assertNotIn('npc_',mid)
            self.assertNotIn('control_',mid)
            self.assertNotIn('pet_',mid)


if __name__=='__main__': unittest.main()
