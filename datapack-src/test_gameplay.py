import json
from pathlib import Path
import unittest
import yaml
from gameplay import DUNGEONS, PROTECTED, patch_graves, script
from cosmeticos import menu_data, script as title_script
from lobby import cosmetic_rewards

ROOT=Path(__file__).resolve().parent.parent
PACK=ROOT/'build/AstralRPG-Items/data/astral'

class GameplayTests(unittest.TestCase):
    def components(self,iid):
        return json.loads((PACK/f'loot_table/item/{iid}.json').read_text(encoding='utf-8'))['pools'][0]['entries'][0]['functions'][0]['components']

    def test_armor_is_durable_breakable_and_uses_easier_defense(self):
        levels=(6,10,14,18,22)
        for cls in ('berserker','mago','arquero'):
            for tier in range(1,6):
                for piece in ('helmet','chestplate','leggings','boots'):
                    c=self.components(f'{cls}_{tier}_{piece}')
                    self.assertGreaterEqual(c['minecraft:max_damage'],1600)
                    self.assertNotIn('minecraft:unbreakable',c)
                    self.assertIn(f'"auraskills:defense":{levels[tier-1]}',c['minecraft:custom_data'])
                    self.assertNotIn('armor_requirements":{"auraskills:forging"',c['minecraft:custom_data'])

    def test_weapons_require_their_combat_skill(self):
        for prefix,skill in [('espada','fighting'),('hacha','fighting'),('baston','sorcery'),('arco','archery')]:
            for tier in range(1,6):
                self.assertIn(f'"auraskills:{skill}":',self.components(f'{prefix}_{tier}')['minecraft:custom_data'])

    def test_migration_never_clears_or_regives_inventory(self):
        text=(PACK/'function/upgrade/check.mcfunction').read_text()
        self.assertNotIn('clear ',text);self.assertNotIn('give ',text)
        for p in (PACK/'item_modifier/upgrade').glob('*.json'):
            mods=json.loads(p.read_text(encoding='utf-8'))
            self.assertNotIn('minecraft:damage',mods[0]['components'])
            self.assertNotIn('minecraft:trim',mods[0]['components'])
            self.assertNotIn('minecraft:enchantments',mods[0]['components'])
            self.assertNotIn('astral:mejora_arma',str(mods))
            self.assertNotIn('astral:mejora_armadura',str(mods))

    def test_tools_respect_shift_world_guards_and_single_drop(self):
        broke=(PACK/'function/tool/broke.mcfunction').read_text()
        self.assertLess(broke.index('astral:sneaking'),broke.index('function astral:tool/at'))
        for world in PROTECTED:self.assertIn('if dimension minecraft:'+world,broke)
        mine=(PACK/'function/tool/mine.mcfunction').read_text()
        self.assertEqual(mine.count('loot spawn'),1)
        self.assertIn('unless block ~ ~ ~ #astral:drillable',mine)
        self.assertIn('positioned ~ ~-2 ~',(PACK/'function/tool/d/down.mcfunction').read_text())
        self.assertNotIn('excellentenchants:tunnel',str(self.components('taladro_infernal')))

    def test_graves_preserve_only_protected_world_inventory(self):
        config=patch_graves({'disabled-worlds':['old']})
        self.assertEqual(config['despawn-time-seconds'],-1)
        self.assertFalse(config['override-keep-inventory'])
        self.assertTrue(config['store-items'])
        self.assertTrue(set(PROTECTED)<=set(config['disabled-worlds']))
        self.assertNotIn('world',config['disabled-worlds'])

    def test_escape_items_and_mobility_are_blocked_in_dungeons(self):
        text=script()
        for w in DUNGEONS:self.assertIn('"'+w+'"',text)
        for word in ['elytra','ender pearl','chorus fruit','trapdoor','wind charge','riptide','water bucket','boat','minecart','on mount:','loop-player is swimming:']:
            self.assertIn(word,text)
        self.assertIn('on player jump key press:\n    if astral_dungeon(world of player) is true:\n        stop',text)
        self.assertNotIn('flight mode',text)

    def test_titles_are_owned_permanently_and_equipping_is_guarded(self):
        for _,_,_,commands in cosmetic_rewards():
            self.assertNotIn('setprefix',str(commands))
        text=title_script()
        for key,item in menu_data()['items'].items():
            if 'view_requirement' not in item:continue
            self.assertIn('click_requirement',item)
            self.assertIn('astral.cosmetico.titulo.'+key,text)
        self.assertNotIn('permission unset',text)

    def test_luck_whitelist_cannot_include_storage_or_resource_blocks(self):
        for skill in ('mining','foraging'):
            d=yaml.safe_load((ROOT/f'build/gameplay/AuraSkills/{skill}.yml').read_text(encoding='utf-8'))
            allowed=d['tags'][skill+'_luck_applicable']
            self.assertNotIn('*',allowed)
            for key in allowed:
                block=d['sources'][key]['block']
                self.assertNotIn('shulker',block)
                self.assertNotIn(block,('beacon','diamond_block','netherite_block','chest','barrel'))
            self.assertTrue(d['default']['check_replace'])

if __name__=='__main__':unittest.main()
