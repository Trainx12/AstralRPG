import sys,zipfile,unittest,re
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from deploy_tier_soporte import level_function
class SupportTierTest(unittest.TestCase):
    def test_all_tier_selectors_exclude_support(self):
        lines=[s for s in level_function().splitlines() if 'if items' in s]
        self.assertTrue(lines)
        for line in lines:
            self.assertIn('!minecraft:custom_data~{astral:{id:"varita_curacion"}}',line)
            self.assertIn('!minecraft:custom_data~{astral:{type:"talisman"}}',line)
    def test_normal_equipment_and_slots_remain(self):
        text=level_function()
        for t in range(1,11):
            for kind in ('weapon','staff','armor'):
                self.assertIn('type:"'+kind+'",tier:'+str(t),text)
        for slot in ('container.*','weapon.mainhand','weapon.offhand','armor.*'):
            self.assertIn(slot,text)
    def test_legacy_skill_requirements_are_ignored(self):
        text=Path(__file__).with_name('runtime').joinpath('AstralProgression.java').read_text()
        self.assertLess(text.index('model.getKey().equals("varita_curacion")'),text.index('var req=meta.'))
if __name__=='__main__':unittest.main()
