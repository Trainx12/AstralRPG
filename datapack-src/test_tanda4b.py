"""Balance, recursos privados, mascotas y comandos de la tanda 4b."""
import json
import struct
import unittest
import zipfile
from copy import deepcopy
from pathlib import Path
from tanda4b import CLONES, SIMPLE, register
from escala import VIDA_PIEZA, DEFENSA_SET
from terceros import ROOT, privado, sources


class Tanda4bTests(unittest.TestCase):
    def loot(self,iid):
        with zipfile.ZipFile(ROOT/'build/AstralRPG-Items.zip') as z:
            return json.loads(z.read('data/astral/loot_table/item/'+iid+'.json'))['pools'][0]['entries'][0]['functions'][0]['components']

    def test_asura_matches_tier_four_and_keeps_identity(self):
        c=self.loot('asura_espada'); ref=self.loot('espada_4')
        self.assertIn('tier:4',c['minecraft:custom_data'])
        self.assertIn('id:"asura_espada"',c['minecraft:custom_data'])
        self.assertEqual(c['minecraft:attribute_modifiers'],ref['minecraft:attribute_modifiers'])
        self.assertNotIn('V', c['minecraft:lore'][0]['text'].replace('IV',''))
        self.assertIn('tier:4',self.loot('asura_alas')['minecraft:custom_data'])

    def test_carnivora_class_stats_and_armor(self):
        total=0
        for piece in ('helmet','chestplate','leggings','boots'):
            c=self.loot('carnivora_'+piece)
            total+=next(m['amount'] for m in c['minecraft:attribute_modifiers'] if m['type']=='minecraft:max_health')
            self.assertIn('tier:3',c['minecraft:custom_data'])
        self.assertEqual(total,4*VIDA_PIEZA[3])
        for iid,(source,_,_) in CLONES.items():
            if iid=='carnivora_hacha': continue
            self.assertEqual(self.loot(iid).get('minecraft:attribute_modifiers'), self.loot(source).get('minecraft:attribute_modifiers'))
            self.assertEqual(self.loot(iid).get('minecraft:enchantments'),self.loot(source).get('minecraft:enchantments'))

    def test_recipes_use_all_coins_and_t4_materials(self):
        items={source:{'components':{'minecraft:custom_data':'{id:"'+source+'"}'}} for source,_,_ in CLONES.values()}
        recipes=[]
        register(items,{},recipes,lambda *a,**k:None,lambda t,*a,**k:{'text':t},lambda *a,**k:[])
        asura=[r for r in recipes if r[0].startswith('asura_')]
        self.assertEqual(len(asura),1)
        self.assertFalse(any(r[0].endswith('_alas') for r in recipes))
        for _,_,ingredients,_ in asura:
            ids={i[1] for i in ingredients}
            self.assertTrue({'asura_moneda_'+k for k in ('emerald','card','circle','square','triangle')}<=ids)
            self.assertNotIn('nucleo_astral',ids); self.assertNotIn('gema_umbria_perfecta',ids)

    def test_ore_fortune_pickaxe_and_all_rare_drops(self):
        with zipfile.ZipFile(ROOT/'build/AstralRPG-Items.zip') as z:
            data=json.loads(z.read('data/minecraft/loot_table/blocks/note_block.json'))
            text=json.dumps(data)
            for k in ('emerald','card','circle','square','triangle'): self.assertIn('asura_moneda_'+k,text)
            self.assertIn('minecraft:fortune',text); self.assertIn('#minecraft:pickaxes',text)
            feature=json.loads(z.read('data/astral/worldgen/configured_feature/asura_ore.json'))
            self.assertEqual(feature['config']['targets'][0]['target']['block'],'minecraft:end_stone')
            from minecraft_commands import validate
            for name in z.namelist():
                if name.endswith('.mcfunction'): validate(z.read(name).decode(),name)

    def test_runtime_is_java25_and_shop_is_present(self):
        with zipfile.ZipFile(ROOT/'build/runtime/AstralDecor.jar') as z:
            self.assertEqual(struct.unpack('>H',z.read('astral/AstralDecor.class')[6:8])[0],69)
            self.assertIn('astral/AstralDecor$PlushShop.class',z.namelist())
        import yaml
        section=yaml.safe_load((ROOT/'build/shop/EconomyShopGUI/sections/Peluches.yml').read_text())
        self.assertEqual(section['title'],'Astral - Peluches')

    def test_private_pet_copies_remove_metadata_and_inverted_outlines(self):
        from build_privado import adapted
        for mid,path in sources().items():
            if not mid.startswith('astral_pet_'): continue
            original=json.loads(path.read_text(encoding='utf8')); before=deepcopy(original)
            copy=adapted(original,mid); self.assertEqual(original,before)
            self.assertFalse(any(e.get('name')=='cube_outline' and any(a>b for a,b in zip(e['from'],e['to'])) for e in copy['elements']))
            self.assertFalse(any(g['name'] in ('hitbox','tag_status','tag_nickname') for g in copy.get('groups',[])))

    def test_private_item_model_and_texture_references(self):
        with zipfile.ZipFile(privado()/'build/AstralRPG-Textures.zip') as z:
            names=set(z.namelist()); seen=set()
            def model(ref):
                if ref.startswith('minecraft:') or ref in seen: return
                seen.add(ref); ns,path=ref.split(':'); key=f'assets/{ns}/models/{path}.json'
                self.assertIn(key,names)
                data=json.loads(z.read(key))
                if 'parent' in data: model(data['parent'])
                for tex in data.get('textures',{}).values():
                    if tex.startswith(('#','minecraft:')): continue
                    ns,path=tex.split(':'); self.assertIn(f'assets/{ns}/textures/{path}.png',names)
            def visit(tree):
                if isinstance(tree,dict):
                    if tree.get('type')=='minecraft:model': model(tree['model'])
                    for value in tree.values(): visit(value)
                elif isinstance(tree,list):
                    for value in tree: visit(value)
            for iid in list(CLONES)+list(SIMPLE)+['carnivora_'+p for p in ('helmet','chestplate','leggings','boots')]:
                visit(json.loads(z.read('assets/astral/items/'+iid+'.json')))


if __name__=='__main__': unittest.main()
