"""Integracion de catalogo, gacha, permisos y conversion privada."""
import json
import unittest
import zipfile
from cosmeticos_catalogo import HATS, WINGS, catalog
from cosmeticos import equipment_menu
from lobby import cosmetic_rewards, crate_yml, GACHAS, icon, RARITY_WEIGHT
from terceros import ROOT, privado


class NewCosmeticsTests(unittest.TestCase):
    def test_delivery_preserves_tienda_yeti_and_vanilla_textures(self):
        base=privado()/'build/entregas/yeti-bastones-guia/AstralRPG-Textures.zip'
        final=privado()/'build/entregas/cosmeticos-skins/AstralRPG-Textures.zip'
        if not final.exists():self.skipTest('Sin entrega privada')
        with zipfile.ZipFile(base) as before,zipfile.ZipFile(final) as after:
            self.assertTrue(set(before.namelist()) <= set(after.namelist()))
            for name in before.namelist():
                self.assertEqual(before.read(name),after.read(name),name)
            added=set(after.namelist())-set(before.namelist())
            self.assertTrue(added)
            self.assertTrue(all(n.startswith(('assets/astral_cosmeticos/','assets/astral/items/cosmeticos/')) for n in added))

    def test_all_rewards_are_permanent_and_have_preview(self):
        rewards=cosmetic_rewards()
        self.assertEqual(len(HATS),20);self.assertEqual(len(WINGS),2)
        for kind,key,name,rarity,model in catalog():
            found=[r for r in rewards if f'astral.cosmetico.{kind}.{key} true' in r[3][0]]
            self.assertEqual(len(found),1)
            self.assertEqual(icon(found[0][3]),('paper',model,1))
            self.assertFalse(any('give ' in c for c in found[0][3]))
        self.assertEqual(len({(r[0],r[1]) for r in catalog()}),22)

    def test_probabilities_keep_rarity_totals_and_titles(self):
        import yaml
        for guarantee in (False,True):
            data=yaml.safe_load(crate_yml('gacha_cosmeticos',GACHAS['gacha_cosmeticos'],guarantee))
            prizes=data['Crate']['Prizes'].values()
            self.assertTrue(any('Titulo' in r['DisplayName'] for r in prizes))
            self.assertAlmostEqual(sum(r['Weight'] for r in prizes),100,places=2)

    def test_locked_equipment_cannot_equip_and_owned_rechecks(self):
        for kind in ('sombrero','alas'):
            items=equipment_menu(kind)['items']
            for _,key,_,_,_ in filter(lambda r:r[0]==kind,catalog()):
                self.assertEqual(items[key]['click_requirement']['requirements']['obtenido']['permission'],f'astral.cosmetico.{kind}.{key}')
                self.assertFalse(any('astralcosmetic' in c for c in items[key+'_locked']['click_commands']))
            slots={v['slot'] for k,v in items.items() if not k.endswith('_locked')}
            self.assertEqual(len(slots),len(items)-sum(k.endswith('_locked') for k in items))

    def test_private_models_resolve_and_never_override_villagers(self):
        folder=privado()/'build/item-pack'
        if not folder.exists():self.skipTest('Sin circuito privado')
        for key,_,_,source in HATS:
            path=folder/f'assets/astral/items/cosmeticos/sombrero_{key}.json'
            tree=json.loads(path.read_text(encoding='utf8'))
            self.assertNotIn('overrides',str(tree))
            if source is None:continue
            model=json.loads((folder/f'assets/astral_cosmeticos/models/item/{key}.json').read_text(encoding='utf8'))
            self.assertIn('head',model['display'])
            for texture in model['textures'].values():
                if texture.startswith('#'):continue
                self.assertTrue(texture.startswith('astral_cosmeticos:item/'))
                ns,rel=texture.split(':')
                self.assertTrue((folder/f'assets/{ns}/textures/{rel}.png').exists())
        with zipfile.ZipFile(ROOT/'build/AstralRPG-Textures.zip') as z:
            self.assertFalse(any(n.startswith('assets/astral_cosmeticos/') for n in z.namelist()))


if __name__=='__main__':unittest.main()
