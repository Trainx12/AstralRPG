"""Regresiones de componentes, geometria de alas y aislamiento de la entrega."""
import itertools
import json
import unittest
import zipfile
from terceros import ROOT,privado
from tanda4b_privado import rotate,wing_components
from deploy_tienda import baseline,BASE_SHA
from lobby import NPC_POS


class TiendaDecorTests(unittest.TestCase):
    def test_wings_do_not_take_armor_slot_or_grant_armor_or_flight(self):
        with zipfile.ZipFile(ROOT/'build/AstralRPG-Items.zip') as z:
            for iid in ('carnivora_alas','asura_alas'):
                c=json.loads(z.read(f'data/astral/loot_table/item/{iid}.json'))['pools'][0]['entries'][0]['functions'][0]['components']
                self.assertNotIn('minecraft:equippable',c)
                self.assertNotIn('minecraft:glider',c)
                self.assertNotIn('minecraft:attribute_modifiers',c)
                self.assertEqual(c['minecraft:max_stack_size'],1)
                self.assertIn('Segunda mano',c['minecraft:lore'][0]['text'])

    def test_entire_wing_geometry_is_behind_shoulders(self):
        pack=privado()/'build/entregas/tienda-modelo/AstralRPG-Textures.zip'
        with zipfile.ZipFile(pack) as z:
            for iid,ref in [('asura_alas','asura:asura_wings'),('carnivora_alas','elitecreatures:carnivoret_weapon_set/wing')]:
                ns,name=ref.split(':');raw=json.loads(z.read(f'assets/{ns}/models/{name}.json'))
                tree,wrapper=wing_components(iid,raw);fixed=wrapper['display']['fixed']
                self.assertEqual(tree,json.loads(z.read(f'assets/astral/items/{iid}.json'))['model'])
                self.assertEqual(wrapper,json.loads(z.read(f'assets/astral/models/cosmetics/{iid}.json')))
                self.assertEqual(tree['cases'][0]['model']['type'],'minecraft:empty')
                points=[]
                for e in raw['elements']:
                    for p in itertools.product(*zip(e['from'],e['to'])):
                        if r:=e.get('rotation'):p=rotate(p,r['origin'],r['axis'],r['angle'])
                        p=rotate([(v-8)*fixed['scale'][a] for a,v in enumerate(p)],[0,0,0],'y',fixed['rotation'][1])
                        points.append([p[a]+fixed['translation'][a] for a in range(3)])
                self.assertLessEqual(max(p[2] for p in points),.00001)
                self.assertAlmostEqual(max(p[1] for p in points),0,places=4)
                self.assertLess(max(p[2]/16-.32 for p in points),-.319)

    def test_pack_preserves_previous_assets_except_two_item_definitions(self):
        import io,hashlib
        blob=baseline('AstralRPG-Textures.zip');self.assertEqual(hashlib.sha1(blob).hexdigest(),BASE_SHA)
        with zipfile.ZipFile(io.BytesIO(blob)) as before,zipfile.ZipFile(privado()/'build/entregas/tienda-modelo/AstralRPG-Textures.zip') as after:
            self.assertTrue(set(before.namelist())<=set(after.namelist()))
            allowed={'assets/astral/items/asura_alas.json','assets/astral/items/carnivora_alas.json'}
            for n in before.namelist():
                if n not in allowed:self.assertEqual(before.read(n),after.read(n),n)

    def test_private_configs_preserve_other_npcs_and_tienda_click(self):
        import yaml
        base=yaml.safe_load(baseline('mythicmobs/mobs/astral.yml'))
        after=yaml.safe_load((privado()/'build/entregas/tienda-modelo/mythicmobs/mobs/astral.yml').read_text(encoding='utf8'))
        for mid,mob in base.items():
            if mid!='astral_npc_tienda':self.assertEqual(mob,after[mid],mid)
        self.assertEqual(base['astral_npc_tienda']['Display'],after['astral_npc_tienda']['Display'])
        self.assertTrue(set(base['astral_npc_tienda']['Skills'])<=set(after['astral_npc_tienda']['Skills']))
        self.assertIn('skill{s=AST_NPC_comerciante} @self ~onLoad',after['astral_npc_tienda']['Skills'])

    def test_coordinates_and_runtime_cover_tienda_seller_and_hidden_guards(self):
        self.assertEqual(NPC_POS['astral_npc_expediciones'],(178.492,103,237.476,180.4))
        self.assertEqual(NPC_POS['astral_npc_portales'],(211.434,105,237.492,90.0))
        import yaml
        with zipfile.ZipFile(ROOT/'build/runtime/AstralDecor.jar') as z:cfg=yaml.safe_load(z.read('config.yml'))
        self.assertEqual(cfg['npc-models']['astral_npc_tienda'],'astral_npc_comerciante')
        self.assertEqual(cfg['npc-models']['astral_npc_venta'],'astral_vendedor')
        self.assertEqual(cfg['npc-models']['astral_mina_guia'],'astral_npc_mago')
        self.assertEqual(set(cfg['hidden-npcs']),{'astral_npc_'+d for d in ('mina','bosque','tumba','cumbre','forja')})


if __name__=='__main__':unittest.main()
