"""Verifica el contrato visible contra los componentes exportados y la migración."""
import json
import unittest
from escala import HECHIZO
from pathlib import Path
from escala import fmt
from items import MEJORA_DANO, STAFFS
from special_weapons import WEAPONS
from ficha import RAREZA

PACK = Path(__file__).resolve().parent.parent/'build/AstralRPG-Items/data/astral'

def read(path):
    return json.loads((PACK/path).read_text(encoding='utf-8'))

def text(component):
    return component.get('text','')+''.join(text(c) for c in component.get('extra',[]))

class FichaTests(unittest.TestCase):
    def components(self,iid):
        return read(f'loot_table/item/{iid}.json')['pools'][0]['entries'][0]['functions'][0]['components']

    def test_sections_attributes_rarity_and_all_upgrade_levels(self):
        cases={'espada_1':(1,'ESPADA'), 'espada_5':(5,'ESPADA'), 'hacha_3':(3,'HACHA'),
               'arco_2':(2,'ARCO'), 'baston_4':(4,'BASTÓN'), 'guadana_3':(3,'GUADAÑA'),
               'lanza_3':(3,'LANZA'), 'guantes_meteoro':(3,'GUANTES'), 'guadana_umbria':(3,'GUADAÑA')}
        cases.update({iid:(3,'HACHA' if iid.startswith('hacha') else 'VARITA' if iid.startswith('varita') else 'ESPADA') for iid in WEAPONS})
        for iid,(tier,kind) in cases.items():
            c=self.components(iid)
            hidden=c['minecraft:tooltip_display']['hidden_components']
            self.assertNotIn('minecraft:enchantments',hidden)
            for level in range(11):
                with self.subTest(iid=iid,level=level):
                    mods=read(f'item_modifier/ficha/{iid}/{level}.json')
                    self.assertEqual(mods[0]['target'],'item_name')
                    self.assertEqual(mods[1]['mode'],'replace_all')
                    lore=mods[1]['lore']; lines=list(map(text,lore))
                    self.assertEqual(lines[-1],RAREZA[tier][0]+' '+kind)
                    self.assertEqual(lore[-1]['color'],RAREZA[tier][1])
                    self.assertTrue(lore[-1]['bold'])
                    stars=0 if iid.startswith('baston') else level
                    self.assertEqual(text(mods[0]['name']).count('✪'),stars)
                    colors=[s['color'] for s in mods[0]['name'].get('extra',[]) if s['text']=='✪']
                    self.assertEqual(colors.count('red'),max(0,stars-5))
                    damage=next((m['amount']+1 for m in c.get('minecraft:attribute_modifiers',[]) if m['type']=='minecraft:attack_damage'),None)
                    if damage is not None:
                        factor=MEJORA_DANO[level-1] if level else 1
                        expected='Daño: +'+fmt(damage*factor)
                        if level:expected+=' (+'+fmt(damage*(factor-1))+')'
                        self.assertEqual(lines[1],expected)
                        self.assertEqual(lore[1]['color'],'gray')
                    req=[n for n,s in enumerate(lines) if s.startswith('Requiere:')]
                    if req:self.assertEqual(req,[len(lines)-2])
                    ability=[n for n,s in enumerate(lines) if s.startswith('Habilidad:')]
                    if ability:self.assertIn('',lines[:ability[0]])
                    def check_italic(component):
                        self.assertIs(component['italic'],False)
                        for child in component.get('extra',[]):check_italic(child)
                    for line in lore:check_italic(line)
                    migrated=read(f'item_modifier/upgrade/{iid}/{level}.json')
                    self.assertEqual(migrated[0]['components']['minecraft:lore'],lore)
                    self.assertNotIn('minecraft:enchantments',migrated[0]['components'])

    def test_staff_uses_cast_damage_without_armor(self):
        for tier,s in enumerate(STAFFS,1):
            # Igual que spell/cast: #pct en %, base x pct / 100 (enteros del scoreboard).
            pct=(10000+s['mdmg']*100+s.get('pierce',0)*100)//100
            damage=HECHIZO[tier]*pct//100
            self.assertLess(HECHIZO[tier]*pct,2**31-1)
            lore=list(map(text,self.components(f'baston_{tier}')['minecraft:lore']))
            self.assertIn('Daño de hechizo: +'+fmt(damage),lore)

    def test_macro_migration_and_defense_wiring(self):
        macro=(PACK/'function/ficha/apply/7.mcfunction').read_text()
        self.assertIn('astral:ficha/$(id)/7',macro)
        slot=(PACK/'function/upgrade/slot/container_0.mcfunction').read_text()
        self.assertLess(slot.index('astral:upgrade/espada_5/7'),slot.index('astral:upgrade/espada_5\n'))
        self.assertIn('scoreboard objectives add astraldef dummy',(PACK/'function/load.mcfunction').read_text())
        self.assertIn('store result score @s astraldef run attribute @s minecraft:armor get',(PACK/'function/loop/t10.mcfunction').read_text())

if __name__=='__main__':unittest.main()
