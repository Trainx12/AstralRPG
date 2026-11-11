"""Regresiones de cajas completas y ubicacion natural de los cinco guias."""
import math
import unittest
import zipfile
from terceros import ROOT
from mobs.tamanos import rows,bounds,scale,VANILLA,SPECIAL,dimensions
from mobs.mazmorra import MINA,skill_yml
from mobs.tanda2 import configure
from mobs.mazmorras_data import catalog
from mobs.salas_seguras import safe
import yaml


class YetiBastonesGuiaTests(unittest.TestCase):
    def test_six_plush_bases_and_boxes_match_transformed_vertices(self):
        import json
        from preview_plush import layouts,vertices
        from terceros import privado
        with zipfile.ZipFile(privado()/'build/entregas/yeti-bastones-guia/AstralRPG-Textures.zip') as z:
            data=layouts();self.assertEqual(len(data),6)
            for key,v in data.items():
                raw=json.loads(z.read('assets/nogs_menagerie/models/plushies/nm_plushie_'+key+'.json'))
                pts=[[(p[a]-8)*v[0]/16+v[a+1] for a in range(3)] for p in vertices(raw,key)]
                self.assertAlmostEqual(min(p[1] for p in pts),0,places=5)
                self.assertAlmostEqual(max(p[1] for p in pts),v[4],places=5)
                self.assertLessEqual(max(math.hypot(p[0],p[2]) for p in pts),1.14/2)

    def test_yeti_exactly_three_blocks_above_ancestral(self):
        model,s=SPECIAL['astral_yeti_cumbre']
        self.assertAlmostEqual(dimensions(model,s)[1],dimensions(model,2)[1]+3)

    def test_all_corners_fit_vanilla_box_at_every_yaw(self):
        for mid,model,s,entity in rows():
            sc=scale(model,s,entity);w,h=VANILLA[entity]
            x,y,z=bounds(model)
            for yaw in range(0,360,5):
                a=math.radians(yaw)
                for px in x:
                    for pz in z:
                        self.assertLessEqual(abs(px*math.cos(a)-pz*math.sin(a))*s,w*sc/2,mid)
                        self.assertLessEqual(abs(px*math.sin(a)+pz*math.cos(a))*s,w*sc/2,mid)
            self.assertLessEqual(y[1]*s,h*sc,mid)

    def test_guides_two_blocks_away_on_natural_floor_and_reset(self):
        ds=[configure(MINA)]+[d for d in catalog() if d['key']!='santuario']
        self.assertEqual(len(ds),5)
        for d in ds:
            room=d['rooms'][-1];fin=room['final_npcs'];key=d['key']
            self.assertEqual(math.dist(fin['cofre'],fin['guia']),2)
            self.assertTrue(safe(d['world'],fin['guia']))
            sk=yaml.safe_load(skill_yml(d))
            prefix=f'{key.upper()}_{room["id"].upper()}'
            end='\n'.join(sk[prefix+'_LIMPIA']['Skills'])
            self.assertIn(f'summon{{type=astral_{key}_guia;',end)
            self.assertIn(f'astral_{key}_cofre,astral_{key}_guia',end)
            self.assertIn(f'astral_{key}_guia','\n'.join(sk[prefix+'_RESET']['Skills']))

    def test_spell_uses_box_instead_of_origin_and_keeps_npc_filter(self):
        with zipfile.ZipFile(ROOT/'build/AstralRPG-Items.zip') as z:
            ray=z.read('data/astral/function/spell/ray.mcfunction').decode()
        self.assertIn('dx=0,dy=0,dz=0',ray)
        self.assertNotIn('distance=',ray)
        self.assertIn('nbt=!{NoAI:1b}',ray)
        self.assertIn('limit=1',ray)


if __name__=='__main__':unittest.main()
