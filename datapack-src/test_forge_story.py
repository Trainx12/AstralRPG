"""La forja de la guia debe registrar la misma fabricacion que el altar."""
import json
from pathlib import Path
import re
import unittest
import zipfile

ROOT=Path(__file__).resolve().parent.parent


class ForgeStoryHooks(unittest.TestCase):
    def test_successful_guide_crafts_record_tier_one_and_five(self):
        seen=set()
        with zipfile.ZipFile(ROOT/'build/AstralRPG-Items.zip') as pack:
            for path in pack.namelist():
                if not path.startswith('data/astral/function/forge/r/'):continue
                function=pack.read(path).decode()
                output=re.search(r'loot give @s loot astral:item/([a-z0-9_]+)',function)[1]
                loot=json.loads(pack.read(f'data/astral/loot_table/item/{output}.json'))
                data=loot['pools'][0]['entries'][0]['functions'][0]['components']['minecraft:custom_data']
                for tier in (1,5):
                    if re.search(rf'\btier:{tier}[,}}]',data) or output==f'baston_{tier}':
                        with self.subTest(recipe=output,tier=tier):
                            event=f'function astral:quest/event/forge{tier}'
                            self.assertIn(event,function)
                            self.assertLess(function.index('run return run function astral:forge/missing'),function.index(event))
                            self.assertLess(function.index('loot give @s'),function.index(event))
                            self.assertLess(function.index(event),function.rindex('return 1'))
                            seen.add(tier)
        self.assertEqual(seen,{1,5})

    def test_traveler_only_teleports_and_does_not_open_missions(self):
        mobs=(ROOT/'build/mythicmobs/mobs/astral.yml').read_text(encoding='utf-8')
        block=re.search(r'^astral_npc_viajero:.*?(?=^astral_npc_|\Z)',mobs,re.M|re.S)[0]
        self.assertIn('mvtp <trigger.name> w:world',block)
        self.assertNotIn('crouching',block)
        self.assertNotIn('AQ_VIAJERO',block)
        bridge=(ROOT/'build/mythicmobs/skills/misiones.yml').read_text(encoding='utf-8').split('AQ_HERRERO:')[0]
        self.assertIn('mvtp <target.name> w:world',bridge)
        self.assertNotIn('dm open',bridge)


if __name__=='__main__':unittest.main()
