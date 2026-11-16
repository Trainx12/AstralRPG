"""Contrato exhaustivo del equipo exportado, balance y migracion conservadora."""
import json
import re
import unittest
from pathlib import Path
from balance_equipo import *
from escala import DANO, fmt, defensa_pieza
from items import TALISMANS, MEJORA_DANO
from special_weapons import WEAPONS

ROOT=Path(__file__).resolve().parents[1]
PACK=ROOT/'build/AstralRPG-Items/data/astral'
def read(path):return json.loads((PACK/path).read_text(encoding='utf-8'))
def item(iid):return read(f'loot_table/item/{iid}.json')['pools'][0]['entries'][0]['functions'][0]['components']
def text(c):return c.get('text','')+''.join(map(text,c.get('extra',[])))
def damage(c):return next(m['amount']+1 for m in c['minecraft:attribute_modifiers'] if m['type']=='minecraft:attack_damage')

class BalanceTests(unittest.TestCase):
    def test_special_tiers_damage_and_sismo(self):
        for iid,w in WEAPONS.items():
            c=item(iid)
            self.assertIn(f"tier:{SPECIAL_TIERS[iid]}",c['minecraft:custom_data'])
            self.assertAlmostEqual(damage(c),w['damage_total'],places=3)
        self.assertAlmostEqual(damage(item('hacha_terremoto')),damage(item('hacha_3')),places=3)
        s=(ROOT/'build/gameplay/astral_armas_especiales.sk').read_text(encoding='utf-8')
        self.assertIn('2 * (attack damage attribute of {_p})',s)
        for lv,factor in enumerate(MEJORA_DANO,1):
            self.assertIn(f'if {{_qu}} is {lv}:\n        set {{_quakeDamage}} to {{_quakeDamage}} * {factor}',s)
        self.assertNotIn('* {@escala}',s)

    def test_talismans_percentages_and_real_defense(self):
        for tid in TALISMANS:
            for lv,pct in enumerate(TALISMAN_PCT,1):
                c=item(f'talisman_{tid}_{lv}');m=c['minecraft:attribute_modifiers'][0]
                self.assertEqual(m['operation'],'add_multiplied_base')
                self.assertEqual(m['amount'],pct)
                self.assertIn(f'{round(pct*100)}%', '\n'.join(map(text,c['minecraft:lore'])))
        pdef=(PACK/'function/player/def.mcfunction').read_text()
        for lv in range(1,4):self.assertIn(f'talisman_roca_{lv}',pdef)
        self.assertIn('operation #v astral.tmp -= #bar astral.tmp',pdef)

    def test_spears_asura_carnivora(self):
        for t in range(1,11):
            c=item(f'lanza_{t}')
            self.assertAlmostEqual(damage(c),DANO[t]*.9,places=3)
            self.assertNotIn('astral:poder_astral',c.get('minecraft:enchantments',{}))
            self.assertIn('spear_balance:1',c['minecraft:custom_data'])
        self.assertAlmostEqual(damage(item('asura_espada')),damage(item('espada_4'))*ASURA_DANO)
        for enchant in ('empalar','poder_astral'):
            self.assertIn('spear_balance:1',json.dumps(read(f'enchantment/{enchant}.json')))
        self.assertLess(damage(item('asura_espada'))*(1+ASURA_EXTRA),damage(item('espada_5')))
        for p in ('helmet','chestplate','leggings','boots'):
            raw=item('carnivora_'+p)['minecraft:custom_data']
            d=int(re.search(r'def:(\d+)',raw)[1])
            self.assertEqual(d,defensa_pieza(3,p,CARNIVORA_DEF))
            self.assertGreater(d,defensa_pieza(3,p))

    def test_every_equipment_card_and_preserving_migration(self):
        count=0
        for path in (PACK/'loot_table/item').glob('*.json'):
            c=item(path.stem);raw=c['minecraft:custom_data']
            if not re.search(r'type:"(?:weapon|staff|armor|tool|utility|talisman)"',raw):continue
            if not re.search(r'tier:\d+',raw):continue
            count+=1;lines=list(map(text,c['minecraft:lore']))
            with self.subTest(item=path.stem):
                self.assertTrue(any(l.startswith('Tier:') for l in lines),lines)
                self.assertTrue(any(l.startswith('Requiere:') for l in lines),lines)
                if 'minecraft:attack_damage' in str(c.get('minecraft:attribute_modifiers',[])) and 'type:"talisman"' not in raw and 'type:"armor"' not in raw:
                    self.assertIn('Daño: +'+fmt(damage(c)),lines)
                if 'type:"armor"' in raw:
                    self.assertTrue(any(l.startswith('Vida:') for l in lines))
                    self.assertIn('Defensa: +'+re.search(r'def:(\d+)',raw)[1],lines)
                    self.assertGreaterEqual(c['minecraft:max_damage'],ARMOR_MIN)
                modifier=read(f'item_modifier/upgrade/{path.stem}.json')[0]['components']
                self.assertNotIn('minecraft:damage',modifier)
                self.assertNotIn('minecraft:enchantments',modifier)
        self.assertGreater(count,180)

    def test_mobility_has_card_without_changing_abilities(self):
        for iid in ('gancho','gancho_realista'):
            c=item(iid);lines=list(map(text,c['minecraft:lore']))
            self.assertIn('tier:1',c['minecraft:custom_data'])
            self.assertIn('Daño: 0 (movilidad)',lines)
            self.assertIn('Tier: 1',lines);self.assertIn('Requiere: sin nivel',lines)
            self.assertTrue(any(l.startswith('Habilidad:') for l in lines))

    def test_water_abilities_and_existing_cleanup(self):
        self.assertEqual(AGUA_PROYECTIL,3186)
        self.assertEqual(AGUA_MANA,90);self.assertEqual(AGUA_CD,22)
        for iid in ('agua_espada','agua_hacha','agua_arco'):
            self.assertIn('Habilidad:', '\n'.join(map(text,item(iid)['minecraft:lore'])))
        import rankings,mazmorras_copias
        self.assertFalse(any(r in ('infinita','trainx') and dim=='minecraft:lobby' for r,dim,*_ in rankings.carteles()))
        self.assertTrue({'item','arrow','trident'}<=set(mazmorras_copias.LIMPIAR))

if __name__=='__main__':unittest.main()
